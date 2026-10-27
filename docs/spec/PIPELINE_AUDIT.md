# PIPELINE_AUDIT — nhánh phân tích ngược (`ef6b75ef`) đi đúng hướng không

> Đánh giá **nhánh dữ liệu**, không đánh giá con người. Mọi kết luận dưới đây tính từ
> `git log` + file trong `c52d04e`. Không có chỗ nào là cảm nhận.
>
> Ngày đo: 2026-10-23 00:13 (commit cuối của nhánh dữ liệu).

## 0. Trả lời ngắn

**Đúng hướng 3/4 tuyến — nhưng đang lạc ở tuyến thứ 4, và mù với lỗ hổng lớn nhất.**

| Tuyến | Kết quả | Đánh giá |
|---|---|---|
| Audio · asset · wave | 69/69 WAV · 2.197 asset · wave resolve 100% | ✅ **tốt** |
| Raw typetree (`Enemy_Controller` hub) | 45 class · 24.706 dòng | ✅ **rất tốt** |
| UI layout | 114 màn · 52.936 node · 3.539 file | ✅ **tốt** |
| Spine timeline | 27 rig · 12.274 keyframe | ✅ **tốt** |
| IL2CPP constants | 98 dòng, **60 dòng là rác** | ❌ **lạc** |
| **Lớp hành vi enemy/boss** | **0 trong 4h39** | ⚠ **bỏ quên** |

## 1. Nhịp độ thật — không chậm

| Chỉ số | Số |
|---|---:|
| Tổng commit trên nhánh | **78** |
| Trong đó commit báo cáo tự động (`chore(re) [skip ci]`) | **36 (46%)** |
| **Commit làm việc thật** | **42** |
| Khung thời gian làm việc | **19:34 → 00:13 = 4h39** |
| Nhịp | **≈ 9 commit thật/giờ** |

⇒ "Phân tích lâu" là **cảm giác do 46% commit là rác tự sinh**, không phải do chậm.
Nhìn 78 commit tưởng nhiều; thực chất **42**.

## 2. Đã đóng góp gì cho spec này

6 lần dữ liệu của họ **trực tiếp đổi số** trong `docs/spec/`:

| Commit | Đổi gì trong spec |
|---|---|
| `820f9ad` | bỏ cap `Enemy_Datas` → **800 → 981** dòng |
| `aacc099` | audio **0 → 69/69 WAV** (bác bỏ kết luận "phải vgmstream" của tôi) |
| `20:11` | wave resolve tên prefab + dedupe `copies` → **23.757 khớp `Call_Data`, lệch 0** |
| `61d5385` | raw typetree → **`Enemy_Controller` hub, ghép 981/981 = 100%** |
| `070de92` | **Spine timeline 12.274 keyframe** — lấp lớp animation |
| `ef1a14f` | sửa atlas page → số region đúng |

Đây là **giá trị thật**, không phải hoạt động hình thức.

## 3. Chỗ đang lạc — IL2CPP constants

40 phút cuối (23:33 → 00:13) dồn **4/4 commit** vào tuyến này. Kết quả hiện tại:

**98 dòng "hằng số", trong đó 60 dòng cùng một giá trị `288733`.**

| Method | Đọc ra |
|---|---|
| `ArenaManager.BackUpDatas` | 288733 |
| `GameDatas.IsProVersion` | 288733 |
| `IAP_Manager.BuyProductConsumable` | 288733 |
| `Device_Get_Data.GetStringRank` | 288733 |
| `Droid_Data_Balance.GetBaseDamage` | 288733 |
| … 55 dòng nữa | 288733 |

60 method **không liên quan** trả cùng một số ⇒ đây là **đọc nhầm một ô literal pool dùng chung**,
không phải hằng số thiết kế. Bằng chứng nội tại: commit cuối `c52d04e` **tự viết**
*"metadata ptr tables gave junk"* — tức chính họ đã phát hiện.

Phần **float thì có vẻ thật** (30 giá trị phân biệt: `0.1` · `1.1` · `0.2` · `0.01` · `2.3` · `0.56` …),
nhưng **chưa biết nhân vào đâu** — `conclusions.md` của họ cũng ghi đúng như vậy.

