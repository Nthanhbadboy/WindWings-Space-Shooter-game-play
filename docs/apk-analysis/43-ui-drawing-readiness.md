# 43 — Đã đủ để vẽ UI stage đầu chưa? (PROVISIONAL)

## Quyết định giao việc vẽ

**Đủ để bắt đầu wireframe/bản vẽ tĩnh có tham chiếu APK cho các board lõi. Chưa
đủ để giao bản vẽ sát nguyên bản của toàn bộ onboarding và mọi trạng thái stage 1–3.**
Không cần chờ mọi logic gameplay mới vẽ Home/Map/Stage/Endgame. Nhưng không được
bịa tutorial overlay, thứ tự popup, nút ẩn/hiện rồi gọi đó là dữ liệu gốc.

Lần kiểm này đã nhận raw mới: Actions **40176643619 success**, commit dữ liệu
**daa2c3a03**. Report 42 là snapshot cũ; các mục “đang chạy/chưa nhận native” ở đó
được cập nhật bởi báo cáo này. Không dùng build điện thoại khác làm bằng chứng.

## 1. Bộ đầu vào vẽ đã nối được

`tools/verify/ui_drawing_readiness.py` đọc **ui/_index.csv hiện tại**, không gom
hàng chục nghìn file lịch sử làm số màn. Mỗi visual node có source/hash, path,
local position/scale, active trong prefab, text/key/tiếng Việt nếu có, sprite và
candidate ảnh/contact-sheet/tile. Raw:
`reverse-engineering/raw/ui-audit/drawing-inputs.json.gz`.

**Sửa một lỗ hổng join:** `docs/assets/sprites-index.csv` dùng tên file đã sanitize
(ví dụ `NutBuySkin_1`); layout giữ tên Unity `NutBuySkin 1`. Đã nối tên Unity gốc
qua `datas/sprites.csv`, rồi (type,path_id) sang gallery. Không tự thay dấu cách
bằng underscore: có collision/suffix. Join ở bước layout vẫn theo tên, vì bản
layout cũ chưa lưu sprite PPtr; do đó gọi là **candidate**, không exact binding.

Asset gốc nằm ở draft release `windwings-assets-1.3.118`, không commit PNG/font
lớn vào repo. Preview: `docs/assets/contact-sheets/`, tra gallery bằng tile.
Nhãn category `unclassified` không có nghĩa ảnh không dùng cho UI.

### Coverage vẽ từ snapshot daa2c3a03

Bảng dưới tính theo subtree serialize, có cả popup con/inactive template; không
phải số phần tử cùng hiện lên màn hình. Sprite = component có trường sprite có
tên, gồm cả component ngoài SpriteRenderer. Text Việt = key occurrence tìm thấy
trong i18n/vi.json, không phải toàn bộ text động đã giải.

| Board | Nodes | Có local position | Sprite có candidate / có tên | Key Việt / key |
|---|---:|---:|---:|---:|
| Board_Maps | 4237 | 4237 | 2419/2429 | 113/114 |
| Board_Players | 1790 | 1790 | 607/619 | 37/38 |
| Board_Drones | 976 | 976 | 413/422 | 30/30 |
| Board_Reborn | 837 | 837 | 355/369 | 34/35 |
| Board_Endgame | 822 | 822 | 352/355 | 33/33 |
| Board_Stage | 802 | 802 | 347/358 | 26/26 |
| Board_Reborn_IAP | 369 | 369 | 161/168 | 6/6 |
| Board_Reborn_IAP | 330 | 330 | 135/143 | 6/6 |
| Board_Reborn_IAP | 257 | 257 | 98/104 | 4/4 |
| Board_Home | 198 | 198 | 58/58 | 11/13 |
| Board_Pause | 92 | 92 | 42/42 | 12/12 |

## 2. Vẽ được gì ngay, phải gắn nhãn gì

| Deliverable | Có thể bắt đầu? | Giới hạn phải ghi trên bản vẽ |
|---|---|---|
| Home, Map/chọn stage | Có — wireframe và asset reference | button lock/unlock/offer theo tiến trình chưa đóng; map không tự coi là stage 1 state |
| Stage/pre-battle và popup thiếu energy/follow tutorial | Có — tách từng panel | không bật đồng thời mọi popup con; giá trị stage/mode/mission/item là placeholder có nguồn |
| Endgame victory/defeat | Có — tách hai trạng thái | không mặc định Back/Replay/Continue đều hiện ở tutorial đầu |
| Pause, revive thường/IAP | Có — bản tĩnh | ba prefab Reborn_IAP trong index là variant riêng, chưa biết nhánh chọn |
| Chọn/nâng cấp tàu, drone | Có — màn tham khảo | không khẳng định người mới phải ghé đây sau stage cụ thể nếu thiếu branch |
| Tutorial điều khiển/đổi tàu/drone/skill | Chưa đủ bản vẽ sát gốc | có code và PPtr panel, nhưng layout panel gameplay đang thiếu trong exporter cũ |
| Prototype click-through first-clear 1→2→3 | Chưa đủ để gọi đúng APK | cần trạng thái lưu, finish/skip, popup queue và destination xác nhận |

