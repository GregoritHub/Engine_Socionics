"""Raw-event closure reconstruction, independent of controller and selectors."""
from hle import model_a
from hle_unified.material import attrs
from hle_unified.development_values import attrs as unpack
from hle_unified.records import Account


def audit_retention(transactions,events):
    txs=tuple(transactions);versions={v.ref:v for tx in txs for v in tx.versions}
    heads={v.ref.identity:v for tx in txs for v in tx.versions}
    windows={};seen=set();history={};certificates={};revoked={}
    def require(good,reason):
        if not good:raise ValueError('FT retention audit: '+reason)
    def paid(ref,actor):
        require(ref in versions,'missing work')
        d=attrs(heads[ref.identity])
        require(d.get('actor')==actor and d.get('status','succeeded')=='succeeded'
            and d.get('required',0)>0 and d.get('completed')==d.get('required')
            and d.get('spent',0)>=d['required'],'unpaid or foreign work')
        return d
    def perspective(tim,pair):
        families={model_a.element_at(tim,p)[0] for p in pair}
        return {frozenset('nf'):'I',frozenset('st'):'IT',frozenset('sf'):'WE',frozenset('nt'):'ITS'}[frozenset(families)]
    def content_referent(d):
        # Reconstruct from native committed work and its typed output. No
        # runtime adapter or evaluator-supplied demand determines this scope.
        target=d['content_target'] if 'content_target' in d else d.get('target')
        if d.get('binding') is not None:
            value=versions.get(d['binding']);account=None if value is None else value.facet(Account)
            require(account is not None and account.holder==d['actor'] and account.referent==target
                and bool(account.content) and all((p.subject,p.context)==(target,d['context'])
                                                 for p in account.content),'inconsistent typed content scope')
        return target
    for row in events:
        kind=row['kind']
        if kind=='exposure':
            actor=row['actor'];dem=row['demand'];kept=row['kept']
            token=(row['consumer'],row['shell'].get('operation'))
            require(token not in seen,'duplicate exposure');seen.add(token)
            scope=(actor,dem['family'],dem['context'],dem['cue'])
            at={v.ref.identity:v for tx in txs[:row['at_tick']] for v in tx.versions}
            owned=bool(kept)
            for ref in kept:
                value=versions.get(ref);account=None if value is None else value.facet(Account)
                own_receipt=any(attrs(v).get('actor')==actor and attrs(v).get('operation')=='bind'
                    and ref in [x for k,x in attrs(v).items() if k.startswith('input.')]
                    and attrs(v).get('completed')==attrs(v).get('required') for v in at.values())
                owned=owned and account is not None and own_receipt and at.get(ref.identity)==value
            require(row['actual_content']==bool(owned),'false kept-content claim')
            consumer=paid(row['consumer'],actor) if row['consumer'] else {}
            use=(consumer.get('context'),content_referent(consumer))==(dem['context'],dem['target']) and any(
                v in kept for k,v in consumer.items() if k.startswith('input.'))
            require(row['paid_use']==bool(use),'false downstream use')
            returned=bool(row['returns']);last=None;previous=None;tim=consumer.get('tim')
            for ref in row['returns']:
                d=paid(ref,actor);tim=d['tim']
                if last is None:last=perspective(tim,(5,6))
                if d['origin']!=last or previous is not None and previous not in [v for k,v in d.items() if k.startswith('input.')]:returned=False
                last=d['destination'];previous=d.get('binding') or d.get('result')
            returned=returned and last==perspective(tim,(1,2))
            require(row['returned']==bool(returned),'false return path')
            sh=row['shell'];clear=False;evaluated=False
            if sh.get('encounter'):
                job=paid(sh['operation'],actor);s=attrs(versions[sh['encounter']])
                require(job.get('encounter')==sh['encounter'],'wrong Shell encounter')
                fields=('trigger','available','safe','requires_partner','willing','approval_required','approved','feedback','recommended')
                evaluated=all('known.'+k in s for k in fields) and (s.get('target'),s.get('context'),s.get('cue'))==(dem['target'],dem['context'],dem['cue']) and s.get('demand') is True and not s.get('truncated')
                clear=evaluated and s.get('reason')=='available_demand' and s.get('route')==s.get('base_route') and not any(s.get(k) for k in ('approval','obligation','excluded','forecast_risk','salience'))
            require((sh['evaluated'],sh['clear'])==(bool(evaluated),bool(clear)),'false or vacuous clearance')
            good=owned and returned and use and clear and not row['interrupted']
            signature=(kept,dem);prior=windows.get(scope)
            hold=prior[1]+1 if good and prior and prior[0]==signature else 1 if good else 0
            require(row['hold']==hold and row['closed']==bool(good and hold>=2),'false continuity or closure')
            windows[scope]=(signature,hold)
            if tim:
                history.setdefault(actor,{perspective(tim,(1,2))})
                if row['closed']:history[actor].add(perspective(tim,(5,6)))
        elif kind=='certificate':
            require(row['key'] not in certificates,'duplicate certificate')
            actor=row['actor'];cap=unpack(versions[row['native_capacity']]);paid(cap['operation'],actor)
            require(row['binding']==cap['binding'] and row['examples']==cap['examples'],'invented native capacity')
            examples=[unpack(versions[r]) for r in cap['examples']]
            require(len(examples)>=2 and all(x['independent'] and not x['supported'] for x in examples),'borrowed practice')
            require(len({x['event'] for x in examples})==len(examples) and len({t.identity for x in examples for t in x['targets']})>=2,'duplicate training')
            maximum=sorted((len(x['targets']) for x in examples),reverse=True)[1]
            require(cap['max_load']==maximum and row['scope']['load']<=maximum,'unearned load capacity')
            require(len(set(row['content_uses']))==len(examples),'duplicate or absent content use')
            for x,ref in zip(examples,row['content_uses']):
                d=paid(ref,actor);practice=paid(x['operation'],actor);response=unpack(versions[x['response']]);r=paid(response['operation'],actor)
                require(content_referent(d) in x['targets'] and d.get('context')==cap['context'] and d.get('route_count',0)>0,'unrelated content use')
                require(r['finished_tick']<=d['started_tick']<=d['finished_tick']<=practice['finished_tick'],'unrelated practice chronology')
            require(row['closure'] in events and row['closure']['closed'],'certificate without closure')
            require(row['material_competence'] is False and row['claim']=='guarded_content_participation','inflated competence claim')
            certificates[row['key']]=row
        elif kind=='certificate_revoked':
            require(row['key'] in certificates and bool(row['reason']),'invalid revocation')
            revoked[row['key']]=row['reason']
        else:require(False,'unknown retention event')
    return dict(passed=True,exposures=sum(r['kind']=='exposure' for r in events),
        closures=sum(r['kind']=='exposure' and r['closed'] for r in events),
        certificates=len(certificates),revocations=len(revoked),
        history=tuple((a,tuple(sorted(v))) for a,v in history.items()))
