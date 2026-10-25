# 65 — Save mở đầu: khóa, cache và getter có side effect

**PROVISIONAL — kiểm chứng tĩnh từ raw APK gốc, không phải save dump/runtime replay.**
Mục tiêu: đưa cho AI viết game một contract cụ thể để dựng first-run/replay/tutorial/progression, thay vì chỉ nói “có save”. Không bóc Premium, IAP, cloud restore hoặc tự chốt schema save cho game mới.

## Đầu ra dùng được

- **`datas/opening_persistence.json`**: contract máy đọc được cho **8 key families**, kiểu lưu/kiểu trả về, default backend, owner/reader/writer, cache, side effect và method IDs làm bằng chứng. Đây là **derived data**, không phải file save thực lấy trên thiết bị; schema_version=1 là version định dạng contract, không phải version save APK.
- **`reverse-engineering/raw/persistence/opening-contracts.json.gz`**: **41 method nguyên thân ASM**, inventories không capped, native calls nối dump, metadata strings nối relocation, field declarations và source SHA256; **25 kiểm tra**.
- Collector `tools/verify/opening_persistence.py`, 8 test mới trong `tests/test_opening_persistence.py`.
- Raw từ các thư mục consts/extra-native có sẵn, **không tải lại APK** và không thay raw bằng prose.

## 1. Bảng khóa — tên thật nối metadata, không đoán từ tên property

Scope default bên dưới: **Application.companyName != "Test"**, backend chưa có key. Nhánh company Test dùng default/debug field riêng; không nhập chung vào cấu hình game mới. Mỗi backend default ở đây là int0, **không đồng nghĩa getter trả0 hoặc không ghi gì**.

| Key / format | Owner và kiểu trả về | Cache | Khi đọc có gì ngoài đọc? |
|---|---|---|---|
| `TUTORIAL` | GP_Tutorials.IndexTutorial → int | indexTut +0x10, sentinel−1 | Đọc StageTarget; nếu target>=2 và tutorial==0 thì cache và ghi **6** |
| `TUT_TOUCH_SKILL` | GP_Tutorials.IsTutTouchSkillDone → bool | Predicate không cache riêng | Trả **stored==1**, không phải stored!=0 |
| `StageTarget` | Stage_Datas.StageTarget → int | stageTarget +0x3C, sentinel−1 | Có nhánh tăng **một bước mỗi lần đọc**, gọi setter lưu lại |
| `ZoneUnlocked` | Stage_Datas.ZoneUnlocked → int | zoneUnlock +0x40, sentinel−1 | Getter đọc cache; setter ghi cache+prefs, không tự clamp trong thân đã đọc |
| `StarStageMaster{stage}_{mode}` | Stage_Datas.GetStarStageMaster → int | Không cache trong getter này | Thứ tự stage rồi `_` rồi mode; đây là saved star count, không phải kills |
| `StarCount` | GameDatas.StarCount → int | starCount +0x4C, sentinel−1 | Đọc Unity PlayerPrefs trực tiếp; tổng sao, không phải sao của riêng màn |
| `DroneUsed{slot}` | Drone_Saved_Datas.GetDroneUsed → int | Không cache trong getter này | Giá trị âm → ghi0 rồi đọc lại. Missing0 **không** tự gắn drone20001 |
| `DroneUnlocked{drone}` | Drone_Saved_Datas.IsDroneUnlocked → bool | Không cache trong getter này | ID20001 có đường tự ghi1; các ID>=20002 yêu cầu stored==1 |

`stage`, `mode`, `slot`, `drone` là **bốn miền tham số khác nhau**. Không đảo key stage/mode; không dùng droneID thay slot hoặc slot thay ID. Literal int→string/Concat và thứ tự stack arg được giữ trong raw.

**Ví dụ:** stage hiển thị2/internal1, mode0 → `StarStageMaster1_0`; drone slot0 → `DroneUsed0`; unlock drone20001 → `DroneUnlocked20001`.

## 2. StageTarget getter không phải truy vấn thuần

Raw `get_StageTarget @12b1f68`:

1. Khi cache ==−1 mới gọi prefs GetInt; normal company!=Test default0.
2. Sau cả cache hit lẫn cache miss, đọc ZoneUnlocked.
3. Nếu `ZoneUnlocked < MAX_ZONE_INDEX` và `target < ZoneUnlocked*10`, **tăng1**, gọi `set_StageTarget` lưu lại.
4. Trả cache hiện hành.

Các lệnh: MAX_ZONE đọc +8 tại `12b20f4`; so zone ở `12b20f8..fc`; nhân10 bằng add/shift ở `12b2120..24`; tăng1 tại `12b2148`; setter tại `12b2150`.

