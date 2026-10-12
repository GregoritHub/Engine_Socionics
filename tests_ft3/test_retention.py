"""Finite externally supplied opportunities, with explicit negative controls."""
import copy
from dataclasses import replace
import unittest
from tests_c5 import fixtures as f
from tests_c3 import fixtures as ca
from tests_c7_workflow import fixtures as wf
from hle_unified.workflow_interruption_execution import WorkflowInterruptionEngine as Engine
from hle_unified.shell_records import Effect
from hle_unified.operation_records import OperationRequest
from hle_unified.self_content import encode
from full_theory.content import ContentBridge
from full_theory.retention import Demand,RetentionLedger,compare_demands
from full_theory.retention_audit import audit_retention


def setup(setting='canonical',generate=True):
    e=f.setup(engine_type=Engine,generate=generate);b=ContentBridge(e);l=RetentionLedger(b)
    d=Demand(setting,f.ROOM,f.CUE5,f.SAW)
    return e,b,l,d


def content(e,b,setting,target,prefix):
    observed_target=ca.SUPPLY if setting=='canonical' else target
    event=f.perform(e,OperationRequest(prefix+'-inspect',f.ALICE,'inspect',f.ROOM,
        target=observed_target,evidence=f.evidence(e,f.ALICE,observed_target)),limit=100000)
    observation=f.receive(e,event,f.ALICE,prefix+'-observation')
    evidence=f.evidence(e,f.ALICE,target)
    if setting=='canonical':
        organize=replace(ca.req(e,prefix+'-a6','organize-accumulation-v1',(observation,)),target=target,evidence=evidence)
    else:organize=wf.request(e,prefix+'-a6','Organize','accumulation',(observation,),target=target)
    model=b.execute(organize,consumed=(observation,))['output']
    if setting=='canonical':
        own=ca.seed(e,prefix+'-own',encode(dict(kind='intention',cap=2,consent=True)),target=target,relation='c3.data',status=f.ClaimStatus.TENTATIVE)
        r=replace(ca.req(e,prefix+'-ego','understand-expenditure-v1',(model,own)),target=target,evidence=evidence,elements=('ne',))
    else:
        own=wf.authored(e,prefix+'-own',(('inspect-0','inspect',(),0,8,f.ALICE),),target=target,kind='stance')
        r=replace(wf.request(e,prefix+'-ego','Understand','expenditure',(model,own),target=target),elements=('ne',))
    result=b.compose(r,own,model)['output']
    return dict(kept=(model,result),returns=(prefix+'-a6',prefix+'-ego'),result=result,target=target)


def use(e,b,setting,c,key):
    if setting=='canonical':
        r=replace(ca.req(e,key,'use-personal-v1',(c['result'],),stock=ca.SUPPLY,demand=2),
            target=c['target'],evidence=f.evidence(e,f.ALICE,c['target']))
    else:r=wf.request(e,key,'use-personal',None,(c['result'],),target=c['target'])
    return b.execute(r,consumed=(c['result'],))


def exposure(e,b,l,d,c,key,**kwargs):
    use(e,b,d.family,c,key+'-use')
    source=f.dev.supply8(e,key+'-facts',target=d.target)
    f.dev.meet(e,key+'-shell',source,target=d.target)
    return l.expose(f.ALICE,d,c['kept'],c['returns'],key+'-shell',key+'-use',**kwargs)


def trained(setting='canonical',supported=False):
    e,b,l,d=setup(setting);p=f.dev.generated(e)
    for i,t in enumerate((f.SAW,f.SAW2,f.KIT,f.STOCK)):
        f.dev.release8(e,'local-'+str(i),p,t)
    c=content(e,b,setting,f.SAW,'first')
    exposure(e,b,l,d,c,'close-1');exposure(e,b,l,d,c,'close-2')
    uses=[]
    for i,targets in enumerate(((f.SAW,f.KIT),(f.SAW2,f.STOCK))):
        event=f.dev.respond8(e,'task-'+str(i),p,targets,approved=supported)
        current=c if i==0 else content(e,b,setting,f.SAW2,'second')
        key='training-use-'+str(i);use(e,b,setting,current,key);uses.append(key)
        f.dev.practice8(e,'practice-'+str(i),p,event)
    if supported:return e,b,l,d,p,uses
    f.dev.reorganize8(e,'organize-practice',p)
    capacity=e._capacities[p.ref]['ref']
    certificate=l.certify('guarded',f.ALICE,d,capacity,tuple(uses))
    return e,b,l,d,p,uses


