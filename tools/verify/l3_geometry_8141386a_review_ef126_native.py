"""Separate R1/122 guarded caller harness, driven only by own fresh original spans.
provenance: arena/8141386a-windwings-space-shooter-game-p
No producer126 verifier/Fixture import/execution. Same Unicorn backend and disclosed
prepared-input protocol. Graph builder and two virtual implementations are explicit
synthetic sinks; inherited N2 IDs are host-service observations, not native discovery.
"""
from __future__ import annotations

from collections import Counter
import gzip
import json
import struct
from tools.verify.geometry_8141386a_atlas_io import ROOT, sha, sha_file

RAW = ROOT / 'reverse-engineering/raw/geometry-8141386a/review-ef126'
SOURCE_HEAD = 'a2d299605c06a3657a251b5bae4fd7314c4e1bd7'
SOURCE_RUN = 40399243691
UNITY = 'd827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7'
TARGET = 0x6cf7b4
SET = 0x6cef64
REBUILD = 0x6cefdc
NATIVE_ENTRIES = {SET, REBUILD, 0x6d6bf8, 0x6cf768, 0x5710ec}
CASES = ('set_full', 'set_equal', 'rebuild', 'set_null')


def read(name):
    return json.loads(gzip.decompress((RAW / name).read_bytes()))


def source_image():
    fresh = read('fresh-original.json.gz'); receipt = read('source-ci-receipt.json.gz')
    run = receipt['run']
    if (run['id'], run['head_sha'], run['status'], run['conclusion']) != (SOURCE_RUN, SOURCE_HEAD, 'completed', 'success'):
        raise ValueError('own fresh original recovery is not exact-source GREEN')
    if sha_file(RAW / 'fresh-original.json.gz') != receipt['fresh_original_sha256'] or fresh['libunity_sha256'] != UNITY:
        raise ValueError('fresh original source identity changed')
    memory = {}
    for row in fresh['peer_selected_spans']:
        data = bytes.fromhex(row['hex'])
        if len(data) != row['size'] or sha(data) != row['sha256']:
            raise ValueError('fresh original span hash/size changed')
        for i, byte in enumerate(data):
            address = row['va'] + i
            if address in memory and memory[address] != byte:
                raise ValueError('conflicting original-byte overlap')
            memory[address] = byte
    fdes = {r['start']: r for r in fresh['selected_fdes']}
    allowed = {pc for a in NATIVE_ENTRIES for pc in range(a, fdes[a]['end_exclusive'], 4)}
    return memory, allowed, fresh


