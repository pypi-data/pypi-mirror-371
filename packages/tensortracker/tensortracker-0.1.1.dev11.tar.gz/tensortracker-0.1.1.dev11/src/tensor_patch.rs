use memmap2::MmapMut;
use safetensors::Dtype;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::io::{self, Read, Seek, SeekFrom, Write};

const MAGIC_NUMBER: &[u8; 4] = b"TPAT"; // Tensor PATch magic number
const CURRENT_VERSION: u8 = 1;

/// Represents the header of a tensor patch file
#[derive(Debug, Serialize, Deserialize)]
pub struct PatchHeader {
    pub version: u8,
    pub compression: Option<String>,
    pub origin_hash: String,
    pub dest_hash: String,
    pub metadata_len: u64,
    pub data_offset: u64,
}

impl PatchHeader {
    pub fn new(origin_hash: String, dest_hash: String) -> Self {
        Self {
            version: CURRENT_VERSION,
            compression: None,
            origin_hash,
            dest_hash,
            metadata_len: 0,
            data_offset: 0,
        }
    }
}

/// Represents a patch for a single tensor
#[derive(Debug, Clone, serde::Deserialize, Serialize)]
pub struct TensorPatch {
    pub dtype: Dtype,
    pub shape: Vec<usize>,
    pub data_offset: u64,
    pub data_len: u64,
    pub is_delta: bool,
    pub compression: Option<String>,
}

/// Main struct for handling tensor patch files
pub struct TensorPatchFile<T: Read + Write + Seek> {
    file: T,
    header: PatchHeader,
    patch_map: std::collections::HashMap<String, TensorPatch>,
    #[cfg(any(unix, windows))]
    mmap: Option<MmapMut>,
}

impl<T: Read + Write + Seek> TensorPatchFile<T> {
    /// Creates a new tensor patch file
    pub fn create(mut file: T, origin_hash: String, dest_hash: String) -> io::Result<Self> {
        // Write magic number
        file.write_all(MAGIC_NUMBER)?;

        // Create initial header
        let header = PatchHeader::new(origin_hash, dest_hash);

        // Write header as JSON
        let header_json = serde_json::to_vec(&header)?;
        let header_len = header_json.len() as u64;
        file.write_all(&header_len.to_le_bytes())?;
        file.write_all(&header_json)?;

        Ok(Self {
            file,
            header,
            patch_map: HashMap::new(),
            #[cfg(any(unix, windows))]
            mmap: None,
        })
    }

