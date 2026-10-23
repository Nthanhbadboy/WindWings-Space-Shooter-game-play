# EXTERNAL_REFS — có ai **phân tích ngược** game này chưa?

> **Trả lời ngắn: CHƯA. Không có một bản phân tích ngược công khai nào của *WindWings: Space Shooter*.**
> Không có `dump.cs`, không có metadata, không có spreadsheet chỉ số, không có wiki riêng, không có
> datamine của cộng đồng. Cái duy nhất tồn tại là **~30 trang phát hành APK mod** (chỉ vá tiền/god mode)
> và **2 repo GitHub quét manifest tự động** — không cái nào chạm vào logic game.

Việc này có một hệ quả quan trọng, ghi ở §5: **mọi con số trong bộ SPEC này không thể đối chiếu chéo
với nguồn ngoài** ⇒ phải tự kiểm nội bộ (`ASM_INTEGRITY`, `VERIFY_ROUND1`).

---

## 0. Sáu loại nguồn tìm được — và mức dùng được

| # | Loại nguồn | Có phân tích ngược? | Dùng được gì |
|---:|---|---|---|
| 1 | **2 repo GitHub** (`beerphilipp/taptrap`, `beerphilipp/tabbed-out`) | **Không** — quét `AndroidManifest` tự động | `target_sdk`, **77 activity**, SDK nhúng, **3 package name** của cùng họ |
| 2 | **~30 trang mod APK** (apkmody, liteapks, happymod, sbenny, platinmods, modyolo, 24hmod, iOSGods…) | **Không** — chỉ vá bộ nhớ | **Danh sách tính năng mod = bản đồ "cái gì ở client"** (§3) |
| 3 | **r/Windwingsgame** (Reddit) | **Không** — mẹo chơi, từ 2021, rất nhỏ | Vài mốc tiến trình của người chơi (§6) |
| 4 | **YouTube** "All Bosses" | **Không** — video | Tên boss theo người chơi (khác id nội bộ) |
| 5 | **Wiki Galaxy Attack: Alien Shooter** | Có — nhưng **GAME KHÁC** | **Chỉ** làm tham chiếu thể loại (§4). **Không** được trích số cho WindWings |
| 6 | **AppBrain · APKPure · softonic · Play Store** | Không | Lịch sử phiên bản, số lượt tải, mô tả chính thức |

**Kết luận:** repo này là **nguồn duy nhất** có số đo của game.

---

## 1. Phép tìm đã chạy — để bạn biết phạm vi (và tin được "chưa có")

| Truy vấn | Kết quả | Có ích? |
|---|---|---|
| `gh search repos windwings` (30 repo) | toàn repo gõ sai "Windows" + repo của chính dự án | **0** |
| `gh api search/code "com.Wind.wings.Space.Shooter"` — **19 repo** | 2 repo quét APK; còn lại là danh sách chặn/tracker/permission | **2** (§2) |
| `gh api search/code "windwings il2cpp"` | **0 kết quả** | — |
| `gh api search/code "windwings"` — **256** | 4 file quét APK + README của chính repo này | **2** |
| web: `"WindWings" github reverse engineering il2cpp` | chỉ ra repo của chính dự án | **0** |
| web: `"com.wind.wings.Space.Shooter" apk mod` | **30 trang mod** | metadata |
| web: `apk decompile il2cpp dump.cs metadata` + WindWings | không có bản dump nào | **0** |
| web: `sprites ripped assets soundtrack` | không có asset rip công khai | **0** |
| Reddit `fetch_page` | **HTTP 403** (Reddit chặn) ⇒ chỉ đọc được qua snippet tìm kiếm | hạn chế |

---

## 2. Hai repo GitHub thật — chứa gì, đo được gì

| Repo | File | Nội dung | Dùng được |
|---|---|---|---|
| `beerphilipp/taptrap` | `vulnerable_app_detection/results/2025-05-20/output/com.Wind.wings.Space.Shooter.json` | quét activity/**exported**/intent-filter (lỗ hổng tap-jacking) | `target_sdk 34` · **77 activity** · launcher = **`com.google.firebase.MessagingUnityPlayerActivity`** |
| `beerphilipp/tabbed-out` | `analysis/results/com.Wind.wings.Space.Shooter.res.json` | quét **Custom Tabs** + lớp `com.google.android.gms.ads.internal.*` | xác nhận **AdMob** có mặt |

### Ba package cùng một họ — `taptrap` quét cả ba

