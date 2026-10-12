#!/usr/bin/env python3
"""Developmental experiments.  usage: python3 bin/socion.py [regime] [ticks]
regimes: pair | flood | flood_then_dual | dual_then_flood | club"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pyref.core import TIMS, element_at, dual_candidate
from crux.typemap import type_map
from algebra.perspective import PERSPECTIVES
from metabolism import develop as D, packet

def summary(ags):
    n = len(ags)
    return "mean altitude %.2f | at four-perspective closure %d/%d | last closure tick %s" % (
        sum(a.altitude for a in ags.values()) / n, sum(a.altitude == 3 for a in ags.values()), n,
        max((x["tick"] for a in ags.values() for x in a.history), default=None))

def club_tutor(ags):
    native = {t: type_map(t)["native_perspective"] for t in TIMS}
    def deliver(h, pk):
        return [o for o, a in ags.items() if o != h and native[h] in set(PERSPECTIVES) - a.org["retained"]]
    return deliver

regime = sys.argv[1] if len(sys.argv) > 1 else "flood_then_dual"
T = int(sys.argv[2]) if len(sys.argv) > 2 else 40
seed = {t: [packet(element_at(t, 1))] for t in TIMS}
dual = lambda h, pk: [dual_candidate(h)]
t0 = time.time()
if regime == "pair":
    ags = {"iee": D.agent("iee"), "sli": D.agent("sli")}
    ags, _ = D.run(ags, {"iee": [packet("ne")], "sli": [packet("si")]}, T)
else:
    ags = {t: D.agent(t) for t in TIMS}
    if regime == "flood":            ags, _ = D.run(ags, seed, T)
    elif regime == "flood_then_dual": ags, _ = D.run(ags, seed, T); ags, _ = D.run(ags, {}, T, deliver=dual)
    elif regime == "dual_then_flood": ags, _ = D.run(ags, seed, T, deliver=dual); ags, _ = D.run(ags, {}, T)
    elif regime == "club":           ags, _ = D.run(ags, seed, T, deliver=club_tutor(ags))
print("%s (%.1fs): %s" % (regime, time.time() - t0, summary(ags)))
for t, a in sorted(ags.items(), key=lambda kv: (-kv[1].altitude, kv[0])):
    print("  %-4s alt=%d %-22s closures %s" % (t, a.altitude, sorted(a.org["retained"]), [(x["tick"], x["closed"]) for x in a.history]))
