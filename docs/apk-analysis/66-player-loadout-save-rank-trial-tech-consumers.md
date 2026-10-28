# 66 — Save tàu và loadout: equip/unlock, rank/level/cards, tech/talent

**Tạm thời — phân tích tĩnh cùng APK đã ghim; chưa phải replay hay luật thiết kế cuối.**
Ngày 25/10/2026. Tiếp [report65](65-opening-save-keys-cache-and-read-side-effects.md), không thay schema save toàn game.

## 1. Raw mới và cách tái kiểm

Hai lớp thiếu thân native đã được phục hồi **riêng**, không chạy lại full analyze:

- `reverse-engineering/raw/player-loadout/native/Player_Saved_Datas.{asm.txt,json}`.
- `reverse-engineering/raw/player-loadout/native/Player_Device_Saved_Datas.{asm.txt,json}`.
- `array-blobs.json.gz`: token InitializeArray, callsite/allocation length, tên private field, **blob hex nguyên có padding**, ints theo allocation length và length audit.
- `index.json`: SHA256 XAPK, native, metadata, dump và từng output raw. XAPK ghim `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`; native `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`; metadata `449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69`.
- Recovery CI **40192146035 success**, từ commit `a6396f427`, workflow `recover-player-loadout.yml`. Chỉ restore XAPK cached đúng hash, đọc hai input đúng hash, export hai lớp; không tải latest, không commit binary gốc.
- Exporter giữ **mọi method boundary của dump**, chỉ mask tên lớp không chọn để không kéo theo animation families mặc định. Không cắt dump chỉ còn hai lớp làm sai next-method boundary.
- Dùng lại `field_defaults.py` trong scratch tree riêng; không ghi đè global field-defaults pack. Không suy giá trị mảng từ token/native len đơn thuần.

Collector `tools/verify/player_loadout_persistence.py` nối native mới với metadata/relocations/dump đã có và các consumer đã giữ raw:

- `contracts.json.gz`: **33 method không capped, 43 checks, 15 key families**, source hashes, dump fields, direct calls/metadata loads và mảng raw.
- `datas/player_loadout_persistence.json`: contract dẫn xuất, reference/hash raw, reader/writer method IDs, default và giới hạn.
- 10 test mới cho contract, 3 test cho recovery; **148 test toàn repo PASS** khi lập report. PASS chỉ xác nhận sự tái tạo/consistency tĩnh, không chứng minh runtime.

```bash
python3 tools/verify/player_loadout_persistence.py
python3 tools/verify/opening_persistence.py
python3 -m unittest discover -s tests
python3 datas/validate.py
```

`schema_version=1` là version **định dạng contract**, không phải save version của APK. Các khóa dưới đây lưu **int32** qua typed PlayerPreferences → Unity PlayerPrefs, không phải dictionary `/Prefs` của report65. Getter có thể trả bool hoặc mảng dù mỗi giá trị lưu là int.

## 2. Equip/unlock: không hợp nhất thành một trạng thái

### GetPlayerUsed(slot) — `0x14e70a0`

Key `PlayerUsed{slot}`. Default **slot0=10001; mọi slot khác=10002**. Scope runtime caller thường chỉ dùng hai slot0/1; so sánh native không phải validation slot.

```text
value = GetInt(key(slot), slot == 0 ? 10001 : 10002)
if value <= 0:
    SetInt("PlayerUsed0", 10001)
    SetInt("PlayerUsed1", 10002)
return GetInt(key(slot), slot == 0 ? 10001 : 10002)
```

- Missing key không tự viết hai giá trị ban đầu: default đã dương.
- Một slot lỗi có thể **ghi đè slot còn lại** đang equip tàu khác. Ví dụ slot0=10009, slot1=0 → đọc slot1 làm hai key thành10001/10002.
- ID dương bất kỳ được trả ra trong routine này; không suy là tàu hợp lệ/unlocked.
- `SetPlayerUsed` `0x14e73bc` chỉ ghi key/value trong body đã giữ; không có unlock check, duplicate check hay reset gameplay cache ở đây.

`CheckDoubleIDShip` `0x14e7464` là routine **riêng**: đọc slots0/1; nếu trùng, duyệt danh sách tàu từ consumer và tìm tàu unlocked khác slot1, sau đó **đổi slot0**, không đổi slot1. Nếu không tìm thấy thì body trở về không sửa. Không tự nhét luật này vào mọi setter.

### IsPlayerUnlocked(ship) — `0x14e24fc`

Nhánh **không Test-cheat và không Premium**:

