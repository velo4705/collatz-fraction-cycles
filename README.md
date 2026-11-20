# collatz-fraction-cycles

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24375499.svg)](https://doi.org/10.5281/zenodo.24375499)

Periodic cycles of the rational Collatz map `T(x)` on fractions `a/d` (reduced,
`d` odd, `1 ≤ a < d`, `3 ≤ d ≤ 1001`). `T(x) = x/2` if the reduced numerator is
even, `T(x) = 3x + 1` otherwise. All arithmetic is exact
(`fractions.Fraction`); cycle detection uses Floyd's tortoise-and-hare.

## Layout

| File | Role |
|---|---|
| `collatz_rational.py` | Enumerator: all reduced `a/d`, `d ≤ 1001`; writes `rational_cycles.csv` (denominator, is_prime, num_distinct_cycles, max_cycle_length, fraction_collapsing_to_1) |
| `rational_cycles.csv` | Per-denominator summary (500 odd denominators) |
| `analyze_global.py` | Builds the registry of all distinct cycles (writes `cycles_global.pkl`, git-ignored) |
| `scan_levels.py` | Persists per-cycle first-seen scan levels (`cycles_levels.pkl`, git-ignored) |
| `scan_field.py` | Level sweep: every reduced `a/D`, `D = 3^k * d'`, `k = 0..8` (k ≤ 6/4 for the minimal-gap-only homes); ~16.9M orbits |
| `aggregate.py` | Sweep-vs-registry comparison; emits `aggregate_out.txt` |
| `aggregate_out.txt` | Aggregated saturation table and registry-completeness check (PASS) |
| `collatz_theorem1.tex` | Theorem 1 proof structure: 3-adic exclusivity of `{1,2,4}` and descent on pure 3-power denominators |

Pickled registries (`*.pkl`) are intentionally not committed (see `.gitignore`).

## Reproduce

```bash
python3 collatz_rational.py 1001 rational_cycles.csv   # ~2 min
python3 analyze_global.py                              # builds cycles_global.pkl, ~2-4 min
python3 scan_levels.py                                 # builds cycles_levels.pkl, ~3 min
python3 scan_field.py                                  # k=0..8 sweep, 407 tasks, 14-core Pool, ~15-30 min
python3 aggregate.py                                   # prints saturation table
```

Requires only Python ≥ 3.10 (stdlib). LaTeX build of `collatz_theorem1.tex`
needs a TeX distribution (not exercised here).

## Key findings

- 203,380 reduced fractions (500 odd denominators) are all eventually periodic;
  1,095 distinct cycles, each homed at a single denominator `d' ≡ 1 or 2 mod 3`.
- **100% collapse to `{1,2,4}` occurs only for `d = 3^k` (k ≤ 6 in range);**
  every other denominator shows exactly 0.0 collapse. No partial collapse.
- Prime vs composite: similar cycle counts (≈2.9 vs ≈3.0); primes have longer
  maximal cycles (mean 142.7 vs 105.1).
- Every cycle satisfies `d' | 2^L − 3^M` with `2^L > 3^M` (L halvings, M odd
  steps), verified with zero violations. 148 of 1095 are minimal-gap
  (`d' = 2^L − 3^M`).
- Latent cycles (not reachable from `a/d'`, only from `3^k·d'`) exist; 23 in the
  ≤1001 scan, 12 of the minimal-gap cycles. The k ≤ 8 sweep found 35 additional
  cycles unreachable below level 1001; first appearances reach k = 8
  (`d' = 71`, one new cycle per level k = 5..8), so the early "k_min ≤ 3"
  observation was a scan-cap artifact and saturation is not universal.
- Every orbit from a `3^k·d'` level (3 ∤ d') lands homed at exactly `d'` —
  0 exceptions across ~16.9M orbits; the trivial cycle is reachable only from
  3-powers, consistent with the exclusivity theorem drafted in
  `collatz_theorem1.tex`.
