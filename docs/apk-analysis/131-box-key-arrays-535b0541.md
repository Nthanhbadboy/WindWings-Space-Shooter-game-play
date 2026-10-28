# 131 — Nội dung `BoxKeyCost` / `KeyPrices` / `NumberRewards` / `AllTimeAds` (STATIC-ONLY)

**Task:** #30-followup-3 (AI-4) · **Branch:** `arena/535b0541-windwings-space-shooter-game-p`
**Artifact:** `datas/l2_535b0541_box_arrays.json.gz` (2.251 B, SHA256 `b5be797d40daedc16676e4ef1a83ce5b976458d9e5d12e1a539d9ea42a469b4d`)
**Nguồn dữ liệu:** `reverse-engineering/il2cpp/field-defaults.json` (`fieldDefaultValues` v31, 10.493 field) + `reverse-engineering/raw/box-draw-535b0541/native.json.gz` + `dump.cs.gz`. **Không** cần raw native mới.
**Bằng chứng:** `STATIC_ONLY_ORIGINAL_APK`. Thứ tự/vật phẩm rút thật vẫn là `MODEL_NOT_MEASURED runtime`.

Đây là bước chặn mà báo cáo 130 để lại (§8): byte của bốn mảng không nằm trong `libil2cpp.so` mà trong field default của `global-metadata.dat`. Bảng đó đã có sẵn trong repo, nên gap đóng được mà không phải bóc lại APK.

---

## 1. Kết quả

| statics | field | kiểu | giá trị | nghĩa |
|---|---|---|---|---|
| 0x38 | `Board_Quest.BoxKeyCost` | `int[3]` | **30 · 30 · 30** | số key cần để mở hộp |
| 0x40 | `Board_Quest.KeyPrices` | `int[3]` | **6 · 20 · 100** | gem cho **mỗi key còn thiếu** |
| 0x48 | `Board_Quest.NumberRewards` | `int[3]` | **5 · 6 · 9** | số lượt rút từ pool pack |
| 0x50 | `Board_Quest.AllTimeAds` | `double[3]` | **18.000 · 259.200 · 691.200** | ngưỡng cooldown quảng cáo, **giây** |

Chỉ số = `Board_QuestRewards.typeBox` (đã đóng ở báo cáo 130: chỉ số nút hộp 0/1/2).

## 2. Chuỗi giải (và vì sao không dùng `blobs` của extractor)

```
bl 0x205B07C (RuntimeHelpers.InitializeArray, RVA 33.927.292)
  ↳ FieldInfo token: kind 4, source lẻ  →  ordinal = (source-1)/2
  ↳ <PrivateImplementationDetails> (pid TypeDefIndex 2461, 740 field)
  ↳ fieldDefaultValues[data_index] → raw
  ↳ new int[3] / new double[3] → 3 phần tử
```

| statics | InitializeArray RVA | ordinal | `data_index` | declared B | raw |
|---|---|---|---|---|---|
| 0x38 | 19.977.024 | 669 | 29.304 | 12 | `1e0000001e0000001e000000…` |
| 0x40 | 19.977.064 | 654 | 28.800 | 12 | `060000001400000064000000…` |
| 0x48 | 19.977.104 | 690 | 30.408 | 12 | `050000000600000009000000…` |
| 0x50 | 19.977.144 | 241 | 11.936 | 24 | `000000000094d140…` |

**Cảnh báo cho lần đọc sau:** trường `initialize_arrays[].blobs` trong raw native **không phải** nội dung mảng — đó là bảng token metadata đã relocate (`0x8000xxxx` tăng dần). Nội dung thật chỉ có ở `fieldDefaultValues`. Artifact ghi rõ điều này ở từng phần tử (`not_the_extractor_blobs`).

Bốn store vào statics nằm sau mỗi lệnh `bl`, đúng thứ tự `+0x38 → +0x40 → +0x48 → +0x50`; tám kiểm tra cấu trúc (`declared_bytes == số phần tử × độ rộng`, và tên field khớp `dump.cs`) đều **PASS** và được ghi trong `artifact.checks`.

## 3. Kinh tế học đọc được từ bốn mảng

| Hộp (`typeBox`) | Key cần | Gem / key thiếu | Mở trọn bằng gem (30 × giá) | Số lượt rút | Cooldown ad |
|---|---|---|---|---|---|
| 0 | 30 | 6 | **180** | 5 | 5 giờ |
| 1 | 30 | 20 | **600** | 6 | 72 giờ |
| 2 | 30 | 100 | **3.000** | 9 | 192 giờ |

