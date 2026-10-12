#!/usr/bin/env python3
"""Re-derive algebra.archetype's tables from the paper.  Usage:
   python3 bin/audit_archetypes.py path/to/Archetypal_Shadow_Complex.docx
Parses the sixteen tables and asserts every archetype is a single
position, every element a single disorder, and both equal the module."""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pyref.core import position_of
from algebra import archetype as A
txt = subprocess.run(["extract-text", sys.argv[1]], capture_output=True, text=True).stdout
NAME = {'SiF':'sei','NeT':'ile','TiN':'lii','FeS':'ese','TiS':'lsi','FeN':'eie','NiF':'iei','SeT':'sle',
        'NiT':'ili','SeF':'see','TeN':'lie','FiS':'esi','TeS':'lse','FiN':'eii','SiT':'sli','NeF':'iee'}
arch, dis = {}, {}
for t1, t2, body in re.findall(r'\| \*\*(\w+) and (\w+)\*\* \|.*?\n((?:\|.*\n)+)', txt):
    for row in body.strip().split('\n'):
        m = re.match(r'\| \*(.+?) - (\w+)\* \| \*?(\w+)\*? \| (\w\w) - ([\w.\-]+ ?\w*) \((\w+)\) \| (\w\w) - ([\w.\-]+ ?\w*) \((\w+)\)', row)
        if not m: continue
        for tim, f, d in ((NAME[t1], m.group(4).lower(), m.group(5)), (NAME[t2], m.group(7).lower(), m.group(8))):
            arch.setdefault(m.group(2), set()).add(position_of(tim, f))
            dis.setdefault(f, set()).add({"pass.-aggr.": "passive_aggressive"}.get(d.lower(), d.lower()))
ok = all(v == {A.POSITION[k]} for k, v in arch.items()) and len(arch) == 8
ok2 = all(v == {A.DISORDER[k][0]} for k, v in dis.items()) and len(dis) == 8
print("archetype->position constant and equal to module:", ok)
print("element->disorder constant and equal to module:  ", ok2)
sys.exit(0 if ok and ok2 else 1)