def replay(case='set_full', base=0x3000000, *, drop_instruction=None, graph_sink=True, fault_unprepared_chunk=False):
    from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, UC_MEM_READ
    from unicorn import arm64_const as reg
    if case not in CASES or base not in (0x3000000, 0x4000000):
        raise ValueError('outside declared bounded caller inputs')
    original, allowed_pcs, fresh = source_image()
    if drop_instruction is not None:
        for i in range(4):
            original.pop(drop_instruction+i, None)
    u = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    u.mem_map(0, 0x1200000); u.mem_map(base, 0x100000)
    start = previous = None; block = bytearray()
    for address in sorted(original):
        if previous is not None and address != previous + 1:
            u.mem_write(start, bytes(block)); block.clear(); start = None
        if start is None:
            start = address
        block.append(original[address]); previous = address
    if block:
        u.mem_write(start, bytes(block))

    def put(a, b): u.mem_write(a, b)
    def q(a, value): put(a, struct.pack('<Q', value))
    def w(a, value): put(a, struct.pack('<I', value & 0xffffffff))
    def rq(a): return struct.unpack('<Q', u.mem_read(a, 8))[0]
    def rw(a): return struct.unpack('<I', u.mem_read(a, 4))[0]
    def x(i): return u.reg_read(getattr(reg, 'UC_ARM64_REG_X' + str(i)))
    def ret_zero():
        u.reg_write(reg.UC_ARM64_REG_X0, 0)
        u.reg_write(reg.UC_ARM64_REG_PC, x(30))

    a = dict(controller=base+0x4000, owner=base+0x5000, chunk=base+0x6000,
        slots=base+0x6100, child=base+0x6200, controller_vtable=base+0x7000,
        owner_vtable=base+0x7100, e0=base+0x7300, d8=base+0x7310,
        memset=base+0x7320, fail=base+0x7330, service=base+0x7400,
        tls=base+0x7500, sentinel=base+0x7600, stop=base+0x1fff0)
    prepared = [(base, base+0x20000), (0x116cb40, 0x116cb48)]
    for lo, hi in prepared:
        put(lo, bytes(hi-lo))
    c, owner = a['controller'], a['owner']
    q(c, a['controller_vtable']); q(c+0x20, a['child']); q(c+0x30, a['chunk'])
    if fault_unprepared_chunk:
        # Negative guard probe only: a mapped zero page is NOT source/prepared data.
        q(c+0x30, 0x100000)
    q(c+0x118, owner if case == 'set_equal' else a['sentinel'])
    q(a['chunk']+0x40, a['slots']); q(a['chunk']+0x50, 1); q(a['chunk']+0x58, 8)
    q(a['controller_vtable']+0xe0, a['e0']); q(a['owner_vtable']+0xd8, a['d8'])
    n2 = read('peer-n2-artifact.json.gz')['serialized_owner']
    ctl, comp, hierarchy = n2['controller'], n2['animator_component'], n2['hierarchy']
    identity = [ctl['path_id'], comp['component_path_id'], comp['gameobject_ref']['m_PathID'],
                hierarchy['parent_chain_child_to_root'][-1]['gameobject_path_id'],
                comp['controller_ref']['m_FileID'], comp['controller_ref']['m_PathID'], hierarchy['transform_path_id']]
    if identity != [1856, 493584, 76852, 73241, 0, 1856, 364641]:
        raise ValueError('inherited published N2 identity differs')
    q(owner, a['owner_vtable'])
    for offset, value in enumerate(identity, 1): q(owner+8*offset, value)
    for i, parent in enumerate(hierarchy['parent_chain_child_to_root']):
        q(owner+0x40+i*16, parent['father_transform_path_id'])
        q(owner+0x48+i*16, parent['gameobject_path_id'])
    q(0x116cb40, a['service']); q(a['tls']+0x28, 0x1122334455667788)
    u.reg_write(reg.UC_ARM64_REG_TPIDR_EL0, a['tls'])
    imports = {r['address']: r['name'] for r in fresh['imports']}
    if imports.get(0x10e3d00) != '__stack_chk_fail' or imports.get(0x10e3d10) != 'memset':
        raise ValueError('fresh original import binding differs')
    q(0x10e3d00, a['fail']); q(0x10e3d10, a['memset'])
    patched = set(range(0x10e3d00, 0x10e3d08)) | set(range(0x10e3d10, 0x10e3d18))
    visits = []; reads = []; writes = []; graph = []; virtual = []; host_identity = []
    stopped = False

    def code(cpu, pc, size, _):
        nonlocal stopped
        if pc == a['stop']:
            stopped = True; cpu.emu_stop(); return
        if pc == TARGET:
            if not graph_sink:
                raise ValueError('graph-builder body prohibited: explicit sink disabled')
            caller = x(30)-4
            if caller not in (0x6cef84, 0x6cefe4) or not visits or visits[-1] != caller:
                raise ValueError('graph-builder sink reached without the declared original BL')
            graph.append(dict(call_pc=caller, x0=x(0), x1=x(1), x2=x(2), x3=x(3)&0xffffffff))
            ret_zero(); return
        if pc in (a['e0'], a['d8']):
            branch_pc = visits[-1]
            if pc == a['e0']:
                if branch_pc not in (0x6cef94, 0x6ceff8) or x(0) != c:
                    raise ValueError('controller virtual service outside declared protocol')
                role = 'rebuild_notify' if branch_pc == 0x6cef94 else 'rebuild_notify_tail'
            else:
                if branch_pc != 0x6cefb0 or x(0) != owner:
                    raise ValueError('owner virtual service outside declared protocol')
                role = 'owner_release'
                # Host reads below are explicit service instrumentation; they are NOT
                # UC/native memory reads and do not prove a native N2 object layout.
                host_identity.append(dict(origin='PYTHON_SYNTHETIC_D8_SERVICE_ONLY',
                    controller_path=rq(owner+8), component_path=rq(owner+16),
                    gameobject_path=rq(owner+24), root_gameobject=rq(owner+32),
                    controller_ref_path=rq(owner+48)))
            virtual.append(dict(pc=branch_pc, target=pc, object=x(0), kind=role))
            ret_zero(); return
        if pc in (a['memset'], a['fail']) or 0x109acc0 <= pc < 0x109acf0:
            raise ValueError('excluded PLT/service/failure path reached')
        if pc == 0x57112c or pc not in allowed_pcs:
            raise ValueError('outside selected original caller/helper/tail domain: ' + hex(pc))
        if size != 4 or not all(pc+i in original for i in range(size)):
            raise ValueError('uncaptured original instruction: ' + hex(pc))
        visits.append(pc)

    def memory(cpu, access, address, size, value, _):
        synthetic = any(lo <= address and address+size <= hi for lo, hi in prepared)
        pc = cpu.reg_read(reg.UC_ARM64_REG_PC)
        if access == UC_MEM_READ:
            if not synthetic and not all(address+i in original or address+i in patched for i in range(size)):
                raise ValueError('uncaptured/unprepared native data read: ' + hex(address))
            reads.append(dict(pc=pc, address=address, size=size,
                              tier='PREPARED_STATE' if synthetic else 'ORIGINAL_OR_EXPLICIT_IMPORT_CELL'))
        else:
            if not synthetic:
                raise ValueError('native write outside prepared state: ' + hex(address))
            writes.append(dict(pc=pc, address=address, size=size, value=value & ((1 << (size*8))-1)))

    u.hook_add(UC_HOOK_CODE, code)
    u.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, memory)
    entry = REBUILD if case == 'rebuild' else SET
    u.reg_write(reg.UC_ARM64_REG_X0, c)
    u.reg_write(reg.UC_ARM64_REG_X1, 0 if case == 'set_null' else owner)
    for i in range(2, 6): u.reg_write(getattr(reg, 'UC_ARM64_REG_X'+str(i)), 0)
    sp = base+0x1f000
    u.reg_write(reg.UC_ARM64_REG_SP, sp); u.reg_write(reg.UC_ARM64_REG_X30, a['stop'])
    u.emu_start(entry, a['stop']+4, count=10000)
    if not stopped or u.reg_read(reg.UC_ARM64_REG_PC) != a['stop'] or u.reg_read(reg.UC_ARM64_REG_SP) != sp:
        raise ValueError('caller did not terminate with original stack restoration at explicit fixture stop')
    if rq(a['tls']+0x28) != 0x1122334455667788:
        raise ValueError('prepared TLS canary changed')
    hits = Counter(visits)
    return dict(case=case, base=base, entry=entry, addresses=a, last_native_pc=visits[-1],
        termination_kind='INDIRECT_TAIL_BRANCH_TO_SYNTHETIC_E0' if case == 'rebuild' else 'ORIGINAL_RET',
        native_instruction_count=len(visits), executed_addresses=sorted(hits),
        pc_counts={hex(pc): n for pc, n in sorted(hits.items())}, graph_builder_sinks=graph,
        virtual_services=virtual, synthetic_d8_identity_observations=host_identity,
        import_services_called=[], native_memory_reads=reads, native_memory_writes=writes,
        return_value=x(0), stack_pointer_after=u.reg_read(reg.UC_ARM64_REG_SP), stop_pc=u.reg_read(reg.UC_ARM64_REG_PC),
        node_after=dict(slot118=rq(c+0x118), byte102=bytes(u.mem_read(c+0x102,1))[0],
            byte103=bytes(u.mem_read(c+0x103,1))[0], flags38=rw(c+0x38), halfword_a8=struct.unpack('<H',u.mem_read(c+0xa8,2))[0]),
        boundary='Original caller/helper/tail instructions on explicitly shared prepared state. Builder/E0/D8 are uncounted synthetic sinks; identity IDs observed by Python D8 service, not native discovery. No original graph-body/heap/serialized game-instance/Unity/Android/runtime proof.')
