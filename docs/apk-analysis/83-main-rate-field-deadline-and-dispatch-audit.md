# 83 — Main-rate → field → deadline → dispatch: đủ 24 implementation

**25/10/2026 — kết luận tạm thời, APK-static.** Tiếp report82 bằng consumer thật,
không lấy bảng rate làm tốc độ phát đạn/hit/DPS. Raw gốc không sửa.

## 1. Nguồn và cách tái kiểm

- `reverse-engineering/raw/combat-chain/native/Player_Attack_*.asm.txt` cùng nested classes;
  `reverse-engineering/il2cpp/dump.cs.gz` xác nhận tên/offset field và method Unity.
- `datas/combat_rate_consumers.json`: hash từng input, 24 setup bindings, 96 access
  owner-qualified, nguyên scheduler prefix, dispatch calls/tail calls, StartAttack context,
  25 MoveNext và 14 direct WaitForSeconds sites có context.
- `tools/verify/combat_rate_consumers.py`: must-alias trên CFG, cả hai nhánh conditional,
  merge xung đột → unknown; W-write làm mất X-pointer; call clobber x0..x18;
  nested owner chỉ lấy từ field `<>4__this` đúng metadata. Access xét byte range,
  **không chỉ offset đầu lệnh**. Ví dụ ctor implementation4 `stur d0,[owner,#0x8c]`
  cũng ghi rate@0x90. Trước khi thêm byte-overlap, một search exact-offset bỏ sót chỗ này.
- Đây là kiểm các alias/access chứng minh được trong các method đã preserve, không
  tuyên bố phân tích interprocedural arbitrary pointer hoàn chỉnh. Không thấy rate read
  owner-qualified trong nested bodies; điều này không biến coroutine thành không có timer.

```sh
python3 -m tools.verify.combat_rate_consumers --check
PYTHONPATH=/home/user/test-deps python3 -m unittest discover -s tests -q
python3 datas/validate.py
git diff --check
```

## 2. Getter không đi thẳng vào một coroutine wait

Metadata base `Player_Attack.demo` là **bool@0x30**. Cả 24 SetupDatas đều gọi getter,
đọc demo, `cmp demo,0; fcsel s0,s0,s1,eq`, rồi ghi `timeRateMainCannon`.
Các lệnh mov/movk/orr xen kẽ ở 2/4/18 không thay NZCV; không bỏ qua chúng rồi
nhầm condition. `demo=false` giữ getter result; `demo=true` chọn **3.0 cho 1–23,
4.0 cho 24**. Không đồng nhất field này với bool serialized@0x28 của một class khác.

Trong inventory owner-qualified có **4 access/implementation**: SetupDatas ghi,
MainCannonShoot đọc, StartAttack đọc, ctor ghi (có scalar/wide/overlapping write).
Có **48 read sites** đã nối rõ vào hai consumer thật. Giá trị getter report82
`base × (1 − MainRatePercent)` là interval dùng cho main deadline, không phải số đạn/s.

## 3. Bảng đủ 24: field và nơi quyết định deadline

Offset trong cùng object implementation; `T` = `timeToShotMainCannon`.
Getter/store chính xác và toàn bộ scheduler prefix nằm trong JSON; bảng chỉ dẫn đường.

