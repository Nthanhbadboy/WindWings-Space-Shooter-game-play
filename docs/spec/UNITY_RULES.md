# UNITY RULES — luật engine tự chốt được gì (và cái nó **không** chốt được)

> **Câu hỏi của vòng này:** *"nghiên cứu Unity đi xem có chốt được cái nào không"*.
> Cách làm: lấy **luật serialization / định dạng asset của Unity** rồi áp vào **dữ liệu đã export**,
> thay vì suy luận thêm về gameplay.
>
> **Nguồn số:** `reverse-engineering/raw/typetrees/*.jsonl.gz` (**109 class**, 5,5 MB) ·
> `reverse-engineering/il2cpp/dump.cs.gz` · `datas/{anim_clips.json.gz, animator_map.csv.gz,
> spine.json, prefab_joins.csv.gz}` — tất cả ở nhánh dữ liệu `arena/ef6b75ef-…` head `68ce86a7`.
> **Nguồn luật engine:** §10 (Unity Manual + source AssetStudio).
>
> **Không chạy lại APK, không dump thêm class, không sửa file dữ liệu.** Mọi con số dưới đây đọc từ
> file **đã có trong repo**.

---

## 0. Trả lời ngắn — **12 luật, 6 mục ĐÓNG, 4 mục hạ mức, 1 mục "không bao giờ tìm được"**

| # | Luật Unity | Áp vào | Kết quả | Mức |
|---:|---|---|---|---|
| 1 | Field chỉ được serialize khi `public` hoặc `[SerializeField]` | `Enemy_Health.armor` | **0/981** prefab có `armor` ⇒ **enemy KHÔNG có giáp per-prefab** (khác câu đang ghi ở 4 file) | **A** |
| 2 | Như trên, áp cho class rỗng | `Enemy_Appear` | **0 field** trong class + **39 class con** ⇒ "appear" là **đa hình**, không phải dữ liệu | **A** |
| 3 | PPtr `m_PathID = 0` là **null thật**; dumper đọc PPtr đúng | `Spawner.dataScript` | **23.570/23.570 null** (7 class) ⇒ **C3 ĐÓNG** | **A** |
| 4 | `autoCacheColliders = false` ⇒ **không** tự nạp collider lúc runtime | `Enemy_Physics` | **981/981** `false` + **981/981** list rỗng ⇒ **C6 ĐÓNG** | **A** |
| 5 | Sprite-swap key nằm ở `m_PPtrCurves`, **không** bị nén/stream | 791 clip | **0/791** có PPtrCurve ⇒ **game không có flipbook** | **A** |
| 6 | Curve float nằm trong `m_MuscleClip` (streamed/dense/constant) | 791 clip | **782/791** có blob, tổng **9.186.264 B** ⇒ "0 keyframe" là **thiếu decoder**, không phải thiếu dữ liệu | **A** |
| 7 | `m_Events` là mảng struct **không nén** | 318 clip | **793 event** có `time` + `functionName`; chỉ `__count` được dump ⇒ **C1 hạ D → thiếu export** | **B** |
| 8 | `AnimatorController.m_AnimationClips` là `PPtr<AnimationClip>[]` | 308 controller | **793** tham chiếu + **3.871** tên state (`m_TOS`) ⇒ **C2 hạ D → thiếu export** | **B** |
| 9 | `static` field **không bao giờ** được serialize | `kHp`, `pct` | quét **109 class / 908 tên field**: **0** field mode/percent ⇒ hai ẩn số này **không nằm trong bất kỳ prefab nào** | **A** |
| 10 | `ScriptableObject` int không gán = 0 | `Wave.indexWave` | **686/686 = 0** ⇒ field chết, thứ tự = thứ tự mảng ⇒ **C4 ĐÓNG** | **A** |
| 11 | `m_Name` của component rỗng; của asset là tên thật | 27 `SkeletonDataAsset` | **26/27** tên `skeleton_SkeletonData` ⇒ **§7 #9 vẫn mở**, nhưng **lý do đã rõ** | **A** |
| 12 | PPtr phải join theo **(m_FileID, m_PathID)** | `Animator.m_Controller` | **175/5.778** trỏ file ngoài, **14** null ⇒ `animator_map.csv` có **rủi ro 3,0 %** | **C** |

