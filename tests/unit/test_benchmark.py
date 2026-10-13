"""Unit tests for the full-catalog search benchmark in benchmark.py.

These check the sampler, the percentile definition, the timing harness and the
report shape on a small Mock catalog. Nothing here asserts a timing threshold.
"""

import hashlib
import json
import platform
import random
import re
import statistics
from collections import Counter
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.musicrec import benchmark
from src.musicrec.benchmark import (
    DEFAULT_SEED,
    EDIT_KINDS,
    HAND_QUERIES,
    REPO_ROOT,
    build_report,
    check_queries,
    count_data_rows,
    derive_typo,
    dumps_report,
    format_table,
    main,
    percentile,
    read_query_file,
    run_benchmark,
    sample_queries,
    write_query_file,
)
from src.musicrec.web.search.engine import SearchEngine

DOUBLE_LETTER_NAME = "Moonlight Ballad"


def make_tracks():
    """The 1,000-track fixture from test_search_performance.py, plus one name with
    doubled letters."""
    tracks = {}
    artists = ["Artist A", "Artist B", "Artist C", "Artist D", "Artist E"]
    genres = ["Pop", "Rock", "Hip Hop", "Electronic", "Jazz"]

    for i in range(1000):
        track_id = f"track{i:04d}"
        artist = artists[i % len(artists)]
        genre = genres[i % len(genres)]
        track_name = f"{genre} Song {i:04d}"

        tracks[track_id] = Mock(data={"track_name": track_name, "artist_name": artist})

    tracks["track1000"] = Mock(
        data={"track_name": DOUBLE_LETTER_NAME, "artist_name": "Artist A"}
    )
    return tracks


def make_engine(tracks, **options):
    """Build a search engine over tracks, by default with web/app.py's arguments."""
    recommender = Mock()
    recommender.genre_tree.tracks = tracks
    return SearchEngine(
        recommender, **{"enable_fuzzy": True, "fuzzy_threshold": 0.6, **options}
    )


def install_clock(monkeypatch, durations_ns):
    """Script perf_counter_ns so the k-th timed search takes durations_ns[k], cycling."""
    clock = {"now": 0, "calls": 0}

    def fake_perf_counter_ns():
        clock["calls"] += 1
        if clock["calls"] % 2 == 0:
            searches = clock["calls"] // 2
            clock["now"] += durations_ns[(searches - 1) % len(durations_ns)]
        return clock["now"]

    monkeypatch.setattr(benchmark.time, "perf_counter_ns", fake_perf_counter_ns)


def write_small_query_file(path, tracks):
    """Write a 12-query file drawn from tracks and return its path."""
    queries = sample_queries(tracks, n_exact=5, n_fuzzy=5, n_warmup=2, hand=())
    write_query_file(path, queries, len(tracks), 7)
    return path


@pytest.fixture
def tracks():
    """The Mock catalog: 1,000 fixture tracks and one doubled-letter name."""
    return make_tracks()


@pytest.fixture
def engine(tracks):
    """A search engine built with the arguments web/app.py uses."""
    return make_engine(tracks)


def test_sample_queries_is_deterministic(tracks):
    """Test that the draw depends only on the catalog and the seed."""
    first = sample_queries(tracks, n_exact=50, n_fuzzy=50)
    second = sample_queries(tracks, n_exact=50, n_fuzzy=50)
    reversed_tracks = dict(reversed(list(tracks.items())))

    assert first == second
    assert sample_queries(reversed_tracks, n_exact=50, n_fuzzy=50) == first
    assert sample_queries(tracks, seed=1, n_exact=50, n_fuzzy=50) != first