- Cả ba hộp đòi **cùng 30 key**; khác nhau ở giá key thiếu và số lượt rút. Hộp 2 đắt gấp ~16,7 lần hộp 0 nhưng chỉ rút 9 lượt so với 5.
- Quy đổi (suy ra, không phải số đọc trực tiếp): theo `GetExchangeGemsFromEnergy` = **0,3 gem/energy** (báo cáo 129) ⇒ mở trọn hộp 2 ≈ **10.000 energy**; hộp 0 ≈ 600 energy.
- `NumberRewards[0] = 5` là con số đưa vào `GetListIndexRandomRewards(pack, 5, 0)`; nhánh `typeBox == 0` còn **nhân đôi trọng số index 13 `DroneExp`** trong pool (báo cáo 129) — hai hiệu ứng độc lập, không cộng dồn vào số lượt.

## 4. Đơn vị của `AllTimeAds` được chứng minh, không phải đoán

`Board_QuestRewards.IsTimeAdsReady` (RVA **19.984.600**, 340 B):

```
d8 = AllTimeAds[typeBox]                       # statics+0x50, double[], bounds-checked
if typeBox == 2 && elapsed == -1: MyLibrary.UpdateSystemTimeSaved(key)   # RVA 21.105.576
ready = elapsed >= d8
elapsed = MyLibrary.GetTotalSecondsTravelTime(key)   # RVA 21.105.208 → double
```

`GetTotalSecondsTravelTime` trả **double giây** và được so trực tiếp với `AllTimeAds[typeBox]` (`fcmp d0, d8`) ⇒ đơn vị của mảng là **giây**: 18.000 = 5 h, 259.200 = 72 h, 691.200 = 192 h. Trường hợp riêng `typeBox == 2` khi chưa từng lưu mốc (`elapsed == -1`) sẽ ghi mốc rồi so lại — tức hộp 2 lần đầu **chưa** coi là sẵn sàng.

## 5. Liên kết với các báo cáo trước

| Nguồn | Số | Dùng ở đây |
|---|---|---|
| 129 | `GetExchangeGemsFromEnergy` = 0,3 gem/energy | quy đổi gem ↔ energy ở §3 |
| 129 | `GetListIndexRandomRewards` nhân đôi `DroneExp` khi `typeBox == 0` | §3 |
| 130 | `typeBox` = chỉ số nút hộp, 2 store (`.cctor`, `OnPressedButtonOpenBox`) | khoá chỉ số cho cả 4 mảng |
| 130 | công thức giá `KeyPrices[typeBox] × (BoxKeyCost[typeBox] − owned)` | khớp đúng ngữ nghĩa hai mảng ở §1 |

## 6. Còn mở

| Hạng mục | Bước chặn |
|---|---|
| Vật phẩm cụ thể của từng lượt rút | `UnityEngine.Random` seed lúc chạy — `MODEL_NOT_MEASURED runtime` |
| Nguồn tăng `KeyCount0/1/2` | call site `GameDatas.set_KeyCount0/1/2` nằm ngoài các họ đã pin (128–131); cần một lượt quét call-site toàn `.text` |
| Số hộp hiển thị | `Board_Quest.allBoxes` là `GameObject[]` do scene gán |

## 7. Tái lập

```
python3 tools/verify/box_arrays.py            # → datas/l2_535b0541_box_arrays.json.gz
python3 -m unittest tests.test_box_arrays -v  # 14 contract
python3 -m unittest discover -s tests -q
python3 tools/verify-claims.py                # in PASS/FAIL, không chép số vào tài liệu
```

## provenance:

- `field-defaults.json` (`fieldDefaultValues` v31, 10.493 field) · raw `box-draw-535b0541` (`908e841c…`) · raw `meta-rewards-535b0541` (`e91a8c76…`) · `dump.cs.gz` (`e08f23fb…`); SHA từng file ghi trong `artifact.provenance.sources`.
- Nguyên bản: XAPK + `libil2cpp.so` với SHA ghi trong `artifact.provenance`.
- Chỉ tĩnh. Không emulator/thiết bị/probe; không sửa 3 file bảo vệ; không merge/self-ACK.
