# ANIMATION — soát lỗ hổng của đợt điều tra animation enemy (23/10)

> **Câu hỏi:** nhánh `arena/ef6b75ef` đã điều tra animation enemy — **còn thiếu gì**?
>
> **Cách làm:** đọc 8 tài liệu + dữ liệu thô của nhánh đó
> (`docs/apk-analysis/{22,23,25,26,27,32,33}-*.md`, `datas/spine*.json*`,
> `datas/animator_map.csv.gz`, `raw/typetrees/*`), rồi **tự ghép lại** những mắt nối mà
> tài liệu của họ ghi là "chưa làm". Mọi số dưới đây đọc trực tiếp bằng script trong phiên
> này; chỗ nào chỉ là suy luận đều ghi `> Nhận định:`.
>
> Không chạy game. Không sửa nhánh kia, không merge.

---

## 0. Bức tranh trong một bảng

| Lớp | Số lượng | Đọc được | Chưa đọc được |
|---|---:|---|---|
| **Spine** (26 rig + `Saw`) | 27 rig · **185** animation · **12.274** keyframe | **100 %** timeline + **21** event có mốc thời gian | rig → đơn vị trong game (**đóng được 1 phần**, §3) |
| **`Enemy_Movement`** | **981** instance / 109 prefab | **100 %** — 9 field serialize | thân hàm (nhưng logic đã rõ từ field) |
| **`Enemy_Appear`** | **914** instance / 107 prefab | **0 field** — tree serialize **rỗng** | **toàn bộ**, và **asm cũng chưa export** (§2a) |
| **Unity `AnimationClip`** | **791** clip (226 tên) | tên · thời lượng · loop · event | **keyframe: 0/791** — curve bị stream |
| **`AnimatorController`** | **308** | số clip tham chiếu | state machine / transition |
| **`Animator` instance** | **5.792** | nối prefab **98,2 %** | — |
| **Boss điều khiển bằng script** | 44 class `*_Director` | **1 chuỗi** đã chứng minh (`Boss1_Director → Boss-39002`) | **43** director còn lại |

---

## 1. Năm lỗ hổng mà chính nhánh kia đã tự ghi

| # | Lỗ hổng | Ghi ở | Chi phí đóng |
|---:|---|---|---|
| 1 | **rig → đơn vị trong game** (boss nào / súng nào) | `23-spine-anim.md` §Còn thiếu | **Rẻ** — xem §3, tôi đóng được 1 phần bằng dữ liệu có sẵn |
| 2 | keyframe của 791 clip | `27-anim-curves.md` | **Đắt** — phải giải mã `m_StreamedClip` thủ công |
| 3 | `ParticleSystem` 4.845 — mới có `path_id` | `26-native-animation.md` | Trung bình — mở rộng `animator_joins` |
| 4 | `OnGunDie` → chuyển pha, timing coroutine | `33-animation-control-native.md` §4 | Đắt — cần đọc thêm asm + `yield` |
| 5 | 43 director còn lại chưa trace | như trên | **Rất đắt** — mỗi boss một chuỗi |

---

## 2. Lỗ hổng nhánh kia **không** liệt kê

### 2a. `Enemy_Appear` — không có field, **và cũng không có asm**. Đây là lỗ lớn nhất

Đếm lại trên typetree thô:

```
Enemy_Appear.jsonl.gz   →  914 instance
field serialize ngoài m_*  →  0 (rỗng hoàn toàn)
```

Nghĩa là **cơ chế xuất hiện / biến mất của 107/109 prefab enemy nằm 100 % trong code**, không có
một tham số nào trong prefab để đọc. Đối chiếu danh sách asm đã export (**65 file .asm.txt**):

```
Boss1_Director · Boss_AttackPhases · Boss_AttackTypes · BossSpineEventHandler
Enemy_Controller · Enemy_Display · Enemy_Health · Enemy_Movement · Enemy_Get_Datas …
```

**`Enemy_Appear` không có trong danh sách.** Tức lớp animation duy nhất mà *mọi* enemy đều có
(§0: 107/109 prefab) thì **chưa được xuất một dòng asm nào**.

**Vì sao quan trọng:** trong game bắn máy bay, "enemy xuất hiện" là hiệu ứng người chơi thấy
**mỗi wave, mỗi enemy** — nhưng hiện chỉ biết nó tồn tại, chưa biết nó làm gì.

