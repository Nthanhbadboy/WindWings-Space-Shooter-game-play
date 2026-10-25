# 69 — Blob đã có: Map inventory và Player field-typed decode

**25/10/2026 — kết luận tạm từ static APK, không phải replay/gameplay approval.**

## Gỡ blocker trao đổi với peer

Đã kiểm trực tiếp peer commit `cfc0197f691f4623294b5ec65195923aa738e397`.
File `reverse-engineering/il2cpp/ia-resolved.json` của peer **đã chứa**:

- `methods["Map_Get_Datas.cctor"]`: **576** record InitializeArray.
- `methods["Player_Get_Datas.cctor"]`: **6** record InitializeArray.
- Hai nhóm record bằng nhau hoàn toàn với bản extraction trên nhánh này, gồm raw hex;
  tất cả `length_valid=true`. Không khẳng định toàn file giống nhau.

Fingerprint so sánh và pin peer giữ ở
`reverse-engineering/raw/initialize-arrays/peer-comparison.json`.
Không cần chờ một lần dump mới chỉ để lấy những byte này.

## Deliverable tái tạo được

Chạy `python3 tools/verify/initialize_array_inventory.py` để tạo
`reverse-engineering/raw/initialize-arrays/typed-inventory.json.gz`.
Giữ từng record gốc (call address, array allocation address, private field, raw hex,
len, ints), thêm typed values/payload length/trailing bytes; giữ hash decompressed
của input, native call→store windows và field binding Player. Không sửa raw cũ.

`len` là số phần tử, **không phải toàn bộ độ dài hex chia 4**. Nhiều raw có đuôi
alignment; tool chỉ unpack `len*4` byte, giữ đuôi riêng. Float dùng IEEE754
little-endian float32; `ints` sẵn có là bit view, không phải damage đã giải mã.

## Player: 1 int[24] + 3 float[24] + 2 float[3]

Đối chiếu native ASM `raw/il2cpp-consts/Player_Get_Datas.asm.txt` với field declarations
trong `il2cpp/dump.cs.gz`. Native call InitializeArray target `0x205b07c`;
array x19 được lưu vào các static field sau:

| Call RVA | Store RVA | Static offset | Field | Kiểu |
|---|---|---|---|---|
| 0x14e5b3c | 0x14e5b48 | 0x38 | PlayerCosts | int[24] |
| 0x14e5e8c | 0x14e5e9c | 0x78 | StartMainCannonDamages | float[24] |
| 0x14e5eb4 | 0x14e5ec4 | 0x80 | StartMainCannonRate | float[24] |
| 0x14e5edc | 0x14e5f18 | 0x88 | StartWingCannonDamages | float[24] |
| 0x14e608c | 0x14e60c4 | 0x1c8 | shipCloneDamage | float[3] |
| 0x14e6204 | 0x14e6244 | 0x308 | PercentToCompleteMissions222 | float[3] |

Main damage mở đầu: `[4500,220,2680,8000,710,1650]`.
Rate mở đầu ≈`[4.8,6.8,4.8,5.8,4.8,4.8]`.
Wing damage mở đầu: `[218,75,186,118,236,309]`.
Đây là thứ tự mảng, **chưa tự gắn ship ID hoặc kết luận effective DPS/TTK**.
Peer mô tả “4 float[24]” cần sửa: PlayerCosts là int[24].

## Map: tại sao chưa chấp nhận “573 blob còn lại”

Inventory có **576 call**, không phải 576 stage. Tất cả record có int32 view;
report này không gắn chúng với container/mode/index. Map class có nhiều container
campaign, branch, arena, PvP, challenge, endless, obstacle và bảng khác.
Ba opening arrays ghi bằng literal stores không tự động là ba record InitializeArray
trong 576; không lấy `576−3=573` làm population contract.

Task có ích tiếp theo cho peer là dùng native cctor/list-add/static-store và consumer
GetListWaves để gắn **call address → container → index → wave IDs**, kiểm lại các
bảng `datas/maps.json`, `datas/map_segments_full.json` hiện có, thay vì chờ raw.
Chỉ thu hẹp gap nào còn thật sự thiếu. Wave ID list cũng chưa phải duration/spawn
schedule; phải join prefab/consumer cho đại lượng đó. Không tự tuyên bố L2 đóng.

## Kiểm thử và phần chưa làm

167 tests PASS; `python3 datas/validate.py` PASS. Năm test mới: artifact reproduction,
Map population+byte roundtrip, Player typed bindings/known values, float bit view
và alignment tail, reject malformed input. Endpoint/declaration checks là regression
checks, không thay việc đọc register flow/native windows.

Chưa re-export asset pack ở bước này. Report68 vẫn hiện hành: pack cũ có collision,
release phải giữ draft; identity-safe re-export là task extraction tiếp theo.
