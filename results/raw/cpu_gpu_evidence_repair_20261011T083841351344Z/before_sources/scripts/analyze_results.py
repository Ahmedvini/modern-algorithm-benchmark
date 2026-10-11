#!/usr/bin/env python3
"""Summarize validated timing bundles without discarding outliers or failures."""
import argparse
import csv
import json
from pathlib import Path
import statistics

FIELDS = ["schema_version", "protocol", "run_id", "run_kind", "algorithm", "distribution",
          "size", "seed", "nearly_sorted_swaps", "duplicate_cardinality", "dataset_generator",
          "input_hash_fnv1a64", "phase", "trial_index", "execution_order", "elapsed_ns",
          "elapsed_unit", "status", "correctness", "error", "repetitions", "warmups",
          "compiler_id", "compiler_version", "build_type", "sanitizers", "platform", "architecture"]


def integer(value):
    if not isinstance(value, str) or not value or any(c not in "0123456789" for c in value):
        raise ValueError(f"invalid unsigned CSV integer: {value!r}")
    result = int(value)
    if result > 2**64 - 1:
        raise ValueError("CSV integer exceeds uint64")
    return result


def summarize_samples(samples):
    return {"successful_trials": len(samples),
            "median_ns": statistics.median(samples) if samples else None,
            "mean_ns": statistics.mean(samples) if samples else None,
            "stdev_ns": statistics.stdev(samples) if len(samples) > 1 else None,
            "min_ns": min(samples) if samples else None,
            "max_ns": max(samples) if samples else None}


def read_bundle(directory, allow_incomplete=False):
    meta = json.loads((directory / "run.json").read_text(encoding="utf-8"))
    if meta["schema_version"] != 1 or meta["protocol"] != "sort_timing_v1":
        raise ValueError("unsupported timing metadata schema")
    algorithms = meta["algorithms"]
    if not algorithms or len(set(algorithms)) != len(algorithms):
        raise ValueError("invalid algorithm list")
    rows = []
    observed = set()
    with (directory / "trials.csv").open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, strict=True)
        if reader.fieldnames != FIELDS:
            raise ValueError("CSV schema does not match sort_timing_v1")
        for row in reader:
            if set(row) != set(FIELDS) or any(value is None for value in row.values()):
                raise ValueError("malformed CSV row")
            if row["schema_version"] != "1" or row["protocol"] != "sort_timing_v1" or row["elapsed_unit"] != "ns":
                raise ValueError("unsupported CSV schema/protocol/unit")
            for field in ["run_id", "run_kind", "distribution", "size", "seed", "nearly_sorted_swaps",
                          "duplicate_cardinality", "dataset_generator", "input_hash_fnv1a64", "repetitions",
                          "warmups", "compiler_id", "compiler_version", "build_type", "platform", "architecture"]:
                if row[field] != str(meta[field]):
                    raise ValueError(f"CSV metadata mismatch: {field}")
            if row["sanitizers"] != str(meta["sanitizers"]).lower():
                raise ValueError("CSV sanitizer metadata mismatch")
            if row["algorithm"] not in algorithms or row["phase"] not in ("warmup", "measure"):
                raise ValueError("unknown algorithm or phase")
            trial = integer(row["trial_index"])
            order = integer(row["execution_order"])
            warmup_end = meta["warmups"] * len(algorithms)
            expected_phase = "warmup" if len(rows) < warmup_end else "measure"
            phase_row = len(rows) if expected_phase == "warmup" else len(rows) - warmup_end
            if row["phase"] != expected_phase or trial != phase_row // len(algorithms) or order != phase_row % len(algorithms):
                raise ValueError("rows violate planned phase/trial sequence")
            limit = meta["warmups"] if row["phase"] == "warmup" else meta["repetitions"]
            if trial >= limit or order >= len(algorithms):
                raise ValueError("trial/order outside planned range")
            offset = (meta["seed"] % len(algorithms) + trial % len(algorithms)) % len(algorithms)
            if algorithms[(offset + order) % len(algorithms)] != row["algorithm"]:
                raise ValueError("execution order differs from protocol")
            identity = (row["phase"], trial, row["algorithm"])
            if identity in observed:
                raise ValueError("duplicate trial")
            observed.add(identity)
            if row["status"] == "ok":
                if row["correctness"] != "passed" or row["error"]:
                    raise ValueError("successful row has failed correctness/error")
                integer(row["elapsed_ns"])
            elif row["status"] == "error":
                if row["correctness"] not in ("failed", "not_checked") or not row["error"]:
                    raise ValueError("failed row lacks diagnostic")
                if row["elapsed_ns"]:
                    integer(row["elapsed_ns"])
            else:
                raise ValueError("unknown trial status")
            rows.append(row)
    expected = (meta["warmups"] + meta["repetitions"]) * len(algorithms)
    if meta["expected_measured_rows"] != meta["repetitions"] * len(algorithms) or \
            meta["expected_warmup_rows"] != meta["warmups"] * len(algorithms):
        raise ValueError("invalid planned row totals")
    complete = False
    marker = directory / "COMPLETE.json"
    if marker.exists():
        done = json.loads(marker.read_text(encoding="utf-8"))
        complete = done.get("schema_version") == 1 and done.get("complete") is True and done.get("rows") == expected
        if not complete or len(rows) != expected or any(row["status"] != "ok" for row in rows) or (directory / "FAILED.json").exists():
            raise ValueError("completion marker contradicts raw data")
    if not complete and not allow_incomplete:
        raise ValueError(f"incomplete/failed run: {directory}; raw observations retained")
    groups = []
    for algorithm in algorithms:
        selected = [row for row in rows if row["algorithm"] == algorithm and row["phase"] == "measure"]
        samples = [integer(row["elapsed_ns"]) for row in selected if row["status"] == "ok"]
        group = {field: meta[field] for field in ["run_id", "run_kind", "distribution", "size", "seed",
                 "nearly_sorted_swaps", "duplicate_cardinality", "input_hash_fnv1a64", "compiler_id",
                 "compiler_version", "build_type", "sanitizers", "platform", "architecture"]}
        group.update(summarize_samples(samples))
        group.update({"algorithm": algorithm, "failed_trials": len(selected) - len(samples),
                      "missing_measured_trials": meta["repetitions"] - len(selected),
                      "warmup_rows": sum(row["algorithm"] == algorithm and row["phase"] == "warmup" for row in rows),
                      "failed_warmups": sum(row["algorithm"] == algorithm and row["phase"] == "warmup" and row["status"] != "ok" for row in rows),
                      "run_complete": complete})
        groups.append(group)
    return complete, groups


