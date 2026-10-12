#!/usr/bin/env python3
"""Uniqueness-of-supplier check.  For each holon in a group, count how many
partners supply each of its missing perspectives (supplier map = the pair
yield table: partner u supplies to t the cost classes that close in pair(t,u)).
Prediction: a holon is content-exact under gating iff no gap has >1 supplier."""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyref.core import v11_beneficiary, v11_supervisee
from metabolism.exchange import relation_of
import horizon as Hz

YIELD = {  # relation -> cost classes supplied (verify_canon EXPECTED)
 "activation": ("lateral_A","complementary","lateral_E"), "supervision": ("lateral_A","lateral_E","complementary"),
 "duality": ("complementary","lateral_E"), "kindred": ("complementary","lateral_E"),
 "identity": ("lateral_A",), "semi_duality": ("lateral_A",), "super_ego": ("lateral_E",),
}
def suppliers(group):
    out = {}
    for t in group:
        c = collections.Counter()
        for u in group:
            if u == t: continue
            for cls in YIELD.get(relation_of(t, u), ()): c[cls] += 1
        out[t] = dict(c)
    return out

def ringf(f, st):
    r = [st]
    while f(r[-1]) not in r: r.append(f(r[-1]))
    return r
groups = {
  "benefit ring": ringf(v11_beneficiary, "ile"), "supervision ring": ringf(v11_supervisee, "ile"),
  "quadra alpha": ["ile","sei","ese","lii"], "triad dual+act": ["ile","sei","ese"],
  "triad sup chain": ["ile","lsi","see"], "mixed": ["ile","esi","lsi","iee"],
  "ring+duals": ringf(v11_beneficiary,"ile") + [__import__("pyref.core",fromlist=["dual_candidate"]).dual_candidate(t) for t in ringf(v11_beneficiary,"ile")],
}
def per_holon_agreement(group, runs):
    ag = {}
    for h in group:
        vals = []
        for k in (1, 2):
            c = collections.Counter(r[h][k][1] for r in runs if len(r[h]) > k)
            if c: vals.append(c.most_common(1)[0][1] / sum(c.values()))
        ag[h] = min(vals) if vals else None
    return ag

if __name__ == "__main__":
    hits = total = 0; rows = []
    for name, g in groups.items():
        sup = suppliers(g)
        runs = Hz.ensemble(g, "gated", steps=90, n_seats=4, n_orders=2)
        ag = per_holon_agreement(g, runs)
        for h in g:
            multi = max(sup[h].values(), default=0) > 1
            exact = ag[h] == 1.0 if ag[h] is not None else None
            if exact is None: continue
            ok = (multi != exact); hits += ok; total += 1
            rows.append((name, h, sup[h], ag[h], "ok" if ok else "MISS"))
    for r in rows: print("%-16s %-4s suppliers=%-52s agree=%3.0f%%  %s" % (r[0], r[1], r[2], 100*r[3], r[4]))
    print("prediction 'exact iff no gap has >1 supplier' holds for %d/%d holons" % (hits, total))