Đây là kết luận theo phạm vi các màn đã kiểm, **không phải toàn bộ UI của game**.

## 3. Đã giải thêm gate tutorial bằng native — không còn chỉ dựa tên hàm

Raw giữ asm excerpt và SHA256: `ui-audit/early-native-gates.json`.
Tái kiểm: `python3 tools/verify/early_ui_native.py` (5 kiểm tra branch/instruction).
Call target resolve từ RVA trong dump:
`0x14efdec = GP_Setup.get_Instance`, `0x14f0da0 = GP_Setup.get_stageIndex`,
`0x14f4a14 = GP_Tutorials.get_IndexTutorial`,
`0x14fa7b0 = GP_Tutorials.IsTutTouchSkillDone`.

| Getter | Điều kiện observed trong body | Nhánh của CheckRunTutorialNew |
|---|---|---|
| hasTutStage1 | stageIndex == 0 và IndexTutorial == 0 | TutMoveFingers; TutTransform(index=1, panel=tutobjChangePlane, delay argument=9f) |
| hasTutStage2 | IndexTutorial == 1 và stageIndex == 1 | TutDrones(panel=tutobjUseDroneSkill, delay argument=2f) |
| hasTutStage3 | stageIndex == 2 và !IsTutTouchSkillDone() | Nếu Board_Talents.GetTalentIndex != -1: TutTalents(panel=tutobjTouchSkill, delay argument=3f); -1 đi nhánh skip riêng |

Tên getter gợi stage hiển thị 1/2/3 nhưng bảng ghi **numeric stageIndex** thật;
chưa dùng bảng này làm chứng minh phép đổi nhãn hiển thị. Delay argument không
đồng nghĩa thời điểm tuyệt đối overlay hiện trong trận; còn coroutine chờ/input.

**Điểm quan trọng cho bản vẽ Endgame:** `SetupTut` @0x126cac4 kiểm
IndexTutorial >1 thì set isReady=true. Với <=1, nó set isReady=false và gọi
GameObject.SetActive(false) trên **btnContinue(+0x88), btnReplay(+0x80),
btnBack(+0x78)**. Vì vậy vẽ kết quả đầu game như màn kết quả thông thường với ba
nút luôn hiện là sai ở nhánh này. Còn phải trace callback bật lại để chốt luồng.

Có instance serialized GP_Tutorials path 7123/GO1902. Panel refs cụ thể:
control1909, changePlane1904, useDroneSkill1906, touchSkill1911, cover1908;
tutSettings và tutSettings2 cùng trỏ GO634. Không vẽ thành hai panel khác nhau
chỉ vì có hai field. Nguồn: typetrees/GP_Tutorials.jsonl.gz.

## 4. Vì sao chưa hứa bản vẽ pixel-accurate

Exporter layout cũ có local_pos/scale và một phần rect sizes, nhưng chưa giữ đủ:
- font asset/material, cỡ chữ, alignment, autosize/margin/overflow;
- sprite PPtr, draw-mode/size (sliced), tint/flip, sorting layer/order;
- camera/world-to-screen và anchor logic runtime/safe area;
- animation/focus/disabled/pressed state, text/giá/reward thay lúc chạy;
- tutorial panel có thể là sibling, không nằm dưới root GP_Tutorials.

Không lấy local_pos cha-tương-đối làm tọa độ pixel màn hình. Không coi thiếu
RectTransform là thiếu vị trí: nhiều UI dùng Transform + SpriteRenderer.
Blank serialized text có thể là text runtime, không tự điền bằng phỏng đoán.

Đã sửa exporter cho lượt tiếp: giữ visual_properties (TMP/sprite), stable asset
ID thay Python object id; chọn thêm GP_Tutorials/Tut_Settings roots và xuất các
panel được GP_Tutorials tham chiếu local (kèm trạng thái unresolved nếu lỗi).
Các cải tiến này **chưa được tính là raw đã xuất** trong coverage bảng trên.

## 5. Brief để bắt đầu vẽ mà không làm sai phạm vi

1. Vẽ bộ Home → Map → Stage; Endgame thắng/thua; Pause/Revive; Player/Drone.
2. Mỗi panel riêng một frame, trạng thái trong prefab chỉ làm reference.
3. Mỗi asset ghi source node + gallery tile; không redraw từ ảnh điện thoại.
4. Tạo riêng frame Endgame tutorial <=1 với ba nút tạm ẩn; flag/callback mở lại còn OPEN.
5. Để placeholder có nhãn cho tutorial gameplay chưa đủ layout và popup queue
   chưa giải. Không nối thành flow khẳng định first-clear cho đến khi có branch evidence.

**Chốt:** bắt đầu vẽ bộ màn tĩnh được ngay; “đủ toàn bộ UI stage 1–3 đúng gốc” thì
chưa. Các khoảng thiếu đã có đường lấy raw, không cần designer tự đoán.
