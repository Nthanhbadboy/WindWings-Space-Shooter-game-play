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
> **Cách dùng:** cột "Luật đã chứng minh" — làm theo là xong, bản gốc đã trả lời; cột "AI tự chọn"
> chỉ vài dòng. Phần thiết kế thật sự của project = **art** (`VISUAL_DESIGN.md`).

| Hệ thống | Raw / hợp đồng (nguồn) | Luật triển khai **đã chứng minh** | AI game mới **tự chọn** | Test nghiệm thu |
|---|---|---|---|---|
| **Player — 6 mảng stat** | `datas/player_start_stats.json` ← `ia-resolved.json` (claim IA2); combat hợp đồng `combat_chain_contract.json.gz` (peer, report 81/82) | save/load: **id − 10001**; **combat: impl N → index N−1** — tàu 10001→2 · 10003→0 · 10004+→id−10001; 24 tàu · 16 bán · 8 giá `−1` | giữ hoặc vẽ lại đường cong | unit test 24 cặp giá trị |
| **Player — nhịp bắn** | reports 79–83 peer (`23b1ceec31`, đủ **24/24** impl) | `rate` = **interval nhóm phát**: `base × (1 − tech tier 0/3/5/8/10/12 %)`, dual deadline, N extra ⇒ **N+1** entry, không catch-up, demo override 3,0/4,0; **`damage × rate` KHÔNG phải DPS** — crit `random ≤ critPercent` ⇒ ×2 trong callback | phát phụ/nòng đã có luật (report 80 §4); `newdesign` nếu thêm catch-up / bỏ extra gate / gộp nòng; DPS runtime còn health/shield gates (nhánh dữ liệu) | replay: đếm entry emitter/nhóm |
| **Player — HP** | `BALANCE` §0.6 (claim B2 mức A) | `HPmax = 2500 × (1 + 0,18×Tech(0) + abi7×…)`; giáp tách riêng | giá trị khởi đầu mỗi cấp | so HP đúng mốc cấp |
| **Enemy — HP** | `datas/enemy_hp_by_id.json` (**150 cặp**, WRH2) | dict theo **id** dựng ở `.cctor`; **`kHp[mode]` không tồn tại**; mất máu: `factor = 100/(100+armor)` (armor<0 ⇒ `2−100/(100−armor)`), overkill clamp 0, gate `IsCaAttack@0x2F` (report 81 §E); `noDamage` 241/981; **Shield_Sub không dùng công thức này** | dải HP theo mode + giá trị armor runtime | kill-count theo mode |
| **Wave / spawn** | `waves.json` (`Call_Data` 23 field) · report 53 | `rate` = **delay nhánh Path/Waypoints** (giây); `number = 0` ⇒ số quân = độ dài list; spawn `y = 9,6` | chọn phân bố điểm/range | replay 1 wave: đúng số quân |
| **Map → wave** | `DIFFICULTY_MODES` §7 (11 cấu trúc/614 mảng) + peer `maps.json` | `GetListWaves(mapIndex)`; len2 = stage→boss (giải thích 299/281) | số màn/độ dài phiên (`A5` cần luật continue) | mở đủ từng stage |
| **Độ khó (mode)** | `DIFFICULTY_MODES` §3–5 · `MaxModeIndex` 4 | mode đổi **composition + thưởng** (`levelDelta = [1,2,3.6,3.6]`), **không nhân HP** | hệ số riêng nếu muốn | A/B 3 mode |
| **Kinh tế** | `ECONOMY` §8.1 + mẫu runtime 23/10 | `GetBonusCoin` **100,0 · 20,0**; mẫu Stage 1 ≈ **2 coin/kill** (276 kill → 540 coin) | tỉ lệ rơi (D3), giá talent | đo coin/phiên |
| **Mission %** | `PercentToCompleteMissions222` float[3] `@0x308` | **[0,2 · 0,6 · 0,98]** — một field duy nhất | giữ | UI hiển thị đúng % |
| **Boss** | `BOSS_ANIM_TIMELINE` (795 event) · `BOSSES` | mốc trong clip mức **A**; điều kiện/chuyển state mức **C** (26 `Stage_Boss`) | thứ tự pha là lựa chọn thiết kế | xem timeline khớp pha |
| **Âm thanh** | `datas/audio_rules.json` (**15 rules**, report 67, PROVISIONAL) | mute/volume ≈0,73/≈0,30 (pool), pause = `AudioListener.pause`, oneshot = pooled, music = `StartSmoothMusic` | map clip ↔ sự kiện; đối chiếu nghe | 1 lần chạy nâng mức |
| **Camera / viewport** | report 77 + **78** peer (`DATA_SYNC` §24.9–24.11) | **ortho = `max(h/w × 5.4f, 9.6f)`** — 9,6 là **sàn**, không cố định; culling mask disjoint Game/UI | chọn viewport/scale | chụp so khung nhìn |
| **UI** | `UI.md` (125 màn hình) · `VISUAL_DESIGN` | luật thị giác **có số**: khung 0,4813 · tương phản 0,45–0,80 · accent ≤10 % | **art vẽ mới** — không bê asset | so khung theo luật |
| **Assets** | pack v2 peer (release `windwings-assets-1.3.118`, report 70) + hợp đồng sprite/scene/font | identity-safe; **chưa import/render approval**; **cấm bê về repo này** | vẽ mới theo luật (`ART_STUDY`) | kiểm theo hợp đồng |
| **Save / meta** | `MISSING` row 9 (schema + flush **scoped unknown**) | chưa chốt — chỉ đào khi task triển khai cần | tự chọn schema | migrate + reload test |

**Bộ 48 câu thiết kế** (`DESIGN_QUESTIONS`, tally ✅ 33 · ⚠ 14 · ❌ 1) trả lời chi tiết hơn bảng này;
bảng này chỉ neo **hợp đồng tối giản**. Chỗ ghi **"scoped unknown"** thì đào khi cần, không đoán.
