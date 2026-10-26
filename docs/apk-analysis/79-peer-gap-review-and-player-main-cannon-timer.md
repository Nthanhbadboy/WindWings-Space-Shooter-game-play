# 79 — Review phần thiếu bên spec và main-cannon timer tàu 1

> **Cập nhật scope từ report81:** “tàu1” ở đây là implementation `Player_Attack_1`,
> source prefab ID10003, không suy ID10001 từ hậu tố. Report81 đã nối thêm ELF RELA/metadata
> callback→concrete Bullet_Plasma→Obj_Collider→receiver; limitation binding ở bản này là lịch sử.


**Tạm thời, static APK evidence; không runtime/playback approval.**

## Đã cập nhật bên kia

Fetch explicit peer `029559d47`; giữ nguyên văn 4 tài liệu và SHA tại
`reverse-engineering/raw/peer-review/update-029559d47.json.gz`.
Đây là chứng cứ trạng thái tài liệu peer, **không phải chứng cứ APK**.
Task P0 gửi PR12 comment6399017163, đồng thời ghi HANDOFF_AI_TASKS:
đồng bộ bảng tổng audio/assets, playerID binding và CameraScaler78; tách lựa chọn thiết kế
khỏi thông số APK. Không merge peer và không chỉnh nhánh peer.

Lỗ hổng cụ thể: MISSING §2.2 dùng report53 delay của Path/Waypoints spawn để đóng
StartMainCannonRate của player. Tên `rate` giống nhau không nối được hai consumer.
COMBAT vẫn ghi damage×rate là DPS dẫn xuất; chưa thể dùng như DPS thực để kết luận TTK.

## Đào mới từ APK, không dump lại media

Recovery **40203414134 SUCCESS**, collector2842bf5f0, rawbot **bb896f1da**.
`raw/player-firing/index.json` giữ SHA XAPK, native, metadata, dump và 6 file native của:
`Player_Get_Datas`, `Player_Attack`, `Player_Attack_1`.
Cả ba có method records, không size_capped; điều này **không** chứng minh mọi method
boundary chính xác (exporter minimum span/shared RVA vẫn phải xét riêng).

### Chuỗi đọc trực tiếp — giới hạn tàu implementation Player_Attack_1

Nguồn: dump.cs.gz field offsets + raw/player-firing/native/*.asm.txt.

| Mắt xích | Native evidence | Ý nghĩa có giới hạn |
|---|---|---|
| Getter | GetMainCannonRate0x14e3cd8;0x14e3d28 đọc static array@0x80;0x14e3d54/58 trừ rồi nhân | `StartMainCannonRate[index] * (1 - GetMainCannonRatePercent())`, chưa mô hình toàn bộ percent |
| Binding | SetupDatas0x147a364 gọi getter với index0 đã setup tại0x147a2f8;0x147a37c FCSEL;0x147a380 store@0xa8 | `timeRateMainCannon`; nhánh demo có literal3 thay getter. Không gộp normal/demo |
| Clock | MainCannonShoot0x147a920 gọi0x2786dc0 | dump xác nhận `UnityEngine.Time.get_time`, không wall clock |
| Gate | 0x147a924/928/92c so now với@0x10c rồi b.mi returnpath | chờ deadline `timeToShotMainCannon` khi now nhỏ hơn deadline |
| Additional-shot branch | 0x147a944..984 dùng@0x118/@0x124 và counters@0x11c/@0x120 | có timer và chuỗi phát phụ, không phải một viên mỗi chu kỳ đơn giản |
| Deadline | 0x147a988..990 load@0xa8;fadd;store@0x10c | tại nhánh này deadline = now + timeRateMainCannon; **interval**, không multiplier shot/second |
| Barrels | 0x147a994..a9e8 duyệt array@0x88 rồi pool getter | còn nhiều nòng/bullet config, không được bỏ qua khi tính DPS |

**Kết luận bàn giao:** ít nhất ở consumer tàu1, main-cannon rate đi vào phép cộng với
Time.time để đặt deadline. Vì vậy phép `StartMainCannonDamages * StartMainCannonRate`
**không được coi là DPS đã chứng minh**. Ngay cả đổi thành damage/rate cũng **chưa đủ**:
modifier, nhánh demo, extra shots, barrels, hit/collision, target/shield và gameplay gates
đều có ảnh hưởng. Không suy rate unit/consumer của 23 tàu khác từ một implementation.
Không gọi đây là số phát đo được trên thiết bị. Native FCMP/branch và float behavior
chưa được chạy qua Unity/FPCR để đóng các special cases.

## Phần còn thiếu thật và ai làm

- **Spec/AI thiết kế:** sửa claim DPS/TTK nói trên; thống nhất bảng tổng thay vì append báo cáo
  mà để entrypoint cũ; viết manifest `system → raw contract → rule → new-design choice → test`.
  L1 có thể khởi công với art/balance mới; reference media đầy đủ không có nghĩa đã import/render approved.
- **Data follow-up:** nếu cần parity nhịp bắn, nối actual emitted bullet/damage trong ship1 trước,
  rồi inventory consumer từng tàu; chưa giao full combat simulator từ phát hiện timer này.
- Các phần allboss transitions, shader/stencil/draw order, lifecycle, migrate/cloud, plugin/build
  parity vẫn scopedunknown, không tự nâng thành không tồn tại hoặc bắt làm hết để khởi công L1.
- Premium và pool-history tiếp tục hoãn theo chỉ đạo; không lấy screenshot làm native numeric evidence.

## Kiểm tra

3 test mới kiểm SHA inputs/raw/dump, getter→field→clock→deadline address-qualified và scope/caps.
Đây là regression của evidence, **không phải mô phỏng nhịp bắn/TTK**.
Recovery workflow regression step PASS; local targeted3tests PASS. Full suite ghi riêng sau khi chạy.

Local fullsuite **250tests PASS** (Pillow12,23.220s), datasvalidate và diffcheck PASS.

Final Verify **40203611037 SUCCESS** cho code9aa2d7e6f: regenerate tables/dependency/regressionsteps PASS.
