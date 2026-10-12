"""The eight archetypes as position labels, and the Shell's diagnostic
appearance S_C.

Source: "Archetypal Shadow Complex -- The Crux in the Locus of Control"
(governing, primary; hashed in source_manifest).  Its sixteen tables
were parsed by bin/audit_archetypes.py; every archetype lands on ONE
Model A position across all sixteen types, so the names are position
labels (derived from the tables, not from memory):

    Saint 1   Missionary 2   Devil 3   Serpent 4
    God 5     Innocent 6     Savage 7  Prophet 8

The paper's three distinctions are three kernel bits (checked):
    Ego / Other         = a   (accepting / producing; Kepinski anabolic/catabolic)
    Syntonic / Dystonic = v   (valued / unvalued; Kepinski toward/away)
    Complex partner     = the (0,1,1) flip: same a, opposite v and r,
                          i.e. the OPP element one ring over
The four complexes therefore index (a, strong): Hero and Parent are the
strong complexes with the syntonic member conscious; Spirit and Child
are the weak complexes with the syntonic member unconscious.

The three functional relations are the kernel's element maps:
    Complementary = counterphase   Oppositional = OPP   Neutralizing = SIB

Diagnostic appearance (source_defined by the paper, citing Ekstrom
1988): each ELEMENT, in its complexity, manifests one disorder.  The
Shell at position p in TIM T therefore appears as DISORDER[element_at
(T, p)], and its projection target is the complex partner.  This is
S_C of Shell Geometry section 6.2 -- the leg V3 left as five abstract
sign names.  It does NOT close the sign -> (K, R) correspondence; it
gives S_C content.

Audit findings recorded here (see docs/SOURCE_AUDIT_V5.md):
  * quadra section headers swap Beta/Gamma on subjectivist/objectivist;
    the tables are right, the headers wrong;
  * the "Concepts of Functional Complexity" headers give Fe histrionic,
    Te paranoid, Si compulsive; the sixteen tables give Fe dissociative,
    Te schizoid, Si paranoia.  The TABLES are taken as authoritative
    (they are the per-type statement); the headers are recorded as a
    source inconsistency.
"""
from __future__ import annotations
from pyref.core import POS_COORD, COORD_POS, OPP, SIB, element_at, vadd
from crux.typemap import COUNTERPHASE

ARCHETYPE = {1: "Saint", 2: "Missionary", 3: "Devil", 4: "Serpent",
             5: "God", 6: "Innocent", 7: "Savage", 8: "Prophet"}
POSITION = {v: k for k, v in ARCHETYPE.items()}
COMPLEX = {"Hero": ("Saint", "Savage"), "Parent": ("Missionary", "Prophet"),
           "Spirit": ("God", "Devil"), "Child": ("Innocent", "Serpent")}
CREATES = {"Hero": "boundaries", "Child": "burdens", "Parent": "authority", "Spirit": "desire"}

# per element, from the sixteen tables (label, parenthetical)
DISORDER = {
    "ti": ("avoidant", "detachment"), "fe": ("dissociative", "splitting"),
    "te": ("schizoid", "solitude"), "fi": ("dependent", "vicarious"),
    "se": ("passive_aggressive", "controlling"), "ni": ("narcissism", "grandiose"),
    "si": ("paranoia", "ambivalent"), "ne": ("antisocial", "immorality"),
}
RELATION = {"complementary": COUNTERPHASE, "oppositional": OPP, "neutralizing": SIB}


def directive(p: int) -> str:
    return "Ego" if POS_COORD[p][0] == 0 else "Other"


def tonic(p: int) -> str:
    return "syntonic" if POS_COORD[p][1] == 0 else "dystonic"


def partner(p: int) -> int:
    """Complex partner: the (0,1,1) flip."""
    return COORD_POS[vadd(POS_COORD[p], (0, 1, 1))]


def complex_of(p: int) -> str:
    a = ARCHETYPE[p]
    return next(c for c, pair in COMPLEX.items() if a in pair)


def diagnostic_appearance(tim: str, p: int) -> dict:
    """S_C at position p of TIM: the archetype, the element, the disorder
    the element manifests in its complexity, and where it projects."""
    e = element_at(tim, p)
    q = partner(p)
    return {"position": p, "archetype": ARCHETYPE[p], "complex": complex_of(p),
            "element": e, "disorder": DISORDER[e][0], "mode": DISORDER[e][1],
            "directive": directive(p), "tonic": tonic(p),
            "projects_onto": {"position": q, "archetype": ARCHETYPE[q],
                              "element": element_at(tim, q),
                              "locus": "Self" if directive(p) == "Ego" else "Other"}}
