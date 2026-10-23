# ANIMATION — 4 hệ, đọc được cái nào, còn gì để design

> Nguồn: `04-unity-assets.md` (census object của `data.unity3d`) · `class-inventory.csv` (số instance) ·
> `reverse-engineering/textassets/skeleton*.json` (27 rig Spine) · `dump.cs` (field + method signature).
> Không có số nào ở đây lấy từ việc chạy lại APK.
>
> **Đơn vị đếm:** *rig* = file skeleton · *instance* = số object trong `data.unity3d` · *animation* = tên trong `animations{}`.

## 0. Trả lời ngắn

| Hệ | Có trong APK | Đã đọc | Kết luận |
|---|---:|---:|---|
| **Spine** (xương) | 27 rig · **185** animation · 616 bone | **100%** | đủ để dựng lại nhịp |
| **Unity Animator** | **791** clip · **308** controller · **5.792** `Animator` | **0 %** curve giải được (**9,19 MB** chưa giải) · **100 % tên** | **3.620/5.792 = 62,5 % là UI** (`Board_*` 2.938 · `Popup` 675 · `Menu` 7); **enemy/boss 154** theo đếm lại — con số **203** không tái lập được (§4.5, `ANIMATION_GAPS.md` §4) |
| **Procedural** (`Rotate`) | **1.120** instance | class 100% · tham số 0% | biết công thức, chưa biết tốc độ |
| **Flipbook sprite** | **28** chuỗi · 160 ảnh / 2.185 `Sprite` | 100% | game **hầu như không dùng** |

⇒ Hiểu được **cấu trúc và nhịp**, chưa dựng lại được **chuyển động cụ thể của boss**.
Khoảng thiếu đã đong được chính xác: **791 clip** + **308 controller** + tham số prefab.

## 1. Census — animation chiếm bao nhiêu trong `data.unity3d`

| Type | Số object | Ghi chú |
|---|---:|---|
| `GameObject` | **238.324** | |
| `Transform` | **228.432** | bảng còn thiếu để ghép 100% (xem `DATA_SYNC.md` §7) |
| `MonoBehaviour` | **125.453** | |
| `SpriteRenderer` | **62.815** | |
| `Animator` | **5.792** | hệ animation chính |
| `ParticleSystem` | **4.845** | + `ParticleSystemRenderer` 4.845 |
| `MeshRenderer` | 11.262 | |
| `LineRenderer` | 707 | |
| `AnimationClip` | **791** | **chưa export** |
| `AnimatorController` | **308** | **chưa export** |
| `TrailRenderer` | 273 | |
| `Sprite` | 2.185 | |
| `SpriteAtlas` | 66 | |
| `AudioClip` | 69 | |
| `Material` | 261 | |
| `Shader` | 70 | |

Tỷ lệ: **1 controller → 18,8 `Animator`** (5.792 / 308) · **1 clip → 7,3 `Animator`** (5.792 / 791).

> **Nhận định (mức A):** 5.792 `Animator` so với **117** `SkeletonAnimation` — tỷ lệ **49 : 1**.
> Nghĩa là **Spine không phải hệ animation chính** của game. Nó là hệ của một nhóm nhỏ
> (tàu đặc biệt, vài boss). Phần lớn chuyển động còn lại chia cho `Animator` + `Rotate`.
>
> **Điều kiện lật ngược:** nếu 5.792 `Animator` chủ yếu là **UI** (nút, popup) thì tỷ lệ này
> không nói gì về enemy. Cần đếm `Animator` theo cha — hiện chưa có bảng Transform để tách.

## 2. Spine — đọc được 100%

**Tổng:** 27 rig · **185** animation · **616** bone · **446** slot · **577** region · Spine **3.8.99** (1 rig 3.8.84).