#### 2a′. **Đã đóng một phần** (dữ liệu kéo về 23/10, commit nhánh dữ liệu `6dc5c4bf5`)

Exporter đã chạy lại và **`Enemy_Appear.asm.txt` giờ có** (cùng `BossSpineEventHandler`). Đọc ra:

```asm
;;; Appear  public virtual void Appear(Action appeared)
    0x1582108: str  x30, [sp, #-0x10]!
    0x158210c: cbz  x1, #0x1582124      ; callback == null -> thoát
    0x1582110: ldr  x2, [x1, #0x18]     ; Action._methodPtr
    0x1582114: ldr  x0, [x1, #0x40]     ; Action._target
    0x1582118: ldr  x1, [x1, #0x28]     ; Action._methodPtrAux / arg
    0x158211c: ldr  x30, [sp], #0x10
    0x1582120: br   x2                  ; tail-call, không làm gì khác
```

**32 byte, và không có logic nào của riêng nó.** `Enemy_Appear.Appear` chỉ là **vỏ gọi delegate**:
nếu callback null thì thoát, ngược lại nhảy thẳng vào callback. Vì thế lớp này **không có field
serialize** — nó không giữ trạng thái, chỉ giữ một `Action`.

Điều đó giải thích luôn vì sao có đúng **39 lớp con**, và **cả 39 đều là `*_Director`**:

```
Boss1 · Boss3 · Boss4 · Boss4Lite · Boss5 · Boss6 · Boss6_Mini · Boss7 · Boss8 · Boss9
Boss9_Mini1 · Boss9_Mini2 · Boss10 · Boss11 · Boss12 · Boss13 · Boss15 · Boss17 · Boss18
Boss_Director · Boss_Appear · MB2..MB16 · MB19 · MB6_ChildDirector · MiniBoss1_Director
```

⇒ Cơ chế xuất hiện nằm ở **lớp con**, không ở lớp cha. Muốn biết boss hiện ra thế nào phải đọc
từng `*_Director` — và một phần đã có asm (`Boss1_Director.asm.txt` cùng 4 coroutine
`_WarningBossAppear`, `_OffGun1Head`, `_OnGun1Static`, `_RotateObject`).

> **Còn thiếu:** asm của 38 director còn lại. Nhưng câu hỏi đã đổi dạng: không còn là "không biết
> `Enemy_Appear` làm gì" (nó không làm gì), mà là "director nào ghi đè `Appear`".

### 2b. `Enemy_HitSkeletonRenderer` nằm trên **3** prefab, không phải 2

Tài liệu này (nhánh spec) đang ghi **sai** ở `ANIMATION.md` §4.5: *"Spine (xương) · 2 root ·
chỉ `Boss-39001` / `Boss-39002`"*.

Ghép lại bằng `transform-tree.tsv.gz` (228.432 dòng) + `prefab-roots.csv`: đi ngược `father`
từ `m_GameObject` của từng hit-renderer lên root:

| prefab root | số hit-renderer | skeleton component | children của root |
|---|---:|---:|---:|
| `Boss-39001` | **5** | 602882 | 2 |
| `Boss-39002` | **3** | 664302 | 5 |
| **`Boss-39003`** | **9** | 602881 | 2 |
| **tổng** | **17** ✅ | 3 component | |

17/17 instance đều đi được tới root, không cái nào rơi ra ngoài. **Mức A.**
⇒ Sửa thành **3 prefab**, và con số 17 instance của nhánh spec vẫn đúng.

### 2c. 23/27 rig Spine **không có đòn nào** — đòn tập trung ở 4 rig

Đếm animation theo rig (`datas/spine_anim.json.gz`):

| Nhóm | Số rig | Animation |
|---|---:|---|
| **Có đòn** | **4** | `skeleton__17` (18) · `skeleton__21` (10) · `skeleton__5` (10) · `skeleton__8` (9) |
| Chung một khuôn 6 animation `Hide · Idle · Idle2 · Left · Right · Show` | **22** | — |
| `Saw` (riêng: `Fly · Teleport …`) | 1 | 5 |

⇒ **23/27 rig là rig phụ** (súng / cánh / bộ phận), không phải thân boss. Câu "27 rig Spine" dễ
bị đọc thành "27 đơn vị có animation riêng" — không phải.