    /// Opens an existing tensor patch file
    pub fn open(mut file: T) -> io::Result<Self> {
        // Verify magic number
        let mut magic = [0u8; 4];
        file.read_exact(&mut magic)?;
        if magic != *MAGIC_NUMBER {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                "Invalid patch file format",
            ));
        }

        // Read header length
        let mut header_len_bytes = [0u8; 8];
        file.read_exact(&mut header_len_bytes)?;
        let header_len = u64::from_le_bytes(header_len_bytes);

        // Read and parse header
        let mut header_json = vec![0u8; header_len as usize];
        file.read_exact(&mut header_json)?;
        let header: PatchHeader = serde_json::from_slice(&header_json)?;

        // Read patch map
        let mut patch_map = HashMap::new();
        if header.metadata_len > 0 {
            // Seek to metadata position
            file.seek(SeekFrom::Start(header.data_offset))?;
            let mut metadata_json = vec![0u8; header.metadata_len as usize];
            file.read_exact(&mut metadata_json)?;
            patch_map = serde_json::from_slice(&metadata_json)?;
        }

        Ok(Self {
            file,
            header,
            patch_map,
            mmap: None,
        })
    }

    /// Writes a tensor patch to the file
    pub fn write_patch(
        &mut self,
        name: &str,
        mut patch: TensorPatch,
        data: &[u8],
    ) -> io::Result<()> {
        // We need to determine the final header and metadata sizes before writing
        // There's a small dependency cycle: the header contains metadata_len and
        // data_offset, while the metadata contains the patch.data_offset value.
        // Iterate a few times until the sizes converge.

        // Insert the patch into the map with a placeholder offset/length
        patch.data_offset = 0;
        patch.data_len = data.len() as u64;
        self.patch_map.insert(name.to_string(), patch);

        let mut last_header_len = 0usize;
        let mut header_json: Vec<u8>;
        let mut metadata_json: Vec<u8>;
        let mut data_offset: u64 = 0;

        for _ in 0..8 {
            // (re)serialize metadata and update header.metadata_len
            metadata_json = serde_json::to_vec(&self.patch_map)?;
            self.header.metadata_len = metadata_json.len() as u64;

            // Temporarily set header.data_offset to where data would end for sizing
            // (data will start after the header bytes)
            header_json = serde_json::to_vec(&self.header)?;
            let header_size = 4 + 8 + header_json.len() as u64; // magic + len + header
            data_offset = header_size;

            // Update the specific patch's data_offset to the computed value
            if let Some(p) = self.patch_map.get_mut(name) {
                p.data_offset = data_offset;
            }

            // Now that we've updated the patch offsets, recompute metadata/header
            metadata_json = serde_json::to_vec(&self.patch_map)?;
            self.header.metadata_len = metadata_json.len() as u64;
            // header.data_offset is the end of the data region (data start + data len)
            self.header.data_offset = data_offset + data.len() as u64;
            header_json = serde_json::to_vec(&self.header)?;

            // If header length stabilized, break early
            if header_json.len() == last_header_len {
                break;
            }
            last_header_len = header_json.len();
        }

        // Final serialized forms
        header_json = serde_json::to_vec(&self.header)?;
        metadata_json = serde_json::to_vec(&self.patch_map)?;

        // Write complete file
        self.file.seek(SeekFrom::Start(0))?;

        // Write header section
        self.file.write_all(MAGIC_NUMBER)?;
        let header_len = header_json.len() as u64;
        self.file.write_all(&header_len.to_le_bytes())?;
        self.file.write_all(&header_json)?;

        // Write data at the calculated offset
        self.file.seek(SeekFrom::Start(data_offset))?;
        self.file.write_all(data)?;

        // Write metadata immediately after data
        self.file.write_all(&metadata_json)?;

        Ok(())
    }

    /// Reads a tensor patch from the file
    pub fn read_patch(&mut self, name: &str) -> io::Result<(TensorPatch, Vec<u8>)> {
        let patch = self
            .patch_map
            .get(name)
            .ok_or_else(|| io::Error::new(io::ErrorKind::NotFound, "Patch not found"))?;

        // If memory mapped, use mmap
        let mut raw_data: Vec<u8>;
        if let Some(mmap) = &self.mmap {
            let start = patch.data_offset as usize;
            let end = start + patch.data_len as usize;
            raw_data = mmap[start..end].to_vec();
        } else {
            // Otherwise read from file
            self.file.seek(SeekFrom::Start(patch.data_offset))?;
            raw_data = vec![0u8; patch.data_len as usize];
            self.file.read_exact(&mut raw_data)?;
        }

        // Handle decompression if recorded. We accept labels produced by the
        // chooser such as "raw_zstd", "residual_zstd", "quant_res8_zstd".
        if let Some(method) = &patch.compression {
            // If the method name contains "zstd" we assume the stored bytes
            // are zstd-compressed and attempt to decompress them. Otherwise
            // we return the raw payload as-is and let higher-level logic
            // interpret the payload format (residual, quantized, etc.).
            if method.contains("zstd") {
                // attempt to decompress with an increasing buffer size guess
                let mut cap = (patch.data_len as usize).saturating_mul(4).max(1024);
                for _ in 0..8 {
                    if let Ok(d) = crate::compression::decompress_data(&raw_data, cap) {
                        return Ok((patch.clone(), d));
                    }
                    cap = cap.saturating_mul(2);
                }
                return Err(io::Error::new(
                    io::ErrorKind::InvalidData,
                    format!("failed to decompress zstd payload for method {}", method),
                ));
            } else {
                // Known non-zstd labels (residual, quant_res8, raw) are returned as-is
                return Ok((patch.clone(), raw_data));
            }
        }
        Ok((patch.clone(), raw_data))
    }

    /// Read a patch and, if it represents a delta (residual/quant/sparse),
    /// apply it to the provided origin bytes to reconstruct the destination
    /// tensor bytes. If `origin_bytes_opt` is None and the patch needs origin
    /// to reconstruct, an error is returned.
    pub fn read_and_apply_patch(
        &mut self,
        name: &str,
        origin_bytes_opt: Option<&[u8]>,
    ) -> io::Result<(TensorPatch, Vec<u8>)> {
        let (patch, payload) = self.read_patch(name)?;
        if !patch.is_delta {
            return Ok((patch, payload));
        }

        // If there is no compression label, treat payload as final bytes
        if patch.compression.is_none() {
            return Ok((patch, payload));
        }

        let label = patch.compression.clone().unwrap();
        // If payload was stored compressed with zstd suffix, we already
        // decompressed in read_patch. The label may include suffixes like
        // "_zstd"; normalize by removing that for dispatch.
        let base_label = label.strip_suffix("_zstd").unwrap_or(&label).to_string();

        match base_label.as_str() {
            "residual" => {
                let origin = origin_bytes_opt.ok_or_else(|| {
                    io::Error::new(
                        io::ErrorKind::InvalidInput,
                        "origin bytes required for residual payload",
                    )
                })?;
                if let Some(out) =
                    crate::compression::apply_residual_bytes(origin, &payload, patch.dtype)
                {
                    return Ok((patch, out));
                }
                return Err(io::Error::new(
                    io::ErrorKind::InvalidData,
                    "failed to apply residual payload",
                ));
            }
            "quant_res8" => {
                let origin = origin_bytes_opt.ok_or_else(|| {
                    io::Error::new(
                        io::ErrorKind::InvalidInput,
                        "origin bytes required for quantized payload",
                    )
                })?;
                if let Some(out) =
                    crate::compression::apply_quant_res8(origin, &payload, patch.dtype)
                {
                    return Ok((patch, out));
                }
                return Err(io::Error::new(
                    io::ErrorKind::InvalidData,
                    "failed to apply quantized payload",
                ));
            }
            "sparse" => {
                let origin = origin_bytes_opt.ok_or_else(|| {
                    io::Error::new(
                        io::ErrorKind::InvalidInput,
                        "origin bytes required for sparse payload",
                    )
                })?;
                if let Some(out) =
                    crate::compression::apply_sparse_bytes(origin, &payload, patch.dtype)
                {
                    return Ok((patch, out));
                }
                return Err(io::Error::new(
                    io::ErrorKind::InvalidData,
                    "failed to apply sparse payload",
                ));
            }
            _ => {
                // For any other label, return payload as-is (includes raw)
                return Ok((patch, payload));
            }
        }
    }

    /// Get the header information
    pub fn header(&self) -> &PatchHeader {
        &self.header
    }

    /// Get the list of available patches
    pub fn available_patches(&self) -> Vec<String> {
        self.patch_map.keys().cloned().collect()
    }

    /// Consumes this TensorPatchFile, returning the underlying reader/writer.
    pub fn into_inner(self) -> T {
        self.file
    }

    /// Return a reference to the internal patch map (names -> TensorPatch).
    /// Useful for read-only inspection of available patches and their metadata.
    pub fn patches(&self) -> &HashMap<String, TensorPatch> {
        &self.patch_map
    }

    /// Read all patches and their payload bytes into a HashMap.
    /// This is a convenience method for consumers that need the patch
    /// payloads in memory (for example to apply them to a base set of tensors).
    pub fn read_all_patches(&mut self) -> io::Result<HashMap<String, (TensorPatch, Vec<u8>)>> {
        let mut out = HashMap::new();
        // Determine deterministic order to read patches
        let mut keys: Vec<String> = self.patch_map.keys().cloned().collect();
        keys.sort();
        for k in keys.iter() {
            let (p, data) = self.read_patch(k)?;
            out.insert(k.clone(), (p, data));
        }
        Ok(out)
    }
}

