# 89 — Nhặt item → callback thật → số xu được cộng

**Tạm thời, nguồn APK đã pin; không phải nghiệm thu Unity runtime.** Tiếp report88
qua cả receiver lẫn producer: nhặt trực tiếp bằng player và drone gửi CollectItems.
Không còn suy giá trị xu từ phép chia spawn budget cho5.

## 1. Bằng chứng và phạm vi đã dịch

Recovery đầu40214015944 SUCCESS/rawfd49689a0; bổ sung40214229547 SUCCESS/raweaa5c7434.
`reverse-engineering/raw/pickup-currency/` giữ ASM/JSON,5 ô float4B, page4096B tại77a000,
RELA,3 encoded literal cells + metadata definitions/data, hai event2 call windows.
XAPK SHA f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e;
lib SHA9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99.

Contract `datas/pickup_currency_flow.json`: **20 method ranges/3530 instructions**,63
order/arithmetic anchors,124 native arithmetic rows,13 switch entries,4 callback
bindings,6 type joins,3 literals,36 payout pairs và2 burst examples. Count method
ranges là độ phủ evidence, không phải tuyên bố đã mô phỏng toàn bộ movement/physics.

`python3 -m tools.verify.pickup_currency_flow --check` kiểm native-range coverage,
source hashes, critical operands, raw float bits, byte dispatch, RELA→metadata,
IPooling.GetID slot0 và literal decoding. Models/tests là fixtures finite, initialized
classes, fields ổn định trong một phép tính; không giả FPCR/NaN/infinity hoặc những
int32 intermediate nằm ngoài miền fixture. Native cộng cuối được model wrap32.

## 2. Binding thật và hai đường nhặt

| Liên kết | GOT → effective metadata cell | Method |
|---|---|---|
| Physics.Start RegisterListener2 | 2ae8238→2bc8428 | OnCollectItem14bc280 |
| Controller.Start STR callback Physics+20 | 2ae8440→2bc8388 | OnCollectCoin1 14c358c |
| Controller.Start STR callback Physics+28 | 2ae8448→2bc8390 | OnCollectCoin2 14c3800 |
| Controller.Start RegisterListener26 | 2ae84d0→2bc8360 | b__11_1 14c5168 |

Các effective cell được verifier kiểm ELF RELA và MethodAddress, không lấy tên
method gần callsite để suy callback. Hai coin callbacks là **gán đè**, không Combine.
RegisterListener26 là **OnPlayerChanged**; đăng ký không có nghĩa callback đã chạy
hay mọi thiết bị đang trang bị đều đã áp bonus ngay khi Start kết thúc.

**Player collider:** OnTriggerEnter2D14bc9c0 kiểm tag **Item** trước Physics.activeHitEnemey90
và invisible91. Nhánh item: lấy GameObject → ItemCollected → **lấy GameObject lần nữa**
→ PoolingManager.PoolObject123acd0. Do đó không gắn nhặt xu với contact-hit permission.
Callback/event exception có thể chặn tail pool; không tự thêm finally/dedup.

**Event2:** OnCollectItem kiểm null/type GameObject và tag Item rồi gọi ItemCollected.
Receiver này **không PoolObject**. Literal Item được decode từ metadata, không đoán tag.

**Producer drone đã tìm và đọc:** Droid_Movement1.Update1589a2c và CollectItems158a224 có
PostEvent2 lần lượt1589f74/158a598. Reached suffix, sau target/scan eligibility:
- distance<5 và Sub_Item.IsForceCollect=false: gọi CollectTo(player), chưa post nhặt;
- ngược lại, distance<.5: post2 với GameObject → reread live target/collider → pool;
- Update còn reset target=player **sau pool**; CollectItems tiếp tục scan, không thêm reset đó.
- .5 và5 là **strict**; không chuyển force+collect thành một thao tác cùng frame.

Sub_Item.CollectTo14cc8c0 chỉ forward movement.player20 và forceTarget44=true;
IsForceCollect14cc8e4 đọc44. Không phải cộng tiền tại CollectTo.

Selector raw tìm hai candidates bằng MOVZ w1,#2 → direct PostEvent1434cb4 trong bounded
window, không qua call/clobber. Đây không phải census mọi indirect/event producer;
sau selection đã đọc hai full bodies và các prefix gates, không lấy scan match làm
bằng chứng item nào cũng được nhặt. Suffix fixture không tự nhận mô phỏng toàn bộ scan.

