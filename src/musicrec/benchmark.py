"""Full-catalog benchmark for the app's track search.

Times SearchEngine.search_tracks end to end, on the engine configuration the Dash
app builds (web/app.py), over a fixed query set drawn from the catalog. Run it
from the repository root:

    PYTHONHASHSEED=0 MUSICREC_ENV=production python -m src.musicrec.benchmark

PYTHONHASHSEED is fixed because the fuzzy phase sorts its trigram candidates by
overlap count only, so tied candidates keep set iteration order and the top-100
cut depends on the hash seed. MUSICREC_ENV=production is the value render.yaml
sets; it skips the similarity graph, which the search engine never reads.
"""

import argparse
import contextlib
import datetime
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import random
import re
import statistics
import subprocess  # nosec B404
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

DEFAULT_SEED = 20261012
EXPECTED_CATALOG_TRACKS = 55446
DEFAULT_QUERIES = Path("benchmarks") / "queries.json"
RESULTS_DIR = Path("benchmarks") / "results"
REPO_ROOT = Path(__file__).resolve().parents[2]

WARMUP = "warmup"
GROUPS = ("exact", "derived", "hand")
SUMMARY_GROUPS = (
    ("exact", ("exact",)),
    ("derived", ("derived",)),
    ("hand", ("hand",)),
    ("fuzzy", ("derived", "hand")),
)
EDIT_KINDS = ("swap", "drop", "next_letter")
PERCENTILE_METHOD = (
    "nearest rank: sort the n values and take the one at 1-based rank "
    "ceil(p * n / 100); a cold-pass percentile is one measured call, and a "
    "repeated-pass percentile is one query's median of runs 2 to repeats"
)

# Misspellings typed by hand of artist and track names read from the catalog, as
# (query, catalog name, field). Nine are single swaps or drops like the derived
# group's; the other eleven are edits the generator never makes: five letter
# substitutions, three doubled letters, one name with both double letters
# collapsed, a dropped accent and a missing space.
HAND_QUERIES: Tuple[Tuple[str, str, str], ...] = (
    ("podingten bear", "podington bear", "artist"),
    ("josh woodard", "josh woodward", "artist"),
    ("mati palanen", "matti paalanen", "artist"),
    ("gregoire lourme", "grégoire lourme", "artist"),
    ("akashik records", "akashic records", "artist"),
    ("juice conection", "juice connection", "artist"),
    ("torely on piano", "torley on piano", "artist"),
    ("igor pumfonia", "igor pumphonia", "artist"),
    ("alexandr lisenkov", "alexander lisenkov", "artist"),
    ("fresh bodyshop", "fresh body shop", "artist"),
    ("age of dinosuars", "age of dinosaurs", "track"),
    ("small town industy", "small town industry", "track"),
    ("monotany of rain", "monotony of rain", "track"),
    ("haunted hosue", "haunted house", "track"),
    ("rainning clocks", "raining clocks", "track"),
    ("a night in serengetti", "a night in serengeti", "track"),
    ("that possitive feeling", "that positive feeling", "track"),
    ("tatered and torn", "tattered and torn", "track"),
    ("pirate anthum", "pirate anthem", "track"),
    ("morning breze", "morning breeze", "track"),
)


def percentile(values: Sequence[float], p: float) -> float:
    """Return the p-th percentile of values by the nearest-rank method.

    The values are sorted and the one at 1-based rank ceil(p * n / 100) is
    returned, so the result is always one of the input values. Multiplying before
    dividing keeps whole-number ranks exact in floating point.

    Args:
        values: The values to rank, at least one
        p: The percentile, greater than 0 and at most 100

    Returns:
        The value at the nearest rank

    Raises:
        ValueError: If values is empty or p is outside (0, 100]
    """
    if not values:
        raise ValueError("percentile() needs at least one value")
    if not 0 < p <= 100:
        raise ValueError(f"p must be in (0, 100], got {p}")
    ordered = sorted(values)
    rank = math.ceil(p * len(ordered) / 100)
    return ordered[rank - 1]