> **Đã sửa 23/10 (kiểm lại bằng `datas/spine_anim.json.gz`):** bản trước ghi **180** ở dòng này.
> 180 là tổng của **26 rig `skeleton*`**; `Saw` có thêm **5** (`Fly · Fly_Idle · Idle · Idle_Fly ·
> Teleport`), nên tổng thật là **185**. Con số 616 bone thì vẫn đúng và **đã gồm** Saw — bản cũ
> trộn hai cách đếm trong cùng một dòng.

Phân bố animation mỗi rig: **6** × 21 rig · **7** × 1 · **9** × 1 · **10** × 2 · **18** × 1.

### 2.1 Bốn rig có animation đòn (boss)

| Rig | Bone | Anim | Các đòn | Thời lượng |
|---|---:|---:|---|---|
| `skeleton__17` | 37 | **18** | `Attack01` … `Attack08` | **0,40 s** mỗi đòn |
| `skeleton__21` | 39 | 10 | `Attack1` · `Attack2` · `Attack3` · `Attack4` | 33,37 · 10,00 · 12,67 · 0,70 s |
| `skeleton__8` | 32 | 9 | `Attack1` · `Attack2` · `Attack3` | 9,00 · 9,00 · 18,00 s |
| `skeleton__5` | 25 | 10 | `AttackSpec` · `AttackSuper` · `AttackTopL` · `AttackTopR` | 0,43 · 0,50 · 0,60 · 0,60 s |

`__21` còn có `Dead` 2,33 s · `Baydi` (bay đi) 3,00 s · `UIShow` 3,67 s — **đủ vòng đời một trận boss**.
`__8` có `Die` 4,83 s · `Chuyensangattack2/3` (chuyển sang attack 2/3) — **clip chuyển trạng thái**, tức có state machine.
`__17` mỗi đòn chỉ **5 key** trong 0,40 s ⇒ gần như **một pose giữ ngắn rồi bắn**, không phải đòn vẽ tay dài.

### 2.2 Hai mươi hai rig không có đòn (tàu / vật thể)

21 rig dùng **cùng một bộ 6 animation**, cùng thời lượng:

| Animation | Thời lượng | Vai trò suy ra |
|---|---:|---|
| `Idle` | 0,00 s (**0 key**) | trạng thái nghỉ — không animate |
| `Idle2` | **1,00 s** | nhấp nhô / thở |
| `Show` | **0,67 s** | xuất hiện |
| `Hide` | **0,33 s** | biến mất |
| `Left` | **0,33 s** | nghiêng trái |
| `Right` | **0,33 s** | nghiêng phải |

> **Nhận định (mức B):** đây là **API của một state machine dùng lại**, không phải 6 clip trang trí.
> `Left` / `Right` = nghiêng khi di chuyển ngang; `Show` / `Hide` = spawn / despawn;
> `Idle2` = 1 vòng lặp 1,00 s.
>
> **Điều kiện lật ngược:** nếu `Left`/`Right` chỉ xuất hiện trên tàu người chơi thì nhóm 21 rig này
> là **tàu**, không phải enemy — và enemy thường không có Spine. Cần bảng map rig → prefab để chốt.

Ngoại lệ đáng chú ý:

| Rig | Khác biệt | Gợi ý |
|---|---|---|
| `skeleton__25` | thêm `Idle3` 0,67 s | 3 trạng thái nghỉ |
| `skeleton__14` | `Idle2` 0,67 s · bone `Gun` | có súng gắn xương |
| `skeleton__26` | bone `GunDB` · `GunL` | 2 hướng súng |
| `skeleton__4` | bone `DongcoL` · `DongcoR` | 2 động cơ trái/phải |
| `skeleton__13` | **170 bone** · `Tong_Ranh` `Duoi_Ranh_1` `Canh_Nho_Phu_Ranh_1` | rồng, 4 cánh + đuôi |
| `Saw.json` | 5 animation `Fly` `Fly_Idle` `Idle` `Idle_Fly` | chướng ngại xoay |

