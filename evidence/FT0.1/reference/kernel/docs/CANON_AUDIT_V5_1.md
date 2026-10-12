# Canon audit V5.1 — intertype relations vs the engine

Sources (all external_secondary; none admitted to source_manifest):
wikisocion aggregate pages "Supervision" and "Benefit" (Meged &
Ovcharov; Slinko; Sedih; Shepetko; Stankevichyute; Vaisband; Bukalov &
Boiko; Gulenko "Criteria of reciprocity"; Gulenko & Molodtsov;
Filatova; Gorenko & Tolstikov; Ganin); Stratievskaya, mirror LII/ILE
and activation ILE/ESE; one conversational transcript on
benefit/revision helices (user-supplied, 2026-08).

Method: kernel-level claims re-derived from `pyref`; dynamical claims
run in `metabolism.develop` under the pair regime; each recorded as
AGREES / ADDS / DISAGREES. Checks in `verify_canon.py`.

## Kernel-level (all exact)
* Benefit rings SEI→LSI→ILI→EII, ILE→EIE→SEE→LSE, LII→SLI→ESI→IEI,
  ESE→IEE→LIE→SLE = kernel `v11_beneficiary` orbits, same direction.
* Supervision rings SEI→EIE→ILI→LSE, ILE→LSI→SEE→EII, LII→IEE→ESI→SLE,
  ESE→SLI→LIE→IEI = kernel `v11_supervisee` orbits, same direction.
* Ring-union characters: supervision {static/dynamic, positivist/
  negativist, process/result}; benefit {E/I, process/result,
  asking/declaring}. Kernel agrees.
* "No asymmetric relation crosses process/result" (transcript): derived.
* Stratievskaya's channel pairings 1-6, 2-5, 4-7, 3-8 for activation =
  `exchange.landing_perm`.

## Dynamical (see NOTE_V5_1.md table)
Verdicts and their check names:
* supervisee 0 @300, supervisor 3 @9 — `canon.supervisee_never_closes_in_isolation_300`
* process vs result ring identical — `canon.process_and_result_rings_indistinguishable`
* benefit then dual → 68/70 — `canon.benefit_then_dual_delays_to_serpent`
* benefit ring of 4 → altitude 3 — `canon.benefit_ring_of_four_reaches_altitude_3`
* ring + duals = ring — `canon.ring_plus_duals_no_better_than_ring_OPEN`

## What canon cannot yet adjudicate
Stratievskaya wrote no supervision or benefit articles; her corpus
tests the signal layer (per-channel valence vs `energy.signals`), not
closure. That comparison is the next audit: a 16-relation × 8-position
table of deficit/overload/support extracted from her channel sections,
scored against the engine's per-position signal profile per relation.
It does not pass through A25/A27.
