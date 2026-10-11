#!/usr/bin/env python3
"""Run serial search_batch_v1 validation/smoke configurations into a new directory."""
import argparse
import datetime
import hashlib
from pathlib import Path
import subprocess
import sys

from capture_environment import capture
from run_matrix import numbers, unsigned, save, DISTRIBUTIONS
from analyze_search_results import CATEGORIES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, default=Path("build/release/search_benchmark"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sizes", type=numbers, default=[0, 1, 64, 1000])
    parser.add_argument("--seeds", type=numbers, default=[1729])
    parser.add_argument("--query-seeds", type=numbers, default=[2718])
    parser.add_argument("--distributions", default="uniform,duplicate_heavy")
    parser.add_argument("--searches", default="all")
    parser.add_argument("--categories", default="all")
    parser.add_argument("--queries", type=unsigned, default=64)
    parser.add_argument("--repetitions", type=unsigned, default=5)
    parser.add_argument("--warmups", type=unsigned, default=1)
    parser.add_argument("--memory-limit-mib", type=unsigned, default=256)
    parser.add_argument("--distinct", type=unsigned, default=16)
    parser.add_argument("--swaps", type=unsigned)
    parser.add_argument("--validation-only", action="store_true")
    args = parser.parse_args()
    owns = False
    try:
        binary = args.binary.resolve()
        available = subprocess.run([str(binary), "--list-searches"], capture_output=True, text=True, check=True).stdout.splitlines()
        searches = available if args.searches == "all" else args.searches.split(",")
        distributions = args.distributions.split(",")
        categories = list(CATEGORIES) if args.categories == "all" else args.categories.split(",")
        for selected, allowed in [(searches, available), (distributions, DISTRIBUTIONS), (categories, CATEGORIES)]:
            if not selected or len(set(selected)) != len(selected) or any(name not in allowed for name in selected):
                raise ValueError("unknown or duplicated algorithm/distribution/category")
        if not 2 <= args.queries <= 100000 or args.queries % 2 or not 1 <= args.repetitions <= 10000 or \
                args.warmups > 1000 or not 1 <= args.memory_limit_mib <= 65536 or not 1 <= args.distinct <= 2**32 or \
                (args.swaps is not None and args.swaps > 10000000):
            raise ValueError("invalid query/round/dataset/resource bounds")
        configurations = len(args.sizes)*len(args.seeds)*len(args.query_seeds)*len(distributions)
        if configurations > 1000 or configurations*len(categories)*len(searches)*(args.repetitions+args.warmups) > 1000000:
            raise ValueError("matrix exceeds configuration/row limits")
        if any(16*size+128*args.queries*9 > args.memory_limit_mib*1024**2 for size in args.sizes):
            raise ValueError("dataset/query workspace exceeds memory planning budget")
        args.output.mkdir(exist_ok=False)
        owns = True
        build = next((p for p in [binary.parent, *binary.parent.parents] if (p/"CMakeCache.txt").is_file()), None)
        if build is None:
            raise ValueError("missing discoverable build cache")
        environment = capture(build, " ".join(sys.argv))
        environment.update(record_kind="search_matrix_environment", workload={
            "sizes": args.sizes, "seeds": args.seeds, "query_seeds": args.query_seeds,
            "distributions": distributions, "searches": searches, "categories": categories,
            "batch_size": args.queries, "repetitions": args.repetitions, "warmups": args.warmups},
            workload_note="Before search execution; completion markers determine outcome.",
            benchmark_executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
            tool_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         [Path(__file__), Path(__file__).with_name("analyze_search_results.py"),
                          Path(__file__).with_name("run_matrix.py"), Path(__file__).with_name("capture_environment.py")]})
        save(args.output/"environment.json", environment)
        names, commands = [], []
        for size in args.sizes:
            for seed in args.seeds:
                for query_seed in args.query_seeds:
                    for distribution in distributions:
                        name = f"run_{len(names):06d}"
                        names.append(name)
                        command = [str(binary), "--output", str(args.output/name), "--search", ",".join(searches),
                                   "--size", str(size), "--seed", str(seed), "--query-seed", str(query_seed),
                                   "--distribution", distribution, "--categories", ",".join(categories),
                                   "--queries", str(args.queries), "--repetitions", str(args.repetitions),
                                   "--warmups", str(args.warmups), "--memory-limit-mib", str(args.memory_limit_mib),
                                   "--distinct", str(args.distinct), "--run-id", args.output.name+":"+name]
                        if args.swaps is not None:
                            command.extend(["--swaps", str(args.swaps)])
                        if args.validation_only:
                            command.append("--validation-only")
                        commands.append(command)
        save(args.output/"matrix.json", {"schema_version": 1, "protocol": "search_batch_v1",
             "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "invocation": sys.argv, "runs": names, "commands": commands})
        for name, command in zip(names, commands):
            result = subprocess.run(command, capture_output=True, text=True)
            save(args.output/(name+"_command.json"), {"command": command, "exit_code": result.returncode,
                 "stdout": result.stdout, "stderr": result.stderr})
            if result.returncode:
                raise RuntimeError(f"{name} failed with exit {result.returncode}: {result.stderr.strip()}")
        save(args.output/"COMPLETE.json", {"schema_version": 1, "complete": True, "runs": len(names)})
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        if owns:
            try:
                save(args.output/"FAILED.json", {"complete": False, "error": str(error)})
            except OSError:
                pass
        parser.exit(1, f"search matrix failed: {error}\n")
    print(f"Completed {len(names)} search configurations: {args.output}")


if __name__ == "__main__":
    main()
