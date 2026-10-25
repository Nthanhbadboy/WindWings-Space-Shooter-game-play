"""Pinned static audio evidence. Explicit RVA IDs avoid overloaded-name collisions."""
import gzip
import csv
import io
import hashlib
import json
from pathlib import Path
import re
from ui_loader_analysis import metadata_loads
from ui_routing import direct_calls

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw'


def effective_volume(mute_stored, value=None, default=0.3):
    """One normal getter observation; float pool values are decimal approximations."""
    return 0.0 if mute_stored==1 else default if value is None else value


def source_busy(time, is_playing):
    return time>0 or is_playing


def build():
    sources=[]
    def load(path):
        content=path.read_bytes()
        if path.suffix=='.gz':content=gzip.decompress(content)
        sources.append(dict(path=str(path.relative_to(ROOT)),sha256_decompressed=hashlib.sha256(content).hexdigest()))
        return content
    dump=load(ROOT/'reverse-engineering/il2cpp/dump.cs.gz').decode()
    declarations={};by_rva={}
    for block in re.split(r'(?=// Namespace:)',dump):
        cls=re.search(r'(?:class|enum) ([^ :\n]+)',block)
        if cls:
            declarations[cls[1]]=block
            for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)',block):
                by_rva[int(m[1],16)]=dict(class_name=cls[1],signature=m[2].strip())
    relocation=json.loads(load(RAW/'ui-audit/native-relocations.json.gz'))['relocations']
    metadata={}
    for group,rows in json.loads(load(RAW/'ui-audit/metadata-index.json.gz'))['tables'].items():
        for row in rows:metadata.setdefault(row['Address'],[]).append(dict(row,group=group))
    manifest=json.loads(load(RAW/'audio-rules/index.json'))
    for source in manifest['files']:
        path=ROOT/source['path'];data=path.read_bytes()
        if path.suffix=='.gz':data=gzip.decompress(data)
        assert hashlib.sha256(data).hexdigest()==source['sha256_decompressed']
    assert sources[0]['sha256_decompressed']==manifest['dump_sha256_decompressed']
    records=[]
    def add_file(path,only_audio_calls=False):
        text=load(path).decode()
        inventory=json.loads(load(path.with_name(path.name.replace('.asm.txt','.json'))))
        sections={re.search(r'\b(0x[\da-f]+):',s)[1]: ';;; '+s for s in text.split(';;; ')[1:]}
        for inv in inventory['methods']:
            asm=sections[inv['rva']]
            calls=direct_calls(asm,by_rva)
            if only_audio_calls and not any(c['declaration'] and c['declaration']['class_name']=='AudioManager' for c in calls):continue
            assert not inv['size_capped']
            assert asm.splitlines()[0]==';;; '+inv['method']+'  '+inv['signature']
            records.append(dict(id=f"{inventory['class']}.{inv['method']}@{inv['rva']}",class_name=inventory['class'],method=inv['method'],asm=asm,inventory=inv,
                calls=calls,metadata_loads=metadata_loads(asm,relocation,metadata),source=str(path.relative_to(ROOT))))
    for path in sorted((RAW/'audio-rules/native').glob('*.asm.txt')):add_file(path)
    callers=[('il2cpp-consts','Boss1_Director._WarningBossAppear_d__15'),('il2cpp-consts','Player_Health'),
        ('ui-audit/extra-native','Home_Loader._Start_d__5'),('ui-audit/extra-native','GP_Endgame._MovePlayer_d__10'),
        ('ui-audit/extra-native','Machine_Gun_Attack')]
    for folder,cls in callers:add_file(RAW/folder/(cls+'.asm.txt'),True)
    names={name:int(number) for name,number in re.findall(r'public const AllClipName (\w+) = (-?\d+);',declarations['AllClipName'])}
    registry=[json.loads(line) for line in load(RAW/'typetrees/SoundClip.jsonl.gz').decode().splitlines() if line]
    legacy_exports=list(csv.DictReader(io.StringIO(load(RAW/'asset-pack/manifest-full.csv').decode('utf-8-sig'))))
    audio_exports={}
    for row in legacy_exports:
        if row['type']=='AudioClip':audio_exports.setdefault(int(row['path_id']),[]).append(row)
    lookup={(r['class_name'],r['method'],r['inventory']['rva']):r for r in records}
    def method(cls,name,rva=None):
        found=[r for (c,n,a),r in lookup.items() if c==cls and n==name and (rva is None or a==rva)]
        assert len(found)==1,(cls,name,rva)
        return found[0]
    def has(cls,name,*parts):return all(p in method(cls,name)['asm'] for p in parts)
    def strings(cls,name):return {v['Value'] for m in method(cls,name)['metadata_loads'] for v in m['records'] if v['group']=='ScriptString'}
    def float_at(name,address):return next(c['value'] for c in method('AudioManager',name)['inventory']['constants'] if c['kind']=='float' and c.get('va')==address)
    checks={
        'all_methods_have_unique_rva_qualified_ids':len({r['id'] for r in records})==len(records),
        'both_GetAudioSource_overloads_preserved':len([r for r in records if r['class_name']=='AudioManager' and r['method']=='GetAudioSource'])==2,
        'mute_key_default_zero_exact_one':strings('AudioManager','get_Mute')=={'MUTE_AUDIO'} and has('AudioManager','get_Mute','0x15b52d4: mov      w1, wzr','0x15b52e4: cmp      w0, #1'),
        'mute_writer_persists_boolean_only_in_selected_body':has('AudioManager','set_Mute','0x15b5354: and      w1, w19, #1','0x15b536c: b        #0x13f1a04'),
        'volume_sound_key_default_pool':strings('AudioManager','get_VolumeSound')=={'VolumeSound'} and float_at('get_VolumeSound','0x756dd4')==0.73,
        'volume_music_key_default_pool':strings('AudioManager','get_VolumeMusic')=={'VolumeMusic'} and float_at('get_VolumeMusic','0x7570e0')==0.3,
        'mute_returns_zero_without_reading_volume_key':has('AudioManager','get_VolumeSound','0x15b5644: fmov     s0, wzr') and has('AudioManager','get_VolumeMusic','0x15b5804: fmov     s0, wzr'),
        'pause_uses_AudioListener':has('AudioManager','get_Pause','0x15b5a58: b        #0x275a760') and has('AudioManager','set_Pause','0x15b5a64: b        #0x275a788'),
        'oneshot_configure_nonloop_before_play':has('AudioManager','PlayOneShot','0x15b5154: mov      w1, wzr','0x15b515c: bl       #0x275ab9c','0x15b5160: bl       #0x15b560c','0x15b5180: bl       #0x275aa24'),
        'music_none_skips_new_source':has('AudioManager','StartSmoothMusic','0x15b5d98: cbz      w19, #0x15b5e58','0x15b5ed0: fmov     s8, wzr'),
        'music_loop_and_ignore_listener_pause':has('AudioManager','StartSmoothMusic','0x15b5da8: mov      w1, #1','0x15b5db0: bl       #0x15b5f38','0x15b5dd0: mov      w1, #1','0x15b5dd8: bl       #0x275ac24','0x15b5e54: bl       #0x275a9e4'),
        'crossfade_increment_and_null_yield':has('AudioManager.<SmoothMusic>d__32','MoveNext','0x15b6748: fadd     s0, s0, s1','0x15b6828: str      xzr, [x19, #0x18]') and any(c.get('va')=='0x756fe0' and c.get('value')==0.01 for c in method('AudioManager.<SmoothMusic>d__32','MoveNext')['inventory']['constants']),
        'free_predicate_time_or_isPlaying':has('AudioManager.<>c__DisplayClass27_0','<DelayFreeSource>b__0','0x15b64d8: bl       #0x275a928','0x15b64dc: fcmp     s0, #0.0','0x15b6500: b        #0x275ab60'),
        'return_source_stops_clears_and_restores_pause_behavior':has('AudioManager','FreeSource','0x15b6238: bl       #0x275ab20','0x15b6248: bl       #0x275a9a0','0x15b6250: mov      w1, wzr','0x15b6258: bl       #0x275ac24'),
        'button_fields_none_guard':has('Button_Sound','OnDown','0x141fdc4: ldr      w0, [x0, #0x20]','0x141fdc8: cbz      w0, #0x141fdd8') and has('Button_Sound','OnClick','0x141fddc: ldr      w0, [x0, #0x24]'),
        'game_playlist_explicit_four_not_five':has('GP_SoundTracks.<Start>d__0','MoveNext','0x14f6b70: mov      w12, #0x21','0x14f6c80: mov      w12, #0x22','0x14f6ce4: mov      w12, #0x23','0x14f6d48: mov      w10, #0x24'),
        'playlist_rerolls_previous_id':has('GP_SoundTracks.<Start>d__0','MoveNext','0x14f6bc8: cmp      w8, w0','0x14f6bcc: b.ne     #0x14f6c30','0x14f6be8: b        #0x14f6bb4'),
        'playlist_stop_gap_and_duration_minus_two_realtime':has('GP_SoundTracks.<Start>d__0','MoveNext','0x14f6bf0: mov      w0, wzr','0x14f6bfc: bl       #0x15b5214','0x14f6c10: fmov     s0, #2.00000000','0x14f6c1c: bl       #0x2786604','0x14f6dd0: fmov     s0, #-2.00000000','0x14f6de0: bl       #0x2786604'),
        'boss_warning_alarm_two_stop_then_boss_one':has('Boss1_Director.<WarningBossAppear>d__15','MoveNext','0x1501a8c: mov      w0, #0x18','0x1501af4: mov      w0, wzr','0x1501b5c: mov      w0, #0x1f'),
        'home_random_pool_two_ids':has('Home_Loader.<Start>d__5','MoveNext','0x13be51c: mov      w1, #2','0x13be538: mov      w8, #0x1d','0x13be548: mov      w8, #0x1e'),
        'endgame_move_uses_flying_not_victory_sound':has('GP_Endgame.<MovePlayer>d__10','MoveNext','0x14f1e48: mov      w0, #0x1a','0x14f1e50: bl       #0x15b50ac'),
        'player_health_branch_uses_player_destroy':has('Player_Health','TakeDamage','0x14c75a4: mov      w0, #0x3a','0x14c75ac: bl       #0x15b50ac'),
        'registry_names_resolve_to_enum':all(r['tree']['m_Name'] in names for r in registry),
        'resource_prefix_and_generic_loadall':strings('AudioManager','GetData')=={'Audio/'} and any(v.get('Name')=='Method$UnityEngine.Resources.LoadAll<SoundClip>()' for m in method('AudioManager','GetData')['metadata_loads'] for v in m['records']),
        'unknown_audio_id_returns_null':has('AudioManager','GetAudioClip','0x15b5c5c: tbz      w0, #0, #0x15b5ca8','0x15b5ca8: mov      x0, xzr'),
    }
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    def rule(identifier,cls,name,**fields):return dict(id=identifier,evidence_method_ids=[method(cls,name)['id']],**fields)
    rules=[
        rule('mute','AudioManager','get_Mute',key='MUTE_AUDIO',stored_type='int32',missing_default=0,predicate='stored == 1',writer_method_id=method('AudioManager','set_Mute')['id'],setter_scope='writes preference only; no direct AudioListener/source mutation in this selected setter'),
        rule('sound_volume','AudioManager','get_VolumeSound',key='VolumeSound',stored_type='float32',missing_default_approx=0.73,predicate='mute -> 0 else saved float',writer_method_id=method('AudioManager','set_VolumeSound')['id']),
        rule('music_volume','AudioManager','get_VolumeMusic',key='VolumeMusic',stored_type='float32',missing_default_approx=0.3,predicate='mute -> 0 else saved float',writer_method_id=method('AudioManager','set_VolumeMusic')['id']),
        rule('pause','AudioManager','set_Pause',behavior='AudioListener.pause, separate from Time.timeScale'),
        rule('oneshot','AudioManager','PlayOneShot',behavior='Acquire pooled source, playOnAwake=false, assign clip, loop=false, VolumeSound, PlayOneShot(clip, input volumeScale), start DelayFreeSource coroutine; does not check mute to skip allocation/play request.'),
        rule('music','AudioManager','StartSmoothMusic',behavior='Nonzero enum creates looping source, ignoreListenerPause=true, starts at volume0 and Play(); returns clip.length. None0 creates no new temp and returns0, still starts smoothing old main. Interrupted smoothing finalized first.'),
        rule('fade','AudioManager.<SmoothMusic>d__32','MoveNext',progress_increment_approx=0.01,yield_kind='null each iteration, not deltaTime',behavior='progress compared against current effective VolumeMusic; temp clamped progress, old main clamped(initialOldVolume-progress); then SmoothMusicDone'),
        rule('reclaim','AudioManager.<>c__DisplayClass27_0','<DelayFreeSource>b__0',predicate='AudioSource.time > 0 OR AudioSource.isPlaying; WaitWhile then FreeSource',coroutine_method_id=method('AudioManager.<DelayFreeSource>d__27','MoveNext')['id']),
        rule('game_playlist','GP_SoundTracks.<Start>d__0','MoveNext',clip_enum_values=[33,34,35,36],selection='Random.Range(0,count), reroll same previous enum',timing='WaitForSecondsRealtime(length-2); PlayMusic(None); WaitForSecondsRealtime(2); select next',scope='Not full boss/playlist interruption lifecycle; Bgm_Game5 exists in registry but not added by this iterator.'),
        rule('home_music','Home_Loader.<Start>d__5','MoveNext',clip_enum_values=[29,30],selection='Random.Range(0,2)'),
        rule('boss_warning','Boss1_Director.<WarningBossAppear>d__15','MoveNext',sequence=[dict(api='PlayOneShot',enum_value=24),dict(api='PlayMusic',enum_value=0),dict(api='PlayMusic',enum_value=31)],scope='Branch/coroutine sequencing retained in raw; not simultaneous calls'),
        rule('endgame_move','GP_Endgame.<MovePlayer>d__10','MoveNext',api='PlayOneShot',enum_value=26,scope='Move-out branch, not a claim that victory/defeat IDs never play elsewhere'),
        rule('player_destroy','Player_Health','TakeDamage',api='PlayOneShot',enum_value=58,scope='Specific branch inside TakeDamage, not every hit'),
        rule('button_down','Button_Sound','OnDown',source_field='soundClickDown+0x20',behavior='None0 skips; otherwise OneShot scale1; serialized override not reconstructed here'),
        rule('button_click','Button_Sound','OnClick',source_field='soundClick+0x24',behavior='None0 skips; otherwise OneShot scale1; serialized override not reconstructed here'),
    ]
    return dict(checks=checks,rules=rules,status='PROVISIONAL_STATIC_AUDIO_RULES_NOT_LISTENING_OR_RUNTIME',schema_version=1,sources=sources,methods=records,
        declarations={cls:text for cls,text in declarations.items() if cls in set(manifest['classes'])|{'AllClipName'}},
        clip_enum=names,registry_raw=registry,
        registry=[dict(sound_id=r['tree']['m_Name'],enum_value=names.get(r['tree']['m_Name']),legacy_registry_path_id=r['path_id'],clip_pptr=r['tree']['soundClip'],legacy_unqualified_export_candidates=audio_exports.get(r['tree']['soundClip']['m_PathID'],[]) if r['tree']['soundClip']['m_FileID']==0 else [],export_join_scope='legacy local PPtr/path_id candidate only; serialized-file identity not retained') for r in registry],
        limitations=['RVA-qualified method IDs disambiguate overloaded names.','Legacy SoundClip raw has no serialized-file identity; PPtr is retained, not promoted to a global audio identity.','Static call sites do not prove an audible runtime event.','No original media committed; see separate draft archive audit/browser.'])


def main():
    data=build()
    evidence=RAW/'audio-rules/contracts.json.gz'
    evidence.write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False,indent=2).encode(),mtime=0))
    out={k:data[k] for k in ['status','schema_version','clip_enum','registry','rules','limitations']}
    out.update(raw_evidence=str(evidence.relative_to(ROOT)),raw_evidence_sha256_decompressed=hashlib.sha256(gzip.decompress(evidence.read_bytes())).hexdigest())
    (ROOT/'datas/audio_rules.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(len(data['methods']),'methods;',len(data['clip_enum']),'enum names;',len(data['registry']),'registry entries')


if __name__=='__main__':main()