> **Nhận định (mức A):** tuyến này đang **đốt thời gian vào lớp đắt nhất** (method body = **0,44%**
> độ phủ, xem `DATA_SYNC.md` §7.12) trong khi **5 việc rẻ hơn nhiều vẫn chưa làm**.

## 4. Lỗ hổng lớn nhất — và nó **không có trong danh sách của họ**

`docs/conclusions.md` mục *"Những gì chưa bóc được"* liệt kê 7 dòng: IL2CPP constants · công thức ·
ý nghĩa hằng số · layout runtime · particle · PvP server · spine timeScale.

**Không có dòng nào** cho lớp hành vi enemy/boss — trong khi `class-inventory` đếm được:

| Class | Instance | Trong `TARGETS`? |
|---|---:|---|
| **`Enemy_Physics`** | **981** | ❌ |
| `Enemy_Destroy` | 971 | ❌ |
| `Enemy_Burned` | 695 | ❌ |
| `Enemy_Stun` | 140 | ❌ |
| `Enemy_LookAtPlayer` | 391 | ❌ |
| 34 `*_Director` + 3 `AttackPhases` | **63** | ✅ số damage đã đọc bằng typetree (§7.22 `DATA_SYNC`) |
| `Call_Point` | **23.757** | ❌ |
| `Transform` | 228.432 object | ❌ |
| `AnimationClip` · `AnimatorController` | 791 · 308 | ❌ |

`TARGETS` trong `unity_data.py` vẫn **45 class**, **không thêm một tên nào** kể từ `61d5385`.

> **Nhận định (mức A):** đây là chỗ đánh giá **sai hướng rõ nhất** — không phải làm sai,
> mà **xếp sai thứ tự**. `Enemy_Physics` là lớp kịch bản chiếm **85,8% entry** mà spec còn trống,
> và PathID của nó **đã nằm sẵn trong `Enemy_Controller.physicsScript`** (`DATA_SYNC.md` §7.7).
> Thêm **1 dòng** vào `TARGETS` là mở.

## 5. Chi phí / lợi ích của 5 việc còn lại

| # | Việc | Chi phí | Mở ra | Nên làm |
|---:|---|---|---|---|
| 1 | Thêm **5 tên** `Enemy_*` vào `TARGETS` | **1 dòng** | 2.787 instance · enemy/boss **58,9% → 100%** · lớp kịch bản #4 **0% → 100%** | **ngay** |
| 2 | Thêm **34 `*_Director` + 3 `AttackPhases`** | 1 dòng | 63 instance · **112 field damage** — **đã lấy được bằng typetree, không cần chạy lại pipeline** | ✅ xong |
| 3 | Thêm **`Call_Point`** | 1 dòng | **23.757** — có thể chứa phần `Call_Data` bị cap | **ngay** |
| 4 | Export **`Transform`** (`m_Father`) | type mới, 228.432 object | **31,9% object** · mở **5 mắt ghép** (§7.9) | sau #1–3 |
| 5 | Export **`AnimationClip` + `AnimatorController`** | cần reader riêng | 1.099 object · đòn boss còn lại | cuối |
| — | IL2CPP method body | đắt nhất, 0,44% | ý nghĩa hằng số | **dừng lại** |

Ba việc đầu **tổng cộng 3 dòng code**. Chúng mở nhiều hơn 40 phút vừa rồi.

## 6. Cái họ làm **tốt hơn** tôi

Nói công bằng, hai điểm:

1. **`raw/typetrees`** — tôi đọc CSV trong 3 vòng và **không phát hiện CSV làm phẳng list**
   (`PathCreator.points` = `[10]`). Họ xuất raw và nó lưu đủ toạ độ. Cách làm của họ **đúng hơn**.
2. **Spine timeline** — tôi chỉ đếm được số animation; họ xuất **12.274 keyframe** với `t`/`x`/`curve`.
   Đây là bước biến "biết nhịp" thành "dựng lại được".

## 7. Kết luận

