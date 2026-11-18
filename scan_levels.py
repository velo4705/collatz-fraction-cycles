"""Persist, for every distinct cycle (d <= 1001 scan), the full set of scan
levels at which it was reached. Saves cycles_levels.pkl."""
import math, pickle, time
from fractions import Fraction
from collections import defaultdict
from collatz_rational import find_cycle

t0 = time.time()
seen = defaultdict(set)
home_of = {}
for d in range(3, 1002, 2):
    for a in range(1, d):
        if math.gcd(a, d) != 1:
            continue
        _, cyc = find_cycle(Fraction(a, d))
        key = frozenset(cyc)
        seen[key].add(d)
        home_of[key] = cyc[0].denominator

out = {}
for key, levels in seen.items():
    home = home_of[key]
    out[repr(sorted(key))] = {
        "home": home,
        "first_seen": min(levels),
        "levels": sorted(levels),
        "k_first": (min(levels) // home).bit_length() - 1 if False else None,
    }
# compute k = v_3(first_seen / home)
def v3(n):
    c = 0
    while n % 3 == 0:
        n //= 3; c += 1
    return c

for key, rec in out.items():
    home, first = rec["home"], rec["first_seen"]
    assert first % home == 0
    rec["k_first"] = v3(first // home)

with open("cycles_levels.pkl", "wb") as f:
    pickle.dump(out, f)
latent = {k: r for k, r in out.items() if r["first_seen"] != r["home"]}
print(f"total cycles={len(out)}  latent={len(latent)}  wall={time.time()-t0:.0f}s")
from collections import Counter
print(Counter(r["k_first"] for r in latent.values()))
