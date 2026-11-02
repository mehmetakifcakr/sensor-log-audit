# Sensor Log Audit

A small, dependency-free Python tool for checking regularly sampled sensor CSV logs before analysis. It reports invalid numeric samples, non-increasing timestamps and unusually large sampling intervals. It runs locally and does not control hardware.

## Run

Requires Python 3.9 or newer. From the repository root:

```sh
python3 sensor_log_audit.py examples/sample.csv --period 1
python3 -m unittest discover -s tests -v
```

The CSV must have `time_s` and `value` columns. Timestamps are numeric seconds, and the expected sampling interval is given by `--period`. `--tolerance` is a relative gap threshold (default 0.1). Extra columns are ignored. Exit status is 0 for a clean file, 1 for detected issues and 2 for invalid arguments or file errors.

## Scope

This is an early-stage data-quality helper, not a calibration tool or safety monitor. It does not infer time units, detect subtly inaccurate readings, interpolate missing data, or validate physical sensor behavior. Invalid rows are skipped when comparing the next valid timestamp, so a gap may be reported after a malformed row. Review the source data and apply domain-specific checks before making engineering decisions.

## License and provenance

MIT licensed. Initial implementation was prepared with AI assistance and automated tests; see the commit history for changes.
