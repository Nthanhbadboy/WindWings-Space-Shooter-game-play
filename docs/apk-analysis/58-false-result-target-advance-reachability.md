# 58 — Đường static victory=false → target advance, có điều kiện

**PROVISIONAL — chỉ dữ liệu APK gốc; chưa runtime replay.**
Scope: GameMode0, IsBranchfalse, LevelCurrent0; tiếp nhánh mission thường report57.
Không phân tích Premium/reborn, không khẳng định mọi loại defeat dùng đường này.

## 1. Khác report57 ở đâu?

Report57 chỉ chứng minh block tăng StageTarget không tự test incoming victory.
Lần này nối ngược **CheckEndgame → closure bool → MoveOutPlayer → callback →
OpenBoardVictory**, và nối xuôi setter target xuống preference write.

Có conditional static witness truyền **false** tới cùng block tăng target.
Đây mạnh hơn “không thấy victory guard cục bộ”, nhưng vẫn khác một session
chơi thật: external events, component validity, coroutine cancellation và
actual reachable kill counts chưa được replay.

Raw bundle: `reverse-engineering/raw/endgame-missions/false-result-reachability.json.gz`.
Collector: `tools/verify/endgame_false_reachability.py`.
Giữ nguyên15 bodies +21 checks, metadata/calls, source SHA, declarations của
interface (không bỏ IHealth/IPlayer vì parser chỉ nhận class).

## 2. Trigger check kết quả và gate ban đầu

GP_Manager.<Start>b__11_7 @14f6104 tạo Action trỏ
**GP_Manager.<Start>b__11_11 @14f6190** (metadata slot2ae9030), rồi gọi
GP_Endgame.StartCheckEndgame14f052c tại14f6188.
StartCheckEndgame dừng check coroutine cũ nếu có, tạo/chạy CheckEndgame.
Đây là consumer của final-wave event đã bóc report53; không phải mỗi enemy
chết đều gọi thẳng OpenBoardVictory.

CheckEndgame.MoveNext14f13d0 kiểm tra:

- GP_Datas.listActiveEnemies instance+70.Count **==0**, tại14f1510..1c;
- GP_States.gameState static+0 **Playing=1**, tại14f1550..58.

Nếu chưa đủ, yield **WaitForFixedUpdate**, không phải poll bằng0.5s hay2s.
Khi đủ thì set local quit flag, tạo closure có victory+10 và this+18, disable
Collider2D[] lấy trên serialized player Transform bằng GetComponents.
Closure ban đầu true tại14f15fc, rồi được sửa theo gameplay mode/mission.

## 3. False được tạo thật trong coroutine, không suy từ tên method

Trong GameMode0 + IsBranchfalse, nhánh14f17fc:

```text
count = GP_Datas.killCount                  // static+1c
maxCount = GP_Datas.Instance.countEnemies    // instance+58
result = Board_Endgame.GetMissionCompleted(count,maxCount)
closure.victory = result >= 0
```

Các điểm native:14f1818,14f182c,14f1850,14f185c..64. `mvn` rồi logical shift31
là sign-based test result>=0, không phải result==2/“phải3 sao”.

Tiếp theo lấy **GetComponentInParent<IHealth>()**, dispatch interface **slot1**
(GetCurrentHealth, đã đối chiếu dump.cs). Nếu **health==0**, set closure.victory
false tại14f18fc rồi join summary14f1984.

So sánh native là **==0**, không tự sửa thành <=0. Nếu health nonzero mà result
âm, code không reset victory thành true. Đường nonzero gọi IPlayer **slot0
SetVictory()**; tên SetVictory không chứng minh closure bool được đổi thành true.
Nó không nhận/ghi closure tại callsite này; implementation là external boundary
của witness, chưa emulate toàn bộ tác dụng phụ.

## 4. False không bị loại trước move-out

Join14f1984:

1. HidePause.
2. timeScale=1.
3. Summary.
4. **GP_Display.SetEndgame(closure.victory)** tại14f19c0..c8.
5. **WaitForSeconds(2)** tại14f19dc..e8: **scaled**, khác reveal0.5 realtime
   của mission UI report57.

Resume state1 tại14f16b0 gọi Action `_endgame` rồi tạo Action trỏ
**GP_Endgame.<>c__DisplayClass4_0.<CheckEndgame>b__0 @14f13ac** từ cùng closure,
truyền sang MoveOutPlayer14f0768. Đoạn này không có `if(victory)` trước move-out.

`_endgame` resolve về GP_Manager.<Start>b__11_11: đổi gameState sang **Endgame3**,
xử lý cleanup/display. Không phải callback truyền true thay cho bool cũ.
External calls/event handlers vẫn là giới hạn chưa replay.

Closure callback đọc victory+10 vào **w1**, this+18 vào x0, tailcall
**OpenBoardVictory14f0830** tại14f13c4. Không có bool filter tại callback.
Còn `<VictoryNow>b__5_0` là callback **riêng**, truyền literaltrue tại14f1318;
không được lẫn hai callback này.

## 5. Move-out và timeout không cùng clock với reveal mission

MoveOutPlayer restore timeScale1, dừng move coroutine cũ nếu có, tạo MovePlayer,
StartCoroutine và giữ handle tại+38. Factory giữ cùng `_gameEnded` Action trong
MovePlayer coroutine+28.

