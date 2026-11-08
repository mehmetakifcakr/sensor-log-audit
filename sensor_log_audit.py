"""Offline checks for regularly sampled, numeric sensor logs."""
import argparse
import csv
import math
import sys


def audit(path, period, tolerance=0.1):
    if not math.isfinite(period) or period <= 0:
        raise ValueError('period must be finite and positive')
    if not math.isfinite(tolerance) or not 0 <= tolerance < 1:
        raise ValueError('tolerance must be finite and in [0, 1)')
    issues = []
    previous = None
    count = 0
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, strict=True)
        if not reader.fieldnames or not {'time_s', 'value'} <= set(reader.fieldnames):
            raise ValueError('CSV must contain time_s and value columns')
        if any(reader.fieldnames.count(name) != 1 for name in ('time_s', 'value')):
            raise ValueError('time_s and value columns must each appear exactly once')
        for line, row in enumerate(reader, 2):
            if None in row:
                issues.append(f'line {line}: extra values beyond CSV header')
                continue
            try:
                t, value = float(row['time_s']), float(row['value'])
                if not math.isfinite(t) or not math.isfinite(value):
                    raise ValueError('non-finite number')
            except (TypeError, ValueError):
                issues.append(f'line {line}: invalid time or value')
                continue
            count += 1
            if previous is not None:
                delta = t - previous
                if delta <= 0:
                    issues.append(f'line {line}: timestamp is not increasing')
                elif delta > period * (1 + tolerance):
                    issues.append(f'line {line}: sampling gap ({delta:g} s)')
            previous = t
    if not count:
        issues.append('no valid samples')
    return count, issues


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv_file')
    p.add_argument('--period', type=float, required=True, help='expected interval in seconds')
    p.add_argument('--tolerance', type=float, default=0.1, help='relative gap tolerance, default 0.1')
    args = p.parse_args(argv)
    try:
        count, issues = audit(args.csv_file, args.period, args.tolerance)
    except (OSError, csv.Error, ValueError) as e:
        print(f'error: {e}', file=sys.stderr)
        return 2
    print(f'Valid samples: {count}')
    for issue in issues:
        print(issue)
    print(f'Issues: {len(issues)}')
    return 1 if issues else 0


if __name__ == '__main__':
    sys.exit(main())