Setter `12bac5c` lấy `MAX_STAGE_INDEX` từ +4, dùng cmp/csel tại `12baccc..d4`, tương đương **min(input, MAX_STAGE_INDEX)** trước khi ghi cache +3C và prefs. Không thấy lower clamp trong thân setter; không tự thêm max(0,…) rồi gọi đó là code gốc. `MAX_ZONE_INDEX=24` được ghi trực tiếp ở cctor `12c548c..9c`; không lấy số ví dụ MAX_STAGE_INDEX trong test làm hằng số APK.

**Ví dụ contract có điều kiện:** zone=2, target0, maxStage đủ lớn → lần đọc1 ghi1, lần đọc2 ghi2; **không** nhảy ngay lên20, cũng không tự loop tới20 trong một lời gọi. Đây là mô hình tĩnh với zone ổn định, số nguyên hợp lệ trong miền thông thường, không phải chứng minh một save/gameplay cụ thể đang ở trạng thái đó.

Hệ quả bàn giao: HUD/debug/log/serializer gọi getter nhiều lần có thể có **observer effect**. Nếu game mới chọn pure getter + explicit migration thì phải ghi là quyết định thiết kế mới, không giả là phục dựng nguyên hàm.

## 3. Tutorial có repair riêng; touch flag không phải tutorial index

`get_IndexTutorial @14f4a14`:
- Cache sentinel−1 mới đọc `TUTORIAL`; normal company!=Test default0.
- **Mỗi lời gọi** tiếp tục đọc StageTarget (`14f4ba8`); nếu target>=2 và cached tutorial==0 thì viết cache6 và `TUTORIAL=6` (`14f4bac..14f4c1c`).
- `set_IndexTutorial` cập nhật cache +10 trước rồi tailcall prefs SetInt (`14f9ff4..14fa020`).

Vì StageTarget cũng có side effect, không đổi thứ tự hai phép đọc này một cách vô thức. Các helper model trong tool nhận StageTarget đã resolve, **không** giả làm toàn bộ call chain/cache engine.

`IsTutTouchSkillDone @14fa7b0`: đọc `TUT_TOUCH_SKILL` default0, so **bằng1** tại `14fa818..1c`. stored2 không được coi done chỉ vì khác0.

Hai đường ghi flag1 đã xác nhận:
- Callback `GP_Tutorials.__c__DisplayClass39_0.<CheckRunTutorialNew>b__1` tại `14fb954..60`.
- Nhánh bypass trong dispatcher `CheckRunTutorialNew` tại `14fa490..4a0` (đọc toàn nhánh talent/điều kiện trong report50/51; không gọi đây là unconditional write).

**Phân biệt gate và completion:** sau khi callback ghi flag1, nó chỉ tăng IndexTutorial nếu **IndexTutorial==2 và Stage_Datas.StageCurrent==2** (`14fb974..14fb9c4`). Hai guard này **không** biến predicate stage3 thành “chỉ chạy khi IndexTutorial2”. Stage3 gate vẫn là stageIndex2 && !touchDone như report64.

## 4. Drone: unlocked không đồng nghĩa equipped

`GetDroneUsed(slotIndex)`:
- Ghép `DroneUsed` + slotIndex.
- Đọc prefs int default0. Nếu số âm thì ghi0, rồi đọc lại default0 (`14dac64..14dacf8`).
- Không kiểm roster/auto-gắn20001 trong getter này. Nhánh Continue có fallback riêng đã bóc ở report51/64; **đừng nhét nó vào getter**.

`IsDroneUnlocked(index)` normal branch:
- ID20001: nếu stored0 thì ghi `DroneUnlocked20001=1`, sau đó trảtrue.
- Index<20002 trảtrue (đó là nhánh native, **không** phải xác nhận mọi số thấp đều là drone hợp lệ!).
- Index>=20002: đọc default0 và trả stored==1.
- Nhánh unlock/Test riêng được giữ ASM, không áp làm luật roster của bản mới.

Setter `SetDroneUsed(slotIndex,index)` ghép key bằng **arg0 slot**, value bằng **arg1 index**; `SetDroneUnlocked(index)` còn có analytics calls trước ghi1. Không suy toàn bộ analytics là yêu cầu bắt buộc của game mới.

## 5. Hai đường persistence khác nhau trong cùng PlayerPreferences

### Typed primitives → Unity PlayerPrefs

Sáu wrapper Set/Get Int/Float/String là các tailcall Unity tương ứng. Ví dụ:

```text
PlayerPreferences.SetInt: 13f1a04 → 277cc10 PlayerPrefs.SetInt
PlayerPreferences.GetInt: 13f1a1c → 277cca0 PlayerPrefs.GetInt
```

Các key ở bảng1 đi qua đường này hoặc gọi Unity trực tiếp (StarCount). Không có đoạn ghi dictionary trong thân các typed wrapper.

