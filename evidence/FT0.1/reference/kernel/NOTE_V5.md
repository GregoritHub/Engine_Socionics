# NOTE_V5 — One Algebra, One State

Build against: V4 unchanged. Kernel: untouched, manifest re-verified.

## Why

V4's own note said the engine was "two theories sharing a verifier":
IE aspects, OIG domains, Crux perspectives and metabolic facets were
four vocabularies for content, meeting at seams. Two of the maps
between them — `oig.CLASS_PAIR` and `typemap.CLUB_PERSPECTIVE` — were
the same table typed twice by hand. V5 derives that table and
collapses the metabolism layer onto one record type.

## The theorem

Let n(e) be the *internal* coordinate of aspect e in UMA §3
(`IE_COORD[e][2]`). For an irrational aspect r and a rational aspect j,

    collective(r, j) = n(r) ⊕ n(j)
    interior(r, j)   = 1 ⊕ n(j)

reproduces `crux.perspectives.CODE` exactly. Checked by exhaustion over
all 32 mixed pairs. Consequently, all derived and checked:

* `oig.CLASS_PAIR` and the Atlas club table both regenerate from
  `IE_COORD` alone (`algebra.class_pair_table`, `algebra.club_table`);
* an aspect fixes one coordinate and covers a **line** of two
  perspectives; a rational+irrational pair fixes a **point**;
* every Model A block is such a pair, so every block addresses a
  perspective: Ego and Id the native one, Super-Ego and Super-Id its
  surface partner, the two laterals the remaining two — typemap's four
  cost classes, now a consequence rather than a table;
* `oig.reach(tim, d)` equals "positions whose aspect's line contains d"
  for all 64 (TIM, domain) cases.

The Crux square is a change of basis on the kernel's internal/external
dichotomy. It is not a fourth primitive, and `crux/typemap.py` now
imports its club table from `algebra` instead of stating it.

## What shipped

    algebra/
      perspective.py   the theorem and its consequences
      content.py       Content(aspects, foreign) with projections:
                       perspectives(), domains(), kernel_delta()
      facets.py        the facet law (below)
    metabolism/        rewritten (v2), 336 -> 336 lines but one shape:
      state.py         State = eight Position records + pending + log
      handler.py       the five rules in 69 lines
      exchange.py      channel + names, anchors as a table of predicates
      tick.py          loop, hunger by counter, commit via Content
    verify_v5.py       106 checks (supersedes verify_v4)

Modified: `crux/typemap.py` (one table replaced by a derivation).
Removed: `verify_v4.py`, `NOTE_V4` retained for the record.

## What changed in kind

* **Metabolism commits as domain content.** V4 wrote foreign keys
  because there was no principled map from aspects to domains. There
  is now: `State.content().domains()` is the union of the retained
  aspects' lines. OIG therefore sees metabolism at domain depth, and a
  check confirms every retaining position lies in the reach of every
  domain it wrote. The kernel, the Crux and the metabolism now read one
  object at three resolutions.
* **Position is the only mutable record.** Retained, residue, processed,
  charge, unfed are fields of one frozen `Position`; the V4 dict-per-
  concern state and its copy dance are gone. Hunger is a counter aged
  once per tick, not a backward scan of the log.
* **Relation names are a table of predicates.** Eight kernel-anchored
  tests in a list, seven audited permutations in a dict, one lookup.

## Suites

    verify_v5   106/106     verify_v3   80/80 (see below)
    verify_v2    54/54      le verify   116/117 (same legacy gap)

`verify_v3` grew from 77 to 80: `verify_finite_object` (three checks
against *A Finite Object* — distinct layings share exactly 7 of 15
cuts; exactly 7 Reinin forms stay affine in the frame atlas; membership
is the N = T coefficient condition) had been written but never called,
and referenced an attribute the kernel does not have (`Affine.v`; the
translation is `Affine.b`). Wired in and corrected; all three pass.

## The facet law (R1 closed)

Three premises: **P1** dimensionality is the *number* of parameters a
function processes, and **P2** the parameters nest (both Bukalov,
source_defined); **P3** dim = 1 + 2·strong + bold (UMA §2, derived).
`verify_v5` enumerates all 16⁴ assignments of the four facets to
boolean functions of (strong, bold). 96 satisfy P1+P3. Exactly one also
satisfies P2:

    experience  always
    norms       strong ∨ bold        absent only on the 1D pair {4, 5}
    situation   strong               the strong/weak dichotomy itself
    time        strong ∧ bold        the 4D pair {1, 8}

The ladder is therefore not a primitive. `algebra/facets.py` states the
law; `Position.facets` is built from it; R1, R4's cap and R5 read
`pos.facets` and nothing else. R1's status moves from
proposed_completion to **derived, conditional on P1 and P2**. The
"product" reading ({norms}↔bold, {situation}↔strong) is refuted: it
gives 3D positions two facets, violating P1.

