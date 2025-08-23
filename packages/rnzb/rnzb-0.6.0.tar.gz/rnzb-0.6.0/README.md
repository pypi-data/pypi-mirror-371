# rnzb

[![Tests](https://img.shields.io/github/actions/workflow/status/Ravencentric/rnzb/tests.yml?label=tests)](https://github.com/Ravencentric/rnzb/actions/workflows/tests.yml)
[![Build](https://img.shields.io/github/actions/workflow/status/Ravencentric/rnzb/release.yml?label=build)](https://github.com/Ravencentric/rnzb/actions/workflows/release.yml)
![PyPI - Types](https://img.shields.io/pypi/types/rnzb)
![License](https://img.shields.io/pypi/l/rnzb?color=success)

[![PyPI - Latest Version](https://img.shields.io/pypi/v/rnzb?color=blue)](https://pypi.org/project/rnzb)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rnzb)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/rnzb)

Python bindings to the [nzb-rs](https://crates.io/crates/nzb-rs) library - a [spec](https://sabnzbd.org/wiki/extra/nzb-spec) compliant parser for [NZB](https://en.wikipedia.org/wiki/NZB) files, written in Rust.

## Table Of Contents

- [About](#about)
- [Installation](#installation)
- [Related projects](#related-projects)
- [Performance](#performance)
- [Building from source](#building-from-source)
- [License](#license)
- [Contributing](#contributing)

## About

`rnzb.Nzb` is a drop-in replacement for [`nzb.Nzb`](https://ravencentric.cc/nzb/api-reference/parser/#nzb.Nzb).

For documentation and usage examples, refer to the [`nzb`](https://pypi.org/project/nzb) library's resources:

- [Tutorial](https://ravencentric.cc/nzb/tutorial/)
- [API Reference](https://ravencentric.cc/nzb/api-reference/parser/)

### Error handling

- `rnzb.InvalidNzbError` is named identically to `nzb.InvalidNzbError`, but it's not a drop-in replacement.
- Error messages will be largely similar to `nzb`'s, though not guaranteed to be identical in every case.
- `rnzb.InvalidNzbError` is a simpler exception (See [PyO3/pyo3#295](https://github.com/PyO3/pyo3/issues/295) for why). Its implementation is effectively:
  
  ```python
  class InvalidNzbError(Exception): pass
  ```
  
  This means that it's lacking custom attributes like `.message` found in `nzb`'s version. Code relying on such attributes on `nzb.InvalidNzbError` will require adjustment. Consider using the standard exception message (`str(e)`) to achieve the same result.
- `rnzb` will *only ever* raise explicitly documented errors for each function. Undocumented errors should be reported as bugs.

## Installation

`rnzb` is available on [PyPI](https://pypi.org/project/rnzb/), so you can simply use pip to install it.

```bash
pip install rnzb
```

## Related projects

Considering this is the fourth library for parsing a file format that almost nobody cares about and lacks a formal specification, here's an overview to help you decide:

| Project                                                  | Description                 | Parser | Meta Editor |
| -------------------------------------------------------- | --------------------------- | ------ | ----------- |
| [`nzb`](https://pypi.org/project/nzb)                    | Original Python Library     | ✅     | ✅          |
| [`nzb-rs`](https://crates.io/crates/nzb-rs)              | Rust port of `nzb`          | ✅     | ❌          |
| [`rnzb`](https://pypi.org/project/nzb)                   | Python bindings to `nzb-rs` | ✅     | ❌          |
| [`nzb-parser`](https://www.npmjs.com/package/nzb-parser) | Javascript port of `nzb`    | ✅     | ❌          |

## Performance

`rnzb` is approximately two to three times faster than [`nzb`](https://pypi.org/project/nzb/), depending on the NZB.

```console
$ hyperfine --warmup 1 --shell=none ".venv/Scripts/python.exe -I -B test_nzb.py" ".venv/Scripts/python.exe -I -B test_rnzb.py"
Benchmark 1: .venv/Scripts/python.exe -I -B test_nzb.py
  Time (mean ± σ):     368.9 ms ±   3.1 ms    [User: 196.9 ms, System: 160.9 ms]
  Range (min … max):   364.4 ms … 374.1 ms    10 runs

Benchmark 2: .venv/Scripts/python.exe -I -B test_rnzb.py
  Time (mean ± σ):     112.7 ms ±   1.2 ms    [User: 45.1 ms, System: 60.7 ms]
  Range (min … max):   111.4 ms … 116.2 ms    26 runs

Summary
  .venv/Scripts/python.exe -I -B test_rnzb.py ran
    3.27 ± 0.04 times faster than .venv/Scripts/python.exe -I -B test_nzb.py
```

## Building from source

Building from source requires the [Rust toolchain](https://rustup.rs/) and [Python 3.9+](https://www.python.org/downloads/).

- With [`uv`](https://docs.astral.sh/uv/):

  ```bash
  git clone https://github.com/Ravencentric/rnzb
  cd rnzb
  uv build
  ```

- With [`pypa/build`](https://github.com/pypa/build):

  ```bash
  git clone https://github.com/Ravencentric/rnzb
  cd rnzb
  python -m build
  ```

## License

Licensed under either of:

- Apache License, Version 2.0 ([LICENSE-APACHE](https://github.com/Ravencentric/rnzb/blob/main/LICENSE-APACHE) or <https://www.apache.org/licenses/LICENSE-2.0>)
- MIT license ([LICENSE-MIT](https://github.com/Ravencentric/rnzb/blob/main/LICENSE-MIT) or <https://opensource.org/licenses/MIT>)

at your option.

## Contributing

Contributions are welcome! Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions.
