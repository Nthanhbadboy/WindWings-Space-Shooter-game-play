import json
import unittest
from tools.verify.combat_rate_consumers import OUT, build, owner_states


class RateConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = build()
        cls.ships = cls.audit['ships']

    def test_regeneration(self):
        self.assertEqual(self.audit, json.loads(OUT.read_text()))

    def test_all_24_named_fields_and_demo_selection(self):
        self.assertEqual(len(self.ships),24)
        for i,s in enumerate(self.ships,1):
            self.assertEqual(s['rate_field']['name'],'timeRateMainCannon')
            self.assertEqual(s['demo_field']['name'],'demo')
            self.assertEqual(s['setup']['demo_constant'],4.0 if i == 24 else 3.0)
            self.assertEqual(s['deadline_field']['name'],'timeToShotMainCannon')

    def test_96_accesses_two_reads_two_writes_each(self):
        for s in self.ships:
            accesses = s['rate_accesses']
            self.assertEqual(len(accesses),4)
            self.assertEqual({a['method'].rsplit('.',1)[1] for a in accesses if a['op'].startswith('ld')},{'MainCannonShoot','StartAttack'})
            self.assertEqual({a['method'].rsplit('.',1)[1] for a in accesses if a['op'].startswith('st')},{'SetupDatas','ctor'})

    def test_overlapping_constructor_write_is_not_lost(self):
        s = self.ships[3]
        ctor = next(a for a in s['rate_accesses'] if a['method'].endswith('.ctor'))
        self.assertEqual(ctor['access_start'],'0x8c')
        self.assertEqual(ctor['access_bytes'],8)
        self.assertEqual(s['rate_field']['offset'],'0x90')

    def test_scheduler_exception_and_refresh_are_not_generalized(self):
        self.assertEqual([i for i,s in enumerate(self.ships,1) if s['scheduler_kind']=='single_deadline'],[19])
        self.assertEqual([i for i,s in enumerate(self.ships,1) if s['ability_refresh_inside_scheduler']],[22,23,24])

    def test_extra_counter_branch_goes_to_dispatch_not_return(self):
        for s in self.ships:
            if s['scheduler_kind']=='single_deadline': continue
            p=s['scheduler_prefix']
            store = int(p[-1]['at'],16)
            self.assertTrue(any(i['op']=='b.le' and int(i['operands'][1:],16)==store+4 for i in p))
            rate_load = next(int(j['at'],16) for j in p if j['op']=='ldr' and j['operands']==f"s1, [x19, #{s['rate_field']['offset']}]")
            self.assertTrue(any(i['op']=='b.lt' and int(i['operands'][1:],16)==rate_load for i in p))

    def test_coroutine_inventory_is_separate_from_rate(self):
        self.assertEqual(sum(len(s['nested_move_next']) for s in self.ships),25)
        self.assertEqual(sum(len(s['wait_for_seconds_sites']) for s in self.ships),14)
        for i in (9,10,11,13,14,17,23):
            self.assertTrue(any(d['symbol']=='MonoBehaviour.StartCoroutine(IEnumerator)' for d in self.ships[i-1]['dispatch']))

    def test_callee_saved_owner_survives_call_but_x0_does_not(self):
        b={0:('mov','x19, x0'),4:('bl','#0x100'),8:('ldr','s0, [x19, #0x80]'),12:('ret','')}
        s=owner_states(b,0)[8]
        self.assertEqual(s[19],'owner'); self.assertIsNone(s[0])

    def test_conflicting_branch_alias_is_not_owner(self):
        b={0:('cbz','w1, #0xc'),4:('mov','x19, x0'),8:('b','#0x10'),12:('mov','x19, x2'),16:('ret','')}
        self.assertIsNone(owner_states(b,0)[16][19])

    def test_w_alias_and_pair_load_destroy_pointer(self):
        for op,args in [('mov','w19, w0'),('ldp','x20, x19, [sp]')]:
            b={0:('mov','x19, x0'),4:(op,args),8:('ret','')}
            self.assertIsNone(owner_states(b,0)[8][19])

    def test_typed_iterator_owner_recovery(self):
        b={0:('mov','x19, x0'),4:('ldr','x20, [x19, #0x28]'),8:('ret','')}
        self.assertEqual(owner_states(b,0,0x28)[8][20],'owner')
        self.assertIsNone(owner_states(b,0,0x20)[8][20])

    def test_writeback_destroys_base_alias(self):
        b={0:('mov','x19, x0'),4:('str','x2, [x19, #0x8]!'),8:('ret','')}
        self.assertIsNone(owner_states(b,0)[8][19])
