"""The generative loop.

tick: deliver pending then inbox (R3 decides what processes now); fire
every charged producing function; advance unfed counters; emit a
request on the suggestive aspect when it has starved for `patience`
ticks (proposed_completion of Super-Id semantics; patience is an
integer instrument value).  Intention: Ego by default, Super-Ego only
when something is pending there and Ego holds no charge.

commit: retained aspects enter the sealed Holon through the kernel's own
transition(), as DOMAIN keys via the unified Content projection.  OIG
therefore sees metabolism at domain depth, which is what its reach map
was built to read."""
from __future__ import annotations
from dataclasses import replace
from .packet import Packet
from .state import State
from .handler import receive, produce, BLOCK, FIRING
from . import chord, energy, clock

REQUEST = "request"
LOG_CAP = 512

# Firing policy (V5.2, A37).  "every_tick": every gas position fires every
# tick (V5).  "relay": firing is expenditure and happens on the relay's
# expenditure turn only -- seat 2 fires the Ego (1, 2) with the boosted
# demonstrative (8, chord A1->A8); seat 6 conducts the return chord and
# emits it at once (the mobilizing produces on its own turn); seat 8 fires
# the demonstrative; seat 4 fires nothing (pessimum).  On accepting seats
# charge is held.  Instrument switch; default keeps V5 behaviour.
FIRING_POLICY = "every_tick"
FIRES_AT = {2: (1, 2, 8), 6: (), 8: (8,), 4: ()}


def firing_set(st: State):
    if FIRING_POLICY == "every_tick":
        return FIRING
    return FIRES_AT.get(st.seat, ())


def intention_for(st: State) -> str:
    if FIRING_POLICY == "relay":
        # the relay IS the intention: a mental seat engages its block; on a
        # vital seat the pressure rule decides.  The launch effect (A6 ->
        # Ego) is realised by the chord emitting on the mobilizing's turn.
        seat_block = clock.engaged_block(st)
        if seat_block is not None:
            return seat_block
        return "super_ego" if clock.pressure(st) else "ego"
    if st.launched:                      # A6 initiates the Leader
        return "ego"
    if clock.pressure(st):               # Super-Ego under pressure, never by preference
        return "super_ego"
    seat_block = clock.engaged_block(st)  # otherwise the relay engages its block
    return seat_block if seat_block is not None else "ego"


def _age(st: State) -> State:
    """Advance counters at tick start: unfed grows; last tick's overload
    hit rolls into the streak; hit resets."""
    return replace(st, positions=tuple(
        replace(q, unfed=q.unfed + 1, over=(q.over + 1 if q.hit else 0), hit=False)
        for q in st.positions))


def tick(st: State, inbox, *, holon_id="self", patience=2, intention=None):
    st = clock.step(st)
    engaged = intention or intention_for(st)
    st = replace(_age(st), tick_mark=len(st.log))
    queued, st = st.pending, replace(st, pending=())
    for pk in tuple(queued) + tuple(inbox):
        st = receive(st, pk, engaged_block=engaged, holon_id=holon_id)
    sig = energy.signals(st, patience)
    outbox = []
    if FIRING_POLICY == "relay":
        if st.seat == 6:                            # the mobilizing's own turn
            st, pk = chord.emit(st, holon_id)
            if pk:
                outbox.append(pk)
    else:
        st = chord.conduct(st)
    for q in firing_set(st):
        if sig["brake"] and BLOCK[q] == "ego":        # A4 overload inhibits
            st = replace(st, log=st.log + (("braked", q),))
            continue
        st, pk = produce(st, q, holon_id)
        if pk:
            outbox.append(pk)
    log = st.log + (("tick_end", st.fed_this_tick()),)
    if len(log) > LOG_CAP:                      # diagnostic only; counters carry state
        log = log[-LOG_CAP:]
    st = replace(st, ticks=st.ticks + 1, launched=sig["launch"], log=log)
    hungry = sig["replenish"]
    if hungry:
        outbox.append(Packet(st.at(5).aspect, st.at(5).facets, holon_id, REQUEST,
                             walk=frozenset({((holon_id, 5, st.at(5).aspect),)})))
    return st, outbox, {"tick": st.ticks, "intention": engaged,
                        "fed": sorted(st.fed_this_tick()), "hungry": hungry,
                        "chord_open": chord.is_open(st), "signals": sig, "seat": st.seat,
                        "out": [(p.aspect, p.tag, tuple(sorted(p.carried))) for p in outbox]}


def run(states: dict, world_inbox: dict, steps: int, *, patience=2, deliver=None):
    """Multi-holon loop; outboxes broadcast next tick unless `deliver`
    (sender_id, packet) -> [receiver_ids] says otherwise."""
    inbox = {h: list(world_inbox.get(h, [])) for h in states}
    history = []
    for _ in range(steps):
        nxt = {h: [] for h in states}
        for h in states:
            states[h], out, rep = tick(states[h], inbox[h], holon_id=h, patience=patience)
            history.append(dict(rep, holon=h))
            for pk in out:
                for t in (deliver(h, pk) if deliver else [o for o in states if o != h]):
                    nxt[t].append(pk)
        inbox = nxt
    return states, history


def commit(holon, st: State):
    """Retained aspects -> domain keys -> kernel transition()."""
    from pyref import holon as H
    delta = st.content().kernel_delta()
    delta["replace_foreign"] = dict(holon.content.foreign)   # F untouched
    rule = {"archetype": holon.archetype, "intention": "metabolize",
            "event": "tick", "content_delta": delta,
            "state_delta": {"seat": st.seat}}
    return H.transition(holon, "metabolize", "tick", rules=[rule])