| Câu hỏi | Đáp |
|---|---|
| Có đi đúng hướng? | **Phần lớn đúng** — 5/6 tuyến cho dữ liệu thật |
| Có chậm không? | **Không** — 42 commit thật / 4h39 |
| Vì sao thấy lâu? | **46% commit là báo cáo tự sinh** + 40 phút cuối dậm chân |
| Sai ở đâu? | **Thứ tự ưu tiên**: đi vào method body (0,44%) khi 3 dòng cấu hình mở được 100% lớp hành vi |
| Thiếu gì lớn nhất? | **`Enemy_Physics` 981** — PathID đã có, chưa export |
| Cần gì để sửa? | Không cần thêm suy luận — cần **3 dòng `TARGETS`** |

> **Điều kiện lật ngược:** nếu `Enemy_Physics` export ra mà phần lớn field rỗng (như
> `Spawner.dataScript` = 0), thì lớp này **không cứu được** và thứ tự ưu tiên của họ mới đúng.
> Chưa biết trước — nhưng chi phí thử là **1 dòng**, nên không có lý do để không thử.

## 8. Cập nhật `06c9c49` (00:26) — họ đã tự sửa 1/3 đề xuất

Sau bản audit trên (`c52d04e`), nhánh dữ liệu đi thêm **3 commit**:

| Commit | Nội dung | Đánh giá |
|---|---|---|
| `3dd62e0` | **bỏ đọc int literal pool** — *"same VA gave a packed word"* | ✅ **đúng như §3 đã chỉ ra** |
| `03d3b64` | báo cáo tự sinh | — |
| `06c9c49` | **index toàn bộ raw UI** + `ui_text_keys` | ✅ dữ liệu mới đáng giá |

### 8.1 Rác `288733` đã sạch

| | `c52d04e` | `06c9c49` |
|---|---:|---:|
| Dòng mang `288733` | **60** | **0** (chỉ còn 1 dòng ghi chú giải thích) |

40 phút dậm chân ở IL2CPP constants **đã kết thúc đúng cách**: họ nhận ra ô literal pool nằm ở
segment ghi được và bỏ hẳn. Không còn con số rác nào trong báo cáo.

### 8.2 `Enemy_Physics` — **vẫn chưa**

`unity_data.py` **không đổi một dòng** giữa `c52d04e` và `06c9c49`. `TARGETS` vẫn 55 class,
**không có** `Enemy_Physics` · `Enemy_Destroy` · `Enemy_Burned` · `Enemy_Stun` ·
`Enemy_LookAtPlayer` · `*_Director` · `Call_Point` · `AnimationClip` · `AnimatorController`.

⇒ Đề xuất **chính** của audit (§5, 3 dòng code) vẫn **chưa được thực hiện**.

### 8.3 Dữ liệu mới: UI giờ là nhóm **đầy đủ nhất**

`06c9c49` index **mọi** file raw UI, gồm cả các lần chạy trước:

| Chỉ số | `20-ui-layout.md` (cũ) | `24-ui-screens.md` (mới) |
|---|---:|---:|
| File | 3.539 | **6.580** |
| Màn (`class`) | 114 | **114** |
| Tổng node (mọi instance) | 52.936 | **1.404.553** |
| Node của instance lớn nhất/màn | — | **119.368** |
| Dòng text/key | — | **103.655** |

**Đơn vị đếm phải nói rõ:** 1.404.553 là **tổng mọi instance** (mỗi màn có 6–178 file);
lấy **instance lớn nhất của mỗi màn** thì là **119.368 node**. Con số 52.936 tôi ghi trước đây
là **1 instance/màn** ⇒ **không sai, chỉ khác đơn vị**.

**`ui_text_keys` (103.655 dòng)** — dữ liệu chưa từng có:

| Chỉ số | Số |
|---|---:|
| Node `TextMeshPro` (text cứng) | **81.098** — trong đó **81.131** có chuỗi hiển thị |
| Node `LanguageTextMeshPro` (đa ngữ) | **22.517** — trong đó **22.524** có key |
| **Key đa ngữ khác nhau** | **325** |
| Màn phủ | **114 / 114** |

> **Nhận định (mức A):** **325 key** cho **22.524** node ⇒ mỗi key dùng trung bình **69 lần**.
> Nghĩa là toàn bộ chữ đa ngữ của game gói trong **325 chuỗi** — dịch hết là dịch xong UI.
> Đây là con số **nhỏ hơn nhiều** so với `12-localization.csv` (1.898 dòng), và là **tập thật sự dùng**.

