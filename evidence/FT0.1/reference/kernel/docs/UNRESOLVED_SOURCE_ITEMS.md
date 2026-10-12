# Unresolved source-extraction items

Items the supplied sources do not decide.  Per SPEC section 76 these are
carried explicitly and NEVER silently completed from general typology
knowledge.  Machine-readable copy: UNRESOLVED_SOURCE_ITEMS.json.

1. **Model G role names for G3, G5, G8.**  UMA section 19 names roles for
   G1 (Leader), G2 (Creative), G4 (Launching), G6 (Manipulative),
   G7 (Braking) and describes G3 only as depending on external support.
   Code returns {unresolved_source_extraction, ...} for G3/G5/G8.
2. **Model G block assignment.**  UMA section 13 names the four blocks
   (Social Mission, Social Adaptation, Creative Self-Realization,
   Inflation) but does not state which G-positions form which block.
   le_model_g:block_assignment/0 -> unresolved_source_extraction.
3. ~~**Names of the 7 unanchored relation-group elements.**~~  **RESOLVED**
   by *Generative Semantics of Information Metabolism v1.1*, Appendix D,
   which supplies all sixteen intertype permutations by name.

   Verified rather than adopted.  Each of the sixteen permutations induces
   a constant permutation across all sixteen TIMs and bijects with
   `relation_group_elements()`; the nine names the kernel had already
   anchored independently all agree.  The seven now named:

       Mirror          (2,1,4,3,6,5,8,7)      Kindred       (1,4,3,2,5,8,7,6)
       Conflict        (4,3,2,1,8,7,6,5)      Semi-duality  (5,8,7,6,1,4,3,2)
       Quasi-identity  (8,7,6,5,4,3,2,1)      Business      (3,2,1,4,7,6,5,8)
       Mirage          (7,6,5,8,3,2,1,4)

   Convention: `perm[i]` is the position in B of the element occupying
   position i in A.

   **Direction of benefit and supervision — provenance note.**  *A Finite
   Object* s.4.2 proves the arrow direction on the four order-4 cycles is
   not recoverable from the arithmetic, and those four cycles are exactly
   the four rows Appendix D self-contradicts on.  The direction the code
   uses rests on `v11_supervisee` / `v11_beneficiary` (V11 `le_itr`
   structural derivation), NOT on Appendix D.  Appendix D's table must not
   be cited as the source for it.

   **Caution when applying.**  Appendix D's *Ego-transfer* column is
   swapped within each directional pair (see SOURCE_AUDIT_V3).  Use the
   permutation tuples, which are correct.  All seven names resolved above
   are self-inverse, so the defect does not touch this resolution.
4. **Verbal pole polarity** for Reinin trait names and the IE semantic
   dichotomies.  **PARTIALLY CLOSED: 6 of 15.**  The partitions were
   always known; what was missing was which pole carries which word.
   Five are now fixed by the supplied sources, with provenance:

   | Dichotomy | Assignment | Source |
   | --- | --- | --- |
   | extraverted/introverted | character 1 = extraverted | Atlas type names, all 16 spelled out (`...Extratim` / `...Introtim`) |
   | intuitive/sensing | character 1 = intuitive | Atlas type names (`Intuitive` / `Sensory`) |
   | logical/ethical | character 1 = logical | Atlas type names (`Logical` / `Ethical`) |
   | static/dynamic | character 0 = static | Generative Semantics s.6 static element set + Part IX per-type ring label (the two agree) |
   | democratic/aristocratic | character 0 = democratic | A Finite Object s.3.1 turn vectors named + s.5 per-TIM turn column; **independently confirmed** by UMA Appendix A ("the orientation bit takes the value 1 exactly on the Democratic types") |
   | irrational/rational | character 1 = irrational | UMA s.5 `P = 1 XOR l_q` + element-level rationality from Shell Geometry s.5 / Generative Semantics s.5 |
   | irrational/rational | character 1 = irrational | Needed Information Package v1.0 s.1.1: type pole follows the leading element's rationality (GenSem Part II + `living_engine_ref.temperament`) |

   The first three are a **provenance upgrade rather than a value change**:
   `jungian_coord` already used E=1 extro, N=1 intuitive, T=1 logical, but
   registered it as a documented *convention*.  The Atlas spells all
   sixteen type names out, so those three are now `source_defined`.
   `frame_orientation`'s note that the Democratic/Aristocratic verbal
   polarity is "not asserted by the source" is superseded by A Finite
   Object s.3.1.

   **Still open, 9 of 15**: carefree/farsighted, yielding/obstinate,
   tactical/strategic, constructivist/emotivist, positivist/negativist,
   judicious/decisive, subjectivist/objectivist, process/result,
   asking/declaring.

   Classical public tables for those nine exist externally.  They are NOT
   adopted here: the Needed Information Package is explicit that external
   classical sources "are not project residual closure", and this file
   carries only what the project's own locked sources fix.

   irrational/rational was the near miss and is now closed.  Shell Geometry
   s.5 and Generative Semantics s.5 fix rationality at the ELEMENT level
   (irrational Ne, Se, Ni, Si; rational Fe, Te, Fi, Ti); the missing piece
   was the TYPE-level rule.  It was supplied:

       A type's rational/irrational pole is determined by the rationality
       of its leading element -- judgment function (Fe, Te, Fi, Ti) means
       rational, perception function (Ne, Se, Ni, Si) means irrational.

   Verified: the rule partitions the socion 8/8, lands exactly on Reinin
   character (0,0,0,1), and agrees with the P coordinate `jungian_coord`
   already computed.  Like the three Atlas-name assignments, the value does
   not change -- its status rises from documented convention to sourced.

   Note also that the polarity table cannot live in `pyref/`, which is
   sealed.  It belongs in a non-frozen layer.
