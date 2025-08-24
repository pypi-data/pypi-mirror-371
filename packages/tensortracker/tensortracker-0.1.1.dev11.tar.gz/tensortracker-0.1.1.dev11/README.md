# TensorTracker
 
[![PyPI](https://img.shields.io/pypi/v/tensortracker.svg)](https://pypi.org/project/tensortracker/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?logo=apache)](LICENSE)
[![Build Status](https://github.com/james-a-page/tensor-track/workflows/CI/badge.svg)](https://github.com/james-a-page/tensor-track/actions)

Currently a WIP to see where it gets to. Learning some rust with the help of some vibe coding (maybe a bad idea?). May fork into a tidier repo when it feels more fully fledged.

## Features (current)

- Compute diffs between SafeTensors files and write patch files.
- Python bindings exposing convenience helpers (for example, `resolve_diff_and_write_patch`).
- Atomic write path for file-backed patch creation (temporary file + atomic rename).

## Status

This repository is under active development. The Python package is not necessarily published to PyPI from this source; to use the Python API locally, build the extension with `maturin develop -r` or install the package into your environment with `pip`.

## Installation (developer)

Prerequisites:
- Rust (stable toolchain)
- Python 3.12+
- maturin (to build the Python extension)

Build and run Rust tests:

```bash
cargo test
```

Build and install the Python extension locally:

```bash
maturin develop -r
# or
python -m pip install .
```

## Quick examples

High-level: create a patch between two safetensors files using the Python binding:

```python
import tensortracker

# writes a patch file that encodes changes from origin -> dest
tensortracker.resolve_diff_and_write_patch('origin.safetensors', 'dest.safetensors', 'out.patch')
```

Low-level: the Python extension also exposes read/write helpers for individual patch entries (see `src/python.rs` for exact names and semantics).

## License

This project is released under the terms documented in `LICENSE`.

## Citation

If you use this software in research, please reference the repository.
