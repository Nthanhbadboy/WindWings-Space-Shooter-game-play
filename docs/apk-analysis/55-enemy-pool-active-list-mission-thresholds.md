# 55 — Enemy ra khỏi active-list ≠ enemy bị diệt; threshold mission thật

**PROVISIONAL — đọc native/dump/metadata APK gốc, không phải runtime replay.**
Premium vẫn để sau. Nối gate endgame report53 và exact prefab report54.

## Nguồn và tái kiểm chứng

- Recovery40184816519: GP_Datas, Enemy_Controller, Enemy_Health.
- Recovery40184927785: Enemy_Destroy; asm/inventory trong
  `reverse-engineering/raw/ui-audit/extra-native/`.
- Native constants Board_Endgame/Player_Get_Datas và field-defaults metadata.
- `enemy-exit-missions.json.gz`:15 method bodies,12 checks, source hashes,
  resolved metadata loads/calls, declarations và3 block initializer bytes.
- `python3 tools/verify/enemy_exit_missions.py`
- `python3 -m unittest discover -s tests -q`:52 tests pass.

Assertions là evidence guards trên nhánh inspected, không phải chứng minh
động cho mọi subclass/override và mọi playthrough.

## 1. Active list nghe event78/79, không nghe mỗi enemy death

`GP_Datas.ResetAlls @14cfc78` đăng ký:

| Event | Native registration | Delegate metadata slot | Callback |
|---|---|---|---|
| OnSpawnEnemy78 |14cfd60..70|2ae87a8|`<ResetAlls>b__60_0 @14d006c`|
| OnPoolEnemy79 |14cfd90..a0|2ae87b0|`<ResetAlls>b__60_1 @14d0180`|
| OnEnemyDie19 |14cfdc0..d0|2ae87b8|`<ResetAlls>b__60_2 @14d0254`|

Spawn callback dùng `listActiveEnemies +70`: Contains trước; nếu chưa có thì
Add (inlined fast path tại14d0114..148, resize fallback14d0170).
Pool callback dùng cùng field: Contains trước; nếu có thì Remove tại14d0238.
Metadata xác nhận generic List<GameObject>.Contains/Add/Remove, không đoán từ
địa chỉ gọi đơn lẻ. Pool event lặp trên cùng object không buộc giảm count lần2.

Không gọi đây là list đã được kiểm tra chỉ chứa enemy sống/hợp lệ: input đi từ
event payload, emitter có thể publish trước kiểm tra Unity-object truthiness
(report53); chưa chứng minh mọi override đều tuân thủ lifecycle.

## 2. Pool path có thể chạy khi enemy hoàn thành đường bay

Base paths đã giữ:

```text
Enemy_Controller.OnDieWhenZeroHp @15846f8 → Destroy virtual(type0)
Enemy_Controller.OnDieWhenHitPlayer @1584754 → Destroy virtual(type1)
Enemy_Controller.OnMoveCompleted @1584778 → Destroy virtual(type2)

DestroyType: WhenDie0 / WhenHit1 / WhenDone2
Enemy_Destroy.Destroy @1581598:
  type0 → virtual OnDestroyByZeroHp
  type1 → OnDestroyWhenHitPlayer
  sau đó tail Pool @1584bf0
  type2/khác → thẳng Pool
```

`Enemy_Destroy.Pool` xóa onDead, lấy GO, emit **OnPoolEnemy79** tại1584c40..4c,
**trước** nhánh trả PoolingManager hoặc deactivate/delayed Unity destruction.
Base type2 không cần có event death để active-list mất object.

`Enemy_Destroy.OnMoveCompleted @1584bec` chỉ ret; dispatch type2 trong
Destroy không gọi nó. Đừng suy tên hook này là nơi phát death event.

Nhánh zeroHP và hit-player đều **có** emit OnEnemyDie19 rồi OnPoolEnemy79;
chúng nằm sau kiểm tra callback `onDestroyed +20` khác null. Không tuyên bố
emit vô điều kiện: nhánh callback null có thể return trước các event này;
outer Destroy vẫn đi Pool trên đường thường. Sau helper đã emit79, Pool có
thể emit79 lần nữa; Contains guard ở remove giải thích tính idempotent.

`DestroyNoEvents` là đường riêng: tên không có nghĩa không gọi callback — nó
vẫn gọi onDestroyed/onDead nếu có, rồi pool/destroy mà không có explicit emit
19/79 trong body inspected. Chưa audit hết caller/override của đường này.

**Hệ quả:** gate `listActiveEnemies.Count==0` trong report53 không chứng minh
kill100%. Enemy bay xong có thể rời list mà không tạo death event ở base path.