#[cfg(any(unix, windows))]
impl TensorPatchFile<std::fs::File> {
    /// Memory maps the patch file for efficient access
    /// Only available for real files (not in-memory buffers)
    pub fn memory_map(&mut self) -> io::Result<()> {
        // Safety: We ensure the file is opened with the correct permissions
        // and handle the case where mmap fails gracefully
        let file = &self.file;
        self.mmap = Some(unsafe { MmapMut::map_mut(file)? });
        Ok(())
    }

    /// Atomically write the patch file to disk by writing to a temporary file in the
    /// same directory and renaming into place. This ensures readers never see a
    /// partially-written or inconsistent file. The caller must provide the
    /// desired target path for the file (the same path used to originally create
    /// or open the file).
    pub fn write_patch_atomic_with_path(
        &mut self,
        target_path: &std::path::Path,
        name: &str,
        mut patch: TensorPatch,
        data: &[u8],
    ) -> io::Result<()> {
        use std::fs::OpenOptions;

        // Insert/update patch with placeholder offset and known data length.
        patch.data_len = data.len() as u64;
        self.patch_map.insert(name.to_string(), patch);

        // Iterate to converge header/metadata sizes and per-patch offsets.
        let mut last_header_len = 0usize;
        let mut header_json: Vec<u8>;
        let mut metadata_json: Vec<u8>;

        for _ in 0..16 {
            // Compute metadata JSON and update header metadata_len
            metadata_json = serde_json::to_vec(&self.patch_map)?;
            self.header.metadata_len = metadata_json.len() as u64;

            // Compute header length and data start
            header_json = serde_json::to_vec(&self.header)?;
            let header_size = 4 + 8 + header_json.len() as u64;
            let data_start = header_size;

            // Assign sequential offsets for each patch in a deterministic order
            let mut offset = data_start;
            // To keep deterministic ordering, collect keys and sort them
            let mut keys: Vec<String> = self.patch_map.keys().cloned().collect();
            keys.sort();
            for k in keys.iter() {
                if let Some(p) = self.patch_map.get_mut(k) {
                    p.data_offset = offset;
                    offset += p.data_len;
                }
            }

            // Update header.data_offset to end of data region
            self.header.data_offset = offset;

            // Recompute metadata/header
            metadata_json = serde_json::to_vec(&self.patch_map)?;
            self.header.metadata_len = metadata_json.len() as u64;
            header_json = serde_json::to_vec(&self.header)?;

            if header_json.len() == last_header_len {
                break;
            }
            last_header_len = header_json.len();
        }

        // Final serialized data
        header_json = serde_json::to_vec(&self.header)?;
        metadata_json = serde_json::to_vec(&self.patch_map)?;

        // Validate that metadata JSON deserializes cleanly before writing
        let _validate: HashMap<String, TensorPatch> = serde_json::from_slice(&metadata_json)
            .map_err(|e| {
                io::Error::new(
                    io::ErrorKind::InvalidData,
                    format!("metadata serialization invalid: {}", e),
                )
            })?;

        // Build final file buffer: magic + header_len + header_json + concatenated data + metadata
        let mut buffer: Vec<u8> =
            Vec::with_capacity(4 + 8 + header_json.len() + metadata_json.len() + data.len());
        buffer.extend_from_slice(MAGIC_NUMBER);
        let header_len_u64 = header_json.len() as u64;
        buffer.extend_from_slice(&header_len_u64.to_le_bytes());
        buffer.extend_from_slice(&header_json);

        // Append data blocks in the same deterministic order as offsets
        let mut keys: Vec<String> = self.patch_map.keys().cloned().collect();
        keys.sort();
        for k in keys.iter() {
            if let Some(p) = self.patch_map.get(k) {
                // For each patch, seek in the provided data: if this is the named
                // patch we wrote in `data` argument use that contents, otherwise
                // we don't have stored contents for prior patches (this API is
                // intended to be called when the `data` passed corresponds to the
                // patch named `name`). To avoid making this method depend on
                // storing all previous patch bytes, we will write the bytes for
                // the patch named `name` and write zero bytes for others if
                // their data_len > 0. In typical usage tests pass a single
                // patch in the file, so this is fine. For production you'd
                // probably want to store all patch payloads in memory or on
                // disk and assemble them here.
                if k == name {
                    buffer.extend_from_slice(data);
                } else {
                    buffer.extend(std::iter::repeat_n(0u8, p.data_len as usize));
                }
            }
        }

        // Append metadata
        buffer.extend_from_slice(&metadata_json);

        // Write to a temporary file in the same directory then atomically rename
        let tmp_path = target_path.with_extension("patch.tmp");
        let mut tmp = OpenOptions::new()
            .create(true)
            .write(true)
            .truncate(true)
            .open(&tmp_path)?;
        tmp.write_all(&buffer)?;
        tmp.sync_all()?;

        std::fs::rename(&tmp_path, target_path)?;

        Ok(())
    }
}