### 2.3 Event trong Spine — mốc bắn nằm ngay trong rig

**8 event định nghĩa**, **21 lần dùng** trong timeline:

| Event | Số lần dùng | Nghĩa |
|---|---:|---|
| `Shot` | **12** | bắn thường |
| `Stop` | **5** | dừng |
| `Banplasma` | 1 | bắn plasma |
| `Spec` | 1 | đòn đặc biệt |
| `TopL` | 1 | bắn trên-trái |
| `TopR` | 1 | bắn trên-phải |

> **Nhận định (mức A):** tên event **trùng tên animation của `skeleton__5`** (`AttackSpec`, `AttackTopL`, `AttackTopR`).
> Tức rig tự mang **mốc thời gian bắn** — không cần đọc `Gun_Attack` cũng biết đạn ra ở giây thứ mấy.
> Đây là mắt nối **animation → đòn đánh** đã có sẵn, không phải suy đoán.

### 2.4 Metadata rò rỉ từ máy nghệ sĩ

3/27 rig còn giữ path Windows trong `skeleton.audio`:

| Rig | Path còn lại |
|---|---|
| `skeleton__13` | `C:/Users/GCenter/Desktop/WinWingPro/May Bay Plane Tree` |
| `skeleton__9` | `C:/Users/GCenter/Desktop/WinWingPro/May Bay Halloween` |
| `skeleton__16` | `F:/THAI UI/BanMayBayB52…/SpineChinhThuc3(3.7.94)/1022ver2/New folder` |

> **Nhận định (mức A):** tên nội bộ của 3 rig là **Plane Tree**, **Halloween**, **B52**.
> Đây là tên nghệ sĩ đặt, không phải tên kỹ thuật ⇒ dùng để đoán 24 rig còn lại khi có bảng map.

Kích thước rig (khung vẽ): nhỏ nhất `__24` **355×311**, lớn nhất `__21` **993×741**.

## 3. Unity Animator — 791 clip chưa đọc

### 3.1 Cầu nối clip → đòn đánh **đã có trong mã**

`BossAnimationEvents`:

```
public Action onStateExit;
public Dictionary<string, Action> allStartAttackActions;
public Dictionary<string, Action> allStopAttackActions;
```

**Khoá của dictionary là `string`** — tên clip hoặc tên state. ⇒ chỉ cần có 791 clip + prefab là đọc được
"clip nào bật đòn nào", đúng cơ chế đã dựng sẵn, không phải thiết kế lại.

`Boss9_AnimationEvents` — callback riêng cho từng đòn:

| Callback | Nghĩa |
|---|---|
| `onAttackStartEvent` / `onAttackEndedEvent` | mốc đầu/cuối đòn |
| `onHandAttackEvent(Action<bool>)` | đòn tay |
| `onCircleAttackEvent` | đòn vòng tròn |
| `onDropAttackEvent` | đòn thả |
| `onCoreAttackEvent` | đòn lõi |
| `die` | chết |

⇒ **Boss9 có 4 đòn phân biệt** (tay · vòng tròn · thả · lõi), đọc từ tên callback.

### 3.2 Đếm lớp AnimationEvents

| Lớp | Instance |
|---|---:|
| `Boss9_AnimationEvents` | **7** |
| `BossAnimationEvents` (generic) | 5 |
| `Boss18_AnimationEvents` | 5 |
| `Boss12_AnimationEvents` | 5 |
| `Boss4_AnimationEvents` | 4 |
| `Boss15_AnimationEvents` | 4 |
| `Boss8_AnimationEvents` | 3 |
| `Boss7_AnimationEvents` | 3 |
| `Boss6_AnimationEvents` | 3 |
| `Boss5_AnimationEvents` | 3 |
| **Tổng** | **42 / 10 họ** |

Cộng `AnimationEventHandler` **30** (`UnityEvent endedEvent` + `OnEnded()` = mốc "clip kết thúc").

