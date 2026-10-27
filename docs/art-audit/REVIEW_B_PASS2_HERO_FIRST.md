# Review lại art B — dừng nhân rộng, khóa một hero trước

**Ngày:** 28/10/2026 · **Vai:** Art-style-auditor `arena/65f8a31f` · **Kết luận:** **chưa duyệt hero hay lô nào**. Bản cũ của báo cáo A/B vẫn ở [AUDIT_A_B_STYLES.md](AUDIT_A_B_STYLES.md); báo cáo này không ghi đè kết luận theo SHA cũ.

## 1. Kết luận thẳng

Phản ánh “vẫn như đồ chơi” **có cơ sở** ở phần lớn fleet chưa được sửa, cũng như một số FX/UI. Không nên gọi cả đợt mới là “không thay đổi”: B đã thay đổi **thực sự** ở một số tàu, drone, boss, W0 và slot UI. Nhưng các thay đổi đó **chưa đồng đều và chưa là đột phá cho cả bộ**. Hero được B đề cử vẫn là cùng PNG đã thấy ở vòng trước; chưa đủ chín để khóa làm chuẩn nhân bản.

| Đối tượng | Kỹ thuật / bằng chứng | Mĩ thuật độc lập | Quyết định |
|---|---|---|---|
| **A** `125e1e33` | Không có head/hero mới từ audit trước. | Kết luận W1 cũ vẫn áp dụng, chưa có candidate mới để chốt. | **REDO / chờ A nộp một hero**, không giả định đã có pass mới. |
| **B hero #01 / 10001** `e2fe4be` | Có master, PNG, crop và proxy; còn ngoài dải proxy, chưa chứng minh gradient **từng panel** và trần viền **cục bộ**. 64 px chỉ kiểm tĩnh. | Có tiến bộ thật so pass đầu; **vẫn REDO**: trắng bóng/viền màu mạnh, khối giáp như vỏ nhựa, tỷ lệ và cụm treo bên chưa có cảm giác khí tài chắc như gốc. | **KHÔNG KHÓA.** B phải sửa chính một hero và nộp lại cả hai cổng. |
| **B #04 / 10004** | Candidate phụ, không phải hero B đề cử; có master và đo mẫu. | Chi tiết kim loại/cơ khí tăng rõ so pass đầu, nhưng chi tiết nhỏ chìm ở canvas 64 px; chưa kết luận đẹp hoặc sẵn sàng làm chuẩn. | **CHƯA DUYỆT**, không coi như hero đã khóa. |
| **B W1 toàn bộ** | 3/25 ship và 2/13 drone đổi giữa `deec4e2` và `e2fe4be`; 22 tàu còn lại không đổi PNG. | #08/#12/#13 và drone #04/#05 khá hơn rõ, nhưng nhiều tàu còn vỏ tròn, màu khối, lặp hình. | **REDO lô / đóng băng nhân rộng.** |
| **B W0** | 25/25 tên/kích thước/mode khớp A; S1–S4 là **concept**, không phải capture Godot. | Mới giảm lóa và dùng sprite thật nhưng quá trống/phẳng; icon 3D poster vẫn khác ngôn ngữ cảnh tĩnh. | **Chưa nhận**; làm theo hero đã khóa rồi chụp build thật. |
| **B W2/W3** | Có các bản mới và mapping boss 7001–7005; chỉ đo mẫu 3 enemy/5 boss độc lập, không giả nhận đo lại toàn lô. | Năm boss đã tiến bộ đáng kể nhưng một số đổi mất đặc trưng ID; các enemy mẫu vẫn tái dùng cùng form. | **REDO/chưa nhận lô**, chỉ quay lại sau P0. |
| **B W4/W5** | W4 nay **có thay đổi**; các va chạm hash quan trọng ở W5 đã được sửa, còn một cặp cần xác minh chức năng. | Một số mẫu UI/FX/planet vẫn phẳng hoặc bóng nhựa so gốc. | **Chưa nhận**, kiểm chức năng/motion sau P0. |

**Lệnh làm việc:** theo director `lần 158` [comment 6447756124](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6447756124), mỗi hướng làm **một** hero P0, nộp master + 3–5 so sánh gốc cùng footprint + mẫu 64 px + kết quả planner. Chỉ nhân tiếp khi auditor xác nhận **cả kỹ thuật lẫn mĩ thuật**; curator không nhận lô trước đó. Không cần xóa những mẫu đã vẽ, nhưng không tiếp tục sản xuất hàng loạt để “đạt số lượng”.

## 2. Snapshot, nguồn và giới hạn

