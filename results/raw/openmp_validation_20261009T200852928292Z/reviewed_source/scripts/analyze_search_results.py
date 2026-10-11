#!/usr/bin/env python3
"""Validate search_batch_v1 bundles and summarize batches without pooling categories."""
import argparse
import csv
import json
from pathlib import Path

from analyze_results import integer, summarize_samples

CATEGORIES = ("hit_first", "hit_middle", "hit_last", "hit_random", "miss_below",
              "miss_between", "miss_above", "mixed_50", "miss_empty")
FIELDS = ("schema_version,protocol,run_id,run_kind,algorithm,distribution,size,seed,"
          "input_hash_fnv1a64,query_seed,query_generator,query_category,query_hash_fnv1a64,"
          "batch_size,hit_queries,miss_queries,phase,trial_index,execution_order,elapsed_ns,"
          "elapsed_unit,status,correctness,error,repetitions,warmups,compiler_id,compiler_version,"
          "build_type,sanitizers,platform,architecture").split(",")
QUERY_FIELDS = ["query_category", "query_id", "target", "selected_position", "expected_position", "expected_hit"]


def rows(path, fields):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, strict=True)
        if reader.fieldnames != fields:
            raise ValueError(f"invalid CSV schema: {path}")
        data = list(reader)
    if any(set(row) != set(fields) or any(value is None for value in row.values()) for row in data):
        raise ValueError("malformed CSV row")
    return data


def fingerprint(queries):
    result = 14695981039346656037
    for query in queries:
        words = [(int(query["target"]) & (2**32-1), 4)]
        words += [(integer(query[field]) if query[field] else 2**64-1, 8)
                  for field in ("selected_position", "expected_position")]
        for word, count in words:
            for byte in word.to_bytes(count, "little"):
                result = ((result ^ byte) * 1099511628211) & (2**64-1)
    return str(result)


