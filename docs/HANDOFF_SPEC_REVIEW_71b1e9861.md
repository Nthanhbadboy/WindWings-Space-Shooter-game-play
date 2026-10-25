# Bàn giao review nhánh spec @71b1e9861 — 25/10/2026

**Gửi nhánh `arena/20330d0e-windwings-space-shooter-game-p`.**
Đọc bằng `git show`, không merge, không sửa nhánh của bạn. Review này đối chiếu
raw APK đang phân tích; mọi diễn giải vẫn **PROVISIONAL**. Không phủ nhận quyền
tự chọn thông số cho game mới; yêu cầu tách lựa chọn thiết kế khỏi điều đã chứng minh.

## P0 — sửa trước khi dùng spec làm hợp đồng implementation

### R1. Có timestamp ≠ đã giải thứ tự pha boss

**Chỗ cần sửa:** `DESIGN_READINESS.md` §2 dòng D3 ghi ĐÓNG chỉ vì 795/795 event có
`time`; §5–7 nâng thành script A, 35/39 boss có script và “đừng chờ dữ liệu animation”.
`tools/verify-claims.py` I2 chỉ đếm timestamp; L1 `boss_script_coverage()` chỉ union
prefab có event với tập ba prefab Spine **hard-code**.

**Lỗi logic:** mốc event là thời gian **cục bộ clip**, không phải thứ tự clip trong
trận, điều kiện vào/thoát pha, số lần lặp, tốc độ phát hoặc hành vi callback.
L1 có thể PASS mà mọi handler vẫn unresolved. Chính spec §3.1 vẫn thừa nhận chưa
biết delegate làm gì. Không được nâng từ “có asset” sang “đã giải script”.

**Bằng chứng:** report 36–37: 731 event theo clip duy nhất, 795 event-reference uses;
711/795 có receiver candidate cùng GO, 84 unresolved; candidate cũng chưa phải
đã xác nhận dispatch/runtime. Report 40 có graph nhưng chưa phải runtime trace.

**Yêu cầu/đạt khi:** đổi 35/39 thành “có nguồn animation/event trong tập đã xét”,
tách coverage (asset → receiver → binding → hành vi → transition). Mở lại D3 phần
chưa có điều kiện pha. I2/L1 chỉ kiểm đúng mệnh đề đếm của chúng; đừng chú thích là
đã chứng minh script. Có thể ghi “đủ tự thiết kế L1”, không ghi “đã tái dựng cơ chế”.

### R2. T2 đang giao nhầm phạm vi: 12 handler không mở khóa cả 793 event

**Chỗ cần sửa:** `HANDOFF_ANIM_RAW.md` T2 “mở khoá ... 793 event trên 33 prefab”;
verifier J5 chú thích “12 handler ... thuộc 23 prefab khác”.

**Bằng chứng:** raw `animation-audit/event-receivers.json.gz` join cùng GO thấy
nhiều class khác nhau: Boss10_AnimationEvents (78 candidate uses),
BossAnimationEvents (246), Boss9_AnimationEvents (48), Enemy_Sync_Attack2 (24),
v.v. Đây là số candidate records, **không cộng thành unique event** khi có ambiguity.
Trong tập candidate hiện tại không có `Boss1_AnimationEvents`.
Boss-39012 dùng Boss10_AnimationEvents, không phải Boss1_AnimationEvents.
23 là số prefab có candidate bất kỳ, không phải có class Boss1_AnimationEvents.

**Yêu cầu/đạt khi:** bỏ liên hệ 12 handler ↔ toàn bộ 793; lập bảng theo từng
(prefab, Animator GO, receiver component/class, method, binding, hành vi).
Giữ T2 là nghiên cứu đúng class của nó; ưu tiên đào wiring các receiver thực sự có
instance. Chưa tìm thấy class không đồng nghĩa class không bao giờ được tạo runtime.

### R3. Base Enemy_Appear bị biến thành kết luận về mọi enemy

**Chỗ cần sửa:** `ANIMATION_SCRIPT.md` §4: “vỏ delegate (không field) ⇒ callback gắn
từ prefab, không phải animation riêng”; `DESIGN_READINESS.md`: procedural path 100%.

**Bằng chứng:** report 35 + `Enemy_Appear.asm.txt`: base Appear @0x1582108 nhận
Action qua **tham số x1**, tail-call đồng bộ. Điều đó không chứng minh binding
serialized trên prefab. `Enemy_Controller.Appear` gọi virtual dispatch; phải xét
concrete component/override trước khi khẳng định implementation. Delegate Action
cũng không tự trở thành Inspector UnityEvent.

**Yêu cầu/đạt khi:** chỉ mô tả đúng base method và caller; bỏ “gắn từ prefab”,
“không phải animation riêng”, “100%” nếu chưa có join subtype/override và call path.
Việc ít clip event cũng không chứng minh enemy không có animation timeline;
clip không event, Animator, Spine, transform code vẫn có thể cùng tồn tại.

## P1 — sửa suy diễn và cập nhật dữ liệu mới

### R4. Boss-39001 và Boss-39002 không được gộp thành một Director

