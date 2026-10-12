"""A37 decomposed.  The rule family that `relay` firing sits in, as a
monkeypatch of the tick (packages untouched; kernel untouched).

`relay` differs from V5 `every_tick` by three readings, not one:

  (i)   EXPENDITURE-TURN   production happens only at seats with a = 1
                           (the seat's directive bit, read onto production)
  (ii)  ENGAGED-BLOCK      what produces is the seat's block (extends the
                           reception rule `engaged_block` to production)
  (iii) CHORD-AS-TURN      A6->A1 conducts and emits on the mobilizing's
                           own turn (seat 6) instead of every tick, and the
                           `launched` intention override is withdrawn

plus one binary reading inside (ii): whether the A1->A8 boost fires when
A1 produces THROUGH the chord at seat 6 (relay says no: that emission is
the mobilizing's, wearing the Leader's aspect).

Each rule below is a (fire_at, emit_at, conduct_every_tick, launch_override,
relay_intention) tuple.  RULES["every_tick"] and RULES["relay"] must
reproduce the engine's own policies tick-for-tick; a37_net.py checks this
before using anything else.
"""
from __future__ import annotations
import sys
from dataclasses import replace
import metabolism.tick as _tick_attr          # NOTE: this is the FUNCTION re-exported by the package
T = sys.modules["metabolism.tick"]            # the module
from metabolism import develop as D, chord, energy, clock
from metabolism.handler import receive, produce, BLOCK, FIRING
from metabolism.packet import Packet

ALL_GAS = (1, 2, 8)
SEATS = tuple(range(1, 9))

def _block_fires(s):
    """Gas positions in the block of seat s (ego block also carries 8 via A1->A8)."""
    blk = [p for p in SEATS if BLOCK[p] == BLOCK[s]]
    out = [p for p in blk if p in ALL_GAS]
    if 1 in out:
        out.append(8)
    return tuple(out)

RULES = {
    # V5: every gas position fires every tick; chord conducts every tick; launch override on
    "every_tick":   dict(fire_at={s: ALL_GAS for s in SEATS}, emit_at=(), conduct_every_tick=True,
                         launch_override=True, relay_intention=False),
    # A37 as implemented (must equal T.FIRES_AT and the engine's relay branch)
    "relay":        dict(fire_at={2: (1, 2, 8), 6: (), 8: (8,), 4: ()}, emit_at=(6,), conduct_every_tick=False,
                         launch_override=False, relay_intention=True),
    # (i)+(ii)+(iii) with the boost also firing when A1 emits through the chord at seat 6
    "relay_boost6": dict(fire_at={2: (1, 2, 8), 6: (8,), 8: (8,), 4: ()}, emit_at=(6,), conduct_every_tick=False,
                         launch_override=False, relay_intention=True),
    # the two remaining C1-C4a survivors (UMA revision: the A1->A8 note is "receives an energy
    # boost from the Leader", a charging relation; "fires too" is the engine's reading, so the
    # boost binary exists at seat 2 as well as seat 6).  noboost2: the demonstrative fires only
    # on its own seat -- the engine analogue of the source's sequential schedule Te->Ne->Fe (s.24)
    "relay_noboost2":        dict(fire_at={2: (1, 2), 6: (), 8: (8,), 4: ()}, emit_at=(6,), conduct_every_tick=False,
                                  launch_override=False, relay_intention=True),
    "relay_noboost2_boost6": dict(fire_at={2: (1, 2), 6: (8,), 8: (8,), 4: ()}, emit_at=(6,), conduct_every_tick=False,
                                  launch_override=False, relay_intention=True),
    # (i) only: gas positions fire on any producing seat; V5 chord wiring and intention kept
    "turn_only":    dict(fire_at={2: ALL_GAS, 4: ALL_GAS, 6: ALL_GAS, 8: ALL_GAS}, emit_at=(), conduct_every_tick=True,
                         launch_override=True, relay_intention=False),
    # (ii) only: the seat's block produces every tick, accepting seats included; chord emits at 5 and 6
    "block_only":   dict(fire_at={s: _block_fires(s) for s in SEATS if BLOCK[s] != "super_id"}, emit_at=(5, 6),
                         conduct_every_tick=False, launch_override=False, relay_intention=True),
    # (i)+(ii) but chord conducts every tick and launch override kept (no (iii))
    "turn_block":   dict(fire_at={2: (1, 2, 8), 4: (), 6: (1,), 8: (8,)}, emit_at=(), conduct_every_tick=True,
                         launch_override=True, relay_intention=False),
}

_ACTIVE = {"rule": None}

def _intention(st, rule):
    if rule["relay_intention"]:
        sb = clock.engaged_block(st)
        if sb is not None:
            return sb
        return "super_ego" if clock.pressure(st) else "ego"
    if rule["launch_override"] and st.launched:
        return "ego"
    if clock.pressure(st):
        return "super_ego"
    sb = clock.engaged_block(st)
    return sb if sb is not None else "ego"

def tick_g(st, inbox, *, holon_id="self", patience=2, intention=None):
    """Mirror of metabolism.tick.tick with the firing rule parameterised."""
    rule = RULES[_ACTIVE["rule"]]
    st = clock.step(st)
    engaged = intention or _intention(st, rule)
    st = replace(T._age(st), tick_mark=len(st.log))
    queued, st = st.pending, replace(st, pending=())
    for pk in tuple(queued) + tuple(inbox):
        st = receive(st, pk, engaged_block=engaged, holon_id=holon_id)
    sig = energy.signals(st, patience)
    outbox = []
    if st.seat in rule["emit_at"]:
        st, pk = chord.emit(st, holon_id)
        if pk:
            outbox.append(pk)
    elif rule["conduct_every_tick"]:
        st = chord.conduct(st)
    for q in rule["fire_at"].get(st.seat, ()):
        if q == 1 and st.seat in rule["emit_at"]:
            continue                          # already produced by the chord emission
        if sig["brake"] and BLOCK[q] == "ego":
            st = replace(st, log=st.log + (("braked", q),))
            continue
        st, pk = produce(st, q, holon_id)
        if pk:
            outbox.append(pk)
    log = st.log + (("tick_end", st.fed_this_tick()),)
    if len(log) > T.LOG_CAP:
        log = log[-T.LOG_CAP:]
    st = replace(st, ticks=st.ticks + 1, launched=sig["launch"], log=log)
    hungry = sig["replenish"]
    if hungry:
        outbox.append(Packet(st.at(5).aspect, st.at(5).facets, holon_id, T.REQUEST,
                             walk=frozenset({((holon_id, 5, st.at(5).aspect),)})))
    return st, outbox, {"tick": st.ticks, "intention": engaged,
                        "fed": sorted(st.fed_this_tick()), "hungry": hungry,
                        "chord_open": chord.is_open(st), "signals": sig, "seat": st.seat,
                        "out": [(p.aspect, p.tag, tuple(sorted(p.carried))) for p in outbox]}

_ORIG_TICK = D._tick

def use(rule: str):
    """Install a rule (or None to restore the engine's own tick)."""
    if rule is None:
        _ACTIVE["rule"] = None
        D._tick = _ORIG_TICK
        return
    if rule not in RULES:
        raise KeyError(rule)
    _ACTIVE["rule"] = rule
    D._tick = tick_g

def native(policy: str):
    """Run the engine's OWN tick under its own switch (for harness validation)."""
    use(None)
    T.FIRING_POLICY = policy
