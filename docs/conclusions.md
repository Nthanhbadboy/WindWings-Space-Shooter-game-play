# Kết luận — trạng thái và độ tin cậy

> **Mọi kết luận trong repo này là TẠM THỜI.** Mỗi lần pipeline chạy lại, số liệu có thể đổi
> (đổi version APK, đổi backend typetree, sửa parser). File này là sổ đăng ký: kết luận nào,
> lấy từ đâu, độ tin cậy bao nhiêu, và **cách kiểm lại**.
>
> Quy ước độ tin cậy:
> - **A — đo được**: đọc trực tiếp từ dữ liệu serialize (CSV/JSON trong `datas/`, `docs/apk-analysis/`).
> - **B — suy ra**: tính từ dữ liệu A bằng công thức/cách gom nhóm đã ghi rõ.
> - **C — giả định**: suy luận thiết kế, chưa có dữ liệu chống lưng.
>
> Kết luận C **không được** dùng làm thông số implement; chỉ để định hướng.

## Đăng ký kết luận

| # | Kết luận | Mức | Nguồn | Kiểm lại bằng |
|---|---|---|---|---|
| 1 | Build Unity 2022.3.62f3, IL2CPP, metadata v31, arm64 | A | `02-unity-engine.md`, `01-apk-inventory.json` | `gh workflow run analyze-apk.yml` → xem `02` |
| 2 | 3.662 type, 2.095 class gameplay, 255 enum | A | `03-il2cpp.md`, `07-enums.md` | đếm lại từ `dump.cs.gz` |
| 3 | 25 tàu (10001–10024 + 10999), 13 drone, 46 wave-boss, 6 item | A | `14-*.csv`, `datas/*.json` | `datas/validate.py` |
| 4 | 1.416 key × 19 ngôn ngữ, có tiếng Việt | A | `12-localization.csv` | đếm dòng CSV |
| 5 | 170 product IAP (99 non-consumable + 71 consumable) | A | `13-iap-products.csv` | `datas/iap_products.json` |
| 6 | 981 `Enemy_Datas`, HP serialize 0–10.000.000 | A | `15-enemy-hp.csv` | `reverse-engineering/raw/typetrees/Enemy_Datas.jsonl.gz` |
| 7 | Boss chương 1 = idWave 7001–7022, chương 2 = 9001–9024 | A | `14-bosses.csv` | cùng file |
| 8 | 282 wave, ~11k spawner, enemy prefab theo tên thật | A | `datas/waves.json` | đọc `raw/typetrees/Call_Data.jsonl.gz` |
| 9 | 458 súng, damage 40–1200 | A | `Gun_Attack.csv` | `raw/typetrees/Gun_Attack.jsonl.gz` |
| 10 | 69 AudioClip tổng ~571 giây, dữ liệu thật trong `resources.resource` | A | `17-audio-diagnose.md`, `assets/audio-index.csv` | release `windwings-assets-1.3.118` |
| 11 | 2.185 sprite + 653 texture, 46 board / 63 popup | A | `04-asset-manifest.csv`, `08-ui-map.md` | `docs/assets/manifest.csv` |
| 12 | Hằng số trong thân hàm: **12 class, 305 method** (GameDatas 73, Player_Get_Datas 62, IAP_Manager 35, ArenaManager 34, Tech_Datas 25…) | **B** | `19-il2cpp-constants.md`, `raw/il2cpp-consts/*.json` + `.asm.txt` | đọc `.asm.txt`, đối chiếu control flow; hằng số có thể là epsilon/clamp chứ không phải giá trị thiết kế |
| 12b | **Hằng số float/int đọc trực tiếp từ literal pool `.rodata`** (`adrp`+`ldr` → VA → offset qua `PT_LOAD`): hệ số thật như `GetBaseDamage` 0.6, `GetBonusCoin` 0.1, `GetWingCannonDamage` 0.168→0.1764→0.1932 (tăng 1.05×/cấp), `GetTechStatUpgradePrice` 0.86/0.689, `GetPlayerUpgradePrice` 0.12 + trần 150000. Đây là byte có thật trong file, không phải suy luận | **A** (giá trị) / **B** (ý nghĩa) | `19-il2cpp-constants.md` mục "Float đọc từ literal pool" | đọc lại `.so` tại đúng VA đã ghi |
| 12c | Getter **không** trả hằng số: 176 getter đã phân loại → 8 `const`, 23 `field`, 29 `computed`, 94 `call`. Bảng cân bằng nằm trong dữ liệu, không hard-code trong getter | **A** | `19-il2cpp-constants.md` mục "Getter: trả hằng số hay đọc dữ liệu?" | chạy lại `il2cpp_consts.py`, xem cột `getter_kind` trong JSON |
| 13 | Layout từng màn: **608 màn, 80.806 node**, có `local_pos`/`scale`/`rotation`, class component, text + nút | **B** | `20-ui-layout.md`, `raw/ui/*.json.gz` (584 file) | so với screenshot; layout group có thể override |
| 13b | UI của game là **SpriteRenderer world-space**, không phải Canvas/RectTransform (chỉ 1 `Canvas` trong toàn build) | **A** | `20-ui-layout.md` (bảng component) | đếm lại `Canvas`/`RectTransform` trong raw |
| 13c | **Spine: 27 rig / 185 animation / 12.274 keyframe**, thời lượng thật từng anim, 21 event (`Shot` đúng 0.3333 s trong 12 anim đánh, boss `Attack3` có `Stop` tại 0.63/3.3/5.87/8.2 s) | **A** | `23-spine-anim.md`, `datas/spine_anim.json.gz`, `spine-events.csv` | `python3 tools/apk-analyze/spine_anim.py` |
| 14 | Damage/giá/thưởng suy ra từ field serialize | **B** | `docs/spec/COMBAT.md`, `ECONOMY.md` | so với hằng số ở #12 |
| 15 | Nhận định "game dễ bypass", "nên dùng Spine"… | **C** | `PHAN_TICH_WINDWINGS_APK.md` | chỉ là đánh giá, không phải số |