- `ship<10003` → true. Đây là so sánh ID rộng, **không phải roster membership** và không tự viết unlock flag cho10001/10002.
- `ship>=10003` → `GetInt("PlayerUnlocked"+ship,0)==1`, không phải `!=0`.

Có nhánh Test và Premium trong body raw nhưng **không phục dựng Premium ở report này**. `SetPlayerUnlocked` `0x14e729c` có analytics/log/LastShipUnlocked trước write1; analyser null có đường throw. Không coi nó là một setter flag thuần hay giao dịch atomic.

## 3. Rank, level và trial là hai tầng

| Key | Default normal | Body đọc/ghi |
|---|---:|---|
| `PLAYER_RANK{ship}` | 2 | GetPlayerRank `14e6d74`, SetPlayerRank `14e76a8` |
| `PLAYER_LEVEL{ship}` | 0 | GetPlayerLevel `14e3b20`, SetPlayerLevel `14e7600` |
| `TRIAL_ID_{ship}` | 0 | Cả hai getter trên; chỉ **==1** mới chọn trial |
| `TRIAL_RANK_{ship}` | 0 | GetPlayerRank; GP_Loader còn đọc trực tiếp khi ship chưa unlocked |
| `TRIAL_LEVEL_{ship}` | 0 | GetPlayerLevel |
| `PLAYER_CARDS{ship}` | 0 | GetPlayerCards `14e7948`, SetPlayerCards `14e7a88` |
| `PLAYER_DEFAULT_SKIN{ship}` | −1 | GetPlayerDefaultSkin `14e77fc`, SetPlayerDefaultSkin `14e78a0` |

Thứ tự GetPlayerRank:

1. Đọc **base** rank default2. Nếu base<=1, **viết base=2**.
2. Đọc TRIAL_ID default0.
3. Nếu trial flag==1, trả **trial rank default0**; không thì đọc base rank default2.

Vì vậy getter có thể vừa repair base thành2 **vừa trả0 hoặc giá trị âm từ trial**. Không viết mô hình `max(2, trial-or-base)` rồi gắn nhãn là getter gốc. Base rank lớn hơn6 cũng không bị getter này cap.

GetPlayerLevel đọc flag rồi chọn `TRIAL_LEVEL_` hoặc `PLAYER_LEVEL`, đều default0; không có rank-style repair ở body này. Trial flag2/−1 không bật trial. Writer/expiry/lifecycle của trial **chưa bóc**, không suy từ IsPlayerUnlocked.

Cards default0 chỉ với company!=`Test`. Nhánh Test lấy missing-default từ CheatGameInfo static+0x24; không phải luôn ghi đè số cards đã lưu. Level/cards setters đã đọc không tự clamp số âm hay giới hạn rank. Rank setter còn có reset offer/analytics side effect, không phải chi phí nâng cấp/đảm bảo giao dịch đã hoàn tất.

### Mảng .cctor — decoded từ metadata, nối đúng static field

`Player_Saved_Datas.cctor` `0x14e8110`:

| Field/offset static | InitializeArray callsite | Giá trị theo allocation length |
|---|---|---|
| MaxLevelPerRanks +0x0 | `14e81b0` | `[10,20,30,60,120,250,500]` |
| CardUpgrades +0x8 | `14e81d8` | `[0,20,50,80,250,500,800]` |
| StartRanks +0x10 | `14e8200` | 24 phần tử, tất cả2 |

Store lần lượt `14e81c0`, `14e81e8`, `14e8214`, khớp field offsets từ dump. Token → private implementation field cùng image → raw blob; bỏ padding chỉ ở ints dẫn xuất, **không xóa padding raw**. `get_MAX_RANK_INDEX` `14e6d0c` trả `MaxLevelPerRanks.Length−1` → **6**. Không suy bảng tự enforce cap, không suy24 phần tử là24 tàu unlocked, không tự gán “tổng card đã tiêu” hay quy trình thanh toán từ riêng mảng này.

## 4. Đường vào gameplay khác giá trị save

### GP_Setup.get_indexPlayers `0x14f2678`

Nhánh normal tạo mảng2, đi `GetPlayerUsed(0)` rồi `GetPlayerUsed(1)`. Có instance initialization flag và static cached array; **không đọc lại saved equip mỗi lần getter được gọi**. Mode4 có nhánh lấy slot đầu từ state mode riêng; slot thứ hai vẫn đi saved reader. `set_indexPlayers` cũng giữ raw. Chưa dựng toàn lifecycle refresh/switching, không coi saved setter là tự cập nhật trận đang chạy.

### GP_Loader.LoadObjects `0x14f2094`