MovePlayer có bốn coroutine states, dùng byte jump table ở VA77a13a với branch
base14f1c00. **Không suy state order chỉ từ layout asm**: recovery run
**40186449228** đã đọc4 bytes **00 16 2d 8d** trực tiếp từ pinned libil2cpp.so
(SHA2569cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99),
lưu `raw/ui-audit/endgame-rodata.json`. State order được kiểm chứng:

| State | Destination |
|---:|---|
|0|14f1c00 — khởi chạy watchdog, wait1s scaled|
|1|14f1c58 — đặt destination đầu, chạy phase1|
|2|14f1cb4 — resume phase1|
|3|14f1e34 — resume phase2|

Phase1 lấy **world position** của player, đặt destination y−2; phase2 giữ x/z
và đặt destination **world y15** (literal41700000). Cả hai cập nhật position
với deltaTime và yieldnull theo frame. Speed accumulator tăng khoảng0.3/frame
ở phase1,0.5/frame ở phase2: **không phải các khoảng chờ0.3/0.5 giây**.
Float ở756a58≈1e−10 được so với **squared distance** để quyết định đến đích;
không phải một timing value. Giữ cả raw little-endian float bytes.

Block14f1c00 khởi chạy FixBugMovePlayerTimeOut với cùng callback trước khi
WaitForSeconds(1). Normal completion tại14f200c..20 invoke callback.

FixBugMovePlayerTimeOut.MoveNext14f1a8c:

- **WaitForSecondsRealtime(4)** tại14f1ae0..ec;
- sau đó gọi cùng `_gameEnded` Action tại14f1b1c;
- nếu movePlayer handle tồn tại, StopCoroutine(handle) tại14f1b34.

Watchdog không check victory trước invoke. Nó là fallback sau khi move-out đã
khởi chạy, **không phải deadline4s kể từ enemy cuối chết**. Còn2s scaled ở bước
trước. OpenBoardVictory mở đầu bằng StopAllCoroutines trên GP_Endgame, nhưng
chưa khẳng định mọi race/callback interleaving đều exactly-once.

## 6. Target advance và upper cap thực tế

OpenBoardVictory block14f0914..14f09b4:

```text
if GameMode == 0
   && GP_Setup.stageIndex == StageTarget
   && StageTarget < ZoneUnlocked * 10 + 9:
    StageTarget = StageTarget + 1
```

Incoming victory giữ trong w20, chưa dùng tới14f09c4. Cờ Board_Endgame.victory
chỉ nhận bool tại14f09e4, **sau** call set_StageTarget.

**Bổ sung clamp của setter, không bỏ qua:** Stage_Datas.set_StageTarget12bac5c
lấy MAX_STAGE_INDEX static+4, giữ **min(input,MAX_STAGE_INDEX)**, lưu cache+3c,
gọi PlayerPreferences.SetInt(key **StageTarget**, value) tại12bad04.
Không có victory parameter ở setter. Đây là preference write, chưa là durable
flush; không suy MAX_STAGE_INDEX bằng cap zone hoặc chapter.

## 7. Witness giới hạn áp vào stage2/3

Giả sử getters ổn định, valid components, owner/coroutines không bị huỷ,
GameMode0, IsBranchfalse, mode difficulty0, target đúng stage đang chơi,
ZoneUnlocked0 và MAX_STAGE_INDEX đủ lớn:

| State giả định khi final-wave check đủ gate | Kết quả bool | Conditional target update |
|---|---|---|
|Stage2/internal1, kill51/count262, player health nonzero|false vì51<52|1→2|
|Stage3/internal2, kill46/count238, player health nonzero|false vì46<47|2→3|
|Đủ tier nhưng health==0 tại check|false do health gate|vẫn dựa target/mode/cap, không dựa bool|

Đây là **synthetic input witness** nối threshold raw report56 với đường native,
không phải capture đã chơi thành công các session kill51/46. Actual wave movement,
kill increments và health/event state có thể ràng buộc khả năng đạt các state đó.
Cũng không áp cho player chết giữa wave còn active enemy hoặc màn reborn.

Ở Board_Endgame.SetMissions, incomingfalse nhảy127289c rồi12728c4→1272c90,
bỏ normal row scoring/star increments/save block. Vì vậy target advance và
stars không đồng nghĩa. Đường Continue chọn Home/loading còn có guards report57;
“target đã đổi” không chứng minh ngay lập tức auto-load stage kế.

## 8. Tái kiểm tra và phần còn mở

- `python3 tools/verify/endgame_false_reachability.py`
- `python3 -m unittest discover -s tests -q`: **72 tests pass**.
- Test bao phủ rebuild/source hashes, interface slots, metadata callback joins,
  bool/health branches, dispatch byte/float decode, replay != target, noncampaign, zone cap, MAX_STAGE_INDEX
  clamp và phân biệt WaitForSeconds/WaitForSecondsRealtime.

Còn mở: runtime witness, external cleanup/interface tác động gì đến coroutine,
actual movement/kill-count reachability, Continue visibility/Animator clips.
Premium vẫn giữ ngoài scope. Không thay raw evidence bằng các bảng tổng hợp này.
