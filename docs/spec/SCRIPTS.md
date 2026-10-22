# SCRIPTS — kịch bản quyết định gì, và đọc được đến đâu

> WindWings: Space Shooter — Unity 2022.3.62f3 · IL2CPP · `com.Wind.wings.Space.Shooter` 1.3.118.
>
> **Điểm xuất phát:** mọi con số trong `docs/spec/` là **số liệu chết** — giá trị serialize trong prefab,
> không phải trạng thái của một game đang chạy. File này tách rõ **ba tầng**: số (giá trị), kịch bản
> (thứ tự + thời điểm), và mã (bộ thực thi). Kịch bản là tầng quyết định.
>
> Nguồn: `datas/waves.json` (23.757 `Call_Data`), `Gun_Attack.csv` (458), `Enemy_Movement.csv` (981),
> `Boss_BodyPhysics.csv` (251), `class-inventory.csv` (677 class), `dump.cs`.
> Mức: **A** đo được · **B** suy ra · **C** ước lượng · **D** chưa đọc. Cuối file: **Còn thiếu / phải đoán**.

---

## 0. Bằng chứng "số liệu chết" — nằm ngay trong dữ liệu

Bốn cột này khớp nhau và cùng nói một điều:

| Cột | Giá trị | Nghĩa |
|---|---:|---|
| `15-enemy-hp.csv` · `start_hp` = 0 | **514 / 981** dòng | quá nửa prefab không mang HP |
| `Enemy_Datas.StartHealthPoint` = 0 | **514 / 981** | trùng khít |
| `Enemy_Datas.CurrentHealthPoint` = 0 | **981 / 981** | **không một dòng nào** có máu hiện tại |
| `Enemy_Datas.IsAlive` = False | **979 / 981** | prefab lưu trạng thái "đã chết" |
| Prefab enemy thường có HP > 0 | **2 / 70** (20.000 mỗi cái) | ngoại lệ là vật phụ `W1`/`W2` |

> **Nhận định (mức A):** `CurrentHealthPoint = 0` và `IsAlive = False` trên **toàn bộ** 981 object là dấu
> hiệu không thể nhầm: đây là **giá trị mặc định của prefab**, bị ghi đè lúc chạy. HP thật của 68/70 prefab
> enemy thường **không tồn tại trong file** — nó được tính bằng mã, đúng như `BOSSES.md` §6 đã ghi.
>
> Hệ quả: mọi bảng "HP / damage / DPS" trong bộ spec là **đầu vào của công thức**, không phải kết quả
> của trận đánh. Muốn biết kết quả thì phải có **kịch bản + mã**, không phải thêm số.

---

## 0.5 Kịch bản lần đầu mở game — kiểm bằng class

Luồng vào game dựng được **hoàn toàn từ tên class + field**, không cần chạy:

| Bước | Thành phần | Bằng chứng (mức A) |
|---:|---|---|
| 1 | **Menu** | `ScenesManager.Scene.Menu = 0` — scene đầu trong 5 scene |
| 2 | **Home** | `Home_Loader` có `public static BoardID defaultBoard` — biến static quyết định **board mở đầu** |
| 3 | **Chọn màn** | `Board_Stage` (`BoardID.BoardStage = 6`): `btnPlay`, `btnUpgrade`, `parentModes` |
| 4 | **Chuẩn bị vào trận** | `Board_Begin` (`BoardID.BoardBeginPlay = 22`): `textStage`, `allAbilityNames`, `popupTalents` |
| 5 | **Vào trận** | `GP_Starter`: `player`, `allBgSpr` (đổi nền), `allStartFxParticles`, `startFxAnimator` — đoạn intro ngắn |
| 6 | **Tutorial** | `GP_Tutorials.GameStarted(Action<int> _through)` — **chạy trong gameplay, không phải board riêng** |
| 7 | Người chơi cũ | `SkipTutorial.OnPressedButtonIPlayedBefore()` + `IESignInOrRestoreYourDatas(...)` |

**5 scene:** `Menu 0` · `Home 1` · `Game 2` · `Endgame 3` · `HomeData 4`.
**39 board** (`BoardID` 1–39), trong đó **không có board tutorial nào** — đây là điểm quan trọng:
tutorial không phải một màn hình, nó là **overlay gắn trong scene Game**.