**Không nhầm cleanup với pickup:** Item_Movement.Update14cc2fc so sánh y với−25;
y<−25 đi SetActive(false) rồi Pool tail14cc354, **không post2/cộng xu** tại block này.
Không có coroutine cần recover ở Update này. Không suy mọi object về pool là được thu.

## 3. ItemCollected: ID qua interface, không qua tên prefab

GameObject.GetComponent<**IPooling**>() (GOT2adc9c0), TypeInfo2adc9c8,
virtual slot0=GetID(). Không phải IItem/ISubObject.GetID theo phỏng đoán.
Byte table77a086: `003a3d51667afd8ea2b6003aca`, target=14bc4c0+4×byte.

| ID | Target | Nhánh coin |
|---|---|---|
|70001,70011|14bc4c0|Physics callback+20, Coin1|
|70002,70012|14bc5a8→14bc4c8|Physics callback+28, Coin2|

13 entries70001..70013 được giữ trong JSON; không gọi đó là toàn bộ ItemCollected
switch. Các ID khác có handler khác; coin-only fixture reject ngoài scope không có
nghĩa APK reject những item đó.

Nhánh coin: callback nếu nonnull → **gọi PlaySoundCoins14bcd3c**. Callback null vẫn gọi
sound helper, callback throw thì không. Helper có Time.time gate riêng, vì thế gọi
helper không đồng nghĩa mỗi vật phẩm luôn phát một tiếng. Không nhét pool vào callback
Coin1/2; pool thuộc collider hoặc drone producer phía trên.

## 4. Công thức currency, không phải denomination5

Controller đọc **GP_Datas.coinCount static+20**. Ký hiệu dưới giữ operation order
binary32; f32 round sau mỗi phép arithmetic, truncate về int32 ở đúng chỗ.

```
g = float(trunc(f32(float(stage+10) / 10)))
A = f32(min(f32(1.5*g),16) + 2.5)     # Coin1 base
B = f32(min(f32(3*g),23) + 12)        # Coin2 base
L = 1                               # tech <= 14
L = f32(1 + f32(float(tech-14)/3))    # tech >= 15
```

Bốn thresholds dùng f32(L×literal). Native **FCMP threshold,balance**, không phải
balance,threshold: PL đi tiếp khi threshold≥balance; Coin2 first-band dùng MI để
nhảy thẳng high-band. Không đảo dấu khiến lower bands trông như unreachable.

| Balance đang có, so sánh strict | Coin1 trước modifiers | Coin2 trước modifiers |
|---|---:|---:|
|>5500L|1|2|
|>4300L và≤5500L|A×.25|B/6|
|>3300L và≤4300L|A/3|B×.25|
|>2500L và≤3300L|A×.5|B×.5|
|≤2500L|A|B|

Sau đó nhân f32(1+Controller.addPercentCoinByDevice54), rồi nhân **.86f nếu stage≤40**;
stage>40 giữ nguyên. Truncate cuối → native ADD w32 vào coinCount → **store trước**
PostEvent48(**AddCoin**, no payload). Dù delta0 vẫn store/post; không thêm minimum1.
Post là đồng bộ theo dispatcher đã bóc85: listener có thể đọc/sửa coinCount/reenter,
hoặc throw sau khi coinCount đã đổi. Không restore coinCount sau callback.

Float cells:756f3c=5500,756e50=4300,7570f0=3300,756fa4=2500,
756de8=`f6285c3f`=.8600000143051147. Stage registers qua csel/branch đã đối chiếu;
trong miền stable của fixture, final stage gate vẫn là stage gốc, không bị csel thành0.

### Mốc dễ triển khai sai

Stage41/tech0/device0, pairs(Coin1,Coin2): balance2500=(10,27),2501=(5,13),
3300=(5,13),3301=(3,6),4300=(3,6),4301=(2,4),5500=(2,4),5501=(1,2).
Stage1 ở4301 nhận(0,2),5501 nhận(0,1); không ép xu nhỏ tối thiểu1.
Tech17 làm L=2, thresholds gấp đôi; tech15 dùng binary32 1+1/3, không int-div.
Stage40 lowband=(8,23),stage41=(10,27), không cùng một hệ số .86.

