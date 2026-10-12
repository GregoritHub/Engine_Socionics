"""Demand-scoped closure and capability, distinct from content and TIM.

The capability bridge is explicitly guarded participation. It reuses native
paid practice, correction, recall and load limits; it grants no material skill.
"""
from dataclasses import dataclass, asdict
from hle_unified.records import ObjectRef
from hle_unified.material import attrs
from hle_unified.development_values import attrs as development_attrs
from hle_unified.shell_policy import FIELDS
from .content import FACETS, fingerprint, semantic_scope
from .historical import type_map


@dataclass(frozen=True)
class Demand:
    family: str
    context: ObjectRef
    cue: ObjectRef
    target: ObjectRef
    requirements: tuple = ("experience",)
    obligations: tuple = ("participate",)
    alternatives: tuple = ("I","IT","WE","ITS")
    load: int = 1
    deadline: int = 1000
    support_allowed: tuple = ()

    def __post_init__(self):
        if self.family not in ("canonical","workflow") or any(type(x) is not ObjectRef for x in (self.context,self.cue,self.target)):
            raise ValueError("supported content family and exact owned scope required")
        for values in (self.requirements,self.obligations,self.alternatives,self.support_allowed):
            if type(values) is not tuple or len(set(values)) != len(values):
                raise ValueError("distinct exact requirement sets required")
        if not self.requirements or not set(self.requirements)<=set(FACETS) or not self.obligations:
            raise ValueError("conjunctive facets and obligations required")
        if not self.alternatives or not set(self.alternatives)<={"I","IT","WE","ITS"}:
            raise ValueError("destinations are alternatives, not summed load")
        if type(self.load) is not int or not 1<=self.load<=8 or type(self.deadline) is not int or not 0<=self.deadline<=1000:
            raise ValueError("bounded integer load and deadline required")

    def record(self):
        return {k:getattr(self,k) for k in self.__dataclass_fields__}


def no_easier(a,b):
    """Partial order: a requires at least as much as b; scope changes incomparable."""
    return ((a.family,a.context,a.cue)==(b.family,b.context,b.cue)
        and set(a.requirements)>=set(b.requirements) and set(a.obligations)>=set(b.obligations)
        and set(a.alternatives)<=set(b.alternatives) and a.load>=b.load and a.deadline<=b.deadline
        and set(a.support_allowed)<=set(b.support_allowed))


def compare_demands(a,b):
    ab,ba=no_easier(a,b),no_easier(b,a)
    return "equivalent" if ab and ba else "harder" if ab else "easier" if ba else "incomparable"


