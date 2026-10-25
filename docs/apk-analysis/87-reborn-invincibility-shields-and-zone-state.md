# 87 — Nối Invoke → RebornDone, khiên và invisible-zone

**Tạm thời, APK-authoritative.** Không phải đồng hồ Unity/visual approval hay tuyên bố
đã dịch toàn bộ APK. Mở rộng chuỗi85–86 bằng 7 root/417 native instructions,
32 anchors chính +6 cross-root checks; executable flag/zone fixtures và18 tests mới.

## 1. Invoke không còn đoán theo tên hàm

Recovery **40211999354 SUCCESS25s**, raw commit **7518813f4**. Giữ từng byte tại
`raw/player-invincibility/invoke.json`:

- GOT **2ae8560** raw0 → ELF RELA1027 → **2be4670**.
- Pointee `133700a000000000` → encoded **a0003713**, usage5/string, index **7049**.
- Metadata31 header và literal definition `0a00000044f40200` → 10 bytes tại
  metadata offset314316: `5265626f726e446f6e65` = **RebornDone**.
- Root đích **Player_Controller.RebornDone14c4d5c** có trong dump/native.

Normal14c6130 và PVP14c44e0 đều IsInvoking(name); nếu true → CancelInvoke(name),
rồi load **Player_Get_Datas.TimeResetInvincible static+8** → Invoke(name, delay).
Không phải luôn chồng nhiều timer. Cả hai dùng cùng literal, không tự đoán string.

Initializer load **d0@757ce0** = `0000404000002041`, store64bit static+8 tại
**14e5b0c**: **TimeResetInvincible=3.0**, **TimeCanActiveInvincible=10.0**.
Hai field32bit, không đọc double3.0 hay gộp cả hai làm một timer. GOT2adbdd8 đã
join RELA→Player_Get_Datas_TypeInfo. Đây là **giá trị khởi tạo**; Invoke đọc live
field, không chứng minh field bất biến hay3 giây wall-clock. Normal còn timeScale0
và.05 đã nêu86; không suy scheduler/runtime timing từ fixture.

GOT2ae82a0 riêng → **2ba6c38**, metadata symbol
**SpaceShooter.Gameplay.GP_Controller_TypeInfo**. Không lẫn với Player_Controller.

## 2. Đính chính85–86: contact-hit không phải movement

`dump.cs` khai báo **Player_Physics.activeHitEnemey@90** (giữ đúng typo gốc).
Các writefalse ở normal/PVP extra-life và OnDie là tắt **enemy-contact hit**;
không đủ căn cứ nói tàu bị khóa di chuyển. Đã sửa model
`Lifecycle.move_enabled` → **hit_enemy_enabled**, test và hai báo cáo cũ; không
để thuật ngữ sai thành design requirement.

Trong RebornDone, Controller+48 cũng **không phải input**: là **playerTalentScript**,
writefalse tại **14c4e78** trỏ **Player_Talent.reborning@20**. Đây là join type từ
metadata, không suy semantic từ một offset bool. Model mới dùng đúng tên talent.

## 3. RebornDone: preserve khác với settrue

Root clear **Controller.inReborning@a8**, activate particle GameObjects và đưa
bone TimeScale về1 trước khi tới shield flag block. Với dependency hợp lệ:

| Flag hiện tại | Health.invincible@30 ở flag block | Physics.activeHitEnemey |
|---|---|---|
| skill hoặc droid101 | giữ giá trị trước | false |
| không skill/101, có onehit | giữ giá trị trước | !droid103 |
| chỉ droid103 | giữ giá trị trước | false |
| cả4false | **false** | **true** |

Skill/101 còn clear **Talent.reborning**, xử lý item slot2; nhánh cleanup có thể
đi **Startup14c2d04** và các item helper. Fixture giữ cleanup hook **sau** write
contact flag, không coi các helper vô tác dụng. Startup root ghi
Health.shield@31 từ GetShieldOneHit14bb960 rồi Ability.Startup1471800; đó không
phải write Health.invincible@30. Không đồng nhất hai bool shield/invincible.

Bảng mô tả **direct flag block**, không bảo đảm trạng thái cuối sau helper/reentry.
Mộthit-only mà invincible đãfalse thì RebornDone **giữfalse**, không bậttrue lại.

