# Holonic Living Engine V1 — config surface

This wrap sits on the already-verified living_engine_v2 kernel. It does not
re-derive the cubes or the observational lattice. It does not claim that
minds have this shape. It is a configuration-driven object model: one kind
of object, nested.

## Picture

```
World  (a Holon, larger scale)
  │
  │  children hold summaries only
  │
  ├── Guard   (a Holon)
  └── Walker  (a Holon)
```

World and characters are the same kind of object. A parent never holds
another Holon's private state. It holds a short observational summary, or
it receives an event the child chose to emit.

There is no game loop, tick, network, save format, or renderer in this
kernel. Those sit outside and may read summaries. They may not write
identity.

## The three files

A game author writes data, not kernel code. Put three JSON files in one
directory and load that directory.

| File | What it is |
| --- | --- |
| `archetypes.json` | Kinds of Holon you may create (gamma, starting content, allowed events, optional seat 1–8) |
| `world.json` | The world Holon's gamma, which child kinds it may hold, and the shared event list |
| `rules.json` | Table: (archetype, intention, event) → a content change and/or a state change |

Examples live in `configs/` (and a second legal set in `configs/alt/`).
Change the files, reload, and you get a different legal world. No kernel
edit.

## What may not go in them

These keys are rejected if they appear as identity or as `pure_state`
fields:

`name`, `dialogue`, `appearance`, `audio`, `map_xy`, `player`, `romance`, `libido`

They belong to a surface layer the kernel does not read. Do not use a
player TIM. Do not treat a Holon as a type of person.

Gamma must be one of:

- `untyped`
- `structural:<name>`
- `TIM:<one of the sixteen verified TIM labels>`

A TIM is a special case of gamma, not a requirement. Seat, if present, is
an integer 1–8. Seat 6 is mobilizing.

Every event named by a rule must already appear in the world's event list
or in that archetype's `allowed_events`. Invalid files are refused before
any Holon is created.

## The eight operations

| Operation | What it does |
| --- | --- |
| `create(gamma, init_content)` | New Holon |
| `transition(H, intention, event)` | Apply a rule; refresh the observational summary. Error if no rule |
| `observe(H, quotient_spec)` | Return the summary. TIM gamma reuses the existing V / N / K / parity / R. Other gamma: empty legal envelope on the same lattice |
| `embed_child(parent, child, summary)` | Parent gains a child handle. Summary only |
| `detach_child(parent, child_id)` | Parent drops that handle |
| `emit(H, intentional_event)` | A message a parent or peer may receive |
| `pure_projection(H)` | Local identity only (`pure_state` + `content`) |
| `set_parent(H, parent_id)` | Structural link only |

All of these return a new object (or an explicit error). Gamma does not
change on an existing Holon; a different gamma is a different Holon.

`pure_projection` is a function of that Holon's own `pure_state` and
`content`. It never includes children, a parent's private data, sibling
state, names, dialogue, or map coordinates used as identity.

Domain content (D) and foreign content (F) replace independently.

## Observation, briefly

There is one 4×3 product lattice. This wrap does not invent a second one.
When gamma is a TIM, summaries come from `pyref/oig.py`. When gamma is
structural or untyped, the envelope is empty and legal (no invented
fingerprint): empty visibility, parity 0, temporal profile omitted.

CAPE phase and shells, if you store them, are opaque optional fields.
This wrap does not run a CAPE protocol.

## Check

```
python3 bin/le.py verify all      # existing v2 gate; meaning unchanged
python3 bin/le.py verify holon    # this wrap
python3 pyref/verify_holon.py     # same wrap gate, also re-runs v2
```
