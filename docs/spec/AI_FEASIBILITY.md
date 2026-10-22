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
| **Cập nhật 10/2026** | Dịch ngược đã **rẻ đi hàng chục lần** (Opus 5.5: < 30 phút/game). Rào cản chuyển từ **kỹ thuật** sang **pháp lý + chất lượng** (§1.6) |
| **Đây là game gì?** | **2.5D sprite + physics 2D** — cả game có **2 mesh**, không có `SkinnedMeshRenderer`, `MeshCollider`; chỉ **7** `BoxCollider` 3D so với **5.424** `BoxCollider2D` (§1.8) |
| **Clone dễ không?** | **Cơ chế: dễ** — thiếu cả 3 thứ khó nhất: **3D, netcode realtime, AI dò đường** (Photon/Mirror/NGO = **0**) (§1.9). Nhưng clone cơ chế chỉ là **~15–20%** công việc |
| Rủi ro pháp lý | Thấp nếu đổi art/tên; **cao** nếu dùng lại asset hoặc tên boss |

### 0.1 Ba mức "dịch ngược đầy đủ" — và mức nào cho ra cái gì

Chữ *"đầy đủ"* quyết định toàn bộ câu trả lời. Cần phân biệt **3 mức**:

| Mức | Có gì | AI làm được gì | Hiện trạng repo này |
|---|---|---|---|
| **A. Đủ dữ liệu** (data-complete) | `*.csv` ScriptableObject + `waves.json` + text/assets đã bóc | Dựng **khung chạy được**, đúng 60–70% hệ thống; **sai luật** (45,6) và **sai feel** (32,1) | ✅ **đang ở đây** |
| **B. Đủ logic** (code-complete) | + `libil2cpp.so` decompile ra **thân hàm** (không chỉ chữ ký) ⇒ có hằng số feel, công thức, state machine | Tái tạo **hành vi** gần 1:1; hết mơ hồ về luật | 🟡 `dump.cs` có **64.727 RVA** nhưng chưa có method body — **lấy được**, xem §1.7 |
| **C. Đủ để ship** (product-complete) | B + asset gốc + cấu hình server (giá IAP, Firebase) | Port được **bản sao 1:1** | ❌ và **không được phép** dùng (bản quyền) |

> **Nhận định:** câu *"AI clone được không"* có **hai đáp án khác nhau** tuỳ mức:
> - Ở mức **A** (hiện tại): **không clone được**, chỉ **bắt chước được** — và đó lại là mục tiêu hợp pháp.
> - Ở mức **B/C**: **clone được về kỹ thuật**, nhưng lúc đó nó là **bản sao vi phạm bản quyền**,
>   không còn là "game khác bắt chước".
>
> Mức B vẫn cần `libil2cpp.so` (arm64) + Il2CppDumper + Ghidra/IDA để có **thân hàm** — `dump.cs`
> 18,8 MB chỉ chứa khai báo. **Nhưng từ 9–10/2026 chi phí mức B đã giảm mạnh** (xem §1.6a):
> AI agent làm được việc này trong **vài giờ đến vài ngày**, không còn là "nhiều tháng".
> `DecompileBench` vẫn đúng ở chỗ code dịch ngược **dễ đọc nhưng có thể sai chức năng** — nên
> mức B **không** phải "bấm nút là xong", nhưng đã **rẻ hơn mức A về công sức thu thập số**.

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

### 1.6 Cập nhật 2026 — mọi thứ đã đổi trong 9 tháng

Từ đầu 2026 đến nay, **hai đường cong đi ngược chiều nhau**:

#### (a) Dịch ngược đã rẻ đi hàng chục lần

