"""#8 complete original-byte models and real default meshes, bounded fixtures.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from copy import deepcopy
from contextlib import redirect_stdout
import io
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.verify.geometry_8141386a_atlas_io import sha,canonical
from tools.verify.geometry_8141386a_gaps_sources import RAW
from tools.verify.geometry_8141386a_gaps_models import load as models_load,check as models_check,declared_fields,Schemas
from tools.verify.l3_geometry_8141386a_gaps_binary import decode_object,encode
import tools.verify.l3_geometry_8141386a_gaps as gaps


def fixtures():
    w=json.loads(gzip.decompress(gaps.WITNESS.read_bytes()));m=models_load()
    return w,{(r['namespace'],r['class_name']):r for r in m['schemas']}


def decoded(pid):
    w,m=fixtures();o=next(o for o in w['header_objects'] if o['identity']['path_id']==pid)
    return decode_object(o,m[o['namespace'],o['class_name']])


class GapsActual(unittest.TestCase):
    def test_artifact_reproduction_and_all_requested_groups(self):
        v=gaps.build();self.assertEqual(v,json.loads(gzip.decompress(gaps.OUTPUT.read_bytes())))
        s=v['summary'];self.assertEqual(s['fresh_original_component_hashes'],57);self.assertEqual(s['complete_supplied_model_roundtrips'],5)
        self.assertEqual(s['fresh_monobehaviour_bytes'],3444);self.assertEqual(s['custom_payload_bytes'],3284);self.assertEqual(s['typed_mb_root_spans'],76)
        self.assertEqual(s['resolved_original_mesh_refs'],52);self.assertEqual(s['mesh_vertices'],149);self.assertEqual(s['mesh_indices'],642)

    def test_csharp_model_reproduces_without_managed_sdk(self):
        with redirect_stdout(io.StringIO()):models_check()

    def test_all_five_full_extents_inverse_equal_original_and_typed_spans(self):
        w,m=fixtures()
        for o in w['header_objects']:
            p=decode_object(o,m[o['namespace'],o['class_name']]);blob=bytes.fromhex(o['original_hex'])
            self.assertTrue(p['inverse_byte_equal']);self.assertEqual(p['fully_consumed_bytes'],len(blob))
            self.assertEqual(encode(m[o['namespace'],o['class_name']]['schema'],p['tree']),blob)
            for r in p['typed_root_spans']:self.assertEqual(r['sha256'],sha(blob[r['offset']:r['offset']+r['size']]))
            self.assertIsNone(p['runtime_state']);self.assertIsNone(p['native_consumer'])

    def test_gun_event_keeps_actual_poision_spelling_not_invocation(self):
        p=decoded(627827);calls=p['tree']['onDestroy']['m_PersistentCalls']['m_Calls'];self.assertEqual(len(calls),1)
        c=calls[0];self.assertEqual(c['m_MethodName'],'OnSpawnPoisionZone');self.assertEqual(c['m_Target']['m_PathID'],692605)
        self.assertEqual(c['m_TargetAssemblyTypeName'],'GunBurstWithPoision, Assembly-CSharp');self.assertEqual(c['m_Mode'],0);self.assertEqual(c['m_CallState'],2)
        self.assertIsNone(p['native_consumer'])

    def test_player_fields_native_gradients_and_serialized_flags(self):
        for pid,demo,enabled in ((629716,False,1),(688329,False,0),(704560,True,1)):
            p=decoded(pid);t=p['tree'];self.assertEqual(t['id'],10002);self.assertEqual(t['demo'],demo);self.assertEqual(t['m_Enabled'],enabled)
            self.assertEqual(t['lerpAngle'],30.0);self.assertEqual(t['radiusCheck'],6.0);self.assertEqual(t['targetLayer']['m_Bits'],512)
            for name,offset in (('colorGraNormal',88),('colorGraSuper',252)):
                s=next(s for s in p['typed_root_spans'] if s['field']==name);self.assertEqual((s['offset'],s['size']),(offset,164))
            self.assertNotIn('timeToShot',t);self.assertNotIn('normalLifetime',t)

    def test_boss_nested_arrays_are_not_fake_empty_defaults(self):
        p=decoded(689449);t=p['tree']
        self.assertEqual([len(t[k]) for k in ('allDataFixedAttack','allDataAttackAuto','allDataAttackAutoCircle','allDataAttackArrangePosition','allDataAttackRandomPositionX')],[8,2,4,2,0])
        self.assertEqual(len(t['pointDrop']),2);self.assertEqual(len(t['offsetY']),3)
        self.assertEqual(t['polygon'],{'m_FileID':0,'m_PathID':700020});self.assertEqual(p['object_size'],2012)

    def test_real_meshes_and_plane_tiny_y_are_preserved(self):
        v=gaps.build();m={r['path_id']:r for r in v['meshes']};self.assertEqual(set(m),{10202,10209,10210})
        p=m[10209];self.assertEqual(p['name'],'Plane');self.assertEqual(p['geometry']['vertex_count'],121);self.assertEqual(p['geometry']['index_count'],600)
        self.assertEqual(p['geometry']['minimum'],[-5.,-1.1102230246251565e-16,-5.]);self.assertEqual(p['geometry']['maximum'],[5.,1.1102230246251565e-16,5.])
        self.assertEqual(v['summary']['mesh_bytes'],9844);self.assertEqual(v['summary']['original_mesh_pointer_bytes'],624)

    def test_pointer_and_fresh_script_crosschecks_are_scoped(self):
        v=gaps.build();self.assertEqual(v['summary']['modeled_pointer_status'],{'CAPTURED_TYPE_COMPATIBLE':54,'FRESH_ORIGINAL_MONOSCRIPT_IDENTITY':5,'NULL_SERIALIZED_POINTER':1})
        self.assertEqual(v['summary']['fresh_original_monoscript_bytes'],304)
        b=next(r for r in v['header_models'] if r['identity']['path_id']==689449)
        self.assertEqual(b['script_binding']['identity'],{'serialized_file':'data.unity3d/globalgamemanagers.assets','path_id':946})
        self.assertEqual(b['script_binding']['class_name'],'Boss19_AttackTypes')

    def test_corrupt_original_or_supplied_schema_pin_fails(self):
        w,m=fixtures();o=deepcopy(w['header_objects'][0]);s=deepcopy(m[o['namespace'],o['class_name']]);o['original_hex']='ff'+o['original_hex'][2:]
        with self.assertRaises(ValueError):decode_object(o,s)
        o=w['header_objects'][0];s['schema_sha256']='0'*64
        with self.assertRaises(ValueError):decode_object(o,s)

    def test_full_extent_and_noncanonical_bool_are_required(self):
        w,m=fixtures();o=deepcopy(next(o for o in w['header_objects'] if o['identity']['path_id']==629716));s=m[o['namespace'],o['class_name']]
        b=bytearray.fromhex(o['original_hex']);b[36]=2;o['original_hex']=b.hex();o['object_sha256']=sha(b)
        with self.assertRaises(ValueError):decode_object(o,s)
        o=deepcopy(next(o for o in w['header_objects'] if o['identity']['path_id']==629716));b=bytes.fromhex(o['original_hex'])+b'\0'*4;o.update(original_hex=b.hex(),object_sha256=sha(b));o['entry']['byte_size']=len(b)
        with self.assertRaises(ValueError):decode_object(o,s)

    def test_serialized_field_selection_is_explicit_not_memory_offsets(self):
        d=dict(text='// Fields\npublic int keep; // 0xF000\nprivate int runtimeOnly; // 0x2\n[SerializeField]\nprivate bool chosen; // 0xA000\npublic static int ignore; // 0x0\n// Methods\n')
        self.assertEqual([(f['name'],f['type']) for f in declared_fields(d)],[('keep','int'),('chosen','bool')])
        d['text']='// Fields\n[SerializeReference]\nprivate object cannotGuess; // 0x20\n// Methods\n'
        with self.assertRaises(ValueError):declared_fields(d)

    def test_ambiguous_inline_type_is_not_guessed(self):
        s=Schemas({('A','Foo'):{},('B','Foo'):{}},{})
        with self.assertRaises(ValueError):s.resolve('Foo','C')

    def test_raised_budget_output_cannot_be_accepted(self):
        s=json.loads(gzip.decompress(gaps.SCHEMAS.read_bytes()));c=json.loads(gzip.decompress(gaps.CI.read_bytes()))
        s['results'][0]['budget_stop']='CHILD_RSS_BUDGET_850MiB'
        with tempfile.TemporaryDirectory() as d:
            sp=Path(d)/'s.gz';cp=Path(d)/'c.gz';sp.write_bytes(gzip.compress(canonical(s),mtime=0));c['schema_witness_sha256']=sha(sp.read_bytes());cp.write_bytes(gzip.compress(canonical(c),mtime=0))
            with patch.object(gaps,'SCHEMAS',sp),patch.object(gaps,'CI',cp):
                with self.assertRaises(ValueError):gaps.build()

    def test_no_runtime_or_native_schema_discovery_acceptance(self):
        v=gaps.build()
        self.assertIn('NOT_ENGINE_SCHEMA_DISCOVERY',v['status']);self.assertFalse(v['group_conclusions'][1]['native_schema_discovery'])
        self.assertEqual(v['budget_boundary']['threshold_mib'],600)
        for r in v['default_mesh_references']:self.assertIsNone(r['runtime_use']);self.assertIsNone(r['world_bounds'])


if __name__=='__main__':unittest.main()