- **B pass đầu:** `31e237fb205cf1e7abde03cb4fcec45adb5b4a4d`.
- **B ROUND 2:** `deec4e248fc05013a396da8c1a91fc8c664a2d29`.
- **B phản hồi audit, head được review:** `e2fe4be67f4748a44377790557948733b31e3286`; [handoff của B](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6449867096). **A:** `125e1e33fd485110d94823efa38e745bc04a2cdf`.
- **Planner:** `100cfcebc38c1aec6dd8dc1cfa62c6aa23f77d86`, `measure_asset.py` SHA-256 `c33182347dabf7e1eba4a3278d298a62a89a43ccbc2ae75e3ba0d6181a22b053`. **Spec/gốc:** `965c770c9ab19846719aeaeae3d6ec56572b0ccd`, `docs/spec/{VISUAL_DESIGN,ART_STUDY}.md`, contact sheets, captures và `datas/`; `tools/design-metrics.py` SHA-256 `77bb6a91edd691145924b63dad4c09d95e98c9525390dbbd986d27ca3bddebc7`. Coordination đã đọc lại `4dfcda58b22e01d4b402244964176b59b7606a62`, `SESSION_PROMPTS.md` và comment PR #12.
- **Anchor:** `datas/ships.json` có 25 ID `10001…10024,10999`; `datas/drones.json` có 13; `datas/bosses.json` và `docs/assets/sprites-index.csv` nối boss 7001–7005 đến `bosses-01.jpg` #2–#6. Manifest W1 mới của B **khai báo** `GLYPH-ship-10001` cho #01, … và `GLYPH-drone-20004` cho drone #04; index/gốc xác nhận các ID và tile gốc. Việc bind những PNG này vào scene/game vẫn **RUNTIME_UNVERIFIED**, không suy ra từ manifest.
- [STATIC_CONFIRMED] = PNG, hash, manifest, phép đo/crop có thể kiểm. [INFERRED] = phán đoán thẩm mỹ hay đối tượng tương tự, không phải dữ kiện engine. [CONFLICTING] = khác baseline/định nghĩa. [UNKNOWN] = chưa đủ dữ liệu. [RUNTIME_UNVERIFIED] = chưa test build, thời gian, pivot, blend hay UI binding. **Không có RUNTIME_CONFIRMED** cho art mới.

## 3. P0 hero #01 — vì sao chưa khóa

**Đã tiến bộ:** ở [12_b_pass2_player, dòng 1–2](comparisons/12_b_pass2_player.png), so `31e237f` → `deec4e2`, #01 có cockpit, nhiều tấm và động cơ; #04 có khung máy, AO tương đối rõ hơn. Đây là thay đổi cấu trúc/vật liệu, không chỉ đổi byte. Nhưng #01 ở `e2fe4be` giống hệt `deec4e2` (cùng SHA-256 `1d52dd22d3952c66ab34b57476da4e5272f213c9169858986c4dce0a84c09fab`); 1024 master SHA-256 `7eb7f444abc02dcc537b164b8f5089ee9295f4db38637dead3c9b36b6c9830e3`. Xem [17_b_latest_player, dòng 1](comparisons/17_b_latest_player.png).

**[INFERRED — phán đoán mắt]** Gốc 10001 đọc trước là thân xanh kim loại compact với hai cánh gắn vào cùng khối. B #01 đọc trước là vỏ trắng sáng + mảng xanh/cam viền mạnh; bóng gương và các bề mặt đều, cộng pod tròn bên phải/thanh mảnh bên trái, tạo cảm giác linh kiện gắn lên mô hình hơn là giáp–cánh–động cơ chịu lực. Có chi tiết nhưng quan hệ lớn/nhỏ và vật liệu chưa thuyết phục. Ở canvas **64×64 pixel hiển thị thực trong PNG board**, vẫn nhận được hình tàu và canopy; nhiều seam/vent và gắn kết pod–cánh không còn đọc rõ. Không yêu cầu nhìn thấy từng đinh tán ở 64 px; yêu cầu khối chính và mối nối vẫn rõ. Board probe của B có downsample 64 px rồi **phóng lên 180 px** để soi; hữu ích để xem pixel, nhưng không thay bài test kích thước hiển thị thật.

**[STATIC_CONFIRMED]** Planner chưa chỉnh sửa đo hero #01 như sau:

| B snapshot | `grad_stops` toàn ảnh | `outline_px` trung bình | `detail` proxy | `V` / `V std` |
|---|---:|---:|---:|---:|
| `31e237f` | 26 | 0.00 | 0.581 | 0.838785 / 0.163273 |
| `deec4e2` | 45 | 0.73 | 0.843 | 0.666813 / 0.277580 |
| `e2fe4be` | 45 | 0.73 | 0.843 | 0.666813 / 0.277580 |

