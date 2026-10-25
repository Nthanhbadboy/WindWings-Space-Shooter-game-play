# System manifest — `hệ thống → raw/hợp đồng → luật đã chứng minh → AI tự chọn → test`

> **Vì sao có bảng này** (task PR12 comment `6399017163`, report 79 peer `549a7b5b7c`): tách rõ
> **"APK nói gì"** khỏi **"mình chọn gì"** — mỗi dòng là một hợp đồng tối giản để AI làm game mới
> biết: nguồn raw nào tin được, luật nào đã chứng minh (mức A/B), chỗ nào **phải tự chọn thiết kế**,
> và nghiệm thu bằng gì. **Cập nhật 25/10 sau report 78–79.**
>
> **Trạng thái chung:** pack tham khảo (asset v2) **có sẵn nhưng chưa runtime/import/visual approval**;
> **L1 khởi công được ngay, không chờ playback**; 2 phép tái đối chiếu runtime (`CROSSCHECK`) làm khi
> có lần chạy mới. Chi tiết từng hệ: `DATA_SYNC.md` · `COVERAGE_AUDIT.md` · `DESIGN_READINESS.md`.
>
> **Cách dùng:** cột "Luật đã chứng minh" — làm theo là xong; cột "AI tự chọn" chỉ vài dòng; chỗ
> nào ghi **scoped unknown** thì **không bịa** — cần thêm đào mới giao nhánh dữ liệu. Nghiệm thu =
> automated regression/reference checks (metrics là gate phát hiện lệch, không phải approval).