def _apply_edit(text: str, kind: str, pos: int) -> Optional[str]:
    """Apply one edit at interior position pos, or return None if it cannot apply.

    Args:
        text: A normalized name
        kind: "swap" (pos and pos + 1), "drop" or "next_letter" (a to b, z to a)
        pos: The position to edit; the first and last characters are never edited

    Returns:
        The edited string, or None when the edit does not apply at pos
    """
    last = len(text) - 1
    if not 0 < pos < last:
        return None
    if kind == "swap":
        if pos + 1 >= last or not (text[pos].isalpha() and text[pos + 1].isalpha()):
            return None
        return text[:pos] + text[pos + 1] + text[pos] + text[pos + 2 :]
    if kind == "drop":
        if not text[pos].isalpha():
            return None
        return text[:pos] + text[pos + 1 :]
    if kind == "next_letter":
        if not "a" <= text[pos] <= "z":
            return None
        replacement = chr((ord(text[pos]) - ord("a") + 1) % 26 + ord("a"))
        return text[:pos] + replacement + text[pos + 1 :]
    raise ValueError(f"unknown edit kind: {kind}")


def derive_typo(
    name: str, kind_index: int, start_pos: int, taken: Set[str]
) -> Optional[Tuple[str, str, int]]:
    """Make a one-edit typo of a normalized name.

    Tries EDIT_KINDS[kind_index] at start_pos first. An edit that does not apply,
    leaves the name unchanged (swapping a doubled letter), leaves fewer than three
    characters or produces a string in taken falls through to the next edit kind,
    then to the next interior position.

    Args:
        name: The normalized source name
        kind_index: Index into EDIT_KINDS of the edit to try first
        start_pos: The interior position to try first
        taken: Strings the typo must not equal

    Returns:
        (typo, edit kind, position), or None when no edit works
    """
    interior = list(range(1, len(name) - 1))
    if not interior:
        return None
    first = interior.index(start_pos) if start_pos in interior else 0
    for pos in interior[first:] + interior[:first]:
        for step in range(len(EDIT_KINDS)):
            kind = EDIT_KINDS[(kind_index + step) % len(EDIT_KINDS)]
            typo = _apply_edit(name, kind, pos)
            if typo is None or typo == name or len(typo) < 3 or typo in taken:
                continue
            return typo, kind, pos
    return None


def sample_queries(
    tracks: Dict[str, Any],
    seed: int = DEFAULT_SEED,
    n_exact: int = 200,
    n_fuzzy: int = 200,
    n_warmup: int = 20,
    hand: Iterable[Tuple[str, str, str]] = HAND_QUERIES,
) -> List[Dict[str, Any]]:
    """Draw the fixed query set from a catalog.

    The track ids are walked in sorted order shuffled by random.Random(seed), so
    the draw depends only on the catalog and the seed. Each track name is
    normalized as the search index does (lower().strip()); non-string names, names
    under three characters, names equal to their track id and names already drawn
    are skipped. The first n_exact names become exact queries (the name itself, so
    phase 1 scores it 1.0), the next names become n_fuzzy derived queries with one
    edit each (the edit kind cycles swap, drop, next letter), and the next n_warmup
    names, alternating the name and a typo of it, become the warm-up set.

    Args:
        tracks: genre_tree.tracks, track id to node
        seed: Seed for the walk order and the edit positions
        n_exact: Number of exact queries
        n_fuzzy: Number of derived (one-edit typo) queries
        n_warmup: Number of warm-up queries, run before timing
        hand: Hand-typed misspellings as (query, source, field), appended last

    Returns:
        Query rows: warm-up, exact, derived, then hand

    Raises:
        ValueError: If the catalog has too few eligible names
    """
    rng = random.Random(seed)
    order = sorted(tracks)
    rng.shuffle(order)

    hand_rows = [
        {"group": "hand", "query": query, "source": source, "field": field}
        for query, source, field in hand
    ]
    # seen holds every source name drawn; taken holds every query string emitted,
    # so no two queries collide and no name is used twice.
    taken: Set[str] = {row["query"] for row in hand_rows}
    seen: Set[str] = set()
    exact: List[Dict[str, Any]] = []
    derived: List[Dict[str, Any]] = []
    warmup: List[Dict[str, Any]] = []

    for track_id in order:
        if (len(exact), len(derived), len(warmup)) == (n_exact, n_fuzzy, n_warmup):
            break
        name = tracks[track_id].data.get("track_name")
        if not isinstance(name, str):
            continue
        normalized = name.lower().strip()
        if (
            len(normalized) < 3
            or normalized == str(track_id).lower().strip()
            or normalized in seen
            or normalized in taken
        ):
            continue
        seen.add(normalized)

        if len(exact) < n_exact:
            exact.append({"group": "exact", "query": normalized, "track_id": track_id})
            taken.add(normalized)
            continue

        if len(derived) < n_fuzzy:
            start = rng.randrange(1, len(normalized) - 1)
            made = derive_typo(normalized, len(derived) % len(EDIT_KINDS), start, taken)
            if made is None:
                continue
            typo, kind, pos = made
            derived.append(
                {
                    "group": "derived",
                    "query": typo,
                    "source": normalized,
                    "track_id": track_id,
                    "edit": f"{kind}@{pos}",
                }
            )
            taken.add(typo)
            continue

        query = normalized
        if len(warmup) % 2:
            start = rng.randrange(1, len(normalized) - 1)
            made = derive_typo(normalized, len(warmup) % len(EDIT_KINDS), start, taken)
            if made is None:
                continue
            query = made[0]
        warmup.append({"group": WARMUP, "query": query, "track_id": track_id})
        taken.add(query)

    if len(exact) < n_exact or len(derived) < n_fuzzy or len(warmup) < n_warmup:
        raise ValueError(
            f"catalog has too few eligible names: drew {len(exact)} exact, "
            f"{len(derived)} derived and {len(warmup)} warm-up queries, needed "
            f"{n_exact}, {n_fuzzy} and {n_warmup}"
        )

    queries = warmup + exact + derived + hand_rows
    check_queries(queries)
    return queries


