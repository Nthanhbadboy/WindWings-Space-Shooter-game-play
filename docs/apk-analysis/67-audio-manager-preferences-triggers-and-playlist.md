# 67 — Audio preferences, source pooling, crossfade và trigger

**Tạm thời / static, ngày25/10/2026. Không phải nghe thử/replay hay full audio timeline.**

## Raw và tái kiểm

- `reverse-engineering/raw/audio-rules/index.json`: input XAPK/native/metadata/dump SHA256 và output hashes, cùng build của report65–66.
- `native/*.{asm.txt,json}`:10 lớp, gồm AudioManager, hai coroutine/callback của manager, GP_SoundTracks coroutine, Button_Sound, AudioBehaviour2, Player_Sounds, SoundClip. Recovery riêng từ cached original đã pin; CI **40192970188 success**. Không full APK rerun. Lần đầu recovery fail trước publish do output directory; đã sửa cách ly khỏi player-loadout và kiểm regression.
- `contracts.json.gz`: **65 method không capped, 25 checks,15 rules**, native/inventory, direct-call targets, metadata loads, source hashes, dump enum/declarations và registry snapshot.
- `datas/audio_rules.json`: rule dẫn xuất +118 enum names +92 registry entries, phương thức tham chiếu **có RVA**. Hai overload GetAudioSource và hai IEnumerator.get_Current không được ghi đè nhau theo tên.
- Snapshot registry gốc: `raw/typetrees/SoundClip.jsonl.gz`. Manifest export gốc đã lấy và pin trong report68. **Legacy snapshot không giữ serialized-file identity**, nên mapping PPtr/path_id sang filename là **candidate có ghi scope**, chưa phải file-scoped identity proof. Không tin m_Script đã lệch layout của legacy tree để tự nhận diện script.

```bash
python3 tools/verify/audio_rules.py
python3 -m unittest discover -s tests
python3 datas/validate.py
```

8 test mới cho audio/recovery; cả repo **162 tests PASS** sau vòng audio+asset audit. Format schema_version1 không phải save version.

## Preferences và pause không phải một thứ

| Key / API | Kết quả của body đã đọc |
|---|---|
| `MUTE_AUDIO` | int default0; chỉ stored==1 là mute. Setter ghi bool bit0 qua typed PlayerPreferences→Unity prefs |
| `VolumeSound` | float missing-default **≈0.73** từ pool `0x756dd4`; mute→0, không mute→GetFloat |
| `VolumeMusic` | float missing-default **≈0.30** từ pool `0x7570e0`; mute→0, không mute→GetFloat |
| `AudioManager.Pause` | wrapper `AudioListener.pause`, không phải Time.timeScale và không có saved key trong hai body này |

Dấu≈ vì native exporter lưu decimal float đã làm tròn, không phải phục dựng IEEE bit pattern đầy đủ. Setter Mute body chọn chỉ persist flag; **không trực tiếp cập nhật AudioListener hay mọi source**. Không biến nó thành lệnh engine mute tức thì dựa trên tên property. Getter volume không tự clamp saved float ở đây; việc Unity AudioSource setter có xử lý riêng không đồng nghĩa saved getter clamp.

VolumeSound setter duyệt source list và tránh music sources; VolumeMusic setter cập nhật main source khi không smoothing, đồng thời lưu preference. Cần đọc caller/UI nếu muốn tái tạo chính xác thao tác toggle volume đang chạy. Report không khẳng định mọi màn settings đã nối.

## Pool/one-shot và API lấy source

`PlayOneShot` `15b50ac`:

1. Lấy source từ pool (đã lấy source **trước** lookup clip).
2. `playOnAwake=false`, gán clip, `loop=false`, volume=VolumeSound.
3. `AudioSource.PlayOneShot(clip,inputVolumeScale)`.
4. Start DelayFreeSource; coroutine yield **WaitWhile** với predicate `source.time>0 OR source.isPlaying`, sau đó FreeSource.

Không có early mute→skip allocation/play request trong body này; volume getter mới trả0. Không mô hình reclaim bằng chờ đúng clip.length: predicate thực là trạng thái/time của AudioSource. FreeSource tránh thêm trùng free-list; Stop, clear clip, reset ignoreListenerPause=false rồi đưa vào free-list. Chính sách max voices/stealing/drop-all chưa được chứng minh.

Hai overload giữ riêng:

- `GetAudioSource()` `15b5a68`: lấy free item/remove hoặc tạo AudioSource mới.
- `GetAudioSource(AllClipName,bool)` `15b5f38`: lấy source, assign clip/loop/volume và trả source; không coi nó tự tương đương PlayOneShot.

