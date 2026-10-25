# 48 — Runtime probe: có đào được, nhưng phải tránh tự đổi trạng thái đo

**PROVISIONAL.** Dữ liệu game có thẩm quyền chỉ từ APK gốc đang bóc. Phân biệt
bằng chứng APK, readiness của công cụ, và quan sát trên APK khác.

## Phát hiện mới quan trọng: getter tutorial có side effect

Nguồn **APK gốc**: `raw/il2cpp-consts/GP_Tutorials.asm.txt`, method
`get_IndexTutorial @0x14f4a14`. Bản dẫn xuất giữ nguyên asm/hash/callsite/metadata
ở `raw/runtime-probe/getter-observer-effect.json.gz` (các đường raw bên dưới đều
thuộc `reverse-engineering/`).

| Điểm native | Thao tác |
|---|---|
| 0x14f4ba8 | gọi Stage_Datas.get_StageTarget @0x12b1f68 |
| 0x14f4bac–bb0 | so với2, nếu nhỏ hơn thì bỏ qua block đổi index |
| 0x14f4bc8–bd0 | đọc GP_Tutorials static+0x10, nếu khác0 thì bỏ qua |
| 0x14f4be8–bec | gán cache indexTut=6 |
| 0x14f4c10–c1c | w1=6, gọi PlayerPreferences.SetInt @0x13f1a04 |

Slot `0x2adc200` resolve qua relocation/metadata thành key **TUTORIAL**, không
phải suy từ tên gần đó. Report47 đã xác nhận SetInt tailcall Unity PlayerPrefs.
Getter còn có nhánh cache=-1 đọc PlayerPrefs trước đó; không coi nó là đọc RAM
thuần. Điều kiện đổi thành6 phải đúng tại thời điểm chạy; **không khẳng định một
phiên probe đã thực sự kích hoạt nó**, cũng không kết luận đã flush xuống đĩa.

**Hệ quả cho probe:** `/statics` quét mọi property và `getter.Invoke(null,null)`
có thể làm thay đổi chính trạng thái cần đo khi gọi với type GP_Tutorials.
Không được quảng cáo thao tác đó là passive/read-only chỉ vì HTTP dùng GET.
Getter của game và property wrapper đọc native field phải được tách riêng.

## Hai nhánh code không giống nhau — không audit nhầm bản cũ

Đã fetch đúng remote tracking ref, không switch/merge nhánh kia.
Snapshot được kiểm: `arena/20330d0e-windwings-space-shooter-game-p` tại
`25c367aca99f06f14df546d2f30e60b427827157`.
`raw/runtime-probe/other-branch-code.json.gz` giữ code/hash/ref, đồng thời so
với head của CI run được chọn. Đây là **source công cụ**, không phải game data.

- Bản cục bộ cũ: adapter BepInEx6 không thấy register host; StaticsJson chỉ đọc
  CLR fields. **Không dùng hai điều này để kết luận nhánh mới còn thiếu.**
- Nhánh kia đã có TryInjectBridgeHost, GetProperties + GetFields, `/types`,
  array/list lồng, `/anim`, và target compile phone-interop (StubUnity=false).
- Bản mới giải quyết thiếu property nhưng quét getter quá rộng: rủi ro observer
  effect ở trên là vấn đề khác. Không blind-merge chỉ để lấy các sửa cũ.
- `collect.sh` snapshot còn dùng `get` trong bước4b trước khi định nghĩa hàm
  `get` bên dưới. Ở shell mới, các lệnh `/types` đó sẽ command-not-found.
  `set -uo pipefail` không có `-e`, nên script còn có thể tiếp tục sau lỗi.
  Đưa helper lên trước lần dùng đầu tiên; validate JSON `ok`, không chỉ HTTP200.

Nguồn upstream pinned của Il2CppInterop field→property và ClassInjector API
được giữ ở `raw/runtime-probe/toolchain/` kèm commit/SHA. Chỉ giải thích yêu cầu
của công cụ; không chứng minh APK đang chạy hay fork Android đã tương thích.

## CI xanh không phải đã lấy runtime

Đã đọc jobs/steps và **phục hồi artifact thật**, không suy từ summary:

- Run **40181812673**, head96c86d4dd, conclusion success.
- Bridge build và gate chạy; **Start session: skipped; Probe game state: skipped**.
- Artifact ghi `bridge: no`. Source XAPK SHA
  `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`
  **khớp nguồn đang bóc**, package `com.Wind.wings.Space.Shooter`, arm64-v8a.
- APK đã merge/ký cho install, nhưng **không có phiên game state ở run này**.
  Không có bridge trong APK cũng không phủ định trường hợp loader cài plugin từ
  storage bên ngoài; trường hợp đó vẫn cần log chứng minh bridge thực sự sống.
- Không đủ dữ liệu để chốt thiết bị run này bị lỗi ABI; nó chưa start session.

Raw: `raw/runtime-probe/40181812673/{ci-run.json,ci-jobs.json,artifact/**}`.
Recovery **40182134370**, success, chỉ download artifact cũ, **không bật Ramus**.
Không thêm APK, screenshot hay DLL gốc vào Git.

## Log điện thoại có thật nhưng khác package — không nhập số vào spec gốc

Remote có bộ `docs/apk-analysis/ramus/2026-10-23-phone/`. Raw logcat chứa đường
`/data/app/com.Gcenter.WindWings.SpaceShooter.Premium-.../lib/arm64/libunity.so`.
Package này khác APK gốc. `raw/runtime-probe/phone-provenance-rejection.json`
giữ excerpt/hash/source-ref để kiểm; **không lấy các giá trị balance/tutorial/
stage từ đó làm kết luận bản hiện tại**. Unity version giống không đủ xác minh
APK/native giống. Tool có thể chạy được trên một build khác không chứng minh
cùng luồng tutorial trên build đang bóc.

## Kế hoạch probe đúng mục tiêu stage1–3

`raw/runtime-probe/stage1-3-watchpoints.json.gz` trích trực tiếp declaration từ
dump APK gốc: **14 native static field +13 method watchpoint**, có offsets/RVA
và declaration. **Đây là kế hoạch thu, không phải các giá trị đã quan sát.**

1. Xác minh package/version và SHA APK/libil2cpp/data trước; ABI thiết bị bằng
   adb getprop. Bản gắn loader phải ghi rõ thay đổi và hash native/data giữ lại.
2. Chứng minh bridge/agent đúng PID bằng health + frame tăng + scene và log nạp;
   build với interop thực của game, không chỉ stub/self-test.
3. Đọc native fields `indexTut`, `inTutorial`, StageCurrent/ModeCurrent/flags,
   victory/defaultBoard. **Không gọi IndexTutorial/StageTarget getter, setter,
   Save hoặc force class initialization để đo.** Chưa init thì ghi trạng thái đó,
   không ép thành0. Nếu dùng property wrapper, chỉ allowlist từ field APK gốc,
   xác minh getter chỉ đọc field và ghi rõ tác động init có thể có.
4. Observe entry/exit setter tutorial, ThroughTut, Continue, OpenBoard consumer,
   CheckSpecPopup và callback; bổ sung trace PlayerPrefs.Save @0x277cf6c để kiểm
   flush khi app tự gọi. Không chủ động gọi Save rồi dùng kết quả làm bằng chứng.
5. Snapshot theo cùng frame/mốc: trước clear stage1 → endgame → Continue →
   Home/Game route → stage2/3. Thu activeSelf **và activeInHierarchy**, button
   enabled/interactable, camera ortho/viewport/resolution và popup order.
6. Chạy riêng new profile/returning profile; quit/focus/restart/force-stop thành
   scenario khác nhau. Không gộp dữ liệu khi bridge đã gọi setter/timescale/send.

Mirror mặc định mỗi10s và chỉ scene/root không chứng minh callback ngắn hay
TUTORIAL flush. Cắt `Substring(0,3500)` còn có thể tạo JSON không hợp lệ khi root
name dài; cần truncate có cấu trúc hoặc chunk JSON. Không dùng thiếu log làm
bằng chứng một event không xảy ra.

## Tái kiểm

```sh
python3 tools/verify/runtime_probe_audit.py
python3 -m unittest discover -s tests -q
```

Lượt này30tests pass. Audit không tạo payload game giả. Chưa có adb/thiết bị gắn
vào sandbox, chưa chạy phiên native-stage1–3 của APK gốc; vì vậy chưa nâng các
OPEN runtime trong report47 thành CLOSED.
