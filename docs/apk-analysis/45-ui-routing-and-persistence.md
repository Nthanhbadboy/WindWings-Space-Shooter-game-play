# 45 — Continue routing và tutorial persistence (PROVISIONAL)

## Bằng chứng native mới kiểm

`tools/verify/ui_routing.py` xuất raw
`reverse-engineering/raw/ui-audit/routing-and-persistence.json.gz`:
8 method selections, asm nguyên đoạn + SHA256 nguồn, direct-call sites resolve
bằng RVA của dump, declaration ScenesManager.Scene/Stage_Datas/Board_Endgame.
6 instruction checks; không resolve indirect delegate bằng đoán tên.

### 1. Continue không phải một cạnh “Next Stage” duy nhất

`OnPressedButtonContinue` @0x126ebcc:
- Nếu `isQuiting` (+0xc8) đang true thì return.
- Đọc `btnX20Coins` (+0x1a0). Nếu activeSelf=true thì gọi
  `popupNotice` (+0x190).SetPopup, confirm delegate là callback
  `<OnPressedButtonContinue>b__103_0` @0x1276814.
- Callback này tail-call `Continue` @0x126ec94. Nếu btnX20Coins không active,
  hàm nút gọi thẳng Continue. Cần giữ một trạng thái confirmation riêng trên
  bản flow; không suy popup này xuất hiện ở mọi clear đầu.
- Continue set isQuiting=true, SkipUnbox và Time.timeScale=1 trước các nhánh.

Body Continue có cả hai call:
`LoadSceneHome` @0x126e5cc và `LoadToLoading` @0x126f3c8.
Tên **LoadToLoading dễ gây hiểu nhầm**: fallback của nó gọi
ScenesManager.LoadScene(**2 = Game**), không có enum scene tên Loading.
LoadSceneHome fallback gọi LoadScene(**1 = Home**).
Nếu FadeScreen tồn tại thì đi qua FadeOut callback trước; không dùng fallback
để khẳng định tên/đích của mọi delegate fade khi chưa resolve metadata.

Nhánh @0x126f220 đọc bool từ static slot0x2adc6b0,+0:
- false → LoadSceneHome;
- true và IndexTutorial>2 → LoadSceneHome;
- true và IndexTutorial<=2 → LoadToLoading.
Trước nhánh đó còn logic mode/zone/stage/stars. Không viết đoạn này thành toàn
bộ routing của mọi mode. Slot metadata cần kiểm độc lập để nâng tên bool thành
victory thay vì suy theo ngữ cảnh.

### 2. Có chuẩn bị drone ở nhánh tutorial

Trong nhánh true, IndexTutorial<=2 nói trên: nếu IndexTutorial==1 và
Drone_Saved_Datas.GetDroneUsed(slotIndex=0)==0 thì gọi
SetDroneUsed(slotIndex=0, playerIndex=**20001**, tức 0x4e21).
Đây là conditional fallback; không nói mọi người chơi đều nhận drone mới hoặc
quà miễn phí. Không tự đổi `playerIndex` trong signature thành item reward.

### 3. Tutorial index không chỉ nằm trong biến RAM

`GP_Tutorials.set_IndexTutorial` @0x14f9f84:
1. Ghi giá trị nhận vào static +0x10 (field indexTut theo dump).
2. Load key qua metadata/string slot0x2adc200.
3. Tail-call **PlayerPreferences.SetInt(string key,int value)** @0x13f1a04.

Đã chứng minh setter gọi preference API. **Chưa chứng minh** key literal là gì,
custom wrapper flush ra disk lúc nào, hoặc kill app ngay thời điểm nào vẫn giữ
được tiến trình. Không gọi đây là test app restart đã thành công.

## Lỗi pipeline phát hiện trong vòng này

Analyze40180363840 kết thúc **failure** ở bước Commit reports; một số bước có
continue-on-error nên không dùng việc đã có artifact để chứng minh mọi export
thành công. Log download từ sandbox trả EOF, chưa có đủ log để chốt nguyên nhân
exit128. Workflow cũ còn `git pull --rebase --autostash || true`, có thể che lỗi.