| Package | `target_sdk` | Số activity | Activity khởi động |
|---|---:|---:|---|
| **`com.Wind.wings.Space.Shooter`** ← bản đang phân tích | 34 | **77** | `…firebase.MessagingUnityPlayerActivity` |
| `com.Gcenter.WindWings.Galaxy.Attack.SHMUP` | 34 | **23** | `…firebase.MessagingUnityPlayerActivity` |
| `com.Windwings.Space.Shooter.SHMUP.Multiverse` (bản **Multiverse**) | 34 | **77** | **`com.unity3d.player.UnityPlayerActivity`** |

**Đọc ra được 3 điều:**

1. **`target_sdk 34`** (Android 14) ⇒ bản 1.3.118 là build mới, không phải bản cũ đóng băng.
2. **77 activity** — cùng con số với bản Multiverse, khác bản `Galaxy.Attack.SHMUP` (23). Hai bản 77 dùng
   chung bộ SDK.
3. **Multiverse không lấy Firebase làm activity khởi động** ⇒ bản sequel **bỏ** đường khởi động qua FCM.
   Đây là khác biệt **kiến trúc**, không phải khác biệt art.

> ⚠️ Cả hai repo là **quét tự động trên APK tải về**, **không** phải phân tích logic. Không có file nào
> trong đó nói về gameplay, HP, wave hay độ khó.

---

## 3. Danh sách tính năng mod = **bản đồ "cái gì nằm ở client"**

Đây là suy ra **hợp lệ** từ 30 trang mod: modder chỉ sửa được thứ **nằm trong máy**. Cái gì mod được
⇒ **server không giữ quyền quyết định**.

| Tính năng mod xuất hiện ở nhiều trang | Nói lên điều gì |
|---|---|
| **Unlimited Gold / Gems / Energy** | tiền tệ + năng lượng **tính ở client** |
| **God Mode** | HP người chơi **client** |
| **One Hit Kill** | **HP enemy ở client** — ủng hộ kết luận `ENEMY_HP_RUNTIME`: HP nằm trong `Enemy_Get_Datas`, đọc lúc chạy |
| **Damage Multiplier** (WindWings **2**) | damage **client**; bản 2 dùng **hệ số** chứ không phải hằng số |
| **High Gold Attraction** (bật **trước khi vào màn**) | **rơi vàng được quyết định lúc bắt đầu màn**, không phải lúc rơi |
| **Pro / Premium purchased**, **Ads removed** | kiểm tra IAP **client-side** |

⇒ **Bản clone làm offline hoàn toàn là đúng hướng**: không có giá trị cân bằng nào bị server khoá.
(Bản gốc vẫn có server cho Arena/PvP/Rank — xem `GAMEPLAY`.)

> **Không** tải, không lưu, không phát hành APK mod. Chỉ đọc **danh sách tính năng** trên trang mô tả.

---

## 4. ⚠️ Cái **KHÔNG** phải game này — đừng lẫn

Có hai wiki rất chi tiết về **một game khác** trong cùng thể loại:

| Wiki | Game thật | Vì sao dễ lẫn |
|---|---|---|
| `galaxy-attack-alien-shooter.fandom.com` | **Galaxy Attack: Alien Shooter** (OnSpace/ABI) | WindWings bị gọi là "Galaxy Attack" trên chính Play Store; **tên gần giống nhau** |
| `alienshooter.org` | cùng game trên | cùng lý do |

Chúng có số rất hấp dẫn — **50 boss**, boss mỗi **4 level**, world boss **15 tỷ / 20 tỷ HP**, 27 loại
"Wings" — **nhưng đó là game khác**. **Tuyệt đối không** trích vào SPEC của WindWings.

| Dùng được | Không dùng được |
|---|---|
| **Chuẩn thể loại**: boss xuất hiện theo chu kỳ, world boss HP cực lớn, "wings" là lớp tăng sức mạnh | **Bất kỳ con số nào** — kể cả số boss, chu kỳ, HP |

> Đây đúng là cái bẫy "ảo tưởng": hai game cùng thể loại, cùng tên gọi trên store, cùng art hướng
> không gian. Số của chúng **không** phải số của WindWings.

---

## 5. Hệ quả: **không có nguồn ngoài để đối chiếu** — nghĩa là gì