### 8.4 Còn thiếu sau `06c9c49`

| # | Thứ | Trạng thái |
|---:|---|---|
| 1 | `Enemy_Physics` 981 | ❌ vẫn ngoài `TARGETS` |
| 2 | 37 `*_Director` | ❌ |
| 3 | `Call_Point` 23.757 | ❌ |
| 4 | `Transform` (m_Father) | ❌ |
| 5 | `AnimationClip` · `AnimatorController` | ❌ |
| 6 | `width × height` sprite | ❌ `datas/sprites.csv` chỉ có `bytes` |
| 7 | `ParticleSystem` | ❌ (họ đã tự ghi trong `conclusions.md`) |

## 9. CI: có song song, nhưng **song song sai kiểu** — và 70% thời gian là một step vô dụng

Đo từ API: run `39876830055` (00:13:36 → 00:24:36, **11 phút 00 giây**), step-by-step.

### 9.1 Thời gian thật chia thế nào

| Nhóm | Step | Thời gian | % |
|---|---|---:|---:|
| Setup + Il2CppDumper + toàn bộ phân tích | 1–25 | **154 s (2p34)** | **23%** |
| **`Build REA … and analyze APK`** | **26** | **460 s (7p40)** | **70%** |
| Publish release + artifact + commit | 27–31 | 37 s | 6% |
| Post | 58–63 | 1 s | ~0% |

**Bên trong 154 s đó, phần tính toán thật chỉ ~85 s:**

| Step | Nội dung | Thời gian |
|---|---|---:|
| 15 | Export asset (texture/sprite/audio) | **31 s** |
| 23 | Dump UI layout | **21 s** |
| 11 | Chạy Il2CppDumper | 13 s |
| **19** | **`unity_data.py` — extract typetree** | **12 s** |
| 21 | Wave composition | 11 s |
| 24 | Spine rig + audio map | 9 s |
| 14 | Unity asset probe | 9 s |
| 10 | Tải Il2CppDumper | 9 s |
| 13 | `pip install UnityPy` | 7 s |
| **22** | **IL2CPP constants** | **1 s** |
| 1–9, 12, 18, 20, 25 | còn lại | ~23 s |

### 9.2 Step 26 (REA) chiếm 7p40 và **không cho dữ liệu game**

Step này: `git clone mytechnotalent/rea` → `cargo build --release` → chạy `rea analyze` trên
APK, rồi `libil2cpp.so` (timeout **1200 s**) và `libunity.so` (timeout **900 s**).

Kết quả trong `05-rea.md`:

> *"native code analysis does not apply"* · *"packing score 2"* · *"27 indicators extracted, including 1 URL"*

**Không một dòng dữ liệu game.** Đây là báo cáo **container APK chung** — thứ Il2CppDumper đã làm tốt hơn
ở step 11 (13 giây).

⇒ **≈70% compute của mọi lần chạy đổ vào một step mà đầu ra không được dùng ở đâu trong spec.**

### 9.3 Vì sao **thêm 1 class** cũng tốn 11 phút

`analyze-apk.yml` có **1 job, 25 step tuần tự**, không `strategy.matrix`, không `needs`, không `concurrency`.

| Việc muốn làm | Compute thật cần | Nhưng phải chạy lại |
|---|---:|---|
| Thêm `Enemy_Physics` vào `TARGETS` | **~3 s** (step 19: 12 s → 15 s) | **cả 25 step = 11 phút** |
| Thêm 37 `*_Director` | ~2 s | cả 25 step |
| Sửa 1 dòng `wave_report.py` | 11 s | cả 25 step |

Đây là lý do **40 phút cuối dồn vào IL2CPP constants**: vòng phản hồi **11 phút/lần** khiến thử-sai
đắt, nên dễ chọn "đào sâu một chỗ" thay vì "thử 5 chỗ rẻ".

### 9.4 Song song **đang có** — nhưng là bản sao, không phải chia việc

Lúc đo, **3 run `in_progress` cùng lúc** (00:24:53 · 00:26:57 · 00:27:12). Không có `concurrency:`,
nên mỗi lần push tạo **một bản sao đầy đủ 25 step**.

