# NOTE_V2 — Holonic Living Engine V2: Identity + Development + Memory

Build against: Holonic_Living_Engine_V2_Specification.docx (August 2026)
Kernel: Holonic_Living_Engine_V1.zip, byte-identical (SHA-256 manifest).

## What shipped

    holon_tower/      schema.py  tree.py  seal.py          Development
    fools_memory/     schema.py  encode.py  retrieve.py  store.py   Memory
    intention/        context.py  generate.py  rules_v2.json        Intention
    manifests/kernel_sha256.json                           purity lock
    verify_v2.py                                           54 checks

Implementation order followed exactly as spec §8: kernel re-verified
first, then tower, then memory, then register, then context, then
generator, then the end-to-end walk (create TIM Holon → store one
Fool's loop → assemble context → generate intention → transition →
observe). That walk is check `e2e.step_transitions` and its three
companions.

## Acceptance

    python3 verify_v2.py        # 54/54, exit 0
    python3 bin/le.py verify all  # 116/117 (see Known gap)

## Hard invariants — how each is enforced

1. **Kernel purity.** `pyref/` untouched; SHA-256 manifest taken from
   the pristine V1 archive and re-checked on every suite run
   (`v2.kernel.sha256_manifest_matches`). Nothing in the three new
   packages writes into `pyref/` or shadows its modules.
2. **Particularity preserved.** `MemoryRegister.put` is append-only;
   duplicate ids rejected; no bulk erase exists; `forget()` removes
   exactly one loop explicitly and returns it. Shells payloads with
   `particularity_guard != true` are rejected at the schema level.
3. **Addressability doctrine.** Loops carry `storage_phase` which must
   be `super_ego`; anything else is rejected (`store_super_ego_only`).
   Ego and Identity values are derived by the +9 ladder at read time
   (`vertical_check`), flagged `derived: true`, and only exist where
   the band permits.
4. **Fool is cursor only.** Residue 0 is rejected both at validation
   (`fool_not_addressable`) and at retrieval — `locate(residue=0)`
   errors rather than returning an empty match.
5. **Trajectory consistency.** Tower and shell mutations are computed
   as pure payloads in `tree.py` and land on a Holon only through
   `transition()` via `materialize_rule()` — a one-rule table passed as
   an explicit argument, per the kernel's no-hidden-globals design.
   Checked: version bump, trajectory extension, projection carry.
6. **Three pillars required.** `require_complete()` gates the
   generator; a packet missing Development or Memory refuses with
   `incomplete_pillars` (two dedicated checks).

## Design decisions the spec left open (flagged, reversible)

- **Register placement:** the preferred option from §5.3 — a parallel
  map keyed by Holon id (`fools_memory/store.py`), persisted as
  `fools_register_v1` JSON. `content.foreign["fools_memory"]` was not
  used; content stays clean for OIG.
- **Band semantics:** band is an inclusive "lo-hi" value window; the
  Super-Ego value is the smallest member of the residue class inside
  the window, Ego = SE+9, Identity = SE+18 where the window permits.
  This reproduces the Manual's worked example exactly: residue 5,
  band 4-18 → SE 5, Ego 14, no Identity
  (`fools.band_4_18_residue_5_gives_se5_ego14_no_identity`).
  `encode.choose_band` derives the minimal band from phases needed; an
  explicit wider band (like 4-18) is always accepted instead.
- **Suit pairing:** Cup↔Heart, Sword↔Spade, Coin↔Diamond, Wand↔Club —
  an involution, checked as such. If the Manual pairs differently,
  it is one table (`SUIT_PARTNER`) to change.
- **Tower legality:** activation may not skip more than one vMeme above
  center; center advances only when all four quadrants of the current
  center are active AND bloom ≥ Apply; bloom is monotone within a
  center and resets on advance; sealing is one-way (no `unseal`
  exists). These are the tightest readings consistent with §4; each is
  a single constant or predicate in `tree.py` if the previously
  specified tower document says otherwise.
- **Court ranks:** Page/Knight/Queen/King → 11–14.
- **Generator:** deterministic rule-based scorer (memory-token overlap,
  recent replays weighted 2×, lexicographic tie-break). An external
  generator (LLM) can be plugged into `generate(..., generator=fn)`;
  its output is validated against the rule table, so nothing illegal
  reaches `transition()` (`intent.external_generator_validated`).
- **rules_v2.json:** superset of `configs/rules.json` plus a `scholar`
  archetype exercising the new gates (`min_center`, `min_bloom`,
  `requires_unsealed`, `grounding`). The kernel ignores the extra
  fields; only the intention layer reads them. Tower-mutating deltas
  are deliberately NOT stored as static rules — a static
  `cape_phase` in JSON would clobber computed state.

## Known gap (environmental, not a regression)

The V1 archive ships without `apps/le_legacy/` (the frozen v1.1 tree),
so `legacy.frozen_v11_sources_present` fails and cascades into two
checks in `verify_holon.py`. Every substantive kernel check passes
(116/117 and 51/53). `verify_v2.py` asserts that these and ONLY these
fail; any new failure breaks the suite. No stub was fabricated to make
the number pretty. Drop the original `apps/le_legacy/` tree in place
and all three go green with no other change.

## Hands-off respected

- pyref/ — untouched (manifest-verified)
- apps/, configs/, bin/, schemas/, fixtures/, studies/, analysis/ — untouched
- No kernel import is monkey-patched; no module shadows a kernel name.

Identity. Development. Memory. Three pillars, one coherent intention —
and every claim above is a named check in verify_v2.py.