# n_exact=0 sends every name to the derived draw, where a repeated name is not
# already blocked by the exact queries.
@pytest.mark.parametrize("n_exact", [3, 0])
def test_sample_queries_skips_short_names_track_ids_and_repeats(tracks, n_exact):
    """Test that only string names of three or more characters, unlike their
    track id and not drawn before, become queries."""
    small = {track_id: tracks[track_id] for track_id in sorted(tracks)[:5]}
    eligible = {node.data["track_name"].lower() for node in small.values()}
    small["short"] = Mock(data={"track_name": " Go ", "artist_name": "Artist B"})
    small["named_after_id"] = Mock(
        data={"track_name": "Named_After_Id", "artist_name": "Artist C"}
    )
    small["not_a_string"] = Mock(data={"track_name": None, "artist_name": "Artist D"})
    small["nan_name"] = Mock(data={"track_name": float("nan"), "artist_name": "E"})
    small["repeat"] = Mock(data={"track_name": "POP SONG 0000", "artist_name": "Z"})
    n_fuzzy = len(eligible) - n_exact
    counts = {"n_exact": n_exact, "n_warmup": 0, "hand": ()}

    queries = sample_queries(small, n_fuzzy=n_fuzzy, **counts)

    assert {row.get("source", row["query"]) for row in queries} == eligible
    assert all(len(row["query"]) >= 3 for row in queries)
    with pytest.raises(ValueError, match="too few eligible names"):
        sample_queries(small, n_fuzzy=n_fuzzy + 1, **counts)


def test_three_character_names_are_long_enough():
    """Test the boundary: a three-character name is a query, a two-character typo
    is not."""
    catalog = {"t1": Mock(data={"track_name": "Run", "artist_name": "A"})}

    queries = sample_queries(catalog, n_exact=1, n_fuzzy=0, n_warmup=0, hand=())

    assert queries == [{"group": "exact", "query": "run", "track_id": "t1"}]
    # Dropping the middle letter would leave "rn", so the next edit is used.
    assert derive_typo("run", 1, 1, set()) == ("rvn", "next_letter", 1)


def test_exact_queries_score_one_on_the_app_engine(tracks, engine):
    """Test that every exact query's top result is an exact match scored 1.0."""
    queries = sample_queries(tracks, n_exact=50, n_fuzzy=10, n_warmup=0, hand=())
    exact = [row for row in queries if row["group"] == "exact"]

    assert len(exact) == 50
    for row in exact:
        top = engine.search_tracks(row["query"])[0]
        assert top["match_type"] == "exact"
        assert top["score"] == 1.0


