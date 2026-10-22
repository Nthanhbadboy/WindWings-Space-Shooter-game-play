# ASSETS — art direction, sprite, Spine, audio

> Nguồn: `docs/apk-analysis/04-unity-assets.md` (probe UnityPy toàn bộ `data.unity3d`),
> `04-asset-manifest.csv` (2.838 file), `SkeletonDataAsset.csv` (27 instance),
> `reverse-engineering/textassets/skeleton*.json` + `*.atlas*.txt` (26 skeleton + 1 `Saw`),
> `SoundClip.csv` (92), `15-audio.md` (69 AudioClip), `12-localization.csv`.
> Danh sách máy đọc được: **`docs/spec/sprite-list.csv`** (163 dòng: 67 Atlas · 27 Spine · 24 Ship · 17 UI · 12 Drone · 8 Background · 8 Bullet/FX).

---

## 0. TL;DR

| Hạng mục | Số lượng thật | Dung lượng | Nguồn |
|---|---:|---:|---|
| `Sprite` | **2.185** | **48,3 MB** | `04-asset-manifest.csv` |
| `Texture2D` | **653** | **64,1 MB** | `04-asset-manifest.csv` |
| Atlas page `sactx-*` | **67** (trong 653 `Texture2D`) | **31,0 MB** | `04-asset-manifest.csv` (cộng `bytes`) |
| Atlas page lớn nhất | 2048×2048 → `UI_Stage` | **3,09 MB** | `04-asset-manifest.csv` |
| Atlas page 2048×2048 | **2** (`UI_Stage`, `UIEvent`) | 3,09 + 2,38 MB | `04-asset-manifest.csv` |
| Spine skeleton | **26** (`skeleton*.json`) + 1 `Saw` | 577 region / 27 atlas | `textassets/*.atlas*.txt` |
| Bone/slot Spine | 616 bones / 446 slots | — | `textassets/skeleton*.json` |
| `SkeletonDataAsset` | **27** | `scale = 0.01`, `defaultMix = 0.2` | `SkeletonDataAsset.csv`, `class-inventory.csv` |
| `AudioClip` | 69 | 1 kênh, 16–48 kHz | `15-audio.md` |
| `SoundClip` (MonoBehaviour map sound) | **92** | — | `SoundClip.csv`, `class-inventory.csv` |
| `SpriteAtlas` | 66 | — | `04-unity-assets.md` |
| `AnimatorController` | 308 | — | `04-unity-assets.md` |

> **Kiểm lại vòng 2 (từ `04-asset-manifest.csv`, 2.838 dòng = 2.185 `Sprite` + 653 `Texture2D`):**
> các số vòng 1 ghi **654** `Texture2D`, **25** `SkeletonDataAsset`, **~50,6 MB** sprite,
> **66 page / 32,5 MB**, page lớn nhất 3,24 MB — **đều lệch**. Số đúng ở bảng trên.
> `SpriteAtlas` 66 và `AnimatorController` 308 không có trong manifest (manifest chỉ chứa
> `Sprite` + `Texture2D`), nên vẫn dẫn `04-unity-assets.md` (báo cáo UnityPy).
>
> **67 page = 66 nhóm.** Chênh 1 đã giải thích được: `UIEvent` bị chia **2 page**
> (`sactx-0-2048x2048` 2,38 MB + `sactx-1-1024x1024` 0,42 MB, **cùng hash `ed25d531`**).
> 67 − 1 = 66 nhóm, khớp `SpriteAtlas` 66. Không có page mồ côi.
>
> **Phân bố kích thước 67 page:** 1024² ×21 · 512² ×17 · 512×1024 ×9 · 1024×512 ×6 ·
> 1024×2048 ×4 · 2048×1024 ×4 · **2048² ×2** · 512×256 ×2 · 256² ×1 · 256×512 ×1.

**Kết luận:** bản gốc dùng **atlas bake sẵn theo nhóm UI/board** (`sactx-…-UI_Stage-…`), không có
quy hoạch atlas toàn cục. Đây là điểm **phải làm khác**: gom về 12 page theo *tần suất load*, không
theo tên board. Chi tiết §4.

---

## 1. Art direction đề xuất — **"Ink & Ember"** (Mực & Than)

