import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/verify'))
from ui_reference_links import resolve


class ScopedReferenceTests(unittest.TestCase):
    def test_same_id_in_another_file_never_selected(self):
        rows=[{'serialized_file':'A','path_id':105,'status':'exported','tree':{'m_Name':'wrong'}},
              {'serialized_file':'B','path_id':105,'status':'exported','tree':{'m_Name':'right'}}]
        owner={'serialized_file':'level2','externals':[{'file_id':3,'path':'B'}]}
        self.assertEqual(resolve(owner,{'m_FileID':3,'m_PathID':105},rows)['name'],'right')
        self.assertEqual(resolve(owner,{'m_FileID':0,'m_PathID':105},rows)['status'],'target_file_unresolved')

    def test_missing_scope_never_guessed_from_id(self):
        r=resolve({'serialized_file':'level2','externals':[{'file_id':3,'path':'B'}]},
                  {'m_FileID':3,'m_PathID':105},[{'serialized_file':'','path_id':105}])
        self.assertEqual(r['status'],'target_file_unresolved')
        self.assertEqual(resolve({}, {'m_PathID':105},[])['status'],'owner_scope_missing')
        self.assertEqual(resolve({}, {'m_PathID':0},[])['status'],'null')


if __name__=='__main__': unittest.main()
