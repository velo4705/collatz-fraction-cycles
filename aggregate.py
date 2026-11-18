"""Aggregate scan_field.json with the cycle registries.

Outputs (stdout):
  - per d': signatures found per k, first-appearance k, saturation k_max(d'),
    cumulative growth of the reachable set, NEW signatures (not in registry),
    and registry cycles missing at tested levels.
"""
import json, pickle, sys
from collections import defaultdict

sweep = json.load(open("scan_field.json"))
glob = pickle.load(open("cycles_global.pkl", "rb"))
lev = pickle.load(open("cycles_levels.pkl", "rb"))

def pkl_sig(v):
    # v["cycle"] is list of (float(numerator), denominator), sorted by numerator
    return repr([(int(fnum), den) for fnum, den in v["cycle"]])

registry = {}  # home -> set of signatures (same canonical form as sweep)
for k, v in glob.items():
    registry.setdefault(v["denominators"][0], set()).add(pkl_sig(v))

by_dp = defaultdict(dict)
for res in sweep:
    by_dp[res["dprime"]][res["k"]] = res

all_ok = True
for dp in sorted(by_dp):
    ks = sorted(by_dp[dp])
    print(f"\n=== d' = {dp}  (k = {ks[0]}..{ks[-1]}) ===")
    per_k = {}
    for k in ks:
        res = by_dp[dp][k]
        sigs = set(res["signatures"])
        per_k[k] = sigs
        print(f"  k={k} D={res['D']:<9} orbits={res['orbits']:<8} homed={res['homed_orbits']:<8} "
              f"distinct={len(sigs)} mixed={len(res['mixed'])} wall={res['wall']:.1f}s")
    cum = set()
    first = {}
    for k in ks:
        new = per_k[k] - cum
        for s in new:
            first.setdefault(s, k)
        cum |= per_k[k]
    reg = registry.get(dp, set())
    new_sigs = cum - reg
    missing = reg - cum
    print(f"  -> reachable-up-to-k distinct cycles: {len(cum)}  (registry homed at d': {len(reg)})")
    # saturation: smallest k after which no later level adds a new cycle
    sat_level = None
    acc = set()
    for k in ks:
        acc |= per_k[k]
        if all(per_k[j] <= acc for j in ks if j > k):
            sat_level = k
            break
    print(f"  k_max(d') = {sat_level}  (no new reachable d'-homed cycle after this k)")
    print(f"  first-appearance k counts: " + ", ".join(
        f"{k}:{sum(1 for v in first.values() if v == k)}" for k in ks))
    if new_sigs:
        print(f"  NEW cycles (beyond d<=1001 registry): {len(new_sigs)}")
        for s in list(new_sigs)[:10]:
            print(f"    example: {s[:120]}...")
    else:
        print("  no new cycles beyond the d<=1001 registry")
    if missing:
        print(f"  registry cycles NOT reachable at tested k: {len(missing)}")
        all_ok = False
    else:
        print("  all registry d'-homed cycles reached")
print(f"\nregistry-completeness check for all swept d': {'PASS' if all_ok else 'FAIL (see above)'}")