> Đây là **đề xuất mới**, không mô tả lại WindWings. Bản gốc: cartoon sci-fi bão hoà, viền đen dày,
> gradient bóng, tàu có "mặt" cười. Bản đề xuất đi ngược lại 4 điểm đó.

### 1.1 Định vị

| Thuộc tính | WindWings (gốc) | **Ink & Ember (đề xuất)** |
|---|---|---|
| Sắc độ | bão hoà cao, nhiều hue | **duotone** + 1 accent, ≤ 5 màu/khung |
| Viền | outline đen dày 3–4 px | **rim light 1 phía**, không outline |
| Bóng | gradient bóng loáng | **flat + noise giấy** |
| Hình khối | tròn, dễ thương, có mắt | **hình học gắt**, không mặt |
| Nền | tinh vân rực rỡ | **giấy cắt nhiều lớp**, tối dần |
| Cảm xúc | vui, ồn | **tĩnh, cô đơn, nguy hiểm** |

### 1.2 Palette

| Vai trò | Hex | Dùng cho |
|---|---|---|
| `--ink-900` | `#0B0E14` | nền sâu nhất, viền âm |
| `--ink-700` | `#161C26` | nền board, panel |
| `--ink-500` | `#2A3442` | khối trung tính, disabled |
| `--paper` | `#E8E3D9` | chữ chính, highlight |
| `--ember` | `#FF5A2B` | **accent chính**: đạn, HP, nút CTA |
| `--ember-dim` | `#8C2F17` | accent phụ, hover tối |
| `--teal` | `#4FD1C5` | thông tin, shield, ally |
| `--gold` | `#F5C518` | phần thưởng, coin, rank cao |
| `--danger` | `#E23A3A` | máu, cảnh báo |

Quy tắc: **1 khung hình chỉ 1 accent nóng**. `ember` dành riêng cho "thứ gây sát thương".

### 1.3 Silhouette & tỉ lệ

| Đối tượng | Tỉ lệ (rộng:cao) | Quy tắc silhouette |
|---|---|---|
| Tàu player | **1 : 1,6** | 1 khối thân + tối đa 2 khối phụ; mũi nhọn hướng lên; **không cánh mảnh** |
| Drone | 1 : 1 | khối tròn/vuông, 1 chi tiết nhận dạng (nòng súng / khiên / ăng-ten) |
| Enemy thường | 1 : 1 | đối xứng tâm, đọc được ở 64 px |
| Boss | **3 : 4** | bất đối xứng, ≥ 1 khối "phá được" tách rời |
| Đạn | 1 : 2 hoặc 1 : 1 | 1 màu + 1 viền sáng, không gradient |

**Test silhouette:** thu nhỏ 64 px, tô đen 100% — vẫn phân biệt được 5 tàu bất kỳ.
Nếu không → sửa hình, không thêm chi tiết.

### 1.4 Mood & chuyển động

| Yếu tố | Đề xuất |
|---|---|
| Parallax | **3 lớp** (nền tĩnh, lớp giữa trôi 0,2×, lớp gần 0,5×), không hơn |
| Particle | ≤ 40 particle/khung, additive chỉ cho đạn & nổ |
| Screen shake | chỉ khi boss chết (0,25 s, 6 px) |
| Màu nền theo chương | ch1 `#0B0E14` → ch2 `#141018` (ngả tím) |
| Typography | 1 font sans condensed cho số, 1 serif mảnh cho tiêu đề board |

> Giữ nguyên "cảm giác" của game bắn máy bay dọc (đọc được trong 0,2 s) nhưng **đổi hoàn toàn
> ngôn ngữ thị giác**. Đây là cách thoát bản quyền mà không mất genre.

### 1.5 Nên / Không nên

| ✅ Nên | ❌ Không nên |
|---|---|
| Dùng lại **tỉ lệ khung** 9:16 và vùng ngón tay (board dưới 220 px) | Copy layout Home của bản gốc |
| Tự vẽ lại 100% sprite | Dùng `sactx-*`/PNG export từ APK |
| 1 accent nóng/khung | Dùng ≥ 3 hue bão hoà cùng lúc |
| Ký hiệu hoá boss bằng hình học | Vẽ lại nhân vật có bản quyền (QueenBee, Monkey King…) |

---

## 2. Kho sprite thật — phân nhóm

