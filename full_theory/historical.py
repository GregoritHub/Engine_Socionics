"""Versioned adapter for the immutable, verified 5.2.1 reference.

Historical facets are not native paid objects or capability certificates.
The lock scopes the reference's two global policy switches to one transition.
Checkpoints carry all state and must exactly match deterministic replay.
"""
from collections import Counter
from dataclasses import asdict, fields, is_dataclass, replace
from pathlib import Path
import hashlib
import importlib
import json
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "evidence/FT0.1/reference"
LOCK = threading.RLock()


def verify_reference():
    manifest = json.loads((REFERENCE / "Immutable_Manifest.json").read_text())
    bad = [name for name, digest in manifest.items()
           if not (REFERENCE / name).is_file()
           or hashlib.sha256((REFERENCE / name).read_bytes()).hexdigest() != digest]
    if bad:
        raise ValueError("historical reference mismatch: " + repr(bad))
    return len(manifest)


verify_reference()
sys.path.insert(0, str(REFERENCE / "kernel"))
from pyref import core as C
from metabolism import develop as D, clock, chord
from metabolism.packet import packet, Packet
from metabolism.state import State, Position
from metabolism.complex import activated
from crux.typemap import type_map, perspective_cost_class
T = importlib.import_module("metabolism.tick")
for module in (C, D, clock, chord, T):
    if not Path(module.__file__).resolve().is_relative_to(REFERENCE / "kernel"):
        raise ValueError("unverified historical module already loaded")


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted((clean(v) for v in value), key=lambda x: json.dumps(x, sort_keys=True))
    if isinstance(value, (tuple, list)):
        return [clean(v) for v in value]
    return value


def digest(value):
    return hashlib.sha256(json.dumps(clean(value), sort_keys=True).encode()).hexdigest()


def exact(value):
    """JSON representation preserves collections, key types and every field."""
    if is_dataclass(value):
        return {"record": type(value).__name__, "fields":
                {f.name: exact(getattr(value, f.name)) for f in fields(value)}}
    if isinstance(value, dict):
        return {"dict": sorted([[exact(k), exact(v)] for k, v in value.items()],
                               key=lambda row: json.dumps(row[0], sort_keys=True))}
    if isinstance(value, (tuple, list, set, frozenset)):
        rows = [exact(v) for v in value]
        if isinstance(value, (set, frozenset)):
            rows.sort(key=lambda row: json.dumps(row, sort_keys=True))
        return {type(value).__name__: rows}
    if value is None or type(value) in (str, int, bool):
        return value
    raise ValueError("non-exact historical checkpoint value")


def packet_row(p):
    return dict(aspect=p.aspect, facets=sorted(p.facets), tag=p.tag, source=p.source,
                carried=sorted(p.carried), spans=sorted(p.spans()), depth=p.depth())


def state_row(a):
    return dict(tick=a.st.ticks, seat=a.st.seat, retained=clean(a.org["retained"]),
                closures=a.altitude, hold=a.hold, clear=a.clear, crossed=a.crossed,
                walk=a.walk, pending=[packet_row(p) for p in a.st.pending],
                positions=[{k: clean(v) for k, v in asdict(q).items() if k != "walks"}
                           for q in a.st.positions], complexes=activated(a.st, a.window))


