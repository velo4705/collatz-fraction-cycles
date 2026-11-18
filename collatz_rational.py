"""Enumerate periodic cycles of the 2-adic rational Collatz map.

T(x) = x/2  if the reduced numerator of x is even
T(x) = 3x+1 if the reduced numerator of x is odd

Domain: reduced fractions a/d with odd d, 3 <= d <= D_MAX, 1 <= a < d, gcd(a,d)=1.
Arithmetic is exact (fractions.Fraction). Cycle detection is Floyd's
tortoise-and-hare, O(1) memory overhead per trajectory (the detected cycle
itself is stored once, at the end, for reporting).
"""

import csv
import math
import sys
import time
from fractions import Fraction

D_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 1001
OUT_CSV = sys.argv[2] if len(sys.argv) > 2 else "rational_cycles.csv"
MAX_STEPS = 5_000_000  # safety cap on total tortoise steps per trajectory


def step(x: Fraction) -> Fraction:
    n, d = x.numerator, x.denominator
    if n & 1 == 0:
        return Fraction(n >> 1, d)
    return Fraction(3 * n + d, d)


TRIVIAL = frozenset({Fraction(1), Fraction(2), Fraction(4)})  # 1 -> 4 -> 2 -> 1


def find_cycle(x0: Fraction):
    """Return (mu, cycle_tuple) for the trajectory starting at x0."""
    tortoise = x0
    hare = x0
    steps = 0
    while True:
        tortoise = step(tortoise)
        hare = step(step(hare))
        steps += 2
        if tortoise == hare:
            break
        if steps > MAX_STEPS:
            raise RuntimeError(f"trajectory from {x0} exceeded {MAX_STEPS} steps")
    # Find mu: index of first cycle element.
    tortoise = x0
    mu = 0
    while tortoise != hare:
        tortoise = step(tortoise)
        hare = step(hare)
        mu += 1
        if mu > MAX_STEPS:
            raise RuntimeError(f"mu search from {x0} exceeded cap")
    # Collect the cycle starting at tortoise (== hare).
    cycle = [tortoise]
    hare = step(tortoise)
    while hare != tortoise:
        cycle.append(hare)
        hare = step(hare)
        if len(cycle) > MAX_STEPS:
            raise RuntimeError(f"cycle extraction from {x0} exceeded cap")
    return mu, cycle


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        if n % p == 0:
            return n == p
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def main():
    t0 = time.time()
    rows = []
    total_traj = 0
    max_num_seen = 0
    for d in range(3, D_MAX + 1, 2):
        cycles = {}  # frozenset -> [length, count]
        phi = 0
        for a in range(1, d):
            if math.gcd(a, d) != 1:
                continue
            phi += 1
            x0 = Fraction(a, d)
            mu, cyc = find_cycle(x0)
            key = frozenset(cyc)
            entry = cycles.get(key)
            if entry is None:
                cycles[key] = [len(cyc), 1]
            else:
                entry[1] += 1
            if abs(cyc[0].numerator) > max_num_seen:
                max_num_seen = abs(cyc[0].numerator)
        total_traj += phi
        num_cycles = len(cycles)
        max_len = max(v[0] for v in cycles.values())
        collapse = sum(v[1] for k, v in cycles.items() if k == TRIVIAL)
        frac = collapse / phi
        rows.append((d, is_prime(d), num_cycles, max_len, frac))
        if d <= 21 or num_cycles > 1:
            reps = []
            for k, v in sorted(cycles.items(), key=lambda kv: -kv[1][1]):
                mn = min(k)
                reps.append(f"{v[1]}x len={v[0]} min={mn}")
            print(f"d={d} phi={phi} cycles={num_cycles} maxlen={max_len} "
                  f"collapse1={frac:.4f} | {'; '.join(reps)}", flush=True)

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["denominator", "is_prime", "num_distinct_cycles",
                    "max_cycle_length", "fraction_collapsing_to_1"])
        for d, p, nc, ml, frac in rows:
            w.writerow([d, "true" if p else "false", nc, ml, f"{frac:.6f}"])

    print(f"\nwrote {len(rows)} rows to {OUT_CSV}")
    print(f"trajectories={total_traj}  wall={time.time()-t0:.1f}s  "
          f"max|numerator| in a detected cycle start={max_num_seen}")


if __name__ == "__main__":
    main()