| Hệ quả | Việc phải làm (đã làm) |
|---|---|
| Không ai kiểm chéo số của mình | **Validator nội bộ** sau mỗi lần sửa bảng (đếm **số dấu ngăn cột** từng hàng, đo lại cột README) |
| Không có "bản công bố" để so | `ASM_INTEGRITY` — **gác cổng asm** (3 cờ tự kiểm, baseline 17 class) |
| Không có ai chỉ ra mình sai | `VERIFY_ROUND1` — tự kiểm chéo 6 phán quyết của nhánh dữ liệu, và **đã bắt được 2 sai** |
| Dễ trích số của game khác | Cảnh báo §4 ghi thành tài liệu, không chỉ nói miệng |

**Điều này cũng là tin tốt:** nếu ai muốn số của game này, **repo này là chỗ duy nhất**. Giá trị của bộ
SPEC không nằm ở chỗ "khớp nguồn ngoài" mà ở chỗ **mỗi số có đường truy vết** tới CSV/asm.

---

## 6. Ba thứ dùng được **ngay** từ nguồn ngoài

### 6.1 Lịch sử phiên bản (để biết mình đang ở đâu)

| Bản | Ghi nhận từ nguồn ngoài | Ghi chú |
|---|---|---|
| **1.3.118** | bản **mới nhất** trên các trang mod (24hmod, modyolo) — **trùng bản đang phân tích** | ✅ SPEC đang đúng bản |
| 1.3.116 · 1.3.115 · 1.3.114 | nhiều trang, kèm `versionCode` (1.3.114 → **307**) | nếu cần so hành vi cũ |
| 1.3.108 · 1.3.106 · 1.3.99 · 1.3.93 · 1.3.79 · 1.2.48 | trang cũ hơn | — |
| **1.0.x** | package **khác**: `com.GCenter.WindWings.SpaceShooter`, kèm **premium** `com.Gcenter.WindWings.SpaceShooter.Premium` | giải thích vì sao có nhiều package name |

### 6.2 Bản **sequel** — tham chiếu thiết kế (không dùng asset)

| Game | Package | Đáng chú ý |
|---|---|---|
| **WindWings 2: Galaxy Revenge** | — | mod có **"Damage Multiplier"** ⇒ bản 2 chuyển sang **hệ số nhân damage** |
| **WindWings: Multiverse Shooter** | `com.Windwings.Space.Shooter.SHMUP.Multiverse` | 77 activity, launcher **Unity thuần** |

### 6.3 Một nhận xét người chơi **khớp** với phát hiện của mình

Review trên Play Store (bản Premium) viết: *"**No 'global' game difficulty** — need to **repeat levels of
increasing difficulty to get stars** to progress."*

Đối chiếu: `GetKillPercentMissionComplete(mode)` + `SetStarStageMaster(stageIndex, modeIndex, stars)` ⇒
sao lưu **theo từng (stage, mode)** ⇒ muốn 3 sao **phải chơi lại cùng stage ở chế độ cao hơn**.
Đây là **xác nhận độc lập** cho `MISSIONS_STARS`, và nó nói bằng ngôn ngữ người chơi — không phải asm.

---

## 7. Còn thiếu / phải đoán

- **Chưa** tìm được bất kỳ ai đã dump `global-metadata.dat` / `dump.cs` của game này ⇒ nếu có, sẽ trả lời
  dứt điểm `kHp[mode]` và `pct[mode]` (2 ẩn số còn lại).
- **Chưa** kiểm được repo `beerphilipp/*` có phiên bản mới hơn 2025-05-20 không (file cố định).
- **Chưa** đọc trực tiếp `r/Windwingsgame` (Reddit trả **403**). Snippet cho thấy subreddit **nhỏ**
  (vài chục bài, 2021) và **không** có datamine — nhưng đây là suy luận từ snippet, **mức C**.
- **Không** xác minh được bản iOS (App Store `id1498160180`, bundle `com.Wind.wings.Space.Shooter`) có
  khác build Android về gameplay hay không. Có tồn tại bản iOS và modder iOS đã đụng vào nó (iOSGods)
  ⇒ **có thể** là nguồn đối chiếu nếu cần, nhưng **ngoài phạm vi** hiện tại.
- **Chưa** có ai làm wiki riêng cho game này. Nếu cộng đồng lập, đó sẽ là nơi đối chiếu số **đầu tiên**.
- **Không** kết luận "game không có ai quan tâm": 79,8K review trên Play Store và **5.000.000+** lượt tải
  ⇒ đông người chơi, nhưng **không ai datamine**. Hai chuyện khác nhau.
