# logslice

A fast log filtering utility that extracts time-bounded slices from large log files without loading them fully into memory.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

Extract log entries between two timestamps:

```bash
logslice --start "2024-03-01 08:00:00" --end "2024-03-01 09:00:00" app.log
```

Pipe the output or save it to a file:

```bash
logslice --start "2024-03-01 08:00:00" --end "2024-03-01 09:00:00" app.log > slice.log
```

Use it as a Python library:

```python
from logslice import slice_log

for line in slice_log("app.log", start="2024-03-01 08:00:00", end="2024-03-01 09:00:00"):
    print(line)
```

### Options

| Flag | Description |
|------|-------------|
| `--start` | Start of the time window (inclusive) |
| `--end` | End of the time window (inclusive) |
| `--fmt` | Timestamp format (default: `%Y-%m-%d %H:%M:%S`) |
| `--output` | Write results to a file instead of stdout |

---

## Why logslice?

Large log files can be gigabytes in size. `logslice` uses binary search and streaming reads to locate and extract the relevant time window efficiently — no full file load, no grep pipelines.

---

## License

MIT © 2024 Your Name