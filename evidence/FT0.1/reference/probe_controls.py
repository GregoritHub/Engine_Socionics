from probe_historical import *
import itertools

def main():
    out=ROOT/'evidence';answer={}
    dump(out/'Followup_Freeze.json',{'script':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'protocol':hashlib.sha256((ROOT/'Followup_Protocol.json').read_bytes()).hexdigest()})
    # Distinct treatment regimes, not a correction to the observed one-seed run.
    mismatches=json.loads((out/'Document_Mismatches.json').read_text());paired=[]
    for m in mismatches:
        r,_,_=run(m['tim'],m['target']['partner'],steps=80,both_seed=True)
        paired.append({'tim':m['tim'],'target':m['target'],'observed':r['history'],'matches':r['complement_tick']==m['target']['tick']})
    answer['both_seed_followup']=paired
    print('both-seeded timing matches',sum(r['matches'] for r in paired),'/',len(paired),flush=True)
    matrix=[]
    for tim in C.TIMS:
        for policy,gate in itertools.product(('every_tick','relay'),(False,True)):
            r,_,_=run(tim,C.dual_candidate(tim),steps=40,policy=policy,gate=gate)
            matrix.append({'tim':tim,'policy':policy,'gate':gate,'history':r['history'],'post4_seats':r['post4_seats'],'pending_final':len(r['final']['pending'])})
    answer['dual_factorial']=matrix
    # Reproduce a natural close first, then remove future deliveries.
    r,rows,saved=run('iee','sli',steps=6,trace=True)
    a=copy.deepcopy(saved['4']['agent']);withdraw=[]
    for _ in range(40):
        a,pk,rep=D.step(a,[])
        withdraw.append({'tick':a.st.ticks,'kept5':sorted(a.st.at(5).kept),'kept6':sorted(a.st.at(6).kept),'unfed5':a.st.at(5).unfed,'request':any(p.tag=='request' for p in pk),'retained':sorted(a.org['retained']),'seat':a.st.seat})
    answer['withdrawal']=withdraw
    # Empty intersection can replace kept with empty; no forgetting or type change.
    st=handler.receive(a.st,packet('si',{'norms'},source='world'),holon_id='iee')
    a.st=st;a,pk,rep=D.step(a,[])
    answer['disjoint_content_replacement']={'kept5':sorted(a.st.at(5).kept),'request':any(p.tag=='request' for p in pk),'retained':sorted(a.org['retained']),'closure_count':a.altitude}
    # A candidate's window tests nonempty facets, not packet identity or equality.
    a=D.agent('iee');a.candidate=DS.organization('iee',retained={'I','IT'});a.crossed='IT';a.last_progress=0
    held=[]
    for i in range(3):
        f={'experience'} if i%2==0 else {'norms'}
        a,pk,rep=D.step(a,[packet('si',{'experience'},source='supplier_'+str(i)),packet('te',f,source='supplier_'+str(i))])
        held.append(dict(tick=a.st.ticks,kept6=sorted(a.st.at(6).kept),hold=a.hold,closed=rep.get('closed'),clear=a.clear))
    answer['alternate_content_candidate']=held
    # Existing forced-intention API can activate 3/4, contrary to the global absence claim.
    st=new_state('iee');hot=[]
    for _ in range(3):
        st,pk,rep=T.tick(st,[packet('se'),packet('ti')],holon_id='iee',intention='super_ego')
        hot.append({'tick':st.ticks,'activated':[x['position'] for x in activated(st,2)],'brake':rep['signals']['brake']})
    answer['directed_super_ego_activation']=hot
    # Isolated sourced chord vs reception/production generation.
    st=new_state('iee',generative=False).with_organization(DS.organization('iee',retained={'I','IT'}))
    for asp in ('si','te'):st=handler.receive(st,packet(asp,{'experience'}),engaged_block='ego',holon_id='iee')
    before=st.at(6);conducted=chord.conduct(st);final,pk=handler.produce(conducted,1,'iee')
    answer['isolated_chord']={'source6_facets':sorted(before.charge),'destination1_facets':sorted(conducted.at(1).charge),'output':pkrow(pk,True),'source6_drained':not conducted.at(6).charge}
    # Richer requested intensity/window is accepted but ignored by conductivity.
    org=DS.organization('iee',retained={'I','IT'})
    ds=[DS.demand('same',{'IT'},intensity=i,window=w) for i,w in ((0,1),(1,99))]
    answer['demand_discrimination']={'demands':ds,'movements':[DS.conductive_movements(org,d) for d in ds],
        'broader_destinations_are_alternatives':DS.meets_conductively(org,DS.demand('broad',{'IT','WE'}))}
    # Slot tests and n/cp conjugations on the actual sealed kernel.
    sys.path.insert(0,str(ROOT.parent/'Socionics_Engine/baseline/HLE_Rebuild_R21B'))
    sys.path.insert(0,str(ROOT.parent/'Socionics_Engine'))
    from hle import model_a as m
    from hle_unified.axes import AXES,axis_cells
    bypos=C.COORD_POS
    def trans(p,v):return bypos[tuple(a^b for a,b in zip(C.POS_COORD[p],v))]
    n=lambda p:trans(p,(0,1,0));cp=lambda p:trans(p,(0,0,1));opp=lambda p:trans(p,(0,1,1))
    E=clock.advance
    einv={E(p):p for p in range(1,9)}
    counts=Counter();bad=[]
    # pyref returns the quotient coordinates; rebuilt axes names the cells.
    cell=lambda ie:{(1,1):'D',(0,1):'C',(1,0):'N',(0,0):'H'}[C.dcnh_cell(ie)]
    for tim in C.TIMS:
        for p in range(1,9):
            el=C.element_at(tim,p);actual={m.position_of(tim,e) for e in C.routing_neighbors(tim,el)}
            assert el==m.element_at(tim,p)
            assert set(C.routing_neighbors(tim,el))==set(m.neighbors(tim,el))
            assert actual=={trans(p,(1,0,0)),n(p),cp(p)}
            assert E(n(p))==n(E(p));assert cp(E(cp(p)))==einv[p]
            assert C.dcnh_cell(el)==C.dcnh_cell(C.element_at(tim,n(p)))
            flip={'D':'N','N':'D','C':'H','H':'C'}
            assert cell(C.element_at(tim,cp(p)))==flip[cell(el)]
            assert cell(C.element_at(tim,opp(p)))==flip[cell(el)]
            counts['type_seat_checks']+=1
            if actual!={E(p),n(p),cp(p)}:bad.append([tim,p])
        for pair,label in zip(AXES,axis_cells(tim)):
            assert {cell(C.element_at(tim,p)) for p in pair}=={label};counts['core_pairs']+=1
        for start in (1,3):
            lap=clock.orbit(start)
            assert {cell(C.element_at(tim,p)) for p in lap}=={'D','C','N','H'}
            assert [C.POS_COORD[p][0] for p in lap]==[0,0,1,1];counts['laps']+=1
    answer['structure']={'passed':dict(counts),'estafette_neighbor_counterexamples':bad}
    # Necessary global gate distinction independently enumerated.
    truth=[]
    for seat,gate,retained,pending in itertools.product(range(1,9),(False,True),(False,True),(False,True)):
        clock.RELAY_GATE=gate;st=new_state('iee');st=replace(st,seat=seat,pending=(packet('ti'),) if pending else (),retained=frozenset({'I','IT'} if retained else {'I'}))
        got=clock.step(st).seat
        expected=3 if seat in (1,2,5,6) and pending and not(gate and retained) else (1 if seat in (3,4,7,8) and not pending else E(seat))
        assert got==expected;truth.append([seat,gate,retained,pending,got])
    clock.RELAY_GATE=False;answer['gate_truth_table']=truth
    dump(out/'Control_Results.json',answer)
    print('controls saved; withdrawal final',withdraw[-1],flush=True)
    print('alternating-content closure',held,flush=True)
    print('complexes',hot,flush=True)
    print('structure',dict(counts),'gate combinations',len(truth),flush=True)

if __name__=='__main__':main()
