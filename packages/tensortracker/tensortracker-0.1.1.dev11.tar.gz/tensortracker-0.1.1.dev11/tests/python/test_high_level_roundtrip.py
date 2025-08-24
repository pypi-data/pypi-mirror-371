import pytest
import os
import tempfile
import numpy as np

tt = None
try:
    import tensortrack as tt
except Exception:
    try:
        import tensortracker as tt
    except Exception:
        pytest.skip("tensortrack/tensortracker extension not installed", allow_module_level=True)

# Ensure the module exposes the expected helper, try fallback if needed
if not hasattr(tt, "create_patch"):
    try:
        import tensortracker as tt2
        tt = tt2
    except Exception:
        pytest.skip("tensortrack/tensortracker extension does not expose create_patch", allow_module_level=True)

try:
    from safetensors.numpy import save_file, load_file
except Exception:
    pytest.skip("safetensors.numpy not available", allow_module_level=True)


def dtype_map(s: str):
    return {
        "F32": np.float32,
        "F64": np.float64,
        "I32": np.int32,
        "I64": np.int64,
        "U8": np.uint8,
    }[s]


def test_create_and_apply_roundtrip(tmp_path):
    # Build origin and dest numpy tensors
    origin = {"layer1": np.zeros((4, 4), dtype=np.float32)}
    dest = {"layer1": np.eye(4, dtype=np.float32)}

    origin_path = str(tmp_path / "origin.safetensors")
    dest_path = str(tmp_path / "dest.safetensors")
    reconstructed_path = str(tmp_path / "reconstructed.safetensors")

    save_file(origin, origin_path)
    save_file(dest, dest_path)

    # Create patch (high-level helper)
    patch = tt.create_patch(origin_path, dest_path)
    assert patch is not None

    # Inspect patch metadata
    origin_hash, dest_hash, meta_len, data_offset, patches = patch.inspect()
    assert isinstance(patches, list)
    assert "layer1" in patches

    # Apply patch bytes to origin
    patched = tt.apply_patch_from_bytes(origin_path, patch.to_bytes())
    assert isinstance(patched, list)

    # Rebuild safetensors from returned tuples
    reconstructed = {}
    for name, dtype_s, shape, data_bytes in patched:
        print(name)
        np_dtype = dtype_map(dtype_s)
        arr = np.frombuffer(bytes(data_bytes), dtype=np_dtype).copy()
        arr = arr.reshape(tuple(shape))
        reconstructed[name] = arr

    save_file(reconstructed, reconstructed_path)

    # Compare destination bytes to reconstructed bytes
    with open(dest_path, "rb") as f:
        dest_b = f.read()
    with open(reconstructed_path, "rb") as f:
        rec_b = f.read()

    assert dest_b == rec_b