### Object dictionary → file custom `/Prefs`

`PlayerPreferences` có **static Dictionary<string,object> dictionary +0x0**; `SetValue/GetValue` dùng nó.

```text
get_path: Application.persistentDataPath + "/Prefs"
SaveToDisk:
  GetRawData → JsonParse.ToJson(dictionary)
  → Encrypt → ASCII encoding → File.WriteAllBytes(path, bytes)
LoadFromDisk:
  nếu file tồn tại: ReadAllBytes → ASCII decode → Decrypt → deserialize dictionary
  nếu thiếu file: tạo dictionary rỗng
```

`GetRawData` lấy field+0 trước gọi ToJson (`13f1b90..13f1ba0`); SaveToDisk đọc raw/Encrypt tại `13f1af8..fc`, lấy ASCII tại `13f1b08`, WriteAllBytes tại `13f1b3c`. File này **không được tự gọi là backup đầy đủ của PlayerPrefs**, không suy rằng nó chứa mọi key trong bảng1. Không khẳng định không có bridge ở nơi khác chưa đọc; các entry đang xét tách biệt rõ.

`Awake` gọi LoadFromDisk; `OnApplicationFocus()` và `OnApplicationQuit()` tailcall SaveToDisk. Chữ ký focus trong dump là **không tham số**; không tự viết thành chỉ-save-khi-focus=false như một APK fact.

**Không có direct PlayerPrefs.Save trong ba thân SaveToDisk/OnApplicationFocus/OnApplicationQuit đã kiểm.** Không biến điều này thành “toàn game không flush” hay “save chắc mất”: đây không phải whole-native closure, engine lifecycle/durability chưa kiểm runtime. Gọi SaveToDisk custom cũng không chứng minh Unity prefs đã flush.

`DeleteKey` chỉ tailcall Unity DeleteKey; không remove dictionary trong thân đã đọc. `DeleteAll` gọi Unity DeleteAll, clear dictionary và SaveToDisk. **Không có bước invalidate cache Stage_Datas/GP_Tutorials/GameDatas trong riêng thân DeleteAll.** Caller có thể refresh ở nơi khác; primitive một mình không đảm bảo cache của profile cũ đã mất.

## 6. Refresh không phải reset profile

- `GP_Tutorials.RefreshDatas`: ghi indexTut−1, không xóa `TUTORIAL`.
- `Stage_Datas.RefreshDatas`: ghi 8 byte toàn1 ở +3C, tức **cả target và zone caches =−1**, không xóa prefs.
- `GameDatas.RefreshDatas`: reset nhiều cache, gồm StarCount+4C.

Sau refresh, getter sẽ đọc lại backend và có thể chạy repair. Sau khi chỉ sửa/xóa key backend, cache hit vẫn có thể giữ giá trị cũ. AI implement cần tách **read / set / invalidate-cache / clear-profile / flush** thành các hành vi rõ ràng, không dùng một nút reset cho tất cả rồi gọi đó là cơ chế gốc.

## 7. Checklist bàn giao và các phần vẫn mở

Có thể dựng các test cho game mới dựa trên contract:
1. Missing key và cache−1: default theo đúng company branch; không gán save0 vào cache mọi frame.
2. StageTarget đọc lặp: test one-step/write guard, không tự loop hay clamp zone ngay lập tức.
3. Tutorial0 + target>=2 → repair6; tutorial1 không bị repair thành6.
4. Touch stored0/1/2, callback write flag độc lập hai guard tăng tutorial index.
5. Stage/mode/slot/drone key không đổi miền/thứ tự; replay không ghi vào key stage khác.
6. Drone thiếu equip →0; unlock20001 không tự equip nó; negative equip repair0.
7. Refresh giữ backend; DeleteAll primitive không hứa reset mọi cache.
8. Custom dictionary và Unity prefs không bị giả làm một store; durability phải test trên platform thật.

**Chưa đủ schema save toàn game:** chưa bóc hết ship equip, rank/cards/talent, nhạc/volume, toàn bộ currencies, cloud/migration, versioned save, corrupt-save recovery, atomicity/crash behavior. Không cần đào Premium để dùng 8 contract này. Ghi rõ những phần đó unknown hoặc là schema mới cần quyết định.

Các test ở đây kiểm pattern/native joins và **partial contract model**, không chạy Unity hay mô phỏng PlayerPrefs platform. Source hash được kiểm trên nội dung giải nén để tránh gzip timestamp/repack làm giả mismatch.

```bash
python3 tools/verify/opening_persistence.py
python3 -m unittest discover -s tests -q
```

Kết quả lượt này: **41 method / 25 checks / 8 key families**, 8 test mới, tổng **135 tests PASS**. Không lấy số PASS làm bằng chứng runtime hoặc “save đã xong toàn bộ”.
