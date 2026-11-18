"""k = 0..8 sweep of levels D = 3^k * d' for selected d'.

For each reduced fraction a/D (1 <= a < D, gcd(a, D) = 1) simulate the Collatz
orbit with integer-only state (num, den), den odd, gcd(num, den) = 1
(invariant: no cancellable factor other than one factor of 3 per odd step, and
even steps only halve an odd-denominator numerator). Floyd's tortoise-hare
detects the cycle; each cycle signature is a canonical repr of the sorted set
of (num, den) pairs. Per task we record how many orbits enter cycles homed at
d' and which signatures those are.

Outputs a JSON report: scan_field.json
"""
import math, json, sys, time, pickle
from multiprocessing import Pool
from collections import defaultdict

LATENT_HOMES = [1, 5, 13, 47, 59, 61, 79, 137, 233, 269, 283, 295]
EXTRA_PRIMES = [3, 7, 11, 17, 19, 23, 29, 31, 37, 41, 43, 53, 67, 71, 73, 83, 89, 97, 101, 103]
MG_ONLY_HOMES = [7, 23, 29, 37, 55, 101, 119, 125, 175, 229, 247, 253, 431, 485, 503, 509, 781, 943, 997]

def tasks():
    for d in LATENT_HOMES + EXTRA_PRIMES:
        for k in range(0, 9):
            yield (d, k)
    for d in MG_ONLY_HOMES:
        for k in range(0, 7 if d <= 333 else 5):
            yield (d, k)

def step(state):
    n, d = state
    if n & 1 == 0:
        return (n >> 1, d)
    n = 3 * n + d
    if d % 3 == 0:
        return (n // 3, d // 3)
    return (n, d)

def cycle_of(start):
    t = start; h = start
    steps = 0
    while True:
        t = step(t); h = step(step(h))
        if t == h:
            break
        steps += 2
        if steps > 20_000_000:
            raise RuntimeError(f"orbit too long from {start}")
    t = start
    while t != h:
        t = step(t); h = step(h)
    cyc = [t]; h = step(t)
    while h != t:
        cyc.append(h); h = step(h)
    return cyc

def signature(cyc):
    return repr(sorted((n, d) for (n, d) in set(cyc)))

def run_task(task):
    d_prime, k = task
    D = (3 ** k) * d_prime
    t0 = time.time()
    reps = {}  # signature -> (count, min_numerator, length, denominators tuple)
    total = 0
    mixed = []
    for a in range(1, D):
        if math.gcd(a, D) != 1:
            continue
        total += 1
        cyc = cycle_of((a, D))
        dens = {p[1] for p in cyc}
        if dens != {d_prime}:
            # only count cycles fully homed at d'
            if True:  # but still flag mixed/other-denominator cycles if d' in dens
                if d_prime in dens and len(dens) > 1:
                    mixed.append((a, sorted(dens)))
                continue
        sig = signature(cyc)
        ent = reps.get(sig)
        if ent is None:
            reps[sig] = [1, min(n for n, _ in cyc), len(cyc), len(dens)]
        else:
            ent[0] += 1
    return {
        "dprime": d_prime, "k": k, "D": D, "orbits": total,
        "homed_orbits": sum(v[0] for v in reps.values()),
        "signatures": {s: v for s, v in reps.items()},
        "mixed": mixed[:5], "wall": time.time() - t0,
    }

def main():
    ts = list(tasks())
    print(f"tasks={len(ts)}", flush=True)
    with Pool(14) as pool:
        results = []
        for i, res in enumerate(pool.imap_unordered(run_task, ts, chunksize=1)):
            results.append(res)
            print(f"[{i+1}/{len(ts)}] d'={res['dprime']} k={res['k']} D={res['D']} "
                  f"orbits={res['orbits']} homed={res['homed_orbits']} "
                  f"distinct={len(res['signatures'])} mixed={len(res['mixed'])} "
                  f"wall={res['wall']:.1f}s", flush=True)
    with open("scan_field.json", "w") as f:
        json.dump(results, f)
    print("wrote scan_field.json")

if __name__ == "__main__":
    main()