### 0.5.1 Tutorial = 5 bước, chạy đè lên trận đầu

`GP_Tutorials` giữ trạng thái bằng **static** (sống qua các scene):

| Trường | Ý nghĩa |
|---|---|
| `public static bool inTutorial` | đang trong tutorial |
| `public static int MaxIndexTutorial` | tổng số bước |
| `public static int IndexTutorial { get; set; }` | bước đã qua |
| `public static GP_Tutorials instance` | singleton |

**5 object hướng dẫn** (`GameObject` field — mỗi cái là một bước):

| # | Field | Dạy gì | Chuỗi tương ứng |
|---:|---|---|---|
| 1 | `tutobjControl` | kéo ngón tay để lái | `txt_tutorial_controls` = "Move your finger to control the spaceship" |
| 2 | `tutobjChangePlane` | nhấc tay để đổi tàu | `txt_tutorial_change` |
| 3 | `tutobjChangePlane2` | đổi tàu + kích hoạt skill | `txt_tutorial_change2` |
| 4 | `tutobjUseDroneSkill` | skill drone | `txt_tutorial_usedroneskill` |
| 5 | `tutobjTouchSkill` | chạm 2 ngón dùng talent | `txt_tutorial_touchskill` |

Thêm hai bước phụ không có `tutobj`: `StartTutChangeGameSpeedBoss()` (dạy đổi tốc độ game khi gặp boss)
và cụm `OnPaused` / `OnResumeGame` / `OnPressedButtonQuitTutSettings`.
**18 khoá chuỗi** `txt_tutorial_*` trong `12-localization.csv`.

> **Nhận định (mức A):** đúng là **mở game lần đầu thì vào trận luôn** — không có board hướng dẫn,
> không có màn "chọn tên", không có màn khoá. Tutorial là **5 overlay** hiện ngay trong trận đầu,
> và người chơi vẫn đang bắn trong lúc bị dạy.
>
> **Chỗ cần chỉnh:** vẫn có **3 trạm trước trận** — `Home` → `BoardStage` → `BoardBeginPlay`.
> Chúng không dạy gì, nhưng là 3 lần bấm. Với người chơi mới, `Board_Begin` hiện `textStage` +
> `allAbilityNames` + `popupTalents` (chọn talent) — tức **có một bước chọn trước khi vào màn 1**,
> trừ khi `popupTalents` bị ẩn lúc chưa có talent (chưa xác định được, cần thân hàm).

### 0.5.2 Người chơi cũ — đường tắt "I played before"

`SkipTutorial` là một `MonoBehaviour` **riêng**, có `public static bool destroyed` và các field
`popupNoInternet`, `loadingObject`, `btnObject`. Nút của nó gọi
`OnPressedButtonIPlayedBefore()` → `IESignInOrRestoreYourDatas(...)` → `GetGameConfigs()`.

⇒ Đây **không** phải nút "bỏ qua tutorial cho người mới" — đây là **đăng nhập/khôi phục dữ liệu**
cho người đã chơi trên máy khác, và khi restore xong thì tutorial bị đánh dấu đã qua.
Nghĩa là người mới **không có nút bỏ qua** ở bước này.

> **Điều kiện lật ngược:** nếu `Home_Loader.defaultBoard` được gán `BoardHome` cho người mới và
> `BoardStage` cho người đã có tiến trình, thì luồng lần đầu là **Home → Stage → BeginPlay → Game**;
> ngược lại nếu nó gán thẳng `BoardBeginPlay` thì gần như "chơi luôn" đúng nghĩa. Cần đọc `.cctor`
> của `Home_Loader` — hiện chỉ có tên, chưa có thân.

---

## 1. Kịch bản chia 5 lớp — trạng thái đọc

