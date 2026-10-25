# 91 — Làm yêu cầu spec: nguồn ghi HP và consumer thật của Board_Drones

**Tạm thời, APK đã pin; không lấy tài liệu spec làm bằng chứng gameplay.** Review
nhánh spec `ecff896c36cac3e58d991beac3328ec62f5cdb62`, theo yêu cầu PR12
comment6400762294. Đã đọc writer được chỉ tên, theo tiếp callback và nguồn float;
đồng thời đọc ctor → field → consumer của Board_Drones, không đóng gap bằng tên class.
Không merge hay sửa nhánh spec. Snapshot3 tài liệu và yêu cầu được giữ ở raw/peer-review.

## 1. Bằng chứng và regression

Recovery40217205190 SUCCESS/raw151418cad; bổ sung literal40217372873
SUCCESS/rawaa8d400bb. Raw `reverse-engineering/raw/player-hp-board/` giữ native
HP/closure, Board/closures/coroutines, các helper được gọi, RELA/ô float/literal
metadata. Có các method raw chưa dịch ở batch này; inventory không phải semantic approval.

`datas/player_hp_board_flow.json`: **20 ranges/1589 instructions/80 anchors**,5 joins
(type/callback),3 array field bindings + SHA kiểm byte sử dụng,1 literal đã decode,
constant-bit proofs và direct-call census của thân Board. Dùng thêm raw combat-chain
cùng APK để kiểm initializer Player_Get_Datas. XAPK SHA
`f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`;
lib SHA `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`.

`python3 -m tools.verify.player_hp_board_flow --check` PASS; **56 test mới/full648
PASS39.654s**; datasvalidate PASS. Models hữu hạn, không overflow int32; nhánh giữ
ratio cần oldStart≠0 để nằm trong miền finite. Không biến lỗi miền fixture thành
kết luận native throw khi chia0. Không suy event đã emit/Unity timer đã chạy từ đăng ký.

## 2. Trả lời nguồn HP: có công thức chung, không phải bảng theo ID tàu

GOT2ae8580→RELA2ba9380→SpaceShooter.Player.Player_Health_TypeInfo.
Static0/4 đúng là **StartHealth/CurrentHealth**. Ba việc phải phân biệt:

| Đường | Native | Tác dụng |
|---|---|---|
| cctor Player_Health |14c7cd8, double@7579f0| StartHealth=**2000**, CurrentHealth=**0** |
| ResetStaticVariables |14c6ca0| chỉ CurrentHealth=StartHealth; không tự tính max mới, không post event21 |
| nguồn GetStartHp |14e311c→14e318c| **2500 × (1 + .18×TechStatPoints(0) + 1×ability7)** |

Công thức theo từng phép f32 native. Init StartHp2500/stepCommon.18 được pack trong
d0@757bc0 rồi store static68 (68=.18,6c=2500). abi7AddPlayerStartHp static314=1,
lane1 q0@778b70 store310. **Không phải** StartHealth cctor2500; cũng không phải
HP riêng mỗi tàu đọc từ một mảng24 phần tử.

`GetHpStatPercent` gọi **GetTechStatPoints(0)**1399aa4, không GetTechStatLevel(0),
không techlab level. Gọi ability7 sau points. Không có ID tàu hay index damage làm
tham số/array lookup trong công thức này. Cùng inputs thì cùng nguồn max HP; điểm
0/ability0→2500; ability7=1→5000. Point1/ability0≈2950, chính xác f32 là
2950.000244140625, không ép thành integer trong model.

Tech points wrapper: mode4 và scene Game thì trả `(index==1)`; do HP hỏi index0 nên
nhánh đó nhận0. GetTechStatLevel(0) ở nhánh tương ứng trả0, nhưng là helper riêng.
Nhánh normal points đọc saved stat points; không lấy bảng tech tier của wing thay
cho points. Platform special-case stat1 không phải hệ số HP stat0.

**Kết luận cho spec:** nguồn max HP và các writer được hỏi đã đọc xong, không còn
chỉ là “thấy field static, writer chưa đọc”. Nhưng câu “mọi tàu luôn HP2500” sai:
modifier, refresh branch, HP history và snapshot cctor khác nhau. Batch này không
phải whole-program census mọi writer ở class khác hay proof không có external overwrite.

