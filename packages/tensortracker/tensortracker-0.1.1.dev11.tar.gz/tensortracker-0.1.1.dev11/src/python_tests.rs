use std::io::Cursor;

#[cfg(test)]
mod python_wrappers {
    use super::*;
    use crate::python;
    use crate::tensor_patch::{TensorPatch, TensorPatchFile};
    use safetensors::Dtype;
    use tempfile::tempdir;
    use std::fs::File;

    #[test]
    fn inspect_and_read_bytes_roundtrip() {
        // Build an in-memory TensorPatchFile and serialize to bytes
        let buf = Cursor::new(Vec::new());
        let mut tpf = TensorPatchFile::create(buf, "orig_h".to_string(), "dest_h".to_string()).expect("create tpf");

        let data: Vec<u8> = vec![1u8, 2, 3, 4];
        let patch = TensorPatch {
            dtype: Dtype::U8,
            shape: vec![4],
            data_offset: 0,
            data_len: data.len() as u64,
            is_delta: true,
            compression: None,
        };

        tpf.write_patch("small", patch.clone(), &data).expect("write_patch");

        // Extract bytes
        let mut inner = tpf.into_inner();
        use std::io::Seek;
        use std::io::SeekFrom;
        inner.seek(SeekFrom::Start(0)).expect("seek");
        let bytes = inner.into_inner();

        // Call the python wrapper helpers that operate on bytes
        let inspected = python::inspect_patch_bytes(bytes.clone()).expect("inspect bytes");
        assert_eq!(inspected.0, "orig_h".to_string());
        assert_eq!(inspected.1, "dest_h".to_string());

        let all = python::read_all_patches_bytes(bytes).expect("read all patches bytes");
        assert_eq!(all.len(), 1);
        let (name, dtype_s, shape, payload, is_delta) = &all[0];
        assert_eq!(name, "small");
        assert_eq!(dtype_s, "U8");
        assert_eq!(shape, &vec![4usize]);
        assert_eq!(payload, &vec![1u8,2,3,4]);
        assert!(*is_delta);
    }

    #[test]
    fn patch_class_bytes_and_inspect() {
        // Create a tpf in-memory and roundtrip through the Patch class helpers
        let buf = Cursor::new(Vec::new());
        let mut tpf = TensorPatchFile::create(buf, "oh".to_string(), "dh".to_string()).unwrap();

        let data = vec![9u8; 4];
    let patch = TensorPatch { dtype: Dtype::U8, shape: vec![4], data_offset:0, data_len:4, is_delta: false, compression: None };
        tpf.write_patch("p", patch, &data).unwrap();

        let mut inner = tpf.into_inner();
        use std::io::Seek;
        use std::io::SeekFrom;
        inner.seek(SeekFrom::Start(0)).unwrap();
        let bytes = inner.into_inner();

        // Use Patch wrapper
        let py_patch = python::Patch::new(bytes.clone());
        let out_bytes = py_patch.to_bytes().expect("to_bytes");
        assert_eq!(out_bytes, bytes);
        let inspected = py_patch.inspect().expect("inspect");
        assert_eq!(inspected.0, "oh".to_string());
    }

    #[test]
    fn create_file_write_and_read_roundtrip() {
        // Create a real file on disk and exercise create_patch_file, available_patches,
        // write_patch_atomic and read_patch wrappers
        let dir = tempdir().expect("tempdir");
        let path = dir.path().join("test.patch");
        let path_s = path.to_str().unwrap().to_string();

        // create empty patch file via python wrapper
        python::create_patch_file(path_s.clone(), "ohash".to_string(), "dhash".to_string()).expect("create_patch_file");

        // inspect header
        let header = python::inspect_patch_file(path_s.clone()).expect("inspect file");
        assert_eq!(header.0, "ohash".to_string());
        assert_eq!(header.1, "dhash".to_string());

        // no patches initially
        let avail = python::available_patches(path_s.clone()).expect("available");
        assert!(avail.is_empty());

        // Atomic write a patch using python wrapper
        let payload = vec![7u8,8,9,10];
        python::write_patch_atomic(path_s.clone(), "layer1".to_string(), "U8".to_string(), vec![4usize], payload.clone(), true).expect("write atomic");

        // Read back the patch
        let (dtype_s, shape, data, is_delta) = python::read_patch(path_s.clone(), "layer1".to_string()).expect("read patch");
        assert_eq!(dtype_s, "U8".to_string());
        assert_eq!(shape, vec![4usize]);
        assert_eq!(data, payload);
        assert!(is_delta);
    }
}