5. **Exact-meet theorem witness (OIG 7.3)**: the source flags its own
   canonical witness as not exhibited (OIG D.7); carried at that status.

6. ~~**Kępiński's toward/away as a position coordinate.**~~ **CLOSED** by
   the Archetypal Shadow Complex: ego-syntonic/dystonic is the valued bit
   on every table (bin/audit_archetypes.py).  Kępiński's own wording is
   not thereby decided, but the position reading has an independent
   governing source.  (Original text retained below.)
   **Kępiński's toward/away as a position coordinate.**  V5 reads it as
   the valued bit `v` (algebra/kepinski.py, STATUS["v"]).  Kępiński may
   intend an orientation toward a *stimulus*, which would make it a
   packet property rather than a position character.  Undecided from
   the supplied texts.  If packet-level, move it to `Packet` beside
   facets; nothing else changes.
7. ~~**The `v` axis has no ordering.**~~ **CLOSED**: oriented dystonic →
   syntonic by the integration direction of the Archetypal Shadow
   Complex (A24), and shown not to be an oscillation axis at all -- the
   estafette never crosses it (clock.py).  Which cycle: the estafette's.
   (Original text retained below.)
   **The `v` axis has no ordering.**  Kępiński orients `a` and `r`; no
   source orients `v`.  This is the one open coordinate for any energy
   flow law.  Together with the chord being a return edge on each axis
   (algebra/kepinski.py chord_report), a flow law must be a cycle; which
   cycle is not decided.
8. **Erlang mirror for `algebra/` and `metabolism/`.**  The v1.1
   precedent is Erlang deliverable + Python proof.  V4/V5 shipped Python
   only.  Until mirrored, treat the two packages as reference
   implementations, not as the deliverable.
9. **Sign → (K, R) for the four activation signs.**  Shell Geometry §7
   states two OIG signatures — maintenance (K ≠ ∅, N = ∅) and
   foreclosure (pure A under demand) — and metabolism/observe.py
   implements exactly those two.  Premature translation, forced
   placement, new defensive structure and residual fragmentation have no
   stated signature; none is asserted.
10. **Shell clearance under continuous demand.**  §16.2 requires "same
    or greater demand + less persistent distortion".  With dimensionality
    fixed by Model A, directed input above a function's law overloads it
    on every tick it arrives, so clearance at Role/Vulnerable is only
    observed when pressure pauses.  Either retention must change how
    Role/Vulnerable register pressure on the retained perspective (a
    reading of "compensation"), or clearance must be judged elsewhere.
    The sources do not decide; the dual-first stall reproduces it.

10. **Distance / exposure as a delivery variable.**  Not in the
    governing documents; universal in the secondary canon (see
    `docs/CANON_AUDIT_V5_1.md`).  The engine has no term for partial
    or intermittent contact, and three of the four dynamical
    disagreements with canon reduce to it (A33).  Completed as an
    instrument (`bin/exposure.py`, gated and periodic policies).  Gating
    does not rescue the audited holon or benefit; periodic exposure
    kills all closure (A34).  Still unresolved as a *source* item.

11. **Timing of production.**  No governing document binds production to a
    position in time.  UMA §13 gives σ = 1⊕a as the static accepting/producing
    polarity; §17 gives one current functional state x_t; §20 makes its dynamics
    an empirical kernel K_T with no numbers; §28 lists the dynamical laws as
    unspecified; §10 warns that carrier geometry ≠ dynamics.  Shell Geometry §2
    gives a formal movement one polarity bit (supports C2 at movement resolution).
    FIRING_POLICY, the C2/C3 readings and the boost binaries (C4b) are therefore
    completions in a source-silent region (docs/A37_RESEARCH_NET.md §5).
    Source read: UMA Verified Revision (sha256 41ebe1b1…), not the pinned edition.
