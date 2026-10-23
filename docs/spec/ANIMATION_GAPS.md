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
| **Spine** (25 rig + `Saw`) | 27 rig · **185** animation · **12.274** keyframe | **100 %** timeline + **21** event có mốc thời gian | rig → đơn vị trong game (**đóng được 1 phần**, §3) |
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

> Nhận định: đây là việc rẻ nhất trong toàn bộ danh sách — thêm `Enemy_Appear` (và
> `Enemy_Rotate`, `Enemy_Sub`) vào `TARGETS` của exporter rồi chạy lại, giống hệt cách commit
> `cf0a71d18` đã làm cho `Enemy_Get_Datas` / `Enemy_Controller` / `Enemy_Health`.
> Không cần thiết bị, không cần chạy game.

**Vì sao quan trọng:** trong game bắn máy bay, "enemy xuất hiện" là hiệu ứng người chơi thấy
**mỗi wave, mỗi enemy** — nhưng hiện chỉ biết nó tồn tại, chưa biết nó làm gì.

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

> Nhận định: với **46 boss** trong `Data_Boss` và **39 prefab `Boss-*`**, mà chỉ **4 rig** có
> animation đòn, thì phần lớn boss **không** dùng Spine để đánh — chúng dùng `Animator` (92
> instance trên 36 prefab `Boss-*`) hoặc thuần code. Đây là kết luận cấu trúc chưa tài liệu nào
> viết ra, và nó ảnh hưởng trực tiếp tới kế hoạch clone.

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

### 2e. Chưa có **một** phép đo runtime nào về playback

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

### 3.1 `skeleton__21` = rig của `Boss-39002` (mức **A**)

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

⇒ **`skeleton__21` là rig của `Boss-39002`.** Đây chính là mắt nối mà `23-spine-anim.md` ghi là
"chưa map rig → đơn vị". Đóng được cho **1 trong 4** rig có đòn.

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

## 4. Một chỗ **hai nhánh đá nhau** — chưa phân xử

| Nguồn | Số `Animator` trên enemy/boss |
|---|---|
| Nhánh kia (`32-enemy-boss-animation.md`) | **63 prefab · 154 instance** (lọc `CB-`/`Boss-`/`MB-` + id) |
| Nhánh spec (`ANIMATION.md` §4.5) | **87 / 109 prefab · 203 instance** (roster "prefab thực sự được spawn") |

Tôi đếm lại trên `datas/animator_map.csv.gz`: đúng **154 instance / 63 prefab** với bộ lọc của
nhánh kia, và **117 prefab** nếu mở rộng mẫu tên (`Boss-` · `CB-` · `MB-` · `W-**` · `HT-`).
Không bộ lọc nào cho ra 87/109.

⇒ **Khác biệt nằm ở định nghĩa roster**, không phải ở dữ liệu — nhưng chưa ai viết ra định nghĩa
của con số 109. Cho tới lúc đó, **203 và 87 là số không kiểm lại được**.

---

## 5. Việc nên làm, xếp theo chi phí

| Ưu tiên | Việc | Vì sao rẻ | Đóng được gì |
|---:|---|---|---|
| **1** | Thêm `Enemy_Appear`, `Enemy_Rotate`, `Enemy_Sub` vào `TARGETS` của exporter, chạy lại CI | Cùng khuôn commit `cf0a71d18`, không cần thiết bị | Toàn bộ §2a |
| **2** | Nối `SkeletonAnimation.AnimationName` + `Skeleton.time` vào bridge | ~30 dòng C#, đã có `OnMain` + `Jw` | §2e — kiểm playback thật |
| **3** | Ghi rõ định nghĩa "109 prefab roster" trong `ANIMATION.md` | Chỉ là viết lại | §4 |
| **4** | Ghép rig → prefab cho 3 rig còn lại | Cần `SkeletonRenderer`/`SkeletonAnimation` typetree — **chưa export** | §3.1 mở rộng |
| **5** | Đối chiếu `Attack1` 33 s với nhịp thật | Cần #2 trước | §2d |
| 6 | Giải mã `m_StreamedClip` | Đắt, và đã có nhịp + Spine | §1 #2 |
| 7 | 43 director còn lại | Rất đắt, giá trị biên | §1 #5 |

---

## Còn thiếu / phải đoán

- **`Boss-39001` và `Boss-39002` có thể dùng chung một rig.** Phép thử "slot của hit-renderer
  phải là tập con của slot rig" chỉ cho **một** ứng viên cho Boss-39001 — chính `580611`
  (`skeleton__21`), mà đó lại là rig của Boss-39002 (§3.1). Hai cách đọc: (a) hai boss dùng
  chung rig; (b) `skeleton` trong hit-renderer là **skeleton con** (súng), không phải skeleton
  thân. **Chưa phân xử** — thiếu typetree của `SkeletonRenderer`.
- **`skeleton__17`** (12 đòn × 0,4 s, `Shot` ở 0,333 s) trông giống **rig súng** hơn là thân
  boss, nhưng chưa có bằng chứng trực tiếp. Đừng gán nó cho boss nào.
- **Chưa rõ `UIShow` / `UiShow`** nằm trong rig boss (`skeleton__21`, `skeleton__8`) nghĩa là gì
  — có thể là animation cho màn preview boss trước khi vào trận. Chưa kiểm.
- **Số 87/109 và 203** ở §4 **không tái lập được** bằng dữ liệu trong repo.
- **Chưa có `timeScale` runtime** (cả hai nhánh đều thiếu) ⇒ mọi thời lượng ở §2d là thời lượng
  **asset**, có thể bị scale khi chơi.
- Mọi so sánh xuyên nhánh ở đây vắt qua hai bản game: nhánh kia bóc **1.3.118**, dữ liệu chạy
  thật của nhánh này là **1.0.69**. Riêng phần animation thì **cả hai đều đọc từ 1.3.118** nên
  không bị vấn đề này.
