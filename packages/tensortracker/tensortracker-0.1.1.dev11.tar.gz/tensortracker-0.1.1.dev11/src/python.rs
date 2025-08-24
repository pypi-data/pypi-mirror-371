use pyo3::{exceptions, prelude::*};
use safetensors::SafeTensors;

use crate::diff::{self, TensorDiff};
use crate::tensor_patch::{TensorPatch, TensorPatchFile};
use safetensors::Dtype;
use std::fs::File;
use std::io::Cursor;
use std::path::Path;
use tempfile::NamedTempFile;

mod io {
    pyo3::import_exception!(io, FileNotFoundError);
}

fn str_to_dtype(s: &str) -> PyResult<Dtype> {
    match s.to_uppercase().as_str() {
        "F32" => Ok(Dtype::F32),
        "F64" => Ok(Dtype::F64),
        "I32" => Ok(Dtype::I32),
        "I64" => Ok(Dtype::I64),
        "U8" => Ok(Dtype::U8),
        other => Err(exceptions::PyValueError::new_err(format!(
            "Unknown dtype: {}",
            other
        ))),
    }
}

fn dtype_to_str(d: &Dtype) -> &'static str {
    match d {
        Dtype::F32 => "F32",
        Dtype::F64 => "F64",
        Dtype::I32 => "I32",
        Dtype::I64 => "I64",
        Dtype::U8 => "U8",
        _ => "UNKNOWN",
    }
}

/// Opaque Patch object held in Python. Stores the raw patch bytes and provides
/// convenience methods to inspect and serialize.
#[pyclass]
pub struct Patch {
    data: Vec<u8>,
}

#[pymethods]
impl Patch {
    #[new]
    pub fn new(data: Vec<u8>) -> Self {
        Patch { data }
    }

    pub fn to_bytes(&self) -> PyResult<Vec<u8>> {
        Ok(self.data.clone())
    }

    #[staticmethod]
    pub fn from_bytes(data: Vec<u8>) -> PyResult<Self> {
        Ok(Patch { data })
    }

    pub fn inspect(&self) -> PyResult<(String, String, u64, u64, Vec<String>)> {
        inspect_patch_bytes(self.data.clone())
    }
}

/// Compute a tensor-level diff between two safetensors files.
///
/// Parameters
/// - path_origin: path to the origin safetensors file
/// - path_dest: path to the destination safetensors file
///
/// Returns
/// - TensorDiff describing changed / new tensors between origin and dest
#[pyfunction]
#[pyo3(text_signature = "(path_origin, path_dest)")]
#[doc = "Compute a tensor-level diff between two safetensors files.\n\nParameters:\n- path_origin: path to the origin safetensors file\n- path_dest: path to the destination safetensors file\n\nReturns:\n- TensorDiff describing changed / new tensors between origin and dest"]
pub fn resolve_diff(path_origin: String, path_dest: String) -> PyResult<TensorDiff> {
    let origin_bytes = read_bytes_from_path(&path_origin)?;
    let dest_bytes = read_bytes_from_path(&path_dest)?;

    let origin = SafeTensors::deserialize(&origin_bytes)
        .map_err(|e| exceptions::PyRuntimeError::new_err(format!("origin deserialize: {}", e)))?;
    let dest = SafeTensors::deserialize(&dest_bytes)
        .map_err(|e| exceptions::PyRuntimeError::new_err(format!("dest deserialize: {}", e)))?;

    diff::resolve_diff(origin, dest)
        .map_err(|e| exceptions::PyRuntimeError::new_err(format!("diff error: {}", e)))
}