Dải tạm class ship của planner là `grad_stops` 6–25 và `detail` 0.05–0.30, nên hai proxy này ngoài dải ở head mới; **25/25 ship** đều ngoài ít nhất một trong ba dải style, **0/25** trong đủ ba. Đây là cảnh báo chứ **không** chứng minh ảnh đẹp/xấu hoặc phải bỏ chi tiết: dải được hiệu chuẩn trên ba mẫu tổng hợp. `grad_stops` đếm histogram toàn ảnh, **không phải 45 tầng trên mỗi panel**; `detail` tính biên tương phản, không biết chi tiết có hợp cơ khí. `outline_px=0.73` là **trung bình** dải tối tại biên, không chứng minh mọi vị trí ≤1 px theo lệnh director. Region crop do B đo có thể cắt nhiều tấm và tạo biên giả; chưa chứng minh từng panel hay viền cục bộ. Palette B sáng có baseline `val/chroma` khác Ink & Ember: **[CONFLICTING]**, không bác chỉ vì màu sáng.

**Việc sửa cụ thể cho B #01:**
1. Khóa lại mass/silhouette theo tàu 10001: mũi–canopy–thân–hai cánh thành một thể, đầu cánh và gốc cánh có tiết diện chịu lực; cụm pod/súng phải có chân gá và tỷ lệ hợp lý, không cắm trang trí ngẫu nhiên. Không bắt buộc ép hai bên đối xứng hoặc sao chép 1:1.
2. Dựng 2–3 lớp giáp thực sự chồng, có contact shadow/AO tại mép, cạnh vát và rim phía trên; phân biệt vật liệu sơn/kim loại, kính cockpit và emissive. Giảm độ bóng nhựa đồng đều, giảm viền màu quá gắt; để màu Solar Neon làm điểm nhấn chứ không lấp khối tối/sáng.
3. Vent/seam/rivet gắn theo công năng và kích thước hợp lý; bỏ đường/bu-lông nhỏ vô nghĩa. So lại phiên bản không micro-detail: silhouette, canopy, cánh, động cơ phải tách được trước; sau đó mới thêm chi tiết.
4. Nộp master, sprite 256, crop **nguyên pixel của từng panel**, ảnh 64 px thực và cặp original/old/new; chứng minh 3–5 mức chuyển liên tục trên panel, AO ở mối nối và kiểm viền ≤1 px tại export. Chạy đúng planner, báo raw bất kể ngoài dải; không hạ ngưỡng/đánh đồng điểm số với đẹp. Test cảnh thật chỉ sau khi có build.

## 4. Cái mới đã tốt hơn — và cái còn vướng