What this buys: the metabolism's capacity gate is now a statement about
the kernel's position characters, so any experiment that distinguishes
strong from weak processing is already an experiment on R1.

## Kępiński in kernel coordinates

His three categorical distinctions are the three position coordinates:
anabolic/catabolic is `a` (typemap's polarity is already `a == 0`),
affective-first/cognitive-second is `r`, toward/away is read as `v`
(proposed_completion — the one identification no source states). His
two orderings orient `a` (0→1) and `r` (1→0); R4 and R3 were already so
oriented. `v` receives no ordering and is the open coordinate. The
sourced Model G chord A6→A1→A8 violates the orientation on one axis per
step: it is a return edge, so any flow law on the chords is a cycle,
not a gradient. `algebra/kepinski.py`; seven checks. **No quantity is
introduced.** There is still no energy; there is now a statement, in
kernel coordinates, of exactly what a source would have to supply.

## The return chord: development touches metabolism

Model G's sourced chord A6→A1 (UMA §19, `G_CHORDS_A`) is the
complement→native return route at position resolution. Three
independent readings agree and are checked for all sixteen TIMs:
position 6 addresses the complementary perspective and 1 the native
(`typemap.return_route`); 6 is expenditure and 1 accumulation, so the
edge is catabolic feeding anabolic; and the IE pair it carries is the
dual's creative → own leading. Its name is per TIM: Embody for the four
I-native types, Express / Educate / Institutionalize for the rest — the
same restriction NOTE_V3 made to the Atlas.

`metabolism/chord.py` gates it on the tower's retained set
(`demand.schema.organization`): closed at ground state, open once the
complementary perspective is retained (proposed_completion; the source
says "increasingly available" and the kernel has no continuum, so the
gate is binary). When open, charge at the activating function flows
into Ego production without facet enrichment, and packets now record
what they **carry**. The observable: at ground state IEE's Ego emits Fi
carrying {Ne}; developed, after the dual answers, it emits Fi carrying
{Ne, Si, Te}. Shell Geometry §18 — "cross into the complement and return
carrying it" — is executable. A6→A8 is reported, not wired.

`State.retained` (perspectives) replaces the old `retained` view, now
`kept` (facets per position), to keep the two senses apart.

## Energy signals in both directions (correction)

A review caught an asymmetry: the suggestive alone could starve, and
no position could be hurt. Two causes. The kernel's four Gulenko notes
(A6 initiates the Leader, A5 replenishes reserves, A4 inhibition and
energy loss, A8 receives a boost) were implemented at one position.
And the V4 redirect rule routed input on a producing aspect to the
block partner, so the vulnerable function could never receive —
**there was no PoLR**. The redirect is withdrawn: every position
receives its own aspect at its own capacity.

Gulenko's four energy levels (his own article on socioniks.net, marked
`external_source` — outside the governing documents and to be admitted
or struck) map through the kernel's G↔A permutation onto Model A and
turn out to be a formula over the position coordinates:

    gas   = 1 ⊕ v ⊕ ar        brake = v ⊕ r ⊕ ar

On the mental ring valued ⇔ gas, unvalued ⇔ brake. On the vital ring gas
and brake coincide and equal the kernel's contact bit. Firing is now by
gas: 1, 2, 8 emit their aspect; 5 emits requests; 3, 4, 6, 7 hold charge
and never fire (R6). Consequence: **the leading function fires** — it
was silent under the old a-bit rule, which is why the dual loop had to
be relayed through the activating function.

`metabolism/energy.py`: deficit (accepting, unfed) and overload (input
above the facet law) are computed for every position, both Kępiński
directions. Effects, one per kernel note, proposed as to mechanism:
replenish (deficit at A5 → request), brake (overload at A4 inhibits Ego
firing that tick), launch (charge at A6 forces Ego next tick — the
trigger role; content return stays gated by retention), boost (A8 is a
gas position and fires when fed). Dual loop now: SLI's leading Si feeds
IEE's suggestive directly, Te lands on the activating function, and
with the chord open IEE's Ne returns carrying {Si, Te}.

## S_C: the Shell has content

Shell Geometry §6.2 projects the Shell object three ways: S_C
(functional/diagnostic appearance), (K,R) (trajectory), ι. V3 built the
trajectory leg and carried S_C as five sign names. *Archetypal Shadow
Complex* is admitted as a governing source because it is S_C: its
sixteen tables, parsed by `bin/audit_archetypes.py`, put each of the
eight archetypes on one Model A position for every type (Saint 1 …
Prophet 8), its Ego/Other directive is the `a` bit, its
syntonic/dystonic is the `v` bit, each complex pairs a position with
its (0,1,1) flip — the OPP element one ring over — and its three
functional relations are counterphase, OPP, SIB. Each element carries
one disorder across all tables. `algebra/archetype.py` states it;
`crux/shell.py` gains `diagnostic_appearance` and `realization_at`;
`metabolism/complex.py` activates a complex when overload at a position
persists (window is an instrument integer; the rule is
proposed_completion). Persistent PoLR overload in IEE activates the
Child complex as the Serpent (Ti, avoidant), projected onto the
Innocent (Te) in the Other. Two prose errors in the paper are recorded
in `docs/SOURCE_AUDIT_V5.md`; the tables are right. Sign → (K,R) stays
open. Consequence for unresolved item 6: the paper puts toward/away on
`v` independently of Kępiński, which is the second source for A17.

