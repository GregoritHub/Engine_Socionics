"""The rules, applied to one packet.  TIM-specific facts are read from
the Position record (kernel) and the gas/brake law (energy).

  R1 gate         facets outside the position's law are residue
                  (derived: algebra.facets, conditional on Bukalov P1,P2)
  R2 retention    valued keep, unvalued don't            proposed_completion
  R3 automaticity vital processes; mental needs intent   proposed_completion
  R4 charge       input at p charges the block's producing position
                  (partner if p accepts, p itself if p produces), and
                  p itself if p has gas                  source_defined (blocks)
                                                         + external (gas)
  R5 generation   a fed block charges to the receiving   proposed_completion
                  position's law; strong generate, weak relay   switchable
  R7 boost        feeding the Leader also charges the demonstrative,
                  capped by its law (chord A1 -> A8, UMA s.19; kernel
                  note "receives an energy boost")    source_defined
  R6 firing       only gas positions fire: 1, 2, 8 emit; 5 emits requests;
                  brake-only and pessimum positions (3,4,6,7) hold charge
                  and never fire                          external (Gulenko)

V5 note: the V4 redirect rule (input on a producing aspect goes to the
block partner) is withdrawn.  It made the vulnerable function unreachable
-- there was no PoLR.  Every position now receives its own aspect."""
from __future__ import annotations
from dataclasses import replace
from algebra.perspective import block_partner
from .packet import Packet, extend
from .state import State
from .energy import gas

BLOCK = {1: "ego", 2: "ego", 3: "super_ego", 4: "super_ego",
         5: "super_id", 6: "super_id", 7: "id", 8: "id"}
FIRING = (1, 2, 8)           # gas positions that emit their aspect


def block_name(p: int) -> str:
    return BLOCK[p]


def is_automatic(p: int) -> bool:
    return p >= 5


def position_of_aspect(st: State, aspect: str) -> int:
    return next(q.index for q in st.positions if q.aspect == aspect)


def _charge(st: State, q: int, facets, carry, walks=frozenset()) -> State:
    pos = st.at(q)
    return st.put(replace(pos, charge=pos.charge | facets, carry=pos.carry | carry,
                          walks=pos.walks | walks))


def receive(st: State, pk: Packet, *, engaged_block=None, holon_id="self") -> State:
    p = position_of_aspect(st, pk.aspect)
    if not is_automatic(p) and engaged_block != BLOCK[p]:               # R3
        return replace(st, pending=st.pending + (pk,),
                       log=st.log + (("queued", pk.aspect, p),))
    pos = st.at(p)
    kept = pk.facets & pos.facets                                       # R1
    dropped = pk.facets - kept
    # Overload (a Shell-relevant hit) registers only for DIRECTED input:
    # conscious-ring output of another psyche, or the world.  Vital-ring
    # output (id, super_id, request) is automatic and does not press
    # (Kepinski K3 on the sender's side; A26).
    pressing = pk.tag in ("ego", "super_ego", "") or pk.source == "world"
    st = st.put(pos.fed(kept, dropped, pos.valued, pressing),           # R2
                ("processed", pk.aspect, p, tuple(sorted(kept)), tuple(sorted(dropped))))
    if not kept:
        return st
    gen = pos.facets if st.generative else kept                         # R5
    carry = {pk.aspect} | pk.carried
    walks = extend(pk.walk, (holon_id, p, pk.aspect))                   # the hop is the landing
    producer = p if not pos.accepting else block_partner(p)
    st = _charge(st, producer, gen, carry, walks)                       # R4
    if gas(p) and producer != p:
        st = _charge(st, p, gen, carry, walks)
    if p == 1:                                                          # chord A1 -> A8
        st = _charge(st, 8, gen & st.at(8).facets, carry, walks)
    return st


def produce(st: State, q: int, holon_id: str = "self"):
    """Fire q.  Returns (state, Packet | None).  Only gas positions fire."""
    if q not in FIRING:
        raise ValueError("position_does_not_fire: %d" % q)
    pos = st.at(q)
    out = pos.charge & pos.facets
    carried = pos.carry - {pos.aspect}
    walks = extend(pos.walks, (holon_id, q, pos.aspect))                # the hop is the firing
    st = st.put(replace(pos, charge=frozenset(), carry=frozenset(), walks=frozenset()))
    if not out:
        return st, None
    pk = Packet(pos.aspect, out, holon_id, BLOCK[q], carried, walks)
    return replace(st, log=st.log + (("produced", pk.aspect, q, tuple(sorted(out))),)), pk
