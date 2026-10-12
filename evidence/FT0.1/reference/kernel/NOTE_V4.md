# NOTE_V4 — Holonic Living Engine V4: Information Metabolism Executes

Build against: the V3 bundle unchanged. Kernel: untouched, SHA-256
manifest re-verified by `verify_v4` on every run.

## Why this build exists

V3 verified the geometry of Model A and never moved an aspect through
it. `transition()` was TIM-blind; `seat` was stored and never read;
dimensionality was a regression column; the relation group was a lookup
with no channel; `other_holons` carried envelope summaries only. The
"Living" in Living Engine was a promissory note held by the unfitted
models. V4 cashes the structural part of that note without touching the
statistical part: no probabilities, no reserves, no energy numbers.

## What shipped

    metabolism/
      packet.py     IE-typed packets with dimensional facets
      handler.py    per-TIM reception, gate, retention, automaticity,
                    block production, generation
      exchange.py   inter-psyche transfer; relation group as channel;
                    all sixteen relations named from kernel + audit
      tick.py       the generative loop; suggestive hunger; kernel commit
    bin/metabolize.py   two-holon demo
    verify_v4.py        48 checks

Touched nothing else. `verify_v2` 54/54, `verify_v3` 77/77,
`bin/le.py verify all` 116/117 (same legacy gap).

## The five rules, with status

| Rule | What it does | Read from kernel | Status |
| --- | --- | --- | --- |
| R1 gate | facets of level > dim(p) dropped as residue | `ACCESS[p].dimensionality` | source_defined (Bukalov ladder 1D..4D as carried by Model A) |
| R2 retention | valued positions retain, unvalued process only | `ACCESS[p].valued` | proposed_completion |
| R3 automaticity | vital positions process without intention; mental queue unless engaged | `ACCESS[p].frame` | proposed_completion (OIG C.3 conscious/automatic) |
| R4 production | accepting input charges block partner; output aspect = element at producing position, capped by its dim | `POS_COORD` a-flip, `element_at` | source_defined (Model A blocks) |
| R5 generation | a fed block charges to its accepting function's full dim; strong functions generate, weak relay | `ACCESS[p].dimensionality` | proposed_completion, switchable (`generative=False` = pass-through) |

Block partner is **derived**: it is the flip of the `a` coordinate in
UMA §2, and `verify_v4` asserts it yields exactly (1,2)(3,4)(5,6)(7,8)
with alternating accepting/producing. No block table is typed in.

A packet landing on a producing function is redirected to its block's
accepting partner and processed at that partner's dimension. Producing
functions answer; they do not ask. This is a modeling decision, logged
on every occurrence as `('redirect', aspect, from, to)`.

## The relation group is now a channel

`landing_position(A, i, B)` computes where A's position-i aspect lands
in B **from `rel_map(A,B)⁻¹`**, not from the stacks, and `verify_v4`
checks it agrees with `position_of` for all 16×16×8 cases. The seven
relation names the kernel lacked are matched by landing permutation
against the tuples already audited in `UNRESOLVED_SOURCE_ITEMS.md` §3;
super-ego is read off the centre of the dynamical group. All sixteen
ordered relations now name, and the name is constant across TIMs for
each group element (checked).

## Generative loop

Default intention is Ego. Super-Ego is engaged only when a packet is
pending there and the Ego has no charge — Super-Ego work under pressure,
never by preference. Hunger: when the suggestive (1D, valued, accepting)
has been unfed for `patience` ticks, the holon emits a request packet on
its suggestive aspect. Structurally, that aspect is the dual's leading;
the dual's creative then lands on the requester's activating. Both
facts are checked for all sixteen TIMs.

Retained facets enter the sealed Holon through `commit()`, which builds
a one-off rule and calls the kernel's own `transition()`. They land as
foreign keys `ie_<aspect>`, so OIG sees a foreign-depth change and
nothing else — the resolution at which the kernel is entitled to see
metabolism.

## Two results

* **Sixteen distinct metabolisms.** The same eight-packet world stream
  produces sixteen distinct (retained, output) signatures. In particular
  contraries differ — the metabolism layer is not subject to the OIG
  fingerprint's contrary degeneracy.
* **Under pass-through, the dual loop collapses to 1D.** A request
  carries `experience` only; a relaying leading function returns only
  what it received; the pair settles at 1D forever. Under generation the
  dual's answer arrives at 3D and the requester's 1D suggestive keeps
  `experience` and records `{norms, situation}` as residue — which is
  the theory's own description of the suggestive function. The
  `generative` flag is therefore not cosmetic; it decides whether
  duality does anything.

## Residual honesty

State is integers, strings, sets, and tuples. `verify_v4` walks every
field of a post-run state for floats and parses every source file for
float literals; both must be absent. No transition costs, weights, or
probabilities exist anywhere in the package. `patience` is an integer
tick count supplied by the caller (experimental_instrument).

## Design decisions left open (flagged, reversible)

- **Redirect rule.** Input on a producing aspect goes to its block's
  accepting partner. Alternative: refuse it. One branch in `receive()`.
- **Generation law (R5).** Full accepting dim on any input is the
  simplest reading of "strong functions generate". A staged law (one
  facet per tick) is a two-line change in `_process()`.
- **Model G chords are not wired.** `directed_chords()` (A6→A1→A8) is
  the obvious energy-path seam for a later tick phase; deliberately
  left out so no numeric energy is implied.
- **Intention is two-valued.** Ego/Super-Ego only. Id engagement is a
  vital-ring matter under R3 and needs no intention; Super-Id likewise.
- **`seat` is unread, by design.** `PureState.seat` (1..8) is set by
  archetype rules, carried into the context packet, and consumed by
  nothing in V1..V4. The theory has no "current position" primitive;
  the metabolism layer computes position from the packet's aspect via
  `position_of`, and all eight positions are live in parallel. The one
  reading that would give `seat` meaning is the estafette as a clock:
  UMA §10 supplies `R(a,v,r) = (r,v,1+a)` as a permutation of order 4,
  but not as a temporal law. If a source says focus cycles under R,
  `seat` is the right primitive and `intention_for` should read the
  block of the current seat. If focus is an emergent summary of which
  blocks were fed, `seat` is a category error and should be removed
  from `PureState` in a deliberate kernel revision with a new manifest.
  Decide on the sources; until then it stays inert.

The stack now metabolizes. The numbers still don't exist, and that is
correct.
