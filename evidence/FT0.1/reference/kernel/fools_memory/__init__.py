"""Fool's Memory Path — the Memory pillar.

Particular memories, not summaries. The register stores loops keyed by
holon id; reads hand back deep copies so a caller cannot reach in and
rewrite a loop's vertices, strength or residue without passing back
through `validate_loop`.

  schema.py    the loop record and its invariants
  store.py     MemoryRegister — put / loops / forget / mark_replayed
  encode.py    turn a holon trajectory into a storable loop
  retrieve.py  band selection and recall
"""

from . import encode, retrieve, schema, store

__all__ = ["encode", "retrieve", "schema", "store"]
