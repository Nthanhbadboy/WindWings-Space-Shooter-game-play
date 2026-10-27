# VERIFY_ROUND2 — đo lại toàn bộ con số đã viết

> **Ngày:** 23/10 · **HEAD:** `4eb81ea61` · **Cách chạy:** `python3 tools/verify-claims.py`
>
> Vòng trước (`VERIFY_ROUND1.md`) kiểm **phán quyết** của nhánh dữ liệu. Vòng này kiểm **con số
> của chính mình**: mỗi số trong docs được đo lại từ dữ liệu nguồn, và dòng doc phải còn ghi đúng
> số đó. Không đọc bằng mắt — 55 tuyên bố, mỗi cái một phép đo chạy được.

---

## 0. Kết quả

| | Số |
|---|---:|
| Tuyên bố được kiểm | **55** |
| Đo ra đúng như doc | **53** |
| **Sai — đã sửa doc** | **4**, trong đó **1 mục (1.4) hoá ra đúng** — xem §5d |
| Không kiểm được offline (SKIP, có lý do) | **2** |
| FAIL còn lại | **0** |

Chạy trên máy: `PASS 53 · FAIL 0 · SKIP 2`, mã thoát 0. Bản sao cố tình lệch một số cho ra
`FAIL 1` và mã thoát 1 — cổng CI thật sự đỏ, không phải chỉ in chữ.

---

## 1. Bốn chỗ sai — đều đã sửa

### 1.1 `SUMMARY_vi.md`: "18 file có `fields`" → **21**

Đếm lại trong `docs/apk-analysis/ramus/2026-10-23-phone/`: **20 file `statics_*` + `boss_boss_gp.json`**
= 21. Ngay tại `5b3c8ae` mà bản cũ dẫn cũng đã là 21 — con số 18 sai ngay từ lúc viết, không phải
"cũ rồi".

**575 field / 88 field tên type / 15,3 % không đổi.** Hai file bị đếm sót không có field nào rơi vào
nhóm tên type.

### 1.2 `ANIMATION.md`: "27 rig · **180** animation · 616 bone" — tự mâu thuẫn

Ba số trong **cùng một dòng** đếm theo hai cách:

| Số | Đếm trên | Đúng |
|---|---|---|
| 27 rig | **26** `skeleton*` + `Saw` | ✅ |
| 616 bone | **cả 27**, gồm `Saw` | ✅ |
| 180 animation | **chỉ 26 rig skeleton** — `Saw` có 5 (`Fly · Fly_Idle · Idle · Idle_Fly · Teleport`) | ❌ phải là **185** |

⇒ Tổng đúng là **185 animation**. Dòng 55 (`6 × 21 + 7 + 9 + 10×2 + 18 = 180`) thì đúng, vì nó
đếm 26 rig — nay đã ghi chú rõ.

### 1.3 `ANIMATION_GAPS.md`: "25 rig + `Saw`" → **26 rig + `Saw`**

Tên file thật: `skeleton.json` + `skeleton__2` … `skeleton__26` = **26**, cộng `Saw.json` = 27.
Bản cũ ghi 25, cộng `Saw` chỉ ra 26 — thiếu một rig.

### 1.4 ~~`ANIMATION.md`: "enemy/boss chỉ **203**" → **154**~~ ⚠️ **MỤC NÀY SAI — xem §5d**

Đếm lại trên `datas/animator_map.csv.gz`, lọc prefab root khớp `CB-|Boss-|MB-`: **154 Animator /
63 prefab**. Không bộ lọc nào ra 203. Doc nay ghi 154 và trỏ về `ANIMATION_GAPS.md` §4 để giữ dấu
vết con số cũ.

> ⚠️ **Sửa lại ở §5d: mục này SAI.** 203 tái lập được **chính xác** — chỉ cần biết định nghĩa
> roster (109 tên trong `waves.json`). Đã khôi phục 203 trong `ANIMATION.md`. Con số 154 chỉ đúng
> với một tập lọc khác (mẫu tên), không phải một sửa chữa.
>
> Giữ nguyên mục này thay vì xoá, vì đây là lần thứ năm mắc cùng một lỗi: lấy một tập khác thay
> cho định nghĩa.

---

## 2. Hai con số **không kiểm được offline** — và vì sao

| Số | Nguồn doc | Vì sao không kiểm được |
|---|---|---|
| **251** clip lặp | `ANIMATION.md` | `anim_clips.json` không có trường loop. `native-types.jsonl.gz` có `m_WrapMode` nhưng **toàn bộ 791 clip đều 0** — reader không giải được giá trị. Chỉ tái lập bằng UnityPy đọc thẳng asset |
| **2.185** `Sprite` | `ANIMATION.md` | `native-types.jsonl.gz` chỉ chứa **5 loại** type (`Animator` 5.792 · `ParticleSystem` 4.845 · `AnimationClip` 791 · `AnimatorController` 308 · `Camera` 6). Không có `Sprite`, nên số 2.185 đến từ asset scan, không có trong bản export |