#### 2c′. Ghép trực tiếp: **chỉ 2 trong 4 rig có đòn là boss**

Typetree `SkeletonAnimation` — **20 instance, export 23/10**, và đây **chỉ là một phần** (game có
ít nhất 21; xem §3.1′) — cho `skeletonDataAsset.m_PathID` và `m_GameObject.m_PathID`; đi lên
`transform-tree` tới `prefab-roots` là ra prefab. Không còn phải đoán theo tên bone:

| rig | animation | gắn vào | loại |
|---|---|---:|---|
| `580611` = `skeleton__21` | 10, có `Attack1–4` | **`Boss-39001`** + **`Boss-39002`** (dùng chung) | **boss** |
| `580613` = `skeleton__8` | 9, có `Attack1–3` | **`Boss-39003`** (`Body/Boss 1/Skeleton`) | **boss** |
| `580619` = `skeleton__17` | 18 × `Attack01–12` | `Popup_UnlockShip` | **UI** |
| `580623` = `skeleton__5` | `AttackSpec`/`TopL`/`TopR` | `Popup_UnlockShip` | **UI** |

Các rig còn lại cũng lộ nguyên hình: `580615` (`Saw`) → `EndgameLoader`; `580633` →
`Board_Combo`/`Board_MiniCombo`; `580621`/`580627`/`580643` → `Board_Players`;
`580629`/`580635`/`580641`/`580659`/`580663` → `Player_10004/10007/10009/10015/10018/10020`.

> **Sửa một kết luận của chính tôi:** §2c bản trước viết "có 4 rig có đòn", ngụ ý 4 boss. Sai —
> **2 rig trong số đó là popup UI**. `skeleton__17` với 18 animation "Attack" 0,4 s không phải
> boss bắn nhanh, mà là **hiệu ứng mở popup mua tàu**. Con số đúng là: **2 rig boss**, và cả hai
> đều là thân boss (`Body/Boss 1/Skeleton`), không phải súng.

> Nhận định: với **46 boss** trong `Data_Boss` và **39 prefab `Boss-*`**, mà chỉ **2 rig** có
> animation đòn gắn trên boss, thì phần lớn boss **không** dùng Spine để đánh — chúng dùng
> `Animator` (154 instance, 63 prefab) hoặc thuần code trong các `*_Director`.

### 2d. Thời lượng đòn của 2 rig "họ Boss 1" dài bất thường — chưa ai đối chiếu

| rig | animation | dài | event |
|---|---|---:|---|
| `skeleton__21` | `Attack1` | **33,367 s** | — |
| | `Attack2` | 10,000 s | — |
| | `Attack3` | 12,667 s | `Stop` ×5 (0,63 · 3,3 · 5,87 · 8,2 · 10,6) |
| | `Attack4` | 1,000 s | `Banplasma` @0,7 |
| `skeleton__8` | `Attack1` / `Attack2` / `Attack3` | 9,0 / 9,0 / **18,0 s** | — |
| `skeleton__17` | `Attack01…Attack12` | **0,4 s** mỗi cái | `Shot` @0,3333 ở **cả 12** |
| `skeleton__5` | `AttackSpec` / `TopL` / `TopR` | 0,43 / 0,6 / 0,6 s | `Spec` · `TopL` · `TopR` |

`33` §1 ghi `SetAnimation` gọi với **`loop=true`**. Vậy `Attack1` **lặp một animation 33 giây**.
Điều này **chưa được đối chiếu** với bất kỳ thứ gì: không ai kiểm boss có thật sự đứng trong
`Attack1` suốt 33 s, hay animation đó chứa nhiều pha và game tự cắt ở `Stop`.

Con số này quan trọng cho clone: nếu chép "boss tấn công 33 s" thì sai nhịp so với cảm giác
người chơi.

### 2e. ~~Chưa có **một** phép đo runtime nào về playback~~ → **đã có công cụ**

