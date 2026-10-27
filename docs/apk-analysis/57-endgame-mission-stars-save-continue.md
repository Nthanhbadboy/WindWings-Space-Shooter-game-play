# 57 — Tier → 3 dòng mission → sao lưu → Continue

**PROVISIONAL — raw APK gốc, static joins, không phải runtime replay.**
Scope: campaign GameMode0, nonbranch, **LevelCurrent0** (mission thường).
Không áp pseudo-code dưới đây sang special mission3/4, Chapter2, challenge hay
Premium. Numeric difficulty ModeCurrent khác với LevelCurrent.

Mức **A**: bytes, native instructions, metadata/PPtr trực tiếp. Mức **B**:
logic nối/tính từ chúng, có verifier. Cả hai vẫn là kết luận tạm thời.

## 1. Nguồn và tái kiểm chứng

- Native recovery `40185724759`: Stage_Mission, GameDatas trong
  `reverse-engineering/raw/ui-audit/extra-native/`.
- Prefab recovery `40185845817`: **boards/board_endgame**,
  resources.assets root GO113205, Board_Endgame component621494, **1070 nodes**.
  Run40185724731 trước đó export thành công nhưng preserve step thất bại;
  bản retry đã preserve thành công, không dùng status export làm status lưu.
- `reverse-engineering/raw/endgame-missions/boards_board_endgame__113205.json.gz`:
  full subtree/components, context-aware identities, raw Mono bytes + SHA256;
  input SHA khớp data.unity3d/libil2cpp/global-metadata của report54–56.
- Native Board_Endgame và RunMissions coroutine trong raw/il2cpp-consts;
  GP_Endgame, Stage_Datas, PlayerPreferences trong raw/ui-audit/extra-native.
- `mission-progress-flow.json.gz`: **18 method bodies,16 checks**, source hashes,
  resolved calls/metadata, exact UI PPtr joins và riêng block StageTarget.
- `python3 tools/verify/endgame_mission_progress.py`
- `python3 -m unittest discover -s tests -q`: **63 tests pass**.

Không resolve generated tree.m_Script bị lệch header alignment: class được đọc
bằng parsed Mono head, raw bytes vẫn giữ lại. Không dùng pointer-named stale UI
exports làm identity/resource evidence mới.

## 2. Counter đưa sang Board_Endgame không phải live list — mức A/B

`GP_Endgame.OpenBoardVictory` snapshot:

- GP_Datas.killCount static+1c → Board_Endgame.killCount static+14
  tại14f0b1c..20.
- GP_Datas.countEnemies instance+58 → Board_Endgame.countEnemies static+18
  tại14f0b30..38.

`Board_Endgame.Init` gọi SetMissions tại126c538. Trong nhánh mission thường,
SetMissions đọc snapshot pair+14/+18, gọi GetMissionCompleted tại12730c4.
Nó còn recompute Board_Endgame.victory bằng result>=0 tại12730e4..ec.

**Có gate entry:** SetMissions đọc victory trước; nhánh incoming defeat có thể
bypass phần chấm mission. Không hiểu recompute này thành “cứ đủ kill là phủ
định mọi kiểm tra player rồi thắng”. Scope model bên dưới là sau khi vào nhánh
scoring thường; không phải emulator toàn bộ endgame.

## 3. Đúng 3 row UI, đã nối đến Animator/text thật — mức A/B

Board_Endgame.listMissions serialize đúng thứ tự:

| i | Component pathID | Path dưới BOARD_ENDGAME/Parent/Parent/Parent_Missions |
|---:|---:|---|
|0|648536|Normal_Missions/Mission (0)|
|1|636132|Normal_Missions/Mission (1)|
|2|696150|Normal_Missions/Mission (2)|

Mỗi row là Stage_Mission, nối PPtr cùng serialized file đến Animator, textInfo,
textBonus; colors có2 phần tử. Raw derived artifact giữ path/identity của từng
field, không chỉ tên row. Special_Missions/Mission (3) là sMission riêng,
**không thêm vào3 row mission thường**.

`Stage_Mission.InitMission(collected,info,bonus) @13896ac`:

- textInfo dùng colors[collected XOR1].
- Animator.SetTrigger(string) tại13897ac: **Collected** nếu collectedtrue,
  **None** nếu false; đây là trigger, không phải SetBool.