| Nhóm | Số sprite | Dung lượng PNG | Ghi chú |
|---|---:|---:|---|
| `Other` (chưa phân loại) | 1.487 | 30,7 MB | tên không theo convention → **phải phân loại tay** |
| `Bullet` (`blt*`) | 177 | 1,41 MB | nhiều nhất trong nhóm có tên |
| `Rank` | 100 | 0,87 MB | 10 league × nhiều size |
| `Background` | 98 | 6,69 MB | nặng nhất/đơn vị |
| `Boss` | 92 | 2,70 MB | 39 prefab boss |
| `PVP` (`PVP1..10`) | 91 | 1,66 MB | 10 rank PvP |
| `UI` | 69 | 1,43 MB | đặt tên thất thường |
| `Drone` | 31 | 0,58 MB | 13 drone |
| `Avatar` (`AvatarP1..24`) | 26 | 4,47 MB | 24 avatar, mỗi cái ~180 KB |
| `FX` | 14 | 0,12 MB | rất ít → FX chủ yếu là particle, không sprite |

Nguồn: đếm từ `04-asset-manifest.csv` theo tiền tố tên (script phân nhóm ở `/tmp`).

**Nhận xét:** 1.487/2.185 sprite (68%) **không có convention đặt tên** → không thể tự động sinh
sprite-list đầy đủ. Đây là lý do `sprite-list.csv` chỉ liệt kê **nhóm + size chuẩn hoá**, không
liệt kê từng sprite.

---

## 3. Size chuẩn hoá đề xuất

| Nhóm | Size gốc (nếu biết) | **Size mới** | 9-slice |
|---|---|---|---|
| Tàu player | không xác định | **256×256** | – |
| Drone | không xác định | **128×128** | – |
| Enemy thường | không xác định | **128×128** | – |
| Boss | Spine (region 100–570 px) | **512×512** hoặc Spine | – |
| Đạn player/enemy | không xác định | **24×24** | – |
| Laser | không xác định | **32×512** (tile dọc) | – |
| Nút chính | không xác định | **200×64**, border 24 | ✅ |
| Panel popup | không xác định | **720×1080**, bo 32 | ✅ |
| Icon tiền tệ | không xác định | **64×64** | – |
| Icon tài nguyên | không xác định | **96×96** | – |
| Ô shop | không xác định | **240×320**, border 16 | ✅ |
| Ô quà | không xác định | **160×160**, border 12 | ✅ |
| Nền (Bg1..7) | **1024×1024** (thật) | 1024×1024 (giữ) | – |
| Avatar | không xác định | **256×256** | – |
| Khung rank | không xác định | **256×256** | ✅ |

> Cột "size gốc = không xác định": `Sprite` rect không được serialize vào textasset/CSV nào trong
> bản dump — chỉ có **kích thước atlas page** và **kích thước region của Spine**. Muốn có size
> từng sprite phải export PNG (vi phạm ràng buộc "không phân tích APK lần nữa").

---

## 4. Atlas plan — thay `sactx-*`

### 4.1 Vấn đề của bản gốc

| Vấn đề | Bằng chứng |
|---|---|
| **67** page, **31,0 MB**, nhiều page 2048² chỉ chứa 1 board | `sactx-0-2048x2048-ETC2-UI_Stage` = **3,09 MB** |
| Page cùng atlas, khác index | `UIEvent` có `sactx-0-2048x2048` + `sactx-1-1024x1024` (cùng hash) |
| Tên page theo board → **1 board đổi = bake lại toàn page** | `UI_Stage`, `UI_FightBoss`, `UI_Begin` |
| Không có page dùng chung cho bullet/enemy | `Bullets` 2 MB, `Enemy_Air` 0,9 MB, `EnemyChapter2` 0,6 MB |

### 4.2 Đề xuất: 12 page theo **tần suất load**

