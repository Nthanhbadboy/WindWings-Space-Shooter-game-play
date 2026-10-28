# 88 — Producer hit-callback thật → FX và burst item

**Tạm thời, lấy trực tiếp APK.** Tiếp85–87: không còn chỉ có callback tự gán trong
test. Đã nối constructor metadata → callback stores,19 serialized co-attachments,
và chuỗi DropGold → event6 → Items_Manager → pool/IItem/activation.

## 1. Tìm producer, không đoán bằng tên component

Recovery40212823781 tìm direct references;40212990348 thêm bindings/consumer;
**40213095828 SUCCESS33s**, raw **098135279**, có đủ literal/helper bổ sung.
`raw/enemy-hit-callbacks/` giữ native, JSON method metadata, RELA, pointee bytes,
metadata string definitions và byte windows.

Quét6,765,005 ARM64 words trong executable PT_LOAD. Metadata index bảo tồn có
GetComponent<Enemy_Health> usage tại **2bc1148**; ELF RELA nối GOT **2ae1718**.
Tìm8 ADRP/LDR windows thuộc4 routine: skeleton.Start, DropGold.Start, Test_Enemy.Start,
Controller.CacheComponents (mỗi routine có metadata-init load và normal load).
Đây là **address-reference census** giới hạn512B/method/branch/clobber, không
whole-program pointer-flow/reflective-writer closure. Sau census đã đọc chính
constructor và store của từng producer, không dùng candidate làm semantic proof.

| Callback được gán | GOT → metadata usage | Native method thật | Cách ghi |
|---|---|---|---|
| Enemy_Health.hitCallback@20 | 2ae1720→2bc2ff8 | Enemy_HitSkeletonRenderer.OnHit1321a1c | **STR gán đè** |
| Enemy_Health.hitDamageCallback@28 | 2aec478→2bc2fe8 | Enemy_DropGold.DropGold1581828 | **Delegate.Combine** với callback cũ |
| hitCallback@20 trong component test | 2ae1780→2bcadd8 | Test_Enemy.b__8_0 13231d0 | **Delegate.Combine** |
| event6 listener | 2ae8630→2bc5e50 | Items_Manager.OnBurstGolds14c8f14 | AddListener6 từ Start |

Các địa chỉ effective ở bảng được verifier đối chiếu raw RELA và symbol MethodAddress.
Controller.CacheComponents chỉ cache healthScript; **Controller+28 không phải
Health+28** dù cùng số offset. Không tính cache pointer thành đăng ký callback.

### Registration order có ý nghĩa

Skeleton.Start: GetComponent → Unity-object presence check → nếu có thì
**GetComponent lần nữa**, new Action(OnHit), **gán trực tiếp** hitCallback; cuối
root gọi CancelEffect ngay cả khi health presencefalse. Nếu getter lần2 trảnull,
đi failure trước tail CancelEffect. Không tự cache kết quả lần1 thay cho lần2.

Test_Enemy.Start setup text dependencies trước reached registration block;
callback chỉ set started=true và chụp Time.time ở hit đầu. Không lấy tên class
để tuyên bố component này không bao giờ có trong gameplay, hoặc lấy nó làm
measurement cadence/DPS của game. Start test sau skeleton sẽ append timer;
skeleton sau test có thể overwrite nó. **Không khẳng định Unity Start order**.

DropGold.Start append Action<float>(DropGold) vào hitDamageCallback. Thứ tự multicast
được giữ; exception callback cũ có thể chặn callback sau. Đây là Start registration,
không tự thêm một lần Combine ở mỗi OnEnable/pool reuse.

## 2. Positive serialized bindings: không phải chỉ component test

Giữ record theo class từ raw typetrees; bỏ generated m_Script bị đọc sai. Vì record
legacy không mang serialized-file, join bằng **GO pointer + component membership**
vào health snapshot có file-qualified identity, bắt buộc unique, không join global
pathID đơn lẻ. Proof có source shard/SHA:

- **2 Enemy_DropGold**, enabled1: CB-30010 GO185688/component668817 ↔ Health691401;
  GO185705/component668818 ↔ Health691402.
- **17 Enemy_HitSkeletonRenderer**, enabled1, trên các Gun/Boss parts; đủ slotNames,
  SkeletonAnimation reference và hitColor serialized trong contract.
- Cả19 resolved trong **data.unity3d/resources.assets**, snapshot health.noDamage=false.

Đây là co-attachment evidence cho GetComponent trên cùng GO, **không chứng minh
prefab đã spawn trong stage nào/Start đã chạy**. Không suy 19 root là cả game,
noDamagefalse bất biến hay visual output đã được nghiệm thu.

## 3. Skeleton OnHit: property `_Black`, không tự redraw hiệu ứng

Literal **_Black**, không phải `_Color`; Invoke literal **CancelEffect** đã decode
qua encoded usage→metadata header/definition/bytes. OnHit duyệt slotNames, tìm slot,
material dictionary entry rồi SetColor(_Black, serialized hitColor). Không silently
skip slot/material thiếu. Duyệt xong mới IsInvoking→CancelInvoke nếu cần→Invoke
CancelEffect với literal **f32(.01)**. CancelEffect ghi **RGBA(0,0,0,1)** vào cùng
property, không ghi lại hitColor. Ctor default hitColor=(1,1,1,1), nhưng serialized
instances có màu riêng (ví dụ .7294118); không thay bằng flash trắng chung.

.01 là delay argument, không measured wall-clock/FX duration; scheduler/timeScale
vẫn là engine. Thay đổi list/material bởi helper vẫn có thể ảnh hưởng live rereads;
fixture không render Spine/material và không nuốt helper exceptions.

## 4. DropGold đọc tỷ lệ HP hiện tại, KHÔNG dùng `_damage`

Ctor load64bit từ **7576b8** = `1c0000000a000000`: hai **int32**
**burstCoins=28**, **totalP=10**, rồi iPlus=1. Các field này không nằm trong serialized
DropGold records; không tự điền chúng từ JSON rỗng hoặc coi đây là float28/10.

DropGold lấy IHealth **GetCurrentHealth slot1**, rồi GetComponent<IHealth> lại,
**GetStartHealth slot0**. Với finite/positive-start/in-range domain:

```
percent = f32(f32(currentHP / startHP) * 100)
lost = 100 - trunc_int32(percent)
if lost > iPlus * totalP:
    iPlus += 1
    post event6 BusrtGolds(BurstGold{burstCoins, parent=transform})
elif lost < totalP:
    iPlus = 1
```

- Threshold là **>**, không >=; lost=10 chưa phát, lost=11 phát lầnđầu.
- **Một increment/một event mỗi lần gọi**, không while-catch-up các mốc bị vượt.
  Hit100→0 qua receiver có thể tới DropGold một lần, không tự phát10 events.
- `_damage` không được dùng trong body. Nếu callback multicast trước nó sửa HP,
  DropGold đọc tỷ lệ mới, không đổi thành tính từ loss argument đã capture.
- iPlus tăng trước synchronous PostEvent; helper/listener throw không rollback.
- Heal về lost<10 resetiPlus=1; lost==10 không reset. Không tự reset tại Appear.

85 vẫn áp dụng: CalculateDamage chỉ invoke damage-callback nếu loss reread>0.
Fixtures thêm chain **receiver → registration thật → DropGold → consumer**;
old-callback mutation/exception cases là fixture đầu vào, không tự nhận đã tìm thấy
mọi subscriber đó ở prefab. Native infinity/FCVTZS special select giữ raw; finite
model không tự biến ràng buộc domain thành input validation của APK.

## 5. Event6 → số item thật, không đồng nhất28 với28 object/currency