| Hệ thống | Raw / hợp đồng (nguồn) | Luật triển khai **đã chứng minh** | AI game mới **tự chọn** | Test nghiệm thu |
|---|---|---|---|---|
| **Player — 6 mảng stat** | `datas/player_start_stats.json` ← `ia-resolved.json` (claim IA2); combat hợp đồng `combat_chain_contract.json.gz` (peer report 81/82 — **file bên nhánh dữ liệu, repo này KHÔNG có**; giá trị 24 index thì có trong `player_start_stats.json`) | save/load: **id − 10001**; **combat: impl N → index N−1** — tàu 10001→2 · 10003→0 · 10004+→id−10001; 24 tàu · 16 bán · 8 giá `−1` | giữ hoặc vẽ lại đường cong | unit test 24 cặp giá trị |
| **Player — nhịp bắn** | reports 79–**84** peer (`c7f72fe22e`, đủ 24/24 impl + **25 coroutine đã dịch control-flow**) | `rate` = **interval nhóm phát**: `base × (1 − tech tier 0/3/5/8/10/12 %)`, dual deadline, N extra ⇒ **N+1** entry, không catch-up, demo override 3,0/4,0; **`damage × rate` KHÔNG phải DPS** — crit `random ≤ critPercent` ⇒ ×2. Report 84 đính chính: `_delay` impl 7/9 là **sau attack hold** · impl 17 chờ **theo cặp** vị trí (`i % 2`) · **impl 18 = toggle particle** (`rateOverDistance` 2/0), **không spawn đạn**; laser/saw/clone/pumpkin có **models chạy được** (`combat_coroutine_models.py`): clone stop→wait **0,34**→pool, pumpkin active 2/charge 1/duration 4→callback Hide | `newdesign` nếu thêm catch-up / bỏ extra gate / gộp nòng / suy helper dispatch = hit; DPS runtime còn callback→damage→HP (peer làm tiếp) | replay: đối chiếu models theo từng tàu |
| **Player — HP** | `BALANCE` §0.6 (claim B2 mức A) | `HPmax = 2500 × (1 + 0,18×Tech(0) + abi7×…)`; giáp tách riêng | giá trị khởi đầu mỗi cấp | so HP đúng mốc cấp |
| **Enemy — HP** | `datas/enemy_hp_by_id.json` (**150 cặp**, WRH2); receivers đã dịch (report **85**) | dict theo **id**; **`kHp[mode]` không tồn tại**; mất máu `factor = 100/(100+armor)` (armor<0 ⇒ `2−100/(100−armor)`), overkill clamp 0, gate `IsCaAttack@0x2F`; `noDamage && !ignoreInvincible` ⇒ **skip**, ignore ⇒ bypass; **CalculateDamage chạy cả 2 callbacks** rồi HP re-read (85) | dải HP theo mode + giá trị armor runtime | regression: damage-flow test theo công thức |
| **Wave / spawn** | `waves.json` (`Call_Data` 23 field) · report 53 | `rate` = **delay nhánh Path/Waypoints** (giây); `number = 0` ⇒ số quân = độ dài list; spawn `y = 9,6` | chọn phân bố điểm/range | replay 1 wave: đúng số quân |
| **Map → wave** | `DIFFICULTY_MODES` §7 (11 cấu trúc/614 mảng) + peer `maps.json` | `GetListWaves(mapIndex)`; len2 = stage→boss (giải thích 299/281) | số màn/độ dài phiên (`A5` cần luật continue) | mở đủ từng stage |
| **Độ khó (mode)** | `DIFFICULTY_MODES` §3–5 · `MaxModeIndex` 4 | mode đổi **composition + thưởng** (`levelDelta = [1,2,3.6,3.6]`), **không nhân HP** | hệ số riêng nếu muốn | A/B 3 mode |
| **Kinh tế** | `ECONOMY` §8.1 + mẫu runtime 23/10 | `GetBonusCoin` **100,0 · 20,0**; mẫu Stage 1 ≈ **2 coin/kill** (276 kill → 540 coin) | tỉ lệ rơi (D3), giá talent | đo coin/phiên |
| **Mission %** | `PercentToCompleteMissions222` float[3] `@0x308` | **[0,2 · 0,6 · 0,98]** — một field duy nhất | giữ | UI hiển thị đúng % |
| **Boss** | `BOSS_ANIM_TIMELINE` (795 event) · `BOSSES` | mốc trong clip mức **A**; điều kiện/chuyển state mức **C** (26 `Stage_Boss`) | thứ tự pha là lựa chọn thiết kế | xem timeline khớp pha |
| **Âm thanh** | `datas/audio_rules.json` (**15 rules**, report 67, PROVISIONAL) | mute/volume ≈0,73/≈0,30 (pool), pause = `AudioListener.pause`, oneshot = pooled, music = `StartSmoothMusic` | map clip ↔ sự kiện; đối chiếu nghe | 1 lần chạy nâng mức |
| **Camera / viewport** | report 77 + **78** peer (`DATA_SYNC` §24.9–24.11) | **ortho = `max(h/w × 5.4f, 9.6f)`** — 9,6 là **sàn**, không cố định; culling mask disjoint Game/UI | chọn viewport/scale | chụp so khung nhìn |
| **UI** | `UI.md` (125 màn hình) · `VISUAL_DESIGN` | luật thị giác **có số**: khung 0,4813 · tương phản 0,45–0,80 · accent ≤10 % | **art vẽ mới** — không bê asset | so khung theo luật |
| **Assets** | pack v2 peer (release `windwings-assets-1.3.118`, report 70) + hợp đồng sprite/scene/font; **pixel tái tạo 2185/2185** (72) · mesh/pivot/PPU/border (75) · scene renderers 1377 (76/77) | identity-safe; đủ làm **reference vẽ** (kích thước + pivot + border từng sprite); **chưa import/render approval**; **cấm bê file về repo này** | vẽ mới theo luật (`ART_STUDY`) + worklist 624 | kiểm theo hợp đồng |
| **Chết — hồi sinh / extra life** | reports **86–87** peer (tip `0561a2185b`, **412 tests**) | hết mạng: hồi **1 s**, KHÔNG full ngay — normal timeScale 0,05 + `HealHp` 0,5 · PVP `HealHp` 1 · zone heal **1,235 % maxHP** sau wait 0,2; **RebornDone** nối Invoke→`RebornDone` (GOT `2ae8560`, `TimeResetInvincible = 3,0` · `TimeCanActiveInvincible = 10,0`); **shield callbacks KHÔNG refcount** — callback(false) khi 3 flag đều false có thể tắt invincible của extra-life (store/order, không refcount); `activeHitEnemey@90` = **tắt enemy-contact hit**, không phải khóa di chuyển (đính chính 85/86) | giữ luật hoặc newdesign có ghi | regression: shield/zone fixtures (`player_shield_models.py`) |
| **Save / meta** | `MISSING` row 9 (schema + flush **scoped unknown**) | chưa chốt — chỉ đào khi task triển khai cần | tự chọn schema | migrate + reload test |

**Bộ 48 câu thiết kế** (`DESIGN_QUESTIONS`, tally ✅ 33 · ⚠ 14 · ❌ 1) trả lời chi tiết hơn bảng này;
bảng này chỉ neo **hợp đồng tối giản**. Chỗ ghi **"scoped unknown"** thì đào khi cần, không đoán.