| Kiểu song song | Đang có? | Tác dụng |
|---|---|---|
| Nhiều run cùng lúc, **cùng nội dung** | ✅ | **0** — 3 run = 3 × 11 phút cho cùng kết quả |
| Nhiều job, **mỗi job một mục** | ❌ | — |

**Tổng đã tiêu:** 30 run thành công × 11,0 phút = **329 phút**. Trong đó **~230 phút là REA**.

### 9.5 Sửa: matrix 6 job + bỏ REA + gộp run

| # | Sửa | Dòng code | Tiết kiệm |
|---:|---|---|---|
| 1 | **Bỏ step 26 (REA)** hoặc đặt `if: false` | 1 | **7p40/lần (−70%)** |
| 2 | `concurrency: {group: analyze, cancel-in-progress: true}` | 2 | hết run trùng |
| 3 | Tách `payload` job (XAPK + extract + Il2CppDumper) → `upload-artifact`; 6 job `needs: payload` chạy song song: `typetrees` · `waves` · `ui` · `spine` · `assets` · `consts` | ~40 | wall-clock **11 → ~3–4 phút** |
| 4 | `paths` filter theo từng script | 5 | sửa `wave_report.py` chỉ chạy job `waves` |

Sau khi sửa, thêm `Enemy_Physics` = **~30 s** (setup + job `typetrees`), không phải 11 phút.
**5 lớp hành vi còn thiếu có thể export trong một buổi** thay vì một đêm.

> **Điều kiện lật ngược:** nếu `rea analyze libil2cpp.so` có cho ra symbol/offset mà
> `Il2CppDumper` không có, thì step 26 đáng giữ — nhưng `05-rea.md` hiện **không chứa** kết quả đó
> (`rea-native.log` không được đưa vào `docs/`). Muốn biết phải xem artifact, không xem report.

### 9.6 Một điểm nữa: 46% commit là rác

Mỗi run kết thúc bằng commit `chore(re): IL2CPP + Unity + REA analysis reports [skip ci]`.
**36 / 78 commit** là loại này ⇒ mỗi lần phân tích đẻ ra **2 commit** (1 của người, 1 của bot),
làm lịch sử khó đọc và kích hoạt thêm workflow khác nếu `paths` không chặn.

## 10. `bb97453` (00:36) — họ đã làm **toàn bộ** 4 đề xuất, và CI nhanh hơn 63%

| Đề xuất của tôi | Commit này | Bằng chứng |
|---|---|---|
| §5 #1 — thêm 5 class `Enemy_*` | ✅ **thêm 27 class** | `TARGETS` nay có `Enemy_Physics` · `Destroy` · `Burned` · `Stun` · `UI` · `LookAtPlayer` · `Attack` · `Sync_Attack` · `SpawnChilds` · `DropGold` · `Rotate` · `Helicopter` · `Display` · `Hp_Bar` · `Laser_Gun` · `Rocket_Attack` · `CameraVibrate` · `EfxDestroyed` · `BombDie` · `BurstBulletWhenDie`… |
| §5 #2 — 37 `*_Director` | ✅ **ghép theo hậu tố** | `TARGET_SUFFIXES = ("_Director", "_MiniDirector", "ChildDirector", "_AttackPhases")` — tự bắt class mới khi game cập nhật |
| §5 #3 — `Call_Point` | ✅ | thêm vào `TARGETS` |
| §5 #4 — `Transform` | ✅ **export thật** | `transform-tree.tsv.gz` **228.432** Transform |
| §9.1 — bỏ REA | ✅ **opt-in** | `if: github.event_name == 'workflow_dispatch' && inputs.run_rea`, mặc định `false` |
| §9.2 — `concurrency` | ✅ | `group: analyze-apk-${{ github.ref }}` · `cancel-in-progress: true` |
| §7.8 — cap | ✅ | `CAP_OVERRIDES`: `Call_Data` **30.000** · `PointToPoint_Spawner` 14.000 · `PathCreator` **1.800** · `Call_Point` 30.000 |

**Kết quả đo được:** run `39879117958` = **4 phút 01 giây** (00:36:27 → 00:40:28), trước đó **11 phút 00**.
**−63% thời gian.** `typetree` từ **45 → 110 class**.