> **Nhận định:** trong 12 luật, **6 cái đóng được mục đang mở** (`C3`, `C6`, `C4`, appear, armor,
> flipbook), **4 cái hạ mức** (`C1`, `C2`, keyframe, `§7 #9`), và **1 cái là kết quả âm tính có ích**:
> `kHp`/`pct` **không thể** tìm trong asset — chỉ asm hoặc đo trong game.
> Ba luật còn lại là công cụ để **kiểm lại** bảng đã có.

---

## 1. Field serialize = **nguồn sự thật** (áp luật 1 + 2)

Unity chỉ serialize field `public`, hoặc `private` **có** `[SerializeField]`; `static`/`const`/`readonly`
thì không (`script-serialization-rules.html`). Hệ quả: **typetree của một prefab chính là danh sách
field mà game thật sự lưu** — field nào không thấy thì **không có dữ liệu**, không phải "dumper bỏ sót".

### 1.1 Phép đối chứng hoàn hảo: hai field cùng một class

`dump.cs` khai `Enemy_Health` có đúng 4 field. Hai field nằm **cạnh nhau** trong bộ nhớ:

| Field | Khai báo trong `dump.cs` | Có trong typetree? | Số instance |
|---|---|---:|---:|
| `noDamage` @`0x30` | `[SerializeField] private bool` | **CÓ** | **981/981** |
| `armor` @`0x34` | `private float` (không attribute) | **KHÔNG** | **0/981** |

⇒ **Đây là bằng chứng A cho cả hai chiều:** dumper đọc đúng (field có attribute xuất hiện **100 %**),
và `armor` **không được serialize** ở bất kỳ prefab nào.

> **ĐÍNH CHÍNH (23/10):** bốn file đang ghi *"enemy cũng có giáp (`armor@0x34`)"* — câu đó chỉ đúng
> **ở mức mã**: class có field, `CalculateDamage` có dùng nó. Nhưng **không prefab nào mang giá trị
> giáp**, nên với thiết kế dữ liệu thì **enemy không có giáp per-prefab**; nếu có thì cùng một hằng
> cho toàn bộ 981 con (gán trong code lúc `Init`).
> **Điều kiện lật ngược:** đọc `Enemy_Health.Init/CalculateDamage` thấy `armor` được **đọc từ
> `Enemy_Get_Datas`** ⇒ giáp có thật nhưng theo **id**, không theo prefab.

### 1.2 Sáu class **0 field** — không phải lỗi, mà là "không có gì để vặn"

| Class | Instance | Field serialize |
|---|---:|---:|
| `Enemy_Appear` | **914** | **0** |
| `Enemy_Attack` | **51** | **0** |
| `Enemy_DropGold` | 2 | **0** |
| `Enemy_SpawnChilds` | 1 | **0** |
| `ArenaManager` | 1 | **0** |
| `MB2_Director` | 1 | **0** |

`Enemy_Appear` là ca lớn nhất: `dump.cs` khai **không có field nào**, chỉ **2 method**
(`Appear(Action appeared)` · `.ctor`). Và nó là **lớp cha của 39 class**: `Boss1_Director`,
`Boss3…Boss18`, `MB2…MB19`, `MiniBoss1_Director`, `Boss_Appear`…

⇒ **"Appear" không phải một component có tham số** — nó là **entry point đa hình**: mỗi boss
override `Appear()` bằng mã riêng. Bản clone **không có gì để copy bằng số**; phải tự đặt hiệu ứng
xuất hiện (fade/teleport/rơi) và giữ đúng **hợp đồng**: có một callback `appeared` gọi khi xong.

> **Nhận định (A):** đây là lý do `Enemy_Appear` "rỗng" ở **914/914** instance — **không** phải export
> thiếu. Điều kiện lật ngược: nếu class con của `Enemy_Appear` có field riêng thì dữ liệu nằm ở
> **class con**, không ở class cha — kiểm bằng typetree `Boss*_Director` (đã có 34 file).

---

## 2. PPtr null là **null thật** ⇒ `C3` ĐÓNG (áp luật 3)

Một `PPtr` có `m_PathID = 0` là **tham chiếu rỗng** (AssetStudio §3.5). Nhưng để chắc không phải
dumper ghi 0 bừa, cần **nhóm đối chứng**: cùng một field `dataScript`, cùng một dumper.