|Impl|Rate|T|Demo interval|Scheduler / dispatch sau deadline|
|---:|---:|---:|---:|---|
|1|`0xa8`|`0x10c`|3|extra counter; inline main emitter (rank/barrel branches)|
|2|`0x130`|`0x180`|3|extra counter; inline main emitter (rank/barrel branches)|
|3|`0xac`|`0xf8`|3|extra counter; inline main emitter (rank/barrel branches)|
|4|`0x90`|`0xe0`|3|extra counter; inline main emitter (rank/barrel branches)|
|5|`0xa8`|`0xe8`|3|extra counter; MainCannonAttack|
|6|`0x84`|`0xe8`|3|extra counter; MainCannonAttack|
|7|`0xa8`|`0x108`|3|extra counter; MainCannonAttack|
|8|`0x84`|`0xe4`|3|extra counter; MainCannonAttack|
|9|`0x9c`|`0x118`|3|extra counter; ShipCloneAttack → StartCoroutine|
|10|`0x8c`|`0x98`|3|extra counter; AttackMainCannon → StartCoroutine|
|11|`0xa8`|`0x10c`|3|extra counter; IEMainCannonAttack → StartCoroutine|
|12|`0x8c`|`0x98`|3|extra counter; MainCannonAttack|
|13|`0xa8`|`0x114`|3|extra counter; IEMainCannonAttack → StartCoroutine|
|14|`0xa8`|`0x11c`|3|extra counter; IEMainCannonAttack → StartCoroutine|
|15|`0x78`|`0xa0`|3|extra counter; MainCannonAttack|
|16|`0xa8`|`0xf8`|3|extra counter; MainCannonAttack|
|17|`0xa8`|`0x114`|3|extra counter; IEMainCannonAttack → StartCoroutine|
|18|`0xc0`|`0x118`|3|extra counter; inline main emitter (rank/barrel branches)|
|19|`0x80`|`0xb8`|3|single deadline; MainCannonAttack|
|20|`0x9c`|`0x104`|3|extra counter; MainCannonAttack|
|21|`0x8c`|`0xf0`|3|extra counter; MainCannonAttack|
|22|`0x9c`|`0xf0`|3|extra counter; MainCannonAttack|
|23|`0x9c`|`0x100`|3|extra counter; IEMainCannonAttack → StartCoroutine|
|24|`0x9c`|`0xf0`|4|extra counter; MainCannonAttack|

## 4. State machine chung là 23/24, không phải 24/24

**1–18 và 20–24:** MainCannonShoot kiểm main deadline bằng Time.get_time@0x2786dc0.
Nhánh `b.mi` chặn `now < T`; bằng nhau đi tiếp với finite operands. Sau đó:

1. Lấy count `N = numberAddMainCannonCount`, đọc time một lần khác.
2. Nếu `N < 1`, đi thẳng tới `T = now + rate`, rồi vào dispatch.
3. Nếu `N >= 1`, còn phải đủ `timeToShotMainCannonDelay` (`E`).
4. Khi đủ: đọc time mới, `turnMainCannonCount += 1`, đặt `E = now + rateAddMainCannon`.
5. Nếu turn <= N, đi **thẳng tới dispatch**, không đặt lại T.
6. Nếu turn > N: reset turn=0, đọc time mới, đặt `T = now + rate`, **vẫn dispatch**.

Vì vậy với N dương **giữ nguyên** và turn ban đầu 0, một chu kỳ counter có
**N+1 lần vào dispatch**, không phải N; đây không phải N+1 viên đạn hay N+1 hit.
Quan trọng: sau lần reset, E vừa được đặt lại cũng còn sống. Chu kỳ tiếp theo
phải vượt **cả T lẫn E** khi N>=1; không được bỏ gate E và lấy rate làm toàn bộ
khoảng nghỉ. Không có vòng catch-up trong scheduler prefix: một invocation chỉ
đi vào một dispatch, dù một emitter/coroutine có thể tạo nhiều object.
Các lần Time.get_time là call riêng, không giả định tất cả cùng một mẫu now.

**Implementation19 khác hẳn:** `0x149a320..0x149a360` chỉ main deadline@0xb8;
đủ giờ → đọc time mới → cộng rate@0x80 → ghi T → tail-call MainCannonAttack@0x149b3a4.
Không mang extra-count state machine của 23 implementation kia sang 19.

**22, 23, 24 còn refresh N ngay trong MainCannonShoot**, sau main gate và trước extra
gate: `GP_Datas.GetNumberAbility(4)`@0x14c7758, demo chọn 0, ghi count.
Sites: 22 `0x14a3354`, 23 xem scheduler prefix, 24 `0x14a7994`.
Do đó công thức N+1 phía trên cần giả thiết N không đổi qua các lượt; không mặc định
N chỉ được chốt một lần trong OnEnable. Đây là khác biệt đọc từ code, không phải
vướng mắc phải chờ runtime mới biết.

## 5. StartAttack là consumer thứ hai, có nhánh bỏ qua rate

