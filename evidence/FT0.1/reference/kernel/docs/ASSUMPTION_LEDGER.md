# Assumption ledger

Complete list of choices this build made where the sources allowed more
than one option, with status tags.  (Unresolvable gaps are in
UNRESOLVED_SOURCE_ITEMS.md instead.)

| # | Assumption | Status | Basis |
| --- | --- | --- | --- |
| A1 | Position coordinate names a,v,r as accepting/valued/mental with 0-pole = accepting, valued, mental | derived | UMA section 2 table reproduces 4,3,2,1,1,2,3,4 and the strong/contact/bold formulas only under this assignment (verified exhaustively) |
| A2 | IE coordinates q,e,n with Si at the origin | derived | UMA section 3; frame theorem shape f = l + a t + v S + r (S+O) verified for all 16 TIMs only in these coordinates |
| A3 | Relation composition convention rel(T1,T2) with f_T2 = f_T1 ∘ G | derived (convention) | one of two lawful conventions; fixed and documented in le_relation_group; chain rule verified |
| A4 | Position-space r-coordinate called mental/vital while OIG C.3 says conscious/automatic | source_defined (naming variance) | the two sources name the same partition differently; sets verified identical |
| A5 | Jungian coordinate polarity E,N,T,P = 1 for extroverted, intuitive, logical, irrational | derived (convention) | any consistent polarity gives the same partitions; only partitions are asserted |
| A6 | Reinin trait *names* attach to characters per UMA section 6 table | source_defined | verbal pole polarity (which pole is e.g. "positivist") not asserted |
| A7 | Estafette translation component (0,0,1) | source_defined | UMA section 10 gives R(a,v,r) = (r,v,1+a) explicitly |
| A8 | Anchored relation names limited to identity, duality, contrary, activation, super_ego, benefit(+inv), supervision(+inv) | source_defined | SPEC sections 14/76; all other elements carry unresolved ids |
| A9 | Demonstration data generator plants a routing-distance effect | experimental_instrument | property of the labeled synthetic generator only; refused by confirmatory analysis |
| A10 | Fixed-effects (within-subject) estimator for the model ladder | experimental_instrument | repeated-measures requirement of SPEC section 44 without statsmodels; documented in fit_models.py |
| A11 | OIG foreign keys treated as opaque | source_defined | OIG section 3/C.4: no semantic interpretation of foreign content |
| A12 | Support fineness vs strength orders kept distinct | source_defined | OIG section 6: visibility uses fineness; union uses strength; conflating them fails the 144-pair union check |
| A13 | Retention follows valuation (R2) | proposed_completion | metabolism/handler.py; no source fixes what unvalued functions keep |
| A14 | Mental positions process only under engaging intention; vital automatically (R3) | proposed_completion | OIG C.3 conscious/automatic; mechanism is ours |
| A15 | Strong functions generate to their own facet law on any input (R5, `generative=True`) | proposed_completion | Shell Geometry 6.1 "two strong valued functions"; switchable to pass-through |
| A16 | Return chord A6→A1 conductive iff complementary perspective retained (binary) | proposed_completion | Shell Geometry §15/§18 "increasingly available"; kernel has no continuum |
| A17 | Kępiński toward/away read as the valued bit v | proposed_completion | Archetypal Shadow Complex puts syntonic/dystonic on v (verified); Kępiński himself does not say it; see UNRESOLVED item 6 |
| A22 | Persistent overload at p (≥ window ticks) activates the complex at p | proposed_completion | Shell Geometry 6.1 persistence requirement; Archetypal "affect from activation of a complex"; window is an instrument integer |
| A18 | Firing set = gas positions; A5 fires requests only (R6) | external_secondary | Gulenko art.113 via kernel G↔A; strike with the source |
| A19 | Energy effects: brake inhibits Ego firing for the tick; launch forces Ego next tick; replenish emits a request | proposed_completion | kernel G_ENERGETIC_NOTE gives the categories; mechanisms are ours |
| A20 | `seat` is the position holding the estafette relay; advances by R each tick | derived (UMA §10 estafette, read as relay order) | orbits 1→5→6→2 / 3→7→8→4 are checked; the temporal reading rests on the name and on UMA calling ⟨relations, R⟩ the dynamical group. 5.2.1: UMA §10 (revision) warns "carrier geometry ≠ dynamics acting on the carrier", and the source's own §24 schedule is not the estafette lap; the reading is kept and carries this caution (docs/A37_RESEARCH_NET.md §5) |
| A23 | Relay drops to the unvalued orbit at 3 under Super-Ego pressure; returns to 1 when nothing pends | proposed_completion | the estafette never crosses v; some rule must; this is the minimal one consistent with the pressure rule |
| A24 | v oriented dystonic → syntonic | source_defined (Archetypal Shadow Complex, integration direction) | not from Kępiński; recorded in kepinski.ORIENTATION_SOURCE |
| A21 | Staged generation not implemented; generation is all-at-once | proposed_completion | no source gives a rate; a rate would be a quantity |
| A25 | A sustained signal at p demands the point addressed by p with any fed position of opposite rationality; a lone signal demands its block's perspective | proposed_completion | Shell Geometry §11 "persistent consequences generate demand"; the point/line algebra is derived; the pairing rule is ours |
| A26 | Overload (a Shell-relevant hit) registers only for directed input: another psyche's conscious-ring output, or the world | proposed_completion | Kępiński K3 applied to the sender; the dual's demonstrative lands on the PoLR (checked) and is automatic |
| A27 | Shell clearance for closure is judged at Role/Vulnerable | source_defined | Shell Geometry §16.1 "increasing Role/Vulnerable compensation" names the carriers |
| A28 | Retention for closure = kept content at every valued position addressing the crossed perspective for ≥ window ticks | proposed_completion | tower closure_admissible condition 1, read at metabolic resolution |
| A29 | A holon that has retained the complement and holds kept suggestive content emits no request | proposed_completion | Shell Geometry §18 "no longer only external pressure"; Archetypal "the dual is not needed in the ways the God projects" |
| A30 | Boredom = the relay walk shows the OIG maintenance signature AND no closure/candidate for ≥ BORED_WINDOW ticks AND something remains unretained | source_defined (Archetypal, Child complex: "bored with the cycle … haven't solved") | window = 64, instrument integer |
| A31 | The Serpent's demand is the whole unretained set, pure, and the Serpent is not an overload hit | source_defined (Archetypal: "paradoxes with no solution within the framework the ego has established") | the trigger is not the compensation the Shell test reads |
| A32 | The Serpent holds the relay on one unvalued lap (3→7→8→4); a candidate unclosed for BORED_WINDOW ticks lapses | proposed_completion | Shell Geometry §8: a visit is not retention |