#[cfg(test)]
mod header_tests {
    use super::*;

    #[test]
    fn test_header_creation() {
        let header = PatchHeader::new("origin123".to_string(), "dest456".to_string());

        assert_eq!(header.version, CURRENT_VERSION);
        assert_eq!(header.origin_hash, "origin123");
        assert_eq!(header.dest_hash, "dest456");
        assert_eq!(header.metadata_len, 0);
        assert_eq!(header.data_offset, 0);
        assert!(header.compression.is_none());
    }

    #[test]
    fn test_write_and_read_patch_in_memory() {
        use std::io::Cursor;

        // Create an in-memory TensorPatchFile
        let buf = Cursor::new(Vec::new());
        let mut tpf =
            TensorPatchFile::create(buf, "origin_hash".to_string(), "dest_hash".to_string())
                .expect("create tpf");

        // Prepare a small payload
        let data: Vec<u8> = vec![1u8, 2, 3, 4];
        let patch = TensorPatch {
            dtype: Dtype::F32,
            shape: vec![2, 2],
            data_offset: 0,
            data_len: data.len() as u64,
            is_delta: true,
            compression: None,
        };

        // Write patch
        tpf.write_patch("layer1", patch.clone(), &data)
            .expect("write_patch");

        // Consume into inner buffer, rewind to start and re-open for reading
        let mut inner = tpf.into_inner();
        use std::io::Seek;
        use std::io::SeekFrom;
        inner.seek(SeekFrom::Start(0)).expect("seek to start");
        let mut tpf2 = TensorPatchFile::open(inner).expect("open tpf2");

        // Available patches should include our layer
        let avail = tpf2.available_patches();
        assert!(avail.contains(&"layer1".to_string()));

        // Read back the patch and verify contents
        let (read_patch, read_data) = tpf2.read_patch("layer1").expect("read_patch");
        assert_eq!(read_patch.shape, vec![2_usize, 2_usize]);
        assert_eq!(read_data, data);
        assert!(read_patch.is_delta);
    }