- textInfo nhận info. Với collectedtrue, textBonus đổi sang chuỗi localized
  txt_completed, có color formatting; false dùng bonus argument.

`ClearMission @138c4d8`:

- SetTrigger(**Clear**) tại138c544;
- textInfo đổi colors[0], textBonus nhận bonus argument.

Không suy độ dài clip Animator từ tên trigger. Đã nối **3 row UI và saved
star semantics**; chưa gọi đó là3 icon sao sáng nằm ngang hay mô tả artwork
mà chưa resolve Sprite/animation graph.

## 4. Lưu sao là result+1, không phải result — mức A/B

`Stage_Get_Datas.IsMissionCompleted(stage,mode,i) @12c558c`:
nonbranch gọi GetStarStageMaster; return **savedStars > i** tại12c5624..30.
Vì vậy saved1 đánh dấu row0; saved2 đánh dấu0/1; saved3 đánh dấu cả3.

SetMissions trong scoring thường:

1. Đọc trạng thái đã lưu cho từng row, giữ vào listCompleted+260,
   InitMission(collected,...); đếm số row cũ completed vào w26.
2. Với mỗi i<=result mà listCompleted[i]false:
   **GameDatas.StarCount++** (127315c..68), post event60 payload1.
3. Lấy **newStars=result+1** tại12731d4.
4. Chỉ nếu newStars>oldCompletedCount mới gọi
   **SetStarStageMaster(stage,ModeCurrent,newStars)** tại1273248.
5. Nhánh sau save quay về1272c90, rồi tạo/chạy RunMissions tại1272d78..88.
   Không đọc thứ tự địa chỉ vật lý trong file asm thành thứ tự execution.

Model giới hạn: saved0..3, result−1..2, đã vào scoring normal:

```text
oldFlags[i] = savedStars > i
newRows = [i trong0..2 mà !oldFlags[i] && i<=result]
globalStarDelta = len(newRows)
savedAfter = max(savedStars, result+1)
```

Đây là guard ở caller, **không phải SetStarStageMaster tự làm max**.
Không áp model này cho saved4/5 của special missions hoặc save lỗi.

Ví dụ: saved1, result2 → thêm2 global stars, lưu3, animate row1/2.
Replay saved3, result0 → lưu vẫn3, không thêm global stars, không clear row mới.
Các row đã đạt từ trước có thể vẫn ở state Collected dù lượt chơi thấp hơn.

### Threshold report56 nay nối sang saved stars

Chỉ ở ModeCurrent0 và scoring thường đang xét:

| Stage hiển thị | Ngưỡng result0 → saved1 | result1 → saved2 | result2 → saved3 |
|---|---:|---:|---:|
|2 (denominator262)|52|117|209|
|3 (denominator238)|47|107|190|

Không phải “đủ52/47 thì thắng ngay”; còn toàn bộ gates report53, incoming
victory/player checks, và nhánh thực tế của session.

## 5. Ghi preference nào? — mức A/B, không khẳng định disk flush

- Stage_Datas.Get/SetStarStageMaster ghép4 strings thành
  **`StarStageMaster{stageIndex}_{modeIndex}`**. Getter default0.
- Setter12c4620 → PlayerPreferences.SetInt13f1a04 → tailcall
  **UnityEngine.PlayerPrefs.SetInt277cc10**.
- Global GameDatas.StarCount setter13256f0 clamp nonnegative, cập nhật cache
  static+4c rồi PlayerPrefs.SetInt với key **StarCount** tại132576c.

Đây là native preference writes. Chưa chứng minh Unity PlayerPrefs.Save hoặc
OS durable flush diễn ra tại thời điểm đó. Không dùng custom
PlayerPreferences.SaveToDisk làm bằng chứng cho Unity prefs flush.

## 6. Animation mission:0.5s realtime, có đường skip — mức A/B

`Board_Endgame._RunMissions_d__162.MoveNext @127a7ec`:

- Kiểm tra victory; scoring lại từ snapshot.
- Duyệt listMissions, bỏ row đã collected; chỉ clear row i<=result.
- ClearMission, xử lý normal reward/effect; cập nhật countMissionChecked=i+1
  tại127ac34.
- **WaitForSecondsRealtime(0.5)** tại127ac48..54 — **unscaled**, không phải
  WaitForSeconds scaled. Wait nằm sau mỗi row mới, kể cả row cuối trước khi
  coroutine đi tới completion callback; không có initial0.5s ở nhánh này.