| # | Lớp kịch bản | Trả lời câu hỏi | Class | Instance | Đọc | Dạng |
|---:|---|---|---|---:|---:|---|
| 1 | **Sinh quân** | con nào, ở đâu, bao lâu một con | `Call_Data` | **23.757** | **100%** | timeline |
| 2 | **Bay** | đi đường nào, nhanh bao nhiêu, dừng hay lặp | `Enemy_Movement` | 981 | **100%** | path + speed |
| 3 | **Bắn** | bắn viên gì, bao lâu một viên, mấy băng | `Gun_Attack` | 458 | **100%** | timeline |
| 4a | **Va chạm boss** | đâm vào mất bao nhiêu máu | `Boss_BodyPhysics` | 251 | **100%** | 2 tham số |
| 4b | **Va chạm enemy thường** | đâm vào mất bao nhiêu máu | `Enemy_Physics` | **981** | **0%** | — |
| 5 | **Pha boss** | đổi đòn ở mốc nào, đòn gì | 37 `*_Director` + 3 `AttackPhases` | **68** | **0%** | bảng pha |

**Ba lớp đầu là timeline có tham số thời gian** — đọc được trọn. Đó là lý do khẳng định
"kịch bản đọc được", không chỉ có số.

---

## 2. Kịch bản bắn — giải mã được thành timeline

`Gun_Attack` có 39 cột, trong đó **6 cột là tham số thời gian** và 5 cột là tham số đạn:

```
timeStart          # giây, lúc bắt đầu bắn          → 0,0 – 5,0 · median 1,0
allGunDatas[i].countMags    # số băng              → 1 – 40 · median 3
allGunDatas[i].countShots   # số viên mỗi loạt     → 0 hoặc 3 – 21
allGunDatas[i].timeShot     # giây giữa 2 viên     → 0,05 – 5,0 · median 0,10
allGunDatas[i].timeReload   # giây giữa 2 băng     → 0,05 – 60 · median 0,25
allGunDatas[i].timeRounds   # giây mỗi băng        → 0,3 – 100 · median 2,0
```

Đọc được (mức **B**, suy từ tên trường + giá trị):

- `countShots = 0` (479/516 slot) ⇒ mỗi lần bắn **1 viên**, nhịp là `timeReload`.
- `countShots > 0` (37/516) ⇒ mỗi loạt **`countShots` viên** cách nhau `timeShot`, rồi nghỉ `timeReload`.
- Một `Gun_Attack` có **1 hoặc 3 nòng**: **429** gun 1 nòng · **29** gun 3 nòng (516 slot cấu hình).

**Ví dụ một kịch bản cụ thể** — `Boss-39006/Enemy_Ingame/Body/Than/Gun5/Gun5/Enemy_Ingame`:

| Tham số | Giá trị |
|---|---|
| `gunType` | 2 |
| `bltId` | 80027 |
| `bltDamage` | **450** |
| `bltSpeed` | 4,8 |
| `bltLifetime` | 6,0 s |
| `timeStart` | 0,0 |
| nòng 0 | `countMags 6` · `countShots 0` · `timeReload 0,12` · `timeRounds 0,5` |

⇒ đọc thành lời: *bắn ngay từ đầu trận, 6 băng, mỗi băng 0,5 s, giữa hai viên 0,12 s* — tức khoảng
**4 viên/băng, 24 viên cho cả loạt**, mỗi viên 450 damage bay với tốc độ 4,8.

**102 pattern khác nhau** trên 516 slot. Tám pattern phổ biến nhất:

| `countMags` | `countShots` | `timeShot` | `timeReload` | `timeRounds` | Số lần |
|---:|---:|---:|---:|---:|---:|
| 3 | 0 | 0 | 0,10 | 1,0 | 33 |
| 15 | 0 | 0 | 0,05 | 2,0 | 30 |
| 1 | 0 | 0 | 0,60 | 1,8 | 24 |
| 3 | 0 | 0 | 0,15 | 2,0 | 16 |
| 6 | 0 | 0 | 0,50 | 15,5 | 15 |
| 1 | 0 | 0 | 0 | 10,0 | 12 |
| 0 | 3 | 0,15 | 1,50 | 0 | 12 |
| 0 | 0 | 0 | 0,20 | 0 | 12 |

