# A37 research net — what is derived, what discriminates, what a lock must carry

Build against: V5.2 canon, unchanged. Kernel untouched, manifest re-verified;
`metabolism/`, `algebra/` and every other package byte-identical to the bundle
(`diff -rq`). New: `bin/a37_rules.py`, `bin/a37_net.py`, `verify_a37.py`
(25 checks), and the outputs under `out/`. Every flip is a monkeypatch in
`bin/`, restored after use, following `completions.py` and `relay_gate.py`.
Revised after reading *A Unified Mathematical Architecture of Socionics,
Verified Revision* (sha256 41ebe1b1…; the manifest pins a different edition,
89fbd25b…): the source net is closed against the revision, and one status in
the derivation changed with it (§1, C4b).

NOTE_V5_2 left the default open and set the bar: the decision should be made
against a source or a preregistered observation, not against the prettiness
of the 0.000. Restated operationally — an acceptable artifact is one that
could have come out against relay firing. This note reports what such an
artifact can and cannot decide, by running the question rather than arguing
it.

## 1. Derivation: `relay` is three readings and one binary (`verify_a37.py`)

`relay` differs from V5 `every_tick` by:

| reading | statement | status |
| --- | --- | --- |
| C2 expenditure-turn | production only at seats with a = 1 | Shell Geometry §2 gives a formal movement ONE polarity bit, Accumulation/Expenditure (source_defined); reading it onto the seat rests on A20 (tick = movement) — proposed_completion |
| C3 engaged-block | what produces is the seat's block | `engaged_block` extended from reception to production — proposed_completion |
| C4a | A6→A1 is the activating function's expenditure, on seat 6's turn | UMA §19 "Launching initiates the Leader" fixes the direction (source); the turn is a reading |
| C4b | 8 fires with 1 on the Ego's turn (boost@2); 8 fires with the chord emission at seat 6 (boost@6) | the kernel note and UMA §19 read "receives an energy boost from the Leader" — a charging relation, wired at reception (R7). "The Leader fires and the demonstrative fires too" is the engine's phrase (energy.py, NOTE_V5_2, HLE R7 row), not the source's. Both boosts are readings |
| (iii) chord-as-turn | conduct+emit at seat 6 only; `launched` override withdrawn | proposed_completion; balance-invisible, see §4 |

Enumerating every seat-dependent firing rule F: seat → subset of the
content-emitting gas positions {1, 2, 8} (8⁸ = 16,777,216 rules; the
suggestive has gas but emits requests, which are not seat-timed under either
policy): C2 and C3 leave six rules; C4a leaves exactly four, which differ
only in whether 8 fires at seat 2 and whether it fires at seat 6. The
engine's `FIRES_AT` is (boost@2 yes, boost@6 no). The source's own proposed
schedule (UMA §24, Si→Te→Ne→Fe→Ti for IEE) enters A8 *after* A1 as a
separate stage; its closest engine analogue is boost@2 no
(`relay_noboost2`, the demonstrative firing only on its own seat).

    a37.C1_C2_C3_leave_six_rules                       6
    a37.C1_to_C4a_leave_exactly_four                   4
    a37.the_four_differ_only_in_8_at_seats_2_and_6
    a37.engine_FIRES_AT_is_the_boost2_noboost6_survivor
    a37.engine_note_for_A8_is_receives_a_boost_not_fires_too
    a37.every_tick_violates_C2

So the numerical rule is no longer a free choice. What remains free is the
readings, each separately switchable in `a37_rules.RULES`. The boost
readings are invisible on the balance table (§4) and decisive in the yield
table: **under seat-timed production, the kindred and supervision channels
are carried by the demonstrative firing on the valued lap.** With 8 firing
only on its own seat, kindred is sterile and the supervisor closes nothing
before the Serpent — at every one of the eight instrument settings.
`kindred ≡ duality`, a locked theorem under both policies, rests under
`relay` on a reading the source does not fix.

## 2. The family: which reading moves which row (`out/family.json`)

Representative pairs (`ile` and `esi` bases agree on every relation; type
invariance and contrary symmetry survive across the family), 120 ticks,
instrument defaults.

