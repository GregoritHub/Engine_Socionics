"""Fixed evaluator witnesses; route assignments here are not runtime autonomy."""
import copy
from dataclasses import replace
import unittest
from tests_c3 import fixtures as ca
from tests_c7_workflow import fixtures as wf
from hle_unified.workflow_execution import WorkflowEngine
from hle_unified.crossing_execution import CrossingEngine
from hle_unified.self_content import encode, decode
from full_theory.content import ContentBridge
from full_theory.content_audit import audit_content


class Ablated(CrossingEngine):
    def _semantic_step(self,name,p,previous):
        kind,target,value=super()._semantic_step(name,p,previous)
        if p.get('request') and p['request'].key=='ft-ego':
            d=decode(value['payload']);d.update(cap=None,consent=False)
            return kind,target,{'payload':encode(d)}
        return kind,target,value


class WorkflowAblated(WorkflowEngine):
    def _semantic_step(self,name,p,previous):
        kind,target,value=super()._semantic_step(name,p,previous)
        if p.get('request') and p['request'].key=='ft-ego':
            d=decode(value['payload']);d.update(tasks=(),feasible=False,authorized=False)
            return kind,target,{'payload':encode(d)}
        return kind,target,value


def handoff(setting,changed=False,ablate=False,provenance=(),partial=False):
    f=ca if setting=='canonical' else wf
    if setting=='canonical':
        e=ca.setup_c3(engine_type=Ablated if ablate else CrossingEngine)
        initial=ca.cell(e,'Mobilize','accumulation',key='ft-supplied',consumer=False)
    else:
        e=wf.setup_workflow(engine_type=WorkflowAblated if ablate else WorkflowEngine)
        initial=wf.cell(e,'Mobilize','accumulation',key='ft-supplied',consumer=False)
    bridge=ContentBridge(e)
    packet=bridge.emit('intake',f.ALICE,'ft-supplied',f.ALICE,initial['result'],provenance=provenance)
    if partial:
        assert bridge.receive('intake',f.ALICE,quantum=1) is None
        assert not bridge.kept and not bridge.receipts
    uptake=bridge.receive('intake',f.ALICE)
    assert uptake['seat']==5
    incoming=uptake['content']
    if setting=='canonical':
        mobilize=ca.req(e,'ft-a6','organize-accumulation-v1',(incoming,))
    else:
        mobilize=wf.request(e,'ft-a6','Organize','accumulation',(incoming,))
    a6=bridge.execute(mobilize,consumed=(incoming,));model=a6['output']
    assert bridge.completed(f.ALICE,'ft-a6')['seat']==6
    if setting=='canonical':
        own=ca.seed_intent(e,'ft-retained',cap=1 if changed else 2)
        ego=replace(ca.req(e,'ft-ego','understand-expenditure-v1',(model,own)),elements=('ne',))
    else:
        rows=(('inspect-0','inspect',(),0,1 if changed else 8,f.ALICE),)
        own=wf.authored(e,'ft-retained',rows,kind='stance')
        ego=replace(wf.request(e,'ft-ego','Understand','expenditure',(model,own)),elements=('ne',))
    combined=bridge.compose(ego,own,model);out=combined['output']
    if setting=='canonical':
        consumer=ca.req(e,'ft-later','use-personal-v1',(out,),stock=ca.SUPPLY,demand=4)
    else:
        consumer=wf.request(e,'ft-later','use-personal',None,(out,),clock=2)
    later=bridge.execute(consumer,consumed=(out,));data=f.data(e,later['output'])
    report=audit_content(e.world.journal(),bridge.events)
    return e,bridge,dict(result=data,ego_cost=e.job_status(f.ALICE,'ft-ego')['spent'],
        a5=packet,a6=model,ego=out,retained=own,ego_request=ego,audit=report)


