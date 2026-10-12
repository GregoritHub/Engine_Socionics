"""Read-only experiments on the supplied 5.2.1 package, not an engine patch.
Runtime interventions are explicitly named; supplied source is never changed.
"""
from pathlib import Path
import sys,importlib,json,gzip,hashlib,copy
from dataclasses import replace,asdict
from collections import Counter

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'kernel/clean'))
from pyref import core as C
from metabolism import develop as D,clock,chord
from metabolism.packet import packet,Packet
from metabolism.state import new_state
from metabolism import handler
from metabolism.complex import activated
from crux.typemap import type_map,perspective_cost_class
from demand import schema as DS
from holon_tower import altitude as ALT
from crux import shell as SH
T=importlib.import_module('metabolism.tick')

def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(set,frozenset)):return sorted((clean(v) for v in x),key=lambda y:json.dumps(y,sort_keys=True))
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    return x
def dump(path,x):path.write_text(json.dumps(clean(x),indent=2,sort_keys=True))
def digest(x):return hashlib.sha256(json.dumps(clean(x),sort_keys=True).encode()).hexdigest()
def pkrow(p,full=False):
    r=dict(aspect=p.aspect,facets=sorted(p.facets),tag=p.tag,source=p.source,carried=sorted(p.carried),spans=sorted(p.spans()),depth=p.depth())
    if full:r['walk']=clean(p.walk)
    return r
def state(a):
    return dict(tick=a.st.ticks,seat=a.st.seat,retained=clean(a.org['retained']),closures=a.altitude,hold=a.hold,clear=a.clear,
        crossed=a.crossed,walk=a.walk,pending=[pkrow(p) for p in a.st.pending],positions=[{k:clean(v) for k,v in asdict(q).items() if k!='walks'} for q in a.st.positions],complexes=activated(a.st,a.window))

def run(tim,partner=None,steps=40,policy='every_tick',gate=False,change=None,erase=False,no_chord=False,window=2,both_seed=False,trace=False):
    T.FIRING_POLICY=policy;clock.RELAY_GATE=gate
    original=D._tick;old_conduct=chord.conduct;old_emit=chord.emit
    if no_chord:
        chord.conduct=lambda st:st
        chord.emit=lambda st,holon_id='self':(st,None)
    interventions=[]
    if change=='engage_super_ego_after4':
        def directed(st,inbox,**kw):
            if st.tim==tim and st.ticks==4:
                kw['intention']='super_ego'
                interventions.append({'tick':5,'operation':'existing tick intention=super_ego'})
            return original(st,inbox,**kw)
        D._tick=directed
    agents={'A':D.agent(tim,window=window)}
    if partner:agents['B']=D.agent(partner,window=window)
    inbox={h:[packet(C.element_at(a.st.tim,1))] if h=='A' or both_seed else [] for h,a in agents.items()}
    rows=[];saved={};sem=[]
    try:
        for t in range(1,steps+1):
            if t==5 and change=='gate_after4':clock.RELAY_GATE=True
            if t==5 and change=='clear_pending_after4':
                a=agents['A'];interventions.append({'tick':5,'operation':'diagnostic pending removal','removed':len(a.st.pending)})
                a.st=replace(a.st,pending=())
            nxt={h:[] for h in agents}
            for h,a in agents.items():
                a,out,rep=D.step(a,inbox[h]);agents[h]=a
                row=dict(holon=h,report=clean(rep),state=state(a),out=[pkrow(p) for p in out])
                rows.append(row)
                sem.append([t,h,a.st.seat,sorted(a.org['retained']),[(p.aspect,sorted(p.facets),p.tag) for p in out],
                    [[q.index,clean(q.kept),clean(q.charge),q.unfed,q.over,q.hit] for q in a.st.positions]])
                if trace and h=='A' and t in (4,5,6):saved[str(t)]={'agent':copy.deepcopy(a),'inbox':copy.deepcopy(inbox[h]),'out':out}
                for p in out:
                    if erase:p=replace(p,carried=frozenset(),walk=frozenset())
                    for target in agents:
                        if target!=h:nxt[target].append(p)
            inbox=nxt
        a=agents['A'];comp=type_map(tim)['complementary_perspective']
        history=[dict(r,closure_class=perspective_cost_class(tim,r['closed'])) for r in a.history]
        result=dict(tim=tim,partner=partner,policy=policy,gate_initial=gate,change=change,erase_metadata=erase,no_chord=no_chord,both_seed=both_seed,window=window,
            history=history,complement_tick=next((r['tick'] for r in history if r['closed']==comp),None),final=state(a),
            post4_seats=[r['state']['seat'] for r in rows if r['holon']=='A' and r['state']['tick']>4],
            output_counts=dict(Counter(p['aspect'] for r in rows if r['holon']=='A' for p in r['out'] if p['tag']!='request')),
            semantic_hash=digest(sem),interventions=interventions)
        return result,rows,saved
    finally:
        D._tick=original;chord.conduct=old_conduct;chord.emit=old_emit
        T.FIRING_POLICY='every_tick';clock.RELAY_GATE=False