| relation | every_tick | relay | relay_boost6 | relay_noboost2 (sequential) | noboost2_boost6 | turn_only (C2) | block_only (C3) | turn_block (C2+C3) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| supervision | latA 4, latE 7, **comp 9** | **comp 5**, latE 7, latA 73 | **comp 4**, latE 6, latA 73 | latE 68 only | **comp 4**, latE 6, latA 73 | **comp 4**, latE 6, latA 73 | **comp 5**, latE 8, latA 75 | **comp 5**, latE 7, latA 74 |
| duality | comp 4, latE 7 | comp 5, latE 9 | comp 5, latE 11 | comp 5, latE 9 | comp 5, latE 11 | comp 4, latE 8 | comp 5, latE 71 | comp 5, latE 9 |
| kindred | comp 4, latE 6 | comp 5, latE 9 | comp 4, latE 8 | **—** | comp 4, latE 8 | comp 4, latE 8 | comp 5, latE 8 | comp 5, latE 9 |
| activation | latA 4, comp 8, latE 11 | latA 5, comp 9, latE 14 | latA 5, comp 12, latE 18 | latA 5, comp 10, latE 16 | latA 5, comp 12, latE 18 | latA 4, comp 6, latE 9 | latA 5, comp 7, latE 10 | latA 5, comp 10, latE 20 |
| identity / semi-dual | latA 3 | — | latA 68 | — | latA 68 | latA 68 | — | — |
| super_ego | latE 68 | — | — | — | — | latE 68 | latE 68 | — |
| mirror | — | latE 68 | latE 68 | latE 68 | latE 68 | — | latE 68 | — |
| benefit ×2, supervisee, conflict, contrary, business, mirage, quasi | — | — | — | — | — | — | — | — |

Four facts, checked in `verify_a37.py`:

* **The supervisor's early lateral-first closure exists only under
  `every_tick`.** Every seat-timed rule with the demonstrative on the valued
  lap gives complement-first — C2 alone, C3 alone. The "natural
  discriminator" named in NOTE_V5_2 tests whether production follows the
  relay at all; it cannot pick `relay` out of `turn_only` or `block_only`.
* **Kindred and supervision are carried by the demonstrative on the valued
  lap.** With 8 firing only on seat 8 (the source-sequential reading),
  kindred is sterile and the supervisor has nothing before the Serpent;
  duality is untouched. This holds at all eight instrument settings.
* **The one-tick delay is reading C3.** `turn_only` keeps the dual's first
  closure at tick 4.
* **The identity/semi-dual closure at tick 3 exists only under
  `every_tick`.** Where it returns in the family it returns through the
  Serpent (≥ 64), i.e. through `BORED_WINDOW`.

The rows on which family members differ from one another are the Serpent
rows and timings. They are the weakest evidence the engine offers, because
they carry an instrument integer.

## 3. The grid: every_tick vs relay across every flip the repo exposes (`out/grid.jsonl`)

256 cells: A23 gate × patience {1, 2} × window {2, 3} × A25 {tick, exposure}
× A27 {on, off} × chord gate {gated, open} × delivery {always, gated} ×
BORED_WINDOW {64, 32}; pair regime, 120 ticks, both policies per cell, base
`ile`. Type invariance is asserted at defaults for all 256 ordered pairs
(`verify_v5_2`), across the rule family on two bases (`verify_a37`), and
re-checked on the grid with a second base (`esi`) in 12 cells covering all
eight instrument settings plus four completion flips: 12/12 agree on every
relation (`out/invariance_spotcheck.json`). It is not asserted for the
remaining 244 cells.

**Completion-independence (A35 extended).** For the supervision row the
five completion/instrument flips A23 gate, A25, A27, chord gate and
BORED_WINDOW are exactly neutral (64/128 each). What moves it is patience,
window and delivery.

**Where the supervisor discriminator holds.** (every_tick, relay) first
closure, 32 completion cells each, all constant within the setting:

| patience, window, delivery | every_tick | relay | verdict |
| --- | --- | --- | --- |
| 1, 2, always / gated | lateral_A | complementary | holds |
| 1, 3, always | lateral_A | complementary | holds |
| 2, 2, always | lateral_A | complementary | holds |
| 1, 3, gated | complementary | complementary | no discrimination |
| 2, 2, gated | complementary | complementary | no discrimination |
| 2, 3, always / gated | complementary | lateral_A | **reversed** |

**The activation row is the every_tick detector.** Under `relay` the
activator's first closure is lateral_A in 256/256 cells. Under `every_tick`
it is lateral_A only at (1, 2); complementary in 176 cells, lateral_E in 16.

**Joint decision matrix, first closures (activation, supervision):**

| observed | consistent with | verdict |
| --- | --- | --- |
| (complementary, ·) | every_tick only | decisive |
| (lateral_A, complementary) | relay only (six of eight settings) | decisive |
| (lateral_A, lateral_A) | every_tick @ (1,2,·) or relay @ (2,3,·) | ambiguous |

