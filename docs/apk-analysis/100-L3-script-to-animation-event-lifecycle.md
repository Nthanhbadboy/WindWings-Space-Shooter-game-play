# 100 — L3: script UI → activation/trigger → state/clip → event → deactivation

**26/10/2026 — tạm thời; L3 chưa render-complete.** Tiếp99 bằng native script thực,
không dừng ở “chọn state bằng tay”. Đã nối nguyên một lifecycle UI tới đúng serialized
objects và controller/event. Đây là source contract + conservative CFG, chưa là Unity trace.

## Chuỗi cụ thể đã đóng bằng source: Popup_QuitMissions trong Board_Pause

Mọi ID dưới đây thuộc `data.unity3d/resources.assets`:

1. GO **57508**, Popup_Notices component **644901**, Animator **495980**. Serialized GO
   inactive; Animator enabled, updateMode2, keepAnimatorStateOnDisable=false. Không suy
   inactive đồng nghĩa không bao giờ được mở.
2. Native **Popup_Notices.SetPopup(Action,Action,bool)@0x13b83cc** ghi callback/flag,
   gọi Component.get_gameObject rồi **GameObject.SetActive(true)** ở0x13b83f4. Receiver
   đã nối đúng GO57508, không tìm object cùng tên. String overload@0x13bfb70 gọi đúng
   overload này và có thêm đường set text/activation; indirect TMP calls vẫn giữ unknown.
3. Animator495980 gắn trực tiếp **controller1974**, tên source `Popup_Network`, mặc dù
   node tên Popup_QuitMissions. Source default state **Appear → clip1572** và coefficients
   scale/alpha đã probe ở99. SetPopup **không được bịa thành lệnh Animator.Play(Appear)**:
   source chỉ chứng minh activation; entry/reset của engine vẫn chưa được chạy/readback.
4. Native **OnPressedButtonExit@0x13c5370** đọc field `anim+0x20`, resolve tới495980,
   nạp literal **"Hide"** qua **GOT0x2adbc30 → ELF RELA → metadata slot0x2bdfb10 →
   stringliteral.json**, rồi tailcall **Animator.SetTrigger(string)@0x27583b0**.
5. Parameter hash của Hide nối tới condition transition thật trong1974, destination
   state1 **Hide → clip1573**. Transition/condition/exit-time/duration giữ nguyên source;
   không khẳng định trigger luôn được consume ngay hay bỏ qua state hiện tại.
6. Clip1573 có event **OffBoard tại0.3333333432674408s**, same-GO receiver candidate
   đúng644901. Nối được vào **Popup_Notices.OffBoard@0x13ca5dc**.
7. Native OffBoard gọi delegate exitAction nếu có, sau đó get_gameObject và
   **SetActive(false)** ở0x13ca638; receiver tiếp tục là **cùng GO57508**.

OnPressedButtonConfirm có guard đọc **exitAfterConfirm+0x38** trước đường Hide. CFG giữ
symbolic branch operand/offset và dump field declaration, không gọi mọi confirm là đóng
popup vô điều kiện. Delegate runtime/callback có thể có effects khác; chưa execute chúng.

Raw joined lifecycle snapshot ở `reverse-engineering/raw/l3-ui-driver-verification/local100.json`.
Không có screenshot redraw, không thay source tween bằng animation tự thiết kế.

## Raw recovery mới, có boundary và namespace thật

- `tools/recovery/l3_ui_native.py` + workflowrecover-l3-ui-native: pinned APK/lib SHA,
  **1074 methods**,13 root classes + generated nested types. Core UI10classes,Popup,
  Popup_Notices,TuPro.UIObjectAnchors. Đây không là toàn bộ game UI/native classes.
- `reverse-engineering/raw/l3-ui-native/`: bounded method bytes, native asm/constants,
  exact relocation bytes/file offsets và manifest hashes. Không commit APK/full executable.
- Bytes dùng **next distinct dump RVA**, không minimum8-byte overlap sang method kế tiếp.
  Interval có thể chứa padding; decoder ghi decoded_bytes/span_decode_status, không giả
  mọi byte trong interval là reachable semantic instruction. Native asm export cũ có thể
  minimum8 overlap ở method rất ngắn; CFG dùng bounded bytes riêng làm authority.
- Lần recover40231346501 fail vì namespace filter sai cho UIObjectAnchors. Đã kiểm dump:
  namespace thật **TuPro**, sửa đúng thay vì bỏ class hoặc ghi “không hỗ trợ”. Corrected
  run **40231440486 SUCCESS**, raw bot commit **161bee87d**.

## Dữ liệu mới dùng ngay trong recipe