> **Cập nhật cùng ngày:** đã thêm endpoint `GET /anim` vào bridge (`RamusBridge.cs`),
> đọc bằng reflection nên không cần reference Spine và vẫn biên dịch cho cả 6 target.
> Cách dùng: `curl 'http://127.0.0.1:8080/anim?name=Boss&max=20'`. `collect.sh` đã gọi nó
> ở cả 3 mốc dump và gate đòi file `anim-ingame.json`.
>
> **Đã có:** tên animation + thời điểm + độ dài + loop + timeScale cho từng object.
> **Chưa có:** phép đo nào **đã chạy trên thiết bị** — công cụ xong, số chưa có. Tự kiểm
> trong CI chứng minh bộ đọc đúng trên component giả; chưa chứng minh trên game thật.


Toàn bộ kết luận về animation hiện là **offline**: đọc asset + đọc asm. Chưa ai xác nhận trên
máy rằng `SkeletonAnimation` thật sự chạy `Xuathien` lúc vào màn, hay `Attack3` được gọi ở pha
thứ ba.

Bridge trong repo này **đã có đủ** để đo việc đó mà không cần đọc thêm asm:

```
GET /find?name=Enemy_Sub        → object đang sống
GET /statics?type=…             → field static
```

> Nhận định: cần thêm **một** endpoint đọc `SkeletonAnimation.AnimationName` + `time` +
> `Animator.GetCurrentAnimatorStateInfo`. Đó là ~30 dòng C# và biến "suy từ tên animation"
> thành "đo được". Đây là mắt nối rẻ nhất giữa hai nhánh.

---

## 3. Đóng được gì ngay trong phiên này

### 3.1 `skeleton__21` = rig của **cả** `Boss-39001` và `Boss-39002` (mức **A**)

`33-animation-control-native.md` §1 chép nguyên văn 8 giá trị state serialize của
`Boss1_Director` trên prefab `Boss-39002`:

```
stateAppear=Xuathien  stateRunAway=Baydi  stateDie=Dead
stateAttack1=Attack1  stateAttack2=Attack2  stateAttack3=Attack3
statePreAttack2=Chuyensangattack2  statePreAttack3=Chuyensangattack3
```

Đối chiếu với tên animation của 27 rig — **chỉ một rig khớp cả 8**:

| rig | khớp |
|---|---:|
| **`skeleton__21`** | **8 / 8** |
| `skeleton__8` | 5 / 8 (thiếu `Xuathien`, `Dead`, `UIShow`) |

⇒ Suy ra `skeleton__21` là rig của họ Boss 1. Đây chính là mắt nối mà `23-spine-anim.md` ghi là
"chưa map rig → đơn vị".

#### 3.1′. Sửa lần hai: `580611` gắn trên **`Boss-39001` *và* `Boss-39002`** — dùng chung rig

Report `38-spine-prefab-links.md` của nhánh dữ liệu ghép bằng **PPtr thật**
(`SkeletonAnimation → SkeletonDataAsset → TextAsset`), không qua tên file, không qua bone:

| prefab | component | SDA | TextAsset | animation |
|---|---:|---:|---:|---:|
| **`Boss-39001`** | 602882 | **`580611`** | 918 | 10 |
| **`Boss-39002`** | 664302 | **`580611`** | 918 | 10 |
| **`Boss-39003`** | 602881 | **`580613`** | 895 | 9 |

Đối chiếu `datas/spine.json`: TextAsset 918 → SDA 580611 → `skeleton__21` (39 bone);
895 → SDA 580613 → `skeleton__8` (32 bone). Khớp.

⇒ **Hai boss đầu dùng chung một rig.** Đây là cách đọc (a) trong câu hỏi treo trước đó — nay
**đã phân xử, mức A**: cùng một con trỏ `SkeletonDataAsset`, không phải suy luận.

Đây là **3 component trên 3 prefab boss**, và cả ba đều `resolved` — không cái nào rơi ra ngoài.
Riêng `Boss-39002` mang `Boss1_Director` instance `582209` (đọc trực tiếp từ typetree, đi lên
`transform-tree` ra root `Boss-39002`) — nên chuỗi **director → prefab → rig** đã khép kín.

##### Tôi đã sai ở đâu trong bản trước

Bản trước viết "SkeletonAnimation của `Boss-39002` **không nằm trong 20 instance đã export**", và từ
đó hạ quan hệ xuống mức B. Nửa đầu **đúng**, kết luận **sai** — vì:

> Thư mục `reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/` **không phải toàn
> bộ**. Nó có **20 file**, nhưng trong game **có ít nhất 21** component: `664302` (của
> `Boss-39002`) **không có** trong đó. Tôi đã lấy "không có trong tập đã export" rồi đọc thành
> "không tồn tại".

Đó là lỗi **dùng đại lượng thay thế hẹp hơn câu chữ**. Bộ kiểm cũng không bắt được: claim `G8`
đo đúng cái thư mục, nên nó PASS trong khi kết luận sai. Nay `G8` đo thẳng `spine-prefabs.json`,
và `G10` giữ con số 3 component để lần sau ai đọc nhầm "20 = tất cả" thì đỏ ngay.

### 3.2 Ghép rig ↔ TextAsset: 18/27 khớp 1-1, 9 cái **không phân biệt được**

Tên `skeleton__N` lấy từ tên file TextAsset (`tools/apk-analyze/spine_anim.py` dùng
`os.path.basename`). Ghép ngược về `skeleton_data_path_id` bằng **so danh sách tên bone**:

| Kết quả | Số rig |
|---|---:|
| Khớp chính xác, chỉ 1 ứng viên | **18 / 27** |
| Nhập nhằng — nhiều rig có **cùng bộ bone** | **9** |
| Không khớp | 0 |

4 rig có đòn đều nằm trong nhóm khớp rõ:

| `skeleton_data_path_id` | rig | bone |
|---|---|---:|
| 580619 | `skeleton__17` | 37 |
| 580611 | `skeleton__21` | 39 |
| 580623 | `skeleton__5` | 25 |
| 580613 | `skeleton__8` | 32 |

> Nhận định: 9 rig nhập nhằng dùng chung một bộ bone chung (kiểu `A/A2/A3/B/B2`). Với chúng,
> **tên `skeleton__N` không phải định danh đáng tin** — hai tài liệu có thể gọi cùng một rig
> bằng hai tên khác nhau mà không ai biết. Muốn hết nhập nhằng phải so **thứ tự bone**, không
> chỉ tập hợp tên; hoặc xuất thêm bảng `path_id → tên file` lúc bóc.

### 3.3 Sửa một chỗ sai của nhánh spec

`ANIMATION.md` §4.5 ghi Spine chỉ trên 2 prefab → **3 prefab** (Boss-39001/2/3). Đã sửa trong
file đó.

---

## 4. ~~Hai nhánh đá nhau~~ → **đã phân xử: cả hai đều đúng, khác định nghĩa**

| Nguồn | Cách đếm | Kết quả |
|---|---|---|
| Nhánh kia (`32-enemy-boss-animation.md`) | `animator_map.prefab_root` khớp mẫu `CB-` · `Boss-` · `MB-` | **154 instance / 63 prefab** |
| Nhánh spec (`ANIMATION.md` §4.5) | `animator_map.prefab_root` ∈ **109 tên trong `waves.json`** | **203 instance / 87 prefab** |

Cả hai **tái lập được**, chính xác đến từng instance. Khác nhau vì tập lọc khác nhau:

```
roster waves.json (109)              203 Animator / 87 prefab
mẫu tên CB-/Boss-/MB-                154 Animator / 63 prefab
roster ∩ mẫu tên                     148 Animator / 60 prefab
prefab tên Boss- (mọi nơi)            **92 Animator / 36 prefab**
```

`203 > 154` được vì roster **không phải** tập con của mẫu tên: nó còn `CD-` (15) · `W2-` (6) ·
`XB-` (5) · `GD-` (4) · `BB-` (4) · `H-` (2) · `W1-` (1) — 37 prefab không mang ba tiền tố kia.

**Mức A** cho cả hai. Dùng số nào là tuỳ câu hỏi: "enemy/boss đánh bằng clip có bao nhiêu" →
**203/87**; "chỉ nhóm CB/Boss/MB" → **154/63**.

### 4′. Tôi đã sửa một con số **đúng** thành **sai** — và đây là lỗi

Ở `VERIFY_ROUND2`, tôi kết luận *"203 không tái lập được"* rồi sửa `ANIMATION.md` từ **203** xuống
**154**. Sai. 203 tái lập được ngay — chỉ cần biết roster là gì. Nay đã khôi phục 203 và ghi kèm
định nghĩa.