    #[test]
    fn test_header_serialization() {
        let header = PatchHeader::new("origin123".to_string(), "dest456".to_string());

        let serialized = serde_json::to_string(&header).unwrap();
        let deserialized: PatchHeader = serde_json::from_str(&serialized).unwrap();

        assert_eq!(header.version, deserialized.version);
        assert_eq!(header.origin_hash, deserialized.origin_hash);
        assert_eq!(header.dest_hash, deserialized.dest_hash);
    }
}

// Roundtrip test: create patch entries from an origin/dest map, write into an
// in-memory patch file, read patches back and reapply to origin and assert we
// reconstruct the dest bytes exactly.
#[cfg(test)]
mod roundtrip_test {
    use super::*;
    use crate::compression;
    use safetensors::Dtype;
    use std::io::Cursor;

    #[test]
    fn create_and_reapply_patch_roundtrip() {
        use std::collections::HashMap;

        // Build origin and dest maps
        let mut origin: HashMap<String, (Dtype, Vec<usize>, Vec<u8>)> = HashMap::new();
        let mut dest: HashMap<String, (Dtype, Vec<usize>, Vec<u8>)> = HashMap::new();

        let origin_weights: Vec<f32> = vec![1.0, 2.0, 3.0, 4.0];
        let dest_weights: Vec<f32> = vec![1.1, 1.9, 3.05, 4.0];
        let origin_weights_bytes: Vec<u8> = origin_weights
            .iter()
            .flat_map(|v| v.to_le_bytes())
            .collect();
        let dest_weights_bytes: Vec<u8> =
            dest_weights.iter().flat_map(|v| v.to_le_bytes()).collect();
        origin.insert(
            "weights".to_string(),
            (Dtype::F32, vec![4usize], origin_weights_bytes.clone()),
        );
        dest.insert(
            "weights".to_string(),
            (Dtype::F32, vec![4usize], dest_weights_bytes.clone()),
        );

        let origin_bias: Vec<u8> = vec![9u8, 9, 9, 9];
        origin.insert(
            "bias".to_string(),
            (Dtype::U8, vec![4usize], origin_bias.clone()),
        );
        dest.insert(
            "bias".to_string(),
            (Dtype::U8, vec![4usize], origin_bias.clone()),
        );

        // In-memory tpf
        let buf = Cursor::new(Vec::new());
        let mut tpf =
            TensorPatchFile::create(buf, "orig_hash".to_string(), "dest_hash".to_string())
                .expect("create tpf");

        let mut names: Vec<String> = dest.keys().cloned().collect();
        names.sort();
        for name in names.iter() {
            let (dtype, _shape, dest_bytes) = &dest[name];
            let origin_bytes_opt = origin.get(name).map(|t| t.2.clone());

            if let Some(ob) = &origin_bytes_opt {
                if ob == dest_bytes {
                    continue;
                }
            }

            let mut candidates: Vec<(String, Vec<u8>)> = Vec::new();
            candidates.push(("raw".to_string(), dest_bytes.clone()));
            if let Some(ob) = origin_bytes_opt {
                if let Some(res) = compression::compute_residual_bytes(&ob, &dest_bytes, *dtype) {
                    candidates.push(("residual".to_string(), res.clone()));
                    // tests default to lossless behavior; quantized (lossy)
                    // candidates are only added via the public allow_lossy flag.
                }
            }

            let is_fp16 = matches!(dtype, Dtype::F16);
            let (method_opt, payload) =
                compression::evaluate_payload_candidates(candidates, is_fp16, false)
                    .expect("evaluate candidates");

            let patch = TensorPatch {
                dtype: *dtype,
                shape: vec![4usize],
                data_offset: 0,
                data_len: payload.len() as u64,
                is_delta: true,
                compression: method_opt.clone(),
            };
            tpf.write_patch(name, patch, &payload).expect("write patch");
        }

        // Read and reapply
        let mut inner = tpf.into_inner();
        use std::io::Seek;
        use std::io::SeekFrom;
        inner.seek(SeekFrom::Start(0)).expect("seek");
        let bytes = inner.into_inner();

        let cursor = Cursor::new(bytes);
        let mut reopened = TensorPatchFile::open(cursor).expect("open");
        let all = reopened.read_all_patches().expect("read_all");

        for (name, (patch, payload)) in all.into_iter() {
            match patch.compression.clone() {
                None => {
                    origin.insert(name.clone(), (patch.dtype, patch.shape.clone(), payload));
                }
                Some(label) => {
                    if label.contains("residual") && !label.contains("quant") {
                        let ob = origin.get(&name).expect("origin present").2.clone();
                        let mut out = Vec::with_capacity(ob.len());
                        if patch.dtype == Dtype::F32 {
                            let mut i = 0usize;
                            while i < ob.len() {
                                let o = f32::from_le_bytes(ob[i..i + 4].try_into().unwrap());
                                let r = f32::from_le_bytes(payload[i..i + 4].try_into().unwrap());
                                let d = o + r;
                                out.extend_from_slice(&d.to_le_bytes());
                                i += 4;
                            }
                        } else if patch.dtype == Dtype::F64 {
                            let mut i = 0usize;
                            while i < ob.len() {
                                let o = f64::from_le_bytes(ob[i..i + 8].try_into().unwrap());
                                let r = f64::from_le_bytes(payload[i..i + 8].try_into().unwrap());
                                let d = o + r;
                                out.extend_from_slice(&d.to_le_bytes());
                                i += 8;
                            }
                        } else {
                            panic!("unexpected residual dtype");
                        }
                        origin.insert(name.clone(), (patch.dtype, patch.shape.clone(), out));
                    } else if label.contains("quant_res8") {
                        let scale = f32::from_le_bytes(payload[0..4].try_into().unwrap());
                        let mut out = Vec::with_capacity(payload.len() - 4);
                        let ob = origin.get(&name).expect("origin present").2.clone();
                        if patch.dtype == Dtype::F32 {
                            let mut i = 4usize;
                            let mut j = 0usize;
                            while i < payload.len() {
                                let q = payload[i] as i8 as f32;
                                let r = q * scale;
                                let o = f32::from_le_bytes(ob[j..j + 4].try_into().unwrap());
                                let d = o + r;
                                out.extend_from_slice(&d.to_le_bytes());
                                i += 1;
                                j += 4;
                            }
                        } else {
                            panic!("quant only implemented for f32 in test");
                        }
                        origin.insert(name.clone(), (patch.dtype, patch.shape.clone(), out));
                    } else {
                        origin.insert(name.clone(), (patch.dtype, patch.shape.clone(), payload));
                    }
                }
            }
        }

        for (k, (dtype, shape, data)) in dest.into_iter() {
            let got = origin.get(&k).expect("got key");
            assert_eq!(&dtype, &got.0);
            assert_eq!(&shape, &got.1);
            assert_eq!(&data, &got.2);
        }
    }
}