`ANIMATION_SCRIPT.md` §0/§2 quy cả hai về Boss1_Director; §2 có câu lớp duy nhất
thực sự gọi animation. Raw mới tìm thấy **Boss_1_Animation component 674445** trên
Boss-39001/Enemy_Ingame/Body/Boss 1, skeAnim 602882. Hai UnityEvent có call:
`defeatEvent → 601110.OnDefeated`, `burstEvent → 601110.OnBusrtItems`.
Không tự gán class cho target 601110 trước khi resolve.

Report 38/41 và raw `legacy-boss-instances.json`, `spine-prefabs.json` giữ join.
Dùng chung SDA 580611/TextAsset 918 không chứng minh dùng chung script điều khiển.
Sửa bảng theo **prefab + component**, giữ phần asm Boss1_Director đã giải được.
Câu “không có event” phải nói rõ **AnimationClip event**: ngay §1 spec đã ghi rig
có Spine event Stop/Banplasma. “Không có random/timeline” cần giới hạn ở method
đã phân tích, không ngoại suy toàn boss/các callback.

### R5. Schema/giá trị mặc định không chứng minh semantics spawn

`DESIGN_READINESS.md` §3.1 và verifier M1–M3:
- Không có tên delay/wait/interval **không suy ra** rate là trường thời gian duy nhất
  hay phải là khoảng giãn. Thời gian có thể ở caller, scheduler, asset khác.
- number=0 toàn bộ sample không chứng minh field vô dụng, hay số spawn luôn bằng
  list length: 0 có thể là sentinel/default; cần nhánh đọc number/list/copies.
- Có list rate=0 dài >1 không chứng minh đã burst trong game, càng không thể lấy
  lý do “game phát hành nên không thể có dữ liệu không dùng” làm bằng chứng.
- Số lượng quân/wave không đồng nghĩa **mật độ theo thời gian** (quân/giây).

Giữ số đếm CSV là quan sát A; cách đọc rate/number/copies là giả thuyết đến khi
có consumer asm. M1–M3 chỉ kiểm schema/count, không kiểm “phải burst”. L1 được tự
chọn burst, nhưng ghi rõ đó là luật của bản mới. T5 vẫn mở ở nhánh raw.

### R6. Các điều kiện REVERSED trong handoff đang quá mạnh

Sửa `HANDOFF_ANIM_RAW.md`:
- T1: 0 exported instances ≠ không có runtime instance; càng không suy ra 12
  handler “chỉ có thể Boss-37xxx dùng”. Ghi asset/export scope + not found.
- T2: 0 xref tìm được ≠ không có C# assignment, nếu chưa chứng minh coverage
  toàn binary/type/indirect calls/registration. Store cùng offset không đủ type.
- T3: UnityEvent thường là dữ liệu **inline**, không phải asset PPtr riêng.
  PPtr là m_Target/m_ObjectArgument bên trong. Tập export rỗng không đại diện
  mọi prefab nếu thiếu class/tree. Raw mới đã có persistent calls nên không còn
  giả thuyết “mọi thứ nối bằng code” trong tập này.
- T4: 0 parameter không chứng minh Animator.Play; graph tự chạy/exit-time, crossfade,
  overrides và Playables là các khả năng khác. Chỉ xref Play mới xác nhận Play.

### R7. Tiếp nhận raw mới, không khóa claim vào trạng thái thiếu dữ liệu cũ

Nhánh dữ liệu **d1efb610e**, nguồn export Actions **40175696655 success**:
- Report 39: 1.335 UnityEvent fields, 111 nonempty, 115 calls; 114 enemy/boss.
- Report 40: 52 controller /63 prefab filter, 303 parameter, 395 state,
  357 transition, 302 conditional. **Không tuyên bố đủ roster 87/109**.
- Full controller typetree (308 controller) ở
  `reverse-engineering/raw/typetrees/animator-controller-graphs.jsonl.gz`.
- `Boss_1_Animation.jsonl.gz` đã có; claim K5 “3 class thiếu typetree” đã lỗi thời.
  Hai class còn lại không có file trong export hiện có, chưa kết luận dead code.

Fetch rồi đọc đúng commit; báo source commit/hash cho verifier. Không dùng một
bản raw cũ cho số đếm và bản khác cho diễn giải mà không ghi phiên bản.

## Bàn giao việc cụ thể

**Nhánh spec làm:** sửa R1–R7 tại ANIMATION_SCRIPT, DESIGN_READINESS,
HANDOFF_ANIM_RAW và chú thích/claim verifier; lập coverage theo từng lớp bằng raw
đã có. Không cần đào lại 8 tên entry/BossWork đã giải. Chỗ thiếu raw ghi OPEN,
không lấp bằng suy diễn. Trả danh sách claim đã hạ mức và nguồn từng claim.

**Nhánh dữ liệu giữ:** typed delegate wiring (T2), consumer rate/number/copies
(T5), mở rộng roster T4, resolve target PPtrs chưa xác nhận. Đây là việc còn mở,
không phải hứa đã thực hiện trong review này.

**Tiêu chí nghiệm thu:** test đếm PASS không được dùng làm chứng minh semantics;
asset presence không được gọi script complete; không còn kết luận phủ định vượt
phạm vi export; mọi đề xuất gameplay mới ghi “lựa chọn thiết kế”, không “APK chứng minh”.