## Motion: the clock, the axis, the observation

* **The estafette is the clock.** UMA §10's R has two orbits on
  positions, 1→5→6→2 and 3→7→8→4 — the valued and unvalued rings, each
  step crossing one axis, a and r once each way per lap, v never.
  Read as its name says, a relay, it is the sourced oscillation the
  Kępiński analysis said any flow law must be. `seat` (inert since V1)
  is where the relay is; it advances each tick, engages its block when
  mental, and is written back into the kernel Holon through commit().
  Orbit switching under pressure is the one proposed rule (A23).
* **v is the axis of development, not oscillation.** Oriented
  dystonic→syntonic by the archetype paper's integration direction
  (A24). With a and r from Kępiński all three axes are oriented; the
  chords remain return edges; the cycle is the estafette's.
* **OIG reads the metabolism.** `observe.projection` runs pyref.oig over
  the trajectory of Content domains — one process, two projections, as
  §5 requires — and states the two Shell signatures the source states:
  maintenance and foreclosure. The four activation signs are not given
  signatures (unresolved 9).

## The development generator, and what a socion does

`metabolism/develop.py` wires §11: sustained metabolic signals become
demands (A25), the conductivity test runs, a boundary yields the
tower's minimal extension as a provisional H', and the tower's own
closure law is met from metabolic observables — retention as kept
content at the perspective's valued positions (A28), the return route
traversed by the estafette, the Shell cleared at Role/Vulnerable (A27).
`altitude.close()` seals it. Altitude is counted; nothing can assign it.
A developed holon stops requesting (A29). `bin/socion.py` runs regimes.

Findings (all reproducible; two are checks):

* **A dual pair** closes the complement at tick 4, one lateral at 7,
  and plateaus at altitude 2. Two egos address two perspectives.
* **The whole socion under broadcast** reaches altitude 2 by tick 6,
  every type, and none makes the fourth closure. In a flood no demand
  is pure: every sustained signal pairs with something already fed, so
  every demand set contains a retained perspective and C(H,D) is never
  empty. The socion as environment makes every demand satisfiable.
* **Flood then dual only**: 16/16 reach four-perspective closure, last
  at tick 42. After the flood what is missing is the complement, and
  the dual supplies it purely.
* **Dual first, then anything** (flood, mirror, activity, super-ego,
  conflict, or even the club that addresses the gap): stuck at 2.
  What is missing is a lateral, and the demand that would force it is
  generated by overload at the Role — the same overload that keeps the
  Shell from clearing. Under continuous directed pressure on a fixed-
  dimension function, "same demand, less distortion" (§16.2) cannot be
  met. This is a theory-level tension, recorded, not patched.
* **A club tutor** — every holon receives only from the club whose ego
  addresses a perspective it lacks — takes all 16 to the top by tick 8.

So: everyone can reach the highest altitude; the order of environments
decides whether they do; and the two regimes that work are the ones
where demand arrives *pure*. Which is §12 stated as an experiment.

* Gulenko art. 113 **admitted** as `external_secondary` in
  `manifests/source_manifest.json`, with its dependents listed so it
  can be struck in one deletion. Shell Geometry v1.1 added to the
  primary hashes.
* Chord A1→A8 wired (R7): feeding the Leader charges the demonstrative.
  Both sourced chords now execute.
* Assumption ledger A13–A21 records every V4/V5 completion with status.
* Unresolved items 6–8 record what the sources don't decide: `v` as
  toward/away, the `v` ordering, and the missing Erlang mirror.
* `seat`: decided inert, recorded (A20). Staged generation: decided
  all-at-once, recorded (A21); a rate would be a quantity.

## Still open

Two-valued intention (Ego / Super-Ego) — adequate while Id and Super-Id
are automatic; revisit if a source gives the vital ring an intention.
Unresolved 8 (Erlang mirror) and 9 (four activation signs) remain. No energy quantity, by design.

## What V5 did not do

It did not refactor V2/V3 packages beyond the one table. `tower_v1`
still ships beside `tower_v2`; the `sys.path.insert` lines remain in
`intention/` and `demand/`. Those pass their suites and touching them
buys tidiness, not truth. The new packages have neither.