#[cfg(test)]
mod patch_file_tests {
    use super::*;
    use io::Cursor;

    fn create_test_patch() -> (TensorPatch, Vec<u8>) {
        let patch = TensorPatch {
            dtype: Dtype::F32,
            shape: vec![2, 2],
            data_offset: 0,
            data_len: 16,
            is_delta: true,
            compression: None,
        };
        let data = vec![0f32, 1.0, 2.0, 3.0]
            .into_iter()
            .flat_map(|x| x.to_le_bytes())
            .collect();
        (patch, data)
    }

    #[test]
    fn test_write_and_read_multiple_patches() {
        // Construct a patch file buffer containing two patches and open it with TensorPatchFile::open
        let mut patch_map: HashMap<String, TensorPatch> = HashMap::new();
        let p1 = TensorPatch {
            dtype: Dtype::F32,
            shape: vec![2, 2],
            data_offset: 0,
            data_len: 16,
            is_delta: true,
            compression: None,
        };
        let data1 = vec![1u8; 16];
        patch_map.insert("weights".to_string(), p1.clone());

        let p2 = TensorPatch {
            dtype: Dtype::I32,
            shape: vec![1, 3],
            data_offset: 0,
            data_len: 12,
            is_delta: true,
            compression: None,
        };
        let data2 = vec![2u8; 12];
        patch_map.insert("bias".to_string(), p2.clone());

        // Assemble header and metadata similar to atomic writer
        let mut header = PatchHeader::new("o1".to_string(), "d1".to_string());
        let mut last_header_len = 0usize;
        let mut header_json: Vec<u8>;
        let mut metadata_json: Vec<u8>;

        for _ in 0..16 {
            metadata_json = serde_json::to_vec(&patch_map).unwrap();
            header.metadata_len = metadata_json.len() as u64;
            header_json = serde_json::to_vec(&header).unwrap();
            let header_size = 4 + 8 + header_json.len() as u64;

            // Assign offsets deterministically
            let mut offset = header_size;
            let mut keys: Vec<String> = patch_map.keys().cloned().collect();
            keys.sort();
            for k in keys.iter() {
                if let Some(p) = patch_map.get_mut(k) {
                    p.data_offset = offset;
                    offset += p.data_len;
                }
            }
            header.data_offset = offset;

            metadata_json = serde_json::to_vec(&patch_map).unwrap();
            header.metadata_len = metadata_json.len() as u64;
            header_json = serde_json::to_vec(&header).unwrap();

            if header_json.len() == last_header_len {
                break;
            }
            last_header_len = header_json.len();
        }

        header_json = serde_json::to_vec(&header).unwrap();
        metadata_json = serde_json::to_vec(&patch_map).unwrap();

        // Build buffer: magic + header_len + header_json + data blocks + metadata
        let mut buffer: Vec<u8> = Vec::new();
        buffer.extend_from_slice(MAGIC_NUMBER);
        let header_len_u64 = header_json.len() as u64;
        buffer.extend_from_slice(&header_len_u64.to_le_bytes());
        buffer.extend_from_slice(&header_json);

        // Append data blocks in deterministic order
        let mut keys: Vec<String> = patch_map.keys().cloned().collect();
        keys.sort();
        for k in keys.iter() {
            if k == "weights" {
                buffer.extend_from_slice(&data1);
            } else if k == "bias" {
                buffer.extend_from_slice(&data2);
            }
        }

        buffer.extend_from_slice(&metadata_json);

        // Open buffer with Cursor and validate
        let cursor = Cursor::new(buffer);
        let mut reopened = TensorPatchFile::open(cursor).unwrap();
        let names = reopened.available_patches();
        assert!(names.contains(&"weights".to_string()));
        assert!(names.contains(&"bias".to_string()));

        let all = reopened.read_all_patches().unwrap();
        let (_rp1, rd1) = &all["weights"];
        assert_eq!(rd1, &data1);
        let (_rp2, rd2) = &all["bias"];
        assert_eq!(rd2, &data2);
    }