| # | Page | Nội dung | Size | Format | Load khi |
|---:|---|---|---:|---|---|
| 1 | `atlas_core_ui` | button, panel, frame, slider, badge | 2048² | ETC2 RGBA | luôn |
| 2 | `atlas_currency` | 6 loại tiền + 4 icon tài nguyên | 512² | ETC2 RGBA | luôn |
| 3 | `atlas_font_num` | số bitmap cho damage/coin | 512² | ETC2 RGBA | luôn |
| 4 | `atlas_home` | keyart home, banner, avatar frame | 2048² | ASTC 6×6 | `Board_Home` |
| 5 | `atlas_maps` | map/chapter thumbnail, rank badge | 1024² | ETC2 RGBA | `Board_Maps` |
| 6 | `atlas_shop` | ô shop, pack art | 1024² | ETC2 RGBA | `Board_Shop` |
| 7 | `atlas_ships` | 25 tàu (256²) | 2048² | ETC2 RGBA | `Board_Players` |
| 8 | `atlas_drones` | 13 drone + 3 droid | 512² | ETC2 RGBA | `Board_Drones` |
| 9 | `atlas_enemy` | enemy thường (128²) | 1024² | ETC2 RGBA | vào trận |
| 10 | `atlas_bullet` | đạn player/enemy/laser | 512² | ETC2 RGBA | vào trận |
| 11 | `atlas_fx` | nổ, hit, shield, muzzle | 1024² | ETC2 RGBA | vào trận |
| 12 | `atlas_boss` | boss không dùng Spine | 2048² | ASTC 6×6 | wave boss |

Tổng: 2048²×3 + 1024²×5 + 512²×4 = **≈ 14,7 MB VRAM** (ETC2 4bpp) so với **31,0 MB** bản gốc
(nguồn: cộng `bytes` của **67** page `sactx-*` trong `04-asset-manifest.csv`) → **giảm ~53%**.

### 4.3 Quy tắc đóng gói

| Quy tắc | Giá trị |
|---|---|
| Padding giữa sprite | **4 px** (tránh bleed khi bilinear) |
| Power-of-two | bắt buộc cho page |
| Max page | 2048×2048 |
| Khoảng trống cho phép | ≤ 15% (nếu > 15% → tách page) |
| Sprite > 512 px | **không đưa vào atlas**, để standalone |
| Nén | ETC2 RGBA cho UI (cần alpha mượt), ASTC 6×6 cho keyart |
| Mipmap | tắt cho UI, bật cho background |
| Filter | Bilinear + clamp (bản gốc dùng `Linear,Linear` — nguồn: `skeleton.atlas.txt`) |

### 4.4 Giữ tương thích với save cũ

Tên sprite **không** được đổi nếu sprite đó được tham chiếu bằng `pathID` trong ScriptableObject
(`DataShopPack.listSpritePlayers[24]`…). Cách an toàn: giữ `pathID`, chỉ đổi atlas chứa nó.

---

## 5. 9-slice — spec chi tiết

| Asset | Border (L,T,R,B) | Corner | Ghi chú |
|---|---|---|---|
| `UIButton_Primary` | 24, 20, 24, 20 | 12 | không scale phần giữa theo trục dọc |
| `UIButton_Secondary` | 20, 16, 20, 16 | 10 | |
| `UIPanel_Popup` | 48, 48, 48, 48 | 32 | viền kép: ngoài sáng, trong tối |
| `UIPanel_Board` | 64, 64, 64, 64 | 40 | |
| `UICell_Shop` | 16, 16, 16, 16 | 8 | |
| `UICell_Reward` | 12, 12, 12, 12 | 6 | |
| `UISlider_Track` | 8, 0, 8, 0 | 4 | chỉ scale ngang |
| `UIBar_HP_Boss` | 6, 6, 6, 6 | 3 | |
| `UITab_Active` | 24, 12, 24, 12 | 8 | |
| `UIFrame_Rank` | 32, 32, 32, 32 | 16 | |

**Quy tắc:** 9-slice chỉ dùng khi asset có **viền đồng nhất**. Nếu hoa văn chạy dọc viền →
dùng 3-slice hoặc tile, không 9-slice.

---

## 6. Spine — 26 skeleton, spec rig lại

### 6.1 Số liệu thật

