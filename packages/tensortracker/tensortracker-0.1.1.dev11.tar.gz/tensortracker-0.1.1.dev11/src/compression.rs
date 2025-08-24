use safetensors::Dtype;
use std::io;
use zstd::bulk::{Compressor, Decompressor};

/// Compute element-wise residual (dest - origin) for f32/f64 tensors and
/// return the residual bytes in the same element type (f32 or f64) in
/// little-endian order. Returns None when dtype not supported or lengths
/// mismatch.
pub fn compute_residual_bytes(origin: &[u8], dest: &[u8], dtype: Dtype) -> Option<Vec<u8>> {
    match dtype {
        Dtype::F32 => {
            if origin.len() != dest.len() {
                return None;
            }
            let mut out: Vec<u8> = Vec::with_capacity(dest.len());
            let mut i = 0usize;
            while i < dest.len() {
                let o = f32::from_le_bytes(origin[i..i + 4].try_into().ok()?);
                let d = f32::from_le_bytes(dest[i..i + 4].try_into().ok()?);
                let r = d - o;
                out.extend_from_slice(&r.to_le_bytes());
                i += 4;
            }
            Some(out)
        }
        Dtype::F64 => {
            if origin.len() != dest.len() {
                return None;
            }
            let mut out: Vec<u8> = Vec::with_capacity(dest.len());
            let mut i = 0usize;
            while i < dest.len() {
                let o = f64::from_le_bytes(origin[i..i + 8].try_into().ok()?);
                let d = f64::from_le_bytes(dest[i..i + 8].try_into().ok()?);
                let r = d - o;
                out.extend_from_slice(&r.to_le_bytes());
                i += 8;
            }
            Some(out)
        }
        _ => None,
    }
}

/// Quantize residual f32 bytes into int8 with a scale header.
/// Input must be residuals encoded as f32 LE. Output format: [scale:f32 LE][i8...]
pub fn quantize_residual_int8(residual_f32_bytes: &[u8]) -> Option<Vec<u8>> {
    if residual_f32_bytes.len() % 4 != 0 {
        return None;
    }
    let n = residual_f32_bytes.len() / 4;
    let mut vals: Vec<f32> = Vec::with_capacity(n);
    let mut i = 0usize;
    let mut max_abs = 0f32;
    while i < residual_f32_bytes.len() {
        let v = f32::from_le_bytes(residual_f32_bytes[i..i + 4].try_into().ok()?);
        if v.abs() > max_abs {
            max_abs = v.abs();
        }
        vals.push(v);
        i += 4;
    }
    let scale = if max_abs == 0.0 { 1.0 } else { max_abs / 127.0 };
    let mut out: Vec<u8> = Vec::with_capacity(4 + n);
    out.extend_from_slice(&scale.to_le_bytes());
    for v in vals.iter() {
        let q = (*v / scale).round().clamp(-128.0, 127.0) as i8;
        out.push(q as u8);
    }
    Some(out)
}

/// Given candidate payloads (label, bytes), try raw and zstd-compressed
/// forms for each candidate and pick the smallest final stored payload.
/// Returns (method_label_opt, payload_bytes) where method_label_opt is None
/// for an uncompressed raw 'raw' candidate, or Some(label) for any stored
/// method (e.g. "zstd", "residual_zstd", "quant_res8").
pub fn evaluate_payload_candidates(
    candidates: Vec<(String, Vec<u8>)>,
    is_fp16: bool,
    allow_lossy: bool,
) -> io::Result<(Option<String>, Vec<u8>)> {
    let mut best_label: Option<String> = None;
    let mut best_payload: Vec<u8> = Vec::new();
    let mut best_size: usize = usize::MAX;

    for (label, bytes) in candidates.into_iter() {
        // Skip lossy quantized candidates unless allowed
        if !allow_lossy && label.starts_with("quant") {
            continue;
        }
        // raw
        if bytes.len() < best_size {
            best_size = bytes.len();
            best_payload = bytes.clone();
            // raw payload represented as None when it corresponds to the
            // destination full tensor; but label may be something like
            // "raw" or "residual". We'll encode raw storage as Some(label)
            // only if it's not the direct dest 'raw' candidate; callers can
            // interpret labels accordingly. For simplicity, store label when
            // it's not 'raw'.
            best_label = if label == "raw" {
                None
            } else {
                Some(label.clone())
            };
        }

        // try zstd
        match compress_data(&bytes, optimal_compression_level(bytes.len(), is_fp16)) {
            Ok(comp) => {
                if comp.len() < best_size {
                    best_size = comp.len();
                    best_payload = comp;
                    best_label = Some(format!("{}_zstd", label));
                }
            }
            Err(_) => {}
        }
    }

    Ok((best_label, best_payload))
}