Burst28 của88 spawn **3 nhỏ+5 lớn**, không28 tiền, không8 tiền, không18 tiền.
Nếu bắt đầu balance0/tech0/device0 và nhận đủ8 theo fixture:
- stage1:3×3+5×12=**69**;
- stage41:3×10+5×27=**165**.

Đây là conditional examples, không hứa tất cả item được thu trong game. Mỗi pickup
đọc balance mới: stage41 bắt đầu2490, ba nhỏ rồi năm lớn thêm90; năm lớn rồi ba nhỏ
thêm94. Không gộp burst thành một fixed payout hoặc tự ấn định pickup order từ spawn order.
coinCount là ledger của gameplay; report này không đồng nhất nó với persistent wallet.

## 5. Nguồn stage/tech và bonus thiết bị

GP_Setup.get_stageIndex14f0da0: Application.companyName==literal **Test** và
GameDatas.fixedStagePlay38 thì trả Map_Get_Datas.mapCurrentPlayTest20; còn lại
Stage_Datas.IsBranch30 chọn StageBranchCurrent2c hoặc StageCurrent24. Không lấy
screenshot stage label làm thay getter. Singleton getter14efdec cũng đã giữ raw.

Tech_Datas.GetTechLabLevel13999ac: GameMode static mode==4 **và** active scene.name==
literal **Game** thì0; còn lại Player_Saved_Datas.GetTechLabLevel14e802c. Vì vậy không
coi helper luôn trả saved tech. Test/Game đều có encoded cell + metadata bytes.

OnPlayerChanged callback14c5168 unbox playerIndex → Player_Device_Saved_Datas.
GetPlayerDevices14e628c → reset bonus54=0 → skip instanceId−1 → Device_Saved_Data.
GetDevice12546d0 → chỉ **Device.id@10 trong5000..5999** → cộng f32(GetStatValue2/100).
Không lọc instanceId theo5000..5999, không nhầm Device.lv14 và rank18.
GetDevice dùng dictionary.TryGetValue/out (có lazy load), miss có thể trảnull;
producer sau đó native null-failure, không tự bỏ qua thiết bị hỏng.

Device_Get_Data.GetStatValue2 1250134:
```
c = trunc(Device.id/1000)
row = listStatValues[c+4]
if row[rank] == 0: return 0
return f32(row[rank] + f32(percentByLevels2[c-1] * float(lv+1)))
```
Rank−1/out-of-bound là failure, không tự clamp. Không lấy cấp hoặc rarity theo tên
asset. Model nhận explicit configuration arrays; test numeric table là **synthetic**
và được đặt tên rõ, không phải bảng APK mới trích. Report này đã dịch getter/caller,
không tuyên bố đã bổ sung giá trị mọi row/percent hay mọi equipped loadout. Khi cần
số bonus thiết bị cụ thể, nối initializer/config của hai fields này; không gọi đó là
thiếu APK hoặc xin runtime thay static extraction.

## 6. Regression và bàn giao

50 tests mới: threshold equal/+1, tech14/15/17, stage40/41, cap riêng, zero payout,
f32 modifier order, native add wrap, synchronous event reentry/failure, aliases,
callback overwrite/null, item-before-hit-guard, live GO reread, device reset/filter,
rank/zero-stat, getter mode gates, drone force/strict-distance/post-pool ordering và
hai fixtures nối xuyên drone→receiver→controller→event48→sound-helper→pool.

Full500 tests + datas validate + verifier check được ghi receipt trong
`raw/pickup-currency/derivation.json`; không lấy tests làm Unity playback evidence.
Peer cập nhật report88+89 cùng nhau; hiện chưa thấy ACK88/89. Queue tiếp theo là
wing-cannon getter14b1eb0/SetBarrels và drone base-fire laws theo ACK87; kiểm raw có
sẵn trước rồi recover dependencies cụ thể, không quay lại pool-history/screenshot.

**Receipt:** code0a700993d, full500 PASS37.337s; Verify40214936072 **SUCCESS55s**.
Findings giao PR12comment6400594184; chưa ACK89, không tự coi peer đã sửa spec.
