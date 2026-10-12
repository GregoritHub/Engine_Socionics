# NOTE_V3 — Holonic Living Engine V3: Demand, Shell, Generated Altitude

Build against: Unified Shell Geometry and Developmental Dynamics v1.1
(Readable Edition) and The Individuation Atlas v1.3 (Readable Edition).
Kernel: unchanged, SHA-256 manifest re-verified.

## Why this build exists

`NOTE_V2` flagged tower legality as a reversible decision: "the tightest
readings consistent with §4 ... a single constant or predicate in
`tree.py` if the previously specified tower document says otherwise."

The tower document arrived. It says otherwise about the *primitive*, not
the constant. `tower_v1` is nine vMemes × four AQAL quadrants advancing on
all-quadrant activity plus bloom. The governing source forbids exactly
that construction on three separate counts:

* it advances with no demand term, against "there is no architectural
  gradient out of the ground state; demand is required to initiate
  movement";
* it never consults Shell state, though altitude is *defined* by whether
  the organization can meet demand without persistent Shell distortion;
* its tiers are primitive coordinates, against "tiers are possible
  emergent summaries, never primitive coordinates."

`tower_v1` is retained and still validates. It is no longer the law.

## What shipped

    crux/         perspectives.py  typemap.py  shell.py     Structural + Shell
    demand/       schema.py  protocol.py  detector.py       Demand + D_Shell
    holon_tower/  altitude.py                               Generated closure
    verify_v3.py                                            75 checks

Modified in place: `holon_tower/schema.py` (tower_v2 payload + dispatch),
`intention/context.py` (version dispatch), `intention/generate.py`
(altitude gates, scoring hoist), `fools_memory/store.py`,
`fools_memory/encode.py`.

## Acceptance

    python3 verify_v3.py          # 75/75, exit 0
    python3 verify_v2.py          # 54/54, unchanged
    python3 bin/le.py verify all  # 116/117 (same known legacy gap)

## The four load-bearing changes

1. **Demand is a first-class object.** `demand/schema.py`. Nothing in V2
   contained the term — zero grep hits across 118 files for `demand`,
   `conductiv`, `foreclos`, `lateral`, `altitude`, or any of the sixteen
   route names. Without it, rest and foreclosure are the same object, and
   the four self-routes are pathological merely for existing.

2. **The two projections now meet.** `demand/protocol.py` renders a Crux
   walk as an OIG content path, so `pyref.oig` computes (V, N, K, R) over
   the very object the Crux names. `oig.shell_of(N,V)` was already
   definitionally identical to `cancellation_K` — the OIG-side Shell
   footprint had been implemented all along and was never connected to
   `pure_state.shells`.

3. **The Shell is structured.** `crux/shell.py`. `x = (m, S, ι)` with
   `π(m,S,ι) = m`, the five enumerated signs, and ι continuous in [0,1]
   carried separately from the sign set so intensity varies without
   changing Shell identity. Foreclosure excludes the four activation
   signs by construction. Clearance and suppression are distinguished:
   dropping ι while keeping every sign is not development.

4. **Altitude is counted, not indexed.** `holon_tower/altitude.py`
   implements `H_(k+1) = min{H' > H_k : C(H',D) ≠ ∅}` as an actual search
   over capacity extensions ordered by the generated dwelling-cost ladder.
   The module deliberately exposes no successor function on tiers, and
   `verify_v3` asserts that absence. Closure requires all three of: the
   capacity retained rather than visited, the return route traversed, and
   the Shell cleared rather than suppressed.

## Two results the documents do not state

* **Scale is a quadra invariant.** The Atlas states it only for Alpha.
  Generated from the stacks: Alpha and Gamma are entirely collective-scale
  (surface flip WE↔ITS); Beta and Delta entirely individual-scale (I↔IT).
  Check `crux.scale_is_a_quadra_invariant`.

* **First-order development never branches.** The source requires that
  equally-minimal solutions be preserved as a branch. Exhaustively over
  all sixteen TIMs and all fifteen non-empty demand destination sets, the
  minimal extension is always unique — because the dwelling-cost ladder
  7/6/4/3 has no ties. Branching, if it exists, is a higher-order
  phenomenon. Check
  `altitude.minimal_extension_is_unique_no_first_order_branching`.

## One correction to the Atlas

Atlas Part 5 ("Embodiment") states the return route as a fixed pair per
scale: IT → I = Embody for individual-scale types, ITS → WE = Educate for
collective-scale. Generated from the stacks, the return route is
structurally *complementary → native* — the inverse of the first crossing
— for every TIM. The Atlas's named pairs are correct for exactly the eight
TIMs whose native perspective is **interior** (second bit 0: I, WE). The
eight exterior-native TIMs return by Express (ST club: LSE, LSI, SLE, SLI)
or Institutionalize (NT club: ILE, ILI, LIE, LII).

The claim is restricted, not wrong, and the restriction is clean. Part 5
should carry the qualification, or each chapter should name its own return
route from the type map rather than inheriting a scale-level default.
Check `crux.atlas_return_route_claim_holds_only_for_interior_native`.

## Three V2 defects closed

* `MemoryRegister.loops()` shallow-copied the list but shared the loop
  dicts, so a caller could rewrite vertices, strength or residue without
  passing through `validate_loop`. The particularity guarantee was true at
  the door and false at the window. Reads are now deep copies; `put()` was
  already safe.
* `choose_band` promised "exactly the requested phases" and silently
  widened. The +9 ladder is contiguous, so exactness is only satisfiable
  for prefixes of (super_ego, ego, identity); non-prefix requests are now
  rejected rather than served wrong.
* `_memory_tokens` ran once per candidate per `generate()`, rebuilding the
  full token bag over every loop. Hoisted; now once per call.

## Design decisions left open (flagged, reversible)

- **Conductivity criterion.** A movement is conductive when its
  destination is a *retained* capacity. Visiting is not retaining — that
  distinction is the whole point of N versus V — but the source does not
  fix how a capacity transitions from visited to retained. Currently that
  is caller-supplied. One predicate in `demand/schema.py`.
- **Foreclosure carriers.** Atlas 8.5 leaves H_R / H_I / H_RI open.
  `crux/shell.py` carries the carrier field and defaults it to `"open"`;
  nothing infers it.
- **Sign → (K,R) correspondence.** The source is explicit that the map
  from individual Crux Shell signs to specific K,R patterns has not been
  derived. `detector.py` therefore classifies into four states and reports
  K and recurrence counts, but never claims a sign from a trajectory.
- **Higher-order closure.** `close()` increments altitude and records the
  retained set. It does not yet build H_(k+1) as a holon containing H_k as
  a constituent; the kernel's `embed_child` is the obvious seam.

## Hands-off respected

- `pyref/` — untouched, manifest-verified, and asserted un-writable from
  the new packages.
- `apps/`, `configs/`, `bin/`, `schemas/`, `fixtures/`, `studies/`,
  `analysis/` — untouched.
- `verify_v2.py` — untouched and still 54/54.

Demand. Shell. Altitude. The tower no longer climbs by itself.
