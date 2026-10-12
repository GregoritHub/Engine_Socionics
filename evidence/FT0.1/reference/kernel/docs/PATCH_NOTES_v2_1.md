# Patch notes — v2.1 (audit release)

Independent audit of v2 against (a) the verified/corrected revision of the
Unified Mathematical Architecture paper (whose Section 24 cycle was fixed:
the Ti -> Si return is not a primitive move) and (b) the OIG Examiner
Edition quantitative layer.

## Verdict of the audit

The kernel was fully correct: every theory constant re-derived
independently (frames, dimensionality fields, Reinin dual, relation group,
order-64 dynamical group, Model G reindexing, OIG endpoint geometry)
matched. The defects found were in the *experimental design layer* and in
*coverage*, not in the mathematics.

## Defects fixed

1. **studies/pilot_001.json — mislabeled mechanism.** The old
   `predicted_intermediate` condition used Fe with the rationale "Fe is on
   a shortest Ne-Ti route". False: the shortest-route intermediates for the
   IEE reference TIM are exactly Fi and Se; Ne -> Fe exists only as a
   directed Model G chord (pure-cube waypoint length 4, hybrid length 2).
   The condition therefore tested the M4 hybrid-graph mechanism while the
   study's primary hypothesis was M3 routing distance. Fixed: the shortest
   route condition now uses Fi; the Fe condition is retained honestly as
   `chord_assisted` with hypothesis tag H4_model_g_chord, giving the study
   a clean M3-vs-M4 contrast for free.

2. **fixtures/make_synthetic_observations.py (synthgen-1.1 -> 1.2) —
   incoherent step criterion.** The per-step "on shortest route" test never
   required consecutive waypoints to be adjacent, so it (a) scored the
   non-primitive hop Ne -> Fe as on-route and (b) *penalized the direct
   condition* (a single Ne -> Ti instruction is distance 2, not one hop),
   inverting the study's own predicted ordering. Fixed: an instructed
   waypoint list is now costed as its shortest lawful completion
   (`waypoint_route_length`); excess = completion length minus direct
   distance.

3. **Coverage gaps closed (11 new acceptance checks, 107 -> 118):**
   corrected Section 24 facts (Ti-Si distance 3; both lawful three-edge
   returns); shortest Ne-Ti intermediates are {Fi, Se}; the chord-assisted
   Ne -> Fe -> Ti classification; relation-group identification by order
   profile (1, 2^11, 4^4) and center order 4 (D4 x C2); base-TIM
   independence of the relation set (torsor well-definedness); the
   Section 5 Jungian atlas frame formulas including E = l_e and
   P = 1 + l_q with the quadratic l_q d term; canonical Reinin membership
   partitions for the five externally anchored dichotomies (partition
   level only — verbal pole polarity remains unasserted per UNRESOLVED
   item 4); pilot-study/theory coherence; and the OIG Section 10.1
   foreign-profile count F_m = B_{m+1} - 2^(m-1), verified by direct
   enumeration for m = 1..5 against the realizability criterion of
   Section 9.2.

## New kernel surface (pyref/core.py, tag `derived`)

    hybrid_successors(tim, ie)
    hybrid_distance(tim, a, b)          # BFS on G_T = cube + chords
    waypoint_route_length(tim, ws, use_chords=False)

## Data regeneration

data/pilot_001 was regenerated end-to-end under the corrected design
(4 conditions x 6 trials x 6 participants = 144 trials, synthgen-1.2,
same randomization seed). All epistemic gates unchanged: predictions
locked pre-outcome, blind export theory-free, confirmatory analysis still
refuses synthetic rows.

## Erlang mirror status

Per the v2 precedent, the Python mirror is the executable proof; the
uncompiled Erlang sources still reflect v2.0. To restore 1:1 parity the
following must be mirrored on an Erlang-equipped machine: the three
hybrid/waypoint functions in le_routing, the synthgen-1.2 costing rule,
and the eleven new checks in le_verify. Until then this asymmetry is a
known limitation of v2.1.