| Mốc | Thời điểm | Ý nghĩa |
|---|---|---|
| `decomp.dev` **đóng cửa** | 15/10/2026 | cộng đồng decompile thủ công "bị AI phá vỡ"; không còn phân biệt dự án người hay AI [9](https://www.404media.co/video-game-reverse-engineering-community-shuts-down-because-ai-has-made-it-too-easy/) |
| Claude Opus 5.5 decompile game Steam → chạy trong Unity | 10/2026 | **< 30 phút**, ra C# đầy đủ [10](https://x.com/AIWarper/status/2109060856466264566) |
| `Reverse Engineer Anything` | 20/10/2026 | **342.000 sao** GitHub — nối AI agent vào decompiler chuyên nghiệp [11](https://aiweekly.co/alerts/reverse-engineer-anything-hits-342000-stars-as-cloning-spreads) |
| Decompile *Snowboard Kids* (N64) | 12/10/2026 | **84 ngày** bằng AI agent, so với **596 ngày** làm tay cho bản trước [12](https://www.reddit.com/r/gamedev/comments/1x3uitu/ai_agents_just_decompiled_an_n64_game_in_84_days/) |
| Hàng trăm bản port AI trong browser | 9/10/2026 | Halo CE, GTA Vice City, Black Ops, Skate 3… "một số chơi tốt" [13](https://www.explainx.ai/blog/ai-decompiled-game-browser-ports-halo-vice-city-black-ops-kotaku-2026) |

⇒ **Mức B (code-complete) không còn là rào cản kỹ thuật.** Điều tôi viết ở §0.1 rằng mức B là
"nơi tốn kém nhất" **không còn đúng từ 10/2026** — chi phí đã giảm từ *nhiều tháng* xuống
*vài giờ đến vài ngày*. Rào cản duy nhất còn lại của mức B/C là **pháp lý**, không phải kỹ thuật.

#### (b) Sinh game từ đặc tả vẫn chưa giỏi — và vẫn đúng chỗ yếu cũ

| Benchmark | Thời điểm | Kết quả |
|---|---|---|
| **GameCraft-Bench** (140 task, 15 họ game, **Godot 4**) | 6/2026 | agent mạnh nhất (Claude Code, Opus-4.7 high) chỉ **41,46%**; phần lớn agent **< 40%**; hay thiếu **nội dung, phản hồi thị giác, trình bày mạch lạc** [14](https://arxiv.org/html/2606.17861v1) |
| **Play2Code** (GUI agent playtest vòng lặp) | 5/2026 | LLM một phát **36,8%** → có vòng **playtest tự động 72,3–77,8%** (**+37,1 điểm**) [15](https://arxiv.org/html/2605.28258v1) |
| **Spec2Game** (chi tiết theo model) | 10/2026 | tốt nhất **Claude Sonnet 5: 77,27 tổng** (D1 96,30 · D2 69,95 · D3 84,42 · **D4 60,01**) [1](https://arxiv.org/html/2610.04253v1) |
| **GameDevBench** | 8/2026 | `pass@1` cao nhất **63,1** (GPT-5.6 Sol high); Claude Opus 4.8 **55,9** [16](https://benchmarklist.com/benchmarks/gamedevbench/) |

⇒ **Hai kết luận đáng giá nhất cho dự án này:**
1. **Engine thật khó hơn Pygame rất nhiều**: 77,27 (Pygame) vs **41,46%** (Godot). Đừng kỳ vọng
   AI dựng xong game trong 1 phát.
2. **Vòng playtest tự động là đòn bẩy lớn nhất** (+37 điểm) — lớn hơn đổi model. Đây là việc
   phải làm **từ ngày đầu**, không phải cuối dự án.

#### (c) Hệ quả nghề nghiệp: các studio bắt đầu **giấu build**

Tháng 10/2026, hai studio độc lập huỷ playtest công khai vì sợ bị clone bằng AI:
**Digital Sun** (`ReVamp`, dời sang Discord 29/10) [17](https://www.polygon.com/revamp-playtest-limited-ai-cloning-fears/)
và **Alliance Arts / Who You** (`Drunken Goddess Reflux`, 16/10) [18](https://thisweekinvideogames.com/news/indie-game-developers-cancel-public-playtests-over-ai-clone-concerns-revamp-drunken-goddess-reflux/).

> **Nhận định:** đây là bằng chứng thị trường cho thấy **clone AI đã chơi được thật** — nếu
> không, không studio nào huỷ demo. Nhưng nó cũng cho thấy **tốc độ ra thị trường** mới là lợi
> thế cạnh tranh, không phải "bí mật kỹ thuật". Với dự án của bạn, điều này **không** tạo lợi
> thế nào từ việc clone giỏi hơn — lợi thế nằm ở **bản sắc art + thiết kế cân bằng riêng**.

---

### 1.7 Chuỗi công cụ: repo đã dùng gì — và cái tốt nhất 10/2026 là gì

**Trả lời ngắn: chưa dùng cái tốt nhất.** Repo đang dùng chuỗi 2022–2024, và chuỗi đó
**không xuất được thân hàm** — nên mọi câu "phải đoán" trong 10 file kia đều là
*giới hạn của công cụ*, **không phải** giới hạn của dữ liệu.

| Bước | Repo đã dùng | Tốt nhất 10/2026 | Chênh lệch |
|---|---|---|---|
| Metadata + RVA | **Il2CppDumper** (Perfare) | **Cpp2IL** / Rodroid `il2cpp-dumper-rs` v8 / CPP2IL platform | Il2CppDumper **không có commit từ 7/2024**; Cpp2IL là bản được duy trì [19](https://github.com/morluto/awesome-reverse-engineering) |
| **Thân hàm → C#** | ❌ **không làm** | **CPP2IL** (Method Body ✅) · Rodroid v8 "C# decompiler" · Cpp2IL (⚠️ partial) | đây là **mảnh ghép còn thiếu** [20](https://github.com/chenzifeng/cpp2il.com) [21](https://github.com/rodroidmods/il2cpp-dumper-rs) |
| Decompile sâu | ❌ không làm | **Ghidra headless + `pyghidra-mcp` / GhidraMCP** — agent tự gọi được | biến decompile thành *lời gọi hàm của agent* [22](https://www.skillsdirectory.com/skills/rehan-remade-reverse-engineering) |
| Asset | **UnityPy 1.25.4** + **AssetStudio** (typetree) | **AssetRipper** | AssetRipper xuất được **pivot / border / mesh / nested serialized** [19](https://github.com/morluto/awesome-reverse-engineering) |
| Runtime | ❌ không làm | **Frida** + `il2cpp-frida-mcp` | đọc giá/drop/feel **lúc chạy**, không cần decompile |

#### Điều quan trọng nhất: **RVA đã nằm trong tay rồi**

`dump.cs` hiện có **64.727 dòng `// RVA: 0x…`**, **2.854 class**, **1.359 `.cctor()`**.
Nghĩa là Ghidra **không phải đi tìm hàm** — chỉ cần nạp `script.json` (Il2CppDumper sinh ra
cùng `dump.cs`) là mọi hàm đã có tên, rồi decompile đúng địa chỉ.

| Thứ tưởng "không có" | Thực tế trong `dump.cs` | Lấy bằng |
|---|---|---|
| 8 class config không serialize | **259 `static` field**, tất cả khởi tạo trong `.cctor()` | Ghidra + RVA → đọc literal trong `.cctor` |
| Toạ độ đường bay | `BezierPath.points` là `[SerializeField] List<Vector3>` → **có trong `data.unity3d`** | AssetRipper (CSV exporter cũ bỏ nested struct) |
| Thưởng/rơi theo enemy | `Enemy_Data_Balance.GetBonusCoin(int id)` · `GetBonusExp(int id)` · `GetSurvivalScore` · `GetArenaScore(idE, timeLife)` | Ghidra → 6 thân hàm |
| Damage/HP/cost của player | `Player_Get_Datas` **178 field** | Ghidra → `.cctor` |
| Giá tech/drone | `Tech_Datas` 13 field + `Droid_Data_Balance` 6 field | " |

Phân rã 259 field: `Player_Get_Datas` **178** · `GameDatas` **40** · `Tech_Datas` **13** ·
`Map_Get_Datas` **13** · `Droid_Data_Balance` **6** · `Stage_Get_Datas` **5** ·
`Device_Get_Data` **3** · `Enemy_Data_Balance` **1**.

> **Kết luận sửa lại:** không có mục nào trong bộ spec này là "vĩnh viễn không lấy được".
> Mỗi mục hoặc **đã có trong CSV**, hoặc **nằm trong `.cctor()`**, hoặc **nằm trong
> serialized field mà exporter cũ bỏ qua**, hoặc **quan sát được lúc chạy bằng Frida**.
> Chênh lệch chỉ là **công cụ**, và công cụ thì thay được.

### 1.8 Trường hợp thuận: đây là game **2.5D sprite**, không phải 3D

Đúng — và đây là lý do **không nên đọc 41,46% của GameCraft-Bench như trần của dự án này**.
Benchmark đó đo agent dựng **game 3D hoàn chỉnh trong Godot 4**. Game này dễ hơn hẳn,
và manifest chứng minh bằng số:

| Chỉ số | Giá trị | Ý nghĩa |
|---|---:|---|
| `Mesh` | **2** | **cả game chỉ có 2 mesh** (nguồn: `04-unity-assets.md`) |
| `SpriteRenderer` | 62.815 | render chính là **sprite 2D** |
| `MeshRenderer` | 11.262 | chủ yếu TMP text + quad UI, không phải model |
| `Rigidbody2D` | 1.907 | **vật lý 2D** |
| `BoxCollider2D` | 5.424 | va chạm 2D |
| `CircleCollider2D` | 1.368 | va chạm 2D |
| `PolygonCollider2D` | 705 | va chạm 2D |
| `BoxCollider` (3D) | **7** | không đáng kể |
| `SkinnedMeshRenderer` | **không có** | không xuất hiện trong manifest → **không rig 3D** |
| `MeshCollider` | **không có** | không xuất hiện trong manifest → không va chạm lưới 3D |
| `Terrain` | **không có** | không xuất hiện trong manifest → không có địa hình |
| `NavMeshSettings` | 4 | asset **mặc định của Unity**, không có NavMesh thật |
| `Animator` / `AnimatorController` | 5.792 / 308 | animation 2D + UI |
| `SkeletonDataAsset` | 27 | **Spine** — xương 2D cho boss |
| `Camera` | 6 | 6 camera cho 6 nhóm màn |

#### Vì sao 2.5D dễ hơn nhiều với AI

| Việc | 3D (benchmark) | Game này |
|---|---|---|
| Dựng model + rig + skinning | bắt buộc, AI yếu | **không có** — thay bằng sprite |
| Ánh sáng / bake lightmap | bắt buộc | **không có** (`LightmapSettings` chỉ là asset mặc định) |
| NavMesh / AI di chuyển 3D | bắt buộc | **không có** — enemy bay theo path + vận tốc tuyến tính |
| Va chạm | mesh collider, đắt | **AABB / circle / polygon 2D** — công thức đóng, tái tạo **chính xác** |
| Camera | perspective + occlusion | **cố định**, không gì che khuất |
| Shader | PBR, nhiều biến thể | **70 shader**, phần lớn Sprite/TMP |

Cộng thêm: `border` của `Enemy_Movement` cho **vùng chơi 20×25 unit** cố định
(nguồn: `Enemy_Movement.csv`), và mọi chuyển động enemy đều là **vận tốc + path điểm**
(nguồn: `ENEMY_BEHAVIOUR.md` §1). Đây là mô phỏng **deterministic, không có vật lý phức tạp** —
đúng loại AI làm tốt nhất.

#### Nhưng "2.5D" không làm **nội dung** rẻ đi

| Phần | Khó vì 2.5D? | Thực tế |
|---|---|---|
| Khung gameplay (bắn, di chuyển, va chạm, spawn) | **Không** — dễ | AI làm tốt, spec đã đủ số |
| **Khối lượng nội dung** | Không liên quan | **22.385 spawner · 282 wave · 39 boss · 458 súng** — phần lớn công việc (nguồn: `ENCOUNTERS.md`, `COMBAT.md`) |
| **Art thay thế** | Không liên quan | 2.185 sprite gốc **không dùng được** (bản quyền) → phải vẽ mới |
| **Cân bằng + feel** | Không liên quan | vẫn phải playtest |

> **Kết luận cập nhật:** với **công cụ tốt nhất + 2.5D + dữ liệu đã bóc**, phần *cơ chế* của game
> này nằm trong vùng AI làm được, không phải vùng 41,46%. Giới hạn thật chuyển sang **khối lượng
> nội dung** và **art** — đo bằng **số asset và số giờ vẽ**, không phải bằng độ thông minh của model.

### 1.9 Xếp hạng độ khó: game này thuộc **nhóm dễ clone nhất**

Đúng — nhưng cần tách "clone cơ chế" khỏi "làm ra game". Cơ chế thì dễ; phần còn lại thì không.

#### Bảng "cái gì khó" — đối chiếu 4 loại game

| Hạng mục khó | 3D action | Open world | Realtime PvP | **WindWings** |
|---|:---:|:---:|:---:|:---:|
| Rig / skinning 3D | ✅ | ✅ | – | **không có** (0 `SkinnedMeshRenderer`, 2 `Mesh`) |
| NavMesh / AI dò đường 3D | ✅ | ✅ | – | **không có** (chỉ path điểm + vận tốc) |
| **Realtime netcode** (rollback, đồng bộ) | – | – | ✅ | **không có** |
| Physics phức tạp | ✅ | ✅ | – | **2D đơn giản** (AABB/circle/polygon) |
| Sinh nội dung thủ tục | – | ✅ | – | **không có** (282 wave đặt tay) |
| Ánh sáng / shader PBR | ✅ | ✅ | – | **không có** (sprite + 70 shader) |
| **Khối lượng nội dung** | ✅ | ✅✅ | – | **✅✅** (22.385 spawner) |
| **Art thay thế** | ✅ | ✅✅ | ✅ | **✅✅** (2.185 sprite) |
| **Cân bằng + feel** | ✅ | ✅ | ✅ | **✅** |

#### Bằng chứng "không có netcode" — phần khó nhất của game nhiều người chơi

| Thư viện | Số lần xuất hiện trong `dump.cs` |
|---|---:|
| `Photon` | **0** |
| `Mirror` | **0** |
| `Netcode` (Unity NGO) | **0** |
| `WebSocket` | **0** |
| `SignalR` / `SocketIO` / `LiteNetLib` | **0** |
| `UnityWebRequest` | 170 |
| `Firebase.Database` | 28 |

Nghĩa là **PvP/Arena là async** (đọc dữ liệu người chơi khác từ Firebase: `ArenaDatabaseCleaner`,
`ArenaRank`, `ArenaUserStruct`), **không phải realtime**. Đây là khác biệt lớn: netcode realtime
là hạng mục khó nhất và tốn kém nhất của game multiplayer — ở đây **không tồn tại**.

#### Quy mô codebase

| Chỉ số | Giá trị |
|---|---:|
| Class trong `Assembly-CSharp` | **2.854** |
| `MonoBehaviour` | 618 |
| `ScriptableObject` | 35 |
| `IEnumerator` (coroutine) | 1.098 |
| `async` / `Task<>` | 811 |

> **Nhận định:** 2.854 class là codebase **trung bình** cho game mobile 10M+ tải, nhưng phần lớn
> là UI (125 class UI) và luồng màn hình — loại code AI sinh tốt nhất. Phần "khó" của game
> (vật lý 3D, netcode, AI dò đường) **không có mặt**.

#### Vậy "dễ clone" nghĩa là gì — và không nghĩa là gì

| Việc | Độ khó | Ai làm |
|---|---|---|
| **Clone cơ chế** (bắn, va chạm, spawn, path, nâng cấp) | **Thấp** — AI làm được | AI + 1 dev |
| **Chép nội dung** (282 wave, 458 súng, 39 boss) | **Trung bình**, nhưng **nhiều giờ** | AI sinh hàng loạt + dev duyệt |
| **Art thay thế** (2.185 sprite, 27 Spine, 69 audio) | **Cao** — không AI nào vẽ được đúng gu | artist |
| **Cân bằng + feel** | **Cao** — đúng chỗ AI yếu nhất (32,1/100) | designer + playtest |
| **Live-ops** (giá, IAP, retention, event) | **Cao**, phụ thuộc thị trường | designer + data |

> **Kết luận thẳng:** clone **cơ chế** của game này là việc **dễ** — dễ hơn đa số game cùng doanh
> thu, vì nó thiếu đúng 3 thứ khó nhất (3D, netcode, AI dò đường). Nhưng clone cơ chế chỉ chiếm
> **~15–20%** công sức ra sản phẩm. **80% còn lại là nội dung, art và cân bằng** — nơi AI yếu,
> và cũng là nơi quyết định game có hay hay không.

### 1.10 Đào lại feel / cân bằng / art: **cả ba đều có đường lấy**

Sau khi người dùng phản biện, tôi đọc lại `dump.cs` theo **tên field** thay vì theo **CSV**.
Kết quả: ba mục tôi từng gọi là "không đào được" **đều có tên biến, kiểu dữ liệu và vị trí**.

| Mảng | Kết luận cũ (sai) | Thực tế | Chi tiết |
|---|---|---|---|
| **Cân bằng** | "không có damage/HP player, không có giá" | `Player_Get_Datas` **178 field** chứa `StartHp`, `StartMainCannonDamages[]`, `PlayerCosts[]`; `Tech_Datas` cho **công thức giá** `price = base[i] + delta[i] × lv` | `TUNING_KNOBS.md` §2–3 |
| **Feel** | "nằm trong `libil2cpp.so`" | **11/16 cơ chế** là `[SerializeField]` → nằm trong **prefab**, tức **đã có trong `data.unity3d`**: `VibrateCamera.levelVibrate`, `Enemy_CameraVibrate.timeVibr/lvVibr`, `Enemy_HitSkeletonRenderer.hitColor`, `EffectGlow`, `TimedTrailRenderer`; slow-mo là **const** `timeSlowed = 0,1` | `TUNING_KNOBS.md` §4 |
| **Art** | "không thể tái tạo" | canvas **10,8 × 19,2 unit** (const `haftOfW/H` = 5,4/9,6 → **9:16**); cả game **2 mesh**; chỉ cần **sprite billboard** ≤ 2048² | `TUNING_KNOBS.md` §5 |

#### Con số quyết định: **4.841**

`dump.cs` cho thấy game classes có **4.841 field `[SerializeField]`**. Đó là lượng giá trị
đang nằm trong `data.unity3d` mà **exporter CSV chưa lấy** — vì nó chỉ quét
`reverse-engineering/scriptableobjects/`, không quét component trên prefab.

> `> Nhận định:` sai sót của tôi là **sai phạm vi công cụ**, không phải sai bản chất dữ liệu.
> Cùng một APK, chỉ cần **AssetRipper** thay vì exporter hiện tại là có thêm 4.841 giá trị.

#### Ba tầng đào — và tầng nào đã xong

| Tầng | Nội dung | Trạng thái |
|---|---|---|
| 1 | `const` trong `dump.cs` (900 const game class) | ✅ **đã có giá trị** — `Ease` 31, `timeSlowed` 0,1, `haftOfW/H` 5,4/9,6 |
| 2 | `[SerializeField]` trong prefab (4.841) | 🟡 **chưa export** — chạy AssetRipper |
| 3 | `static` khởi tạo trong `.cctor()` (259) | 🟡 **chưa đọc** — chạy Ghidra |

**Kết luận sửa lại:** cả **feel**, **cân bằng** và **art** đều đào được — không mảng nào
"không có dữ liệu". Cái còn lại chỉ là **chưa chạy 2 công cụ**, và cả hai đều đã có tên
chính xác để chạy. Xem `TUNING_KNOBS.md`.

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

### 2.3 Chưa bóc — nhưng **mỗi dòng đều có đường lấy**

| Hạng mục | Thiếu vì | Đường lấy | Kết quả kỳ vọng |
|---|---|---|---|
| Toạ độ đường bay | `PathCreator.csv`: 30 cột `editorData` nhưng **0 cột `points[i].x/y`** | **AssetRipper** — `BezierPath.points` là `[SerializeField]` | 399 path × ~9 điểm = **~3.600 Vector3** |
| Tham số spawner | 6/7 file `*_Spawner.csv` có **0 cột dữ liệu** | Ghidra (RVA từng `*_Spawner`) | trường `[SerializeField]` + hằng số |
| Damage/HP của player | `forceType = Enemy` **458/458**; `Player_Get_Datas` không serialize | Ghidra `.cctor` | **178 field** |
| Giá / tỉ lệ rơi | `Box_Rewards.id = 0` **800/800**; không cột `weight`/`price` | Ghidra `GetBonusCoin/Exp` + Frida | hàm thưởng theo `id` |
| Hiệu ứng item | `Sub_Item.csv` **0 cột hiệu ứng** | Ghidra (class item) + Frida | hiệu ứng + thời gian |
| **Toàn bộ feel** | chỉ export ScriptableObject, **bỏ prefab** | **AssetRipper** — 4.841 field `[SerializeField]` | shake, tốc độ, màu hit, trail, delay bắn |
| Âm thanh | 69 `AudioClip` nhưng **0 file export** (FSB5 trong `.resS`) | **AssetRipper** / vgmstream | 69 file `.wav` |
| Hành vi (appear/burn/stun) | `Enemy_Appear.csv` chỉ có ref | Ghidra: `Enemy_Appear.Appear(Action)` … | toàn bộ state machine |
| Pivot/border sprite | 586 sprite không-Atlas ghi `?` | **AssetRipper** | pivot, border, mesh |

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
>
> **Đây là độ phủ với chuỗi công cụ cũ.** Nếu chạy thêm §1.7 (Cpp2IL + Ghidra + AssetRipper
> + Frida), ước lượng **85–95%** — vì cả 8 bảng trên đều có đường lấy, không mục nào
> nằm ngoài dữ liệu.

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
5. **Từ 10/2026, giá trị của "dịch ngược giỏi" giảm mạnh** vì ai cũng làm được trong vài giờ.
   Giá trị chuyển sang **chất lượng** (GameCraft 41,46%) và **vòng playtest** (+37 điểm) —
   tức là sang phần **thiết kế và tinh chỉnh**, đúng phần spec này không làm hộ được.
6. **Con số 41,46% KHÔNG phải trần của dự án này.** Nó đo game **3D hoàn chỉnh trong Godot**;
   đây là game **2.5D sprite + physics 2D** với **2 mesh** và không có `SkinnedMeshRenderer` (§1.8).
   Phần *cơ chế* nằm trong vùng AI làm tốt; giới hạn thật là **khối lượng nội dung** và **art**.

> `> Nhận định:` với một đội 3–5 người, bộ spec này rút ngắn **giai đoạn nghiên cứu** (~15–20%
> tổng công) xuống gần 0, nhưng **không** rút ngắn giai đoạn sản xuất art/audio/test.
>
> **Ước lượng công còn lại cho một bản 2.5D tương đương** (không tính live-ops):
> code cơ chế **~1–2 tháng/2 người** (AI hỗ trợ mạnh) · nội dung 282 wave **~1–2 tháng** ·
> art thay thế **~2–3 tháng/1 artist** · cân bằng + playtest **~1 tháng**.
> Art là **đường găng**, không phải code.

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
| 9 | 404 Media (16/10/2026) | `decomp.dev` đóng cửa vì AI |
| 10 | X/@AIWarper (10/2026) | Opus 5.5 decompile game Steam trong < 30 phút |
| 11 | aiweekly (20/10/2026) | `Reverse Engineer Anything` 342.000 sao |
| 12 | r/gamedev (12/10/2026) | N64 decompile 84 ngày (AI) vs 596 ngày (tay) |
| 13 | explainx.ai / Kotaku (10/2026) | hàng trăm bản port AI chạy trong browser |
| 14 | GameCraft-Bench, arXiv 2606.17861 | Godot 4: agent mạnh nhất 41,46% |
| 15 | Play2Code, arXiv 2605.28258 | 36,8% → 72,3–77,8% nhờ vòng playtest |
| 16 | GameDevBench (8/2026) | `pass@1` cao nhất 63,1 |
| 17 | Polygon (19/10/2026) | Digital Sun huỷ playtest `ReVamp` |
| 18 | ThisWeekInVideoGames (19/10/2026) | thêm studio huỷ demo vì sợ clone |
| 19 | awesome-reverse-engineering (21/10/2026) | Il2CppDumper **ngừng commit 7/2024**, Cpp2IL thay thế; AssetRipper |
| 20 | cpp2il.com (6/2026) | so sánh: Method Body — CPP2IL ✅ · Il2CppDumper ❌ · Cpp2IL ⚠️ partial |
| 21 | Rodroid il2cpp-dumper-rs v8.0 (7/2026) | decompiler C#, đọc cả Unity 6 |
| 22 | skillsdirectory (6/10/2026) | Ghidra/IDA MCP + `il2cpp-frida-mcp` cho agent |

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