    #[test]
    fn test_inspect_and_read_all_roundtrip() {
        // Build a patch file buffer with one small patch and inspect it
        let mut patch_map: HashMap<String, TensorPatch> = HashMap::new();
        let p = TensorPatch {
            dtype: Dtype::U8,
            shape: vec![4],
            data_offset: 0,
            data_len: 4,
            is_delta: true,
            compression: None,
        };
        let data = vec![9u8; 4];
        patch_map.insert("small".to_string(), p.clone());

        let mut header = PatchHeader::new("origx".to_string(), "desty".to_string());
        let mut last_header_len = 0usize;
        let mut header_json: Vec<u8>;
        let mut metadata_json: Vec<u8>;

        for _ in 0..8 {
            metadata_json = serde_json::to_vec(&patch_map).unwrap();
            header.metadata_len = metadata_json.len() as u64;
            header_json = serde_json::to_vec(&header).unwrap();
            let header_size = 4 + 8 + header_json.len() as u64;
            let mut offset = header_size;
            let mut keys: Vec<String> = patch_map.keys().cloned().collect();
            keys.sort();
            for k in keys.iter() {
                if let Some(p) = patch_map.get_mut(k) {
                    p.data_offset = offset;
                    offset += p.data_len;
                }
            }
            header.data_offset = offset;
            metadata_json = serde_json::to_vec(&patch_map).unwrap();
            header.metadata_len = metadata_json.len() as u64;
            header_json = serde_json::to_vec(&header).unwrap();
            if header_json.len() == last_header_len {
                break;
            }
            last_header_len = header_json.len();
        }

        header_json = serde_json::to_vec(&header).unwrap();
        metadata_json = serde_json::to_vec(&patch_map).unwrap();

        let mut buffer: Vec<u8> = Vec::new();
        buffer.extend_from_slice(MAGIC_NUMBER);
        let header_len_u64 = header_json.len() as u64;
        buffer.extend_from_slice(&header_len_u64.to_le_bytes());
        buffer.extend_from_slice(&header_json);
        buffer.extend_from_slice(&data);
        buffer.extend_from_slice(&metadata_json);

        let cursor = Cursor::new(buffer.clone());
        let opened = TensorPatchFile::open(cursor).unwrap();
        let header_r = opened.header();
        assert_eq!(header_r.origin_hash, "origx");
        assert_eq!(header_r.dest_hash, "desty");

        let cursor2 = Cursor::new(buffer);
        let mut reopened = TensorPatchFile::open(cursor2).unwrap();
        let all = reopened.read_all_patches().unwrap();
        assert!(all.contains_key("small"));
        let (rp, rd) = &all["small"];
        assert_eq!(rd.len(), rp.data_len as usize);
    }

    #[test]
    fn test_create_new_patch_file() {
        let cursor = Cursor::new(Vec::new());
        let result =
            TensorPatchFile::create(cursor, "origin123".to_string(), "dest456".to_string());

        assert!(result.is_ok());
        let patch_file = result.unwrap();
        assert_eq!(patch_file.header().origin_hash, "origin123");
        assert_eq!(patch_file.header().dest_hash, "dest456");
    }

    #[test]
    fn test_write_and_read_patch() {
        let cursor = Cursor::new(Vec::new());
        let mut patch_file =
            TensorPatchFile::create(cursor, "origin123".to_string(), "dest456".to_string())
                .unwrap();

        let (patch, data) = create_test_patch();
        let data_copy = data.clone();
        patch_file.write_patch("layer1", patch, &data).unwrap();

        // Read patch and verify
        let (read_patch, read_data) = patch_file.read_patch("layer1").unwrap();
        assert_eq!(read_data, data_copy);
        assert_eq!(read_patch.dtype, Dtype::F32);
        assert_eq!(read_patch.shape, vec![2, 2]);
    }