> **Nhận định (mức B):** **9 boss** có lớp event riêng (`Boss4` · `5` · `6` · `7` · `8` · `9` · `12` · `15` · `18`),
> cộng **4** rig Spine có đòn. Hai nhóm này có thể trùng nhau — chưa chồng lên được vì thiếu bảng map.

### 3.3 Đã export (bản `e162065`) — **791 clip, nhưng curve bị stream**

`raw/typetrees/native-types.jsonl.gz`: `AnimationClip` **791** · `AnimatorController` **308**.

| Chỉ số `AnimationClip` | Giá trị |
|---|---:|
| Tên khác nhau | **226** (791 − nhiều bản sao theo prefab) |
| Tên phổ biến | `Idle` **82** · `idle` **80** · `Xuathien` 41 · `Setup` 37 · `Appear` 26 |
| `m_StopTime > 0` | **707 / 791** |
| Thời lượng median | **1,9 s** · min 0,02 · max **75,0** |
| Phân bố | 1,0 s ×76 · 2,0 s ×45 · 0,5 s ×33 |
| Clip lặp (`m_LoopTime`) | **251** |
| Clip có event | **318** — tổng **793 event** |
| `m_SampleRate` | **60 fps** ×764 · 80 ×4 · 50 ×4 |

| Chỉ số `AnimatorController` | Giá trị |
|---|---:|
| Số clip tham chiếu (tổng) | **793** — khớp đúng **793 event** |
| Max clip/controller | **28** · controller rỗng: **1** |
| **`m_StateMachineBehaviours > 0`** | **0 / 308** |

> **Nhận định (mức A) — quan trọng:** **0 / 308 controller có StateMachineBehaviour**.
> Nghĩa là `BossAnimationEvents` (§3.1) **không** gắn qua state machine — nó nghe
> **event của clip** (`m_Events`, 793 cái trên 318 clip). Đó là lý do `allStartAttackActions`
> là `Dictionary<string, Action>`: khoá là **tên event**, không phải tên state.

> ⚠ **Curve không đọc được bằng typetree:** **791 / 791** clip có
> `m_FloatCurves__count = m_PositionCurves__count = … = 0`. Curve nằm ở **`m_StreamedClip`** —
> nhưng **dữ liệu vẫn còn trong asset**, đếm được bằng `m_MuscleClipSize`:

| `m_MuscleClipSize` (bản `68ce86a7`) | Giá trị |
|---|---:|
| Clip `> 0` | **782 / 791** |
| Tổng dung lượng curve | **9.186.264 B** (9,19 MB · 8,76 MiB) |
| Median · lớn nhất | **5.076 B** · **175.712 B** |
| Clip `= 0` | **9** — `Idle` · `idle` · `Setup` · `Test` · `UILock` · `Xuathien` · `Laze` · `Player4` · `Chuyensangattack3` (giữ pose **1,0 s**) |

> ⇒ Đọc được **tên + nhịp + event**; **dáng chuyển động** thiếu **decoder**, **không** thiếu dữ liệu
> (`UNITY_RULES` §4.2). Thêm nữa: **0 / 791** clip có `m_PPtrCurves` ⇒ **không clip nào là flipbook**
> (`UNITY_RULES` §4.1).

### 3.5 Đã thử `parse_as_object()` — **cũng 0 keyframe**: giới hạn của **bộ đọc**, không phải của dữ liệu

Bản `ae1f2be` chạy `tools/apk-analyze/anim_curves.py` dùng UnityPy `parse_as_object()`
trên **791 clip**:

| Kết quả | Số |
|---|---:|
| Clip parse được | **791 / 791** |
| Lỗi parse | **0** |
| **Clip có keyframe** | **0** |
| **Tổng keyframe** | **0** |