Commit28296be16 sửa không nuốt lỗi pull, replay generated output với strategy
thích hợp và push rõ branch. Thêm `/tmp/apk/unity/raw/ui` vào artifact: trước đây
artifact có script.json nhưng **không có raw UI**, nên nếu commit bot thất bại
không thể lấy layout mới từ artifact đó.

Có job recovery riêng lấy script.json của run40180363840, chỉ giữ metadata UI
cần thiết (không asset/binary). Recovery lần đầu40180792840 failure vì chưa nhận
được output dùng được; không gọi đó là đã resolve. Bản mở rộng name-filter đang
thu hồi để kiểm GOT slots vs metadata addresses, không thay chúng cho nhau.

## Việc còn mở

- Nghiệm thu render-context và Map truncation của lượt export mới.
- Map GOT slot → metadata/string thật: bool và key indexTutorial.
- Resolve callback FadeOut → scene, consumer preference flush/restart.
- Thứ tự queue unlock/premium/offer và first-clear/replay/quit state matrix.

**Đầu vào vẽ tăng thêm:** tách frame Endgame tutorial/confirmation/loading-route;
không nối Continue thành “luôn next stage”, không gọi setter preference là bằng
chứng persistence runtime đã hoàn tất. Các kết luận vẫn tạm thời.

## Cập nhật trong cùng vòng: đã resolve bằng relocation, không đoán offset

Recovery **40180955473 success**, bot **633d552b1**. Raw metadata-slots.json giữ
SHA256 script.json, SHA256 libil2cpp.so và từng GOT→effective address. Native
source lấy từ XAPK cache có checksum đúng bản APKPure đang phân tích.
Recovery40180858092 trước đó đã lấy được metadata names nhưng chưa đủ join GOT;
lượt40180955473 lấp đúng bước còn thiếu này.

| GOT slot | Effective address | Resolve chính xác |
|---|---|---|
| 0x2adc6b0 | 0x2ba5400 | Board_Endgame_TypeInfo → static +0 là **victory** theo dump |
| 0x2adc200 | 0x2be6688 | key string **TUTORIAL** |
| 0x2adc840 | 0x2ba6d38 | GameMode_TypeInfo → +0 là playMode |
| 0x2adc768 | 0x2ba7030 | Home_Loader_TypeInfo → +0 là defaultBoard |
| 0x2adbde8 | 0x2baa360 | Stage_Datas_TypeInfo |
| 0x2addcc0 | 0x2bceb78 | Fade Home callback → RVA0x1276e10 |
| 0x2addcf0 | 0x2bceb80 | Fade Game callback → RVA0x1276e1c |

Hai Fade callback trong Board_Endgame.__c đã có asm: lần lượt gọi LoadScene(1)
và LoadScene(2), khớp fallback. Không còn treo đích hai callback này.
Script kiểm routing hiện giữ **10 method selections/10 instruction+join checks**.

**Các OPEN phía trên được thu hẹp như sau:**
- Tên bool đã xác nhận là victory. Nhánh sau chuẩn bị state: thua hoặc
  IndexTutorial>2 → scene Home; thắng và IndexTutorial<=2 → scene Game.
- Key preference đã xác nhận là `TUTORIAL`; setter viết key đó, chưa chứng minh
  wrapper flush/atomicity khi app bị kill.
- Continue mode Normal đặt Home_Loader.defaultBoard=6 (**BoardStage**) ở nhánh
  mặc định; zone/stars có nhánh ghi đè BoardMaps=5. Cần phân biệt **scene Home**
  với **màn Home**: vào scene Home không có nghĩa mở Board_Home.
- Stage_Datas.IsContinue/IsReplay liền nhau +0x38/+0x39 được ghi strh1, tức
  IsContinue=true, IsReplay=false trên little-endian ARM64. Không chỉ đổi màn.
- Victory callback trong report44 giờ được gọi đúng tên: bật Continue, ẩn Replay,
  tăng IndexTutorial. Không còn phải giữ tên nhánh “bool chưa biết”.

Còn OPEN: Home_Loader consumer/defaultBoard ưu tiên popup, đầy đủ queue sau
reward, crash/restart persistence; nghiệm thu raw render-context/Map lượt mới.
