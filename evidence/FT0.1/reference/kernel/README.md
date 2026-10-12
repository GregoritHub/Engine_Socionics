# Holonic Living Engine V5

A formal model of individuation, implemented so that it can be checked
rather than believed, and wrapped in an experiment platform designed so
that the psychological claims can be *tested* rather than assumed.

Three governing documents define the architecture. Nothing here is entered
by hand that could instead be generated from them:

* **Unified Shell Geometry and Developmental Dynamics v1.1** — the Crux,
  OIG, the Shell, demand, and the altitude law.
* **The Individuation Atlas v1.3** — the sixteen type geometries.
* **Unified Mathematical Architecture of Socionics** + **OIG Examiner
  Edition** — the finite-affine kernel underneath both.

    python3 verify_v5.py          # 106 checks — algebra + metabolism (V4/V5)
    python3 verify_v3.py          #  80 checks — the V3 developmental layer
    python3 verify_v2.py          #  54 checks — the V2 three-pillar layer
    python3 bin/le.py verify all  # 117 checks — the kernel and platform
                                  #   (116/117 in this bundle; see Known gaps)

No dependencies for any of the above. Python 3.8+, standard library only.

---

## What V4 and V5 added

V3 verified the geometry of Model A and never moved an aspect through
it. V4 built `metabolism/`: IE-typed packets, per-TIM reception, the
facet gate, block production, transfer over the relation group, and a
generative loop. V5 unified the vocabularies under `algebra/` — the
Crux perspectives, OIG domains and the Atlas club table are all images
of one affine map on the IE cube; the facet ladder is the unique nested
law consistent with the kernel's dimension formula; Kępiński's three
categories are the three position coordinates; Gulenko's energy levels
are a degree-2 formula over them — and coupled development to
metabolism through the sourced return chord. See `NOTE_V4.md`,
`NOTE_V5.md`, and `docs/ASSUMPTION_LEDGER.md` A13–A21.

    python3 bin/metabolize.py iee sli 4 --developed   # one dual exchange, traced
    python3 bin/socion.py                              # the five environment regimes

## What V3 added, and why

V2 had no word for what a system was *required* to do. Without a demand
term, **rest and foreclosure are the same object** — both look like a
holon sitting on its native self-route, and no amount of trajectory detail
separates them. That is not an implementation gap; it is a theorem
(Atlas 8.3, Demand-Blindness), and it is why the Shell detector has to be
joint rather than purely observational.

V3 introduces four things, in dependency order:

**1. Demand is a first-class object** — `demand/schema.py`. V2 contained
zero occurrences of `demand`, `conductiv`, `foreclos`, `altitude`, or any
of the sixteen route names across 118 files. Without it the four
self-routes are pathological merely for existing.

**2. The two projections meet** — `demand/protocol.py` renders a Crux walk
as an OIG content path, so `pyref.oig` computes (V, N, K, R) over the very
object the Crux names. One process, two resolutions, as the source
requires.

**3. The Shell is structured** — `crux/shell.py`. `x = (m, S, ι)` with
`π(m,S,ι) = m`, five enumerated signs, and ι carried separately from the
sign set so intensity varies without changing Shell identity. Clearance
and suppression are distinguished: dropping ι while keeping every sign is
not development.

**4. Altitude is counted, not indexed** — `holon_tower/altitude.py`
implements `H_(k+1) = min{H' > H_k : C(H',D) ≠ ∅}` as an actual search over
capacity extensions. The module deliberately exposes **no successor
function on tiers**, and `verify_v3` asserts that absence.

> The predecessor payload `tower_v1` — nine vMemes × four AQAL quadrants,
> advancing on all-quadrant activity — is retained and still validates,
> but it is no longer the law. It advances with no demand term, never
> consults Shell state, and treats its tiers as primitive coordinates. The
> governing source forbids all three.

## Reading order

Start here and the rest follows. Roughly two hours end to end.

| # | Read | Why |
| --- | --- | --- |
| 1 | `crux/perspectives.py` | 4 perspectives as 2 bits, 16 routes. Everything is built on this. |
| 2 | `crux/typemap.py` | The 16 type maps, **generated** from the locked stacks. Nothing per-type is written. |
| 3 | `demand/schema.py` | Demand, Organization, and the conductivity test `C(H, D)`. |
| 4 | `crux/shell.py` | Realizations, the five signs, clearance vs suppression. |
| 5 | `holon_tower/altitude.py` | The altitude law. The payoff. |
| 6 | `demand/detector.py` | The four states, read off the γ₀ / γ_D perturbation pair. |
| 7 | `verify_v3.py` | 80 checks. The claims, executable. |
| 8 | `algebra/perspective.py` | V5: the Crux, OIG domains and the club table as one affine map. |
| 9 | `metabolism/tick.py` | V5: content actually moving through Model A, committed to the kernel. |

## Layout

    algebra/        one content algebra: perspective, content,
                    facets, kepinski, archetype           V5 unification
    metabolism/     packet, state, handler, energy, clock,
                    exchange, chord, boredom, complex,
                    observe, develop, tick                V4/V5 metabolism
    crux/           perspectives, type maps, Shell        structural layer
    demand/         demand, protocol, detector            the V3 term
    holon_tower/    altitude (tower_v2), schema, tree     Development pillar
    fools_memory/   loop store, encode, retrieve          Memory pillar
    intention/      context packet, generation            three pillars -> one intention
    pyref/          the kernel — SEALED, see below        1:1 Python mirror
    apps/           le_core le_socionics le_oig
                    le_dynamic le_empirical le_api        Erlang implementation
    analysis/       fit_models, diagnostics, reports,
                    compare_models, power_simulation      needs numpy
    bin/le.py       CLI (Python; works with no Erlang)
    bin/le          CLI (Erlang escript; needs rebar3)
    schemas/        versioned record schemas
    studies/        pilot_001 demonstration study
    fixtures/       participants, task registry, synthetic generator
    manifests/      kernel SHA-256 seal, source manifests
    docs/           reports, ledgers, protocol, audits