Dùng ship IDs từ setup để nạp object; tại đoạn chọn rank:

- `IsPlayerUnlocked(id)` true → `GetPlayerRank(id)`.
- false → đọc trực tiếp `TRIAL_RANK_{id}` default0.
- Sau đó **effective rank floor2** tại `14f238c..14f2394`.

Đây là floor **ở loader**, không phải getter hay migration save. Loader còn đọc default skin; sentinel−1 chọn đường skin theo default/rank. Không thay sentinel bằngskin0. Full skin prefab/rank mapping và toàn chuỗi stat initialization không được đóng gói lại ở slice này.

## 5. Tech, device và talent: không dùng cùng sentinel

| Key | Default | Native saved reader |
|---|---:|---|
| `PlayerStatPoints{stat}` | 0 | GetTechStatPoints `14e7d94` |
| `PlayerStatLevel{stat}` | 0 | GetTechStatLevel `14e7ee0` |
| `TECHLAB_LV` | 0 | GetTechLabLevel `14e802c` |
| `PLAYER_DEVICE_{ship}_{slot}` | −1 | GetPlayerDevices `14e628c`, bốn slot0..3 |
| `FIRST_INSTALL_DEVICE` | 0 | Đọc nội bộ trong SetPlayerDevices `14e64a4`, không có getter riêng ở contract |
| `TALENT_SELECTED` | −1 | Board_Talents.get_GetTalentIndex `1397438` |

- Saved tech getters/setters là raw integer trong những body này. `Tech_Datas.GetTechStatLevel` `139d96c` là **wrapper gameplay**: mode4 **và** active scene tên `Game` → trả0, không đọc saved level; còn lại đi saved reader. Không xóa level đã mua khỏi save khi vào mode này.
- `Player_Get_Datas.GetMainCannonRatePercent` `14e3d6c` gọi effective stat**1**. Native branch constants giữ trong JSON; không phát minh công thức linear từ tên hàm.
- `GetMaxCountRockets` `14e5380` gọi stat**5** và branch tĩnh: level<=0→7;1..5→8;6..8→**3**;>=9→10. Giá trị **không đơn điệu** được giữ nguyên và có test. Không “sửa đẹp”3 thành9; chưa có replay để giải thích đường này.
- Devices: mode4 **và** scene `Game` → mảng mới `[-1,-1,-1,-1]`, không phải đổi saved slots. Nhánh khác đọc bốn key riêng default−1. Setter lặp **đúng bốn**, không theo độ dài input: array ngắn có thể đã ghi một số key rồi bounds fault; không có atomicity được chứng minh. `FIRST_INSTALL_DEVICE` chỉ được set1 sau event feature0 khi có ít nhất một giá trị!=-1 và flag cũ0.
- Talent selection khác tech level. Board_Talents.OnClickTalent có đường persist selection; startup callback `Player_Talent.<Start>b__8_3` `14bf3b8` đòi `StageTarget>=Board_Begin.stageUnlockTalents` (static+0x4), đòi selection!=-1, mode!=4, rồi mới chép index vào component+0x28. Raw có cả đường disable object. Report này **không gán số cho stage threshold** chưa nối value (cctor nạp SIMD rodata, không đoán từ tên field); StageTarget read còn có side effect như report65.

## 6. Cách AI triển khai nên dùng và phần còn mở

**Có thể dùng ngay làm contract tham khảo:** exact key/case/underscore, default theo scope, rank base-vs-trial, các write-on-read, mảng rank có binding, distinction saved/effective/cached values và consumer IDs có raw.

**Không được tự nâng thành fact:**

- schema/version/migration/cloud save đầy đủ; first-install profile số dư đã chạy thật;
- toàn economy/upgrade payment, trial grant/expiry, offer hay Premium;
- auto refresh mọi cache khi setter chạy, mọi stat/combat formula và full skin mapping;
- mọi ID dưới threshold đều là roster hợp lệ;
- runtime correctness hay ý đồ thiết kế chỉ từ test tĩnh.

Đề nghị peer cập nhật spec phần save/loadout theo report65–66, giữ riêng bốn lớp `saved`, `trial override`, `effective gameplay`, `cached loadout`. Nếu bản game mới chọn sửa branch bất thường hay thêm validation/atomic save, ghi **new design**, không gắn nhãn APK fact.

Full asset pack/audio/spine/font browsing/validation và audio trigger rules vẫn còn mở. Không dùng việc thiếu chúng làm cớ chạy lại toàn APK, không quay lại speculative pool-history/BB-death hoặc Premium.
