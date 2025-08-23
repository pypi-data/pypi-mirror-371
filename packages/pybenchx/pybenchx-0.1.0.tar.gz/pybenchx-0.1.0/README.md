# PyBench — a microbenchmarking framework for Python

Write small, focused benchmarks with automatic file discovery, simple parameterization, and a clean, minimal CLI.

Run benchmarks with a single command:

```bash
pybench path/to/file_or_dir [-k keyword] [-P key=value ...]
```

## ✨ Features

- One-line registration: register cases with `bench.bench(...)`; optionally use `BenchContext.start()/end()` to measure only the critical section.
- Auto-discovery: `pybench <dir>` expands `**/*bench.py`.
- Parameterization: generate multiple cases via `params={...}` (cartesian product) or per-case `args/kwargs`.
- CLI overrides: `-P key=value` to tweak parameters at runtime (no code edits).
- Sound timing: high-resolution, monotonic clock; built-in warmup and repeat.
- Nice output: medians, means, and stdev per call (ns) with iterations/repeats.

## 📦 Installation

- With pip:
  ```bash
  pip install pybench
  ```
- With uv:
  ```bash
  uv pip install pybench
  ```

## 🚀 Usage

- Run benchmarks in a file or directory:
  ```bash
  pybench path/to/file_or_dir [-k keyword] [-P key=value ...]
  ```
- Examples:
  ```bash
  # Filter by keyword in case/file name
  pybench benches/ -k json

  # Pass runtime parameters
  pybench benches/ -P size=1000 -P repeats=10
  ```

Tip: use `BenchContext.start()/end()` when you only want to measure the critical section of your benchmark.