Hai số này **không bị coi là sai** — chỉ là không có nguồn để đo. Công cụ báo SKIP kèm lý do thay
vì đoán.

---

## 3. Bốn con số **không tái lập được** — chưa sửa, vì thiếu định nghĩa

Khác với §1: ở đây tôi **không kết luận doc sai**, vì chưa có định nghĩa để đo lại.

| Số | Vấn đề |
|---|---|
| **109** prefab enemy/boss ("roster thực sự được spawn") | Cắt `gameobject` theo `/` đầu tiên cho ra **253** root (`Enemy_Movement`) và **258** (`Enemy_Appear`). Hai phép đo khác nhau, chưa có định nghĩa nào tái lập được con số 109 |
| **107** prefab có `Enemy_Appear` | như trên |
| **44** class `*_Director` | `raw/typetrees/` chỉ có **33** file `*_Director`; 44 có thể tính cả class không được export |
| **117** `SkeletonAnimation` | Không typetree nào chứa type này (`native-types` không có, `prefab_joins` không có class Spine) |

⇒ Muốn đóng, phải viết **định nghĩa** của "roster" trước, rồi đếm lại theo đúng định nghĩa đó.

---

## 4. Những gì đã kiểm và **đúng**

Không phải chỉ đi tìm cái sai. 53 tuyên bố đã đo lại và khớp:

| Nhóm | Đã kiểm |
|---|---|
| **Runtime (điện thoại)** | 575 field / 88 tên type / 15,3 % · `listStatValues` **10** · `listMapDatas` `_count` **250** nhưng chỉ **128** phần tử · `percentByLevels1/2` đúng từng số · `GP_Datas` 65 field |
| **Spine** | 27 rig · **185** animation · **12.274** keyframe · **21** event · **616** bone · **446** slot · 4 rig có đòn · 23 rig không có đòn |
| **Unity clip** | **791** clip · **226** tên · **318** clip có event · **793** event · median **1,9 s** · max **75,0 s** |
| **Enemy** | `Enemy_Movement` **981** · `Enemy_Appear` **914** instance / **0 field** · `Enemy_HitSkeletonRenderer` **17** · **46** boss · **39** prefab `Boss-*` |
| **Ghép rig** | **18/27** khớp đúng một TextAsset bằng tập bone |
| **Số điện thoại** | `MaxModeIndex` 4 · `levelDelta [1,2,3.6,3.6]` · `StartHp` 2500 · `stepCommon` 0,18 · `shipCloneDamage [1.35,1.6,1.86]` · `DeltaStarCost` 50 · `StartStarCost` 30 · `MaxLevelPerRanks [10,20,30,60,120,250,500]` · `PercentToCompleteMissions222 [0.2,0.6,0.98]` |
| **Code** | route `GET /anim` · `collect.sh` gọi nó · gate đòi `anim-ingame.json` · 5 lần biên dịch + 1 self-test = 6 mục ma trận |

---

## 5. Cái đã học được từ chính vòng này

**Bốn lỗi trong 55 tuyên bố, và cả bốn đều thuộc một dạng: đếm hai thứ khác nhau rồi ghi vào một
dòng.** 18 vs 21 file, 180 vs 185 animation, 25 vs 26 rig, 203 vs 154 — không cái nào là tính sai;
tất cả là **đếm trên tập khác nhau mà không ghi tập nào**.

Vì vậy công cụ này kiểm **hai chiều**, và mỗi claim phải khai báo **định nghĩa** ngay trong mã. Một
con số không kèm định nghĩa sẽ không bảo vệ được — nó chỉ đúng cho tới lần đếm sau.

---

## 5b. Cập nhật cùng ngày — dữ liệu đã kéo về repo

Nhánh dữ liệu tiến lên `6dc5c4bf5` và **đã đóng hai mục tôi đánh dấu**:

| Mục | Trước | Nay |
|---|---|---|
| `Enemy_Appear` chưa có asm | §2a | **Có.** `Appear` = vỏ gọi delegate 32 B, không logic. Có **39 lớp con**, cả 39 là `*_Director` |
| Ghép rig → prefab | chỉ suy theo tên bone, 18/27 | **Có typetree `SkeletonAnimation`** → ghép trực tiếp bằng con trỏ |

**Và sửa một kết luận của chính tôi:** 4 rig có animation tên đòn, nhưng chỉ **2 là boss**.
`580619` (`skeleton__17`) và `580623` (`skeleton__5`) nằm trên **`Popup_UnlockShip`** — 18 animation
`Attack01–12` dài 0,4 s là hiệu ứng mở popup mua tàu.

Bộ kiểm nay **62 claim**: thêm nhóm **G** (9 claim) cho bằng chứng mới, và đọc **bản local trước**
— chạy được cả khi không có nhánh dữ liệu. Toàn bộ nguồn ghi ở `datas/PROVENANCE.md`.

## 5c. Kéo lần 2 (`019e704d1`) — cổng bắt được chính tôi