def test_derived_queries_differ_from_their_source(tracks):
    """Test that every derived query is a real edit and the edit kinds rotate."""
    queries = sample_queries(tracks, n_exact=0, n_fuzzy=len(tracks), n_warmup=0)
    derived = [row for row in queries if row["group"] == "derived"]
    doubled = [row for row in derived if row["source"] == "moonlight ballad"]
    kinds = Counter(row["edit"].split("@")[0] for row in derived)

    assert len(derived) == len(tracks)
    assert all(row["query"] != row["source"] for row in derived)
    assert len(doubled) == 1
    assert doubled[0]["query"] != "moonlight ballad"
    assert all(kinds[kind] >= len(derived) // 5 for kind in EDIT_KINDS)


def test_sampler_moves_on_when_a_swap_changes_nothing():
    """Test that the draw falls through when swapping equal letters leaves the
    name as it was."""
    catalog = {"t1": Mock(data={"track_name": "Aaaaaaaa", "artist_name": "A"})}

    (row,) = sample_queries(catalog, n_exact=0, n_fuzzy=1, n_warmup=0, hand=())

    assert row["query"] != "aaaaaaaa"
    assert row["edit"].startswith("drop")


def test_derive_typo_falls_through_on_a_doubled_letter():
    """Test that no start position or edit kind returns the name unchanged."""
    name = DOUBLE_LETTER_NAME.lower()

    for kind_index in range(len(EDIT_KINDS)):
        for pos in range(1, len(name) - 1):
            typo, _, _ = derive_typo(name, kind_index, pos, set())
            assert typo != name
    # Swapping the doubled "oo" changes nothing, so the drop edit is used instead.
    assert derive_typo(name, 0, 1, set()) == ("monlight ballad", "drop", 1)
    assert derive_typo(name, 0, 1, {"monlight ballad"})[0] == "mponlight ballad"


def test_run_benchmark_counts_phases_and_percentile_order(tracks, engine):
    """Test the record counts, the phase-2 flag and the per-query result fields."""
    queries = sample_queries(tracks, n_exact=20, n_fuzzy=20, n_warmup=4)
    # "pop song" is a substring of 200 names, so phase 1 alone fills 20 results.
    queries.append({"group": "exact", "query": "pop song"})
    expected = Counter(row["group"] for row in queries if row["group"] != "warmup")

    run = run_benchmark(engine, queries, repeats=2)

    assert Counter(record["group"] for record in run["records"]) == expected
    assert run["warmup"]["n"] == 4
    for name in ("exact", "derived", "hand"):
        assert run["groups"][name]["n"] == expected[name]
    assert run["groups"]["fuzzy"]["n"] == expected["derived"] + expected["hand"]

    assert engine.max_results == 20
    phases = [record["phase2_ran"] for record in run["records"]]
    assert True in phases and False in phases
    touched_cache = False
    for record in run["records"]:
        assert record["phase2_ran"] == (record["n_exact"] < 20)
        if record["cold_cache"]["hits"] + record["cold_cache"]["misses"]:
            touched_cache = True
            assert record["phase2_ran"]
        assert len(record["repeated_ns"]) == 2
        assert record["results_stable"]
        results = engine.search_tracks(record["query"])
        types = [result["match_type"] for result in results]
        top = (None, None)
        if results:
            top = (results[0]["match_type"], results[0]["score"])
        assert record["n_results"] == len(results)
        assert record["n_exact"] == types.count("exact")
        assert record["n_fuzzy"] == types.count("fuzzy")
        assert (record["top_match_type"], record["top_score"]) == top
    assert touched_cache

    for group in run["groups"].values():
        for key in ("cold_ms", "repeated_ms", "cold_cpu_ms"):
            stats = group[key]
            assert stats["p50"] <= stats["p95"] <= stats["max"]

    parts = [run["warmup"]["cache"]] + [
        run["groups"][name]["cache"][phase]
        for name in ("exact", "derived", "hand")
        for phase in ("cold", "repeated")
    ]
    assert run["cache_totals"]["hits"] == sum(part["hits"] for part in parts)
    assert run["cache_totals"]["misses"] == sum(part["misses"] for part in parts)


def test_group_summaries_come_from_their_own_records(tracks, engine, monkeypatch):
    """Test that each group's figures and counts are computed from that group's
    records, in milliseconds."""
    install_clock(monkeypatch, [k * 1000 for k in range(1, 400)])
    queries = sample_queries(tracks, n_exact=20, n_fuzzy=20, n_warmup=2)

    run = run_benchmark(engine, queries, repeats=3)

    def ms(values):
        return {
            "p50": round(percentile(values, 50) / 1e6, 3),
            "p95": round(percentile(values, 95) / 1e6, 3),
            "max": round(max(values) / 1e6, 3),
        }

    for name, members in (
        ("exact", {"exact"}),
        ("derived", {"derived"}),
        ("hand", {"hand"}),
        ("fuzzy", {"derived", "hand"}),
    ):
        rows = [record for record in run["records"] if record["group"] in members]
        group = run["groups"][name]
        assert group["cold_ms"] == ms([row["cold_ns"] for row in rows])
        assert group["repeated_ms"] == ms([row["repeated_ns_median"] for row in rows])
        assert group["top_exact"] == sum(
            row["top_match_type"] == "exact" for row in rows
        )
        assert group["phase2_ran"] == sum(row["phase2_ran"] for row in rows)
        assert group["any_fuzzy"] == sum(row["n_fuzzy"] > 0 for row in rows)
        assert group["cache"]["cold"]["misses"] == sum(
            row["cold_cache"]["misses"] for row in rows
        )
    assert run["groups"]["exact"]["cold_ms"] != run["groups"]["derived"]["cold_ms"]


def test_passes_run_warmup_then_shuffled_cold_then_back_to_back(
    tracks, engine, monkeypatch
):
    """Test the call order: warm-up in file order, each measured query once in the
    seeded order, then each query repeated back to back."""
    calls = []
    search = engine.search_tracks

    def spy(query):
        calls.append(query)
        return search(query)

    monkeypatch.setattr(engine, "search_tracks", spy)
    queries = sample_queries(tracks, n_exact=5, n_fuzzy=5, n_warmup=4, hand=())
    warmup = [row["query"] for row in queries if row["group"] == "warmup"]
    measured = [row["query"] for row in queries if row["group"] != "warmup"]
    order = list(range(len(measured)))
    random.Random(DEFAULT_SEED).shuffle(order)
    cold = [measured[index] for index in order]

    run_benchmark(engine, queries, repeats=3)

    assert calls == warmup + cold + [query for query in cold for _ in range(3)]


def test_repeated_figure_is_the_median_of_runs_two_onward(engine, monkeypatch):
    """Test that the repeated figure is the median, not the mean, of runs 2 to 5."""
    install_clock(monkeypatch, [1_000_000, 2_000_000, 4_000_000, 8_000_000, 10**8])
    queries = [
        {"group": "exact", "query": "pop song 0001"},
        {"group": "derived", "query": "pop snog 0002", "source": "pop song 0002"},
    ]

    run = run_benchmark(engine, queries, repeats=5)

    for record in run["records"]:
        later = record["repeated_ns"][1:]
        assert statistics.median(later) != statistics.mean(later)
        assert record["repeated_ns_median"] == statistics.median(later)


@pytest.mark.parametrize(
    "values, p, expected",
    [
        # 0.95 * 100 is a whole number, so this case passes with floor as well.
        (list(range(1, 101)), 95, 95),
        # These two need ceil: rank ceil(9.5) = 10 and rank ceil(1.5) = 2.
        (list(range(1, 11)), 95, 10),
        ([5, 1, 3], 50, 3),
        # Rank ceil(1.2) = 2; rounding to the nearest rank would give 1.
        ([5, 1, 3], 40, 3),
    ],
)
def test_percentile_uses_the_nearest_rank(values, p, expected):
    """Test the nearest-rank definition, rank ceil(p * n / 100)."""
    assert percentile(values, p) == expected


def test_percentile_rejects_an_empty_list():
    """Test that a percentile of nothing is an error, not a default."""
    with pytest.raises(ValueError):
        percentile([], 50)


def requirement_names():
    """Package names listed in requirements.txt."""
    names = set()
    for line in (REPO_ROOT / "requirements.txt").read_text().splitlines():
        match = re.match(r"[A-Za-z0-9._-]+", line.split("#", 1)[0].strip())
        if match:
            names.add(match.group(0))
    return names


def test_build_report_records_what_it_was_given(tracks, monkeypatch):
    """Test that the report round-trips as JSON and reads its values back from the
    engine, the run and the environment."""
    monkeypatch.delenv("PYTHONHASHSEED", raising=False)
    engine = make_engine(
        tracks,
        min_query_length=4,
        max_results=7,
        fuzzy_threshold=0.5,
        prefilter_top_n=50,
        cache_size=64,
    )
    queries = sample_queries(tracks, n_exact=5, n_fuzzy=5, n_warmup=2)
    run = run_benchmark(engine, queries, repeats=2)

    report = build_report(
        engine,
        run,
        mode="sample",
        argv=["--sample"],
        queries_path=Path("benchmarks/queries.json"),
        queries_sha256="ab" * 32,
        catalog_tracks=len(tracks),
        load_seconds=1.5,
        data_rows={"data/example.tsv": 3},
    )

    assert json.loads(json.dumps(report)) == report
    assert json.loads(dumps_report(report)) == report
    assert re.search(r"[+-]\d{2}:\d{2}$", report["timestamp"])
    assert {"platform", "machine", "cpu_count", "cpu_brand"} <= set(report["host"])
    assert {"commit", "dirty"} <= set(report["git"])
    assert report["argv"] == ["--sample"]
    assert report["environment"]["PYTHONHASHSEED"] is None
    assert report["environment"]["hash_seed_fixed"] is False
    assert "MUSICREC_ENV" in report["environment"]
    assert report["python"]["version"] == platform.python_version()
    assert set(report["packages"]) == requirement_names()
    assert report["dataset"]["files"] == {"data/example.tsv": 3}
    assert report["dataset"]["catalog_tracks"] == len(tracks)
    for name in (
        "min_query_length",
        "max_results",
        "enable_fuzzy",
        "fuzzy_threshold",
        "fuzzy_method",
        "prefilter_top_n",
        "cache_size",
    ):
        assert report["engine"][name] == getattr(engine, name)
    assert report["engine"]["max_results"] == 7
    assert report["engine"]["exact_index_keys"] == len(engine._exact_index)
    assert report["engine"]["trigram_index_keys"] == len(engine._trigram_index)
    assert report["queries"] == {
        "path": "benchmarks/queries.json",
        "sha256": "ab" * 32,
        "counts": {"exact": 5, "derived": 5, "hand": 20, "warmup": 2},
    }
    assert report["cache"]["totals"]["maxsize"] == 64
    assert set(report["cache"]["per_group"]) == {"exact", "derived", "hand", "fuzzy"}
    assert {"cold_ms", "repeated_ms", "top_exact", "phase2_ran", "any_fuzzy"} <= set(
        report["groups"]["fuzzy"]
    )
    assert "ceil(p * n / 100)" in report["method"]["percentile"]
    assert report["load_and_build_seconds"] == 1.5
    assert report["peak_rss"]["unit"] in ("bytes", "kilobytes")


def test_query_file_round_trips(tmp_path, tracks):
    """Test that a written query file reads back unchanged, with its digest."""
    queries = sample_queries(tracks, n_exact=5, n_fuzzy=5, n_warmup=2)
    path = tmp_path / "queries.json"

    write_query_file(path, queries, len(tracks), 7)
    loaded, digest = read_query_file(path)

    assert loaded == queries
    assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="appears twice"):
        write_query_file(tmp_path / "bad.json", queries + [queries[-1]], 1, 7)


