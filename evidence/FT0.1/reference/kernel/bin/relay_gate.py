"""A23 gated on the complement (monkeypatch, package untouched):
the relay drops to the Super-Ego only when the complementary perspective
is NOT retained.  A developed holon keeps the valued lap under pressure."""
from dataclasses import replace
from pyref.core import ACCESS
from crux.typemap import type_map
from metabolism import clock
def step(st):
    s = st.seat
    comp_kept = type_map(st.tim)["complementary_perspective"] in st.retained
    if ACCESS[s]["valued"] and clock.pressure(st) and not comp_kept:
        s = 3
    elif st.serpent:
        s = clock.advance(s); st = replace(st, serpent=st.serpent - 1)
    elif not ACCESS[s]["valued"] and not st.pending:
        s = 1
    else:
        s = clock.advance(s)
    return replace(st, seat=s)
def install():
    clock.step = step
