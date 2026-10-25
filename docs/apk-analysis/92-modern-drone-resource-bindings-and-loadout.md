# 92 — 12 modern drone: save → getter → resource → prefab → class/serialized fields

**Tạm thời, chỉ áp dụng APK đã pin.** Batch này trả lời ba việc spec ACK90/91 yêu cầu:
sourceID thật của modern drone, actual loadout/resource loader và `Drone_Attack3.turnRate`
serialized. Không dùng suffix lớp để đoán ID, không lấy constructor thay prefab,
không dùng UI damage xác nhận combat. ACK90/91 đã nhận: PR12 comment6401051274.

## 1. Nguồn và kiểm chứng

- XAPK SHA256 `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`.
- `data.unity3d` SHA256 `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7`.
- Native/metadata: `raw/drone-loadout/{index,cells}.json`, native GP_Loader,
  GP_Setup, Drone_Saved_Datas. CI **40219444444 SUCCESS**.
- Serialized: `raw/drone-prefabs/{component-index.json,components.json.gz,resource-managers.json.gz}`.
  CI **40219666819 SUCCESS**. Snapshot retains the ResourceManager **m_Container section**,
  external-file table and dependency-entry count, not its unrelated 703606-entry dependency array.
- 125453 MonoBehaviour headers scanned; 37 selected records = GP_Loader + 36 modern drone instances.
  Selected records **không lỗi**. Four retained scan warnings: three null TMPro resource pointers,
  one header cannot resolve `unity default resources` (pathID580792). Không xóa warning để coi green
  CI là chứng minh scan tuyệt đối; 12 bindings dưới đây có pointer/object proof riêng đầy đủ.
- Contract `datas/drone_loadout_flow.json`; verifier `tools/verify/drone_loadout_flow.py`:
  **5 method ranges / 319 instructions, 29 exact anchors, 4 RELA→symbol joins**;
  2 encoded metadata string joins; 36 serialized IDs cross-checked against raw object bytes.
  ResourceManager external file #3 resolves to `resources.assets`, không nối bằng pathID trần.
- 35 tests mới PASS; full **683 tests PASS (42.905s)**; `datas/validate.py` PASS.
  Fixtures là mô hình hành vi bounded, không phải Unity replay/FPS/DPS benchmark.

## 2. Resource-backed identity — đủ 12 modern source IDs

`GP_Loader.StartDrones14f2864` ghép literal **`Prefabs/Drones/Drone_`** với ID thập phân.
GOT2adf0e0 → relocation → encoded usage5 → string definition/data bytes, không đoán prefix.
Generic method-info GOT2adbac8 = `Resources.Load<GameObject>()`; GOT2adbac0 =
`Object.Instantiate<GameObject>()`, lần lượt đưa vào calls174a654/173efb4.

ResourceManager keys lưu lowercase. Mỗi key dưới đây trỏ root GameObject thật;
MonoBehaviour cùng root chứa cả `m_Script` đã resolve sang MonoScript class và serialized `id`.
Đây mới là binding, không phải quy tắc tự suy suffix→ID.

| ID | Resource key (sau `prefabs/drones/`) | Root GO pathID | Component pathID | MonoScript class |
|---:|---|---:|---:|---|
|20001|drone_20001|26348|694706|Drone_Attack1|
|20002|drone_20002|26345|621213|Drone_Attack2|
|20003|drone_20003|26346|627384|Drone_Attack3|
|20004|drone_20004|26344|590281|Drone_Attack4|
|20005|drone_20005|26347|663701|Drone_Attack5|
|20006|drone_20006|137982|606560|Drone_Attack6|
|20007|drone_20007|137986|630501|Drone_Attack7|
|20008|drone_20008|137981|694277|Drone_Attack8|
|20009|drone_20009|137985|605005|Drone_Attack9|
|20010|drone_20010|137984|685357|Drone_Attack10|
|20011|drone_20011|137983|674069|Drone_Attack11|
|20012|drone_20012|137987|628627|Drone_Attack12|

Tất cả trên thuộc `data.unity3d/resources.assets`. Mỗi class có thêm **hai bản UI**:
ancestry root `boards/board_drones` và `boards/popup_common/popup_newdrone`, mỗi bản cũng có
serialized ID đúng. Contract giữ riêng cả ba context/pathIDs, không lấy demo UI thay gameplay
prefab. Năm legacy `Droid_Attack*` không phải bộ 12 modern này.

Binding này cho phép áp implementation laws report90 lên đúng source IDs. Không biến nó thành
claim mọi đường spawn toàn chương trình đã audit, hay claim screenshot build khác tương đương.

## 3. Drone3: serialized turnRate = **1.0f**, không phải ctor8

Gameplay component627384, GO26346, raw object124 bytes:

| Raw object byte offset | Giá trị |
|---:|---|
|32|id = 20003|
|84|barrels length = 1|
|100|turnRate = **1.0f**, bytes `0000803f`|
|104|shotRate = 2.0f|
|108|shotSpeed = 24.0f|
|112|idBlt = 80084|
|116|turnNumber = 3|
|120|damage = 0.0f|

Cả hai bản UI của Drone3 cũng turnRate1, nhưng kết luận gameplay dựa bản resource riêng.
Report90 đã chứng minh `Drone_Attack3.OnEnable` **không ghi turnRate**, do đó constructor8
không thay được serialized1. Theo scheduler90, khi counter đạt turnNumber thì chargeDeadline
được ghi `now + turnRate`, ở prefab này là `now + 1`; đây không phải kết luận DPS hay frame count.