class ContentTests(unittest.TestCase):
    def test_public_packet_requires_exact_scoped_paid_uptake(self):
        for setting in ('canonical','workflow'):
            if setting=='canonical':
                e=ca.setup_c3()
                ca.cell_c2(e,'Commune','expenditure',prefix='public',consumer=False)
            else:
                e=wf.setup_workflow()
                wf.cell(e,'Share','expenditure',key='public',consumer=False)
            b=ContentBridge(e);public=e.job_status(ca.ALICE,'public')['public.0']
            self.assertFalse(e.participant_view(ca.BOB).resolve(public))
            b.emit('public',ca.ALICE,'public',ca.BOB,public)
            self.assertFalse(b.receipts)
            with self.assertRaises(ValueError):b.receive('public',ca.ALICE)
            with self.assertRaises(ValueError):b.emit('foreign',ca.ALICE,'public',ca.EVE,public)
            before=e.wallet(ca.BOB)['energy']
            self.assertIsNone(b.receive('public',ca.BOB,quantum=1))
            self.assertFalse(b.receipts)
            self.assertFalse(e.participant_view(ca.BOB).resolve(public))
            uptake=b.receive('public',ca.BOB)
            self.assertEqual(uptake['source'],public)
            self.assertTrue(e.participant_view(ca.BOB).resolve(public))
            self.assertGreater(before,e.wallet(ca.BOB)['energy'])
            self.assertTrue(audit_content(e.world.journal(),b.events)['passed'])
            with self.assertRaises(ValueError):b.receive('public',ca.BOB)

    def test_nonphysical_semantic_scope_and_tampering(self):
        for setting in ('canonical','workflow'):
            e,b,r=handoff(setting)
            job=e.job_status(ca.ALICE,'ft-later')
            self.assertIsNone(job['target'])
            self.assertEqual(b.completed(ca.ALICE,'ft-later')['target'],job['content_target'])
            self.assertIsNotNone(job['content_target'])
            b.emit('scope',ca.ALICE,'ft-ego',ca.ALICE,r['ego'])
            b.packets['scope']['target']=ca.CUE5
            with self.assertRaises(ValueError):b.receive('scope',ca.ALICE)
            with self.assertRaises(ValueError):audit_content(e.world.journal(),b.events)

    def test_both_handoffs_have_content_and_later_use(self):
        for setting in ('canonical','workflow'):
            e,b,r=handoff(setting)
            self.assertEqual(r['audit']['compositions'],1)
            self.assertTrue(r['audit']['passed'])
            self.assertEqual(b.completed(ca.ALICE,'ft-ego')['aspect'],'ne')

    def test_essential_operand_change_at_fixed_labels_and_cost(self):
        for setting in ('canonical','workflow'):
            e,b,a=handoff(setting);ee,bb,z=handoff(setting,changed=True)
            self.assertEqual(a['ego_cost'],z['ego_cost'])
            self.assertEqual(b.completed(ca.ALICE,'ft-ego')['aspect'],bb.completed(ca.ALICE,'ft-ego')['aspect'])
            field='amount' if setting=='canonical' else 'next_action'
            self.assertNotEqual(a['result'][field],z['result'][field])

    def test_matched_chord_ablation(self):
        for setting in ('canonical','workflow'):
            e,b,a=handoff(setting);ee,bb,z=handoff(setting,ablate=True)
            self.assertEqual(a['ego_cost'],z['ego_cost'])
            field='amount' if setting=='canonical' else 'next_action'
            self.assertNotEqual(a['result'][field],z['result'][field])

    def test_decorative_provenance_does_not_change_semantics(self):
        for setting in ('canonical','workflow'):
            e,b,a=handoff(setting);ee,bb,z=handoff(setting,provenance=('carried','walk'))
            self.assertEqual(a['result'],z['result'])
            self.assertEqual(a['ego_cost'],z['ego_cost'])

    def test_missing_operand_and_relabel_rejected(self):
        e,b,r=handoff('canonical')
        request=replace(r['ego_request'],key='missing',inputs=(r['retained'],))
        with self.assertRaises(ValueError):b.compose(request,r['retained'],r['a6'])
        with self.assertRaises(ValueError):b.compose(replace(r['ego_request'],key='renamed',elements=('ni',)),r['retained'],r['a6'])

    def test_paid_partial_uptake_and_duplicate(self):
        e,b,r=handoff('workflow',partial=True)
        with self.assertRaisesRegex(ValueError,'duplicate'):b.receive('intake',ca.ALICE)
        with self.assertRaises(ValueError):b.emit('intake',ca.ALICE,'ft-supplied',ca.ALICE)

    def test_labels_only_and_wrong_receiver(self):
        e,b,r=handoff('canonical')
        with self.assertRaises((ValueError,KeyError)):b.emit('label',ca.ALICE,'not-paid',ca.ALICE)
        b.emit('wrong',ca.ALICE,'ft-supplied',ca.ALICE,r['a5']['output'])
        with self.assertRaisesRegex(ValueError,'wrong'):b.receive('wrong',ca.BOB)

    def test_forged_aspect_and_stale_job_rejected(self):
        e,b,r=handoff('canonical')
        b.emit('aspect',ca.ALICE,'ft-supplied',ca.ALICE,r['a5']['output']);b.packets['aspect']['aspect']='ne'
        with self.assertRaises(ValueError):b.receive('aspect',ca.ALICE)
        b.emit('stale',ca.ALICE,'ft-supplied',ca.ALICE,r['a5']['output']);p=b.packets['stale'];p['operation']=replace(p['operation'],revision=1)
        with self.assertRaises(ValueError):b.receive('stale',ca.ALICE)

    def test_independent_auditor_rejects_forged_receipt_and_packet(self):
        e,b,r=handoff('canonical')
        events=copy.deepcopy(b.events)
        next(x for x in events if x['kind']=='uptake')['receipt']=r['retained']
        with self.assertRaises(ValueError):audit_content(e.world.journal(),events)
        events=copy.deepcopy(b.events)
        next(x for x in events if x['kind']=='emit')['packet']['aspect']='ne'
        with self.assertRaises(ValueError):audit_content(e.world.journal(),events)

    def test_private_content_is_not_public_competence(self):
        e,b,r=handoff('canonical')
        with self.assertRaisesRegex(ValueError,'private'):b.emit('stolen',ca.ALICE,'ft-ego',ca.BOB,r['ego'])