/// Compute a patch file that transforms `path_origin` -> `path_dest` and write
/// it to `out_patch` on disk.
///
/// Signature: resolve_diff_and_write_patch(path_origin: str = "origin.safetensor",
///                                           path_dest: str = "dest.safetensor",
///                                           out_patch: str = "diff.tpatch",
///                                           allow_lossy: bool = False)
///
/// When `allow_lossy` is False (default) quantized lossy candidates are
/// disabled; set True to allow lossy quantization for higher compression.
#[pyfunction]
#[pyo3(signature = (path_origin="origin.safetensor".to_string(), path_dest="dest.safetensor".to_string(), out_patch="diff.tpatch".to_string(), allow_lossy=false))]
pub fn resolve_diff_and_write_patch(
    path_origin: String,
    path_dest: String,
    out_patch: String,
    allow_lossy: Option<bool>,
) -> PyResult<()> {
    let origin_file = std::fs::read(&path_origin)
        .map_err(|e| exceptions::PyIOError::new_err(format!("read origin error: {}", e)))?;
    let origin_res = SafeTensors::deserialize(&origin_file)
        .map_err(|e| exceptions::PyRuntimeError::new_err(format!("origin deserialize: {}", e)))?;

    let dest_file = std::fs::read(&path_dest)
        .map_err(|e| exceptions::PyIOError::new_err(format!("read dest error: {}", e)))?;
    let dest_res = SafeTensors::deserialize(&dest_file)
        .map_err(|e| exceptions::PyRuntimeError::new_err(format!("dest deserialize: {}", e)))?;

    let out_path = std::path::Path::new(&out_patch);
    let allow = allow_lossy.unwrap_or(false);
    crate::diff::resolve_diff_and_write_patch(origin_res, dest_res, out_path, allow)
        .map(|_d| ())
        .map_err(|e| {
            exceptions::PyRuntimeError::new_err(format!("resolve/write patch failed: {}", e))
        })
}

/// Read a single patch from a patch file.
///
/// Returns a tuple: (dtype_str, shape, data_bytes, is_delta)
#[pyfunction]
#[pyo3(text_signature = "(path, name)")]
#[doc = "Read a single patch from a patch file. Returns (dtype_str, shape, data_bytes, is_delta)"]
pub fn read_patch(path: String, name: String) -> PyResult<(String, Vec<usize>, Vec<u8>, bool)> {
    let p = Path::new(&path);
    let file = File::open(p)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open file error: {}", e)))?;
    let mut tpf = TensorPatchFile::open(file)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open patch file error: {}", e)))?;
    let (patch, data) = tpf
        .read_patch(&name)
        .map_err(|e| exceptions::PyIOError::new_err(format!("read patch error: {}", e)))?;
    let dtype_s = dtype_to_str(&patch.dtype).to_string();
    Ok((dtype_s, patch.shape, data, patch.is_delta))
}

/// List available patch names inside a patch file.
#[pyfunction]
#[pyo3(text_signature = "(path)")]
#[doc = "List available patch names inside a patch file."]
pub fn available_patches(path: String) -> PyResult<Vec<String>> {
    let p = Path::new(&path);
    let file = File::open(p)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open file error: {}", e)))?;
    let tpf = TensorPatchFile::open(file)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open patch file error: {}", e)))?;
    Ok(tpf.available_patches())
}

/// Inspect basic header information and available patch names for a patch file
/// Inspect a patch file and return header info and available patch names.
///
/// Returns (origin_hash, dest_hash, metadata_len, data_offset, [patch names])
#[pyfunction]
#[pyo3(text_signature = "(path)")]
#[doc = "Inspect a patch file and return header info and available patch names. Returns (origin_hash, dest_hash, metadata_len, data_offset, [patch names])"]
pub fn inspect_patch_file(path: String) -> PyResult<(String, String, u64, u64, Vec<String>)> {
    let p = Path::new(&path);
    let file = File::open(p)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open file error: {}", e)))?;
    let tpf = TensorPatchFile::open(file)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open patch file error: {}", e)))?;
    let header = tpf.header();
    Ok((
        header.origin_hash.clone(),
        header.dest_hash.clone(),
        header.metadata_len,
        header.data_offset,
        tpf.available_patches(),
    ))
}

