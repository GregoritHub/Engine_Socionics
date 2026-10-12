#!/usr/bin/env python3
"""Is the ~87% content-agreement floor under gated delivery a constant?
Gated ensembles over structurally different groups; report per-closure
perspective agreement (min over holons too) and tick spread."""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyref.core import TIMS, v11_beneficiary, v11_supervisee, dual_candidate
import horizon as Hz

def ring(f, start):
    r = [start]
    while f(r[-1]) not in r: r.append(f(r[-1]))
    return r
groups = {
  "benefit ring (ile)":     ring(v11_beneficiary, "ile"),
  "benefit ring (lii)":     ring(v11_beneficiary, "lii"),
  "supervision ring (ile)": ring(v11_supervisee, "ile"),
  "supervision ring (ese)": ring(v11_supervisee, "ese"),
  "quadra alpha":           ["ile", "sei", "ese", "lii"],
  "quadra beta":            ["sle", "iei", "eie", "lsi"],
  "club NT (researchers)":  ["ile", "lii", "ili", "lie"],
  "triad dual+activator":   ["ile", "sei", "ese"],
  "triad supervision chain":["ile", "lsi", "see"],
  "mixed 4 (conflict+sup)": ["ile", "esi", "lsi", "iee"],
}
print("%-26s %-5s %-5s %-5s   ticks k2      k3" % ("group", "k1", "k2", "k3"))
for name, g in groups.items():
    runs = Hz.ensemble(g, "gated", steps=90, n_seats=4, n_orders=2)
    rows = Hz.horizon(g, runs)
    # per-holon min agreement at k=2..3
    mins = []
    for k in (1, 2):
        for h in g:
            c = collections.Counter(r[h][k][1] for r in runs if len(r[h]) > k)
            if c: mins.append(c.most_common(1)[0][1] / sum(c.values()))
    fmt = lambda r: ("%3.0f%%" % (100 * r[1])) if r[1] is not None else "  --"
    print("%-26s %s  %s  %s   %s  %s   min-holon %3.0f%%" % (name, fmt(rows[0]), fmt(rows[1]), fmt(rows[2]),
          ("%2d..%2d" % (rows[1][2], rows[1][3])) if rows[1][1] is not None else "  --  ",
          ("%2d..%2d" % (rows[2][2], rows[2][3])) if rows[2][1] is not None else "  --  ",
          100 * min(mins) if mins else -1), flush=True)