def analyze(source, allow_incomplete=False):
    matrix_file = source / "matrix.json"
    if matrix_file.exists():
        matrix = json.loads(matrix_file.read_text(encoding="utf-8"))
        names = matrix["runs"]
        if matrix.get("schema_version") != 1 or not names or len(set(names)) != len(names) or \
                any(Path(name).name != name or name in (".", "..") for name in names):
            raise ValueError("invalid matrix manifest")
        directories = [source / name for name in names]
        matrix_complete = (source / "COMPLETE.json").exists()
        if matrix_complete:
            marker = json.loads((source / "COMPLETE.json").read_text(encoding="utf-8"))
            if marker.get("complete") is not True or marker.get("runs") != len(names) or (source / "FAILED.json").exists():
                raise ValueError("invalid matrix completion marker")
        if not matrix_complete and not allow_incomplete:
            raise ValueError("incomplete/failed matrix; raw data retained")
    else:
        directories = [source]
        matrix_complete = True
    groups = []
    all_complete = matrix_complete
    missing_runs = []
    for directory in directories:
        if not (directory / "run.json").exists():
            if not allow_incomplete:
                raise ValueError(f"missing planned run: {directory}")
            missing_runs.append(str(directory))
            all_complete = False
            continue
        complete, run_groups = read_bundle(directory, allow_incomplete)
        all_complete = all_complete and complete
        groups.extend(run_groups)
    return {"schema_version": 1, "summary_kind": "sort_timing_summary", "source": str(source.resolve()),
            "complete": all_complete, "elapsed_unit": "ns", "outlier_policy": "retain_all",
            "stdev_definition": "sample_ddof_1; null for fewer than two successes",
            "missing_runs": missing_runs, "groups": groups}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    try:
        result = analyze(args.source, args.allow_incomplete)
        serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(serialized)
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as error:
        parser.exit(1, f"analysis failed: {error}\n")
    print(args.output)
    if not result["complete"]:
        parser.exit(1, "analysis retained incomplete/failed status\n")


if __name__ == "__main__":
    main()
