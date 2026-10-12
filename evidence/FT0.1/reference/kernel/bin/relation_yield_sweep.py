import sys, collections
sys.path.insert(0, '/home/claude/clean')
from pyref.core import TIMS, element_at, contrary
from crux.typemap import perspective_cost_class
from metabolism import develop as D, packet
from metabolism.exchange import relation_of
from metabolism.complex import activated
T=int(sys.argv[1])
def pair(t,u,T=T):
    ags = {"A": D.agent(t), "B": D.agent(u)}
    ags,hist = D.run(ags, {"A":[packet(element_at(t,1))], "B":[packet(element_at(u,1))]}, T)
    return ags,hist
# contrary symmetry done right
res={}
for t in TIMS:
    for u in TIMS:
        ags,_=pair(t,u)
        res[(t,u)]=[(h["tick"],perspective_cost_class(t,h["closed"])) for h in ags["A"].history]
bad=[(t,u) for (t,u) in res if res[(t,u)]!=res[(contrary(t),contrary(u))]]
print("T=%d contrary-involution divergences:"%T, len(bad))
byrel=collections.defaultdict(set)
for k,v in res.items(): byrel[relation_of(*k)].add(tuple(v))
for r,s in sorted(byrel.items()): print("  %-20s"%r, sorted(s))
