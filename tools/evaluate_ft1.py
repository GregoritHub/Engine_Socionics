"""Prospectively frozen historical parity and exact restart panel."""
from pathlib import Path
import gzip
import hashlib
import itertools
import json
import sys
import unittest
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "baseline/HLE_Rebuild_R21B")]
from full_theory.historical import HistoricalController as H, REFERENCE, C, clock, clean, digest, LOCK
from metabolism.state import new_state
from metabolism.packet import packet
from hle import model_a as m
from hle_unified.axes import AXES, axis_cells


def freeze():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for area in ("full_theory", "tests_ft1", "contracts/ft")
            for p in sorted((ROOT / area).rglob("*")) if p.is_file() and "__pycache__" not in p.parts} | {
                "tools/evaluate_ft1.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main(out):
    out.mkdir(parents=True, exist_ok=False)
    initial = freeze()
    (out / "source_freeze.json").write_text(json.dumps(initial, indent=2) + "\n")
    checks = []
    failures = []
    def check(case, got, expected):
        ok = got == expected
        checks.append(dict(case=case, passed=ok, observed_sha256=digest(got), expected_sha256=digest(expected)))
        if not ok:
            failures.append(dict(case=case, observed=clean(got), expected=clean(expected)))
        return ok
    saved = REFERENCE / "study_evidence"
    control = json.loads((saved / "Control_Results.json").read_text())
    cases = []
    for family, file, turns in (("dual_solo", "Witness_Results.json", 40),
                                ("nonidentity", "Pair_Results.json", 80)):
        for index, expected in enumerate(json.loads((saved / file).read_text())):
            cases.append((f"{family}:{index:03}", dict(tim=expected["tim"], partner=expected["partner"]),
                          turns, expected, "full"))
    for index, expected in enumerate(control["both_seed_followup"]):
        cases.append((f"both_seed:{index:02}", dict(tim=expected["tim"],
            partner=expected["target"]["partner"], both_seed=True), 80, expected["observed"], "history"))
    for index, expected in enumerate(control["dual_factorial"]):
        cases.append((f"factorial:{index:02}", dict(tim=expected["tim"], partner=C.dual_candidate(expected["tim"]),
            firing=expected["policy"], gate=expected["gate"]), 40, expected, "factorial"))
    with gzip.open(out / "observable_traces.jsonl.gz", "wt") as raw:
        for name, config, turns, expected, kind in cases:
            model = H(**config)
            observed = model.run(turns)
            for row in model.rows:
                raw.write(json.dumps(clean(dict(case=name, **row)), sort_keys=True) + "\n")
            if kind == "full":
                actual = observed
            elif kind == "history":
                actual = observed["history"]
            else:
                actual = dict(tim=config["tim"], policy=config["firing"], gate=config["gate"],
                    history=observed["history"], post4_seats=observed["post4_seats"],
                    pending_final=len(observed["final"]["pending"]))
            check(name, actual, expected)
            if kind == "factorial":
                for split in (3, 17):
                    part = H(**config); part.run(split)
                    restored = H.restore(part.checkpoint()); restored.run(turns-split)
                    check(f"{name}:restart:{split}", restored.checkpoint(), model.checkpoint())
            if len(checks) % 30 == 0:
                print("checks", len(checks), "failures", len(failures), flush=True)
    for firing, split in itertools.product(("every_tick", "relay"), (1, 3, 4, 5, 17)):
        model = H("iee", "sli", firing=firing, gate=True); model.run(40)
        part = H("iee", "sli", firing=firing, gate=True); part.run(split)
        restored = H.restore(part.checkpoint()); restored.run(40-split)
        check(f"special_restart:{firing}:{split}", restored.checkpoint(), model.checkpoint())
    def trans(p, v):
        return C.COORD_POS[tuple(a ^ b for a, b in zip(C.POS_COORD[p], v))]
    n = lambda p: trans(p, (0, 1, 0))
    cp = lambda p: trans(p, (0, 0, 1))
    inv = {clock.advance(p): p for p in range(1, 9)}
    cells = {(1,1): "D", (0,1): "C", (1,0): "N", (0,0): "H"}
    for tim in C.TIMS:
        for p in range(1, 9):
            el = C.element_at(tim, p)
            got = (el == m.element_at(tim, p), set(C.routing_neighbors(tim, el)) == set(m.neighbors(tim, el)),
                {m.position_of(tim, e) for e in C.routing_neighbors(tim, el)} == {trans(p,(1,0,0)), n(p), cp(p)},
                clock.advance(n(p)) == n(clock.advance(p)), cp(clock.advance(cp(p))) == inv[p],
                C.dcnh_cell(el) == C.dcnh_cell(C.element_at(tim, n(p))))
            check(f"structure:{tim}:{p}", got, (True,) * 6)
        for pair, label in zip(AXES, axis_cells(tim)):
            check(f"core_pair:{tim}:{pair[0]}", {cells[C.dcnh_cell(C.element_at(tim,p))] for p in pair}, {label})
    with LOCK:
        old = clock.RELAY_GATE
        try:
            truth = []
            for seat, gate, retained, pending in itertools.product(range(1,9), (False,True), (False,True), (False,True)):
                clock.RELAY_GATE = gate
                st = replace(new_state("iee"), seat=seat, pending=(packet("ti"),) if pending else (),
                             retained=frozenset({"I","IT"} if retained else {"I"}))
                truth.append([seat, gate, retained, pending, clock.step(st).seat])
            check("gate_truth_table:64", truth, control["gate_truth_table"])
        finally:
            clock.RELAY_GATE = old
    with (out / "unit_tests.log").open("w") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/"tests_ft1")))
    check("unit_tests", (result.testsRun, len(result.failures), len(result.errors)), (5, 0, 0))
    check("source_unchanged", freeze(), initial)
    (out / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    (out / "failures.json").write_text(json.dumps(failures, indent=2) + "\n")
    summary = dict(passed=not failures, historical_runs=len(cases), checkpoint_splits=138,
        type_seat_cells=128, core_pairs=64, gate_states=64, checks=len(checks), failed=len(failures),
        reference_version=H.VERSION, source_unchanged=freeze()==initial)
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary), flush=True)
    return summary


if __name__ == "__main__":
    sys.exit(not main(Path(sys.argv[1]).resolve())["passed"])