## 3. killCount là counter khác

Death-event callback `<ResetAlls>b__60_2` có cập nhật static
`GP_Datas.killCount +1c` tại14d0638..40; sau đó gọi onEnemyDie nếu delegate có.
Nó còn xử lý dữ liệu/reward và nhánh branch có filter trước increment; không
đồng nhất mọi pool với kill, không suy normal/branch luôn đếm như nhau.

Report53 đã nối normal nonbranch GP_Endgame đọc killCount và instance
countEnemies+58, gọi Board_Endgame.GetMissionCompleted; result>=0 cho nhánh
victory candidate. Các kiểm tra player và flow khác vẫn còn, không chỉ counter.

## 4. Đã decode bảng threshold từ raw initializer, không từ đoán tên

`Player_Get_Datas.GetKillPercentMissionComplete @14e5618` tạo float[3],
chọn field bằng mode: mode0→slot2ae8b88; mode1→2ae8b80; còn lại→2ae8b78;
InitializeArray tại14e56b8. Caller normal đọc **Stage_Datas.ModeCurrent +34**
(không phải field cùng offset của GameDatas).

| Mode int | Slot |12 bytes initializer little-endian| Float32, hiển thị làm tròn |
|---|---|---|---|
|0|2ae8b88|`cdcc4c3e6666e63ecdcc4c3f`|0.20 /0.45 /0.80|
|1|2ae8b80|`3333b33e9a99193f48e17a3f`|0.35 /0.60 /0.98|
|khác|2ae8b78|`0000003fcdcc4c3f0000803f`|0.50 /0.80 /1.00|

Mỗi block12 bytes có SHA256 **khớp chính tên hash field PrivateImplementationDetails**
được resolve từ relocation→metadata. Raw artifact giữ cả tên hash, record field
và float32 chính xác. Không dùng bytes padding phía sau như phần tử thứ4.
Chưa gán nhãn difficulty bằng suy đoán cho mode0/1/khác.

Normal nonbranch trong `Board_Endgame.GetMissionCompleted @12734f8`:

```text
result = -1
for i in 0..2:
    threshold = ARM_fcvtzs(float32(maxCount) * table[ModeCurrent][i])
    if count >= threshold:
        result += 1
return result
```

Phạm vi pseudo-code: input nonnegative hữu hạn, đường normal nonbranch.
Native còn có xử lý infinity và branch objectives riêng; không xóa chúng khỏi
raw hoặc lấy pseudo-code này làm toàn bộ method.
`fcvtzs` là truncate về0, không phải ceil; với số dương tương đương floor.
Method trả số tier pass trừ1 (−1..2), chưa nối ra số sao render ở Board_Endgame.

Ví dụ **synthetic**, không phải count của stage thật: mode0, denominator100:
count19→−1;20→0;45→1;80→2. Vậy nhánh victory candidate normal không đòi100%
ngay trong bảng này. Không lấy ví dụ100 làm denominator của stage2/3.

## 5. Còn mở: denominator và subclass thật

- Report54 có274/95/155 **slot cấu hình**, không tự thay vào countEnemies.
- Đã tìm raw `Stage_Get_Datas.GetCountEnemies @12c5f60`: lấy list wave, load
  prefab theo chapter/branch, GetComponentsInChildren<Call_Data>(false), bỏ
  spawnType5, duyệt listPrefabEnemies, lấy IPooling ID và filter một danh sách
  ID trước khi cộng (12c62c0..12c63c4). Method này **không đơn thuần cộng number**.
- Chưa nối caller/store chính xác vào GP_Datas+58 và chưa resolve membership
  của filter cho các prefab thật. Chưa công bố denominator hoặc số kill cần
  để thắng stage2/3.
- Enemy_Controller gọi virtual Destroy; cần nối concrete component của từng
  enemy prefab (bao gồm subclass) trước khi áp base path cho toàn bộ274 slots.
- Timeline spawn vẫn cần map placement/scroll/tutorial pauses, không lấy local
  y/rate làm timestamp.

Đây là các raw joins tiếp tục đào; screenshot stage2/3 không phải điều kiện chờ.

### Bổ sung sau report này

Report56 đã nối GetCountEnemies→MapController.Start store GP_Datas+58, resolve
IPooling IDs/filter và concrete destroy references cho14 root. Static normal
chapter0 denominator stage2/3 là262/238, **không phải274/250 slot**. Các cảnh báo
runtime, branch và chưa nối tier result sang số sao UI vẫn giữ nguyên.
