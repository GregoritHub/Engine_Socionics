# NOTE_V5.1 — Relation Yield, and the Canon Audit

Build against: V5 unchanged. Kernel untouched, manifest re-verified.
New: `verify_canon.py` (29 checks), `bin/relation_yield_sweep.py`,
`docs/CANON_AUDIT_V5_1.md`, ledger A31–A33, unresolved item 10.
No package modified. No float, weight, or rate introduced.

## The experiment `bin/socion.py` did not run

Every ordered pair of TIMs, each holon alone with one partner, both
seeded with their own leading aspect, 80 ticks, default `window=2`,
`patience=1`. Closures recorded for the focal holon by cost class.

    activation          lateral_A@4  complementary@8   lateral_E@11   alt 3
    supervision (as supervisor)
                        lateral_A@4  lateral_E@7       complementary@9  alt 3
    duality             complementary@4  lateral_E@7                  alt 2
    kindred             complementary@4  lateral_E@6                  alt 2
    identity            lateral_A@3                                   alt 1
    semi_duality        lateral_A@3                                   alt 1
    super_ego           lateral_E@68  (Serpent; BORED_WINDOW = 64)    alt 1
    mirror, conflict, benefit, benefit_inverse, business, mirage,
    quasi_identity, contrary, supervision (as supervisee)            alt 0

Three facts about this table are theorems of the engine, all checked:

1. **Yield is a function of relation alone.** Zero variance across the
   sixteen types within any relation, closure ticks included.
2. **The contrary involution is a dynamical symmetry.** For all 256
   pairs, `yield(t,u) == yield(contrary(t), contrary(u))`. The V5
   perspective theorem reads only the n-bit; this confirms nothing
   downstream (estafette, energy formula, complex, tower) reintroduces
   extraversion. Extraversion is developmentally invisible.
3. **Rings pair under process/result.** Benefit rings and supervision
   rings each collapse to two under exactly one Reinin character, and it
   is process/result in both cases (kernel, `shared_characters`). The
   verbal polarity of that character remains unresolved (item 4); the
   partition is now derived.

## Canon audit (docs/CANON_AUDIT_V5_1.md)

Twelve authors on supervision and benefit (wikisocion aggregate pages),
Stratievskaya on mirror and activation, one external transcript on the
benefit/revision helices. Kernel-level claims in all sources check out
exactly: rings, directions, shared Reinin traits, channel permutations.
The disagreements are entirely dynamical:

    AGREES    supervisee suffers / supervisor gains; supervisee never
              closes at 300 ticks under persistent PoLR overload with
              complex activation (Bukalov, Slinko, Filatova: illness)
    AGREES    benefit sterile in isolation; beneficiary must distance
              (Vaisband, Slinko, Stankevichyute, Gulenko)
    AGREES    benefit ring of four is productive (Filatova): all four
              reach altitude 3, complement via Serpent at 72
    AGREES    mirror: creative overloaded by partner's leading, Super-Id
              unfed, no exit (Stratievskaya)
    ADDS      benefit-then-dual closes only at the boredom threshold
              (68/70 vs 4/7 fresh): benefit exposure leaves a scar
    ADDS      a closed supervision ring of four develops every member;
              supervisor/supervisee cancel
    DISAGREES Gulenko: isolated auditor completes an "educational
              mission" on the audited. Never reproduced.
    DISAGREES Filatova: ring + four duals "especially effective".
              Identical to the ring alone, tick for tick.
    DISAGREES Gulenko: process and result rings are different relations.
              Indistinguishable in every trace.
    DISAGREES Stratievskaya: activation cools two extraverts, heats two
              introverts. Contradicts theorem 2 above.

## Diagnosis

The three structural disagreements share one missing variable, and it
is the variable every author reaches for: **distance**. The delivery
model is total or absent per tick. Gulenko's "pulsating" benefit,
Filatova's dual-buffered ring, Vaisband's beneficiary who must leave to
act, the LSI/SEE family surviving on quarterly separation — none of
these can be stated in the engine. Consequences: a dual added to a
broadcast group is more broadcast, so every demand stays impure and
the group cannot outrun the ring; an audited holon never receives a
tick free of the auditor's leading on its PoLR, so the Shell never
clears. Process/result invisibility is a known hole, not a finding.

Recorded as unresolved item 10 and A33. The completion is narrow and
quantity-free: a delivery policy as an instrument parameter (partner
delivers every k-th tick, or only when the receiver is not `hit`).
Rerun the sterile eight under it. If intermittent supervision still
never closes the supervisee, the engine is making a real claim against
Gulenko; if it does, the machine was wrong in exactly one place.