| Class | Instance | `dataScript` **null** | Tỉ lệ |
|---|---:|---:|---:|
| `Spawner` | 1.370 | **1.370** | 100 % |
| `Path_Spawner` | 1.688 | **1.688** | 100 % |
| `PointToPoint_Spawner` | 13.292 | **13.292** | 100 % |
| `PinMap_Spawner` | 3.165 | **3.165** | 100 % |
| `Rocket_Spawner` | 2.019 | **2.019** | 100 % |
| `Waypoints_Spawner` | 1.151 | **1.151** | 100 % |
| `AirFree_Spawner` | 885 | **885** | 100 % |
| **Tổng 7 class spawner** | **23.570** | **23.570** | **100 %** |
| **Đối chứng:** `Enemy_Controller` | **981** | **0** | **0 %** |

⇒ **`C3` (Spawner.dataScript) ĐÓNG — A.** Field này là **field chết**: 23.570/23.570 rỗng, trong khi
cùng field đó ở `Enemy_Controller` **có giá trị 981/981**. Quy luật spawn **không nằm ở component**;
nó nằm ở asset `Wave` + `Call_Data` (đã có: 282 wave / 23.757 `Call_Data`).

> **Vì sao phép đối chứng quan trọng:** nếu chỉ có "100 % null" thì chưa loại được khả năng
> "dumper không giải được PPtr". Có `Enemy_Controller.dataScript` **981/981 non-null** thì khả năng
> đó bị loại. **Điều kiện lật ngược:** export `Spawner.Awake` thấy nó gán `dataScript` lúc runtime —
> khi đó field vẫn "chết trong asset" nhưng sống trong mã; kết luận thiết kế **không đổi**.

---

## 3. `autoCacheColliders = false` ⇒ `C6` ĐÓNG (áp luật 4)

`Enemy_Physics` có 2 field serialize. Đếm toàn bộ **981** instance:

| Field | Giá trị | Số instance |
|---|---|---:|
| `autoCacheColliders` | `false` | **981/981** |
| `allColliders` | `[]` (rỗng) | **981/981** |

⇒ **`C6` ĐÓNG — A.** Trước đây tôi chỉ dựa vào "list rỗng" và vẫn để ngỏ khả năng "nạp lúc runtime
bằng `GetComponentsInChildren`". Cờ `autoCacheColliders = false` **đóng đúng khả năng đó**: component
tự khai là **không** tự cache ⇒ **enemy thường không có collider nào** ⇒ **không gây damage va chạm**.
Damage của enemy chỉ đến từ **đạn** (`Gun_Attack`).

> **Điều kiện lật ngược:** một class khác gọi `GetComponentsInChildren<Collider>` rồi tự xử lý va chạm
> (ví dụ `Enemy_Controller.OnTriggerEnter`). Chưa đọc asm `Enemy_Controller` nên chỉ dám nói:
> **dữ liệu prefab không có collider**, không phải "game không có va chạm".

---

## 4. AnimationClip có **4 kho chứa** — chỉ 1 kho là "không đọc được" (áp luật 5 + 6 + 7)

Một `AnimationClip` trong build chứa **4 nhóm dữ liệu độc lập** (AssetStudio §8.1):

| Kho | Chứa gì | Nén/stream? | Dump hiện tại |
|---|---|---|---|
| `m_FloatCurves` · `m_PositionCurves` · `m_RotationCurves` · `m_ScaleCurves` · `m_EulerCurves` | curve **số** dạng editor | không | **0/791** (đúng: clip build không dùng kho này) |
| **`m_PPtrCurves`** | **sprite-swap / material-swap** | **không** | **0/791** |
| **`m_MuscleClip`** → `m_StreamedClip` / `m_DenseClip` / `m_ConstantClip` | curve **đã bake** | **có** (`StreamedClip.data: uint[]`) | **có blob nhưng không dump** |
| **`m_Events`** | `AnimationEvent[]` | **không** | **chỉ có `__count`** |

### 4.1 `m_PPtrCurves = 0` ở **791/791** ⇒ **không có flipbook** (A)

Sprite animation trong Unity **bắt buộc** đi qua `m_PPtrCurves` (`EditorCurveBinding.PPtrCurve`
+ `ObjectReferenceKeyframe`; khoá là thời gian, value là `PPtr<Sprite>`). Kho này **không** bị
streamed/compressed — nó là mảng struct thường trong asset.

