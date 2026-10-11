#!/usr/bin/env python3
"""Capture a baseline environment; exclusively create the requested manifest."""

import argparse
import datetime
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys


def probe(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return {"command": command, "returncode": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr}
    except OSError as error:
        return {"command": command, "returncode": None, "error": str(error)}


def read_optional(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return None


def capture(build_dir, invocation):
    cache_path = build_dir / "CMakeCache.txt"
    cache = cache_path.read_text(encoding="utf-8")
    entries = {}
    for line in cache.splitlines():
        if line and not line.startswith(("#", "//")) and "=" in line:
            key, value = line.split("=", 1)
            entries[key.split(":", 1)[0]] = value
    compiler = entries.get("CMAKE_CXX_COMPILER")
    if not compiler:
        raise ValueError("CMake cache does not identify the C++ compiler")
    commands_path = build_dir / "compile_commands.json"
    return {
        "schema_version": 1,
        "record_kind": "baseline_environment",
        "captured_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "invocation": invocation,
        "working_directory": str(Path.cwd()),
        "build_directory": str(build_dir.resolve()),
        "os": platform.platform(),
        "machine": platform.machine(),
        "cpu_reported_by_python": platform.processor() or None,
        "logical_cpu_count": os.cpu_count(),
        "cpu_probe": probe(["lscpu"]),
        "linux_meminfo": read_optional("/proc/meminfo"),
        "linux_cgroup": read_optional("/proc/self/cgroup"),
        "python": sys.version,
        "cmake": probe(["cmake", "--version"]),
        "compiler": probe([compiler, "--version"]),
        "cmake_cache": cache,
        "compile_commands": (json.loads(commands_path.read_text(encoding="utf-8"))
                             if commands_path.exists() else None),
        "git_status": probe(["git", "status", "--short"]),
        "workload": None,
        "workload_note": "Correctness baseline only; no benchmark workload executed.",
        "gpu_status": "not probed; no GPU experiment attempted",
    }


def write_manifest(output, record):
    # Serialize before opening, then use x mode so existing raw data is preserved.
    serialized = json.dumps(record, indent=2, sort_keys=True) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        stream.write(serialized)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        write_manifest(args.output, capture(args.build_dir, shlex.join(sys.argv)))
    except (OSError, ValueError) as error:
        parser.exit(1, f"environment capture failed: {error}\n")
    print(args.output)


if __name__ == "__main__":
    main()