def test_check_queries_compares_queries_as_search_sees_them():
    """Test that case and spacing do not hide a repeat or a non-typo."""
    with pytest.raises(ValueError, match="appears twice"):
        check_queries(
            [
                {"group": "hand", "query": "haunted hosue"},
                {"group": "hand", "query": " Haunted Hosue "},
            ]
        )
    with pytest.raises(ValueError, match="equals its source"):
        check_queries(
            [{"group": "derived", "query": "Pop Song 0001", "source": "pop song 0001"}]
        )


def test_committed_query_file_has_the_documented_groups():
    """Test that benchmarks/queries.json holds 20 warm-up, 200 exact, 200 derived
    and the hand-typed queries."""
    queries, _ = read_query_file(REPO_ROOT / "benchmarks" / "queries.json")
    hand = [
        (row["query"], row["source"], row["field"])
        for row in queries
        if row["group"] == "hand"
    ]

    assert Counter(row["group"] for row in queries) == {
        "warmup": 20,
        "exact": 200,
        "derived": 200,
        "hand": 20,
    }
    assert hand == list(HAND_QUERIES)


def test_count_data_rows_counts_lines_after_the_header(tmp_path):
    """Test the row counts with and without a final newline, and a missing file."""
    files = {
        "trailing.tsv": "h\n1\n2\n",
        "no_trailing.tsv": "h\n1\n2",
        "head.tsv": "h\n",
    }
    for name, text in files.items():
        (tmp_path / name).write_text(text)
    paths = [str(tmp_path / name) for name in files] + [str(tmp_path / "gone.tsv")]

    assert list(count_data_rows(paths).values()) == [2, 2, 0, None]