## The kernel is sealed

`pyref/` is byte-frozen. Every file is SHA-256 pinned in
`manifests/kernel_sha256.json`, and **every** verification suite
(`verify_v2`, `verify_v3`, `verify_v5`) checks the manifest on every run.
`verify_v3` additionally asserts that no V2 or V3 package can write into
it; `verify_v5` asserts the same for `algebra/` and `metabolism/`.

This is deliberate, and it is the load-bearing discipline of the whole
repository: the layers above `pyref/` may only *read* the locked
architecture. A type map that disagreed with the kernel could not be
written into existence — it would have to be derived, and the derivation
would fail. If you are modifying this repository, treat `pyref/` as
read-only. Changing one byte fails all three suites at their first check.

## Run the demonstration study

Labeled synthetic data, end to end. Every step is append-only and
ledgered; predictions lock before outcomes exist.

    python3 bin/le.py study create studies/pilot_001.json
    python3 bin/le.py study freeze pilot_001
    python3 bin/le.py participant import pilot_001 fixtures/participants.csv
    python3 bin/le.py trial randomize pilot_001
    python3 bin/le.py predictions freeze pilot_001
    python3 fixtures/make_synthetic_observations.py data/pilot_001 obs.jsonl
    python3 bin/le.py observations import pilot_001 obs.jsonl
    python3 bin/le.py export blind pilot_001
    python3 bin/le.py export theory pilot_001        # writes 0 rows: synthetic
    python3 bin/le.py export theory pilot_001 --include-synthetic --dev-override
    python3 bin/le.py analyze pilot_001 --dev-synthetic
    python3 bin/le.py report pilot_001

The unflagged `export theory` writing zero rows is not a bug — it is
confirmatory analysis refusing synthetic records. Overriding it requires
two explicit flags and stamps `SYNTHETIC / NOT EMPIRICAL` on every
downstream artifact.

`analyze` and `report` need `pip install -r requirements.txt` (numpy).
Everything else is standard library.

## Erlang build

    rebar3 compile && bin/le verify all && rebar3 eunit

The Erlang sources are the deliverable implementation; the Python mirror
under `pyref/` is the executable proof of behavior, following the v1.1
precedent. They ship uncompiled here — see `docs/KNOWN_LIMITATIONS.md`.

## Epistemic discipline

This is the part worth reading before judging the rest.

**Every theory constant carries a source-status tag**: `source_defined`,
`derived`, `proposed_completion`, `empirical_estimate`,
`experimental_instrument`, or `legacy`. Items the sources do not decide
are carried as `unresolved_source_extraction` and never guessed —
`docs/UNRESOLVED_SOURCE_ITEMS.md` lists them, with a machine-readable
`.json` beside it.

**No transition costs are hard-coded anywhere.** All numerical behavioral
parameters must be estimated from data. Unfitted models return `unknown`
rather than inventing a number.

**Two levels are kept apart throughout**: derived mathematical claims about
the architecture, and empirical claims about people. The first are proved
here. The second are not, and statistical model comparison is never
presented as proof of Socionics.

**The sources are audited, not trusted.** `docs/SOURCE_AUDIT_V3.md`
re-derives every structural claim in both governing documents from the
kernel — 400+ assertions — and records where they disagree. Every
machine-generated table in both documents checks out; the errors found are
in authored prose, including one `[S]`-labelled route claim that is wrong
for half the socion. Where a result depends on which of two readings of a
source you take, the audit says so rather than picking quietly.

## Known gaps

* `apps/le_legacy/` (the frozen v1.1 tree) is not in this bundle, so
  `legacy.frozen_v11_sources_present` fails — 116/117 rather than 117/117.
  Expected, and the only failing check.
* Four design decisions are flagged open and reversible in `NOTE_V3.md`:
  the conductivity criterion, foreclosure carriers, the sign → (K,R)
  correspondence, and higher-order closure.
* **The Jungian baseline is missing from the fitted ladder.** SPEC §42 and
  `pyref.features.model_feature_sets()` define six models, M0–M5;
  `analysis/fit_models.py` fits four. The absent M1 is plain Jungian
  E/N/T/P — the control that answers whether the structural signal is just
  dichotomies in Model A notation. It cannot currently be fitted because
  `features.extract()` never emits its four columns, though
  `pyref.core.jungian_coord()` computes them. Until it is run, the reported
  M0 < M2 < M3 < M4 comparison is conditional on a control that is missing.
  See the header of `analysis/fit_models.py`.


V5.2: NOTE_V5_2.md — relay firing (A37), provenance walks (A38), cognitive styles as a subgroup (A39); verify_v5_2.py.

V5.2.1 (notes only; defaults and packages unchanged, energy.py docstring
re-attributed): docs/A37_RESEARCH_NET.md — A37 decomposed into readings,
the 256-cell discriminator grid, the balance decomposition, the source net
closed against the UMA Verified Revision; verify_a37.py (25 checks);
bin/a37_rules.py, bin/a37_net.py; ledger A40–A41; unresolved item 11.