/// Inspect a patch stored in-memory as bytes
/// Inspect patch bytes in-memory and return header info and available patch names.
#[pyfunction]
#[pyo3(text_signature = "(data)")]
#[doc = "Inspect patch bytes in-memory and return header info and available patch names."]
pub fn inspect_patch_bytes(data: Vec<u8>) -> PyResult<(String, String, u64, u64, Vec<String>)> {
    let cursor = Cursor::new(data);
    let tpf = TensorPatchFile::open(cursor)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open patch bytes error: {}", e)))?;
    let header = tpf.header();
    Ok((
        header.origin_hash.clone(),
        header.dest_hash.clone(),
        header.metadata_len,
        header.data_offset,
        tpf.available_patches(),
    ))
}

/// Read all patches and payloads from in-memory patch bytes
/// Read all patch entries from in-memory patch bytes.
///
/// Returns a list of tuples: (name, dtype_str, shape, data_bytes, is_delta)
#[pyfunction]
#[pyo3(text_signature = "(data)")]
#[doc = "Read all patch entries from in-memory patch bytes. Returns a list of tuples: (name, dtype_str, shape, data_bytes, is_delta)"]
pub fn read_all_patches_bytes(
    data: Vec<u8>,
) -> PyResult<Vec<(String, String, Vec<usize>, Vec<u8>, bool)>> {
    let cursor = Cursor::new(data);
    let mut tpf = TensorPatchFile::open(cursor)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open patch bytes error: {}", e)))?;
    let all = tpf
        .read_all_patches()
        .map_err(|e| exceptions::PyIOError::new_err(format!("read_all_patches error: {}", e)))?;

    let mut out: Vec<(String, String, Vec<usize>, Vec<u8>, bool)> = Vec::new();
    for (name, (patch, data)) in all.into_iter() {
        let dtype_s = dtype_to_str(&patch.dtype).to_string();
        out.push((name, dtype_s, patch.shape, data, patch.is_delta));
    }
    Ok(out)
}

/// Create a Patch by computing the diff between two safetensor files and
/// returning the produced patch bytes as a `Patch` object. This is a thin
/// helper around `resolve_diff_and_write_patch` which creates a temporary
/// file on disk and reads it back into memory.
/// Create an in-memory `Patch` by diffing two safetensors files.
///
/// Equivalent to running resolve_diff_and_write_patch on disk and returning
/// the produced patch bytes as a `Patch` object. Defaults to lossless
/// compression choices (`allow_lossy=False`).
#[pyfunction]
#[pyo3(text_signature = "(path_origin, path_dest)")]
#[doc = "Create an in-memory `Patch` by diffing two safetensors files. Equivalent to running resolve_diff_and_write_patch on disk and returning the produced patch bytes as a `Patch` object. Defaults to lossless compression choices (allow_lossy=False)."]
pub fn create_patch(path_origin: String, path_dest: String) -> PyResult<Patch> {
    // create a uniquely-named temporary file
    let tmp = NamedTempFile::new()
        .map_err(|e| exceptions::PyIOError::new_err(format!("create temp file failed: {}", e)))?;
    let tmp_path = tmp.path().to_owned();

    // call resolve_and_write to write the patch to the temp path
    resolve_diff_and_write_patch(
        path_origin,
        path_dest,
        tmp_path.to_str().unwrap().to_string(),
        Some(false),
    )
    .map_err(|e| exceptions::PyRuntimeError::new_err(format!("resolve/write failed: {}", e)))?;

    // read produced file bytes
    let bytes = std::fs::read(&tmp_path)
        .map_err(|e| exceptions::PyIOError::new_err(format!("read temp patch failed: {}", e)))?;
    // best-effort cleanup
    let _ = std::fs::remove_file(&tmp_path);
    Ok(Patch { data: bytes })
}