def test_format_table_prints_one_row_per_group():
    """Test the table cells: rounded milliseconds and the two counts."""
    group = {
        "n": 200,
        "cold_ms": {"p50": 1.23, "p95": 4.56, "max": 7.89},
        "repeated_ms": {"p50": 0.12, "p95": 0.34, "max": 0.5},
        "phase2_ran": 101,
        "any_fuzzy": 99,
    }
    report = {"groups": {"exact": group, "fuzzy": dict(group, n=220)}}

    lines = format_table(report).splitlines()

    assert lines[2] == "| exact | 200 | 1.2 | 4.6 | 7.9 | 0.1 | 0.3 | 101 | 99 |"
    assert lines[3].startswith("| fuzzy (derived + hand) | 220 | ")


def test_main_runs_on_the_sample_data(tmp_path, tracks, monkeypatch, capsys):
    """Test a smoke run end to end: the warning, the environment default, the
    engine arguments and the table."""
    # setenv records the original state, so teardown also removes the value
    # main() sets with setdefault.
    monkeypatch.setenv("MUSICREC_ENV", "unset-by-the-test")
    monkeypatch.delenv("MUSICREC_ENV")
    monkeypatch.delenv("PYTHONHASHSEED", raising=False)
    query_path = write_small_query_file(tmp_path / "queries.json", tracks)
    output = tmp_path / "results.json"

    args = ["--sample", "--queries", str(query_path), "--output", str(output)]
    assert main(args + ["--repeats", "2"]) == 0

    report = json.loads(output.read_text(encoding="utf-8"))
    captured = capsys.readouterr()
    assert report["mode"] == "sample"
    assert report["dataset"]["files"] is None
    assert report["environment"]["MUSICREC_ENV"] == "production"
    assert report["engine"]["enable_fuzzy"] is True
    assert report["engine"]["fuzzy_threshold"] == 0.6
    assert len(report["records"]) == 10
    assert "the hash seed is not fixed" in captured.err
    assert "| group | n |" in captured.out
    assert "| fuzzy (derived + hand) | 5 |" in captured.out
    with pytest.raises(SystemExit):
        main(["--write-queries", "--sample"])
    with pytest.raises(SystemExit):
        main(args + ["--repeats", "1"])