## V5.1 additions

**A31 — pair regime as the isolation condition.** `derived from
canon`. Every author's "closed-off pair" is the engine's default
delivery (every tick, every partner). Results under it are results
about isolation and are labelled so.

**A32 — relation yield is type-invariant and contrary-symmetric.**
`derived` (verify_canon: `yield.every_relation_type_invariant`,
`symmetry.contrary_involution_exact`). Consequence: extraversion is
developmentally invisible. Stratievskaya's activation E/I asymmetry is
an observational counterexample the engine cannot express; recorded.

**A33 — distance is absent.** `unresolved` (item 10). Delivery is
total or absent per tick. Gulenko's pulsating benefit, Filatova's
dual-buffered ring, and every author's "the beneficiary must distance"
are unstatable. Proposed completion: an instrument-integer delivery
policy (every k-th tick, or gated on the receiver's `hit`), no
quantity. Expected to overturn `canon.ring_plus_duals_no_better_than_ring_OPEN`.

**A34 — demand and retention require consecutive ticks.** `exposed by
instrument` (`exposure.periodic_k2_kills_all_non_serpent_closure`).
A25's streak and the closure `hold` both reset on any gap. Intermittent
exposure produces no development -- but flipping A25, A27, A28 and the
chord gate (bin/completions.py) does not recover it, so the cause is
at the tick layer, partly the estafette's 2-cycle phase-locking of
production. Open mechanism question; not a completion artifact.

**A35 -- the yield table is completion-independent.** `derived`
(stage1.* checks; full 8-cell run in bin/completions.py). Every
pair-regime distinction survives all flips of A25/A27/A28/gate. The
table rests on the facet law, the landing permutation and the
estafette only.

**A36 -- content predictability under gating: mechanism open.**
`withdrawn conjecture`. "Exact iff unique supplier per gap" holds
8/27 (bin/suppliers.py). The structural result (floor.* checks) is
retained; its cause is not the supplier count and not simply the
withholding rate. Do not re-propose without a new variable.

## V5.2 additions

**A23 (refined) — the relay's drop to the Super-Ego is gated on the
complement.** `proposed_completion` (`clock.RELAY_GATE`, default off).
Under pressure the relay leaves the valued lap only while the
complementary perspective is not retained (Shell Geometry §18). With
the gate, the developed holon meets Super-Ego pressure from the valued
lap; without it, V5 behaviour exactly.

**A37 — firing is expenditure on the relay's expenditure turn.**
`proposed_completion` (`tick.FIRING_POLICY = "relay"`, default
"every_tick"). Decomposed in 5.2.1 (`verify_a37.py`): C2 expenditure-turn
(production only at a = 1 seats; Shell Geometry §2's one-bit movement
polarity, read onto the seat via A20), C3 engaged-block (the seat's block
produces), C4a (A6→A1 as the activating function's expenditure on seat 6's
turn; direction source_defined, UMA §19), and two boost readings C4b
(does 8 fire with the Ego at seat 2; with the chord emission at seat 6 —
the source gives A1→A8 as "receives an energy boost", a charging relation,
so both are readings); plus chord-as-turn with the `launched` override
withdrawn. Of all 8^8 seat-dependent firing rules, C2 ∧ C3 ∧ C4a leave
exactly four; FIRES_AT is (boost@2 yes, boost@6 no). Consequence
(checked): the developed holon's valued lap is 2:2 — balance 0.000 at
altitudes 2 and 3 with no altitude branch — and the 2:2 is C2 ∧ C3 with
the refined gate: neither alone produces it (0.332, 0.159), boosts and
chord-as-turn are balance-invisible (≤ 0.003). Yield-table movements are
locked as `relay.*`; kindred ≡ duality and the supervisor's closures rest
under relay on the demonstrative firing on the valued lap (A40). The
default decision is open; the source path is closed negative against the
UMA Verified Revision; the observational path is the three-dyad lock of
docs/A37_RESEARCH_NET.md §6 (activation, supervision, kindred), with
patience, window and delivery locked (A41).

**A38 — provenance walks.** `experimental_instrument`
(`Packet.walk`, `Position.walks`, `metabolism/spectrum.py`).
Order-preserving history of (holon, position, aspect) hops per packet,
capped by instrument integers WALK_CAP=16, WALKS_CAP=64; `carried`
unchanged and uncapped. Joint fraction reported as an exact Fraction.

**A39 — cognitive styles are coordinates, and dynamically invisible.**
carriers `external_secondary` (Gulenko 2002 via wikisocion); the rest
`derived` (`style.*`, `spectrum.*`). static + process = positivist in
the character group; each style is a coset of the order-4 annihilator
of span{static, process}; that subgroup is the supervision ring;
duality/benefit/contrary map style to partner style. The type-relative
emission spectrum is identical across all 16 types per altitude under
both firing policies, so style has no metabolic signature; the style
question is the process/result question (unresolved item 4), not a new
one.

## 5.2.1 additions

**A40 — the demonstrative on the valued lap carries kindred and supervision.**
`derived` (verify_a37: `kindred_productive_iff_demonstrative_fires_on_the_valued_lap`,
`supervisor_complement_first_iff_demonstrative_fires_on_the_valued_lap`). The
kindred's demonstrative carries A's activating aspect (lands on A6, chord to
A1); the supervisee's carries A's suggestive (lands on A5); the dual supplies
through its Ego. Under every_tick the demonstrative fires every tick, so all
three are channels. Under seat-timed production they are channels iff 8 fires
at seat 2 or seat 6 (reading C4b); with 8 firing only on seat 8, kindred is
sterile and the supervisor closes nothing before the Serpent, at all eight
instrument settings. The reading is a switch, not a fact.

**A41 — the supervisor discriminator is instrument-dependent, and A37 is
confounded with (patience, window) along one line.** `derived` (256-cell grid,
docs/A37_RESEARCH_NET.md §3). Completion flips (A23 gate, A25, A27, chord gate,
BORED_WINDOW) are exactly neutral; patience, window and delivery are not: the
discriminator holds at five of eight settings, collapses at (1,3,gated) and
(2,2,gated), reverses at (2,3,·). every_tick @ (1,2) and relay @ (2,3) give the
same ordinal closure sequences on all sixteen relations. Any prediction lock
must carry patience, window and delivery; patience is fixable independently
from the request rate at the suggestive (A29).