⇒ **Kết luận A:** **không clip nào** của game là flipbook. "Enemy động" = **1 sprite + di chuyển
procedural**, đúng như `ANIMATION` §4.5 đã chốt. Con số "28 chuỗi · 160 ảnh" ở §5 là **cách đặt tên
sprite trong atlas**, **không phải** animation clip.

### 4.2 `m_MuscleClipSize` — **9,19 MB curve đang nằm trong file**

| Chỉ số | Giá trị |
|---|---:|
| Clip có `m_MuscleClipSize > 0` | **782 / 791** |
| Tổng kích thước blob | **9.186.264 B** (9,19 MB · 8,76 MiB) |
| Median | **5.076 B** |
| Lớn nhất | **175.712 B** |
| Clip `= 0` | **9** — `Idle` · `idle` · `Setup` · `Test` · `UILock` · `Xuathien` · `Laze` · `Player4` · `Chuyensangattack3` |

⇒ **"0 keyframe" ở 791 clip là giới hạn của reader, không phải game không có curve.** 9 clip kích
thước 0 là **clip giữ pose** (`m_StopTime = 1,0`, `m_Events__count = 0`) — đúng nghĩa "không có
keyframe".

> **Nhận định (A):** `ANIMATION` §3.5 kết luận *"giới hạn thật"* — **đúng một nửa**. Đúng: reader
> hiện tại không giải `StreamedClip`. Sai: **dữ liệu không thiếu**; 9,19 MB nằm trong asset và
> thuật toán giải đã có (Hermite + `coeff[4]`, `StreamedFrame` → `StreamedCurveKey`).
> **Điều kiện lật ngược:** nếu `m_MuscleClipSize` tính cả `m_ConstantClip` rỗng thì con số 9,19 MB
> phóng đại — nhưng kể cả vậy, **782/791 clip khác 0** vẫn bác "không có curve".

### 4.3 `m_Events` — **793 event có `time`**, chỉ là chưa dump phần tử

`AnimationEvent` là struct cố định gồm `time` (float), `functionName` (string), `floatParameter`,
`intParameter`, `stringParameter`, `objectReferenceParameter`. Không nén, không stream.

| Chỉ số | Giá trị |
|---|---:|
| Clip có event | **318 / 791** |
| Tổng event | **793** |
| Dump hiện tại | chỉ `m_Events__count` |

⇒ **`C1` hạ từ "vắng mặt thật (D)" xuống "thiếu export độ sâu 3 (B)"**. Cần đúng **793 bản ghi
`(clip, time, functionName)`** — không cần giải nén gì. Đây là **việc rẻ nhất trong toàn bộ danh sách
còn mở**, và nó chốt luôn **thời điểm ra đòn của boss** (cùng `m_StopTime`).

> **Vì sao trước đây tưởng mất:** dump `native-types.jsonl.gz` là **census nông** — nó ghi
> `mảng.__count` thay vì phần tử. Không phải giới hạn của định dạng Unity.

### 4.4 Nhịp bắn: **`timeShot` có thật, và số 0 là số 0** (không phải thiếu field)

`Gun_Attack` có `allGunDatas` = **mảng struct `[Serializable]`** — Unity serialize **cả struct lồng**
(`countShots`, `timeShot`, `timeReload`, `timeRounds`, `countMags`).

| Chỉ số | Giá trị |
|---|---:|
| Instance `Gun_Attack` | **458** |
| Có `allGunDatas` | **458 / 458** |
| Bản ghi gun-data | **516** (429 × 1 + 29 × 3) |
| `timeShot > 0` | **79** bản ghi |
| Instance có ít nhất 1 `timeShot > 0` | **61 / 458 = 13,3 %** |
| `timeShot` median (khi > 0) | **0,10 s** · min 0,05 · max 5,0 |

⇒ **Xác nhận con số 13,3 %** đang ghi ở `OPEN_ISSUES` C1 — nhưng **đổi cách hiểu**: 87,7 % còn lại
**không phải "dữ liệu thiếu"**, mà là **`timeShot = 0` thật** (súng bắn 1 phát / bắn theo event).
Với clone: **13,3 % súng copy được nhịp**, phần còn lại **phải tự đặt** — không có gì để trích thêm.

---