/// Read all patches and payloads from a patch file. Returns a list of tuples:
/// (name, dtype_str, shape, data_bytes, is_delta)
/// Read all patches from a patch file and return a list of tuples
/// (name, dtype_str, shape, data_bytes, is_delta)
#[pyfunction]
#[pyo3(text_signature = "(path)")]
#[doc = "Read all patches from a patch file and return a list of tuples (name, dtype_str, shape, data_bytes, is_delta)"]
pub fn read_all_patches(
    path: String,
) -> PyResult<Vec<(String, String, Vec<usize>, Vec<u8>, bool)>> {
    let p = Path::new(&path);
    let file = File::open(p)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open file error: {}", e)))?;
    let mut tpf = TensorPatchFile::open(file)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open patch file error: {}", e)))?;
    let all = tpf
        .read_all_patches()
        .map_err(|e| exceptions::PyIOError::new_err(format!("read_all_patches error: {}", e)))?;

    let mut out: Vec<(String, String, Vec<usize>, Vec<u8>, bool)> = Vec::new();
    for (name, (patch, data)) in all.into_iter() {
        let dtype_s = dtype_to_str(&patch.dtype).to_string();
        out.push((name, dtype_s, patch.shape, data, patch.is_delta));
    }
    Ok(out)
}

/// Apply a patch file to an origin safetensors file and return the resulting
/// set of tensors as a list of tuples: (name, dtype_str, shape, data_bytes).
/// Apply a patch file to an origin safetensors file and return reconstructed tensors.
///
/// Auto-decodes residual/sparse/quant payloads where possible (origin bytes are
/// used to reconstruct deltas). Returns a list of tuples: (name, dtype_str, shape, data_bytes).
#[pyfunction]
#[pyo3(text_signature = "(origin_path, patch_path)")]
#[doc = "Apply a patch file to an origin safetensors file and return reconstructed tensors. Auto-decodes residual/sparse/quant payloads where possible (origin bytes are used to reconstruct deltas). Returns a list of tuples: (name, dtype_str, shape, data_bytes)."]
pub fn apply_patch_from_files(
    origin_path: String,
    patch_path: String,
) -> PyResult<Vec<(String, String, Vec<usize>, Vec<u8>)>> {
    // Read origin safetensors
    let origin_file = std::fs::read(origin_path)
        .map_err(|e| exceptions::PyIOError::new_err(format!("read origin error: {}", e)))?;
    let origin = SafeTensors::deserialize(&origin_file)
        .map_err(|e| exceptions::PyRuntimeError::new_err(format!("origin deserialize: {}", e)))?;

    // Build a map of tensors from origin
    let mut tensors: std::collections::HashMap<String, (Dtype, Vec<usize>, Vec<u8>)> =
        std::collections::HashMap::new();
    for name in origin.names() {
        if let Ok(view) = origin.tensor(name) {
            tensors.insert(
                name.clone(),
                (view.dtype(), view.shape().to_vec(), view.data().to_vec()),
            );
        }
    }

    // Read patch file and apply changes (auto-decode deltas using origin tensors)
    let p = Path::new(&patch_path);
    let file = File::open(p)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open patch file error: {}", e)))?;
    let mut tpf = TensorPatchFile::open(file)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open patch file error: {}", e)))?;
    let mut keys: Vec<String> = tpf.available_patches();
    keys.sort();
    for name in keys.into_iter() {
        let origin_bytes_opt = tensors.get(&name).map(|t| t.2.as_slice());
        let (patch, data) = tpf
            .read_and_apply_patch(&name, origin_bytes_opt)
            .map_err(|e| {
                exceptions::PyRuntimeError::new_err(format!("apply patch error: {}", e))
            })?;
        tensors.insert(name, (patch.dtype, patch.shape, data));
    }

    // Convert to Vec for Python
    let mut out: Vec<(String, String, Vec<usize>, Vec<u8>)> = Vec::new();
    for (name, (dtype, shape, data)) in tensors.into_iter() {
        out.push((name, dtype_to_str(&dtype).to_string(), shape, data));
    }
    Ok(out)
}