def check_queries(queries: List[Dict[str, Any]]) -> None:
    """Reject a query set the benchmark would mis-measure.

    Queries are compared as search_tracks sees them, after lower().strip(), so a
    repeat that differs only in case or spacing cannot reach the cold pass with
    its similarity pairs already cached.

    Args:
        queries: Query rows with "group", "query" and, for misspellings, "source"

    Raises:
        ValueError: On an unknown group, a query under three characters after
            normalization, a repeated query, or a misspelling equal to its source
    """
    seen: Set[str] = set()
    for row in queries:
        group, query = row.get("group"), row.get("query")
        if group not in GROUPS and group != WARMUP:
            raise ValueError(f"unknown query group: {group!r}")
        if not isinstance(query, str) or len(query.lower().strip()) < 3:
            raise ValueError(f"query shorter than three characters: {query!r}")
        key = query.lower().strip()
        if key in seen:
            raise ValueError(f"query appears twice: {query!r}")
        source = str(row.get("source", "")).lower().strip()
        if group in ("derived", "hand") and key == source:
            raise ValueError(f"misspelling equals its source: {query!r}")
        seen.add(key)


def missing_hand_sources(
    tracks: Dict[str, Any], hand: Iterable[Tuple[str, str, str]] = HAND_QUERIES
) -> List[Tuple[str, str, str]]:
    """Find hand-typed queries whose source name is not in the catalog.

    Args:
        tracks: genre_tree.tracks, track id to node
        hand: Hand-typed misspellings as (query, source, field)

    Returns:
        The rows whose source is not a normalized track name (field "track") or
        artist name (field "artist") in the catalog
    """
    names: Dict[str, Set[str]] = {"track": set(), "artist": set()}
    for node in tracks.values():
        for field, key in (("track", "track_name"), ("artist", "artist_name")):
            value = node.data.get(key)
            if isinstance(value, str):
                names[field].add(value.lower().strip())
    return [row for row in hand if row[1] not in names.get(row[2], set())]


def _digest(results: List[Dict[str, Any]]) -> str:
    """Fingerprint a result list (track ids, match types and scores, in order)."""
    key = [[row["track_id"], row["match_type"], row["score"]] for row in results]
    return hashlib.sha256(json.dumps(key).encode("utf-8")).hexdigest()[:16]


def _cache_delta(before: Any, after: Any) -> Dict[str, int]:
    """Hits and misses between two cache_info() snapshots."""
    return {"hits": after.hits - before.hits, "misses": after.misses - before.misses}


def _timed_search(engine: Any, query: str) -> Tuple[int, int, List[Any], Any]:
    """Run one search, timing only the search_tracks call.

    Args:
        engine: The SearchEngine
        query: The query string, as typed

    Returns:
        Wall nanoseconds (perf_counter_ns), thread CPU nanoseconds, the results and
        the similarity cache delta. Wall time far above CPU time means the process
        waited for a core.
    """
    cache = engine._calculate_similarity_cached
    before = cache.cache_info()
    cpu_start = time.thread_time_ns()
    start = time.perf_counter_ns()
    results = engine.search_tracks(query)
    elapsed = time.perf_counter_ns() - start
    cpu = time.thread_time_ns() - cpu_start
    return elapsed, cpu, results, _cache_delta(before, cache.cache_info())