Nhánh dữ liệu tiến thêm một commit và bổ sung `spine-prefabs.json`: ghép
`SkeletonAnimation → SkeletonDataAsset → TextAsset` bằng **PPtr thật**.

| prefab | component | SDA | TextAsset |
|---|---:|---:|---:|
| `Boss-39001` | 602882 | **580611** | 918 |
| `Boss-39002` | 664302 | **580611** | 918 |
| `Boss-39003` | 602881 | **580613** | 895 |

**Kết luận cũ của tôi sai.** Tôi từng hạ quan hệ `Boss-39002 → 580611` xuống mức B, lý do
"SkeletonAnimation của nó không nằm trong 20 instance đã export". Nay biết `Boss-39002` **có**
component `664302` — thư mục 20 file là **export một phần**.

**Và cái sai thứ hai, đáng chú ý hơn: cổng của tôi đã PASS trong khi kết luận sai.** Claim `G8`
đo `"Boss-39002 có SkeletonAnimation trong 20 file không?"` → `True`, nên nó xanh. Nhưng câu hỏi
đúng phải là *"trong game"*, không phải *"trong tập đã export"*. Đại lượng thay thế hẹp hơn câu
chữ — đúng loại lỗi mà cả tài liệu này đang chống.

Đã sửa: `G8` nay đọc thẳng `spine-prefabs.json`. `G10` giữ con số **3 component** để lần sau ai
đọc nhầm "20 = tất cả" thì đỏ ngay. Tổng **69 claim** (67 PASS · 2 SKIP).

> **Bài học:** một cổng kiểm cũng có thể đo sai thứ. Nó chỉ bảo vệ được đúng cái nó thật sự đo.

## 5d. Sửa lại chính §1.4 — con số **203 là đúng**, tôi đã sửa nó thành sai

Đây là chỗ tệ nhất trong cả vòng kiểm.

§1.4 ở trên ghi *"enemy/boss 203 → 154"*, và `ANIMATION.md` đã bị sửa theo. **Sai.** Con số 203
tái lập được **chính xác**, chỉ cần biết "109 prefab roster" nghĩa là gì — và cái đó chưa ai viết
ra cho tới hôm nay.

Định nghĩa thật:

```
datas/waves.json → waves[].spawners[].enemies[] → đếm tên phân biệt = 109
```

Đếm `Animator` trên đúng 109 tên đó: **203 instance / 87 prefab**. Khớp từng số với nhánh spec.

| tập lọc | Animator / prefab |
|---|---:|
| **roster `waves.json` (109)** | **203 / 87** |
| mẫu tên `CB-`·`Boss-`·`MB-` | 154 / 63 |
| roster ∩ mẫu tên | 148 / 60 |
| prefab tên `Boss-` | 92 / 36 |

**Cả hai nhánh đều đúng** — khác tập, không khác dữ liệu. `203 > 154` được vì roster còn 37 prefab
mang tiền tố khác (`CD-` 15 · `W2-` 6 · `XB-` 5 · `GD-` 4 · `BB-` 4 · `H-` 2 · `W1-` 1).

### Vì sao tôi sai — cùng một lỗi, lần thứ năm

Tôi đếm theo **mẫu tên** rồi đem so với con số đếm theo **roster spawn**. Hai đại lượng khác
nhau. §5 ở trên viết *"bốn lỗi, cả bốn cùng một dạng"* — giờ là **năm**, và lần này tôi mắc nó
ngay trong tài liệu đi sửa lỗi đó.

Khác biệt duy nhất lần này: **109 chưa từng có định nghĩa**, nên không có gì để đối chiếu. Một con
số không định nghĩa thì không thể kiểm — và tôi đã lấy một tập khác thay vào rồi tuyên bố nó sai.

Đã sửa: `ANIMATION.md` khôi phục 203 kèm định nghĩa; claim `B14` đo **đúng roster**, `B15` khoá
định nghĩa 109, `B16`/`B17` giữ hai định nghĩa kia để không ai lẫn nữa. Thêm nhóm **H** (3 claim)
cho chính bảng spawn — phân bố tiền tố, quy mô 22.461 lượt spawn, và **182** prefab có
`Enemy_Movement` trong asset (khác 109 được spawn).

Tổng **75 claim** (73 PASS · 2 SKIP).

> **Bài học:** thứ tự đúng là *viết định nghĩa trước, đếm sau*. Làm ngược lại thì con số đúng
> cũng bị xoá vì không ai tái lập được nó.

## 6. Cách chạy lại

```bash
python3 tools/verify-claims.py                 # đủ 55 claim
python3 tools/verify-claims.py --only B        # chỉ nhóm Spine/clip
python3 tools/verify-claims.py --ref <sha>     # chỉ định ref nhánh dữ liệu
```

CI: `.github/workflows/docs-verify.yml` chạy trên mọi PR đổi `docs/**` hoặc `tools/verify-claims.py`.
Nhánh dữ liệu được fetch best-effort: không có thì nhóm B/C/F **SKIP**, nhóm A/D/E vẫn kiểm —
nên job vẫn có nghĩa trên clone sạch.