**42 prefab có súng** (21 boss + 19 enemy thường + 2 object `90048`/`90049`).
Nhiều súng nhất: `Boss-39010` **17** · `Boss-39006` **12** · `Boss-37006` **10** · `Boss-39004` **9** ·
`CD-31016` **7**.

> **Nhận định (mức B):** chỉ **102 pattern** cho toàn bộ 458 khẩu súng — đây là **bộ kịch bản bắn nhỏ**,
> dựng lại được bằng một struct 6 trường + một coroutine. Không cần AI, không cần animation-driven.
>
> **Điều kiện lật ngược:** nếu `countShots`/`timeShot` thực ra do `gunType` quyết định (4 giá trị: 0–3)
> chứ không phải đọc trực tiếp từ trường, thì bảng pattern phải gộp lại theo `gunType` trước.

---

## 3. Kịch bản sinh quân — timeline 3 tham số

Mỗi `Call_Data` là một dòng kịch bản: *spawn loại nào, ở đâu, nhịp bao nhiêu*.

| Tham số | Giá trị (11.093 spawner sau dedupe) |
|---|---|
| `rate` | **1,0** (7.741) · 0,5 (532) · 2,0 (163) · 0,65 (111) |
| `y_spawn` | **9,6** (7.427) · 12,0 (1.701) · 8,0 (284) · 5,0 (218) |
| `radius` | **0,1** — đúng 11.093/11.093, không có ngoại lệ |
| `speed` | 1,5 (4.984) · 5,2 (1.462) · 2,0 (750) · 3,5 (243) |
| `spawn_type` | `point_range` 7.540 · `point` 2.084 · `path` 861 · `boss` 327 · `special` 281 |

⇒ kịch bản mặc định của game: **1 con mỗi 1,0 giây, tại `y = 9,6`, bán kính 0,1**.
`y = 9,6` đúng bằng **nửa chiều cao canvas 19,2** — quân vào từ chính giữa mép trên.

**Kiểm toàn vẹn:** tổng `copies` = **23.757** = số `Call_Data` trong `class-inventory` — **lệch 0**.
Không một dòng kịch bản nào bị mất khi gộp.

---

## 4. Kịch bản bay — 94% dừng lại trong màn

`Enemy_Movement` (981) cho mỗi enemy:

| Tham số | Giá trị |
|---|---|
| `endOfPathInstruction` | **`Stop` = 924 / 981 (94,2%)** · `Loop` = 57 (5,8%) |
| `isTurret` | False 869 · **True 112** |
| `facingMove` | True 949 (96,7%) |
| `fixedAngle` | False 962 · True 19 |
| `listSpeeds[0]` | 1,0 – 20,0 · median 5,0 |

> **Nhận định (mức A):** `Stop` chiếm **94,2%** nghĩa là phần lớn enemy **bay hết đường rồi đứng yên trong màn**,
> không bay vòng, không biến mất. Đây là chi tiết quyết định: nếu để `Loop`, wave sẽ không bao giờ
> "sạch quân"; để `Stop` thì mỗi con đều phải bị xử lý.

---

## 5. Pha boss — lớp kịch bản duy nhất **chưa có gì**

37 class `*_Director` (65 instance) + `Boss19/20/21_AttackPhases` (3) = **68 instance**, **0% đọc**.

Đây là nơi chứa **thứ tự đòn theo pha** — thứ mà số liệu không thể suy ra. Biết một boss có 21 bộ phận
HP (`39017`) và 11 vùng va chạm **không** cho biết nó đổi đòn lúc nào.

| Nhóm | Class | Instance | Nội dung nghi vấn |
|---|---|---:|---|
| Điều phối | `Boss1_Director` … `Boss18_Director` · `Boss_Director` · `Boss4_DirectorLite` | 19 class | thứ tự pha |
| Điều phối mini-boss | `MB2_Director` … `MB19_Director` · `MB6_ChildDirector` | 17 class | pha mini-boss |
| Bảng pha | `Boss19_AttackPhases` · `Boss20_AttackPhases` · `Boss21_AttackPhases` | 3 | bảng pha tường minh |
| Đòn đặc biệt | `Boss3_Plasma` 75 · `Boss_PlasmaBeam` 68 · `BossLaser` 16 · `Boss_Rocket` 12 · `Boss8_Spawner` 12 · `Boss6_Sword` 8 · `Boss3_Flamer` 6 | 197 | đòn riêng từng boss |
| Animation event | `Boss4_AnimationEvents` 5 · `Boss5_…` 3 · `Boss6_…` 3 · `Boss7_…` 3 · `Boss10_…` 3 · `Boss11_…` 3 · `Boss12_…` 5 · `Boss15_…` 3 · `Boss17_…` 3 · `Boss18_…` 5 · `Boss9_AnimationEvents` 7 | 43 | **mốc bật đòn theo animation** |

