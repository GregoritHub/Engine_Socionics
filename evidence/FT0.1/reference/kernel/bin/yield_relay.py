import os, sys; _d=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,_d); sys.path.insert(0,os.path.dirname(_d))
import collections
import metabolism.tick; T=sys.modules["metabolism.tick"]
from pyref.core import TIMS, element_at, contrary
from crux.typemap import perspective_cost_class as pcc
from metabolism import develop as D, packet
from metabolism.exchange import relation_of
def seed(ags): return {h: [packet(element_at(a.st.tim, 1))] for h, a in ags.items()}
def hist(a): return tuple((x["tick"], pcc(a.st.tim, x["closed"])) for x in a.history)
for pol in ("every_tick","relay"):
    T.FIRING_POLICY=pol
    res={}
    for t in TIMS:
        for u in TIMS:
            ags={"A":D.agent(t),"B":D.agent(u)}; ags,_=D.run(ags,seed(ags),80); res[(t,u)]=hist(ags["A"])
    byrel=collections.defaultdict(set)
    for k,v in res.items(): byrel[relation_of(*k)].add(v)
    print("==",pol,"type-invariant:",all(len(s)==1 for s in byrel.values()),"contrary-symmetric:",all(res[(t,u)]==res[(contrary(t),contrary(u))] for (t,u) in res))
    for r in sorted(byrel): print("  %-20s"%r, sorted(byrel[r])[0] if len(byrel[r])==1 else "VARIANT %d"%len(byrel[r]))