def _sum_deltas(deltas: Iterable[Dict[str, int]]) -> Dict[str, int]:
    """Add up cache deltas."""
    total = {"hits": 0, "misses": 0}
    for delta in deltas:
        total["hits"] += delta["hits"]
        total["misses"] += delta["misses"]
    return total


def _stats_ms(values_ns: List[float]) -> Dict[str, float]:
    """p50, p95 and max of nanosecond values, in milliseconds."""
    return {
        "p50": round(percentile(values_ns, 50) / 1e6, 3),
        "p95": round(percentile(values_ns, 95) / 1e6, 3),
        "max": round(max(values_ns) / 1e6, 3),
    }


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Per-group counts, latency percentiles and cache totals.

    Queries are grouped by how they were made, never by the top result's match
    type; "fuzzy" is derived and hand together.

    Args:
        records: Per-query records from run_benchmark

    Returns:
        Group name to its summary, for the groups present in records
    """
    summary: Dict[str, Dict[str, Any]] = {}
    for name, members in SUMMARY_GROUPS:
        rows = [row for row in records if row["group"] in members]
        if not rows:
            continue
        summary[name] = {
            "members": list(members),
            "n": len(rows),
            "top_exact": sum(row["top_match_type"] == "exact" for row in rows),
            "phase2_ran": sum(row["phase2_ran"] for row in rows),
            "any_fuzzy": sum(row["n_fuzzy"] > 0 for row in rows),
            "query_is_index_key": sum(row["query_is_index_key"] for row in rows),
            "results_stable": sum(row["results_stable"] for row in rows),
            "cold_ms": _stats_ms([row["cold_ns"] for row in rows]),
            "repeated_ms": _stats_ms([row["repeated_ns_median"] for row in rows]),
            "cold_cpu_ms": _stats_ms([row["cold_cpu_ns"] for row in rows]),
            "cache": {
                "cold": _sum_deltas(row["cold_cache"] for row in rows),
                "repeated": _sum_deltas(
                    delta for row in rows for delta in row["repeated_cache"]
                ),
            },
        }
    return summary


def run_benchmark(
    engine: Any,
    queries: List[Dict[str, Any]],
    repeats: int = 5,
    seed: int = DEFAULT_SEED,
) -> Dict[str, Any]:
    """Time engine.search_tracks over a query set, on the engine's live cache.

    Three passes: the warm-up queries once each, in file order and not recorded;
    a cold pass that runs every measured query once, in an order shuffled with
    seed; and a repeated pass that runs each query repeats times back to back, in
    the same order, keeping the median of runs 2 to repeats. The similarity cache
    is never cleared, as in the app, and its hits and misses are recorded around
    every timed call.

    Args:
        engine: The SearchEngine to time
        queries: Query rows; rows in the warm-up group are run but not measured
        repeats: Runs per query in the repeated pass, at least 2
        seed: Seed for the cold-pass order

    Returns:
        The per-query records (in file order), per-group summaries, the warm-up
        cache delta and the cache totals after the run

    Raises:
        ValueError: If repeats is below 2 or the query set fails check_queries
    """
    if repeats < 2:
        raise ValueError(f"repeats must be at least 2, got {repeats}")
    check_queries(queries)
    cache = engine._calculate_similarity_cached
    warmup = [row for row in queries if row["group"] == WARMUP]
    measured = [row for row in queries if row["group"] != WARMUP]

    started = time.perf_counter()
    before = cache.cache_info()
    for row in warmup:
        engine.search_tracks(row["query"])
    warmup_cache = _cache_delta(before, cache.cache_info())

    order = list(range(len(measured)))
    random.Random(seed).shuffle(order)
    records: List[Dict[str, Any]] = [{} for _ in measured]
    for index in order:
        row = measured[index]
        elapsed, cpu, results, delta = _timed_search(engine, row["query"])
        # Everything below runs after the timed call returns.
        n_exact = sum(result["match_type"] == "exact" for result in results)
        records[index] = {
            "group": row["group"],
            "query": row["query"],
            "query_is_index_key": row["query"] in engine._exact_index,
            "n_results": len(results),
            "n_exact": n_exact,
            "n_fuzzy": sum(result["match_type"] == "fuzzy" for result in results),
            "top_match_type": results[0]["match_type"] if results else None,
            "top_score": results[0]["score"] if results else None,
            "phase2_ran": n_exact < engine.max_results,
            "result_digest": _digest(results),
            "cold_ns": elapsed,
            "cold_cpu_ns": cpu,
            "cold_cache": delta,
        }

    for index in order:
        record = records[index]
        runs: List[int] = []
        cpu_runs: List[int] = []
        deltas: List[Dict[str, int]] = []
        stable = True
        for _ in range(repeats):
            elapsed, cpu, results, delta = _timed_search(engine, record["query"])
            runs.append(elapsed)
            cpu_runs.append(cpu)
            deltas.append(delta)
            stable = stable and _digest(results) == record["result_digest"]
        record["repeated_ns"] = runs
        record["repeated_ns_median"] = statistics.median(runs[1:])
        record["repeated_cpu_ns"] = cpu_runs
        record["repeated_cache"] = deltas
        record["results_stable"] = stable

    info = cache.cache_info()
    return {
        "repeats": repeats,
        "order_seed": seed,
        "seconds": round(time.perf_counter() - started, 3),
        "warmup": {"n": len(warmup), "cache": warmup_cache},
        "cache_totals": {
            "hits": info.hits,
            "misses": info.misses,
            "maxsize": info.maxsize,
            "currsize": info.currsize,
        },
        "groups": summarize(records),
        "records": records,
    }


def _run_command(command: List[str]) -> Optional[str]:
    """Run a command from the repository root; return its stdout, or None."""
    try:
        completed = subprocess.run(  # nosec B603
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
            cwd=REPO_ROOT,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout


def _cpu_brand() -> Optional[str]:
    """CPU model from sysctl on macOS or /proc/cpuinfo on Linux, else None."""
    system = platform.system()
    if system == "Darwin":
        out = _run_command(["sysctl", "-n", "machdep.cpu.brand_string"])
        if out is None:
            return None
        return out.strip() or None
    if system == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as cpuinfo:
                for line in cpuinfo:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            return None
    return None


def _load_average() -> Optional[List[float]]:
    """The 1, 5 and 15 minute load averages, or None where unavailable."""
    try:
        return [round(value, 2) for value in os.getloadavg()]
    except (AttributeError, OSError):
        return None


def _git_state() -> Dict[str, Any]:
    """HEAD commit, and whether git status --porcelain lists anything."""
    commit = _run_command(["git", "rev-parse", "HEAD"])
    status = _run_command(["git", "status", "--porcelain"])
    return {
        "commit": commit.strip() if commit else None,
        "dirty": bool(status.strip()) if status is not None else None,
    }


def _package_versions() -> Dict[str, Optional[str]]:
    """Installed versions of every package named in requirements.txt."""
    versions: Dict[str, Optional[str]] = {}
    try:
        lines = (REPO_ROOT / "requirements.txt").read_text().splitlines()
    except OSError:
        return versions
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        name = re.split(r"[<>=!~;\[ ]", line, maxsplit=1)[0]
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def _peak_rss() -> Optional[Dict[str, Any]]:
    """Peak resident set size of this process, from getrusage, with its unit."""
    try:
        import resource
    except ImportError:
        return None
    return {
        "value": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "unit": "bytes" if platform.system() == "Darwin" else "kilobytes",
        "scope": "the whole benchmark process: catalog load, index build, searches",
    }


def count_data_rows(paths: Iterable[str]) -> Dict[str, Optional[int]]:
    """Count the rows of each data file as its lines minus the header line.

    Args:
        paths: Data file paths

    Returns:
        Path to row count, or None for a file that cannot be read
    """
    rows: Dict[str, Optional[int]] = {}
    for path in paths:
        lines = 0
        last = b"\n"
        try:
            with open(path, "rb") as data_file:
                for chunk in iter(lambda: data_file.read(1 << 20), b""):
                    lines += chunk.count(b"\n")
                    last = chunk[-1:]
        except OSError:
            rows[path] = None
            continue
        if last != b"\n":
            lines += 1
        rows[path] = max(lines - 1, 0)
    return rows


def build_report(
    engine: Any,
    run: Dict[str, Any],
    *,
    mode: str,
    argv: Sequence[str],
    queries_path: Path,
    queries_sha256: str,
    catalog_tracks: int,
    load_seconds: float,
    data_rows: Optional[Dict[str, Optional[int]]],
    load_average_start: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Assemble the results JSON: environment, method, summaries, raw records.

    Args:
        engine: The SearchEngine that was timed
        run: The return value of run_benchmark
        mode: "full" or "sample"
        argv: The command-line arguments after the module name
        queries_path: The query file that was read
        queries_sha256: sha256 of the query file's bytes
        catalog_tracks: len(genre_tree.tracks)
        load_seconds: Wall time of the load and build
        data_rows: Row counts per data file, or None in sample mode
        load_average_start: Load averages taken before the load

    Returns:
        The report, ready for json.dumps or dumps_report
    """
    counts: Dict[str, int] = {}
    for record in run["records"]:
        counts[record["group"]] = counts.get(record["group"], 0) + 1
    counts[WARMUP] = run["warmup"]["n"]
    return {
        "benchmark": "SearchEngine.search_tracks on the app's engine configuration",
        "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "mode": mode,
        "argv": list(argv),
        "argv_note": (
            "sys.argv[1:] of python -m src.musicrec.benchmark; argv[0] is this "
            "module's absolute path on the machine and is left out"
        ),
        "environment": {
            "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
            "hash_seed_fixed": hash_seed_is_fixed(),
            "hash_randomization": sys.flags.hash_randomization,
            "ignore_environment": sys.flags.ignore_environment,
            "MUSICREC_ENV": os.environ.get("MUSICREC_ENV"),
            "RENDER": os.environ.get("RENDER"),
        },
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
            "cpu_brand": _cpu_brand(),
            "load_average_start": load_average_start,
            "load_average_end": _load_average(),
        },
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
        },
        "packages": _package_versions(),
        "git": _git_state(),
        "dataset": {
            "row_count_method": "lines minus the header line",
            "files": data_rows,
            "catalog_tracks": catalog_tracks,
            "expected_catalog_tracks": EXPECTED_CATALOG_TRACKS,
        },
        "engine": {
            "constructor": (
                "SearchEngine(recommender, enable_fuzzy=True, fuzzy_threshold=0.6)"
            ),
            "min_query_length": engine.min_query_length,
            "max_results": engine.max_results,
            "enable_fuzzy": engine.enable_fuzzy,
            "fuzzy_threshold": engine.fuzzy_threshold,
            "fuzzy_method": engine.fuzzy_method,
            "prefilter_top_n": engine.prefilter_top_n,
            "cache_size": engine.cache_size,
            "exact_index_keys": len(engine._exact_index),
            "trigram_index_keys": len(engine._trigram_index),
        },
        "queries": {
            "path": str(queries_path),
            "sha256": queries_sha256,
            "counts": counts,
        },
        "method": {
            "timer": "time.perf_counter_ns() around engine.search_tracks(query)",
            "cpu_timer": (
                "time.thread_time_ns() around the same call; wall time well above "
                "CPU time means the process waited for a core"
            ),
            "warmup": "each warm-up query once before timing; not recorded",
            "cold": "each measured query once, order shuffled with order_seed",
            "repeated": (
                "each query run repeats times back to back; the figure is "
                "statistics.median of runs 2 to repeats, the mean of the middle "
                "two runs when their count is even"
            ),
            "repeats": run["repeats"],
            "order_seed": run["order_seed"],
            "percentile": PERCENTILE_METHOD,
            "phase2_ran": "n_exact < max_results, the condition search_tracks checks",
            "results_stable": (
                "every repeated run returned the cold run's result list; a check "
                "within one process, where search is deterministic"
            ),
            "result_digest": (
                "sha256 prefix of the result list (track ids, match types, scores), "
                "for comparing runs of the same query set"
            ),
            "cache": (
                "the engine's similarity LRU cache is never cleared; hits and "
                "misses are cache_info() deltas around each timed call"
            ),
            "gc": "garbage collection stays enabled, as in the app",
        },
        "load_and_build_seconds": round(load_seconds, 3),
        "load_and_build_note": (
            "wall time of load_data, MusicRecommender and SearchEngine in this "
            "process, after the imports; recorded for the workflow's runtime, not a "
            "startup figure"
        ),
        "timed_passes_seconds": run["seconds"],
        "peak_rss": _peak_rss(),
        "cache": {
            "totals": run["cache_totals"],
            "warmup": run["warmup"]["cache"],
            "per_group": {
                name: group["cache"] for name, group in run["groups"].items()
            },
        },
        "groups": run["groups"],
        "records": run["records"],
    }