def test_main_rejects_a_catalog_of_the_wrong_size(
    tmp_path, tracks, monkeypatch, capsys
):
    """Test that a full run on anything but the 55,446-track catalog exits 1 and
    prints the real count."""
    monkeypatch.setenv("MUSICREC_ENV", "production")
    engine = make_engine(tracks)
    monkeypatch.setattr(
        benchmark, "load_engine", lambda sample: (engine.recommender, engine, 0.0)
    )
    query_path = write_small_query_file(tmp_path / "queries.json", tracks)
    output = tmp_path / "results.json"

    assert main(["--queries", str(query_path), "--output", str(output)]) == 1
    assert f"len(genre_tree.tracks) == {len(tracks)}" in capsys.readouterr().err
    assert not output.exists()


def test_main_stops_before_loading_when_the_query_file_is_missing(
    tmp_path, monkeypatch, capsys
):
    """Test that a missing query file fails fast with a pointer to --write-queries."""
    monkeypatch.setenv("MUSICREC_ENV", "production")

    def must_not_load(sample):
        raise AssertionError("the catalog was loaded")

    monkeypatch.setattr(benchmark, "load_engine", must_not_load)

    assert main(["--queries", str(tmp_path / "missing.json")]) == 1
    assert "--write-queries" in capsys.readouterr().err


def test_write_queries_needs_every_hand_source_in_the_catalog(
    tmp_path, tracks, monkeypatch, capsys
):
    """Test that --write-queries refuses a catalog without the hand-typed sources
    and writes the file once they are present."""
    monkeypatch.setenv("MUSICREC_ENV", "production")
    engines = {"current": make_engine(tracks)}
    monkeypatch.setattr(
        benchmark,
        "load_engine",
        lambda sample: (
            engines["current"].recommender,
            engines["current"],
            0.0,
        ),
    )
    monkeypatch.setattr(benchmark, "EXPECTED_CATALOG_TRACKS", len(tracks))
    path = tmp_path / "queries.json"

    assert main(["--write-queries", "--queries", str(path)]) == 1
    assert "Hand-typed sources not in the catalog" in capsys.readouterr().err
    assert not path.exists()

    for i, (_, source, field) in enumerate(HAND_QUERIES):
        data = {"track_name": f"Hand Track {i:02d}", "artist_name": "Artist A"}
        data["track_name" if field == "track" else "artist_name"] = source
        tracks[f"hand{i:02d}"] = Mock(data=data)
    engines["current"] = make_engine(tracks)
    monkeypatch.setattr(benchmark, "EXPECTED_CATALOG_TRACKS", len(tracks))

    assert main(["--write-queries", "--queries", str(path)]) == 0
    queries, _ = read_query_file(path)
    assert Counter(row["group"] for row in queries) == {
        "warmup": 20,
        "exact": 200,
        "derived": 200,
        "hand": 20,
    }