/// Compresses data using zstd compression
pub fn compress_data(data: &[u8], level: i32) -> io::Result<Vec<u8>> {
    let mut compressor = Compressor::new(level)?;
    compressor.compress(data).map_err(|e| io::Error::other(e))
}

/// Decompresses zstd compressed data
pub fn decompress_data(compressed: &[u8], original_size: usize) -> io::Result<Vec<u8>> {
    let mut decompressor = Decompressor::new()?;
    decompressor
        .decompress(compressed, original_size)
        .map_err(|e| io::Error::other(e))
}

/// Calculates the optimal compression level based on tensor size and type
pub fn optimal_compression_level(size: usize, is_fp16: bool) -> i32 {
    if size < 1024 * 1024 {
        // < 1MB
        return 1; // Light compression for small tensors
    }
    if is_fp16 {
        3 // Moderate compression for fp16 tensors
    } else {
        5 // Higher compression for other types
    }
}

/// Try a few compression strategies and pick the smallest payload.
/// Currently this tries no compression and zstd compression and returns
/// (method_name_opt, payload_bytes). `method_name_opt` is None when
/// data is stored uncompressed, or Some("zstd") when compressed.
pub fn choose_best_compression(
    data: &[u8],
    is_fp16: bool,
) -> io::Result<(Option<String>, Vec<u8>)> {
    // Baseline: uncompressed
    let mut best: Vec<u8> = data.to_vec();
    let mut best_method: Option<String> = None;

    // Try zstd
    let level = optimal_compression_level(data.len(), is_fp16);
    match compress_data(data, level) {
        Ok(comp) => {
            if comp.len() < best.len() {
                best = comp;
                best_method = Some("zstd".to_string());
            }
        }
        Err(_) => {
            // Ignore compression errors and keep baseline
        }
    }

    Ok((best_method, best))
}

/// Apply residual bytes (element-wise addition) to origin to reconstruct dest.
pub fn apply_residual_bytes(origin: &[u8], residual: &[u8], dtype: Dtype) -> Option<Vec<u8>> {
    match dtype {
        Dtype::F32 => {
            if origin.len() != residual.len() {
                return None;
            }
            let mut out = Vec::with_capacity(origin.len());
            let mut i = 0usize;
            while i < origin.len() {
                let o = f32::from_le_bytes(origin[i..i + 4].try_into().ok()?);
                let r = f32::from_le_bytes(residual[i..i + 4].try_into().ok()?);
                let d = o + r;
                out.extend_from_slice(&d.to_le_bytes());
                i += 4;
            }
            Some(out)
        }
        Dtype::F64 => {
            if origin.len() != residual.len() {
                return None;
            }
            let mut out = Vec::with_capacity(origin.len());
            let mut i = 0usize;
            while i < origin.len() {
                let o = f64::from_le_bytes(origin[i..i + 8].try_into().ok()?);
                let r = f64::from_le_bytes(residual[i..i + 8].try_into().ok()?);
                let d = o + r;
                out.extend_from_slice(&d.to_le_bytes());
                i += 8;
            }
            Some(out)
        }
        _ => None,
    }
}