Items_Manager.Start bind **OnBurstGolds** vào **EventID.BusrtGolds=6** (giữ typo).
Consumer cast BurstGold, không silently bỏ payloadnull/sai type. Với budget n≥0:

- q=max(trunc(n/5),0), r=n−5q; radius chọn theo **q+r trước split**.
- Bình thường spawn r×**70001**, rồi q×**70002**.
- Nếu q≥2 và r=0: spawn **5×70001 + (q−1)×70002**, không chỉq object.
- n=28 → **3×70001 +5×70002 =8 object**; n=10 → **5+1=6 object**, radius vẫn
  chọn từ q+r=2 trước khi chuyển split.

Radius: q+r=1→bits9a99193e (~.15),2–3→.75,4→**bits6766e63f**
(**1.8000000715255737**, khác nearestf32(1.8) mộtULP),>4→f32(2.4).
Budget0/negative không tự sinh object; model bounded int32, không fabricated clampAPK.
Parent transform position được đọc **lại cho mỗi object**, không snapshot một lần.

**Chia5 là luật chia spawn budget; không đủ để khẳng định70002 cộng5 tiền khi nhặt**.
OnCollectCoin1/2 là nhánh receiver khác có modifiers; không suy collected currency
hayTTK từ budget hoặc số object.

### BurstOut → helper → pool → interface → explicit activation

BurstOut gọi MyPhysics2D.GetEllipseRandomizeVector(centerXY,radius,inside=true,
eccentricity=0,minRadius=radius>1?0:radius/2). Đã đọc helper:

1. random x trong các tham số[-radius,radius]; tính vertical cap bằng sqrt.
2. random y magnitude với tham số[minRadius,cap], kể cả khi endpoint đảo thứ tự.
3. Random.Range int tham số(0,5), return<2 thì âm, còn lại dương.

Không thay bằng uniform-angle/uniform-area circle trong bản dịch. Random outputs
là input fixture; không gọi đây là histogram đã đo. Pool.GetObject(id,targetXY,
**GameLayer.layerItem**) → GetComponent<IItem> → **IItem.BurstOut(centerXY,targetXY)**
→ lệnh SetActive(true) của root. Exception ở interface ngăn lệnh activation phía
sau; không suy Pool.GetObject trước đó không có activation/side effects riêng.
Không đào lại pool-history để chứng minh scenario thắng/thua.

## 6. Handoff, coverage và việc tiếp

`datas/enemy_hit_callback_flow.json`:4 callback/listener bindings +6 typed joins,
2 exact literals,4 raw cells, **16 method ranges/1256 instructions/56 anchors**,
19 co-attachments vàSHA. Reproduce:
`python3 -m tools.verify.enemy_hit_callback_flow --check`.
Full local **450 tests PASS38.652s**, data validation +receiver/lifecycle/shield/callback
regeneration +whitespace checks PASS. Code **16748ccc3**, Verify **40213772726 SUCCESS55s**.
Đã gửi findings cho peer qua PR12comment**6400435826**, chưa có ACK88 được ghi nhận.
Models `enemy_hit_callback_models.py`, **38 tests mới**: registration order,
multicast exceptions/reentry, strict threshold/no catchup/HP reread,1001 budget
cases, exact non-nearest float, sampler parameters và interface→activation order.

Đã thay khoảng hở producer nêu87 bằng các join cụ thể ở trên; không nói đã exhaust
mọi indirect writer hoặc prefab lifecycle execution. Tiếp nối pickup branch
**Player_Physics.ItemCollected14bc328/OnTriggerEnter2D14bc9c0 → OnCollectCoin1/2**
để phân biệt spawn budget và collected currency. Peer đã ACK87 ở6400347386,
tip8ac40be40e; đề nghị queue thêm wing-cannon getter14b1eb0/SetBarrels và drone
base-fire rules. Phải review raw đã có trước khi nhận các đề nghị đó thành “thiếu dữ liệu”.
Không chờ screenshot mới, runtime hay hỏi lại định hướng để đọc tiếp native.
