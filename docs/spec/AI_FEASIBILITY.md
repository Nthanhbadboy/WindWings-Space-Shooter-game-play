# AI_FEASIBILITY — AI dựng lại game từ bộ spec này được đến đâu?

> Tài liệu **đánh giá**, không phải spec kỹ thuật. Nguồn gồm:
> (a) nghiên cứu công bố 2025–2026 về việc LLM sinh game từ đặc tả,
> (b) số đo thực tế trong chính repo này (`docs/spec/*.md`).
> Mỗi khẳng định có nguồn; suy luận của tôi đánh dấu `> Nhận định:`.

---

## 0. TL;DR

**Dựng lại được "hệ thống", không dựng lại được "cảm giác" — và nghiên cứu công bố
định lượng đúng khoảng cách đó.**

| Câu hỏi | Trả lời ngắn |
|---|---|
| AI viết ra game **chạy được**? | ✅ Gần như chắc chắn — tỉ lệ pass syntax/dependency/event lên tới **99,2%** |
| Game đó **đúng đặc tả**? | ⚠️ **Không** — điểm "Rule & Mechanism Modeling" chỉ **45,6/100**, "Goal & Termination" **44,0** |
| Game đó **chơi thấy hay**? | ❌ Điểm "Dynamic Feedback Fidelity" chỉ **32,1/100** — đúng chỗ "game feel" nằm |
| Bao lâu thì ra sản phẩm? | Phụ thuộc art/audio/test — spec không rút ngắn được 3 phần này |
| Rủi ro pháp lý | Thấp nếu đổi art/tên; **cao** nếu dùng lại asset hoặc tên boss |

---

## 1. Nghiên cứu công bố nói gì (2025–2026)

### 1.1 `Spec2Game` — 14 LLM, 3.330 dự án game