def _dump_with_rows(head: Dict[str, Any], key: str, rows: List[Any]) -> str:
    """JSON text with head indented and rows under key, one object per line."""
    if key in head:
        raise ValueError(f"{key!r} is written last and must not be in head")
    text = json.dumps({**head, key: []}, indent=2, ensure_ascii=False)
    body = ",\n    ".join(json.dumps(row, ensure_ascii=False) for row in rows)
    return text[: -len("[]\n}")] + "[\n    " + body + "\n  ]\n}\n"


def dumps_report(report: Dict[str, Any]) -> str:
    """Serialize a report with one record per line."""
    head = {key: value for key, value in report.items() if key != "records"}
    return _dump_with_rows(head, "records", report["records"])


def write_query_file(
    path: Path, queries: List[Dict[str, Any]], catalog_tracks: int, seed: int
) -> None:
    """Write a checked query set to path, one query per line.

    Args:
        path: The query file to write
        queries: Query rows from sample_queries
        catalog_tracks: Size of the catalog they were drawn from
        seed: The seed sample_queries used

    Raises:
        ValueError: If the query set fails check_queries
    """
    check_queries(queries)
    counts: Dict[str, int] = {}
    for row in queries:
        counts[row["group"]] = counts.get(row["group"], 0) + 1
    head = {
        "generated_by": "python -m src.musicrec.benchmark --write-queries",
        "seed": seed,
        "catalog_tracks": catalog_tracks,
        "counts": counts,
        "groups": {
            WARMUP: "run once before timing; names and one-edit typos",
            "exact": "normalized catalog track names",
            "derived": "one-edit typos of other catalog track names",
            "hand": "hand-typed misspellings of catalog artist and track names",
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_dump_with_rows(head, "queries", queries), encoding="utf-8")


def read_query_file(path: Path) -> Tuple[List[Dict[str, Any]], str]:
    """Load and check a query file.

    Args:
        path: The query file

    Returns:
        The query rows and the sha256 of the file's bytes

    Raises:
        FileNotFoundError: If path does not exist
        ValueError: If the query set fails check_queries
    """
    raw = path.read_bytes()
    queries = json.loads(raw.decode("utf-8"))["queries"]
    check_queries(queries)
    return queries, hashlib.sha256(raw).hexdigest()


def format_table(report: Dict[str, Any]) -> str:
    """Render the per-group figures as a Markdown table.

    Args:
        report: A report from build_report

    Returns:
        The table, times in milliseconds
    """
    lines = [
        "| group | n | cold p50 ms | cold p95 ms | cold max ms | repeated p50 ms "
        "| repeated p95 ms | phase 2 ran | any fuzzy result |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, group in report["groups"].items():
        label = "fuzzy (derived + hand)" if name == "fuzzy" else name
        cold, repeated = group["cold_ms"], group["repeated_ms"]
        lines.append(
            f"| {label} | {group['n']} | {cold['p50']:.1f} | {cold['p95']:.1f} "
            f"| {cold['max']:.1f} | {repeated['p50']:.1f} | {repeated['p95']:.1f} "
            f"| {group['phase2_ran']} | {group['any_fuzzy']} |"
        )
    return "\n".join(lines)


def hash_seed_is_fixed() -> bool:
    """True when PYTHONHASHSEED holds a number and the interpreter honours it.

    An unset variable, PYTHONHASHSEED=random, or python -E (which ignores PYTHON*
    variables while os.environ still shows them) all leave hashing randomized.
    """
    value = os.environ.get("PYTHONHASHSEED", "")
    return value.isdigit() and not sys.flags.ignore_environment


def load_engine(sample: bool) -> Tuple[Any, Any, float]:
    """Build the recommender and the search engine the way the app does.

    Args:
        sample: Use the sample data instead of the catalog files

    Returns:
        The recommender, the engine, and the wall seconds spent in load_data,
        MusicRecommender and SearchEngine (the imports before them not counted)
    """
    # Imported here so that importing this module stays cheap for the unit tests.
    from .core.engine import MusicRecommender
    from .main import load_data
    from .web.search.engine import SearchEngine

    started = time.perf_counter()
    recommender = MusicRecommender(load_data(use_sample=sample))
    engine = SearchEngine(recommender, enable_fuzzy=True, fuzzy_threshold=0.6)
    return recommender, engine, time.perf_counter() - started


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse the command line and reject combinations the benchmark cannot run."""
    parser = argparse.ArgumentParser(
        prog="python -m src.musicrec.benchmark",
        description="Time the app's track search on the full catalog.",
    )
    parser.add_argument(
        "--queries",
        type=Path,
        default=DEFAULT_QUERIES,
        help=f"query file to read or write (default: {DEFAULT_QUERIES})",
    )
    parser.add_argument(
        "--write-queries",
        action="store_true",
        help="build the catalog, write the query file and exit",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "results JSON path (default: "
            f"{RESULTS_DIR}/<YYYY-MM-DD>-search-full-catalog.json, or "
            "<YYYY-MM-DD>-search-sample.json with --sample)"
        ),
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
        help="back-to-back runs per query in the repeated pass (default: 5)",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="use the sample data instead of the catalog (a smoke run, not a figure)",
    )
    args = parser.parse_args(argv)
    if args.repeats < 2:
        parser.error("--repeats must be at least 2")
    if args.write_queries and args.sample:
        parser.error("--write-queries draws from the full catalog; drop --sample")
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the benchmark, or write the query file with --write-queries.

    Args:
        argv: Command-line arguments; sys.argv[1:] when None

    Returns:
        The exit status: 0 on success, 1 if the query file is missing, the catalog
        has the wrong size or a hand-typed source is not in it
    """
    args_list = list(sys.argv[1:] if argv is None else argv)
    args = _parse_args(args_list)
    if not hash_seed_is_fixed():
        print(
            "warning: the hash seed is not fixed (PYTHONHASHSEED unset or random, "
            "or ignored under python -E), so the fuzzy candidate cut changes from "
            "run to run; run with PYTHONHASHSEED=0",
            file=sys.stderr,
        )
    os.environ.setdefault("MUSICREC_ENV", "production")

    # Read the query file before the slow catalog load, so a missing file fails fast.
    queries: List[Dict[str, Any]] = []
    queries_sha256 = ""
    if not args.write_queries:
        try:
            queries, queries_sha256 = read_query_file(args.queries)
        except FileNotFoundError:
            print(
                f"Query file not found: {args.queries}; write it with --write-queries",
                file=sys.stderr,
            )
            return 1

    load_average_start = _load_average()
    with contextlib.redirect_stdout(sys.stderr):
        recommender, engine, load_seconds = load_engine(args.sample)

    tracks = recommender.genre_tree.tracks
    if args.sample:
        print(f"Catalog check skipped (--sample): {len(tracks)} sample tracks")
    elif len(tracks) != EXPECTED_CATALOG_TRACKS:
        print(
            f"Catalog check failed: len(genre_tree.tracks) == {len(tracks)}, "
            f"expected {EXPECTED_CATALOG_TRACKS}",
            file=sys.stderr,
        )
        return 1
    else:
        print(f"Catalog check: len(genre_tree.tracks) == {len(tracks)}")

    if args.write_queries:
        missing = missing_hand_sources(tracks)
        if missing:
            print(f"Hand-typed sources not in the catalog: {missing}", file=sys.stderr)
            return 1
        queries = sample_queries(tracks)
        write_query_file(args.queries, queries, len(tracks), DEFAULT_SEED)
        print(f"Wrote {len(queries)} queries to {args.queries}")
        return 0

    run = run_benchmark(engine, queries, repeats=args.repeats)
    data_rows = None
    if not args.sample:
        from .config.settings import get_data_paths

        paths = get_data_paths()
        data_rows = count_data_rows(
            paths[key]
            for key in ("spotify_path", "genre_path", "mood_path", "metadata_path")
        )
    report = build_report(
        engine,
        run,
        mode="sample" if args.sample else "full",
        argv=args_list,
        queries_path=args.queries,
        queries_sha256=queries_sha256,
        catalog_tracks=len(tracks),
        load_seconds=load_seconds,
        data_rows=data_rows,
        load_average_start=load_average_start,
    )
    output = args.output
    if output is None:
        suffix = "sample" if args.sample else "full-catalog"
        today = datetime.date.today().isoformat()
        output = RESULTS_DIR / f"{today}-search-{suffix}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(dumps_report(report), encoding="utf-8")
    print(format_table(report))
    print(f"Results: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
