# Performance Benchmarks

How long the app's track search takes on the full catalog, measured by `python -m src.musicrec.benchmark`. Every figure from the run comes from [`benchmarks/results/2026-10-13-search-full-catalog.json`](../../benchmarks/results/2026-10-13-search-full-catalog.json), which also holds each query's timings and the environment the run recorded.

## What is measured

`SearchEngine.search_tracks(query)` end to end, on an engine built the way `web/app.py` builds it: `SearchEngine(recommender, enable_fuzzy=True, fuzzy_threshold=0.6)`, which leaves `min_query_length` 3, `max_results` 20, trigram fuzzy matching, `prefilter_top_n` 100 and a 128-entry similarity cache at their defaults. The catalog is loaded through `main.load_data()` and `MusicRecommender`, the path the app takes. The Dash callback and the dropdown rendering around the search are not part of the figures.

## How it was run

From the repository root:

```bash
PYTHONHASHSEED=0 MUSICREC_ENV=production python -m src.musicrec.benchmark --repeats 5
```

Each run writes a dated file under `benchmarks/results/` and prints the per-group table on stdout.

- `MUSICREC_ENV=production` is the value `render.yaml` sets. It skips the similarity graph at startup; the search engine never reads that graph.
- `PYTHONHASHSEED=0` fixes the hash seed. The fuzzy phase sorts its trigram candidates by overlap count only, so tied candidates keep set iteration order and the cut to the top 100 depends on the hash seed. A run under `PYTHONHASHSEED=1` with `--repeats 2` (not committed) returned a different result list for 17 of the 420 queries, all of them queries that reach the fuzzy phase; `result_digest` is the per-query field to compare across two results files.
- Query set: [`benchmarks/queries.json`](../../benchmarks/queries.json), drawn once from the catalog by `--write-queries` with seed 20261012. Track ids are walked in sorted order shuffled by that seed, so the draw does not depend on the hash seed. Names under three characters (the search minimum) and repeated names are skipped.
  - exact, 200 queries: catalog track names as the index stores them, lower case and trimmed, so the exact phase scores each 1.0
  - derived, 200 queries: one-edit typos of 200 other track names, with two adjacent letters swapped, one letter dropped, or one letter replaced by the next in the alphabet
  - hand, 20 queries: misspellings of artist and track names from the catalog, typed by hand
  - warm-up, 20 queries: run once before timing and not recorded
- Passes: the warm-up, then a cold pass that runs each of the 420 measured queries once in an order shuffled by the seed, then a repeated pass that runs each query 5 times back to back. The cold figure is a query's first run; the repeated figure is the median of the repeated pass's runs 2 to 5, so that pass's first run is dropped. The similarity cache is never cleared, as in the app.
- Timer: `time.perf_counter_ns()` around the `search_tracks` call. CPU time from `time.thread_time_ns()` is recorded beside it; wall time well above CPU time means the process waited for a core.
- Percentiles: nearest rank. The n values are sorted and the one at rank ceil(p / 100 × n) is reported, so a cold-pass percentile is one measured call. p50 and p95 are taken across queries. The fuzzy row is derived and hand together, 220 queries; the hand row alone is indicative only.

## Environment

| | |
|---|---|
| Run | 2026-10-13 01:49 EDT, commit `78906a8`, working tree clean |
| Host | Apple M2, 8 cores, macOS 27.0 (arm64) |
| Python | CPython 3.13.1 |
| Packages | pandas 2.2.3, numpy 2.1.1, plotly 5.24.1, dash 2.18.2, networkx 3.4.2, scikit-learn 1.5.2 |
| Catalog | 55,446 tracks in `genre_tree.tracks` |
| Data files, lines minus header | `spotify_songs.csv` 32,833; `autotagging_genre.tsv` 55,215; `autotagging_moodtheme.tsv` 18,486; `raw_meta_data.tsv` 56,639 |
| Index sizes | 107,757 exact-index keys; 26,208 trigrams |
| Load average, 1 / 5 / 15 min | 3.79 / 13.45 / 22.84 at the start; 3.26 / 12.25 / 22.02 at the end |

## Results

Milliseconds; nearest-rank percentiles across queries.

| Queries | n | Cold p50 | Cold p95 | Cold max | Repeated p50 | Repeated p95 | Reached fuzzy phase | Any fuzzy result |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| exact | 200 | 7.3 | 16.7 | 18.6 | 7.2 | 16.5 | 101 | 4 |
| derived | 200 | 10.8 | 16.2 | 22.0 | 9.9 | 17.2 | 143 | 105 |
| hand | 20 | 10.9 | 15.4 | 18.4 | 10.2 | 16.1 | 14 | 13 |
| fuzzy (derived + hand) | 220 | 10.8 | 16.2 | 22.0 | 9.9 | 17.2 | 157 | 118 |

