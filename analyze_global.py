"""Global cycle analysis: re-scan d<=1001, register every distinct cycle,
and report order/divisibility regularities. Exact arithmetic throughout."""
import math, pickle
from fractions import Fraction
from collections import defaultdict
import collatz_rational
from collatz_rational import step, find_cycle

D_MAX = 1001

t0 = __import__("time").time()
cycles = {}   # canonical key: frozenset of Fractions -> dict info
for d in range(3, D_MAX + 1, 2):
    for a in range(1, d):
        if math.gcd(a, d) != 1:
            continue
        _, cyc = find_cycle(Fraction(a, d))
        key = frozenset(cyc)
        if key not in cycles:
            odd_steps = sum(1 for x in cyc if x.numerator % 2 == 1)
            L = len(cyc) - odd_steps
            M = odd_steps
            denoms = {x.denominator for x in cyc}
            cycles[key] = dict(length=len(cyc), M=M, L=L,
                               denominators=sorted(denoms),
                               cycle=sorted((float(x.numerator), x.denominator) for x in cyc))
print(f"total distinct cycles: {len(cycles)}  ({__import__('time').time()-t0:.0f}s)")

by_denom = defaultdict(list)
for k, v in cycles.items():
    by_denom[v["denominators"][0]].append(v)

print("\ncycle count per denominator (all scanned levels):")
multi = {d: v for d, v in by_denom.items() if len(v) >= 2}
for d in sorted(by_denom):
    n = len(by_denom[d])
    print(f"  d={d:<5} cycles={n}")
print(f"\ndenominators supporting >=2 cycles: {len(multi)}")

print("\nlength arithmetic (L halvings vs M odd steps):")
bad = 0
for v in cycles.values():
    if not (2**v["L"] > 3**v["M"]):
        bad += 1
print(f"  cycles with 2^L <= 3^M: {bad} (must be 0 for positive cycles)")

def factor(n):
    fs, m, p = [], n, 2
    while p * p <= m:
        while m % p == 0:
            fs.append(p); m //= p
        p += 1 if p == 2 else 2
    if m > 1:
        fs.append(m)
    return fs

def mult_order(a, n):
    # assumes gcd(a, n) == 1
    ph = n
    for p in set(factor(n)):
        ph = ph // p * (p - 1)
    o = ph
    for p in set(factor(ph)):
        while o % p == 0 and pow(a, o // p, n) == 1:
            o //= p
    return o

print("\norders vs cycle lengths (denominator d' of cycle):")
recs = []
for v in cycles.values():
    d0 = v["denominators"][0]
    if len(set(v["denominators"])) == 1 and d0 > 1:
        o2, o3 = mult_order(2, d0), mult_order(3, d0)
        recs.append((d0, v["length"], o2, o3, v["length"] % o2, v["length"] % o3))
recs.sort()
for d0, lam, o2, o3, m2, m3 in recs:
    if lam % o2 == 0 or lam % o3 == 0:
        mark = " <<<"
    else:
        mark = ""
    print(f"  d={d0:<6} len={lam:<4} ord2={o2:<5} ord3={o3:<5} len%ord2={m2} len%ord3={m3}{mark}")

with open("cycles_global.pkl", "wb") as f:
    pickle.dump({repr(sorted(k)): v for k, v in cycles.items()}, f)
print(f"\nwall={__import__('time').time()-t0:.0f}s")
