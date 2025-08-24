use pyo3::prelude::*;
use safetensors::{tensor::TensorView, Dtype, SafeTensors};
use sha2::{Digest, Sha256};
use std::{collections::HashMap, fs::File, path::Path, time::SystemTime};

mod io {
    pyo3::import_exception!(io, UnsupportedOperation);
}

use crate::compression;
use crate::tensor_patch::{TensorPatch, TensorPatchFile};
use crate::verification;

#[pyclass]
#[derive(Debug, Clone)]
pub struct TensorDelta {
    pub(crate) dtype: Dtype,
    #[pyo3(get, set)]
    pub shape: Vec<usize>,
    #[pyo3(get, set)]
    pub data: Vec<u8>,
    #[pyo3(get, set)]
    pub compressed: bool,
}

#[pyclass]
pub struct TensorDiff {
    #[pyo3(get, set)]
    pub timestamp: SystemTime,
    #[pyo3(get, set)]
    pub changes: HashMap<String, TensorDelta>,
    #[pyo3(get, set)]
    pub origin_hash: String,
    #[pyo3(get, set)]
    pub dest_hash: String,
    #[pyo3(get, set)]
    pub metadata: HashMap<String, String>,
}

fn calculate_tensor_hash(tensor: &SafeTensors) -> String {
    let mut hasher = Sha256::new();
    let mut tensor_names = tensor.names();
    tensor_names.sort();
    for name in tensor_names {
        if let Ok(view) = tensor.tensor(name) {
            hasher.update(view.data());
        }
    }
    format!("{:x}", hasher.finalize())
}

pub fn resolve_diff(origin: SafeTensors, dest: SafeTensors) -> Result<TensorDiff, PyErr> {
    let mut changes = HashMap::new();
    let origin_names: Vec<&String> = origin.names();
    let dest_names: Vec<&String> = dest.names();

    // Check for changes in existing tensors
    for name in origin_names.iter() {
        if dest_names.contains(name) {
            let origin_tensor = origin.tensor(name).unwrap();
            let dest_tensor = dest.tensor(name).unwrap();

            if origin_tensor.data() != dest_tensor.data() {
                changes.insert(
                    name.to_string(),
                    TensorDelta {
                        dtype: dest_tensor.dtype(),
                        shape: dest_tensor.shape().to_vec(),
                        data: dest_tensor.data().to_vec(),
                        compressed: false,
                    },
                );
            }
        }
    }

    // Check for new tensors in dest
    for name in dest_names.iter() {
        if !origin_names.contains(name) {
            let dest_tensor = dest.tensor(name).unwrap();
            changes.insert(
                name.to_string(),
                TensorDelta {
                    dtype: dest_tensor.dtype(),
                    shape: dest_tensor.shape().to_vec(),
                    data: dest_tensor.data().to_vec(),
                    compressed: false,
                },
            );
        }
    }

    Ok(TensorDiff {
        timestamp: SystemTime::now(),
        changes,
        origin_hash: calculate_tensor_hash(&origin),
        dest_hash: calculate_tensor_hash(&dest),
        metadata: HashMap::new(),
    })
}