class HistoricalController:
    VERSION = "historical-521-v1"

    def __init__(self, tim="iee", partner=None, *, firing="every_tick", gate=False,
                 both_seed=False, window=2, erase_metadata=False, no_chord=False):
        if tim not in C.TIMS or partner is not None and partner not in C.TIMS:
            raise ValueError("known TIMs required")
        if firing not in ("every_tick", "relay") or any(type(x) is not bool
                for x in (gate, both_seed, erase_metadata, no_chord)):
            raise ValueError("explicit reference policy required")
        if type(window) is not int or not 1 <= window <= 64:
            raise ValueError("bounded integer window required")
        self.config = dict(tim=tim, partner=partner, firing=firing, gate=gate,
                           both_seed=both_seed, window=window,
                           erase_metadata=erase_metadata, no_chord=no_chord)
        self.agents = {"A": D.agent(tim, window=window)}
        if partner:
            self.agents["B"] = D.agent(partner, window=window)
        self.inbox = {h: [packet(C.element_at(a.st.tim, 1))]
                      if h == "A" or both_seed else [] for h, a in self.agents.items()}
        self.rows = []
        self.semantic = []
        self.turn = 0

    def step(self):
        with LOCK:
            old = T.FIRING_POLICY, clock.RELAY_GATE, chord.conduct, chord.emit
            try:
                T.FIRING_POLICY = self.config["firing"]
                clock.RELAY_GATE = self.config["gate"]
                if self.config["no_chord"]:
                    chord.conduct = lambda st: st
                    chord.emit = lambda st, holon_id="self": (st, None)
                self.turn += 1
                nxt = {h: [] for h in self.agents}
                emitted = []
                for h, a in self.agents.items():
                    a, out, report = D.step(a, self.inbox[h])
                    self.agents[h] = a
                    row = dict(holon=h, report=clean(report), state=state_row(a),
                               out=[packet_row(p) for p in out])
                    self.rows.append(row)
                    emitted.append(row)
                    self.semantic.append([self.turn, h, a.st.seat, sorted(a.org["retained"]),
                        [(p.aspect, sorted(p.facets), p.tag) for p in out],
                        [[q.index, clean(q.kept), clean(q.charge), q.unfed, q.over, q.hit]
                         for q in a.st.positions]])
                    for p in out:
                        if self.config["erase_metadata"]:
                            p = replace(p, carried=frozenset(), walk=frozenset())
                        for target in self.agents:
                            if target != h:
                                nxt[target].append(p)
                self.inbox = nxt
                return clean(emitted)
            finally:
                T.FIRING_POLICY, clock.RELAY_GATE, chord.conduct, chord.emit = old

    def run(self, turns):
        if type(turns) is not int or not 0 <= turns <= 10000:
            raise ValueError("bounded integer turns required")
        for _ in range(turns):
            self.step()
        return self.summary()

    def summary(self):
        a = self.agents["A"]
        tim = self.config["tim"]
        history = [dict(row, closure_class=perspective_cost_class(tim, row["closed"]))
                   for row in a.history]
        comp = type_map(tim)["complementary_perspective"]
        return clean(dict(tim=tim, partner=self.config["partner"],
            policy=self.config["firing"], gate_initial=self.config["gate"], change=None,
            erase_metadata=self.config["erase_metadata"], no_chord=self.config["no_chord"],
            both_seed=self.config["both_seed"], window=self.config["window"], history=history,
            complement_tick=next((r["tick"] for r in history if r["closed"] == comp), None),
            final=state_row(a), post4_seats=[r["state"]["seat"] for r in self.rows
                if r["holon"] == "A" and r["state"]["tick"] > 4],
            output_counts=dict(Counter(p["aspect"] for r in self.rows if r["holon"] == "A"
                for p in r["out"] if p["tag"] != "request")),
            semantic_hash=digest(self.semantic), interventions=[]))

    def checkpoint(self):
        payload = dict(version=self.VERSION, config=self.config, turn=self.turn,
            state=exact(self.agents), inbox=exact(self.inbox), rows=clean(self.rows),
            semantic=clean(self.semantic))
        return json.dumps(dict(payload=payload, sha256=digest(payload)), sort_keys=True,
                          separators=(",", ":"), allow_nan=False)

    @classmethod
    def restore(cls, text):
        def unique(pairs):
            out = {}
            for k, v in pairs:
                if k in out:
                    raise ValueError("duplicate checkpoint key")
                out[k] = v
            return out
        envelope = json.loads(text, object_pairs_hook=unique)
        p = envelope["payload"]
        if envelope["sha256"] != digest(p) or p["version"] != cls.VERSION:
            raise ValueError("historical checkpoint identity mismatch")
        result = cls(**p["config"])
        result.run(p["turn"])
        if json.loads(result.checkpoint()) != envelope:
            raise ValueError("historical checkpoint differs from exact replay")
        return result
