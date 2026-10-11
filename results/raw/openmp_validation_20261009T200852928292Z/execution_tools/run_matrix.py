#!/usr/bin/env python3
"""Run a bounded deterministic sorting matrix into a new immutable result directory."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from capture_environment import capture

DISTRIBUTIONS = ("uniform", "sorted", "reverse_sorted", "duplicate_heavy", "nearly_sorted")


def unsigned(text):
    if not text or any(c not in "0123456789" for c in text) or int(text) > 2**64 - 1:
        raise argparse.ArgumentTypeError("expected unsigned decimal fitting uint64")
    return int(text)


def numbers(text):
    parts = text.split(",")
    if len(parts) > 1000:
        raise argparse.ArgumentTypeError("matrix list exceeds 1000 values")
    values = [unsigned(part) for part in parts]
    if len(set(values)) != len(values):
        raise argparse.ArgumentTypeError("duplicate matrix value")
    return values


def save(path, data):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, default=Path("build/release/sort_benchmark"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sizes", type=numbers, default=[1000, 10000])
    parser.add_argument("--seeds", type=numbers, default=[1729])
    parser.add_argument("--distributions", default=",".join(DISTRIBUTIONS))
    parser.add_argument("--sorts", default="all")
    parser.add_argument("--repetitions", type=unsigned, default=5)
    parser.add_argument("--warmups", type=unsigned, default=1)
    parser.add_argument("--memory-limit-mib", type=unsigned, default=256)
    parser.add_argument("--distinct", type=unsigned, default=16)
    parser.add_argument("--swaps", type=unsigned)
    parser.add_argument("--validation-only", action="store_true")
    args = parser.parse_args()
    owns_output = False
    try:
        binary = args.binary.resolve()
        available = subprocess.run([str(binary), "--list-sorts"], check=True, capture_output=True, text=True).stdout.splitlines()
        sorts = available if args.sorts == "all" else args.sorts.split(",")
        distributions = args.distributions.split(",")
        if not sorts or len(set(sorts)) != len(sorts) or any(name not in available for name in sorts):
            raise ValueError("unknown or duplicate sorter")
        if not distributions or len(set(distributions)) != len(distributions) or any(name not in DISTRIBUTIONS for name in distributions):
            raise ValueError("unknown or duplicate distribution")
        if not 1 <= args.repetitions <= 10000 or args.warmups > 1000 or not 1 <= args.memory_limit_mib <= 65536:
            raise ValueError("invalid repetitions/warmups/memory limit")
        if not 1 <= args.distinct <= 2**32 or (args.swaps is not None and args.swaps > 10000000):
            raise ValueError("invalid distinct/swaps")
        if any(size > args.memory_limit_mib * 1024**2 // 16 for size in args.sizes):
            raise ValueError("size exceeds planned array/workspace budget")
        configurations = len(args.sizes) * len(args.seeds) * len(distributions)
        if configurations > 1000 or configurations * len(sorts) * (args.repetitions + args.warmups) > 1000000:
            raise ValueError("matrix exceeds 1000 configurations or 1000000 total rows")
        cases = [(size, seed, distribution) for size in args.sizes for seed in args.seeds for distribution in distributions]
        args.output.mkdir(exist_ok=False)
        owns_output = True
        build_directory = next((parent for parent in [binary.parent, *binary.parent.parents]
                                if (parent / "CMakeCache.txt").is_file()), None)
        if build_directory is None:
            raise ValueError("benchmark binary has no discoverable CMake build cache")
        environment = capture(build_directory, " ".join(sys.argv))
        environment.update({"record_kind": "sorting_matrix_environment", "workload": {
            "sizes": args.sizes, "seeds": args.seeds, "distributions": distributions,
            "sorts": sorts, "repetitions": args.repetitions, "warmups": args.warmups},
            "workload_note": "Environment captured before the declared sorting matrix; completion markers determine outcome.",
            "benchmark_executable_sha256": hashlib.sha256(binary.read_bytes()).hexdigest()})
        save(args.output / "environment.json", environment)
        commands = []
        names = []
        for index, (size, seed, distribution) in enumerate(cases):
            name = f"run_{index:06d}"
            names.append(name)
            command = [str(binary), "--output", str(args.output / name), "--sort", ",".join(sorts),
                       "--size", str(size), "--seed", str(seed), "--distribution", distribution,
                       "--repetitions", str(args.repetitions), "--warmups", str(args.warmups),
                       "--memory-limit-mib", str(args.memory_limit_mib), "--distinct", str(args.distinct),
                       "--run-id", args.output.name + ":" + name]
            if args.swaps is not None:
                command.extend(["--swaps", str(args.swaps)])
            if args.validation_only:
                command.append("--validation-only")
            commands.append(command)
        save(args.output / "matrix.json", {"schema_version": 1, "protocol": "sort_timing_v1",
             "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "invocation": sys.argv, "runs": names, "commands": commands})
        for name, command in zip(names, commands):
            result = subprocess.run(command, capture_output=True, text=True)
            save(args.output / (name + "_command.json"), {"command": command, "exit_code": result.returncode,
                 "stdout": result.stdout, "stderr": result.stderr})
            if result.returncode:
                raise RuntimeError(f"{name} failed with exit {result.returncode}: {result.stderr.strip()}")
        save(args.output / "COMPLETE.json", {"schema_version": 1, "complete": True, "runs": len(names)})
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        if owns_output:
            try:
                save(args.output / "FAILED.json", {"complete": False, "error": str(error)})
            except OSError:
                pass
        parser.exit(1, f"matrix failed: {error}\n")
    print(f"Completed {len(names)} configurations: {args.output}")


if __name__ == "__main__":
    main()