def read_bundle(directory, allow_incomplete=False):
    meta = json.loads((directory / "run.json").read_text())
    if meta.get("schema_version") != 1 or meta.get("protocol") != "search_batch_v1":
        raise ValueError("unsupported search protocol/schema (counts are separate)")
    algorithms = meta["algorithms"]
    if not algorithms or len(set(algorithms)) != len(algorithms) or any(
            name not in ("linear_search", "binary_search", "exponential_search") for name in algorithms):
        raise ValueError("invalid search algorithm list")
    if meta["input_order"] != "ascending" or meta["query_generator"] != "mt19937_64_queries_v1" or \
            meta["dataset_generator"] != "mt19937_64_v1" or meta["clock"] != "steady_clock" or \
            meta["order_policy"] != "seed_offset_cyclic_v1" or meta["elapsed_unit"] != "ns":
        raise ValueError("unsupported dataset/query/timing policy")
    if meta["run_kind"] not in ("validation", "performance") or (meta["run_kind"] == "performance" and
            (meta["build_type"] != "Release" or meta["sanitizers"] is not False)):
        raise ValueError("invalid performance build")
    for name in ("size", "seed", "query_seed", "batch_size", "repetitions", "warmups"):
        if type(meta[name]) is not int or not 0 <= meta[name] <= 2**64-1:
            raise ValueError("invalid metadata integer")
    if not 2 <= meta["batch_size"] <= 100000 or meta["batch_size"] % 2 or \
            not 1 <= meta["repetitions"] <= 10000 or not 0 <= meta["warmups"] <= 1000:
        raise ValueError("invalid batch/round bounds")
    integer(meta["input_hash_fnv1a64"])
    categories = meta["categories"]
    names = [entry["category"] for entry in categories]
    if not names or names != [name for name in CATEGORIES if name in names]:
        raise ValueError("invalid category list/order")
    queries = rows(directory / "queries.csv", QUERY_FIELDS)
    cursor = 0
    expected_by_target = {}
    for entry in categories:
        name = entry["category"]
        if type(entry["available"]) is not bool or not isinstance(entry["reason"], str):
            raise ValueError("invalid category availability")
        count = meta["batch_size"] if entry["available"] else 0
        if entry["batch_size"] != count or bool(entry["reason"]) == entry["available"]:
            raise ValueError("unavailable category lacks reason or has invented queries")
        selected = queries[cursor:cursor+count]
        cursor += count
        if len(selected) != count:
            raise ValueError("missing query records")
        hits = 0
        for index, query in enumerate(selected):
            target = query["target"]
            value = int(target)
            if str(value) != target or not -(2**31) <= value < 2**31:
                raise ValueError("invalid signed int32 query target")
            if query["query_category"] != name or integer(query["query_id"]) != index:
                raise ValueError("query identity/order mismatch")
            present = bool(query["expected_position"])
            if query["expected_hit"] != str(present).lower():
                raise ValueError("query hit/expected-position mismatch")
            for field in ("selected_position", "expected_position"):
                if query[field] and integer(query[field]) >= meta["size"]:
                    raise ValueError("query position outside data")
            if bool(query["selected_position"]) != present or (present and
                    integer(query["expected_position"]) > integer(query["selected_position"])):
                raise ValueError("selected/first-match position mismatch")
            if target in expected_by_target and expected_by_target[target] != query["expected_position"]:
                raise ValueError("same key has inconsistent expected answer")
            expected_by_target[target] = query["expected_position"]
            expected_hit = name.startswith("hit_") or (name == "mixed_50" and index % 2 == 0)
            if present != expected_hit:
                raise ValueError("category hit/miss policy mismatch")
            if name == "miss_empty" and meta["size"] != 0:
                raise ValueError("empty-input policy used on nonempty data")
            if name in ("hit_first", "hit_middle", "hit_last"):
                position = {"hit_first": 0, "hit_middle": meta["size"]//2, "hit_last": meta["size"]-1}[name]
                if integer(query["selected_position"]) != position or target != selected[0]["target"]:
                    raise ValueError("fixed-rank query policy mismatch")
            hits += present
        if entry["hit_queries"] != hits or entry["miss_queries"] != count-hits or \
                entry["query_hash_fnv1a64"] != fingerprint(selected):
            raise ValueError("query fingerprint/count mismatch")
    if cursor != len(queries) or meta["query_rows"] != cursor or \
            meta["hit_queries"] != sum(entry["hit_queries"] for entry in categories) or \
            meta["miss_queries"] != sum(entry["miss_queries"] for entry in categories):
        raise ValueError("query plan totals mismatch")
    available = [entry for entry in categories if entry["available"]]
    per_round = len(available) * len(algorithms)
    expected = per_round * (meta["repetitions"] + meta["warmups"])
    if meta["expected_rows"] != expected:
        raise ValueError("planned row count mismatch")
    data = rows(directory / "trials.csv", FIELDS)
    if len(data) > expected:
        raise ValueError("extra timing rows")
    for index, row in enumerate(data):
        if row["schema_version"] != "1" or row["protocol"] != "search_batch_v1" or row["elapsed_unit"] != "ns":
            raise ValueError("invalid trial schema/unit")
        for field in ("run_id", "run_kind", "distribution", "size", "seed", "input_hash_fnv1a64", "query_seed",
                      "query_generator", "batch_size", "repetitions", "warmups", "compiler_id", "compiler_version",
                      "build_type", "platform", "architecture"):
            if row[field] != str(meta[field]):
                raise ValueError(f"trial metadata mismatch: {field}")
        if row["sanitizers"] != str(meta["sanitizers"]).lower():
            raise ValueError("sanitizer metadata mismatch")
        warmup_rows = meta["warmups"] * per_round
        phase = "warmup" if index < warmup_rows else "measure"
        phase_index = index if phase == "warmup" else index-warmup_rows
        trial, offset = divmod(phase_index, per_round)
        category_index, order = divmod(offset, len(algorithms))
        entry = available[category_index]
        algorithm = algorithms[(meta["seed"] % len(algorithms)+trial % len(algorithms)+order) % len(algorithms)]
        if row["phase"] != phase or integer(row["trial_index"]) != trial or integer(row["execution_order"]) != order or \
                row["algorithm"] != algorithm or row["query_category"] != entry["category"]:
            raise ValueError("trial order/identity mismatch")
        for field in ("hit_queries", "miss_queries", "query_hash_fnv1a64"):
            if row[field] != str(entry[field]):
                raise ValueError("trial query batch mismatch")
        if row["status"] == "ok":
            if row["correctness"] != "passed" or row["error"]:
                raise ValueError("successful row has failed correctness")
            integer(row["elapsed_ns"])
        elif row["status"] == "error":
            if row["correctness"] not in ("failed", "not_checked") or not row["error"]:
                raise ValueError("failed row lacks diagnostic")
            if row["elapsed_ns"]:
                integer(row["elapsed_ns"])
            if (row["correctness"] == "failed") != bool(row["elapsed_ns"]):
                raise ValueError("failure timing/validation distinction mismatch")
            if index != len(data)-1:
                raise ValueError("rows continue after fail-fast error")
        else:
            raise ValueError("unknown row status")
    complete = (directory / "COMPLETE.json").exists()
    if complete:
        marker = json.loads((directory / "COMPLETE.json").read_text())
        if marker.get("schema_version") != 1 or marker.get("complete") is not True or marker.get("rows") != expected or \
                len(data) != expected or any(row["status"] != "ok" for row in data) or (directory / "FAILED.json").exists():
            raise ValueError("completion marker contradicts raw observations")
    elif not allow_incomplete:
        raise ValueError("incomplete search run; raw observations retained")
    groups = []
    for entry in available:
        for algorithm in algorithms:
            selected = [row for row in data if row["phase"] == "measure" and
                        (row["algorithm"], row["query_category"]) == (algorithm, entry["category"])]
            samples = [integer(row["elapsed_ns"]) for row in selected if row["status"] == "ok"]
            stats = summarize_samples(samples)
            group = {field: meta[field] for field in ("run_id", "run_kind", "size", "distribution", "seed", "query_seed",
                     "input_hash_fnv1a64", "batch_size", "nearly_sorted_swaps", "duplicate_cardinality",
                     "dataset_generator", "query_generator", "compiler_id", "compiler_version", "build_type", "sanitizers", "platform", "architecture")}
            group.update(algorithm=algorithm, query_category=entry["category"],
                         query_hash_fnv1a64=entry["query_hash_fnv1a64"], hit_queries=entry["hit_queries"], miss_queries=entry["miss_queries"],
                         successful_trials=stats["successful_trials"], failed_trials=len(selected)-len(samples),
                         missing_measured_trials=meta["repetitions"]-len(selected), run_complete=complete)
            warmups = [row for row in data if row["phase"] == "warmup" and
                       (row["algorithm"], row["query_category"]) == (algorithm, entry["category"])]
            group.update(warmup_rows=len(warmups), failed_warmups=sum(row["status"] != "ok" for row in warmups))
            for name in ("median", "mean", "stdev", "min", "max"):
                value = stats[name+"_ns"]
                group[name+"_batch_ns"] = value
                group[name+"_normalized_ns_per_query"] = value/meta["batch_size"] if value is not None else None
            groups.append(group)
    availability = [dict(entry, run_id=meta["run_id"], size=meta["size"], distribution=meta["distribution"],
                         seed=meta["seed"], query_seed=meta["query_seed"]) for entry in categories]
    return complete, groups, availability


def analyze(source, allow_incomplete=False):
    matrix_path = source / "matrix.json"
    missing, groups, availability = [], [], []
    complete = True
    if matrix_path.exists():
        matrix = json.loads(matrix_path.read_text())
        names = matrix["runs"]
        if matrix.get("schema_version") != 1 or matrix.get("protocol") != "search_batch_v1" or not names or \
                len(set(names)) != len(names) or any(Path(name).name != name or name in (".", "..") for name in names) or \
                len(matrix["commands"]) != len(names):
            raise ValueError("invalid search matrix plan")
        directories = [source/name for name in names]
        complete = (source/"COMPLETE.json").exists()
        if complete:
            marker = json.loads((source/"COMPLETE.json").read_text())
            if marker.get("schema_version") != 1 or marker.get("complete") is not True or marker.get("runs") != len(names) or (source/"FAILED.json").exists():
                raise ValueError("invalid matrix completion")
            for name, command in zip(names, matrix["commands"]):
                record = json.loads((source/(name+"_command.json")).read_text())
                if record["exit_code"] != 0 or record["command"] != command:
                    raise ValueError("completed matrix has failed/mismatched child")
        elif not allow_incomplete:
            raise ValueError("incomplete search matrix")
    else:
        directories = [source]
    for directory in directories:
        if not (directory/"run.json").exists():
            if not allow_incomplete:
                raise ValueError("missing planned search run")
            complete = False
            missing.append(str(directory))
            continue
        done, run_groups, run_availability = read_bundle(directory, allow_incomplete)
        if matrix_path.exists() and json.loads((directory/"run.json").read_text())["invocation"] != matrix["commands"][names.index(directory.name)]:
            raise ValueError("child invocation differs from matrix plan")
        complete = complete and done
        groups.extend(run_groups)
        availability.extend(run_availability)
    return {"schema_version": 1, "summary_kind": "search_batch_summary", "source": str(source.resolve()),
            "complete": complete, "elapsed_unit": "ns", "outlier_policy": "retain_all",
            "stdev_definition": "sample_ddof_1; null below two successes",
            "normalized_latency_definition": "batch_ns/batch_size; not measured individual-query duration",
            "missing_runs": missing, "availability": availability, "groups": groups}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    try:
        result = analyze(args.source, args.allow_incomplete)
        serialized = json.dumps(result, indent=2, allow_nan=False)+"\n"
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(serialized)
    except (OSError, ValueError, KeyError, TypeError, csv.Error, ZeroDivisionError) as error:
        parser.exit(1, f"search analysis failed: {error}\n")
    print(args.output)
    if not result["complete"]:
        parser.exit(1, "incomplete/failed search results retained\n")


if __name__ == "__main__":
    main()
