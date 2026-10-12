"""Holon Tower — the Development pillar.

Two payload generations live here, and the distinction matters:

  tower_v2  `altitude.py` — the law in force. Altitude is COUNTED as
            completed coherent closures, and rises only when the complete
            current organization cannot meet a demand. Build payloads with
            `altitude.altitude_phase()`.

  tower_v1  `schema.py`, `tree.py` — the predecessor grid (9 vMemes x 4
            AQAL quadrants). Retained for compatibility and still fully
            validated, but it advances on internal activity with no demand
            term, never consults Shell state, and treats its tiers as
            primitive coordinates. The governing source forbids all three.
            Do not build new work on it.

`schema.validate_any()` accepts either generation and dispatches on the
payload's own `version` field.
"""

from . import altitude, schema, seal, tree

__all__ = ["altitude", "schema", "seal", "tree"]