⇒ **Hai đường đọc độc lập đều trả 0.** Không phải lỗi tool: dữ liệu nằm trong
**`m_StreamedClip`** ở định dạng nén riêng, phải có **bộ giải mã viết riêng** (đọc `m_StreamedClip`
dạng mảng byte rồi dựng lại bảng curve binding + keyframe).

**Kích thước đã đo (bản `68ce86a7`):** `m_MuscleClipSize` = **9.186.264 B** trên **782 / 791** clip
(median **5.076 B**, max **175.712 B**; 9 clip = 0). ⇒ **Dữ liệu có thật**; "0 keyframe" là
**giới hạn của reader**, không phải của asset (`UNITY_RULES` §4.2).

> **Nhận định (mức A) — sửa lại điều tôi đã viết:** tôi từng ghi *"muốn có keyframe chỉ cần
> `parse_as_object()`"*. **Sai** — đã thử, ra 0. Điều kiện để có curve là **viết decoder cho
> streamed clip**, không phải đổi reader.
>
> **Nhưng không phải bế tắc:** cái quyết định cảm giác đòn boss **đã có** — `m_StopTime` (1,9 s median),
> 793 event chia đúng trên các clip, và `allStartAttackActions` với khoá là tên event.
> Timing dựng lại được; chỉ **dáng chuyển động** của Mecanim là thiếu.

**Điều kiện lật ngược:** nếu giải mã được `m_StreamedClip` thì 791 clip cho ra keyframe thật —
đây là việc **làm được** (AssetStudio/AssetsTools.NET có bộ đọc clip đầy đủ), chỉ là chưa làm.

### 3.4 Vì sao chưa đọc — và vì sao biết là đọc được

`04-asset-manifest.csv` chỉ chứa **`Sprite` 2.185 + `Texture2D` 653**. Không có `AnimationClip`,
không có `AnimatorController`.

⇒ **791 clip chưa từng được export**, không phải bị lỗi hay không tồn tại.

Điều kiện để đọc (mức B, chưa chạy): `AnimationClip` chứa `m_Curves` + `m_SampleRate` + `m_AnimationClipSettings`;
`AnimatorController` chứa `m_AnimatorParameters` + state machine. Cả hai là **cùng loại object**
mà UnityPy đã đọc được cho `Sprite`/`Texture2D`/`MonoBehaviour` — chỉ là chưa có trong `TARGETS`.

## 4. Procedural — 1.120 instance, biết công thức chưa biết số

| Lớp | Instance | Tham số serialize |
|---|---:|---|
| `Rotate` | **1.044** | `speedRotate` · `delay` · `SetSpeed(mul)` · `SetToAngle(angle, cb)` |
| `Enemy_Rotate` | 35 | |
| `Rotate2` | 27 | |
| `Drone_AutoRotate` | 8 | |
| `Rotate1` | 7 | |
| `ChildRotateAround` | 6 | |
| **Tổng** | **1.127** | |

`Rotate.Update()` xoay theo `speedRotate` mỗi frame, chờ `delay` trước khi chạy;
`SetToAngle(góc, callback)` xoay tới góc chỉ định rồi gọi callback.

**Nhưng** giá trị `speedRotate` nằm trong **prefab**, mà prefab chưa export ⇒ **mức C**:
biết cơ chế xoay, chưa biết con nào xoay bao nhiêu độ/giây.

> **Nhận định (mức A):** 1.044 `Rotate` trên 109 prefab enemy/boss + effect ⇒ đây là
> **"animation" phổ biến nhất của game**: xoay sprite (quạt, tua bin, hành tinh, khiên, vòng năng lượng).
> Hệ quả cho design: phần lớn chuyển động không cần rig — chỉ cần **sprite + trục xoay + tốc độ**.

## 4.5 Enemy — animation của enemy **gồm những gì** (đếm mới 23/10)

> Câu hỏi: *"đã có animation của enemy chưa?"* — **Có, nhưng chia làm hai nửa: một nửa đọc được 100 %,
> một nửa chỉ có TÊN.** Bảng dưới đếm trên **109 prefab enemy/boss thực sự được spawn**.