## Những gì **chưa** bóc được (còn thiếu thật)

| Thiếu | Vì sao | Cách làm tiếp |
|---|---|---|
| `Player_Get_Datas`, `Droid_Data_Balance`, `Tech_Datas`, `Stage_Get_Datas`, `Map_Get_Datas`, `Enemy_Data_Balance`, `Device_Get_Data`, `GameDatas` | **0 instance** trong `data.unity3d` → giá trị nằm trong thân hàm IL2CPP | `19-il2cpp-constants.md` + `raw/il2cpp-consts/*.asm.txt` (đang làm) |
| Công thức đầy đủ (thứ tự nhân, clamp, nội suy) | cần đọc control flow, không chỉ hằng số | Ghidra/IDA trên `libil2cpp.so` (đã có trong artifact) |
| Ý nghĩa từng hằng số ở #12 | capstone chỉ thấy số, không thấy phép tính | **Đã bóc được giá trị float thật từ literal pool** (#12b); còn thiếu *thứ tự nhân/chia* → đọc `raw/il2cpp-consts/*.asm.txt` hoặc Ghidra |
| Layout runtime thực tế | prefab ≠ runtime (layout group, safe area) | screenshot + so với `raw/ui/` |
| Hiệu ứng/particle cụ thể | `ParticleSystem` chưa dump | mở rộng `unity_data.py` sang ParticleSystem |
| Logic PvP/Arena server | nằm ở Firebase, **không có trong APK** | không lấy được |
| Spine animation curve | **đã xong** — `23-spine-anim.md` + `datas/spine_anim.json.gz` (12.274 keyframe) | còn thiếu `timeScale` runtime |

## Cách giữ cho kết luận không bị "chết cứng"

1. Dữ liệu thô luôn nằm trong `reverse-engineering/raw/` (JSONL gzip, **không cắt field**).
2. Mọi bảng tóm tắt đều sinh lại được từ thô bằng script trong `tools/apk-analyze/`.
3. Khi sửa parser, chạy lại pipeline rồi `git diff` — chênh lệch chính là chỗ kết luận cũ sai.
4. Đừng xoá file thô để "cho gọn": nếu thiếu dung lượng thì nâng cap trong workflow, không xoá.
