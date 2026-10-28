# L2 #18 — DPS runtime parity, tàu 10001 / `Player_Attack_3` — `arena/a5a74747-windwings-space-shooter-game-p`

**Kết luận: parity DPS runtime CHƯA ĐO.** Có đối chiếu khớp hai input tĩnh (base damage và rate) với `/statics` từ một run game trên phone, nhưng run đó là app 1.0.69 modded Premium trong khi APK/native source đang phân tích là 1.3.118 official. Không có chuỗi HP mục tiêu theo thời gian, sự kiện hit, hay instance field của `Player_10001`; không tuyên bố runtime DPS parity.

## Model tĩnh (nguồn APK/native)

| Field | Tàu 10001 | Cách đọc |
|---|---:|---|
| Combat implementation | `Player_Attack_3` | Component snapshot gắn class này lên GameObject `Player_10001`; snapshot không chứng minh object được spawn/chạy |
| Combat array index | **2** | `Player_Attack_3` truyền literal `2` tới shared damage getter `0x14e3948` và `GetMainCannonRate` `0x14e3cd8` |
| `StartMainCannonDamages[2]` | **2.680** | Base per-accessor-call value trước tech/level/runtime modifiers |
| `StartMainCannonRate[2]` | **4,8 s** | Native `GetMainCannonRate` dùng giá trị này làm đầu vào interval và nhân `(1 − GetMainCannonRatePercent())` |
| `p3_startShotRate` | **0,15** | Field cấu hình khác; không thay thế `timeRateMainCannon` dùng bởi scheduler này |

`SetupDatas` lưu kết quả rate vào `timeRateMainCannon` (`Player_Attack_3` offset `0xac`) trừ nhánh `demo`, nơi native chọn `3,0 s`. `MainCannonShoot` so sánh `Time.time` với `timeToShotMainCannon` (`0xf8`), rồi cộng interval vào deadline tiếp theo. Vì thế `damage × rate = 12.864` có đơn vị **damage·seconds**, không phải DPS. Đây là điểm cần ưu tiên native APK evidence hơn ghi chú backlog dùng cách gọi “damage × rate”.

Điều kiện đơn giản hóa `2680 / 4.8` cho **558,333333 damage/s trên một projectile stream** chỉ là baseline mô hình có điều kiện: không tech/level modifier, không demo, không extra-shot group, không critical, một projectile hit mỗi scheduled interval, không miss và không receiver/HP/shield reduction. Không phải DPS toàn tàu. Snapshot serialize **4** `mainCannonPoints` reference, nhưng con số đó không chứng minh 4 phát thực tế, 4 hit, hay target nhận đủ damage.

## Runtime readback đã có — và chưa có

Ramus `/statics` trên run phone trả `StartMainCannonDamages[2]=2680`, `StartMainCannonRate[2]=4.8`, `p3_startShotRate=0.15`; hai mảng có 24 phần tử. Đây là **parity giá trị field tĩnh** với artifact model, không phải phép đo DPS. Runtime profile ghi app `com.Gcenter.WindWings.SpaceShooter.Premium` 1.0.69 modded, scene `Game`, `timeScale=1`; static source là APK `com.Wind.wings.Space.Shooter` 1.3.118. Không gộp hai build thành cùng-bản parity.

Không có runtime readback của `timeRateMainCannon`, active barrel/extra-shot counts, damage event, hit/miss, hoặc target HP delta theo timestamp. **Measured DPS = none**; không dùng screenshot để gate hoặc thay số liệu.

## Kết quả cần để đóng parity

Cần cùng-build runtime capture xác nhận `Player_10001` active; đọc rate/tech/level/demo/extra-shot state; ghi timestamp và HP mục tiêu trước/sau nhiều scheduled cycles với receiver gates đã biết; so damage thực tế / thời gian với model trong đúng state đó. Không suy ra tàu khác từ tàu 10001.

## Provenance / kiểm tra

- Nhãn chia sẻ: **REPLICATION**, peer source ref `origin/arena/ef6b75ef-windwings-space-shooter-game-p`, commit `d7e718cfb5466fd7bd03e2d8357400d744b108cb`.
- Gói Unity snapshot: `data.unity3d` SHA-256 `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7`; `resources.resource` SHA-256 `032264516f0b33b5af50eb87d4d7ce7cf0763eac8cf72090f66c198991991c7f`.
- Full per-input SHA pins (native method files, cctor artifacts, exact serialized component shard, Ramus static/runtime snapshots and version notes) are embedded in `datas/l2_dps_runtime_parity_ship1_18.json.gz`; that artifact also pins the XAPK/lib hashes.
- Artifact SHA-256: `9fe9d1e2bc16a3252c78a3c3ae0263fdce049fe68b23ae861064f04fab1a3e04`.
- Generator: `tools/build_dps_runtime_parity_ship1_18.py`.