The ambiguous cell is ordinally irreducible in the pair regime: every_tick
at (patience 1, window 2) and relay at (patience 2, window 3) produce the
same closure-class sequences on all sixteen relations, up to
completion-dependent overlaps (`benefit`, `supervision` second closures
under gated delivery). A37 is therefore confounded with (patience, window)
along exactly one line. Patience is in principle observable independently
of closures — it is the request rate at the suggestive (infants request
every tick; A29) — which is the observable that would break the confound.

**Fragile rows, recorded so they are not preregistered:**

* relay identity/semi-dual sterility: only at patience 1, window 2,
  BORED_WINDOW 64 (32/128 cells); the Serpent returns lateral_A otherwise.
* every_tick benefit closure: 32 cells, all under gated delivery with the
  chord gate open and A25 on ticks. Relay benefit is sterile in 256/256.
* super-ego and mirror: Serpent rows; both policies vary with A25 and
  BORED_WINDOW.
* duality and kindred: complement-first in all 512 policy-cells. Structural,
  non-discriminating.

## 4. Balance decomposition: what makes the lap 2+2 (`out/balance.json`)

`bin/balance.py` machinery, altitude 3, world on the accepting seat.

| rule | gate off: balance / idle | gate on: balance / idle |
| --- | --- | --- |
| every_tick | 0.628 / 0.112 | 0.334 / 0.249 |
| turn_only (C2) | 0.496 / 0.041 | 0.332 / 0.249 |
| block_only (C3) | 0.564 / 0.124 | 0.159 / 0.136 |
| turn_block (C2+C3, V5 chord wiring, launch kept) | 0.219 / 0.016 | 0.002 / 0.002 |
| relay (C2+C3+(iii)) | 0.224 / 0.019 | 0.000 / 0.005 |
| relay_boost6 | 0.200 / 0.048 | 0.003 / 0.005 |
| relay_noboost2 (sequential) | 0.119 / 0.010 | 0.002 / 0.004 |
| relay_noboost2_boost6 | — | 0.003 / 0.005 |

* The note's "V5 0.334" is every_tick **with** the A23 gate installed
  (`verify_v5_2` sets `RELAY_GATE = True` before both measurements). True
  V5 defaults give 0.628. The gate alone takes every_tick from 0.628 to
  0.334; relay alone takes it to 0.224; together, 0.000.
* **Neither reading alone produces the 2+2.** C2 with the gate gives 0.332,
  C3 with the gate 0.159. The pure finding is the conjunction C2 ∧ C3 (with
  the gate), which strengthens the note's "no wiring of the chord alone".
* **Reading (iii) is balance-invisible.** `turn_block` — C2 and C3 with V5
  chord wiring and the `launched` override retained — gives 0.002. Its
  only footprints are in the yield table (mirror's Serpent row, activation
  and supervisor timings).
* **The boost readings are balance-invisible too.** All four C4a survivors
  give ≤ 0.003 with the gate. The 2+2 lap is C2 ∧ C3 and nothing else; the
  boosts decide channels, not balance.

## 5. Source net

Reachable governing text: Unified Shell Geometry v1.1 as the Project's text
rendering (hash ≠ manifest), and *A Unified Mathematical Architecture of
Socionics, Verified Revision* (sha256 41ebe1b1…; the manifest pins 89fbd25b…,
an earlier edition — every quotation below is from the revision and should
be re-checked against the sealed edition before the manifest is touched).
The OIG Examiner Edition and the Shadow Complex remain unread.

