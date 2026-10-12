import os, sys; _d=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,_d); sys.path.insert(0,os.path.dirname(_d))
import collections
import movement as M
from pyref.core import v11_beneficiary
def ringf(f,st):
    r=[st]
    while f(r[-1]) not in r: r.append(f(r[-1]))
    return r
GROUPS={"quadra":["ile","sei","ese","lii"],"benefit ring":ringf(v11_beneficiary,'ile'),"mixed":["ile","esi","lsi","iee"]}
def table(label, world="seat", policy="always", steps=200):
    agg=collections.defaultdict(collections.Counter); seat=collections.defaultdict(collections.Counter); reached=collections.Counter()
    for name,g in GROUPS.items():
        runs=M.ensemble(g,steps=steps,n_seats=8,all_orders=False,policy=policy,world=world,sync=True,calling=True,polarity=True,use_reach=True)
        for r in runs:
            for h in g:
                m=r[h]; reached[m.a.altitude]+=1
                for alt,c in m.pol_by_alt.items():
                    for k,n in c.items(): agg[alt][k]+=n
                for alt,c in getattr(m,'seat_by_alt',{}).items():
                    for k,n in c.items(): seat[alt][k]+=n
    print("=== %s  world=%s policy=%s  final altitudes %s"%(label,world,policy,dict(sorted(reached.items()))))
    print("  alt  moves  acc_eff exp_eff acc_idle exp_idle  balance  idle   seat-share")
    for alt in sorted(agg):
        c=agg[alt]; ae=c[("accepting",True)]; ee=c[("producing",True)]; ai=c[("accepting",False)]; ei=c[("producing",False)]; tot=ae+ee+ai+ei
        ss=seat[alt]; tt=max(1,sum(ss.values()))
        print("   %d  %6d  %6d  %6d  %6d  %6d   %.3f   %.3f   %s"%(alt,tot,ae,ee,ai,ei,abs(ae-ee)/max(1,ae+ee),(ai+ei)/max(1,tot),
              " ".join("%d:%.0f%%"%(q,100*ss[q]/tt) for q in sorted(ss))))
if __name__=="__main__":
    import relay_gate
    if "gate" in sys.argv: relay_gate.install()
    table("A23 "+("gated" if "gate" in sys.argv else "plain"))