## 5. AnimatorController giữ **cả clip lẫn tên state** ⇒ `C2` hạ mức (áp luật 8)

`AnimatorController` (AssetStudio §8.4) chứa:

| Field | Kiểu | Ý nghĩa | Đếm được ở 308 controller |
|---|---|---|---:|
| `m_AnimationClips` | `List<PPtr<AnimationClip>>` | **clip nào thuộc controller** | **793** (khớp đúng 793 event) |
| `m_TOS` | `Dictionary<uint,string>` | **hash → tên state** | **3.871** |
| `m_StateMachineBehaviours` | mảng | behaviour gắn state | **0** |

| Phân bố clip/controller | 0 | 1 | 2 | 3 | 4–5 | 7–14 | 28 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Số controller | **1** | 160 | 72 | 43 | 8 | 23 | 1 |

⇒ **`C2` hạ từ "vắng mặt thật (D)" xuống "thiếu export (B)"**: asset **có** danh sách `PPtr` clip và
**có** bảng tên state. Export độ sâu 3 cho 308 controller là ra **controller → clip → tên state**, tức
đúng cái `C2` ghi là "0 bản ghi".

> **Nhận định (B):** tên trong `m_TOS` là **tên state do dev đặt**, nên có thể đọc được **ý đồ**
> (Idle/Attack/Die) chứ không chỉ thứ tự. Điều kiện lật ngược: nếu `m_TOS` chỉ chứa hash của clip thì
> tên state vẫn phải suy từ clip — nhưng 3.871 khoá trên 308 controller (12,6/controller) nhiều hơn
> 793 clip, nên **chắc chắn không phải chỉ là clip**.

---

## 6. `static` **không serialize** ⇒ `kHp` / `pct` **không bao giờ** nằm trong prefab (áp luật 9)

Đây là luật quan trọng nhất của vòng này, vì nó **đóng một hướng tìm sai** đã tốn nhiều vòng.

| Phép quét | Kết quả |
|---|---|
| Class có file typetree | **109** |
| Tên field phân biệt (không trùng) | **908** |
| Field khớp `mode` / `difficulty` / `percent` / `pct` / `hard` / `ratio` / `multipl` | **0** |
| Field serialize trong `Stage_Datas` (class giữ `ModeCurrent`) | **16 field — TOÀN BỘ là `static`** ⇒ không field nào vào typetree |

`Stage_Datas` khai `public static int ModeCurrent; // 0x34` và `Stage_Get_Datas` khai
`private static float[] levelDelta; // 0x10`. **Cả hai đều `static`** ⇒ Unity **không** lưu vào asset.

> **ĐÍNH CHÍNH TÊN:** mảng mà `GetBonus` index theo chế độ **không phải** "`modeMultiplier`" (tên tôi
> tự đặt) — nó là **`Stage_Get_Datas.levelDelta`** (`private static float[]` @`0x10`). Asm đọc
> `ldr x8,[x8,#0x10]` → `ldr w9,[x8,#0x18]` (độ dài) → `ldr s0,[x8,w20*4+0x20]` khớp **đúng** layout
> `float[]` của field này. Tên thật **củng cố** cách đọc: `levelDelta` = hệ số theo **level/chế độ**.

⇒ **Kết luận A (âm tính, có ích):**
1. **`kHp[mode]`** và **`pct[mode][slot]`** (nếu là `static`/`const`) **không thể** tìm ra bằng bất kỳ
   lần export asset nào — không phải "chưa export", mà **đúng luật Unity là không có trong asset**.
   Đường duy nhất: **asm** (`.cctor` / hàm đọc) hoặc **đo trong game** (giao thức đã có ở
   `DIFFICULTY_MODES` §5.5).
2. Bớt được **một lớp việc**: mọi đề xuất "export thêm prefab để tìm hệ số chế độ" **đều vô ích**.

> **Điều kiện lật ngược:** nếu `kHp` là field **instance** trên một MonoBehaviour mà chưa class nào
> trong 109 class chứa nó (ví dụ `Mission_Data`) thì nó vẫn có thể serialize. Phép quét chỉ phủ
> **109 class đã dump**; một class chưa dump vẫn có thể giữ.

---

## 7. `ScriptableObject` int mặc định 0 ⇒ `C4` ĐÓNG (áp luật 10)