class RetentionLedger:
    VERSION="stable-content-guarded-capability-v1"

    def __init__(self,bridge):
        self.bridge=bridge;self.engine=bridge.engine
        self.history={};self.windows={};self.exposures=set();self.certificates={};self.revoked={};self.events=[]

    def _paid(self,ref,actor):
        d=attrs(self.engine.world.head(ref.identity))
        if (d.get('actor')!=actor or d.get('status','succeeded')!='succeeded'
            or d.get('completed')!=d.get('required') or not d.get('required') or d.get('spent',0)<d['required']):
            raise ValueError('complete owned paid evidence required')
        return d

    def _owned(self,actor,ref):
        view=self.engine.participant_view(actor)
        return (ref in view._bindings and view._bindings[ref].endorsement.value not in ('retracted','disputed')) or bool(view.resolve(ref))

    def shell_state(self,actor,demand,job_key):
        e=self.engine;job=e._jobs.get((actor,job_key))
        if job is None:return dict(evaluated=False,clear=False,reason='no_paid_shell_job')
        d=self._paid(job,actor);ref=d.get('encounter')
        if ref is None:return dict(evaluated=False,clear=False,reason='no_encounter')
        s=attrs(e.world.resolve(ref))
        complete=all('known.'+name in s for name in FIELDS)
        scoped=(s.get('target'),s.get('context'),s.get('cue'))==(demand.target,demand.context,demand.cue)
        evaluated=complete and scoped and s.get('demand') is True and not s.get('truncated')
        clear=evaluated and s.get('reason')=='available_demand' and s.get('route')==s.get('base_route')
        clear=clear and not any(s.get(k) for k in ('approval','obligation','excluded','forecast_risk','salience'))
        return dict(evaluated=bool(evaluated),clear=bool(clear),reason=s.get('reason'),
            encounter=ref,operation=job,patterns=tuple(v for k,v in s.items() if k.startswith('pattern.')),
            effects={k:s.get(k) for k in ('approval','obligation','excluded','forecast_risk','salience')})

    def _return(self,actor,keys):
        tm=type_map(self.bridge.tim(actor));perspective=tm['complementary_perspective'];previous=None;refs=[]
        if not keys:return False,()
        for key in keys:
            job=self.engine._jobs.get((actor,key))
            if job is None:return False,tuple(refs)
            d=self._paid(job,actor)
            if not d.get('route_count') or d.get('origin')!=perspective:return False,tuple(refs)
            inputs=tuple(v for k,v in d.items() if k.startswith('input.'))
            if previous is not None and previous not in inputs:return False,tuple(refs)
            perspective=d['destination'];previous=d.get('binding') or d.get('result');refs.append(job)
        return perspective==tm['native_perspective'],tuple(refs)

    def expose(self,actor,demand,kept,return_jobs,shell_job,consumer_job,*,interrupted=False):
        e=self.engine;tm=type_map(self.bridge.tim(actor));self.history.setdefault(actor,{tm['native_perspective']})
        key=(actor,demand.family,demand.context,demand.cue)
        consumer=e._jobs.get((actor,consumer_job));shell=e._jobs.get((actor,shell_job))
        token=(consumer,shell)
        if token in self.exposures:raise ValueError('duplicate exposure does not advance continuity')
        self.exposures.add(token)
        kept=tuple(kept)
        actual=bool(kept) and all(self._owned(actor,r) and e.world.head(r.identity).ref==r for r in kept)
        returned,returns=self._return(actor,return_jobs)
        sh=self.shell_state(actor,demand,shell_job)
        use=False
        if consumer is not None:
            d=self._paid(consumer,actor)
            use=d.get('context')==demand.context and semantic_scope(e,d)==demand.target and any(
                v in kept for k,v in d.items() if k.startswith('input.'))
        good=bool(actual and returned and use and sh['clear'] and not interrupted)
        prior=self.windows.get(key)
        signature=(kept,demand.record())
        hold=prior['hold']+1 if good and prior and prior['signature']==signature else 1 if good else 0
        row=dict(kind='exposure',actor=actor,at_tick=e._now().tick,demand=demand.record(),kept=kept,returns=returns,
            consumer=consumer,shell=sh,actual_content=bool(actual),returned=returned,paid_use=bool(use),
            interrupted=interrupted,hold=hold,closed=good and hold>=2,crossed=tm['complementary_perspective'])
        self.windows[key]=dict(signature=signature,hold=hold,last=row)
        if row['closed']:self.history[actor].add(row['crossed'])
        self.events.append(row)
        return row

    def certify(self,key,actor,demand,capacity_ref,content_uses):
        if key in self.certificates:raise ValueError('certificate identity already exists')
        window=self.windows.get((actor,demand.family,demand.context,demand.cue))
        if not window or not window['last']['closed']:raise ValueError('non-vacuous content closure required')
        capacity=next((x for x in self.engine.development_view(actor)['capacities'] if x['ref']==capacity_ref),None)
        if not capacity or (capacity['context'],capacity['cue'])!=(demand.context,demand.cue):
            raise ValueError('actual owned native capacity in this scope required')
        self._paid(capacity['operation'],actor)
        practices={x['ref']:x for x in self.engine.development_view(actor)['practices']}
        examples=[practices[x] for x in capacity['examples']]
        if len(examples)<2 or any(not x['independent'] or x['supported'] for x in examples):
            raise ValueError('independent paid practice required')
        if len({x['event'] for x in examples})!=len(examples) or len({t.identity for x in examples for t in x['targets']})<2:
            raise ValueError('duplicate practice cannot create capability')
        if len(content_uses)!=len(examples) or len(set(content_uses))!=len(content_uses):
            raise ValueError('each independent episode requires distinct paid content use')
        uses=[]
        for ex,use in zip(examples,content_uses):
            d=self._paid(self.engine._jobs[actor,use],actor)
            if not d.get('route_count') or d.get('context')!=demand.context or semantic_scope(self.engine,d) not in ex['targets']:
                raise ValueError('content use must serve this practice episode and context')
            practice_job=attrs(self.engine.world.head(ex['operation'].identity))
            response=development_attrs(self.engine.world.resolve(ex['response']))
            response_job=attrs(self.engine.world.head(response['operation'].identity))
            if not response_job['finished_tick']<=d['started_tick']<=d['finished_tick']<=practice_job['finished_tick']:
                raise ValueError('content use must follow this response and precede retained practice')
            uses.append(self.engine._jobs[actor,use])
        if demand.load>capacity['max_load']:raise ValueError('certificate exceeds native learned load')
        bound=dict(demand.record(),load=capacity['max_load'])
        row=dict(kind='certificate',key=key,actor=actor,claim='guarded_content_participation',
            scope=bound,native_capacity=capacity_ref,binding=capacity['binding'],
            examples=tuple(capacity['examples']),content_uses=tuple(uses),closure=window['last'],
            required_support=(),material_competence=False)
        self.certificates[key]=row;self.events.append(row);return row

    def applicable(self,key,actor,demand):
        c=self.certificates.get(key)
        if c is None:return False,'absent_certificate'
        if key in self.revoked:return False,'revoked_evidence'
        if c['actor']!=actor:return False,'foreign_certificate'
        bound=Demand(**c['scope'])
        if not no_easier(bound,demand):return False,'outside_trained_demand_bounds'
        if not self._owned(actor,c['binding']):return False,'no_present_access'
        recalled=self.engine.participant_view(actor).traverse(demand.cue,demand.context)
        if recalled.truncated or c['binding'] not in recalled.visited:return False,'not_recalled'
        if not set(c['required_support'])<=set(demand.support_allowed):return False,'support_withdrawn'
        return True,'owned_recalled_scoped_capacity'

    def revoke(self,key,reason):
        if key not in self.certificates or not isinstance(reason,str) or not reason.strip():
            raise ValueError('exact certificate and evidence fault required')
        self.revoked[key]=reason
        self.events.append(dict(kind='certificate_revoked',key=key,reason=reason))