| passage | bears on | verdict |
| --- | --- | --- |
| UMA §10: R(a,v,r) = (r, v, 1⊕a); two parallel four-cycles; R² = Activation; G = F₂³ ⋊ D₄, order 64; "coupled, noncommuting estafette and Benefit/Supervision four-phases" | A20 | kernel ESTAFETTE confirmed. The dynamic vocabulary ("four-phases", §26 "estafette dynamics") is there — and so is the caution, in the same section: *"carrier geometry ≠ dynamics acting on the carrier. The same affine cube can support several distinct lawful cycle structures."* A20 is a reading the source names and warns about in one breath. |
| UMA §13: σ = 1⊕a is Model G's accepting/producing polarity | C2 | the polarity is source_defined as a static coordinate; nothing binds production to it in time |
| UMA §17: one current functional state x_t ∈ E; "Model A position of an IE ≠ current functional state" | C3 | the source's fast dynamics has one active IE at a time. Consistent with localised production; but x_t is an element, not a block, and its dynamics is the kernel K_T (§20), an empirical object, not R. Consistent-with, not fixed-by |
| UMA §19: G4→G1 "Launching initiates the Leader"; G1→G2 "the Creative receives an energy boost from the Leader"; spine A6→A1→A8 | C4a, C4b | directions confirmed (G2 = A8 under the §13 reindexing). The boost is a charging relation. Nothing on simultaneous firing |
| UMA §24: proposed cycle Si→Te→Ne→Fe→Ti⇝Si for IEE, "a five-stage energetic schedule", "not asserted as a universal psychic law" | A20, C4b | the source's own dynamical proposal is *not* the estafette lap (it uses two R-steps, both chords, and crosses v through A1→A8), and it enters A8 after A1 as a separate stage — the sequential reading |
| UMA §20, §21, §28: K_T proposed, no numerical kernel; "energetic expression ≠ remaining energetic reserve"; dynamical laws unspecified | all | timing of production is explicitly among the open dynamical parameters |
| UMA Appendix A | all | "every finite claim of Parts I–III, and every static claim of Parts IV–V" is machine-verified; the dynamics is not |
| Shell Geometry §2: m_t = (o_t, d_t, p_t), "polarity requires one additional bit" | C2 | supports C2 at movement resolution: one movement, one polarity. Reading it onto the tick is A20 |
| Shell Geometry §15 names cp "the counterphase map" | — | vocabulary note: the mind/body operator has a source name |

**Verdict of the source path.** No passage in either reachable governing
document fixes the timing of production at position resolution. What the
revision does fix: the chord directions (C4a's direction), the boost as a
charging relation (so C4b is a reading, and the corpus phrase "the Leader
fires and the demonstrative fires too" should be re-attributed to the
engine in energy.py, NOTE_V5_2 and HLE §11 R7), and — twice, in §10 and
§24 — that the estafette is a cycle structure on the carrier, not the
source's dynamics. A source-defined promotion of A37 is not available from
these texts. The source path is closed, negative.

## 6. What an acceptable artifact now looks like

**Source.** Closed, negative (§5): UMA §10 and §19 do not bind production to
the relay's turn, and §10 warns against the identification. C2 keeps its
partial support from Shell Geometry §2; C3 has §17's single active state as
consistent-with; the boosts stay switches. Promotion of A37 now runs
through observation only.

**Preregistered observation.** The lock is `out/a37_prediction_table.json`,
sha256(body) `97ae16f8…e1e99f`: ordinal closure-class sequences for both
policies at each of the eight (patience, window, delivery) settings, with a
completion-independence flag per entry, plus `relay_noboost2` at the same
eight settings (completion defaults only). Ticks are dropped; only order is
locked. The design is two dyads per participant, activator and supervisee,
coded blind to the classes of §3; the decision matrix is the one above;
patience is fixed by the request rate before closures are read. Failure
conditions: activation complement-first refutes relay in every setting;
(lateral_A, complementary) refutes every_tick in every setting; supervisee
arms closing refutes the type invariance upstream of A37 (A35), and then
neither policy survives.

**The boost discriminator.** Whether the kindred channel delivers the
complement at all separates the boost readings inside seat-timed
production, and it is not a Serpent row: kindred complement-first under
every rule that fires 8 on the valued lap (and under every_tick), sterile
under the sequential reading, at all eight instrument settings. A kindred
dyad added to the two above makes the lock three rows.

**Derivation.** Done as far as the engine allows: `FIRES_AT` is forced by
C2 ∧ C3 ∧ C4a up to the two boost readings. Promotion of A37 to `derived`
now means promotion of C2 and C3, not of the rule.

## Status

Nothing here changes a default. `tick.FIRING_POLICY = "every_tick"` and
`clock.RELAY_GATE = False` stand. What changed is the shape of the open
decision: it is no longer "relay or every_tick" but "does production follow
the seat's polarity (C2), does the engaged block produce (C3), and does the
demonstrative fire on the valued lap (C4b)" — three readings, each with a
named observable, one with partial source support, the first two jointly
sufficient for the 2+2 and jointly confounded with (patience, window)
along one line that the request rate can break, the third deciding whether
kindred and supervision are channels at all.

    python3 verify_a37.py                       # 25 checks, ~25 s
    python3 bin/a37_net.py family  out          # ~20 s
    python3 bin/a37_net.py grid    out [lo hi]  # 256 cells, ~15 min; chunkable
    python3 bin/a37_net.py balance out          # 12 tables, ~8 min
    python3 bin/a37_net.py analyze out
    python3 bin/a37_net.py lock    out          # emits and hashes the prediction table