### 10.1 Ba điều dữ liệu mới dạy — trong đó **một điều tôi sai**

1. **`Transform` mở mắt ghép nhưng không tới 100%.** `Gun_Attack` → `Enemy_Controller`: **95,6%**
   (leo tổ tiên) hoặc **99,3%** (root tuyệt đối). `Boss_BodyPhysics`: **75,3% / 87,3%**.
   Nguyên nhân: prefab lồng + súng UI dùng chung component. **Kết luận cũ của tôi ("1 bảng mở 5 mắt") đúng một nửa.**
2. **`Call_Point` không chứa phần `Call_Data` bị cắt.** 23.757/23.757 khớp 1-1, nhưng trỏ về
   `Call_Data` chứ không mang dữ liệu spawner. ⇒ vẫn phải bỏ cap thật.
3. **`Enemy_Physics` rỗng — tôi đã sai rõ ràng.** 981 instance, **2 field**,
   `allColliders = []` **981/981**. Damage va chạm **không nằm ở đây**.
   Tôi đã khẳng định export nó "mở khoá 85,8% entry". Sai. Điều kiện lật ngược tôi tự ghi đã xảy ra.

### 10.2 Bài học chung, ghi để lần sau không lặp

> **PathID có sẵn ≠ nội dung có sẵn.** Một class có 981 instance và PathID trỏ đúng
> vẫn có thể **0 field hữu ích**. Chi phí kiểm là 1 dòng — nhưng kết luận phải chờ **sau** khi đọc.

Điều này áp dụng cho cả 2 phía: audit của tôi đúng về **thứ tự** (đọc rẻ trước),
sai về **kỳ vọng nội dung** (tưởng có damage).

### 10.3 Còn lại sau `bb97453`

| # | Thứ | Trạng thái |
|---:|---|---|
| 1 | `AnimationClip` 791 · `AnimatorController` 308 | ❌ **giờ là mắt chặn lớn nhất** — Director đã có nhưng giữ *tham chiếu* tới 2 loại này |
| 2 | Damage va chạm enemy | ❌ không ở `Enemy_Physics`; phải tìm ở `Collider2D` / `Damager` / `Enemy_Datas` |
| 3 | `Call_Data` đầy đủ 23.757 | ⚠ cap đã nâng 30.000 — **chưa thấy file mới**, cần run kế tiếp |
| 4 | `width × height` sprite | ❌ `datas/sprites.csv` chỉ có `bytes` |
| 5 | `ParticleSystem` | ❌ |

## 11. `0a5083c`+`e162065` (00:47) — export `AnimationClip`/`AnimatorController` + tool ghép

| Việc | Kết quả |
|---|---|
| `AnimationClip` **791** + `AnimatorController` **308** | ✅ đã export (`native-types.jsonl.gz`, 19 KB) |
| `datas/prefab_joins.csv.gz` | ✅ **3.870 dòng** · 7 mắt ghép · **100%** |
| `ParticleSystem` | chỉ **đếm**, chưa xuất chi tiết (họ ghi rõ lý do: ~30 module) |

### 11.1 Bảng ghép **hoàn chỉnh** — 7/7 mắt 100%

| Class.field | Dòng |
|---|---:|
| `Enemy_Controller.m_GameObject` | 981 |
| `Wave.startPoint` · `endPoint` | 686 · 686 |
| `Enemy_Movement.parentRotate` | 558 |
| `Gun_Attack.m_GameObject` | 458 |
| `Boss_BodyPhysics.m_GameObject` | 251 |
| `Stage_Behaviour.bossObj` | 250 |

Mắt cuối `Stage_Behaviour.bossObj` (mà §7.9 xếp vào nhóm "0%, thiếu Transform") **đã 250/250 = 100%**.
⇒ **Không còn mắt ghép cấu trúc nào dưới 100%.** Nhóm B của §7.9 **đã đóng hoàn toàn**.

### 11.2 Nhưng 18% bảng ghép là **UI**, và nó làm sai một số của tôi