`tools/verify/l3_native_cfg.py` và `tools/verify/l3_ui_drivers.py` sinh
`datas/l3_ui_drivers.json.gz`; `l3_recipe.py --root 10 --include-raw ...` có thêm `native_ui`:

| Source-derived mục | Kết quả |
|---|---:|
| Native methods |1074|
| Serialized UI instances, kể cả selected-family descendants |214|
| Potential appearance-call instances |1751|
| Receiver exact-join / unresolved |1274 /477|
| Animator condition/state routes |230|
| Exact receiver + target RVA direct-callee links |687|
| Persistent-call/animation-event entries nối native effects |409|
| Inherited animation-event candidates bổ sung |9|

Counts là static instances/calls/candidates, **không** runtime invocation count, không độ phủ
full L3. Recipe giữ `effect_index`, `direct_callee_effect_indices`, `callback_index` theo
**global source artifacts** và artifact path/SHA; không đổi chúng thành local-array indices.
Call sang receiver ngoài hierarchy của root có thể tra global bank; không tự kéo arbitrary GO
references vào scene hay nhận chúng là visible children.

Native method/CFG có raw callsites, tất cả declaration candidates cùng RVA, register arguments,
conditional branches/edges/symbolic operands, unresolved indirect calls. Scene join đi từ
`this → dump field offset → serialized PPtr` hoặc Component.get_gameObject; string đi qua
RELA/metadata đúng địa chỉ. Không chỉ tìm chữ Hide trong disassembly rồi ghép theo tên.

Direct-callee links yêu cầu **receiver identity + exact target RVA**, phân biệt overload.
Một base method vẫn có potential effects khi gọi explicit base body; callback selection không
tự ép base body thay subclass override chưa bóc. Action/delegate runtime không bị tự invoke.

## Sửa thiếu callback kế thừa mà không nhận nhầm runtime delivery

Popup_EventConfirmQuit có class **Popup_QuitEvent**, component594188, Animator496687.
Dump chứng minh `Popup_QuitEvent : Popup_Notices`. Event OffBoard của clip1573 trước đây
không có *same-class declared method* candidate; nay có **base-declared candidate** OffBoard
trên Popup_Notices. Nối candidate đó tới đúng native body/GO của instance594188.

Tất cả46 old animation-event gaps đã rà theo declared namespace-qualified ancestry:
**9** thêm base-declared candidate, **37** chưa có candidate theo phép tra này. Không sửa
raw98 hay âm thầm gọi cả46 đã resolve. Với private base method, giữ rõ candidate và chưa
chạy Unity message lookup; **không** nhận chứng minh callback đã được gửi/chạy.
Không global-match class cùng tên ở namespace khác.

## Bảo thủ ở đúng chỗ, không tạo “giới hạn” giả

- CFG đi theo branches trong bounded method, merge register chỉ giữ giá trị bằng nhau ở
  mọi incoming path. Unsupported writes kill symbolic value; call clobbers caller-saved
  registers/flags, không giữ “giá trị gần nhất” qua nhánh để đoán receiver.
- Branch predicates không được execute; graph là over-approximation, có thể chứa infeasible
  paths. Có CFG/guard source **không** đồng nghĩa đã có transition scheduler/runtime trace.
- Static arg0 không bị gọi là this. Metadata initialization không được giả lập; chỉ chứng minh
  slot/string identity từ relocation + pinned metadata table.
-477 unresolved receivers vẫn còn, thường do runtime arguments/indirect/runtime object paths;
  đây là **model không resolve**, không chứng minh source thiếu/bỏ được call. Không chọn
  unknown thành default receiver hoặc false/true cho đẹp số.
- Alpha/scale probe99 vẫn là arithmetic model; batch100 nối được script entry/exit tới model,
  chưa chạy shader/stencil/particles/layout/camera projection để tạo hình cuối.

17 tests mới: CFG diamond/unknown join, unsupported-write kill, ABI clobbers, GOT/literal,
getter receiver, static args, unreachable blocks, namespace inheritance; regenerate artifact,
raw hashes/boundaries, exact Popup receiver/Hide/guard/controller, OffBoard same GO, exact-RVA
callee expansion, event→native body, inherited candidate và recipe integration.
Local full suite/remote receipts ghi riêng sau chạy, không dùng tests làm visual acceptance.

**Tiến độ thật:** không còn chỉ có clip inventory/stategraph; đã có script-driven lifecycle
source join và call/guard graph cho selected core UI. Vẫn chưa engine transition/blending,
runtime delegate execution, driven layout, particle/shader/composition-render.5 header-only
MonoBehaviours và52default-mesh refs ở98 vẫn không được tự nhận đã xử lý. L3 chưa complete.

Local final: **957 tests PASS /147.821s**,17new tests. CI receipt follows separately.