## 3. Start chỉ nối listener; callback mới thực hiện các nhánh HP

Start14c6b5c nối2 delegate qua metadata method pointers (đã RELA→MethodAddress):

- event36→`Player_Health.<>c.<Start>b__14_0`14c7fe8;
- event64→`Player_Health.<Start>b__14_1`14c7d28.

**Event36:** unbox payload đúng Int32. Null/wrong type đi nhánh native exception;
chỉ payload==7 mới gọi GetStartHp và **ghi StartHealth thôi**. Không ghi Current,
không rebake amountAutoGainHpByTech, không post event21 ở callback này.
Ví dụ mất bonus ability: max5000→2500 trong khi current4800 có thể còn4800 ở đây.
Không tự thêm clamp/reset/heal vào callback36.

**Event64:**

```
if GameMode.playMode == 1 && GameMode.waveIndex != 0:
    cache oldStart, oldCurrent
    newStart = GetStartHp()
    newCurrent = f32(f32(oldCurrent / oldStart) * newStart)
    store StartHealth, CurrentHealth
    PostEvent(21, newCurrent)
else:
    StartHealth = GetStartHp()
    ResetStaticVariables()  # Current=Start; không post21 trong nhánh này
```

Điều kiện là **waveIndex**, không index tàu/test flag. Ratio không clamp ở đây:
oldCurrent gấp2 oldStart vẫn cho newCurrent gấp2 newStart. Preserve branch giữ
current0 là0; nhánh reset thì refill. Event21 sau store và trước bước đọc nguồn heal;
callback đồng bộ đổi StartHealth có thể ảnh hưởng phép tính heal tiếp theo.

Sau hai nhánh, callback64:
1. amountAutoGainHpByTech=GetHpRecoverSpeed()×StartHealth;
2. InvokeRepeating(**"AutoGainHealth"**,5,5); literal2ae8618 được lấy encoded usage,
   metadata definition và bytes UTF8 thật — không đoán tên từ method gần đó;
3. timeToImmuneOneHit=Time.time+TimeToImmuneOneHit(); sau đó resolve player reference.

GetHpRecoverSpeed dựa **TechStatLevel(0)**: level0→0; level1→.01;2→.01×1.03;
3..4→.01×1.06;5..7→.01×1.08;≥8→.01×1.10 (per-op f32). Native không viết
`level<=0→0`; level âm khác0 rơi nhánh base. TimeToImmuneOneHit: ≤0→float.MaxValue;
1..3→50;4..5→45;6→40;7..8→35;9→30;≥10→25. Đây là interval tính deadline, không
lời hứa immunity luôn active hay mỗi hit dùng cùng nhánh TakeDamage.

AutoGainHealth14c7bc8 chỉ khi Current>0, cộng lần lượt techHeal rồi deviceHeal,
upper-clamp StartHealth, store trước event21. **Không nhân deltaTime**; số heal này
là chunk mỗi callback được schedule5s. Full HP vẫn post21; không heal người đã chết.
GainHealth(amount,bool) cũng chỉ upper-clamp, không lower-clamp: amount âm có thể làm
Current âm; FX chạy trước read Current để post21. Không đổi nó thành auto-resurrection.

## 4. OnChangeDataDevice không ghi HP max

14c58ec gọi GetDevices(_idPlayer), rồi reset reduction58/heal28 về0 **trước khi
null-check array**. Với mỗi instanceID≠−1: lấy Device, đọc **Device.id** để chọn band:

- id1000..1999: cộng **GetStatValue1(device)/100** vào reduceDamageByDevice;
- id5000..5999: cộng **StartHealth×GetStatValue1(device)/100** vào deviceHeal;
- ngoài band không cộng. Không lấy instanceID để phân band, không GetStatValue2.

Không clamp reduction≤1 trong method này. Device/null error sau partial writes
không rollback; nếu chính GetDevices throw thì reset chưa diễn ra. Không ghi Start
hay Current. `_idPlayer` chọn loadout để tính reduction/heal, **không** nhân max HP
với hệ số riêng ID tàu trong writer này. Cách áp reduction trong TakeDamage là
consumer khác, không lấy configured value làm khẳng định damage runtime.

## 5. Board_Drones: ba bảng UI có consumer thật, không phải combat BaseDamages

### a. Ctor price24 → SetUpgradeCost

