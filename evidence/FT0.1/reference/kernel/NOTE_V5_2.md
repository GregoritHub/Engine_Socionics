# NOTE_V5.2 — The Pure Finding, Provenance, and the Fourth Vocabulary That Wasn't

Build against: V5.1 unchanged. Kernel untouched, manifest re-verified.
New: `metabolism/spectrum.py`, `algebra/cognitive_style.py`,
`verify_v5_2.py` (36 checks), `bin/balance.py`, `bin/pure.py`,
`bin/yield_relay.py`, `bin/relay_gate.py`; ledger A37–A39 and the A23
refinement. Two package files gain instrument switches whose defaults
are V5 exactly: `tick.FIRING_POLICY = "every_tick"` and
`clock.RELAY_GATE = False`. All prior suites pass at defaults
(verify_v5 106/106, verify_canon, verify_v3, verify_v2). No float, no
weight, no rate: the one ratio the new instrument reports (the joint
fraction) is an exact `Fraction` of packet counts.

## Two corrections before the finding

**The V5.1 balance addendum misread its own tables by one seat.**
`bin/movement.py` forced a movement's polarity — and chose the world's
feed — from the seat the relay was LEAVING, while `tick()` advances the
relay first and works at the seat it arrives at. Fixed: polarity and
the world now read the post-advance seat, the same one `tick()` uses.
Consequence: the idle turn at altitude three was the CREATIVE's, not
the mobilizing's.

**And the diagnosis was wrong with it.** The chord as wired was not the
problem. The problem is that under `every_tick` all three gas positions
fire every tick wherever the relay is, so everything the lap
accumulates is produced and released on the mobilizing's turn (the
first expenditure turn after the accumulations), and the creative
arrives to an empty psyche. No wiring of the chord alone can make that
lap 2:2.

## The pure finding (A37)