/// Compute the diff between two SafeTensors and write a patch file representing
/// the changes to `out_path`. Returns the same TensorDiff as `resolve_diff`.
pub fn resolve_diff_and_write_patch(
    origin: SafeTensors,
    dest: SafeTensors,
    out_path: &Path,
    allow_lossy: bool,
) -> Result<TensorDiff, PyErr> {
    // Compute diff inline (don't consume dest before writing patches)
    let mut changes = HashMap::new();
    let origin_names: Vec<&String> = origin.names();
    let dest_names: Vec<&String> = dest.names();

    // Check for changes in existing tensors
    for name in origin_names.iter() {
        if dest_names.contains(name) {
            let origin_tensor = origin.tensor(name).unwrap();
            let dest_tensor = dest.tensor(name).unwrap();

            if origin_tensor.data() != dest_tensor.data() {
                changes.insert(
                    name.to_string(),
                    TensorDelta {
                        dtype: dest_tensor.dtype(),
                        shape: dest_tensor.shape().to_vec(),
                        data: dest_tensor.data().to_vec(),
                        compressed: false,
                    },
                );
            }
        }
    }

    // Check for new tensors in dest
    for name in dest_names.iter() {
        if !origin_names.contains(name) {
            let dest_tensor = dest.tensor(name).unwrap();
            changes.insert(
                name.to_string(),
                TensorDelta {
                    dtype: dest_tensor.dtype(),
                    shape: dest_tensor.shape().to_vec(),
                    data: dest_tensor.data().to_vec(),
                    compressed: false,
                },
            );
        }
    }

    let origin_hash = calculate_tensor_hash(&origin);
    let dest_hash = calculate_tensor_hash(&dest);

    let diff = TensorDiff {
        timestamp: SystemTime::now(),
        changes: changes.clone(),
        origin_hash: origin_hash.clone(),
        dest_hash: dest_hash.clone(),
        metadata: HashMap::new(),
    };

    // Create the patch file on disk
    let file = File::create(out_path).map_err(|e| {
        std::io::Error::new(
            std::io::ErrorKind::Other,
            format!("failed to create patch file: {}", e),
        )
    })?;
    let mut tpf = TensorPatchFile::create(file, origin_hash, dest_hash).map_err(|e| {
        std::io::Error::new(
            std::io::ErrorKind::Other,
            format!("failed to create TensorPatchFile: {}", e),
        )
    })?;

    // For each change, write a patch entry using the destination tensor bytes.
    // Try a simple compression strategy and record the chosen method in the
    // TensorPatch so reads can automatically decompress.
    for (name, _delta) in changes.iter() {
        if let Ok(dest_tensor) = dest.tensor(name) {
            let data = dest_tensor.data().to_vec();
            let mut candidates: Vec<(String, Vec<u8>)> = Vec::new();
            // raw destination payload
            candidates.push(("raw".to_string(), data.clone()));

            // If origin has tensor, try residuals for floating types
            if let Ok(origin_tensor) = origin.tensor(name) {
                if let Some(res_bytes) = compression::compute_residual_bytes(
                    origin_tensor.data(),
                    &data,
                    dest_tensor.dtype(),
                ) {
                    candidates.push(("residual".to_string(), res_bytes.clone()));
                    // quantize residuals (lossy) only when caller allows lossy compression
                    if allow_lossy {
                        if let Some(q) = compression::quantize_residual_int8(&res_bytes) {
                            candidates.push(("quant_res8".to_string(), q));
                        }
                    }
                    // sparse encoding: encode only changed elements (lossless)
                    if let Some(s) = compression::compute_sparse_bytes(
                        origin_tensor.data(),
                        &data,
                        dest_tensor.dtype(),
                    ) {
                        candidates.push(("sparse".to_string(), s));
                    }
                }
            }

            // Evaluate payloads (raw, residual, quantized) and their compressed forms
            let is_fp16 = matches!(dest_tensor.dtype(), Dtype::F16);
            let (method_opt, payload) =
                match compression::evaluate_payload_candidates(candidates, is_fp16, allow_lossy) {
                    Ok(pair) => pair,
                    Err(_) => (None, data.clone()),
                };

            let patch = TensorPatch {
                dtype: dest_tensor.dtype(),
                shape: dest_tensor.shape().to_vec(),
                data_offset: 0,
                data_len: payload.len() as u64,
                is_delta: true,
                compression: method_opt.clone(),
            };

            tpf.write_patch(name, patch, &payload).map_err(|e| {
                std::io::Error::new(
                    std::io::ErrorKind::Other,
                    format!("failed to write patch for {}: {}", name, e),
                )
            })?;
        }
    }

    Ok(diff)
}
