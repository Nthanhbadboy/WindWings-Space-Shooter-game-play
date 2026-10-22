# Phân việc vòng 2 — WindWings RE

> **Vòng 1 đã xong**: `docs/spec/{GAMEPLAY,UI,ASSETS,BALANCE}.md` + `screens.csv` + `sprite-list.csv`
> (nhánh `arena/20330d0e`, đã merge vào `arena/ef6b75ef`).

## Luật chơi

1. **Nguồn sự thật duy nhất** = file dữ liệu sinh trực tiếp từ APK:
   `docs/apk-analysis/*.csv`, `datas/*.json`, `reverse-engineering/scriptableobjects/*.csv`.
   **Không** trích dẫn lại `PHAN_TICH_WINDWINGS_APK.md`, `probe-results.md`, `HANDOFF_AI_TASKS.md`
   hay bất kỳ tài liệu tóm tắt cũ nào — số trong đó có thể đã lỗi thời.
2. Đọc thêm trong `docs/spec/` (vòng 1) để giữ giọng văn, nhưng **mọi con số phải kiểm lại**
   từ CSV. Chỗ nào vòng 1 nói "không có số" mà giờ đã có → sửa lại.
3. Chỉ ghi trong `docs/spec/`. Không sửa `datas/`, `tools/`, `.github/`, `docs/apk-analysis/`.
4. Mỗi bảng ghi `(nguồn: <file>)`. Suy đoán ghi `> Giả định:`. Không bịa.
5. Không commit ảnh/audio/APK. PR riêng, tiêu đề `docs(spec2): ...`.

## Việc cần làm

### 1. `docs/spec/COMBAT.md` — súng, damage, TTK

Nguồn: `reverse-engineering/scriptableobjects/Gun_Attack.csv` (458 súng),
`docs/apk-analysis/Gun_Attack.csv`, `Bullet_Linearly.csv`, `Enemy_Health.csv`,
`docs/apk-analysis/15-enemy-hp.csv`.

- Phân bố `bltDamage`: min 40, max 1200 — vẽ histogram theo khoảng 50.
- `gunType` (0/1/2/3) + `forceType` + `shootAudioClipName` → phân loại vũ khí.
- Bảng "súng của boss": nhóm theo `_gameobject` root (`Boss-37001`…), lấy damage cao nhất.
- `allGunDatas[]`: `countShots / timeShot / timeReload / timeRounds / countMags` → burst pattern,
  tính **DPS lý thuyết** = damage × shots / chu kỳ.
- `bltSpeed`, `bltLifetime` → tầm bắn.
- Ghép với HP: bảng **TTK** (thời gian giết) cho 5 mốc HP phổ biến.
- `Enemy_Health.armor` (`noDamage`) — có bao nhiêu enemy có armor, giá trị nào.

### 2. `docs/spec/ENCOUNTERS.md` — 282 wave

Nguồn: `datas/waves.json` (282 wave, spawner đã dedupe + tên enemy),
`docs/apk-analysis/Call_Data.csv`, `MapController.csv`, `Stage_Behaviour.csv`.

- Bảng tổng: số wave, số spawner/wave (min/median/max), phân bố `spawn_type`
  (`point_range`, `point`, `path`, `special`, `boss`).
- Danh mục enemy: prefab nào xuất hiện ở bao nhiêu wave, wave đầu/cuối.
- Trích 10 wave tiêu biểu (đầu game, giữa, boss wave) — mô tả bằng số.
- `Wave.csv` (`indexWave`, start/end point) → wave nối tiếp nhau thế nào.
- Ghi rõ: tên prefab còn `pathID:` nghĩa là prefab nằm ngoài `data.unity3d`.

### 3. `docs/spec/ECONOMY.md` — phần thưởng & shop

Nguồn: `docs/apk-analysis/Box_Rewards.csv`, `Shop_Cell.csv`, `Sub_Item.csv`,
`Item_Movement.csv`, `DataShopPack.csv`, `RankManager.csv`, `Tech_Ability_Data.csv`.

- `Box_Rewards`: loại hộp, số lượng phần thưởng, tỉ lệ nếu có.
- `Shop_Cell`: cell nào bán gì, `PurchaseType` nào (`Free/Pro/IAP/IAPBeginner/Gem/Coin`),
  giá nằm ở field nào (ghi rõ field và đơn vị nếu suy ra được).
- `Sub_Item`: 6 item rơi × hiệu ứng (`+1Level`, `Fullpower`, `+Hp`, `Droid-1..3`).
- `DataShopPack`: 69 cột — nhóm thành pack, ghi rõ cột nào là sprite (bỏ qua) cột nào là số.
- Kết luận: **cái gì là số thật, cái gì chỉ là id/sprite** — đừng gán giá trị kinh tế không có.

### 4. Sửa lại vòng 1 cho khớp dữ liệu mới

- `BALANCE.md` §0 đang ghi *"0 giá trị damage/giá/thưởng"* → **sai**: đã có 458 damage,
  `Box_Rewards`/`Shop_Cell` có thưởng. Cập nhật §0, §1, §6.
- `BALANCE.md` §6 "phần 2 đi tìm" → gạch những mục đã tìm được, giữ mục còn thiếu thật
  (`Player_Get_Datas`, `Droid_Data_Balance`, `Tech_Datas`, `Stage_Get_Datas`, `Map_Get_Datas`,
  `Enemy_Data_Balance`, `Device_Get_Data`, `GameDatas` — các class này **không được serialize**
  trong `data.unity3d`, phải decompile `libil2cpp.so`).
- `GAMEPLAY.md` / `UI.md` / `ASSETS.md`: bỏ mọi tham chiếu tới file tóm tắt cũ; thay bằng nguồn CSV.

## Tiêu chí xong

- 3 file mới + 4 file cũ đã cập nhật, mọi bảng có `(nguồn: …)`.
- Không còn câu nào khẳng định "không có số" nếu CSV đã có số đó.
- Mỗi file kết thúc bằng "Còn thiếu / phải đoán" chỉ liệt kê cái **thật sự** thiếu.