- **Fleet:** [17_b_latest_player](comparisons/17_b_latest_player.png) cho thấy #08 bỏ vòng nhựa xanh/vàng thành tàu + vòng cơ khí; #12 bỏ mecha đồ chơi thành tàu cánh dài; drone #04 chuyển sang orb có vỏ/khớp. Đây là nâng cấp thật. Nhưng theo ID được khai báo, gốc #08 là khối vòng ngắn và gốc #12 là mecha dạng rộng; các bản mới đã thay nhiều nhận diện — cần thống nhất chủ ý trước khi coi là đúng ID. [22_b_latest_unfixed_fleet](comparisons/22_b_latest_unfixed_fleet.png) là 5 cặp chưa đổi: #02 bóng vàng/hồng, #06 và #11 rất gần một công thức vòng dù gốc khác nhau, #23 là robot xanh-vàng thay vì silhouette cánh dơi gốc. #06/#11 **không cùng byte**; nhận định lặp là mắt, không phải hash trùng.
- **Boss:** [19_b_latest_boss](comparisons/19_b_latest_boss.png), năm ID 7001–7005: bản mới có khối máy/tầng/ánh kim rõ hơn, bỏ mẫu mắt tròn lặp hàng loạt cũ. Tuy vậy 7004 gốc là khối mũ bảo hộ ngang, bản mới là tàu mũi nhọn; 7005 đã giữ được motif vòng tốt hơn. Xử lý lại từng silhouette theo danh tính được map, **không** phủ nhận cải thiện của cả năm. Part tách, pivot và va chạm vẫn chưa test.
- **Enemy:** [20_b_latest_enemy](comparisons/20_b_latest_enemy.png), ba ví dụ là **analogues**, không phải tuyên bố cùng ID. #06 và #18 mới có chất cơ khí hơn nhưng vẫn gần như cùng orb + hai móc chỉ đổi màu; #01 red dart không đổi và vẫn giống đồ chơi. Cần phân biệt silhouette theo vai trò, không lấy cùng model đổi màu làm bằng chứng đa dạng.
- **W4/W5:** [23_b_latest_core](comparisons/23_b_latest_core.png) cho thấy sky được làm tối; Earth/Jupiter được đổi bề mặt, nhưng Earth vẫn như quả cầu sơn bóng, impact vẫn là ngôi sao cartoon so vụ nổ gốc. Đây là đánh giá **5 mẫu**, không phải đo hết lô. [21_b_latest_w5](comparisons/21_b_latest_w5.png) cho thấy ShopIcon, event, Blink, coin pile được sửa đúng hướng chức năng và không còn cùng biểu tượng sao. Hãy ghi nhận điều này thay vì lặp lỗi cũ.
- **W5 còn kiểm binding:** trong `deec4e2`, AP-0251/0264/0443/0462 cùng SHA `9c12a639…`; ở `e2fe4be` bốn PNG đã có **bốn SHA khác nhau**. Coin AP-0181/0191 cũng đã khác byte. Tổng 274 file W5: **178 → 187 hash khác nhau**, trùng vượt bản đầu **96 → 87**. AP-0323/0324 lock/unlock vẫn cùng SHA `7a5510d8023079285d1829bee05efeb57229eefa7990d4484a99cea1ac6f6ac2`; **không tự kết luận sai** vì có thể cùng khung + overlay động. [latest_w5_hash_review.csv](latest_w5_hash_review.csv) ghi từng `row_id`, path và hai hash. **USER/nhóm tích hợp:** xác nhận layer/binding lock/unlock và các slot trùng có được bổ sung nội dung động không; static decode chưa trả lời đủ.

## 5. W0: hết lóa nhưng chưa phải game đẹp đã chạy

[18_b_latest_w0](comparisons/18_b_latest_w0.png) so gốc / `deec4e2` / `e2fe4be`: bản mới đổi từ poster nhiều tia, nổ sáng thành composite tối ít đạn, dùng sprite hiện tại. Cải thiện kiểm soát lóa là thật, nhưng có nguy cơ quá rỗng, nền xanh phẳng và thiếu cảm giác va chạm/chiều sâu so capture gốc. Icon W0 vẫn là key art 3/4 rực, khác mức thể hiện của sprite/cảnh; cần thống nhất hình dáng và vật liệu của hero, không buộc cùng góc máy.

| Concept | Contrast p95–p05 `deec` → `e2fe` | Accent mọi hue `deec` → `e2fe` | Detail-gradient `deec` → `e2fe` |
|---|---:|---:|---:|
| S1 | 0.7295 → 0.3524 | 0.0803 → 0.0279 | 63.06 → 21.84 |
| S2 | 0.8642 → 0.3467 | 0.4078 → 0.0297 | 81.60 → 26.07 |
| S3 | 0.9362 → 0.3083 | 0.4165 → 0.0217 | 102.63 → 17.31 |
| S4 | 0.6669 → 0.4387 | 0.0958 → 0.0207 | 51.24 → 28.31 |

Đo bằng đúng `design-metrics.py`, xem [frame_metrics_pass2.csv](frame_metrics_pass2.csv) và [frame_metrics_latest.csv](frame_metrics_latest.csv). Bốn frame gốc contrast 0.511–0.667, nhưng nội dung, text overlay và độ phân giải khác; **không** coi so số giữa cảnh khác là nghiệm thu. Accent là mọi pixel S>0.6/V>0.6, không chỉ màu nóng. 25 slot mới đã được kiểm trực tiếp có cùng tên/cỡ/mode với A; không chứng minh store duyệt hoặc game chạy.

**Sửa thông tin cũ:** ở `deec4e2`, `W0B_MANIFEST.md` vẫn ghi S1 V 0.848/520 KB trong khi PNG thực 680.776 byte, spec tool V 0.6851. Ở `e2fe4be`, B **đã thay manifest**, ghi rõ concept và không còn dòng cũ; S1 mới 201.471 byte, SHA `f348d7ef042eb1b64a93a06583ab33aecbd07884d1c063e7d29d4c630ad2632d`, spec tool V 0.3596. Không tiếp tục gán mâu thuẫn cũ cho head mới. Trước submission phải chụp từ release build thật, test 10 frame chơi + 3 frame thưởng, motion/0,2 giây, UI, VFX, nền và readability.