| file | bones | slots | skins | anim | 4 anim đầu |
|---|---:|---:|---:|---:|---|
| `skeleton.json` | 17 | 19 | 6 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__2.json` | 23 | 20 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__3.json` | 13 | 12 | 6 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__4.json` | 11 | 10 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__5.json` | 25 | 24 | 6 | 10 | AttackSpec, AttackSuper, AttackTopL/R |
| `skeleton__6.json` | 15 | 16 | 6 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__7.json` | 13 | 12 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__8.json` | 32 | 23 | 1 | 9 | Attack1..3, Chuyensangattack2 |
| `skeleton__9.json` | 29 | 31 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__10.json` | 10 | 23 | 6 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__11.json` | 13 | 34 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__12.json` | 13 | 12 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__13.json` | **170** | 19 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__14.json` | 10 | 9 | 6 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__15.json` | 14 | 13 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__16.json` | 9 | 8 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__17.json` | 37 | 24 | 6 | **18** | Attack01..04, Hi* |
| `skeleton__18.json` | 9 | 8 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__19.json` | 15 | 17 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__20.json` | 12 | 11 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__21.json` | 39 | 31 | **1** | 10 | Attack1..4 (tên tiếng Việt) |
| `skeleton__22.json` | 12 | 11 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__23.json` | 12 | 14 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__24.json` | 19 | 18 | 5 | 6 | Hide, Idle, Idle2, Left |
| `skeleton__25.json` | 12 | 11 | 5 | 7 | Hide, Idle, Idle2, Idle3 |
| `skeleton__26.json` | 14 | 10 | 6 | 6 | Hide, Idle, Idle2, Left |
| `Saw.json` | 18 | 6 | 1 | 5 | Fly, Fly_Idle, Idle, Idle_Fly |

Tổng: **616 bones / 446 slots / 27 file** (nguồn: parse 27 file `reverse-engineering/textassets/*.json`).

### 6.2 Bất thường phải xử lý

| # | Bất thường | Ảnh hưởng | Xử lý khi rig lại |
|---:|---|---|---|
| 1 | `skeleton__13` có **170 bones** nhưng chỉ 19 slot | 151 bone không gắn ảnh → có thể là bone điều khiển/IK | kiểm tra, cắt về ≤ 40 bone |
| 2 | `skeleton__8` và `__21` chỉ **1 skin** | không có biến thể màu | thêm `Skin2` nếu cần palette |
| 3 | `skeleton__21` animation **đặt tên tiếng Việt** (`Chuyensangattack2`, `Baydi`, `XuatHien`) | không theo convention | đổi sang `transform_attack2`, `fly`, `spawn` |
| 4 | `skeleton__17` có 18 anim `Attack01..12` + `Hi*` | 12 đòn cho 1 boss | gom còn 4 (`attack_1..4`) + 1 `combo` |
| 5 | `Saw.json` có `Fly`/`Idle_Fly` nhưng chỉ 6 slot | rig đơn giản | giữ, dùng cho enemy "cưa" |
| 6 | Tất cả page đều 512² hoặc 1024², **1 page duy nhất** | 1 boss 1 atlas → 26 atlas | gom 4 boss/page 2048² |

### 6.3 Animation set chuẩn (áp cho mọi skeleton mới)

| Anim | Loop | Thời lượng | Dùng khi |
|---|---|---|---|
| `idle` | ✅ | 1,2–2,0 s | mặc định |
| `idle_alt` | ✅ | 2,0–3,0 s | biến thể, tránh lặp |
| `spawn` | ❌ | 0,4 s | xuất hiện |
| `hide` | ❌ | 0,3 s | chết/biến mất |
| `attack_1` | ❌ | 0,5 s | đòn cơ bản |
| `attack_2` | ❌ | 0,7 s | đòn mạnh |
| `attack_3` | ❌ | 1,0 s | đòn đặc biệt |
| `hit` | ❌ | 0,15 s | trúng đạn |
| `die` | ❌ | 0,8 s | chết |
| `ui_show` | ❌ | 0,5 s | hiện trong popup/preview |

**Không dùng** `Left`/`Right` làm 2 anim riêng — thay bằng code lật `scale.x`
(`skeleton__*` bản gốc có `Left`/`Right` ở 21 skeleton → lãng phí 21 cặp clip).

### 6.4 Thông số `SkeletonDataAsset` (giữ nguyên hành vi)

| Field | Giá trị thật | Ghi chú |
|---|---:|---|
| `scale` | **0,01** (nguồn: `SkeletonDataAsset.csv`) | 100 px atlas = 1 unit world |
| `defaultMix` | **0,2 s** | blend mặc định giữa mọi anim |
| `fromAnimation` / `toAnimation` + `mixDuration` | nhiều cặp, mix **0,1** | blend riêng cho cặp `idle↔attack` |
| `atlasAssets` | 1 | 1 atlas/skeleton |
| `blendModeMaterials.applyAdditiveMaterial` | false | additive xử lý ở material riêng |

Nguồn: `SkeletonDataAsset.csv` (25 dòng). Giữ `scale = 0.01` để physics/collider khớp.

### 6.5 Quy tắc đặt tên rig mới

```
root
├─ bone/body            # thân
├─ bone/turret          # khối xoay bắn (boss)
├─ bone/gun_l, gun_r    # nòng
├─ bone/part_1..3       # khối phá được (HP riêng)
└─ bone/fx_muzzle       # điểm spawn particle
```
Slot: `art_<part>`; skin: `default`, `elite`, `damaged`.
Anim: `<action>_<variant>` — **snake_case**, không dấu.

---

## 7. Audio — 69 clip, 92 `SoundClip`

### 7.1 Phân loại (theo tên + vai trò)

| Nhóm | Số | Ví dụ | Loop |
|---|---:|---|---|
| **BGM** | 9 | `Bgm_Home1/2`, `Bgm_Boss1/2`, `Bgm_Game1..5` | ✅ |
| **Boss SFX** | 6 | `Sfx_BossLaser1`, `Sfx_Alarm1/2`, `Sfx_Robot0..3` | một phần |
| **Enemy shoot** | 20 | `Sfx_EnemyShoot1..20`, `Sfx_EnemyShoot30` | ❌ |
| **Player shoot** | 2 | `Sfx_Shot1/2` | ❌ |
| **Collect** | 6 | `Sfx_CollectCoin/Droid/Hp/Overdrive/Power/SupperPower` | ❌ |
| **Destroy/explosion** | 13 | `Sfx_Destroy1..12`, `Sfx_PlayerDestroy` | ❌ |
| **UI** | 4 | `Sfx_ClickUp`, `Sfx_ClickDown`, `Sfx_Change`, `Sfx_Whoosh1` | ❌ |
| **Transform/skill** | 24 | `Sfx_Transform1..24` | ❌ |
| **Loop môi trường** | 4 | `Sfx_Flamethrower`, `Sfx_Flying`, `Sfx_LightningLoop`, `Sfx_SawLoop` | ✅ |
| **Kết trận** | 2 | `Sfx_Victory`, `Sfx_Defeat` | ❌ |

Nguồn: `SoundClip.csv` (92 dòng `m_Name`) + `15-audio.md` (69 `AudioClip`).

**Chênh lệch 92 vs 69:** `SoundClip` là **MonoBehaviour map enum→AudioClip**, 92 entry nhưng chỉ
69 clip thật (nhiều entry trỏ cùng clip, ví dụ `Sfx_Shot1/2` có thể cùng file). ⇒ Khi dựng lại:
**1 enum = 1 AudioClip**, 69 là con số budget đúng.

### 7.2 Tên tiếng Việt trong file gốc

`Bắn Đạn Dính Trên Màn Hình`, `Súng Máy Bắn nhiều Viên Liên Tục Tốc Độ Nhanh`,
`Âm Nổ Player`, `Địch Xanh Bắn Đạn Nhanh`, `Địch Đất Đỏ Bắn`, `Súng Boss Vỗng` (mojibake
`S£ng Boss VÖng`), `Boss nhện đỏ laze` — **10/69 clip đặt tên tiếng Việt** ⇒ đội làm game là
người Việt. **Không** dùng lại các file này (bản quyền + tên lộ nguồn).

### 7.3 Spec audio mới

| Hạng mục | Đề xuất |
|---|---|
| Format | Vorbis q=0.4 (BGM), ADPCM (SFX ngắn) |
| Sample rate | 44.100 Hz (thống nhất; gốc lẫn 16/22/48 kHz) |
| Kênh | mono cho SFX, stereo cho BGM |
| Loudness | BGM −18 LUFS, SFX −14 LUFS, peak ≤ −1 dBTP |
| Số clip budget | **48** (9 BGM + 39 SFX) thay vì 69 |
| Biến thể shoot | 3 biến thể/loại, random pitch ±5% thay vì 20 file riêng |
| Ducking | BGM giảm 6 dB khi boss xuất hiện |

Lý do cắt 20 `Sfx_EnemyShoot*` → 3: tai người chơi không phân biệt được 20 biến thể khi bắn
liên tục; pitch randomization cho kết quả tương đương với 1/7 dung lượng.

---

## 8. Legal checklist — trước khi dùng bất kỳ asset nào

| # | Việc phải làm | Trạng thái |
|---:|---|---|
| 1 | **Không** dùng `sactx-*`, PNG, Spine, audio export từ APK | ⛔ cấm tuyệt đối |
| 2 | **Không** dùng tên riêng của game gốc (WindWings, tên 24 tàu, 12 drone, 20 boss) trong bản phát hành | ⛔ |
| 3 | **Không** dùng UI layout 1:1 (kể cả wireframe — chỉ dùng cấu trúc chức năng) | ⛔ |
| 4 | Vẽ lại 100% sprite theo art direction §1 | ✅ bắt buộc |
| 5 | Thu âm/mua license audio mới; ghi nguồn từng clip vào `CREDITS.md` | ✅ bắt buộc |
| 6 | Font: chỉ dùng font có license thương mại (bản gốc dùng Noto/Roboto/Agency/Amiri — **không** copy file `.ttf` từ APK) | ✅ |
| 7 | Kiểm tra trademark "WindWings", "GCenter", "GCENTER VIET NAM TECHNOLOGY JSC" — không xuất hiện trong store listing | ⛔ |
| 8 | Nếu giữ cơ chế (arena league, battle pass) → OK, cơ chế không được bảo hộ; **tên league** (Bronze…Champion) là generic, dùng được | ✅ |
| 9 | Tên boss lấy từ thần thoại/dân gian (Monkey King, Dracula, Hydra…) là public domain — **nhưng** hình dạng cụ thể thì không | ⚠️ |
| 10 | Lưu log: mọi asset mới phải có `source`, `license`, `author` trong metadata | ✅ |

> Ghi chú pháp lý: repo này là **tài liệu phân tích kỹ thuật** (reverse engineering cho mục đích
> học tập/nghiên cứu). Việc **tái sử dụng asset** là hành vi khác và **không** được bảo vệ bởi
> mục đích nghiên cứu. Việc **tái sử dụng asset** là hành vi khác và không được bảo vệ bởi
> mục đích nghiên cứu. Xem `assets_samples/00_LICENSES` cho các bộ CC0 dùng thay thế.

---

## 9. Còn thiếu / phải đoán

| # | Điều | Trạng thái |
|---:|---|---|
| 1 | Kích thước pixel **từng sprite** | **không xác định được từ APK** — chỉ có size atlas page + region Spine |
| 2 | Border 9-slice thật của sprite UI | **không xác định** — `Sprite.border` không nằm trong dump |
| 3 | Mapping `skeleton__N` → nhân vật nào | **không xác định** — JSON không có field `name`; phải so khớp thủ công bằng mắt |
| 4 | Pivot từng sprite | **không xác định** |
| 5 | 1.487 sprite "Other" là gì | **C** — tên không theo convention |
| 6 | `Saw` (skeleton thứ 27) dùng cho enemy nào | **C** — có `Fly`/`Idle_Fly` → khả năng enemy bay có cưa |
| 7 | 23 `SoundClip` không có `AudioClip` tương ứng | **C** — có thể trỏ clip trùng hoặc clip bị strip |
| 8 | `skeleton__13` 170 bone là rig gì | **D** — bất thường, cần xem trực quan |
| 9 | Có sprite nào > 512 px không | **không xác định** (không có rect) |
| 10 | Atlas gốc dùng Crunch/ETC2 quality nào | **C** — tên `ETC2` cho biết format, không cho biết quality |

---

## 10. Nguồn

`docs/apk-analysis/04-unity-assets.md` · `04-asset-manifest.csv` · `SkeletonDataAsset.csv` ·
`SoundClip.csv` · `15-audio.md` · `12-localization.csv` ·
`reverse-engineering/textassets/skeleton*.json` · `reverse-engineering/textassets/*.atlas*.txt` ·
`reverse-engineering/scriptableobjects/SkeletonDataAsset.csv` (27 instance) ·
`reverse-engineering/scriptableobjects/SoundClip.csv` (92 entry) ·
`docs/spec/sprite-list.csv`.

**Liên quan:** `Gun_Attack.csv` có cột `shootAudioClipName` (13 clip bắn khác nhau) — map id →
`AllClipName` ở `COMBAT.md` §2.3.