| | Trước | Sau khi biết nguồn |
|---|---:|---:|
| Prefab có súng | 42 | **68** (Boss **26**, không phải 21) |
| Súng "thật" | 458 | **319** — 139 là preview trên `Board_SelectBoss`/`Board_FightBoss` |
| `Boss_BodyPhysics` "thật" | 251 | **185** — 66 là trên màn UI |
| `Enemy_Controller` "thật" | 981 | **777** |

### 11.3 `AnimationClip` — có **danh mục + nhịp**, không có **curve**

| | Số |
|---|---:|
| Clip / tên khác nhau | 791 / **226** |
| `m_StopTime > 0` | **707** |
| Median / max | **1,9 s** / **75,0 s** |
| Lặp | 251 |
| Clip có event | **318** — **793 event** |
| `m_SampleRate` | **60 fps** ×764 |
| **`m_StateMachineBehaviours > 0`** | **0 / 308** |
| Curve trong typetree | **0 / 791** (nằm ở `m_StreamedClip`) |

> **Nhận định (mức A):** đây là lần đầu **793 event của Mecanim** đếm được — và nó **khớp đúng
> 793 tham chiếu clip** của 308 controller. Cộng `m_StateMachineBehaviours = 0` ⇒ cơ chế đòn của boss
> là **animation event gắn trên clip**, không phải state machine. Điều này **xác nhận** mục 3.1 của
> `ANIMATION.md` và **bác bỏ** cách hiểu "state machine điều khiển đòn".

### 11.4 Còn lại đúng 3 thứ

| # | Thứ | Vì sao còn |
|---:|---|---|
| 1 | **Curve của 791 clip** | streamed — cần `parse_as_object()` riêng |
| 2 | **`ParticleSystem`** 4.845 | ~30 module, nặng; mới đếm |
| 3 | **Map `Animator` → prefab** | `Animator` (5.792) chưa export; controller là asset lẻ |

Ngoài ra: **method body** (0,44%) vẫn ngoài tầm — nhưng giờ **không còn là mắt chặn** cho bất kỳ
câu hỏi thiết kế nào nêu trong `SCRIPTS.md` §7, trừ `number = 0` (số quân).

### 11.5 `ae1f2be` — thử keyframe, **thất bại có kiểm soát**

`anim_curves.py` dùng `parse_as_object()` trên **791 clip**: **0 lỗi parse, 0 keyframe**.
Họ ghi đúng nguyên nhân (`m_StreamedClip`) và **không giả vờ thành công** — đây là cách xử lý đúng.

`4c84d90` còn **tự kiểm lại số 45.659** độc lập từ `Call_Data` đầy đủ: khớp. Không phải chỉ
nhận kết luận của nhánh spec.

### 11.6 Một số của tôi bị sửa ngược lần nữa

| Tôi ghi | Thực tế |
|---|---|
| `Stage_Behaviour.bossObj` 250 = mắt ghép **về boss** | **250/250 root `Board_Maps`** — là **icon boss trên bản đồ**, không phải boss |
| "Muốn keyframe chỉ cần `parse_as_object()`" | **0 keyframe** — cần decoder `m_StreamedClip` riêng |

## 12. Còn thiếu / phải đoán

| # | Thứ | Mức | Ghi chú |
|---:|---|---|---|
| 1 | 5 class `Enemy_*` có field thật hay rỗng như `Spawner.dataScript` | **C** | ✅ **đã trả lời** (`UNITY_RULES` §1.2): `Enemy_Appear` **0 field** ở **914** instance · `Enemy_Attack` **0** ở **51** · `Spawner.dataScript` **23.570/23.570** rỗng |
| 2 | `Call_Point` có phải bản đầy đủ của `Call_Data` | **C** | — |
| 3 | 60 dòng `288733` — ô literal pool nào bị đọc nhầm | **B** | — |
| 4 | Nhánh dữ liệu có tiếp tục sau `c52d04e` không | **C** | — |
| 5 | `rea-native.log` (kết quả trên `.so`) có giá trị gì | **C** | nằm trong artifact, **không** nằm trong `docs/` |
| 6 | Repo có bật hạn mức Actions hay không | **C** | chưa thấy ghi chú; chưa tới giới hạn dù 329 phút |
| 7 | 6 job matrix có cùng cache XAPK được không | **B** | `actions/cache` dùng chung key → có; cần artifact cho payload đã giải nén |
