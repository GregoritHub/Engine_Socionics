#!/usr/bin/env python3
"""Demo: two holons exchanging information for N ticks.
usage: python3 bin/metabolize.py TIM_A TIM_B [steps] [--seed-aspect ne]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pyref.core import element_at
from metabolism import new_state, packet, run, relation_of, return_chord
from demand import schema as DS

a, b = sys.argv[1].lower(), sys.argv[2].lower()
steps = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 5
seed = sys.argv[sys.argv.index("--seed-aspect") + 1] if "--seed-aspect" in sys.argv else element_at(a, 1)
dev = "--developed" in sys.argv
sa = new_state(a)
if dev:
    from crux.typemap import type_map
    tm = type_map(a)
    sa = sa.with_organization(DS.organization(a, retained={tm["native_perspective"], tm["complementary_perspective"]}, dwelling=tm["native_perspective"]))
rc = return_chord(a)
print("%s -> %s : %s   (seed: world sends %s to %s)" % (a, b, relation_of(a, b), seed, a))
print("%s return chord A6->A1 = %s->%s realizes %s->%s (%s); %s\n" % (a, *rc["aspects"], *rc["route"], rc["name"], "OPEN (--developed)" if dev else "closed (ground state)"))
states, hist = run({a: sa, b: new_state(b)}, {a: [packet(seed)]}, steps, patience=1)
for h in hist:
    print("t%d %-4s intent=%-9s fed=%-8s hungry=%-5s out=%s" % (
        h["tick"], h["holon"], h["intention"], h["fed"], h["hungry"], h["out"]))
for name, st in states.items():
    print("\n%s log:" % name)
    for e in st.log:
        if e[0] != "tick_end":
            print("   ", e)
    print("   retained:", {p: sorted(f) for p, f in st.kept.items()})
    print("   content :", sorted(st.content().aspects), "->", sorted(st.content().domains()))
    print("   residue :", {p: sorted(r) for p, r in st.residue.items()})