## 6. Bằng chứng, tái lập, CI

Bảng 12–16 so gốc ↔ `31e237f` ↔ `deec4e2`, [pass2_index.csv](comparisons/pass2_index.csv) có **22 hàng**. Bảng 17–23 so gốc ↔ `deec4e2` ↔ `e2fe4be`, [latest_index.csv](comparisons/latest_index.csv) có **32 hàng**. Mỗi hàng ghi đường dẫn, tile, crop, hash gốc và hash hai PNG; sprite/frame fit giữ tỉ lệ với cùng footprint tối đa, không khẳng định cùng world scale. JPEG contact tile rất nhỏ, đặc biệt enemy dart crop 27×28: chỉ dùng silhouette/motif, không dùng để suy nét nhỏ gốc. Bảng so là tài liệu nội bộ, **không đưa reference vào game/store**.

Đã đo độc lập **56 PNG ở mỗi head mới**: đủ W1 48 + 3 enemy + 5 boss; [pass2_metrics.csv](pass2_metrics.csv), [latest_metrics.csv](latest_metrics.csv), 0 lỗi và hash khớp PNG. 56 dòng mới khớp toàn bộ trường đo tương ứng trong CSV 512 dòng do B nộp, nhưng 456 dòng còn lại **chưa đo lại độc lập**; không trình bày chúng như kiểm độc lập. Đã tái chạy byte-identical cả 112 kết quả sprite, W0 frames, hash W5, 12 board và hai index; kiểm SHA nguồn của 54 hàng và link trong báo cáo. Đã kiểm trực tiếp 512 manifest records/nguồn master có mặt, 412 hash PNG khác nhau; đây là coverage, không chứng minh đúng thẩm mỹ hoặc runtime. Planner `--style-selftest` và `gate_batch --selftest` exit 0. `gate_batch` đếm cặp, không tự xác minh cặp có đúng nội dung.

Ví dụ tái lập sau khi fetch các commit đã pin (không checkout/sửa nhánh khác, `docs/spec/`, `datas/` hay `tools/`):

```bash
R=/tmp/ww-b-review
mkdir -p "$R"/{spec,planner,A,B-old,B-round2,B-latest}
git archive 965c770c9ab19846719aeaeae3d6ec56572b0ccd docs/spec docs/assets/contact-sheets docs/assets/sprites-index.csv docs/apk-analysis/ramus/2026-10-23-phone tools/design-metrics.py | tar -x -C "$R/spec"
git archive 100cfcebc38c1aec6dd8dc1cfa62c6aa23f77d86 docs/art-plan | tar -x -C "$R/planner"
git archive 125e1e33fd485110d94823efa38e745bc04a2cdf art | tar -x -C "$R/A"
git archive 31e237fb205cf1e7abde03cb4fcec45adb5b4a4d art | tar -x -C "$R/B-old"
git archive deec4e248fc05013a396da8c1a91fc8c664a2d29 art | tar -x -C "$R/B-round2"
git archive e2fe4be67f4748a44377790557948733b31e3286 art | tar -x -C "$R/B-latest"
python3 -m venv "$R/venv"
"$R/venv/bin/pip" install 'Pillow==13.0.0' 'numpy==2.4.6'
P="$R/venv/bin/python"
"$P" docs/art-audit/measure_b_pass2.py --b-root "$R/B-latest" --planner "$R/planner/docs/art-plan/measure_asset.py" --out "$R/latest_metrics.csv" --workers 3
"$P" docs/art-audit/measure_frames.py --spec-root "$R/spec" --a-root "$R/A" --b-root "$R/B-latest" --out "$R/frame_metrics_latest.csv"
"$P" docs/art-audit/build_b_pass2_comparisons.py --spec-root "$R/spec" --old-root "$R/B-round2" --new-root "$R/B-latest" --out "$R/boards" --latest
"$P" docs/art-audit/compare_b_w5_hashes.py --old-root "$R/B-round2" --new-root "$R/B-latest" --out "$R/latest_w5_hash_review.csv" --by-row-id
# Thay B-latest bằng B-round2 để đo vòng trước; bỏ --latest, dùng B-old → B-round2 để dựng bảng 12–16.
```

**CI [UNKNOWN]:** check-runs GitHub đúng B head `e2fe4be67f4748a44377790557948733b31e3286`: **0**, không gọi PASS. Không có test ba người nhận diện “cùng game” và không có build/runtime được thử; cần ghi kết quả thật khi có. Quyền tên/art vẫn chờ USER xác nhận. Head bằng chứng và số check-runs riêng sẽ được ghi ở comment bàn giao PR #12.