`Wave` là component — **686** instance trên **281** GameObject wave khác nhau (nhánh dữ liệu có **282**, thêm 1 wave `unknown`). Field serialize của nó chỉ có **3**:
`indexWave` (int), `startPoint` (PPtr), `endPoint` (PPtr).

| Giá trị `indexWave` | Số instance |
|---|---:|
| `0` | **686 / 686** |
| khác 0 | **0** |

⇒ **`C4` ĐÓNG — A.** `indexWave` là **field chết**: 686 bản sao của 282 wave, **không cái nào** được
gán. Thứ tự wave vì vậy là **thứ tự phần tử trong `listMapDatas`** (Unity giữ nguyên thứ tự `List`),
khớp với cách `waves.json` đang đánh số.

> **Điều kiện lật ngược:** asm `Wave` gán `indexWave` lúc `Start()` (chưa export asm `Wave`). Khi đó
> field "chết trong asset" nhưng vẫn dùng được lúc runtime — **kết luận thiết kế không đổi**: clone
> dùng thứ tự mảng.

---

## 8. `m_Name`: component rỗng, asset mới có tên ⇒ `§7 #9` **vẫn mở** (áp luật 11)

| Đối tượng | `m_Name` | Diễn giải |
|---|---|---|
| Component `Spawner` · `Wave` · `Enemy_*` | **`""`** (100 %) | tên nằm ở **GameObject**, không ở component |
| `SkeletonDataAsset` (27 rig) | **26 × `skeleton_SkeletonData`** + 1 × `Saw_SkeletonData` | tên **thật**, nhưng **trùng nhau** |

⇒ **`§7 #9` (rig nào thuộc prefab nào) vẫn mở**, nhưng câu "vì sao không có tên" **đã đóng (A)**:
không phải exporter làm mất — **asset gốc đã đặt tên giống nhau**. Vì vậy **không có đường đọc tên**;
chỉ còn **một** đường: join `SkeletonAnimation.skeletonDataAsset` (PPtr) → `SkeletonDataAsset`, tức
export **117 component `SkeletonAnimation`**.

> **Nhận định (A):** 27 rig có **21 bộ xương khác nhau** và **7 bộ animation khác nhau**; 21 rig dùng
> chung bộ 6 animation `Hide/Idle/Idle2/Left/Right/Show` — nhóm này gần như chắc là **tàu/drone**
> (có `Left`/`Right` = nghiêng), nhưng **chưa chứng minh được** nếu không có join.

---

## 9. Bẫy PPtr — join chỉ theo `m_PathID` có thể sai **3 %** (áp luật 12)

`PPtr` gồm **hai** phần: `m_FileID` (0 = cùng file, >0 = file ngoài) và `m_PathID`. Đếm trên 5.792
`Animator`:

| `m_Controller.m_FileID` | Số `Animator` |
|---|---:|
| 0 (cùng file) | **5.617** |
| 2 · 3 · 4 (file ngoài) | **52 · 67 · 56 = 175** |
| `m_PathID = 0` (null) | **14** |

`datas/animator_map.csv.gz` chỉ có cột `controller_path_id` — **không có `m_FileID`**. Với **175**
dòng, cùng một `PathID` có thể trỏ hai object khác nhau ở hai file khác nhau.

⇒ **Mức C — rủi ro 3,0 %** cho bảng `animator → controller`. Cách kiểm rẻ: export lại kèm
`m_FileID`; nếu 175 dòng đổi controller thì mọi thống kê theo controller lệch ≤ 3 %.

> **Nhận định:** bảng `animator_map` hiện dùng để đếm **bucket** (UI/wave/enemy) — các bucket đến từ
> **tên prefab**, không từ controller, nên **kết luận §4.5c của `ANIMATION` không bị ảnh hưởng**.

---

## 10. Nguồn luật engine