/// Apply quantized residuals payload to origin. Payload format: [scale:f32 LE][i8...]
pub fn apply_quant_res8(origin: &[u8], payload: &[u8], dtype: Dtype) -> Option<Vec<u8>> {
    if payload.len() < 4 {
        return None;
    }
    let scale = f32::from_le_bytes(payload[0..4].try_into().ok()?);
    match dtype {
        Dtype::F32 => {
            let n = (payload.len() - 4) as usize;
            if origin.len() != n * 4 {
                return None;
            }
            let mut out = Vec::with_capacity(origin.len());
            let mut i_payload = 4usize;
            let mut i_origin = 0usize;
            while i_payload < payload.len() {
                let q = payload[i_payload] as i8 as f32;
                let r = q * scale;
                let o = f32::from_le_bytes(origin[i_origin..i_origin + 4].try_into().ok()?);
                let d = o + r;
                out.extend_from_slice(&d.to_le_bytes());
                i_payload += 1;
                i_origin += 4;
            }
            Some(out)
        }
        _ => None,
    }
}

/// Decode sparse payload format and apply to origin to reconstruct dest.
/// Format: [elem_size:u8][n_changes:u32 LE][ repeated: index:u32 LE | value:elem_size bytes ]
pub fn apply_sparse_bytes(origin: &[u8], sparse: &[u8], dtype: Dtype) -> Option<Vec<u8>> {
    if sparse.len() < 5 {
        return None;
    }
    let elem_size = sparse[0] as usize;
    let n_changes = u32::from_le_bytes(sparse[1..5].try_into().ok()?) as usize;
    let expected_min = 1 + 4 + n_changes * (4 + elem_size);
    if sparse.len() < expected_min {
        return None;
    }
    if origin.len() % elem_size != 0 {
        return None;
    }
    let mut out = origin.to_vec();
    let mut cursor = 5usize;
    for _ in 0..n_changes {
        let idx = u32::from_le_bytes(sparse[cursor..cursor + 4].try_into().ok()?) as usize;
        cursor += 4;
        let off = idx.checked_mul(elem_size)?;
        if off + elem_size > out.len() {
            return None;
        }
        out[off..off + elem_size].copy_from_slice(&sparse[cursor..cursor + elem_size]);
        cursor += elem_size;
    }
    Some(out)
}

/// Return element size in bytes for a given Dtype.
fn elem_size_for_dtype(dtype: Dtype) -> Option<usize> {
    match dtype {
        Dtype::U8 | Dtype::I8 => Some(1),
        Dtype::U16 | Dtype::I16 | Dtype::F16 => Some(2),
        Dtype::F32 | Dtype::I32 | Dtype::U32 => Some(4),
        Dtype::F64 | Dtype::I64 | Dtype::U64 => Some(8),
        _ => None,
    }
}

/// Compute a sparse encoding of the destination tensor relative to origin.
/// Format: [elem_size:u8][n_changes:u32 LE][ repeated: index:u32 LE | value:elem_size bytes ]
/// Returns None if dtype not supported or lengths mismatch.
pub fn compute_sparse_bytes(origin: &[u8], dest: &[u8], dtype: Dtype) -> Option<Vec<u8>> {
    let elem_size = elem_size_for_dtype(dtype)?;
    if origin.len() != dest.len() {
        return None;
    }
    if elem_size == 0 {
        return None;
    }
    let n_elems = origin.len() / elem_size;
    let mut changes: Vec<(u32, Vec<u8>)> = Vec::new();
    for i in 0..n_elems {
        let off = i * elem_size;
        if origin[off..off + elem_size] != dest[off..off + elem_size] {
            changes.push((i as u32, dest[off..off + elem_size].to_vec()));
        }
    }

    // encode
    let mut out: Vec<u8> = Vec::with_capacity(1 + 4 + changes.len() * (4 + elem_size));
    out.push(elem_size as u8);
    let n_changes = changes.len() as u32;
    out.extend_from_slice(&n_changes.to_le_bytes());
    for (idx, val) in changes.into_iter() {
        out.extend_from_slice(&idx.to_le_bytes());
        out.extend_from_slice(&val);
    }
    Some(out)
}