Nguyên nhân: tôi đếm theo **mẫu tên** rồi so với một con số đếm theo **roster spawn**. Hai đại
lượng khác nhau. Đúng **loại lỗi** mà `VERIFY_ROUND2` §5 ghi là đã mắc bốn lần — và tôi mắc lần
thứ năm ngay trong tài liệu đi sửa lỗi đó.

> **Lần này khác ở chỗ:** con số 109 chưa từng có định nghĩa, nên không có gì để đối chiếu. Nay
> định nghĩa đã viết ở `ANIMATION.md` §4.5, và claim `B14` khoá nó lại.

## 5. Việc nên làm, xếp theo chi phí

| Ưu tiên | Việc | Vì sao rẻ | Đóng được gì |
|---:|---|---|---|
| ~~**1**~~ | ~~Thêm `Enemy_Appear`, `Enemy_Rotate`, `Enemy_Sub` vào `TARGETS`~~ | ✅ **xong** ở nhánh dữ liệu `6dc5c4bf5` | §2a′ — `Appear` là vỏ delegate, 39 lớp con |
| ~~**2**~~ | ~~Nối `SkeletonAnimation.AnimationName` + `Skeleton.time` vào bridge~~ | ✅ **xong** — `GET /anim` | §2e — còn thiếu **số đo trên máy** |
| ~~**3**~~ | ~~Ghi rõ định nghĩa "109 prefab roster"~~ | ✅ **xong** — định nghĩa ở `ANIMATION.md` §4.5, claim `B15` khoá lại | §4 — hai nhánh **cùng đúng** |
| ~~**4**~~ | ~~Ghép rig → prefab cho 3 rig còn lại~~ | ✅ **xong** — typetree `SkeletonAnimation` đã export | §2c′, §3.1′ — **2 rig boss**, 2 rig UI |
| **5** | Đối chiếu `Attack1` 33 s với nhịp thật | Cần #2 trước | §2d |
| 6 | Giải mã `m_StreamedClip` | Đắt, và đã có nhịp + Spine | §1 #2 |
| 7 | 43 director còn lại | Rất đắt, giá trị biên | §1 #5 |

---

## Còn thiếu / phải đoán

- ~~**`Boss-39001` và `Boss-39002` có thể dùng chung một rig.**~~ → **đã phân xử: ĐÚNG, dùng
  chung.** Cả hai trỏ cùng `SkeletonDataAsset` `580611` bằng PPtr thật (§3.1′). Cách đọc (b) —
  "skeleton trong hit-renderer là súng con" — **loại bỏ**: đường dẫn đầy đủ là
  `Enemy_Ingame/Body/Boss 1/Skeleton`, ngay trên thân boss.
- ~~**`skeleton__17`** trông giống rig súng~~ → **sai, đã xác định: `Popup_UnlockShip`.** 18
  animation tên `Attack01–12` dài 0,4 s là **hiệu ứng mở popup mua tàu**, không phải đòn.
  `skeleton__5` cùng popup đó.
- **Chưa rõ `UIShow` / `UiShow`** nằm trong rig boss (`skeleton__21`, `skeleton__8`) nghĩa là gì
  — có thể là animation cho màn preview boss trước khi vào trận. Chưa kiểm.
- ~~**Số 87/109 và 203** ở §4 không tái lập được.~~ → **tái lập được**, xem §4: roster =
  109 tên trong `waves.json`; 203 `Animator` / 87 prefab trên đúng roster đó.
- **Chưa có `timeScale` runtime** (cả hai nhánh đều thiếu) ⇒ mọi thời lượng ở §2d là thời lượng
  **asset**, có thể bị scale khi chơi.
- **`/anim` chưa chạy trên thiết bị lần nào.** Tự kiểm chứng minh bộ đọc trả đúng với
  component giả có cùng tên member; trên il2cpp thật, tên property của Spine/Unity có thể
  khác (ví dụ `AnimationName` là field thay vì property, hay proxy đổi tên class). Nếu
  response trả `count:0` trên máy **thì chưa kết luận được gì** — phải xem `scanned` trước.
- Mọi so sánh xuyên nhánh ở đây vắt qua hai bản game: nhánh kia bóc **1.3.118**, dữ liệu chạy
  thật của nhánh này là **1.0.69**. Riêng phần animation thì **cả hai đều đọc từ 1.3.118** nên
  không bị vấn đề này.