| Hệ | Instance trên enemy | Phủ prefab | Đọc được | Ghi chú |
|---|---:|---:|---|---|
| **`Enemy_Movement`** (di chuyển theo path) | **981** | **109 / 109 = 100 %** | công thức + tham số | `listSpeeds` · `facingMove` · `isTurret` · `endOfPathInstruction` · `parentRotate` |
| **`Enemy_Appear`** (xuất hiện / biến mất) | **914** | **107 / 109** | **cơ chế**, không tham số | tree serialize **rỗng** — không field nào |
| **Animator** (clip Unity) | **203** | **87 / 109 = 79,8 %** | **tên clip** · 0 % curve | 36 root `Boss-*` = **92** instance; 22 prefab **không có** Animator |
| **`Enemy_Rotate`** (xoay) | **35** | 1 root roster | ✅ đủ | trap `W2-30043` (7) · `W2-30042` · `W2-30056` · `W2-30036` · `W2-30055` |
| **Spine** (xương) | **17** `Enemy_HitSkeletonRenderer` | **3 root** | ✅ đủ | **`Boss-39001` / `Boss-39002` / `Boss-39003`** — sửa 23/10, trước ghi 2; xem `ANIMATION_GAPS.md` §2b |
| **Flipbook** | **0** | 0 | — | 28 chuỗi/160 ảnh toàn game ⇒ enemy **không** dùng khung hình |

### (a) Nửa **đọc được**: chuyển động thật của enemy là **procedural**

`Enemy_Movement` phủ **100 %** prefab. Đây **không** phải animation clip — nó là **di chuyển theo đường
path** + hướng mặt + tốc độ theo danh sách. Cộng `Enemy_Appear` (107/109) và `Rotate`/`Enemy_Rotate`
(1.127 instance toàn game) ⇒ **cái người chơi cảm nhận là "enemy động"** đến từ:

```
path (PathCreator) → Enemy_Movement.listSpeeds → hướng/mặt → xoay (Rotate) → particle
```

**Không có khung hình nào** trong đường này. Đây là lý do một enemy chỉ cần **1 sprite** (§5).

### (b) Nửa **chỉ có tên**: 791 clip Animator — biết *tên*, không biết *pose*

`datas/anim_clips.json.gz` (791 clip · **226 tên khác nhau**) — phân bố tên:

| Clip | Số | Nghĩa |
|---|---:|---|
| `Idle` + `idle` | **82 + 80 = 162** | phần lớn thời gian enemy **đứng yên** |
| **`Xuathien`** | **41** | **"xuất hiện"** — tên tiếng Việt của hoạ sĩ (§2.4) |
| `Setup` | 37 | dựng/khởi tạo |
| `Appear` | 26 | xuất hiện (bản tiếng Anh) |
| `Active` + `active` | 19 + 8 | bật |
| `attack1` … `attack8` + `Attack1..3` + `Attack` | **≈ 135** | **bộ đòn của boss** |
| `UIShow` | 14 | **UI**, không phải enemy |
| `Die` | 10 | chết |
| `move_in` | 3 | bay vào |

> **Đếm quyết định:** `keyframe_total = 0` ở **791/791** clip. Tên + thời lượng (median **1,9 s**) thì có,
> **curve thì không** — vì chúng bị **stream** (`m_StreamedClip`, §3.5). ⇒ **chưa dựng lại được pose**.

### (c) `Animator` 5.792 — hoá ra **62,5 % là UI**, không phải enemy

| Bucket | Instance | % |
|---|---:|---:|
| **UI** (`Board_*` 2.938 · `Popup` 675 · `Menu` 7) | **3.620** | **62,5 %** |
| prefab **wave** (`Wave_*`) | 912 | 15,7 % |
| khác (effect, shop, item…) | 1.057 | 18,3 % |
| **enemy / boss trong roster** | **203** | **3,5 %** |

