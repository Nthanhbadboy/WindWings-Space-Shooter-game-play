# WindWings: Space Shooter — reverse engineering & clone reference

Phân tích ngược bản Android **`com.Wind.wings.Space.Shooter` v1.3.118** (Unity 2022.3.62f3,
IL2CPP, metadata v31) để làm tài liệu tham chiếu cho bản clone.

## Đọc gì trước

| Muốn gì | Mở |
|---|---|
| Xem **ảnh/asset** để design | [`docs/assets/INDEX.md`](docs/assets/INDEX.md) — 42 contact sheet, 2.197 asset |
| Dữ liệu dùng được ngay (JSON) | [`datas/`](datas/README.md) — tàu, drone, boss, item, HP, IAP, i18n |
| Spec thiết kế | [`docs/spec/`](docs/spec/) — GAMEPLAY / UI / ASSETS / BALANCE |
| Số liệu thô bóc từ APK | [`docs/apk-analysis/`](docs/apk-analysis/) — 23 báo cáo + CSV từng class |
| Hằng số trong code máy | [`docs/apk-analysis/19-il2cpp-constants.md`](docs/apk-analysis/19-il2cpp-constants.md) |
| Layout UI dạng số | [`docs/apk-analysis/20-ui-layout.md`](docs/apk-analysis/20-ui-layout.md) + [`24-ui-screens.md`](docs/apk-analysis/24-ui-screens.md) (114 màn, text/key) |
| **Spine**: rig, animation, keyframe, event | [`docs/apk-analysis/22-spine-rigs.md`](docs/apk-analysis/22-spine-rigs.md) + [`23-spine-anim.md`](docs/apk-analysis/23-spine-anim.md) |
| Truy vết công thức trong thân hàm | [`docs/apk-analysis/28-formula-traces.md`](docs/apk-analysis/28-formula-traces.md) |
| Animation gốc Unity (clip/controller) | [`docs/apk-analysis/26-native-animation.md`](docs/apk-analysis/26-native-animation.md) + [`27-anim-curves.md`](docs/apk-analysis/27-anim-curves.md) |
| Lớp hành vi enemy/boss + cây Transform | [`docs/apk-analysis/25-enemy-behaviour.md`](docs/apk-analysis/25-enemy-behaviour.md) |
| Âm thanh: id → file, thời lượng | [`docs/apk-analysis/21-audio-map.md`](docs/apk-analysis/21-audio-map.md) |
| Code C# đã dump | [`reverse-engineering/`](reverse-engineering/) — `dump.cs.gz`, Spine, ScriptableObject |
| **Dữ liệu thô (không cắt)** | [`reverse-engineering/raw/`](reverse-engineering/raw/) — typetree JSONL gz, UI layout gz, hằng số IL2CPP + asm |
| Đọc nhánh spec của AI kia (tham khảo, **không merge**) | [`docs/CROSS_BRANCH_20330d0e.md`](docs/CROSS_BRANCH_20330d0e.md) |
| Độ tin cậy từng kết luận | [`docs/conclusions.md`](docs/conclusions.md) — mức A/B/C và cách kiểm lại |

## Lấy file gốc

- APK: draft release **`windwings-apk-1.3.118`** (`windwings.xapk`, 142 MB)
- Asset full-size (PNG atlas + WAV): draft release **`windwings-assets-1.3.118`**
  → `assets.z01` + `assets.zip` (94 MB + 63 MB), ghép lại:
  `cat assets.z01 assets.zip > assets.zip && unzip assets.zip`
- Bản preview nhẹ: `asset-previews.zip` (12 MB) trong cùng release

## Pipeline

`.github/workflows/analyze-apk.yml` — tải XAPK (cache) → tách part → Il2CppDumper →
UnityPy export → typetree ScriptableObject → wave/combat data → REA → contact sheet →
release + commit báo cáo. Chạy lại: `gh workflow run analyze-apk.yml`.

> Toàn bộ nội dung là **tài liệu tham chiếu**. APK/asset thuộc bản quyền GCenter;
> không phát hành lại, không đóng gói vào sản phẩm.