Ctor12649ec InitializeArray24 float, GOT2add988→private field
`C9A0FA1D0ECC4E61C8B391176C4974E4CEC7B7B6D5446684E5735F4FC7AFC9CB`;
store **instance238/playerPriceMultipleA**. indexDefault1c8 được ctor đặt **20001**.
SetUpgradeCost đọc238 tại125ea60 và125eb00, index=`cellIndexCurrent-indexDefault`;
ngưỡng giá trị>1 và platform gates dẫn tới nhánh label/format. Không đổi array này
thành drone damage/cadence. Đọc consumer UI không tự chứng minh giao dịch trừ tiền.

### b. Static ctor → GetPlayerPower → textDispDamage

Board static10 **allBasicAtk**, static18 **allDeltaAtk**, không phải Drone_Get_Datas:

```
allBasicAtk = [500,600,800,1250,1500,1800,2300,2800,2535,2500,1251,2680]
allDeltaAtk = [.16f]*12
```

GOT2add998/2add9a0→hai SHA-named fields→InitializeArray12 float→store10/18.
Mỗi48 byte dùng có hash đúng; raw56B thêm8 padding. Price24 dùng96/104B tương tự.

GetPlayerPower1263860 gọi GetDroneLevel(sourceID) **trước** đọc array, rồi dùng
sourceID−indexDefault, **clamp độc lập** theo độ dài hai array. Numeric display:

```
power = f32(basic[indexBasic] * f32(1 + f32(delta[indexDelta] * level)))
rounded = round-to-nearest, ties-to-even  # miền finite Int32
```

SetPlayerInfo12605d8 gọi GetPlayerPower, kết quả qua string concat rồi setter của
textDispDamage48. Model kiểm numeric/rounding, không hứa locale/string formatter.

**Không được thay bằng combat GetBaseDamage report90.** Ví dụ level0/source20001:
UI basic500, combat base450; source20003:UI800, combat6000. UI helper không đưa rank
hay ability21 vào phép tính trên. Direct-call census thân Board có **0 direct site**
tới14da6f0 — chỉ là direct census, không proof không thể đi qua callback/indirect.

Vì vậy yêu cầu đọc consumer của **Board_Drones ctor và hai attack arrays** đã có
câu trả lời A cho binding/calls, B cho pseudo-code; không đóng các Board_* khác
hay skill consumer chỉ vì Drone_Get_Datas raw liệt kê method.

## 6. Góp ý cụ thể gửi spec, không sửa hộ nhánh kia

Snapshot ecff896c còn các điểm cần sửa:

1. Row9/MISSING + DATA_SYNC cuối file còn ghi wing/drone chưa report. **Report90 đã
   có** codebf4827ae2/CI40216724849 SUCCESS. Nhờ áp và ACK90 theo đúng phạm vi:
   shared Level + wing1/source10003; all12 drone implementation laws; không all24
   wing/prefab source-ID mapping/serialized turnRate3 live value/DPS closure.
2. HP writer không còn D vì chưa đọc. Thay bằng công thức và3 loại writer§2–4;
   giữ điều kiện HP inputs/history, không nâng runtime2500 của một tàu thành universal.
3. Không dùng GetBaseDamage mới để “xác nhận” bảng Board cũ. UI static12 và price24
   có consumer riêng§5; UI power ≠ combat damage và không damage×rate proxy.
4. Trong cùng MISSING, §2.1 giữ unknown thứ tự nạp listMapDatas nhưng §5 gạch xong
   “bind576”. Cần tách **phân loại cấu trúc đã xong** khỏi **binding entry cụ thể**,
   không để một việc vừa DONE vừa UNKNOWN. Không yêu cầu dump lại576 blob.
5. DATA_SYNC cuối còn “chưa ACK89” trong khi ACK89 đã ở6400668714. Đồng bộ ledger
   với ACK88/89 và phân biệt handoff90 chưa ACK. Peer tự báo≠đã review độc lập cả spec.

Đã xử lý yêu cầu HP writer + consumer Board_Drones bằng chain/fixtures, không chỉ
thêm queue. Việc sau:23 wing implementation còn lại, drone prefab/loadout sourceID
và serialized turnRate3; rồi named map/save consumers còn mở. Không yêu cầu thêm
screenshot/runtime để đọc tiếp static, không merge/push peer.