def main():
    out=ROOT/'evidence';targets=json.loads((out/'Program_Targets.json').read_text())
    dump(out/'Probe_Freeze.json',{'probe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((ROOT/'Protocol.json').read_bytes()).hexdigest()})
    witnesses=[];summary=[];mismatch=[]
    with gzip.open(out/'dual_solo_traces.jsonl.gz','wt') as raw:
        for tim,data in targets.items():
            dual=data['targets'][0]['partner']
            for partner in (dual,None):
                r,rows,_=run(tim,partner)
                witnesses.append(r)
                for row in rows:raw.write(json.dumps(clean(dict(case=[tim,partner],**row)))+'\n')
                expected=4 if partner else None
                if r['complement_tick']!=expected or (partner is None and r['history']):mismatch.append(dict(kind='witness',tim=tim,partner=partner,history=r['history']))
    dump(out/'Witness_Results.json',witnesses);print('witnesses',len(witnesses),'mismatches',len(mismatch),flush=True)
    with gzip.open(out/'pair_traces.jsonl.gz','wt') as raw:
        for tim in targets:
            for partner in targets:
                if tim==partner:continue
                r,rows,_=run(tim,partner,steps=80)
                summary.append(r)
                for row in rows:
                    raw.write(json.dumps(clean(dict(case=[tim,partner],**row)))+'\n')
                if (len(summary)%30)==0:print('pairs',len(summary),flush=True)
    for tim,data in targets.items():
        for target in data['targets']:
            r=next(x for x in summary if (x['tim'],x['partner'])==(tim,target['partner']))
            if target['what']=='complementary' and r['complement_tick']!=target['tick']:
                mismatch.append(dict(kind='supplier',tim=tim,target=target,observed=r['history']))
            if target['tick'] is None and r['complement_tick'] is not None:
                mismatch.append(dict(kind='negative_supplier',tim=tim,target=target,observed=r['history']))
            if target['what'].startswith('lateral_E') and not any(h['tick']==target['tick'] and h['closure_class']=='lateral_E' for h in r['history']):
                mismatch.append(dict(kind='lateral',tim=tim,target=target,observed=r['history']))
    dump(out/'Pair_Results.json',summary);dump(out/'Document_Mismatches.json',mismatch)
    cases={};traces={}
    for policy in ('every_tick','relay'):
        for gate in (False,True):
            name=f'{policy}_gate_{gate}';r,rows,_=run('iee','sli',steps=80,policy=policy,gate=gate)
            cases[name]=r;traces[name]=rows
    for change in ('gate_after4','clear_pending_after4','engage_super_ego_after4'):
        r,rows,_=run('iee','sli',steps=80,gate=change!='gate_after4',change=change)
        cases[change]=r;traces[change]=rows
    for name,kwargs in [('metadata_erased',{'erase':True}),('chord_ablated',{'no_chord':True})]:
        r,rows,_=run('iee','sli',steps=80,**kwargs);cases[name]=r;traces[name]=rows
    dump(out/'Gate_Chord_Results.json',cases)
    with gzip.open(out/'gate_chord_traces.json.gz','wt') as f:json.dump(clean(traces),f)
    print('document mismatches',len(mismatch),flush=True)
    for name,r in cases.items():print(name,'closure',r['complement_tick'],'seats',r['post4_seats'][:12], 'outputs',r['output_counts'],flush=True)
    print('metadata behavioral identity',cases['metadata_erased']['semantic_hash']==cases['every_tick_gate_False']['semantic_hash'],flush=True)

if __name__=='__main__':main()