/// Apply a patch provided as bytes to an origin safetensors file and return
/// the resulting tensors as a list of tuples (name, dtype_str, shape, data_bytes).
/// Apply a patch (provided as bytes) to an origin safetensors file and return reconstructed tensors.
///
/// Auto-decodes deltas where possible and returns a list of tuples (name, dtype_str, shape, data_bytes).
#[pyfunction]
#[pyo3(text_signature = "(origin_path, patch_bytes)")]
#[doc = "Apply a patch (provided as bytes) to an origin safetensors file and return reconstructed tensors. Auto-decodes deltas where possible and returns a list of tuples (name, dtype_str, shape, data_bytes)."]
pub fn apply_patch_from_bytes(
    origin_path: String,
    patch_bytes: Vec<u8>,
) -> PyResult<Vec<(String, String, Vec<usize>, Vec<u8>)>> {
    // Read origin safetensors
    let origin_file = std::fs::read(origin_path)
        .map_err(|e| exceptions::PyIOError::new_err(format!("read origin error: {}", e)))?;
    let origin = SafeTensors::deserialize(&origin_file)
        .map_err(|e| exceptions::PyRuntimeError::new_err(format!("origin deserialize: {}", e)))?;

    // Build a map of tensors from origin
    let mut tensors: std::collections::HashMap<String, (Dtype, Vec<usize>, Vec<u8>)> =
        std::collections::HashMap::new();
    for name in origin.names() {
        if let Ok(view) = origin.tensor(name) {
            tensors.insert(
                name.clone(),
                (view.dtype(), view.shape().to_vec(), view.data().to_vec()),
            );
        }
    }

    // Open patch bytes as cursor and read patches (auto-decode)
    let cursor = Cursor::new(patch_bytes);
    let mut tpf = TensorPatchFile::open(cursor)
        .map_err(|e| exceptions::PyIOError::new_err(format!("open patch bytes error: {}", e)))?;
    let mut keys: Vec<String> = tpf.available_patches();
    keys.sort();
    for name in keys.into_iter() {
        let origin_bytes_opt = tensors.get(&name).map(|t| t.2.as_slice());
        let (patch, data) = tpf
            .read_and_apply_patch(&name, origin_bytes_opt)
            .map_err(|e| {
                exceptions::PyRuntimeError::new_err(format!("apply patch error: {}", e))
            })?;
        tensors.insert(name, (patch.dtype, patch.shape, data));
    }

    // Convert to Vec for Python
    let mut out: Vec<(String, String, Vec<usize>, Vec<u8>)> = Vec::new();
    for (name, (dtype, shape, data)) in tensors.into_iter() {
        out.push((name, dtype_to_str(&dtype).to_string(), shape, data));
    }
    Ok(out)
}

// Helper: read file path into bytes vec.
fn read_bytes_from_path(path: &str) -> PyResult<Vec<u8>> {
    let bytes = std::fs::read(path)
        .map_err(|e| exceptions::PyIOError::new_err(format!("read file error: {}", e)))?;
    Ok(bytes)
}

pub(crate) fn register_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Curated Python API surface
    m.add_function(wrap_pyfunction!(resolve_diff, m)?)?;
    m.add_function(wrap_pyfunction!(resolve_diff_and_write_patch, m)?)?;
    m.add_function(wrap_pyfunction!(create_patch, m)?)?;
    m.add_function(wrap_pyfunction!(available_patches, m)?)?;
    m.add_function(wrap_pyfunction!(inspect_patch_file, m)?)?;
    m.add_function(wrap_pyfunction!(inspect_patch_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(read_patch, m)?)?;
    m.add_function(wrap_pyfunction!(read_all_patches, m)?)?;
    m.add_function(wrap_pyfunction!(read_all_patches_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(create_patch, m)?)?;
    m.add_function(wrap_pyfunction!(apply_patch_from_files, m)?)?;
    m.add_function(wrap_pyfunction!(apply_patch_from_bytes, m)?)?;
    m.add_class::<TensorDiff>()?;
    m.add_class::<Patch>()?;
    Ok(())
}