⇒ Con số "5.792 `Animator`" trong §0 **không** phải 5.792 animation của enemy. Enemy thật: **203**.
(Đóng một phần câu hỏi §7 #10.)

### (d) Trả lời thẳng

| Câu | Trả lời |
|---|---|
| **Enemy có animation không?** | **Có** — 87/109 prefab có Animator; 100 % có di chuyển procedural |
| **Đã dựng lại được chưa?** | **Chưa.** Tên clip + nhịp: **có**; pose/khung hình: **không** — nhưng **9,19 MB curve có trong asset** (`UNITY_RULES` §4.2), thiếu **decoder** chứ không thiếu dữ liệu |
| **Bao nhiêu %?** | Theo **hệ**: procedural **100 %** · clip **0 % curve giải được / 100 % tên / 100 % dung lượng curve** · Spine **100 %** (nhưng chỉ 2 boss) |
| **Cần gì để dựng lại?** | **1 decoder `m_StreamedClip`** — không phải export thêm asset |
| **Có chặn design không?** | **Không.** Bản clone cần *cảm giác*, không cần pose gốc: dùng `Enemy_Movement` + `Rotate` + 1 sprite (§5) |

---

## 5. Sprite thật sự dùng làm gì

**2.185 `Sprite`** · **62.815 `SpriteRenderer`** · 577 region Spine.

Đếm chuỗi frame (tên region kết thúc bằng số, ≥ 3 ảnh liên tiếp): **28 chuỗi / 160 ảnh** = **27,7%** region.
Chuỗi lớn nhất: **13 ảnh** (`skeleton.atlas__14`) · 12 ảnh (`__9`) · 11 ảnh (`__20`).

> **Nhận định (mức A):** nếu game dùng flipbook thì phải có hàng trăm chuỗi 8–16 ảnh. Có **28** ⇒
> **flipbook gần như không tồn tại**. Enemy thường = **1 sprite tĩnh + transform chuyển động**;
> "animation" mà người chơi cảm nhận đến từ **di chuyển · xoay · particle**, không từ khung hình.
>
> **Hệ quả trực tiếp cho design:** không cần vẽ 8 khung cho mỗi enemy. Cần **1 sprite đẹp + trục xoay + trail**.
> Đó là lý do 70 prefab enemy chỉ cần 2.185 sprite cho cả game.

Lớp hiệu ứng đi kèm: `Sub_Effect` **113** · `Effect_Timer` **95** · `FlameParticles` **59** ·
`ParticleCollision` 23 · `EffectGlow` 6 · `ParticleSystemUnscaled` 12.

## 6. Vậy đã hiểu để design chưa

| Mảng | Trạng thái | Còn thiếu | Gỡ bằng |
|---|---|---|---|
| Hình dạng + nhịp enemy thường | **đủ** | tốc độ xoay từng con | prefab field (C) |
| Nhịp xuất hiện / biến mất | **đủ** (`Show` 0,67 · `Hide` 0,33) | — | — |
| Đòn của boss dùng Spine | **đủ tên + thời lượng + mốc event** | pose từng khung | JSON đã có, chỉ cần dựng |
| Đòn của boss dùng Animator | **danh mục + nhịp** (791 clip · 226 tên · median 1,9 s · 793 event) | **curve** (streamed, đã thử 2 đường = 0) | decoder `m_StreamedClip` |
| Chuyển cảnh giữa các đòn | **thiếu** | state machine | export `AnimatorController` |
| FX / particle | biết số lớp | tham số | prefab |

**Trả lời thẳng:** đủ để dựng **bản clone có cảm giác giống**, chưa đủ để dựng lại **đúng** chuyển động boss.

Cái quyết định cảm giác đã đo được hết:

- nhịp spawn **1,0 s** (`SCRIPTS.md` §3)
- enemy **dừng lại trong màn** 924/981 = **94,2%** (§4)
- xoay liên tục bằng `Rotate` **1.044** instance
- bộ 5 trạng thái chuẩn `Idle2` 1,0 · `Show` 0,67 · `Hide` 0,33 · `Left` 0,33 · `Right` 0,33

## 7. Còn thiếu / phải đoán

| # | Việc | Mức | Cách gỡ |
|---:|---|---|---|
| 1 | Rig nào thuộc prefab nào | **B** (một phần) | `Transform.m_Father` **đã có sẵn** — đi ngược lên root được. Kết quả 23/10: Spine hit-skeleton nằm trên **3** prefab (39001/39002/39003, §4.5); `skeleton__21` = rig của **Boss-39002** (khớp **8/8** tên state của `Boss1_Director`). **3 rig có đòn còn lại chưa map** — cần typetree `SkeletonRenderer`, xem `ANIMATION_GAPS.md` §3 |
| 2 | ~~791 clip tên gì, dài bao nhiêu~~ | **A** | ✅ xong — 226 tên · median 1,9 s · 793 event (§3.3) |
| 2b | **keyframe curve** của 791 clip | **B** | **Dữ liệu CÓ**: `m_MuscleClipSize` **9.186.264 B** trên **782/791** clip — thiếu **decoder `m_StreamedClip`**, không thiếu export (`UNITY_RULES` §4.2) |
| 3 | `speedRotate` / `delay` từng object | **C** | export field prefab |
| 4 | 25 boss còn lại animate bằng gì | **B** | Đếm lại 23/10: chỉ **4/27** rig Spine có animation đòn; **92 `Animator` trên 36 prefab `Boss-*`** + 44 class `*_Director` lo phần còn lại. **Chưa** nối từng boss với rig/clip cụ thể (`ANIMATION_GAPS.md` §2c–2d) |
| 5 | `allStartAttackActions` có bao nhiêu khoá | **C** | export field prefab (dictionary) |
| 6 | Clip nào dùng chung giữa nhiều boss | **C** | export `AnimatorController` |
| 7 | Thứ tự pha (clip nào trước clip nào) | **C** | export 34 `*_Director` (**60** instance) + 3 `AttackPhases` = **63** |
| 8 | `Idle` có 0 key nghĩa là "đứng yên" hay "giữ pose đầu" | **B** | đọc `SkeletonRenderer` init |
| 9 | Nhóm 21 rig bộ 6 animation là **tàu** hay **enemy** | **B** | vẫn mở, nhưng **hết mơ hồ**: `m_Name` của 27 `SkeletonDataAsset` = **26 × `skeleton_SkeletonData`** + 1 × `Saw_SkeletonData` ⇒ tên **thật sự trùng**, không phải exporter làm mất (`UNITY_RULES` §8). Chỉ còn 1 đường: export `SkeletonAnimation.m_SkeletonDataAsset` (**117** component) để nối |
| 11 | **Time + `functionName`** của **793** animation event | **B** | `m_Events` là mảng struct **không nén** — dump hiện tại chỉ lấy `__count` ⇒ **export độ sâu 3** là ra (`UNITY_RULES` §4.3) |
| 12 | Controller → clip → **tên state** | **B** | `m_AnimationClips` **793** PPtr + `m_TOS` **3.871** tên state nằm trong 308 controller (`UNITY_RULES` §5) |
| 10 | ~~`Animator` 5.792 phân bố enemy / UI / FX~~ | **A** | ✅ xong (§4.5c): **UI 3.620 (62,5 %)** · wave 912 · khác 1.057 · **enemy/boss 203** |

> Không mục nào ở trên là "không lấy được": **791 clip · 308 controller · 5.792 `Animator` ·
> 228.432 `Transform`** đều **đã đếm được trong file** — nghĩa là chúng nằm đó, chỉ chưa export.
> Điều kiện duy nhất: một lần chạy export bổ sung.
