#!/usr/bin/env python3
"""Horizon: decay of prediction from O with closures elapsed.
Ensemble = runs identical in O (types, relations, policy), differing only in H
(estafette phase per member; order members are stepped within a tick, which
decides who is hit first).  For each holon's k-th closure: agreement on WHICH
perspective (share of ensemble on the modal one) and the spread of WHEN."""
import os, sys, collections, itertools
from dataclasses import replace
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pyref.core import element_at, v11_beneficiary, dual_candidate
from crux.typemap import perspective_cost_class as pcc
from metabolism import develop as D, packet

def run(agents, order, steps, policy):
    inbox = {h: [packet(element_at(agents[h].st.tim, 1))] for h in agents}
    for t in range(1, steps + 1):
        nxt = {h: [] for h in agents}
        for h in order:
            a, out, rep = D.step(agents[h], inbox[h]); agents[h] = a
            for pk in out:
                for o in agents:
                    if o == h: continue
                    if policy == "gated" and any(q.hit for q in agents[o].st.positions): continue
                    nxt[o].append(pk)
        inbox = nxt
    return {h: [(x["tick"], pcc(a.st.tim, x["closed"])) for x in a.history] for h, a in agents.items()}

def ensemble(group, policy, steps=90, n_seats=6, n_orders=3):
    n = len(group); runs = []
    seats = [tuple(((i * 3 + j * 5 + 1) % 8) + 1 for j in range(n)) for i in range(n_seats)]
    perms = list(itertools.permutations(range(n))); orders = perms[::max(1, len(perms) // n_orders)]
    for s in seats:
        for od in orders:
            ags = {t: D.agent(t) for t in group}
            for t, x in zip(group, s): ags[t].st = replace(ags[t].st, seat=x)
            runs.append(run(ags, [group[i] for i in od], steps, policy))
    return runs

def horizon(group, runs, kmax=3):
    rows = []
    for k in range(kmax):
        agree, ticks = [], []
        for h in group:
            c = collections.Counter(r[h][k][1] for r in runs if len(r[h]) > k)
            if c: agree.append(c.most_common(1)[0][1] / sum(c.values()))
            ticks += [r[h][k][0] for r in runs if len(r[h]) > k]
        if not agree: rows.append((k + 1, None, None, None)); continue
        rows.append((k + 1, sum(agree) / len(agree), min(ticks), max(ticks)))
    return rows

if __name__ == "__main__":
    ring = ["ile"]
    while v11_beneficiary(ring[-1]) not in ring: ring.append(v11_beneficiary(ring[-1]))
    eight = ring + [dual_candidate(t) for t in ring]
    for name, grp in (("ring4", ring), ("ring4+duals", eight)):
        for policy in ("always", "gated"):
            runs = ensemble(grp, policy)
            print("%-12s %-7s n=%d" % (name, policy, len(runs)))
            for k, a, lo, hi in horizon(grp, runs):
                if a is None: print("   closure %d: not reached within 90 ticks" % k); continue
                print("   closure %d: perspective agreement %3.0f%%   tick %2d..%2d" % (k, 100 * a, lo, hi))
