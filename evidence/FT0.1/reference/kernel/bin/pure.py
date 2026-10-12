import os, sys; _d=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,_d); sys.path.insert(0,os.path.dirname(_d))
import collections
import movement as M, relay_gate, balance
import metabolism.tick; T=sys.modules["metabolism.tick"]
relay_gate.install()
T.FIRING_POLICY = sys.argv[1] if len(sys.argv)>1 else "relay"
balance.table("A23 gated, firing=%s"%T.FIRING_POLICY)
agg=collections.defaultdict(collections.Counter)
for name,g in balance.GROUPS.items():
    runs=M.ensemble(g,steps=200,n_seats=8,all_orders=False,policy="always",world="seat",sync=True,calling=True,polarity=True,use_reach=True)
    for r in runs:
        for h in g:
            for alt,c in r[h].seat_eff.items():
                for k,n in c.items(): agg[alt][k]+=n
for alt in sorted(agg):
    print("alt",alt, {q: "%d/%d"%(agg[alt][(q,True)],agg[alt][(q,False)]) for q in range(1,9) if agg[alt][(q,True)]+agg[alt][(q,False)]})
