"""FT2 frozen all-cell paid adapter panel and independently audited witnesses."""
from pathlib import Path
import concurrent.futures
import gzip
import hashlib
import json
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'baseline/HLE_Rebuild_R21B')]
from hle_unified.selection_records import NAMES,FACES,dumps
from full_theory.content import ContentBridge
from full_theory.content_audit import audit_content


def cell(out,setting,number):
    name=NAMES[number//2];face=FACES[number%2]
    if setting=='canonical':
        from tests_c5 import fixtures as f
        e=f.setup(generate=False,actual='serviceable' if name=='Act' and face=='expenditure' else 'damaged')
        r=f.prepare(e,name,face,key='case');b=ContentBridge(e);row=b.execute(r,consumed=r.inputs)
        later=f.downstream(e,r,name,face)
    else:
        from tests_c7_workflow import fixtures as f
        e=f.setup_workflow();prepared=f.cell(e,name,face,key='case',prepare_only=True)
        r=prepared['request'];b=ContentBridge(e);row=b.execute(r,consumed=r.inputs)
        later=f.consume_result(e,dict(prepared,result=row['output']))['consequence']
    if row['status']!='succeeded':raise AssertionError((setting,name,face,row))
    audit=audit_content(e.world.journal(),b.events)
    identity=b.completed(r.actor,r.key)
    report=dict(setting=setting,cell=number,name=name,polarity=face,passed=True,
        native=identity,later=later,events=b.events,audit=audit)
    destination=out/f'{setting}-{number:02}'
    destination.mkdir(parents=True,exist_ok=False)
    with gzip.open(destination/'native_checkpoint.json.gz','wt') as f:f.write(e.checkpoint())
    (destination/'result.json').write_text(dumps(report)+'\n')
    print(setting,number,'passed',flush=True)


def manifest():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for area in ('full_theory','tests_ft2','contracts/ft') for p in sorted((ROOT/area).rglob('*'))
        if p.is_file() and '__pycache__' not in p.parts} | {'tools/evaluate_ft2.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main(out):
    out.mkdir(parents=True,exist_ok=False);freeze=manifest()
    (out/'source_freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
    def run(setting,number):
        with (out/f'{setting}-{number:02}.log').open('w') as log:
            result=subprocess.run([sys.executable,str(Path(__file__).resolve()),str(out),'--cell',setting,str(number)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        return dict(setting=setting,cell=number,exit_code=result.returncode)
    rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        tasks=[pool.submit(run,s,n) for s in ('canonical','workflow') for n in range(32)]
        for task in concurrent.futures.as_completed(tasks):
            rows.append(task.result());(out/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
    with (out/'controls.log').open('w') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/'tests_ft2')))
    summary=dict(passed=len(rows)==64 and all(r['exit_code']==0 for r in rows) and result.wasSuccessful() and result.testsRun==12 and manifest()==freeze,
        required_cells=64,executed_cells=len(rows),passed_cells=sum(r['exit_code']==0 for r in rows),
        control_methods=result.testsRun,control_failures=len(result.failures),control_errors=len(result.errors),source_unchanged=manifest()==freeze)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
    return summary


if __name__=='__main__':
    if len(sys.argv)>2 and sys.argv[2]=='--cell':cell(Path(sys.argv[1]),sys.argv[3],int(sys.argv[4]))
    else:sys.exit(not main(Path(sys.argv[1]).resolve())['passed'])
