# `datas/` — data pack WindWings

Dữ liệu bóc từ APK **WindWings: Space Shooter 1.3.118**, đã chuẩn hoá thành JSON để dùng cho
bản clone (engine nào cũng đọc được). Sinh tự động bằng:

```bash
python3 tools/apk-analyze/data_pack.py --root .   # đọc từ docs/apk-analysis/*.csv
python3 datas/validate.py                          # kiểm tra tính nhất quán
```

## Nội dung

| File | Bản ghi | Ý nghĩa |
|---|---:|---|
| `ships.json` | 25 | roster tàu (`id`, `star`, `actived`, sprite) |
| `drones.json` | 13 | roster drone |
| `bosses.json` | 46 | wave → boss icon (ch1 `7001–7022`, ch2 `9001–9024`) |
| `items.json` | 6 | item rơi (`index`, icon, 5 sprite stat) |
| `enemy_hp.json` | 981 | HP serialize của từng enemy/boss component |
| `boss_hp.json` | 277 | gom theo prefab gốc, bỏ bản trùng scene |
| `iap_products.json` | 170 | product ID, tách consumable / non-consumable |
| `sprites.csv` | ~2.800 | `path_id → tên sprite + file PNG` (chỉ có sau lần export mới) |
| `../i18n/en.json`, `vi.json` | 1.415 key | chuỗi UI tiếng Anh / tiếng Việt |

## Quy ước

- `sprite_path_id` / `sprite_name`: **pathID Unity**, không phải asset path. Tên chỉ có khi
  `docs/apk-analysis/04-asset-manifest.csv` đã có cột `path_id` (lần chạy pipeline mới).
  Tra bằng `sprites.csv`.
- `star`: hệ số sức mạnh (2.0 → 5.11) — **không phải** sao hiển thị.
- `actived: false` = có trong data nhưng chưa mở cho người chơi.
- HP trong `enemy_hp.json` là giá trị **serialize sẵn trong prefab**; HP runtime còn bị nhân bởi
  `Enemy_Data_Balance` và cấu hình stage.
- Các class config nằm trong code (`Player_Get_Datas`, `Droid_Data_Balance`, `Tech_Datas`,
  `Stage_Get_Datas`, `Map_Get_Datas`, `Enemy_Data_Balance`, `Device_Get_Data`, `GameDatas`)
  **không được serialize** trong build → giá trị nằm trong thân hàm IL2CPP, cần decompile
  `libil2cpp.so` mới lấy được. Chúng không có trong pack này.

## Bản quyền

ID, số liệu và khoá chuỗi là dữ liệu kỹ thuật của game gốc (GCenter). Dùng để tham chiếu thiết kế
cho bản clone của bạn; **không** phát hành lại kèm asset/âm thanh/nội dung chữ gốc.

## Contract save mở đầu — bổ sung sau report65

`opening_persistence.json` là bảng **dẫn xuất tạm thời** của 8 nhóm khóa (tutorial,
stage/zone, sao, drone equip/unlock), không phải save thực hay schema toàn game.
Có kiểu lưu, kiểu getter trả về, default theo scope, cache, side effect, method IDs
và SHA256 raw evidence. `schema_version=1` là version **định dạng contract**, không
phải version save của APK. Xem
[`65-opening-save-keys-cache-and-read-side-effects.md`](../docs/apk-analysis/65-opening-save-keys-cache-and-read-side-effects.md).

Tái tạo: `python3 tools/verify/opening_persistence.py`. Không sửa bảng này tay.
Không gọi getter trong serializer/debug như truy vấn thuần: StageTarget và
IndexTutorial có nhánh ghi ngược tiến độ; Unity PlayerPrefs khác dictionary `/Prefs`.

## Contract ship/loadout — bổ sung report66

`player_loadout_persistence.json`:15 nhóm khóa int32 cho ship equip/unlock,
level/rank/trial/cards/skin, tech/device/talent; có reader return type riêng,
method refs, raw hash, mảng rank đã join metadata và consumer gameplay.
**Tạm thời/partial**, không phải full save schema hay save version của APK.
Raw `reverse-engineering/raw/player-loadout/` giữ native ASM/JSON, metadata array
blobs có padding và `contracts.json.gz` (33methods/43checks).

Tái tạo: `python3 tools/verify/player_loadout_persistence.py`. Không sửa tay.
Phân biệt saved/trial/effective/cached: getter equip lỗi có thể reset cả hai slot;
rank repair base trước override; floor2 nằm ở loader; mode4/Game override tech và
device không xóa saved state. Xem [report66](../docs/apk-analysis/66-player-loadout-save-rank-trial-tech-consumers.md).

## Audio contract — report67; pack audit — report68

`audio_rules.json` giữ118enum names,92registry rows,15rules dẫn xuất và reference
raw `reverse-engineering/raw/audio-rules/contracts.json.gz` (65methods/25checks).
Method refs có RVA để phân biệt overload. Registry PPtr→export file là **candidate
legacy pathID join**, chưa file-scoped identity proof. Tái tạo bằng
`python3 tools/verify/audio_rules.py`. Float pool defaults≈0.73/.30 và fade≈.01
là decimal rounded từ exporter, không full IEEE bits. Không nhầm realtime playlist
với fade theo coroutine frame, mute preference với AudioListener.pause.

Asset pack ngoài Git đã kiểm CRC nhưng chưa đủ: raw/asset-pack/catalog.json.gz
có151collision paths và320manifest size mismatches. Đọc report68/browser instructions;
không dùng manifest filename như object identity, không coi0missing paths là đủ.