Cold-pass CPU time was within 0.1 ms of wall time at p50 and p95 in every row, so waiting for a core did not move the cold percentiles; the largest gap on a single cold call was 2.0 ms. The repeated pass did wait: 13 queries had at least one run more than 5 ms above its CPU time, the slowest being `banhbang` at 231.1 ms of wall time on 17.8 ms of CPU, so the derived and fuzzy repeated p95 of 17.2 ms includes waiting; on CPU time it is 15.8 and 16.0 ms. `straigh beat` waited on all five runs (40 to 160 ms of wall time on 25 to 42 ms of CPU), which makes its median of runs 2 to 5, 95.2 ms, the repeated maximum in the results file.

## What the engine does with these queries

- Exact phase: each query scans all 107,757 exact-index keys and keeps any key that contains the query or is contained in it, scoring 1.0 for an equal key, 0.95 when the key starts with the query, 0.9 when it ends with the query, and 0.8 for any other match, which includes every key contained in a longer query. All 200 exact queries come back with a 1.0 match on top. 99 of them fill the 20 result slots in this phase and skip the fuzzy phase; 101 go on to it, and 4 of those get a fuzzy result.
- Misspelled queries: 219 of the 220 derived and hand queries have an exact-phase result on top, 218 of them a 0.8 match and one a 0.95 prefix match; one returns nothing. Counted over the exact index after loading the catalog (these counts are not in the results file), the index holds 122 keys shorter than three characters, such as "go", "in" and "i", and a key contained in the query counts as a match, so 219 of the 220 match at least one of them, and for 180 the top result comes from such a key. 157 of the 220 reach the fuzzy phase and 118 return at least one fuzzy result.
- Fuzzy phase: for each of the 258 measured queries that reach it, the engine counts trigram overlaps over every track that shares a trigram with the query, other than those the exact phase already returned, sorts all of those candidates by count, and scores the top 100 by track and artist name, 199 or 200 similarity lookups per query. On the cold pass, exact queries that reached it took a median 11.7 ms against 5.8 ms for those that did not; derived queries took 11.8 ms against 6.0 ms.
- Similarity cache (`lru_cache` with 128 entries, keyed on the query and the name it is compared with): 90,988 hits and 221,000 misses over the run, 564 and 1,836 of them in the warm-up. A query string is new to the cache on its cold run, so every cold-pass hit is a repeat inside one query, such as two candidates by the same artist: 11,530 of 51,598 lookups. On repeated runs 2 to 5, every similarity lookup of the 31 queries whose cold run missed the cache at most 128 times was a hit. The other 227 cycle through more pairs than the cache holds, so most entries are evicted before they come round again; the 2 to 19 that survive from one run to the next gave them about 8 more hits per run than their cold run. The exact phase and the trigram count run in full on every call either way.

| Queries | Cold hits | Cold misses | Repeated hits | Repeated misses |
|---|---:|---:|---:|---:|
| exact | 4,281 | 15,918 | 28,129 | 72,866 |
| derived | 6,153 | 22,446 | 41,613 | 101,382 |
| hand | 1,096 | 1,704 | 9,152 | 4,848 |
| fuzzy (derived + hand) | 7,249 | 24,150 | 50,765 | 106,230 |

## The 200 ms budget in CI

The 200 ms figure is a regression check, separate from these measurements: `tests/performance/test_search_performance.py` asserts it on a 1,000-track Mock fixture, through `ci.yml` on every push and pull request to main, and again in `performance.yml`. `performance.yml` then runs this benchmark with `--repeats 3` and uploads `benchmark-ci.json` for 90 days. That step has no latency threshold: it fails when the catalog check finds a count other than 55,446 or the run itself errors, for example on a missing `benchmarks/queries.json`, and never on a timing, because shared runner timings are not comparable with the table above.

## Not measured

- Startup time. The results file records how long this process spent loading the data and building the index (`load_and_build_seconds`), for the workflow's runtime; it is not the app's startup time.
- Memory. The results file keeps the benchmark process's peak resident set size for the record; the app's memory use was not measured.
- Concurrency. Queries run one at a time in one process.
- The deployed service, including the network round trip to Render.
- Browser compatibility.