Cả 24 có nhánh đọc rate để ghi T=`Time.get_time()+rate` khi không yêu cầu immediate.
Nhánh immediate đặt main deadline=0. 6/8/10/12/15 dùng `fmov s0,wzr` rồi `tbnz`
để bỏ qua call Time/get rate; các implementation còn lại có store wzr riêng.
Không mô tả thành “StartAttack luôn chờ rate”. Các gate victory/player/state trước đó
vẫn phải giữ nguyên. Context mỗi rate load đã lưu, không lấy một class thay tất cả.
Implementation19 immediate còn chỉnh wing timer riêng; đó không phải extra-main timer.

## 6. Coroutine: đã nối dispatch, chưa tráo inventory thành semantics hoàn chỉnh

Main scheduler trực tiếp tạo IEnumerator rồi StartCoroutine ở **9/10/11/13/14/17/23**.
5/6/7/8/12/15/16/19/20/21/22/24 tail-call MainCannonAttack; method này có thể khởi động
coroutine khác. 1/2/3/4/18 tiếp tục inline emitter có rank/barrel branches.
Đây là phân loại dispatch ngay sau scheduler, không phải phân loại “có/không coroutine”
của toàn tàu.

Đã inventory **25 MoveNext**, **14 WaitForSeconds ctor sites**. Các điểm cần phân tích
kế tiếp là code hiện có, không ghi thành “thiếu runtime”:

|Site/method|Điều đã đọc tại argument wait|Việc còn phải nối|
|---|---|---|
|6 ControlMainCannonBullet `0x14b3dd8`|s8 từ iterator@0x20|factory arg → iterator field → resume transition|
|7/9 ControlMainCannonBullet, mỗi class 2 sites|iterator@0x34; site sau đọc literal pool@0x756b0c|giải toàn bộ path/transform quanh từng yield|
|10 AttackMainCannon `0x147fc4c`|immediate **0.25**|đếm emitter theo state/rank trước và sau yield|
|11 IEMainCannonAttack `0x1482948`|iterator@0x38|factory/writer field và loop/resume|
|12 SyncAttack `0x1486db8`;17 IEMainCannonAttack `0x1496214`|literal pool@0x75700c|decode đúng cell và đường yield/next emission|
|13 ShotAllBarrels `0x148a228`|iterator@0x38|writer và barrel loop/resume|
|14 MoveObject `0x148d208`|iterator@0x34|writer và transform-vs-emission path|
|18 IESpawnHeart `0x1499b50`|s8 có assignments 0.5/1.0|CFG chọn giá trị và heart spawn loop, không coi là main rate|
|23/24 IEShootBarrels `0x14a7170`/`0x14a92bc`|s0 = s8 / float(w20), s8 load owner@0xac|w20 return/callee + rank/ability guards + barrel loop|

Không kết luận tất cả wait này điều khiển phát đạn: có movement/control/heart paths.
Không lấy 14 ctor sites làm số lần yield thực tế. Danh sách trên là câu hỏi cụ thể,
đã có RVA/raw để đào tiếp; không bị chặn bởi thiếu screenshot hay encounter capture.

## 7. Tác động bàn giao

- Import **rate + scheduler + count + extra-delay + dispatch semantics**; không dùng
  `1/rate` làm DPS hoặc tốc độ mọi projectile.
- Giữ riêng nguồn implementation N/index N−1 với source ship ID (report81/82).
- Đếm lần vào dispatch ≠ object spawn ≠ collision callback ≠ requested damage ≠ HP loss.
- Chưa hoàn thành toàn bộ 25 coroutine emission/transform semantics; không tuyên bố
  đã đóng việc này chỉ vì đủ inventory và unit tests. Phần còn lại ở §6 có thể tiếp tục
  bằng raw hiện có, không phải generic runtime limitation.

## 8. Verification

**Local:** 302 tests PASS (32.245s), `datas/validate.py` PASS, `git diff --check` PASS.
12 tests mới gồm regeneration, đủ 24 field/demo, 96 access, overlapping ctor write,
19 exception, 22/23/24 refresh, counter branch, coroutine inventory và CFG alias
clobber/merge/typed iterator/writeback. CI receipt bổ sung sau push.
Test là regression của extraction/proof, không tự nâng giả định thành APK fact hay đo gameplay.
