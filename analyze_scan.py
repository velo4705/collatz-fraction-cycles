"""Per-cycle first-visibility analysis.

For each distinct cycle, record every scan denominator d at which it was
reached. A cycle homed at d' is 'latent' if it never appeared while scanning
a/d' itself with 1 <= a < d' — i.e. it is only reachable from larger multiples.
"""
import math, pickle, time
from fractions import Fraction
from collections import defaultdict
from collatz_rational import find_cycle

D_MAX = 1001
t0 = time.time()
scans_by_cycle = defaultdict(set)
home_of = {}
for d in range(3, D_MAX + 1, 2):
    for a in range(1, d):
        if math.gcd(a, d) != 1:
            continue
        _, cyc = find_cycle(Fraction(a, d))
        key = frozenset(cyc)
        scans_by_cycle[key].add(d)
        home_of[key] = cyc[0].denominator

latent = []
own = defaultdict(int)
for key, scans in scans_by_cycle.items():
    home = home_of[key]
    if home in scans:
        own[home] += 1
    else:
        latent.append((home, min(scans), sorted(scans)))
print(f"total distinct cycles: {len(scans_by_cycle)}")
print(f"cycles reachable at their own home level: {len(scans_by_cycle) - len(latent)}")
print(f"latent cycles (only visible from multiples): {len(latent)}")
for home, first, scans in sorted(latent, key=lambda x: (x[0], x[1])):
    print(f"  home d'={home}  first-seen at d={first}  scan-levels={scans[:6]}")
print(f"wall={time.time()-t0:.0f}s")
