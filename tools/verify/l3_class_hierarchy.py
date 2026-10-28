"""Declared APK dump inheritance, namespace-qualified; never global same-name guessing."""
import re
from collections import defaultdict

def hierarchy(dump):
    types={}
    for block in re.split(r'(?=// Namespace:)',dump):
        ns=re.match(r'// Namespace:([^\n]*)',block)
        decl=re.search(r'(?m)^[^\n]*\bclass ([\w.]+)(?:\s*:[ \t]*([^\n]+?))?\s*// TypeDefIndex:',block)
        if ns and decl:
            parent=(decl[2] or '').split(',')[0].strip()
            types[(ns[1].strip(),decl[1])]=parent
    parents={}
    for qualified,parent in types.items():
        own=(qualified[0],parent)
        if own in types:parents[qualified]=own
        elif '.' in parent:
            ns,_,name=parent.rpartition('.')
            if (ns,name) in types:parents[qualified]=(ns,name)
        # Unqualified framework types are not guessed across namespaces.
    return parents

def lineage(qualified,parents):
    out=[];seen=set()
    while qualified not in seen:
        out.append(qualified);seen.add(qualified)
        if qualified not in parents:break
        qualified=parents[qualified]
    return out