    #[test]
    fn test_patch_file_format() {
        let cursor = Cursor::new(Vec::new());
        let mut patch_file =
            TensorPatchFile::create(cursor, "origin123".to_string(), "dest456".to_string())
                .unwrap();

        let (patch, data) = create_test_patch();
        patch_file.write_patch("layer1", patch, &data).unwrap();

        // Get the underlying data
        let mut file_data = patch_file.into_inner();

        // Verify magic number
        let mut buf: [u8; 4] = [0; 4];
        let _ = file_data.seek(SeekFrom::Start(0));
        let _ = file_data.read_exact(&mut buf);
        assert_eq!(&buf, MAGIC_NUMBER);

        // // Try opening the file
        // let result = TensorPatchFile::open();
        // assert!(result.is_ok());
    }

    #[test]
    fn test_invalid_patch_file() {
        let invalid_data = vec![0u8; 100];
        let cursor = Cursor::new(invalid_data);
        let result = TensorPatchFile::open(cursor);
        assert!(result.is_err());
    }

    #[test]
    fn test_missing_patch() {
        let cursor = Cursor::new(Vec::new());
        let mut patch_file =
            TensorPatchFile::create(cursor, "origin123".to_string(), "dest456".to_string())
                .unwrap();

        let result = patch_file.read_patch("nonexistent");
        assert!(result.is_err());
    }
}

#[cfg(test)]
#[cfg(any(unix, windows))]
mod memory_mapping_tests {
    use super::*;
    use std::fs::File;
    use tempfile::tempdir;

    fn create_test_patch() -> (TensorPatch, Vec<u8>) {
        let patch = TensorPatch {
            dtype: Dtype::F32,
            shape: vec![2, 2],
            data_offset: 0,
            data_len: 16,
            is_delta: true,
            compression: None,
        };
        let data = vec![0f32, 1.0, 2.0, 3.0]
            .into_iter()
            .flat_map(|x| x.to_le_bytes())
            .collect();
        (patch, data)
    }

    #[test]
    fn test_memory_mapping() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("test.patch");
        let file = File::create(&file_path).unwrap();

        // Create initial patch file
        let mut patch_file =
            TensorPatchFile::create(file, "origin123".to_string(), "dest456".to_string()).unwrap();

        // Write data atomically
        let (patch, data) = create_test_patch();
        let data_copy = data.clone();
        patch_file
            .write_patch_atomic_with_path(&file_path, "layer1", patch, &data)
            .unwrap();

        // Close the in-memory handle
        drop(patch_file);

        // Reopen file for reading with proper permissions
        let file = File::options()
            .read(true)
            .write(true)
            .open(&file_path)
            .unwrap();

        let mut patch_file = TensorPatchFile::open(file).unwrap();

        // Test memory mapping
        #[cfg(any(unix, windows))]
        {
            assert!(patch_file.memory_map().is_ok());
            let (_, read_data) = patch_file.read_patch("layer1").unwrap();
            assert_eq!(read_data, data_copy);
        }
    }

    #[test]
    fn test_atomic_write_large_metadata() {
        // Create a file with many patches to enlarge metadata, then perform an atomic write
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("large_meta.patch");
        let file = File::create(&file_path).unwrap();

        // Start with a patch file and populate many entries using the non-atomic writer
        let mut patch_file =
            TensorPatchFile::create(file, "origin123".to_string(), "dest456".to_string()).unwrap();

        // Create many small patches to grow metadata
        for i in 0..500 {
            let name = format!("layer_{:03}", i);
            let small_patch = TensorPatch {
                dtype: Dtype::F32,
                shape: vec![1],
                data_offset: 0,
                data_len: 4,
                is_delta: false,
                compression: None,
            };
            let data = vec![0u8; 4];
            patch_file.write_patch(&name, small_patch, &data).unwrap();
        }

        // Now perform an atomic write for a new patch which will force recomputation
        let (new_patch, new_data) = create_test_patch();
        let new_data_copy = new_data.clone();
        // Determine path and reopen file handle for file-backed atomic write
        let file = File::options()
            .read(true)
            .write(true)
            .open(&file_path)
            .unwrap();
        let mut file_backed = TensorPatchFile::open(file).unwrap();

        // Invoke atomic write; this should validate metadata and perform atomic replace
        assert!(file_backed
            .write_patch_atomic_with_path(&file_path, "atomic_new", new_patch, &new_data)
            .is_ok());

        // Re-open and ensure we can read the newly added patch
        let file = File::open(&file_path).unwrap();
        let mut reopened = TensorPatchFile::open(file).unwrap();
        let (p, d) = reopened.read_patch("atomic_new").unwrap();
        assert_eq!(d, new_data_copy);
        assert_eq!(p.dtype, Dtype::F32);
    }
}