`GetData` load generic `Resources.LoadAll<SoundClip>("Audio/")`, dictionary keyed Object.name; `GetAudioClip` dùng enum.ToString→dictionary. Nếu không có key thì trả null trong body `15b5bb0`. Điều đó **không chứng minh caller xử lý thiếu clip an toàn**: music nonzero còn dereference clip.length; không sáng tác fallback clip hay guaranteed silent drop.

## Music và crossfade

`PlayMusic`→`StartSmoothMusic` `15b5d30`:

- Nonzero enum: temp source loop=true, **ignoreListenerPause=true**, volume0 rồi Play; trả clip.length.
- `AllClipName.None=0`: không tạo temp mới, trả0 nhưng vẫn chạy smoothing để dọn main cũ. Đây không phải “không làm gì”.
- Nếu đang smoothing, finalize trước khi bắt đầu transition mới.

Coroutine `AudioManager.<SmoothMusic>d__32.MoveNext` `15b6678`:

- progress ban đầu0; lưu old main volume.
- Khi progress<effective VolumeMusic, tăng **≈0.01 mỗi coroutine iteration**, cập nhật temp/old-main volume có clamp0..current target và **yield null**.
- Không dùng deltaTime trong phép tăng này; không được gọi đây là fade cố định1giây hay2giây. Với target≈0.3 là khoảng30 bước tăng, không phải30ms; frame rate và thay đổi target/mute ảnh hưởng thời gian.
- Cuối nhánh gọi SmoothMusicDone để thu hồi main cũ và chuyển temp thành main.

Music source được set ignoreListenerPause=true; vì vậy AudioListener.pause không mặc định im tất cả music. Không suy riêng điều này thành mọi loại pause/UI flow của game đã được tái tạo.

## Playlist và các trigger đã nối

| Consumer | Clip/logic từ native |
|---|---|
| Home_Loader.Start iterator | Tạo mảng `[29,30]` = Bgm_Home1/2, Random.Range(0,2), PlayMusic |
| GP_SoundTracks.Start iterator | List **`[33,34,35,36]`** = Bgm_Game1..4; không tự thêm Bgm_Game5 chỉ vì registry có |
| GP_SoundTracks vòng lặp | Chọn random index, reroll nếu cùng enum trước; play, **WaitForSecondsRealtime(length−2)**, PlayMusic(None), **WaitForSecondsRealtime(2)**, chọn tiếp |
| Boss1_Director.WarningBossAppear iterator | Theo các nhánh/yield raw: OneShot24=Sfx_Alarm2, PlayMusic0=None, PlayMusic31=Bgm_Boss1 |
| Player_Health.TakeDamage | Một branch gọi OneShot58=Sfx_PlayerDestroy; không phải mọi hit đều phát nó |
| GP_Endgame.MovePlayer iterator | Branch gọi OneShot26=**Sfx_Flying**, không tự đổi thành Sfx_Victory27 vì tên class là Endgame |
| Button_Sound.OnDown / OnClick | Đọc field+0x20/+0x24; enum0 thì bỏ; khác0→OneShot scale1; chưa giả định mọi serialized override giống ctor |
| Machine_Gun_Attack.NormalShoot / BarrelShoot | Clip ID động từ state/field, có None guard; không hardcode mọi súng là Sfx_Shot1 |

Timing playlist là realtime, khác fade step theo coroutine frame. Không suy playlist không bị interrupt, boss music luôn được coordinator riêng bảo vệ, hay thắng/thua chỉ có một tiếng. Chưa giữ mọi consumer toàn game; tên clip không phải bằng chứng trigger.

AudioBehaviour2 có keyboard/demo calls và PlayMusic0/1/2; **không dùng demo ấy thay gameplay routing**. Player_Sounds trong dump chỉ có ctor; không nâng thành subsystem chứa mọi sound player.

## Registry khác số enum, khác số WAV

- 118 enum names (gồm None),92 SoundClip entries trong legacy raw; cả92 tên đều match enum.
- 92 entries trỏ tới **69 distinct legacy `(fileID,pathID)` pairs**; Boss1/Boss2 cùng PPtr là một alias điển hình.
-Archive report68 thực có69 WAV, tổng≈571.465giây, header/CRC đã kiểm; không phải92 WAV. Candidate mapping từ export manifest có scope rõ trong JSON.
- Enum tồn tại nhưng không có registry row trong snapshot không chứng minh toàn APK không có clip đó. GetAudioClip missing-key→null là body fact; eventual runtime failure/audibility chưa replay.

**Còn mở:** settings UI và caller toggle, toàn sound prefab/animation-event consumer, lifecycle boss↔playlist interruption, phối âm thực tế/latency/listening, và mapping audio identity file-scoped. Không phát minh event chỉ từ tên file.