The Stratievskaya E/I asymmetry is a separate matter: theorem 2 says
the engine cannot express it at all. Either it is a Shell-level
(S_C) effect below closure resolution, or extraversion enters the
dynamics somewhere the algebra does not — recorded, not adjudicated.

## Status of the findings

Every row of the yield table is downstream of A25 (signal→demand),
A27 (clearance at 3/4), the binary chord gate, `window=2` and
`patience=1`. The rows most exposed to A27 are the sterile ones whose
mechanism is PoLR overload: benefit both ways and the supervisee. The
supervisor's win passes through `return_route_not_traversed` resolving
at tick 4; whether that is an artifact of the seat starting at 1 has
not been checked. The `_OPEN` suffix on one canon check marks the
finding the distance completion is expected to overturn.

## Addendum — the exposure instrument was run (`bin/exposure.py`)

Two delivery policies, both instrument-level, no quantity:
`gated` (a partner's packet is delivered only when the receiver was
not `hit` on the previous tick — canon's "distance when it hurts") and
`every_k` (delivered only on ticks divisible by k — canon's
"pulsating"). Checks under `exposure.*`.

**Gated.** The sterile rows stay sterile: supervisee 0 at 400 ticks,
benefit 0 both ways. The supervisor still reaches altitude 3. Mirror
gains one closure, via the Serpent. The pair table stays
type-invariant. So the distance completion does **not** rescue the
audited holon: with the auditor's leading withheld whenever the PoLR is
hot, the supervisee still never clears. **This is now a claim the
engine makes against Gulenko's educational completion**, and for the
Bukalov/Slinko pathology reading, no longer a gap.

What gating does change is the group. The benefit ring of four reaches
altitude 3 at ticks 10–16 instead of 72 — the Serpent is no longer
needed — and the members close in different orders at different ticks.
Gating is the first thing in the engine that breaks type-invariance,
and it does so only in groups of three or more, where whose demand is
heard depends on who is hurting. Filatova's "ring is productive" is
now strongly supported. Her "ring + duals is especially effective" is
still not: the eight-group is no faster than the four (23 vs 16 for
the slowest member). Left `_OPEN`.

**Periodic.** Every-other-tick delivery kills every non-Serpent closure
for every relation, and raising `window` to 3 or 4 does not recover
it. Cause: A25's streak counter resets on any tick the position is not
hot, so a signal can never be "sustained" across a gap; retention
(`hold`) has the same consecutiveness. Under A25 as written, a
relationship experienced intermittently does nothing developmental
at all. That is either the engine's strongest empirical claim or a
defect in A25 (ticks counted rather than exposures). Recorded as A34;
the decision needs a source, not a tuning.

## Stage 1 — which distinctions are the completions' and which are the algebra's

`bin/completions.py` flips the three proposed_completion rules the
yield table passes through, by monkeypatch, packages untouched:
A25 (streak counts ticks → counts exposures, never resets), A27
(clearance at 3/4 required → not required), and the return-chord gate
(retained → always open). All eight cells rerun the 16×16 sweep and the
benefit-scar test. A28 (retention must be consecutive) was flipped
separately.

**Every distinction survives every cell.** Type-invariance, the
contrary symmetry, supervisee sterility, supervisor altitude 3,
activation 3 > duality 2, kindred ≡ duality, mirror and benefit
sterile, the benefit scar — none of them moves under any combination,
nor under A28. The only thing that changes is that super-ego's lone
Serpent closure disappears when A25 counts exposures (9 → 10 sterile).

So the yield table is not a property of the completions. What it is a
property of: the facet law (derived from P1–P3), the landing
permutation (kernel), and the estafette (kernel). That is the answer
to "which distinctions are real": at engine level, all of the
pair-regime ones. Any of them that is empirically wrong is wrong
because Model A's dimensionality-by-position or the relation group is
wrong, not because a rule of ours is.

**The periodic result is not A25.** It persists with A25, A27 and A28
all flipped. Partial diagnosis from the trace: production is
phase-locked to the estafette's 2-cycle — a holon emits its full
block output on alternate ticks and only requests on the others — so
k=2 delivery samples exactly the request phase. But k=3 also kills
closure, so aliasing is not the whole story. Reclassified: not a
completion artifact, not yet a claim; an open mechanism question at
the tick layer (A34 rewritten).

Practical consequence: stage 1 is finished and it did not shrink the
list. The next discriminator has to be empirical, and the only layer
where the engine and the observers both emit at the same resolution is
the signal layer (per-position deficit/overload per relation). That is
the study to design.

## Horizon — the decay of prediction, measured (`bin/horizon.py`)

Ensemble of runs identical in O (types, relations, policy) and differing
only in H (estafette phase per member; the order members are stepped
within a tick, which decides who is hit first). For each holon's k-th
closure: agreement across the ensemble on which perspective, and the
spread of when. Benefit ring of four, and ring plus duals; 90 ticks.

    ring4         always   k=1 100%  t 3..4    k=2 100%  t 5..6    k=3 100%  t 72..72
    ring4         gated    k=1 100%  t 3..4    k=2  89%  t 5..10   k=3  89%  t 8..18
    ring4+duals   always   k=1 100%  t 3..4    k=2 100%  t 5..6    k=3 100%  t 72..72
    ring4+duals   gated    k=1 100%  t 3..4    k=2  86%  t 5..9    k=3  86%  t 10..72

Three results, all locked (`horizon.*`):

1. **Regime I is exact at every closure.** Under always, the whole
   ensemble agrees on perspective and lands within one tick, out to the
   Serpent closure at 72.
2. **The horizon in Regime II is exactly one closure.** Under gated
   delivery, the first closure is still fully predictable from O — same
   perspective, one-tick spread. From the second closure on, prediction
   decays.
3. **Timing dies before content.** Agreement on *which* perspective
   settles near 87% and stays there; the spread of *when* goes from one
   tick to ten at k=2 and to sixty-two at k=3 in the eight-group (some
   runs close in the group's own window, others wait for the Serpent).
   What a holon will develop next remains fairly predictable; when it
   will is not.

For the theory (Prediction and Steering §4): the horizon is measured in
closures, not ticks, and equals one. Prediction of content outlasts
prediction of timing. A steerer who owns delivery fixes the class and
does not need the timing; a predictor who does not own delivery loses
the timing first and can keep, at best, a probable content.

## The content floor is structural (`bin/floor.py`)

Same ensemble method, gated, ten groups of different structure.
Perspective agreement at closures 2–3, and the worst single holon:

    benefit ring (either family)      94%   min-holon  75%   ticks k3  8..18
    supervision ring (either family) 100%   min-holon 100%   ticks k3  8..16
    supervision chain of three       100%   min-holon 100%   ticks k3  7..79
    quadra (alpha, beta)              91%   min-holon  62%   ticks k3  8..12
    triad dual + activator            83%   min-holon  62%   ticks k3  7..79
    mixed conflict + supervision      81%   min-holon  62%   ticks k3  8..13
    club NT                           no second closure at all

The ~87% was not a constant. It is a property of the group's structure,
and the pattern is sharp: **in asymmetric rings and chains, content is
exactly predictable and only timing is free; in groups with symmetric
relations, content itself becomes uncertain.** The supervision ring is
100% at every closure under gating — the gate can delay a closure but
cannot change which one comes next. The quadra, where a holon's gaps
can be addressed by more than one partner (dual, activator), drops to
62% for its worst member.

Conjecture [C], not yet checked mechanically: content predictability
in Regime II equals the uniqueness of supplier per missing perspective.
Where exactly one partner addresses a given gap, the gate can only
reorder timing; where two or more can, the gate decides which arrives
first and the perspective order becomes a function of H. Asymmetric
relations are content-deterministic under distance precisely because
they are one-directional.

Also re-confirmed: process/result rings and alpha/beta quadras are
identical run for run. A club cannot make a second closure under any
policy: all four share one native perspective and supply nothing
lateral to each other.

Consequence for Prediction and Steering: the two regimes were too
coarse. Within Regime II there is a further split — asymmetric
structures lose timing only; symmetric structures lose timing and
content. A steerer who wants a predictable *content* order under
distance should build the group out of chains, and the society that
is most predictable in what develops next is the one organised by
supervision and benefit. Which is, uncomfortably, the Hierarch's
argument, and it is correct as far as it goes.

## Uniqueness-of-supplier: refuted (`bin/suppliers.py`)

The conjecture was: under gating a holon is content-exact iff no
missing perspective has more than one supplier in the group (supplier
map = the pair yield table). Checked over 27 holons in seven groups.
**Holds for 8/27.** Withdrawn.

What the data show instead: every supervision-ring member has two
suppliers of lateral_E and is 100% exact; the benefit ring's SEE has a
single supplier and is 75%; the alpha quadra has four members with the
same supplier profile and only SEI loses content. Content loss is
holon-specific within a group and is not a function of the supplier
count. A second candidate — gate withholding rate per holon — is
suggestive in two groups (SEI most-withheld in the quadra, ILE in the
mixed group) and flat in two others. No predictor found.

Status: the structural split stands as [D] (asymmetric rings and chains
are content-exact; symmetric groups are not); the mechanism is open.
The uniqueness conjecture is recorded as withdrawn so it is not
re-proposed.