The rule that produces it is the one the polarity layer was already
half-stating: **firing is expenditure, and expenditure happens on the
relay's expenditure turn.** `FIRING_POLICY = "relay"`:

    seat 2   the Ego fires (A1, A2) with the boosted demonstrative
             (A8; chord A1→A8 — the source says the demonstrative
             "receives an energy boost from the Leader"; that it also
             FIRES with the Leader is this build's reading, C4b)
    seat 6   the return chord conducts AND emits, at once — the
             mobilizing produces on its own turn, as the Leader's
             aspect, tagged ego, carrying the activating aspect
             ("return carrying it" happens on the return turn)
    seat 8   the demonstrative fires (unvalued lap)
    seat 4   nothing fires (pessimum)

Accepting seats hold charge. Under this policy the chord conducts only
at seat 6 (`chord.emit`), so charge at the activating function waits
for the mobilizing's turn instead of leaking into the Leader's. Two
consequences of the same reading: the relay decides intention (a mental
seat engages its block; the `launched` override belongs to the
`every_tick` mechanism and under `relay` it deadlocked the unvalued lap
against a standing A6 charge), and `A23` refines to: **the relay drops
to the Super-Ego under pressure only while the complement is not
retained** (`clock.RELAY_GATE`; Shell Geometry §18, "no longer only
external pressure").

Measured (`pure.*` checks; quadra + benefit ring + mixed, 200 steps,
8 seat vectors × orders, world on the accepting seat):

                      V5 default   every_tick+gate   relay + gate
    alt 3  balance        0.628          0.334           0.000
    alt 3  idle           0.112          0.249           0.005
    alt 2  balance        0.657          0.285           0.000
    valued lap share                          ≥ 97%, 25% per seat
    without any world     —                   0.015 (alt 3)

    (5.2.1: the column formerly labelled "V5 every_tick" was measured
    with the refined gate installed, as verify_v5_2 does; V5 defaults
    added. The alt-2 figure 0.330 did not reproduce through the suite's
    own path; 0.285 is the reproduced value. Decomposition in
    docs/A37_RESEARCH_NET.md §4: the 2+2 is C2 ∧ C3 with the gate.)

Each valued lap is exactly two accumulations (leading, suggestive) and
two expenditures (mobilizing via the chord, creative firing the Ego).
That is Kępiński's undisturbed anabolic/catabolic oscillation at
altitude, produced by the estafette and the two sourced chords — and
`verify_v5_2` checks textually that `tick()` contains no altitude
branch: development changes the balance only through what the tower
has retained.

**What relay firing does to the locked yield table** (`relay.*`; pair
regime, defaults elsewhere): every structural theorem survives —
type-invariance, the contrary symmetry, activation 3 > duality 2,
kindred ≡ duality, benefit sterile both ways, supervisee sterile with
the supervisor at altitude 3. (5.2.1: kindred ≡ duality and the
supervisor's closures rest, under relay, on the demonstrative firing on
the valued lap — reading C4b; docs/A37_RESEARCH_NET.md §2.) Four movements, recorded not adjudicated:
first closures land one tick later (accumulation must wait for an
expenditure turn); identity and semi-duality lose their lone lateral_A
closure (9 → 11 sterile rows); the super-ego pair loses its Serpent
closure and mirror gains one; and the supervisor closes the COMPLEMENT
first (tick 5), before lateral_E, with lateral_A arriving only through
the Serpent at 73. If the supervisor's early complementary closure is
the empirically right shape — the auditor gaining the crossed
perspective from the audited before anything lateral — that is a point
for relay firing; the V5.1 remark that the supervisor's win might be a
seat-1 artifact dissolves either way, since under relay the win no
longer passes through `return_route_not_traversed` at tick 4.

## Provenance walks (A38)

`carried` forgot order; now it doesn't have to carry that weight alone.
A `Packet` gains `walk`: a set of walks, each a tuple of
`(holon, position, aspect)` hops — the landing and the firing the
content passed through, across holons. Charge accumulates walks
(`Position.walks`), the chord moves them, firing extends them. Two
instrument integers bound the record (`WALK_CAP = 16` hops,
`WALKS_CAP = 64` walks); within the cap the order is exact, and
`carried` remains the uncapped set (checked: capped walk aspects ⊆
carried). World packets and requests start walks of their own.

The measurable your daydream named (`metabolism/spectrum.py`): a
packet's SHAPE is `(aspect, |facets|, carried, tag)`; `joint(pk)` is
true iff its provenance spans two or more holons — content produced
jointly and owned by neither; `relative_shape` re-keys aspects to the
emitter's own positions so spectra compare across types. Checked on
the dual pair: the developed pair's Ego output is 100% joint, the
joint fraction rises with altitude to exactly 1, the walk alternates
holon-runs (`ile·5 → ile·1 → sei·5 → sei·1 → …`, landing then firing,
each emission the other's complement wearing the sender's own aspect),
and the chord's crossing appears in the walk as the 5→1 run inside one
holon.

## Cognitive styles are not a fifth vocabulary (A39)

Gulenko's four styles (Forms of Thinking, 2002; carriers per the
wikisocion translation, external_secondary — the V5.1 canon audit's
aggregate-page caveat applies) enter the algebra as
`algebra/cognitive_style.py`, and they enter as COORDINATES, not
content. Derived and checked (`style.*`):

  1. The three defining dichotomies are two: in the character group,
     static/dynamic + process/result = positivist/negativist. Three
     dichotomies, four classes — that is WHY there are four styles.
  2. Each style is a coset of the annihilator of span{static, process}:
     an order-4 subgroup of the TIM space. Style is a point in a
     two-coordinate quotient of the F₂ algebra.
  3. **That subgroup is the supervision ring.** `v11_supervisee` fixes
     every style, and its orbit IS the style. Gulenko's own emphasis —
     supervision rings transmit forms of thinking through society — is,
     at kernel level, an identity rather than an observation.
  4. Duality, benefit, and contrary each map a style to its partner
     (CD↔DA, HP↔VS).

And the engine's verdict on their dynamics (`spectrum.*`): across all
sixteen types in dual pairs, the type-relative emission spectrum is ONE
spectrum per altitude, under either firing policy. Cognitive style has
no metabolic signature. This is not a new hole: contrary symmetry
already maps each style onto its partner, and the process/result
character — the styles' other coordinate — is the invisibility recorded
since V5.1 (rings indistinguishable, unresolved item 4). The style
question and the process/result question are now ONE question: any
observed difference between a causal-determinist and a holographer that
survives typing is evidence about where process/result enters the
dynamics, which the algebra says it currently does not. One less place
for the theory to hide.

## Status

A37 (relay firing) and the A23 refinement are proposed_completion:
readings of the estafette-as-relay and the polarity of the seat, with
UMA §10, §19 and Shell Geometry §18 as their sources, switchable, off
by default. A38 is instrument. A39's carrier lists are
external_secondary; everything derived from them is kernel-checked.
The decision the build leaves open, deliberately: whether relay firing
becomes the default. It should be made against a source or a
preregistered observation — not against the prettiness of the 0.000.
The discriminator first named here, the supervisor's first closure, is
qualified in 5.2.1: it is family-wide across seat-timed rules, reverses
at patience 2 / window 3, and requires the demonstrative on the valued
lap; the activation dyad detects every_tick, and the lock must carry
patience, window and delivery (docs/A37_RESEARCH_NET.md §3, §6).

## 5.2.1 addendum (4 September 2026)

A37 decomposed (`verify_a37.py`, 25 checks; `bin/a37_rules.py`,
`bin/a37_net.py`; report `docs/A37_RESEARCH_NET.md`): relay firing is
three readings — C2 expenditure-turn, C3 engaged-block, chord-as-turn —
plus two boost binaries at seats 2 and 6. Enumerating all 8^8
seat-dependent firing rules, C2 ∧ C3 ∧ C4a leave exactly four; the
engine's FIRES_AT is (boost@2 yes, boost@6 no). The 2+2 lap is C2 ∧ C3
with the gate and nothing else. The source net is closed negative
against the UMA Verified Revision (§10 caution, §17, §20, §24, §28).
Defaults unchanged.