## 4. Shield callbacks không refcount với rebirth/onehit

Đã đọc đủ OnShieldActive2678, OnShieldDroidActive10126e0,
OnShieldDroidActive1032748, OnShieldOneHitActive27b0 (prefix14c):

- Ba callback đầu ghi flag của nó rồi tính **skill OR101 OR103**.
  Health.invincible=aggregate, contact-hit=!aggregate.
- Onehit callback ghi flag53 và chỉ tính contact-hit bằng **ba flag còn lại**;
  không trực tiếp ghi Health.invincible.
- Các callback này không gate bằng inReborning và không cộng onehit vào aggregate.

Do đó shield callback(false) khi ba flag đềufalse có thể clear invincible dù
extra-life trước đó đã settrue. Đây là static store/order, **không phải khẳng định
scenario đó đã được quan sát trên máy**. Không thay bằng cơ chế refcount “hợp lý hơn”
trong reference/spec mà không đánh dấu đổi thiết kế.

## 5. SetInvisible: list zone không đồng nghĩa OR/count protection

Native **14c2e68** có thứ tự:

1. Enter add nếu chưa có; exit remove nếu có. Fixture dùng key bình thường,
   không giả lập UnityEngine.Object equality/destroyed-null.
2. Enter với heal=true và !isHealing: set isHealing=true, stop coroutine cũ nếu có,
   StartCoroutine IEHealInZoneInvisible; lưu handle. Đãhealing thì không restart.
3. **Đọc lại inReborning sau helper calls**. Nếu true → return, trước write
   Health.invisible@49/Physics.invisible@91, display và exit stop-heal.
4. Không reborning: hai invisible field = bool của lần gọi, display inverse.
   Exit sau đó clear isHealing và stop handle nếu có; không có clear handle ở root.

**Hệ quả đọc được, không cần bịa thiếu dữ liệu:**

- Heal có thể bắt đầu trước guard dù invisible fields chưa được apply.
- Exit trong rebirth vẫn remove zone nhưng skip stop-heal và skip invisible writes.
- Exit A khi list vẫn còn B **vẫn ghi invisible=false**; body không tính OR/listcount.
  Exit một zone không có trong list cũng đi nhánhfalse này.
- RebornDone root không gọi trực tiếp SetInvisible để replay zone list; loop của nó
  là particle array. Không từ đây khẳng định toàn chương trình không có helper/event
  khác reapply; chỉ không tự thêm lời gọi replay vào bản dịch root.

## 6. Evidence, kiểm tra và phần tiếp theo

Full local **412 tests PASS36.340s**, data validation/receiver44-root/lifecycle/shield regeneration
và diff whitespace PASS.18 tests mới. CI receipt ghi sau khi push, không suy từ local PASS.

`datas/player_shield_flow.json`, verifier `python3 -m tools.verify.player_shield_flow --check`:
literal chain, TypeInfo, packed initializer, typed fields,7 complete method ranges,
32 anchors +cross-root checks vàSHA. Models `player_shield_models.py`;18 tests mới,
có32 reborn combinations (kể cả initial invincible),256 callback cases, receiver85
→ normal extra-life86 → shield callback, multi-zone và live guard reread.

Format reference riêng: Perfare/Il2CppDumper commit
**4741d46ba9cd6159c5d853eb9d6fc48b4bfa2b1a**, Metadata.cs/MetadataClass.cs/LICENSE
preserved trong raw/toolchain. Chỉ giải format, không phải gameplay evidence.
Hai recovery đầu40211864359/40211929906 fail do lib và metadata nằm ở **hai splitAPK**;
đã sửa cross-split read, giữ failure trace lịch sử; không gọi đó là thiếu metadata.
Không đưa APK/lib/assets/audio gốc vàoGit; draft media release không đổi.

**Tiếp:** producer writes thật của **Enemy_Health.hitCallback@20/hitDamageCallback@28**
và callback registration theo consumer; CalculateDamage158479c đã đọc85 nhưng
fixture callbacks không chứng minh producer/listener thật. Không mở lại pool-history,
full media export hay dùng runtime để thay phần static còn phải nối.
