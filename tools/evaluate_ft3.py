"""Frozen FT3 controls and saved replayable positive closure/capacity witnesses."""
from pathlib import Path
import gzip
import hashlib
import json
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'baseline/HLE_Rebuild_R21B')]
from hle_unified.selection_records import dumps
from full_theory.retention_audit import audit_retention


def manifest():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for area in ('full_theory','tests_ft3','contracts/ft') for p in sorted((ROOT/area).rglob('*'))
        if p.is_file() and '__pycache__' not in p.parts} | {'tools/evaluate_ft3.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main(out):
    out.mkdir(parents=True,exist_ok=False);freeze=manifest()
    (out/'source_freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
    with (out/'controls.log').open('w') as log:
        tests=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/'tests_ft3')))
    witnesses=[]
    if tests.wasSuccessful():
        from tests_ft3.test_retention import trained
        for setting in ('canonical','workflow'):
            e,b,l,d,p,uses=trained(setting)
            report=audit_retention(e.world.journal(),l.events)
            with gzip.open(out/(setting+'-native.json.gz'),'wt') as f:f.write(e.checkpoint())
            (out/(setting+'-events.json')).write_text(dumps(dict(content=b.events,retention=l.events,audit=report))+'\n')
            witnesses.append(dict(setting=setting,passed=report['passed'],closures=report['closures'],certificates=report['certificates']))
    summary=dict(passed=tests.wasSuccessful() and tests.testsRun==13 and len(witnesses)==2 and manifest()==freeze,
        methods=tests.testsRun,failures=len(tests.failures),errors=len(tests.errors),witnesses=witnesses,source_unchanged=manifest()==freeze)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True);return summary


if __name__=='__main__':sys.exit(not main(Path(sys.argv[1]).resolve())['passed'])