| Luật | Nguồn | Dùng để chốt |
|---|---|---|
| Field serialize = `public` hoặc `[SerializeField]`; `static`/`const`/`readonly` không | `docs.unity3d.com/Manual/script-serialization-rules.html` | §1, §6 |
| `AnimationEvent` có `time`, `functionName`, tham số | `docs.unity3d.com/ScriptReference/AnimationEvent.html` | §4.3 |
| `m_PPtrCurves` cho sprite/material; `EditorCurveBinding.PPtrCurve` | `docs.unity3d.com/ScriptReference/EditorCurveBinding.PPtrCurve.html` | §4.1 |
| `AnimationClip`: `m_PPtrCurves` · `m_MuscleClip` (`m_StreamedClip.data: uint[]` · `m_DenseClip` · `m_ConstantClip`) · `m_Events` | AssetStudio source `Classes/AnimationClip.cs` (qua DeepWiki §8.1–8.2) | §4 |
| `AnimatorController`: `m_AnimationClips` (`List<PPtr<AnimationClip>>`) · `m_TOS` (`Dictionary<uint,string>`) | AssetStudio source `Classes/AnimatorController.cs` (qua DeepWiki §8.4) | §5 |
| `PPtr` = (`m_FileID`, `m_PathID`); `0` = cùng file; `m_PathID = 0` = null | AssetStudio source `Classes/PPtr.cs` (qua DeepWiki §3.5) | §2, §9 |

> Đây là **luật của engine**, không phải suy đoán về game. Chúng áp dụng cho mọi build Unity
> 2022.3.x, không phụ thuộc phiên bản APK.

---

## 11. Cái Unity **không** chốt được (đừng thử lại)

| # | Ẩn số | Vì sao engine không giúp | Đường còn lại |
|---:|---|---|---|
| 1 | **`kHp[mode]`** | Nếu là `static`/`const` ⇒ không serialize (§6) | asm `Enemy_Controller.GetStartHealth` / đo số phát bắn |
| 2 | **`pct[mode][slot]`** | Cùng lý do; `GetKillPercentMissionComplete` đọc **field instance** của object khác, class đó chưa dump | asm `GetKillPercentMissionComplete` + đọc 3 float `@0x20/0x24/0x28`; hoặc 3 con số UI |
| 3 | **Rig → prefab** | `m_Name` 26/27 trùng (§8) | export `SkeletonAnimation.skeletonDataAsset` (117 component) |
| 4 | **Cảm giác / aim assist / input** | Không nằm trong asset | phải tự thiết kế (`D1`) |
| 5 | **Nhịp bắn 87,7 % súng** | `timeShot = 0` là **giá trị thật** (§4.4) | event clip (793, §4.3) hoặc tự đặt |

---

## 12. Còn thiếu / phải đoán

| # | Việc | Mức | Chi phí | Ra được gì |
|---:|---|---|---|---|
| 1 | Export **793 `m_Events`** (`clip · time · functionName`) | **B** | 1 lần chạy, độ sâu 3 | **thời điểm ra đòn của boss** — mục mở lâu nhất của `ANIMATION` |
| 2 | Export **308 `AnimatorController`**: `m_AnimationClips` + `m_TOS` | **B** | cùng lần chạy | controller → clip → **tên state** (`C2`) |
| 3 | Viết decoder `m_StreamedClip` (**9,19 MB**, 782 clip) | **A/B** | việc lớn, thuật toán đã có | **pose thật** của 791 clip — nâng `ANIMATION` từ "biết tên" lên "biết dáng" |
| 4 | Export **117 `SkeletonAnimation`** (`skeletonDataAsset` PPtr) | **B** | 1 lần chạy | đóng `§7 #9` (rig nào của prefab nào) |
| 5 | Re-export `animator_map` **kèm `m_FileID`** | **C** | rất rẻ | loại rủi ro **3,0 %** ở §9 |
| 6 | Đọc `Enemy_Health.Init` (asm) xem `armor` **có được gán** không | **B** | 1 method | chốt hẳn "enemy có giáp" — hiện chỉ biết **không per-prefab** |
| 7 | **Đo `kHp` / `pct` trong game** | **A** | 3 giá trị UI + số phát bắn | đóng hai ẩn số cuối; **không có đường tĩnh nào rẻ hơn** |

> **Tổng kết vòng này:** 6 mục **đóng** bằng luật engine (`C3` · `C6` · `C4` · appear · armor ·
> flipbook), 4 mục **hạ mức** (`C1` · `C2` · keyframe · `§7 #9`), 1 mục **bị loại khỏi hướng tìm**
> (`kHp`/`pct` trong asset). Cái **không đổi**: hai ẩn số cân bằng vẫn phải **đo trong game** — nhưng
> giờ đã biết chắc **không phải vì thiếu công cụ**, mà vì **chúng nằm ngoài dữ liệu serialize**.
