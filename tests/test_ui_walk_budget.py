"""Isolate the pure tree walker from runner-only UnityPy dependencies."""
import ast
from collections import deque
from pathlib import Path
from types import SimpleNamespace
import unittest


def walker():
    tree=ast.parse(Path('tools/apk-analyze/ui_layout.py').read_text())
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='walk')
    scope={'deque':deque,'stable_object_id':id,'_pptr':lambda x:x,
           'node_info':lambda x:{'name':x.name,'components':[]}}
    exec(compile(ast.Module(body=[function],type_ignores=[]),'<walk>','exec'),scope)
    return scope['walk']


class WalkBudgetTests(unittest.TestCase):
    def test_wide_parent_not_silently_capped(self):
        children=[SimpleNamespace(name=str(i),m_Children=[]) for i in range(150)]
        root=SimpleNamespace(name='root',m_Children=children)
        diag={}
        self.assertEqual(len(walker()(root,50000,diag)),151)
        self.assertFalse(diag['truncated'])
        self.assertEqual(diag['pending_transforms'],0)

    def test_budget_and_cycles_are_explicit(self):
        child=SimpleNamespace(name='child',m_Children=[])
        root=SimpleNamespace(name='root',m_Children=[child])
        child.m_Children=[root]
        diag={}
        self.assertEqual(len(walker()(root,1,diag)),1)
        self.assertTrue(diag['truncated'])
        self.assertEqual(diag['pending_transforms'],1)
        diag={}
        self.assertEqual(len(walker()(root,50000,diag)),2)
        self.assertFalse(diag['truncated'])


if __name__=='__main__':unittest.main()