> **Nhận định (mức A):** 5/39 boss (`37011`, `37015`, `37017`, `39001`, `39007` — 6,7% HP boss) **không có
> súng và không có vùng va chạm**. Với 5 con này, **100% kịch bản đòn đánh** nằm trong nhóm
> Director/AnimationEvents — tức toàn bộ nằm ở lớp chưa đọc.

---

## 6. Ba tầng, và tầng nào còn thiếu

| Tầng | Trả lời | Trạng thái |
|---|---|---|
| **Số** (giá trị) | bao nhiêu máu, damage bao nhiêu | ✅ đọc được — nhưng là **giá trị chết** |
| **Kịch bản** (thứ tự) | khi nào spawn, bắn, đổi pha | ⚠ **3/5 lớp đủ** · va chạm enemy thường và pha boss **chưa** |
| **Mã** (thực thi) | công thức HP theo stage, điều kiện qua màn | ❌ **method body chưa có** |

Cái quyết định "game chạy đúng" là **tầng kịch bản + tầng mã**, không phải tầng số. Và đó chính là hai
tầng còn thiếu.

> **Ví dụ cho thấy số không thay được kịch bản:** `Boss-39010` có **17 khẩu súng** và 22 bộ phận HP.
> Biết cả 17 khẩu bắn 450 damage vẫn **không** dựng lại được con boss này, vì không biết **khẩu nào bắn
> ở pha nào**. Cùng dữ liệu đó, nếu đọc được `Boss10_Director` (2 instance) thì dựng được gần như trọn.

---

## 7. Còn thiếu / phải đoán

| # | Thứ | Mức | Cách lấy |
|---:|---|---|---|
| 1 | **Bảng pha** 37 `*_Director` + 3 `AttackPhases` | **D** | thêm vào `TARGETS` của `unity_data.py` — 68 instance, cùng đường 8 class đã đọc |
| 2 | **Damage va chạm enemy thường** (`Enemy_Physics` 981) | **D** | cùng cách; mở khoá 85,8% entry |
| 3 | **Công thức HP theo stage** (`Enemy_Health.Init`) | **D** | method body IL2CPP — `dump.cs` chỉ có RVA, chưa có thân |
| 4 | **Điều kiện qua màn** (`Wave.CheckSpawnEnded`) | **B** | method body; hiện chỉ biết tên hàm |
| 5 | Ý nghĩa chính xác `gunType` (0–3) | **C** | chưa thấy enum tương ứng trong `07-enums.md` |
| 6 | `rate` là giây hay hệ số | **C** | 1,0 chiếm 70%; nếu là giây thì 1 con/giây |
| 7 | `countShots = 0` nghĩa là 1 viên hay "không giới hạn" | **B** | suy từ 479/516 slot; cần xác nhận bằng mã |
| 8 | `Home_Loader.defaultBoard` cho người chơi mới | **C** | static, gán trong `.cctor`; chưa có thân hàm |
| 9 | Tutorial có **chặn** gameplay hay chỉ đè lên | **C** | `inTutorial` static + `GameStarted(Action<int>)`; cần thân hàm |
| 10 | `popupTalents` có hiện ở màn 1 khi chưa có talent | **C** | `Board_Begin.popupTalents`; phụ thuộc dữ liệu người chơi |

> Không có mục nào ở đây là "không thể". #1 và #2 là **chưa thêm tên class vào danh sách đọc**
> (cùng một lệnh đã đọc được 8 class khác), #3–#4 cần **method body**, #5–#7 là **chưa chốt cách đọc**.