Benchmark yêu cầu LLM sinh **cả một game Pygame** từ đặc tả chi tiết, chấm 4 chiều.
Kết quả chính [1](https://arxiv.org/html/2610.04253v1):

| Chiều | Điểm trung bình | Nghĩa |
|---|---:|---|
| D1 — Executability (chạy được) | **gần bão hoà** (syntax 99,2% · dependency 99,2% · event 99,2% · window 92,4%) | AI viết code chạy được rất tốt |
| D2 — *Game Element Modeling* | **80,8** | tạo được vật thể, sprite, HUD |
| D2 — *Interaction Modeling* | 63,8 | |
| D2 — *Dynamic Evolution* | 65,8 | |
| **D2 — Rule & Mechanism Modeling** | **45,6** | **luật chơi bị làm sai** |
| **D2 — Goal & Termination Modeling** | **44,0** | **điều kiện thắng/thua bị làm sai** |
| D4 — Visual Presentation | 70,4 | |
| **D4 — Dynamic Feedback Fidelity** | **32,1** | **phản hồi khi chơi (hit/hurt/juice) sai** |
| D4 — Visual Actionability | 40,7 | |

Chi tiết đáng chú ý: trong **630 dự án**, **387 pass đủ 6 kiểm tra "chạy được"**, nhưng
**87 trong số đó vẫn có điểm đặc tả < 60** — tức *chạy ngon mà vẫn sai luật* [1](https://arxiv.org/html/2610.04253v1).

### 1.2 `A2Z GameSpec-Bench` — 100 game của coding agent

Chấm mức "trung thành với GDD" [2](https://arxiv.org/html/2609.39564v1):

| Chỉ số | Giá trị |
|---|---:|
| GDD Fidelity — game nhỏ | **71,1** |
| GDD Fidelity — game lớn | **51,1** |
| "Verifiable rate" (chạy + kiểm được) | 93,9% / 94,2% |
| Rule pass **cục bộ** | 72,4% |
| Rule pass **sau khi tính phụ thuộc** (rule trước phải đúng) | **22,7%** |

⇒ Một luật đơn lẻ thì AI làm đúng 72% số lần; nhưng **cả chuỗi luật phụ thuộc nhau** thì chỉ
**22,7%** — giảm **49,7 điểm** [2](https://arxiv.org/html/2609.39564v1). Đây chính là hình
dạng của một game: HP → damage → chết → drop → nâng cấp → cân bằng.

### 1.3 Dịch ngược bằng LLM

`DecompileBench` (2025, 23.400 hàm / 130 chương trình): code do LLM dịch ngược **dễ đọc hơn**
nhưng **kém đúng chức năng hơn** công cụ truyền thống [3](https://sherafy.com/ai-game-cloning-copyright-law/).
Các dự án port lại game (Mario 64 DS…) báo "99,9% hàm khớp" nhưng chỉ **~31%** chuyển được
thành mã nguồn **đọc được** [3](https://sherafy.com/ai-game-cloning-copyright-law/).

### 1.4 Sinh game bằng video (GameNGen, Muse)

- GameNGen (2024) tạo "DOOM chơi được" **không cần engine**, nhưng **càng chơi lâu càng
  "mơ"** ra chi tiết không có trong game gốc [4](https://www.theguardian.com/games/2025/mar/10/are-ai-generated-video-games-microsoft-muse-google-gamengen).
- Microsoft Muse cần **~500.000 phiên chơi (~100.000 giờ)** mới ổn định, và **chỉ đúng trong
  phạm vi đã ghi** [4](https://www.theguardian.com/games/2025/mar/10/are-ai-generated-video-games-microsoft-muse-google-gamengen).
- Kết luận của Guardian: **chưa tạo ra game mới**, chỉ tái tạo clip giống gameplay [4](https://www.theguardian.com/games/2025/mar/10/are-ai-generated-video-games-microsoft-muse-google-gamengen).

### 1.5 Thực tế ngoài thị trường

- Axios (8/2026): *"model hiện tại thực chất chỉ tạo được **bản remake của game đã có**"*, vì
  dựa trên dữ liệu quá khứ; làm ra thứ **mới** cần rất nhiều lượt prompt đắt đỏ [5](https://www.axios.com/2026/08/10/ai-cod-call-of-duty-claude-opus-prompts).
- Polygon (10/2026): các bản clone do AI dịch ngược *"phần lớn **không phải build ổn định**,
  có thể **không chơi được**"* [6](https://www.polygon.com/revamp-playtest-limited-ai-cloning-fears/).
- 404 Media: AI làm việc clone game **dễ hơn bao giờ hết**, số lượng tăng vọt [7](https://www.404media.co/ai-made-cloning-games-easier-than-ever/).
- Ngược lại, một nghiên cứu 2026 cho thấy game do AI thiết kế được người chơi đánh giá
  **vui/hay hơn** game của amateur và cả professional ở nhóm game đơn giản [8](https://arxiv.org/html/2610.18921v1) —
  nhưng thí nghiệm đó **không cho AI test hay tinh chỉnh**, tức chưa phải "làm game thương mại".

---

## 2. Đối chiếu với bộ spec này

### 2.1 Ba chỉ số nghiên cứu ↔ ba lỗ hổng của repo

| Chỉ số nghiên cứu | Điểm | Ứng với lỗ hổng nào trong repo | Trạng thái |
|---|---:|---|---|
| **Rule & Mechanism** 45,6 | thấp | 8 class config **không serialize**: `Player_Get_Datas`, `Enemy_Data_Balance`, `Stage_Get_Datas`, `Map_Get_Datas`, `Tech_Datas`, `Droid_Data_Balance`, `Device_Get_Data`, `GameDatas` | ❌ phải tự định nghĩa |
| **Goal & Termination** 44,0 | thấp | 45.659 entry `enemies` = `"?"` ⇒ **không biết wave nào có enemy nào** | ❌ phải tự thiết kế |
| **Dynamic Feedback Fidelity** 32,1 | thấp nhất | feel: gia tốc, hitstop, shake, flash — nằm trong `libil2cpp.so` | ❌ không có số |

Ba lỗ hổng của repo **trùng khít** ba điểm thấp nhất trong nghiên cứu. Đây không phải trùng
hợp: đó là **cùng một giới hạn** — *đặc tả tĩnh không chuyển được thành hành vi động*.

### 2.2 Cái mới bóc được ở vòng này (thu hẹp lỗ hổng)

| Mảng | Trước | Sau (vòng bổ sung) | Nguồn |
|---|---|---|---|
| Tốc độ enemy | 0 | **0,2–30, median 5,0** | `ENEMY_BEHAVIOUR.md` §1.1 |
| Turret / fixed-angle | 0 | **95 turret · 13 fixed-angle** | §1.3 |
| Bán kính va chạm | chỉ đạn | **15 unit cho 799/800 enemy** | §1.3 |
| Biên vùng chơi | 0 | **20 × 25 unit** | §1.4 |
| Số anchor đường bay | 0 | **399 path, 16 độ dài** | §2 |
| Thiên thạch | 0 | **517 generator, 2–5 s, X −7…5** | §4 |
| Nhịp nổ boss | 0 | **0,5–6,8 s, 3 `idFx`** | §5 |
| Kiến trúc 1 enemy | 0 | **9 component** | §6 |

### 2.3 Cái vẫn **không** bóc được (đã kiểm, không phải bỏ sót)

| Hạng mục | Bằng chứng "không có" |
|---|---|
| Toạ độ đường bay | `PathCreator.csv`: 30 cột `editorData` nhưng **0 cột `points[i].x/y`** |
| Tham số spawner | 6/7 file `*_Spawner.csv` có **0 cột dữ liệu** |
| Damage/HP của player | `forceType = Enemy` **458/458**; `Player_Get_Datas` không serialize |
| Giá / tỉ lệ rơi | `Box_Rewards.id = 0` **800/800**; không cột `weight`/`price` |
| Hiệu ứng item | `Sub_Item.csv` **0 cột hiệu ứng** |
| Âm thanh | 69 `AudioClip` nhưng **0 file export được** (FSB5 trong `.resS`) |
| Hành vi (appear/burn/stun/destroy) | `Enemy_Appear.csv` chỉ có ref |

---

## 3. Ước lượng độ phủ sau vòng bổ sung

| File | Phủ | Còn thiếu để "viết được game" |
|---|---:|---|
| `UI.md` | ~85% | animation chuyển board |
| `GAMEPLAY.md` | ~75% | feel, đường cong tiến trình |
| `COMBAT.md` | ~72% | toàn bộ phía player |
| `ENEMY_BEHAVIOUR.md` (mới) | **~70%** | hình học path, tham số spawner |
| `ENCOUNTERS.md` | ~62% | nội dung enemy trong wave |
| `BALANCE.md` | ~55% | hệ số nâng cấp theo cấp |
| `ASSETS.md` | ~50% | asset dùng được (chỉ có inventory) |
| `ECONOMY.md` | ~40% | **mọi con số kinh tế** |

> `> Nhận định:` các % này là **tự đánh giá**, không phải số đo. Cách đo khách quan hơn:
> đếm số bảng có số thật / tổng số bảng cần cho một bản clone (khoảng **60–65%**).

---

## 4. Vì sao "AI clone được" vẫn đúng — nhưng có điều kiện

**Đúng:** AI viết được **khung** game này nhanh hơn con người nhiều lần, vì:
- 125 class UI + screen graph → sinh được toàn bộ scene/prefab
- 458 cấu hình súng + burst 5 tham số → weapon system data-driven
- 282 wave + 10.498 spawner → level generator có tham số
- 800 enemy × 9 component → enemy framework đúng kiến trúc gốc

**Điều kiện:** phải **thay 3 thứ** mà spec không cho:
1. **Enemy roster** — tự thiết kế bộ enemy (vì wave toàn `"?"`).
2. **Đường cong cân bằng** — tự chọn DPS player, HP player, giá, tỉ lệ rơi.
3. **Feel** — tự tinh chỉnh bằng playtest (nghiên cứu gọi là *Dynamic Feedback Fidelity*).

Không làm 3 việc đó thì kết quả đúng như Polygon mô tả: **build không ổn định, chơi không
được** [6](https://www.polygon.com/revamp-playtest-limited-ai-cloning-fears/) — dù code compile sạch.

---

## 5. Cách giảm rủi ro (đề xuất, không phải số của game)

| Rủi ro | Cách chặn |
|---|---|
| AI làm sai luật (Rule 45,6) | Viết **test theo luật**, không theo hàm: "bắn 3 phát vào enemy 900 HP phải còn sống" |
| Sai chuỗi phụ thuộc (22,7%) | **Golden test**: replay 1 wave, so số enemy chết/giây với spec |
| Feel sai (32,1) | Playtest sớm 2 tuần/lần; chỉnh **hằng số**, không chỉnh code |
| Cân bằng lệch | Dùng `COMBAT.md` §4 (DPS 2 đỉnh) + `BALANCE.md` §2 (HP) làm **baseline**, không phải đích |
| Pháp lý | Đổi art/tên/âm thanh (xem `ASSETS.md` §8); **không** dùng `sactx-*`, Spine, audio gốc |

---

## 6. Kết luận

1. **AI dựng được game chạy được từ bộ spec này** — tỉ lệ thành công phần "code" rất cao.
2. **AI sẽ làm sai luật và sai feel** nếu chỉ có spec — có số liệu công bố xác nhận
   (45,6 và 32,1 trên 100).
3. **Khoảng trống lớn nhất không phải code, mà là**: enemy roster, cân bằng, feel, art/audio.
4. Bộ spec này có giá trị nhất ở chỗ **biến 6 tháng nghiên cứu thành 0**, và **cho một
   baseline số để test**, không phải một bản thiết kế thi hành được.

> `> Nhận định:` với một đội 3–5 người, bộ spec này rút ngắn **giai đoạn nghiên cứu** (~15–20%
> tổng công) xuống gần 0, nhưng **không** rút ngắn giai đoạn sản xuất art/audio/test.

---

## 7. Nguồn

| # | Nguồn | Dùng cho |
|---:|---|---|
| 1 | Spec2Game, arXiv 2610.04253 | bảng điểm D1–D4, 14 LLM / 3.330 dự án |
| 2 | A2Z GameSpec-Bench, arXiv 2609.39564 | GDD fidelity 71,1/51,1; rule pass 72,4% → 22,7% |
| 3 | sherafy.com — AI game cloning & DecompileBench | 99,9% hàm khớp / 31% đọc được |
| 4 | The Guardian (3/2025) — GameNGen & Muse | drift khi chơi lâu, 100.000 giờ dữ liệu |
| 5 | Axios (8/2026) | "chỉ remake được game đã có" |
| 6 | Polygon (10/2026) | clone AI "không phải build ổn định" |
| 7 | 404 Media (7/2026) | clone game tăng vọt nhờ AI |
| 8 | arXiv 2610.18921 | phản biện: game do AI thiết kế được đánh giá tốt hơn |

Số liệu nội bộ: `ENEMY_BEHAVIOUR.md`, `COMBAT.md`, `ENCOUNTERS.md`, `BALANCE.md`, `ECONOMY.md`,
`ASSETS.md` (cùng thư mục).

---

## 8. Còn thiếu / phải đoán

| # | Điều | Trạng thái |
|---:|---|---|
| 1 | % phủ chính xác của bộ spec | **D** — chỉ là tự đánh giá; muốn đo phải thử sinh 1 bản MVP rồi chấm |
| 2 | Thời gian thực tế để AI sinh MVP | **D** — phụ thuộc model + scope, chưa có thử nghiệm |
| 3 | Chi phí art/audio thay thế | **D** — `ASSETS.md` §7 chỉ có ước lượng |
| 4 | Chất lượng "feel" đo được | **D** — cần playtest, không có trong APK |
| 5 | Ảnh hưởng pháp lý theo từng quốc gia | **D** — cần luật sư, tài liệu này không thay được |