**Không bê toàn bộ serialized fields vào runtime:** ví dụ Drone3 serialized idBlt80084 nhưng
OnEnable90 cấu hình idBlt80014; Drone4 serialized turnRate1 nhưng OnEnable ghi0; Drone8/11/12
có nhiều serialized field0 nhưng OnEnable cấu hình lại. Rate ability25 vẫn theo90:
`baseRate / f32(2.5f * ability25_read_again)`, không thêm1 vào mẫu số; Drone3 chỉ điều chỉnh shotRate,
không điều chỉnh turnRate. Drone9 gameplay serialized width10 cũng được bóc, không còn chỉ ctor.
Contract lưu toàn bộ selected serialized field tree để đối chiếu cụ thể, không coi chúng đều sống nguyên.

## 4. Saved slots → getter mới mỗi lần, không cache

### Saved data

- `GetDroneUsed14dabd4(slot)` tạo key **`DroneUsed` + slot.ToString()**.
  Đọc `PlayerPreferences.GetInt(key,0)`; nếu âm thì `SetInt(key,0)`; **đọc lại GetInt(key,0)** rồi trả về.
  Key literal GOT2adc180 cũng có encoded literal proof. Mặc định là **0 = không drone**, không 20001.
  Không ép giá trị dương vào 20001..20012 trong method này; không khóa slot vào0/1.
- `SetDroneUsed14db228(slot, playerIndex)` chỉ ghi cùng key với giá trị argument thứ hai.
  Tên parameter `playerIndex` không đủ để coi đó là player implementation index:
  actual consumer dùng giá trị làm drone resource ID. Setter không tự dedup/clamp.
- `CheckDoubleIDDrone14db2d0` là routine **riêng**, không được nhét vào setter/loader:
  nếu hai slot bằng nhau và slot0≥1, đọc lại slot1, duyệt candidate từ20001 tăng1;
  gặp candidate khác slot1 và `GetDroneUnlocked(candidate)&1` thì **ghi slot0** và dừng.
  Native không có explicit cap20012. Fixture có iteration budget chống treo test, ghi rõ
  đó là test safety, không phải native behavior. Chưa audit mọi caller của routine này.

### GP_Setup.get_indexDrones14f2a2c

Đọc `GameMode.playMode` (TypeInfo GOT2adc840/static+0), **allocate int[2] mới mỗi invocation**:

```
ids = new int[2]
if playMode != 4:
    ids[0] = GetDroneUsed(0)
    ids[1] = GetDroneUsed(1)
return ids
```

Mode4 trả `[0,0]`, không đọc saved slots. Không có scene-name gate trong method này.
Không nhầm với cache/player-array logic của `get_indexPlayers` hay áp scene guard của getter khác.

## 5. StartDrones: đúng hai slots, parent/transform thật

Mỗi vòng slot0 rồi1: gọi GP_Setup instance/get_indexDrones **lại**, lấy `ids[slot]`.
Không lấy một snapshot dùng chung hai slot. Nếu ID<1 thì skip slot đó (slot1 không đổi thành slot0).
Với ID≥1:

1. Ghép path; `Resources.Load<GameObject>`.
2. Lấy `parentDrones@28.GetChild(slot)`; instantiate prefab dưới child ấy.
3. Gọi `transform.set_localScale` = **(0.800000011920929, 0.800000011920929, 1)**.
   Pool literal `0x756c14` bytes `cdcc4c3f`, không làm tròn thành source double0.8.
4. `transform.set_localPosition`: slot0 **(-20,-20,0)**; slot1 **(+20,-20,0)**.
5. `GameObject.SetActive(true)`.

Không thấy range validation ID phía trên, ownership guard hay dedup trong **method này**.
ID dương không tồn tại vẫn đi tới resource-load attempt; fixture plan không hứa instantiate thành công.
Null array/object và child bounds có đường exception: không đổi thành silent-skip fallback.
Không khẳng định callback timing qua mỗi Unity call hay global absence của guard ở caller khác.

## 6. Review spec độc lập và việc giao tiếp theo

Peer reviewed **de2d1366bee5c25e2e19aee7d6d8977b0d75d2a0**, hai source snapshots + feedback receipt
trong `raw/peer-review/review92-*`. Các sửa91 về Board UI/combat và row map structural-only là đúng.
Feedback đã gửi PR12, còn ba chỗ:

1. DATA_SYNC§24.22 “hai đường nhặt đều postevent2” sai: player collider gọi ItemCollected trực tiếp;
   drone mới post2→OnCollectItem→ItemCollected. Không thêm event vào player làm đếm kép (report89).
2. AutoGain phải giữ guard CurrentHealth>0; TechStatLevel0/âm→tech-heal0, không .01×1 ở level0.
3. MISSING§5 footer “hai việc đã xong” còn trái row map entry UNKNOWN; chỉ classification đã xong,
   named binding/order vẫn cần đọc. Không mở lại gate/scenario đã đóng chỉ vì wording ledger.

Giao spec nhập **bindings/resource path + serialized1 + fresh getter/mode4/loadout positions** ở trên;
không đóng 23 wing implementations hay named map/save consumers bằng batch drone này.
Nhánh reverse tiếp tục hai nhóm đó riêng; không đợi ACK mới đào tiếp. Mọi kết luận vẫn provisional.