- Sau các row, invoke callback; ordinary callback
  `<SetMissions>b__158_0 @1276b44` khởi chạy UnboxGifts.

Không lấy0.5s này làm thời lượng clip Clear, hoặc timestamp từ khi enemy cuối
chết. Các nhánh/callback sau unboxing có phần Premium, để ngoài scope.

**Continue không bắt người dùng phải chờ hết các wait này:**

- Continue đặt isQuitingtrue tại126ed4c, gọi **SkipUnbox** tại126ed50 rồi
  restore timeScale1 tại126ed5c, sau đó mới điều hướng.
- SkipUnbox gọi **StopAllCoroutines** tại126de48, không chỉ dừng unboxing.
- Normal mission path đọc countMissionChecked+270 để xử lý phần row còn lại,
  kiểm tra current result và listCompleted, ClearMission/reward cho row đủ
  điều kiện (126e2a4..126e4f4). Tên method không đủ mô tả tác dụng.
- Vì thế Continue có thể đi qua logic settle mission thay vì chờ coroutine
  tự hoàn tất. Chưa biến điều này thành tuyên bố mọi interleaving/nhấn lặp
  đều an toàn; wrapper có isQuiting guard và Continue đặt flag trước skip.

## 7. Nút Continue thật đã wired, nhưng prefab activefalse ≠ không bao giờ hiện

`BOARD_ENDGAME/Bar_Menu/Btn_Continue`, GO92306:
ButtonEvents.eventClick persistent call nhắm **Board_Endgame component621494**,
method **OnPressedButtonContinue**, m_CallState2. Không suy callback từ label.

Nút serialize activefalse. Native init/tutorial/popup có thể đổi visibility;
chưa khẳng định thời điểm hiện nút chỉ dựa vào prefab này.

Wrapper126ebcc kiểm tra isQuiting; có đường gọi Continue trực tiếp và đường
popup callback. Callback `<OnPressedButtonContinue>b__103_0 @1276814` tail
Continue126ec94. Không lấy persistent call làm bằng chứng click luôn load ngay.

Đường điều hướng đã giữ toàn bộ body raw:

- Có clamp StageCurrent theo StageTarget, fortification/star-search branches.
-126f124..134 có nhánh tăng StageCurrent+1 và clamp target; không phải mọi
  Continue đều đi nhánh này.
-126f224..250 còn victory và IndexTutorial checks để chọn Home.
- Victory phù hợp + IndexTutorial<=2 có đường LoadToLoading126f298;
  IndexTutorial1 và chưa equip drone slot0 có SetDroneUsed(0,20001), như
  report51. Đây không phải ownership grant.
- Loading→Game scene2 ở report52; scene index không phải display stage2.

## 8. Đính chính độ chắc chắn của “victory → unlock”

Nối lại raw cho thấy không được giản lược thành “chỉ victory mới tăng target”:

Trong **GP_Endgame.OpenBoardVictory**, block14f08f4..14f09b4 kiểm tra
GameMode0, GP_Setup.stageIndex==StageTarget, StageTarget<ZoneUnlocked×10+9,
rồi **StageTarget++**. Incoming `_victory` được giữ trong w20 tại14f0850 nhưng
**block tăng target không đọc/test w20**; nó chỉ được dùng sau đó.

Verifier giữ riêng cả block và kiểm tra sự vắng mặt của w20/x20 ở block đó.
Đây là bằng chứng **không có local victory predicate ở đoạn tăng target**,
không phải runtime proof “thua chắc chắn vẫn unlock”: còn phải chứng minh
reachability/call context của từng kết quả. Tên OpenBoardVictory không thay
thế được branch predicates.

Do đó tách3 sự kiện:

1. StageTarget update ở GP_Endgame;
2. stars/global StarCount write ở Board_Endgame.SetMissions;
3. Continue chọn StageCurrent/scene.

Không gộp chúng thành một bước “nhận3 sao rồi unlock rồi load ngay”.

## Còn mở

- Actual Animator graph/clip và sprite semantics của3 row; runtime visibility
  của Continue qua mọi init/tutorial gates.
- Caller reachability của target-advance khi `_victory=false`.
- Concrete Enemy_Movement completion registration/timing để nối việc pool
  trong gameplay với đường kết quả đã bóc.
- Runtime replay/durable prefs flush vẫn chưa có. Premium tiếp tục để riêng.