class RetentionTests(unittest.TestCase):
    def test_nonphysical_scope_and_wrong_target_control(self):
        for setting in ('canonical','workflow'):
            e,b,l,d=setup(setting,generate=False);c=content(e,b,setting,f.SAW,'scope')
            good=exposure(e,b,l,d,c,'correct')
            job=e.job_status(f.ALICE,'correct-use')
            self.assertIsNone(job['target'])
            self.assertEqual(job['content_target'],d.target)
            self.assertTrue(good['paid_use'])
            wrong=exposure(e,b,l,replace(d,target=f.KIT),c,'wrong')
            self.assertTrue(wrong['shell']['clear'])
            self.assertFalse(wrong['paid_use'])
            self.assertFalse(wrong['closed'])
            self.assertTrue(audit_retention(e.world.journal(),l.events)['passed'])
            bad=copy.deepcopy(l.events);bad[-1]['paid_use']=True
            with self.assertRaises(ValueError):audit_retention(e.world.journal(),bad)

    def test_two_settings_close_and_register_scoped_capacity(self):
        for setting in ('canonical','workflow'):
            e,b,l,d,p,uses=trained(setting)
            self.assertTrue(l.applicable('guarded',f.ALICE,d)[0])
            self.assertEqual(l.history[f.ALICE],{'I','IT'})
            self.assertEqual(audit_retention(e.world.journal(),l.events)['certificates'],1)

    def test_novel_target_changed_partner_and_harder_load(self):
        for setting in ('canonical','workflow'):
            e,b,l,d,p,uses=trained(setting)
            novel=replace(d,target=f.BORROWED,load=2)
            self.assertTrue(l.applicable('guarded',f.ALICE,novel)[0])
            event=f.dev.respond8(e,'novel-response',p,(f.BORROWED,f.dev.MEMORY),partner=f.ObjectRef(f.EVE,1))
            self.assertTrue(e._response_results[event]['completed_demand'])
            self.assertFalse(l.applicable('guarded',f.ALICE,replace(novel,load=3))[0])
            too_many=f.dev.respond8(e,'hard-response',p,(f.dev.MEMORY,f.dev.POSSIBILITY,f.dev.ACTION),partner=f.ObjectRef(f.EVE,1))
            self.assertFalse(e._response_results[too_many]['completed_demand'])

    def test_capacity_removal_changes_later_guarded_action(self):
        e,b,l,d,p,uses=trained();initial=e.checkpoint();control=Engine.restore(initial)
        control._capacities={}  # Declared evaluator intervention, not a production command.
        ordinary=f.dev.respond8(e,'reuse',p,(f.dev.MEMORY,f.dev.POSSIBILITY),partner=f.ObjectRef(f.EVE,1))
        removed=f.dev.respond8(control,'reuse',p,(f.dev.MEMORY,f.dev.POSSIBILITY),partner=f.ObjectRef(f.EVE,1))
        self.assertTrue(e._response_results[ordinary]['completed_demand'])
        self.assertFalse(control._response_results[removed]['completed_demand'])

    def test_interrupted_and_changing_windows_do_not_close(self):
        e,b,l,d=setup(generate=False);c=content(e,b,d.family,f.SAW,'a')
        self.assertFalse(exposure(e,b,l,d,c,'one')['closed'])
        self.assertFalse(exposure(e,b,l,d,c,'break',interrupted=True)['closed'])
        self.assertEqual(exposure(e,b,l,d,c,'after')['hold'],1)
        changed=content(e,b,d.family,f.SAW,'changed')
        self.assertEqual(exposure(e,b,l,d,changed,'changed')['hold'],1)

    def test_mere_visit_and_missing_return_do_not_close(self):
        e,b,l,d=setup(generate=False);c=content(e,b,d.family,f.SAW,'a');c['returns']=()
        self.assertFalse(exposure(e,b,l,d,c,'visit1')['closed'])
        self.assertFalse(exposure(e,b,l,d,c,'visit2')['closed'])
        self.assertEqual(l.history[f.ALICE],{'I'})

    def test_all_five_active_shell_effects_are_nonvacuous(self):
        for effect in ('approval','obligation','salience','forecast','exclude_route'):
            e,b,l,d=setup(generate=False)
            source=f.dev.supply8(e,'initial');f.dev.inject(e,Effect(effect,'*',1))
            f.dev.meet(e,'active',source)
            row=l.shell_state(f.ALICE,d,'active')
            self.assertTrue(row['evaluated'],effect);self.assertFalse(row['clear'],effect)

    def test_empty_or_incomplete_detector_is_not_clearance(self):
        e,b,l,d=setup(generate=False)
        self.assertFalse(l.shell_state(f.ALICE,d,'absent')['evaluated'])
        source=f.dev.supply8(e,'incomplete',safe=None);f.dev.meet(e,'incomplete',source)
        self.assertFalse(l.shell_state(f.ALICE,d,'incomplete')['evaluated'])

    def test_duplicate_exposure_and_training_are_rejected(self):
        e,b,l,d,p,uses=trained()
        x=l.events[1]
        with self.assertRaises(ValueError):l.expose(f.ALICE,d,x['kept'],('first-a6','first-ego'),'close-2-shell','close-2-use')
        with self.assertRaises(ValueError):l.certify('duplicate',f.ALICE,d,e._capacities[p.ref]['ref'],(uses[0],uses[0]))

    def test_supported_practice_does_not_award_capacity(self):
        e,b,l,d,p,uses=trained(supported=True)
        self.assertTrue(all(not x['independent'] for x in e._practices[p.ref]))
        with self.assertRaises(ValueError):f.dev.reorganize8(e,'invalid-mastery',p)

    def test_partial_order_preserves_incomparability(self):
        e,b,l,d=setup(generate=False)
        self.assertEqual(compare_demands(replace(d,load=2),d),'harder')
        self.assertEqual(compare_demands(replace(d,load=2,deadline=999),replace(d,requirements=('experience','norms'))),'incomparable')
        self.assertEqual(compare_demands(replace(d,family='workflow'),d),'incomparable')

    def test_missing_recall_and_revocation_preserve_history(self):
        e,b,l,d,p,uses=trained();before=set(l.history[f.ALICE])
        wrong=replace(d,cue=f.CUE)
        self.assertFalse(l.applicable('guarded',f.ALICE,wrong)[0])
        l.revoke('guarded','independent episode evidence withdrawn')
        self.assertEqual(l.applicable('guarded',f.ALICE,d),(False,'revoked_evidence'))
        self.assertEqual(l.history[f.ALICE],before)

    def test_independent_audit_rejects_false_clearance_and_history(self):
        e,b,l,d,p,uses=trained();bad=copy.deepcopy(l.events)
        bad[0]['closed']=True
        with self.assertRaises(ValueError):audit_retention(e.world.journal(),bad)
        bad=copy.deepcopy(l.events);bad[-1]['scope']['load']=8
        with self.assertRaises(ValueError):audit_retention(e.world.journal(),bad)
