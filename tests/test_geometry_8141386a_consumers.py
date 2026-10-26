"""Report118 reverse-reference integrity, exact context and non-use counterexamples.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from collections import Counter
import gzip
import json
from pathlib import Path
import sqlite3
import struct
import tempfile
import unittest
from tools.verify.geometry_8141386a_atlas_io import canonical,sha,sha_file,key,identity,iter_arrays
from tools.verify.geometry_8141386a_consumers_sources import RAW
from tools.verify.geometry_8141386a_consumers_context import context,resolve,reference_category
from tools.verify.l3_geometry_8141386a_consumers import INDEX,OUTPUT,native_rows,build,sprite_probe,renderer_probe


def context_db():
    d=sqlite3.connect(':memory:');d.executescript('''CREATE TABLE cap_objects(file TEXT,pid INTEGER,sha TEXT,kind TEXT,cls TEXT,go_file TEXT,go_pid INTEGER,name TEXT,parent_file TEXT,parent_pid INTEGER,context_error TEXT,PRIMARY KEY(file,pid));CREATE TABLE cap_aliases(file TEXT,pid INTEGER,kind TEXT,label TEXT,sources TEXT,PRIMARY KEY(file,pid,kind,label));''');return d


def put(d,pid,kind,go=None,parent=None,name=None,sha='a'):
    d.execute('INSERT INTO cap_objects VALUES(?,?,?,?,?,?,?,?,?,?,?)',('data.unity3d/a',pid,sha,kind,None,'data.unity3d/a' if go else None,go,name,'data.unity3d/a' if parent else None,parent,None))


def fresh(pid=1,tr=2):return dict(identity=dict(serialized_file='data.unity3d/a',path_id=pid),object_sha256='a',transform_candidates=[dict(serialized_file='data.unity3d/a',path_id=tr)])


class Consumers(unittest.TestCase):
    def test_compact_artifact_reproduction(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'out.gz';build(p);self.assertEqual(sha_file(p),sha_file(OUTPUT))

    def test_complete_native_census_spans_and_exact_nulls(self):
        idx=json.loads(INDEX.read_bytes());c=Counter()
        for r,_ in native_rows(idx):
            c['all']+=1;c['null' if r['sprite']is None else 'nonnull']+=1
            self.assertTrue(r['complete_inverse_equal']);self.assertTrue(r['gameobject']['complete_inverse_equal'])
            p=r['sprite_pointer'];s=r['original_sprite_pointer_span'];self.assertEqual(s['size'],12);self.assertEqual(s['sha256'],sha(struct.pack('<iq',p['m_FileID'],p['m_PathID'])))
            self.assertLessEqual(s['offset']+12,r['object_size'])
            if r['sprite']is None:self.assertEqual(p['m_PathID'],0)
        self.assertEqual(c,{'all':62815,'null':951,'nonnull':61864})

    def test_measured_coverage_is_not_global_unused_or_all_consumers(self):
        rows=list(r for _,_,r in iter_arrays(OUTPUT,{'sprites'}));self.assertEqual(len(rows),2185)
        n=sum(r['native_renderer_count']>0 for r in rows);anyref=sum(r['coverage']=='SCOPED_STATIC_REFERENCE_FOUND' for r in rows)
        self.assertEqual((n,anyref),(1802,1897));self.assertEqual(len(rows)-anyref,288)
        for r in rows:
            self.assertIsNone(r['meaning_label'])
            if not r['native_renderer_count'] and not r['captured_additional_references']:self.assertIn('NOT_GLOBAL_UNUSED',r['coverage'])

    def test_every_reverse_native_id_has_matching_original_target(self):
        expected={}
        for r,_ in native_rows(json.loads(INDEX.read_bytes())):
            if r['sprite']:expected[key(r['identity'])]=key(r['sprite']['identity'])
        count=0
        for _,_,s in iter_arrays(OUTPUT,{'sprites'}):
            for file,ids in s['native_renderer_ids_by_file'].items():
                for pid in ids:self.assertEqual(expected.pop((file,pid)),key(s['identity']));count+=1
        self.assertEqual(count,61864);self.assertEqual(expected,{})

    def test_summary_distinguishes_capture_overlap_and_categories(self):
        s=next(r for _,_,r in iter_arrays(OUTPUT,{'summary'}));self.assertEqual(s['counts']['captured_native_owner_hash_matches'],26452);self.assertEqual(s['counts']['captured_native_sprite_edge_matches'],25998)
        self.assertEqual(s['captured_additional_reference_categories'],{'SERIALIZED_COMPONENT_REFERENCE':3990,'ANIMATION_MAPPING_NOT_ACTIVE_SELECTION':892,'ATLAS_MEMBERSHIP_NOT_USAGE':1450})
        self.assertEqual(s['captured_context_status'],{'COMPLETE_CAPTURED_PARENT_CHAIN':19263,'PARTIAL_CAPTURED_PARENT_CHAIN':7189,'CAPTURED_TRANSFORM_ABSENT':36363})

    def test_exact_query_probes_and_panel_info_not_name_assignment(self):
        r=sprite_probe('resources.assets',3564);self.assertEqual(r['name'],'Panel_Info');self.assertEqual(r['native_renderer_count'],14)
        owner_file=next(iter(r['native_renderer_ids_by_file']));pid=r['native_renderer_ids_by_file'][owner_file][0]
        native=renderer_probe(owner_file,pid);self.assertEqual(key(native['sprite']['identity']),key(r['identity']));self.assertIn('raw_location',native)
        with self.assertRaises(ValueError):sprite_probe('other.assets',3564)
        with self.assertRaises(ValueError):renderer_probe('other.assets',pid)

    def test_atlas_animation_component_categories_are_not_equated(self):
        self.assertEqual(reference_category('SpriteAtlas',None),'ATLAS_MEMBERSHIP_NOT_USAGE')
        self.assertEqual(reference_category('AnimationClip',None),'ANIMATION_MAPPING_NOT_ACTIVE_SELECTION')
        self.assertEqual(reference_category('MonoBehaviour','data.unity3d/a'),'SERIALIZED_COMPONENT_REFERENCE')
        self.assertEqual(reference_category('MonoBehaviour',None),'SERIALIZED_ASSET_REFERENCE')

    def test_owner_qualified_pointer_resolution_not_bare_pid(self):
        ext={'data.unity3d/a':[dict(path='b')]}
        self.assertEqual(resolve('data.unity3d/a',dict(m_FileID=0,m_PathID=12),ext),('data.unity3d/a',12))
        self.assertEqual(resolve('data.unity3d/a',dict(m_FileID=1,m_PathID=12),ext),('data.unity3d/b',12))
        self.assertIsNone(resolve('data.unity3d/a',dict(m_FileID=0,m_PathID=0),ext))
        with self.assertRaises(ValueError):resolve('data.unity3d/a',dict(m_FileID=2,m_PathID=12),ext)

    def test_captured_parent_chain_uses_exact_ids_not_names(self):
        with context_db() as d:
            put(d,1,'GameObject',name='same');put(d,2,'Transform',go=1,parent=4);put(d,3,'GameObject',name='same');put(d,4,'Transform',go=3)
            d.execute('INSERT INTO cap_aliases VALUES(?,?,?,?,?)',('data.unity3d/a',3,'resource','prefabs/example',canonical(['test']).decode()))
            c=context(d,fresh());self.assertEqual(c['status'],'COMPLETE_CAPTURED_PARENT_CHAIN');self.assertEqual(c['root_aliases'][0]['gameobject']['path_id'],3)
            self.assertEqual([r['identity']['path_id'] for r in c['source_path']],[3,1])

    def test_missing_captured_transform_does_not_get_guessed_root(self):
        with context_db() as d:
            put(d,1,'GameObject',name='Boss');put(d,99,'GameObject',name='Boss')
            d.execute('INSERT INTO cap_aliases VALUES(?,?,?,?,?)',('data.unity3d/a',99,'resource','prefabs/Boss',canonical(['test']).decode()))
            c=context(d,fresh());self.assertEqual(c['status'],'CAPTURED_TRANSFORM_ABSENT');self.assertEqual(c['root_aliases'],[])

    def test_direct_alias_stays_exact_even_without_parent_capture(self):
        with context_db() as d:
            put(d,1,'GameObject',name='root');d.execute('INSERT INTO cap_aliases VALUES(?,?,?,?,?)',('data.unity3d/a',1,'resource','prefabs/root',canonical(['test']).decode()))
            c=context(d,fresh());self.assertEqual(c['status'],'CAPTURED_TRANSFORM_ABSENT');self.assertEqual(c['root_aliases'][0]['gameobject']['path_id'],1)

    def test_context_hash_disagreement_is_not_repaired(self):
        with context_db() as d:
            put(d,1,'GameObject',name='X',sha='different')
            with self.assertRaises(ValueError):context(d,fresh())

    def test_parent_cycle_is_scoped_not_invented_ancestry(self):
        with context_db() as d:
            put(d,1,'GameObject',name='X');put(d,2,'Transform',go=1,parent=2)
            self.assertEqual(context(d,fresh())['status'],'CAPTURED_PARENT_CYCLE')

    def test_native_transform_to_wrong_go_is_rejected(self):
        with context_db() as d:
            put(d,1,'GameObject',name='X');put(d,3,'GameObject',name='Y');put(d,2,'Transform',go=3)
            with self.assertRaises(ValueError):context(d,fresh())


if __name__=='__main__':unittest.main()
