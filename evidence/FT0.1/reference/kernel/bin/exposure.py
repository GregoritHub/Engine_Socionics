#!/usr/bin/env python3
"""Unresolved item 10 / A33: delivery policy as an instrument integer.
Rerun of the sterile eight and the canon claims under intermittent contact.
  every_k      partner packets arrive only on ticks t % k == 0
  gated        partner packets arrive only when the receiver was not `hit` last tick
No package modified; the loop mirrors metabolism.develop.run with a tick index."""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pyref.core import TIMS, element_at, v11_beneficiary, v11_supervisee, dual_candidate
from crux.typemap import perspective_cost_class as pcc
from metabolism import develop as D, packet
from metabolism.exchange import relation_of

def run(agents, inbox0, steps, policy, k=2):
    inbox = {h: list(inbox0.get(h, [])) for h in agents}
    for t in range(1, steps + 1):
        nxt = {h: [] for h in agents}
        for h, a in agents.items():
            a, out, rep = D.step(a, inbox[h]); agents[h] = a
            for pk in out:
                for o in agents:
                    if o == h: continue
                    if policy == "every_k" and (t % k): continue
                    if policy == "gated" and any(q.hit for q in agents[o].st.positions): continue
                    nxt[o].append(pk)
        inbox = nxt
    return agents

def hist(a): return tuple((x["tick"], pcc(a.st.tim, x["closed"])) for x in a.history)
def seed(ags): return {h: [packet(element_at(a.st.tim, 1))] for h, a in ags.items()}

def sweep(policy, k, T=120):
    byrel = collections.defaultdict(set)
    for t in TIMS:
        for u in TIMS:
            ags = run({"A": D.agent(t), "B": D.agent(u)}, seed({"A": D.agent(t), "B": D.agent(u)}), T, policy, k)
            byrel[relation_of(t, u)].add(hist(ags["A"]))
    return byrel

if __name__ == "__main__":
    T = 120
    for policy, k in (("always", 1), ("every_k", 2), ("every_k", 3), ("every_k", 4), ("gated", 0)):
        print("=== policy=%s k=%s  T=%d" % (policy, k, T))
        byrel = sweep(policy, k, T)
        for r in sorted(byrel):
            v = sorted(byrel[r])
            tag = "" if len(v) == 1 else "  TYPE-VARIANT(%d)" % len(v)
            print("  %-20s %s%s" % (r, v[0] if len(v) == 1 else v, tag))
    print("=== Filatova: ring of four vs ring + duals, every_k=2, T=120")
    ring = ["ile"]
    while v11_beneficiary(ring[-1]) not in ring: ring.append(v11_beneficiary(ring[-1]))
    eight = ring + [dual_candidate(t) for t in ring]
    for grp, name in ((ring, "ring4"), (eight, "ring4+duals")):
        ags = {t: D.agent(t) for t in grp}; ags = run(ags, seed(ags), T, "every_k", 2)
        print("  %-12s %s" % (name, {t: hist(ags[t]) for t in grp}))
