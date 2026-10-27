# 41 — Kiểm handoff animation @90453024 (PROVISIONAL)

Đọc nhánh spec để tham khảo, không merge. Đối chiếu bằng raw từ Actions
40175696655 (success); không dùng runtime Premium-mod thay cho APK đang bóc.

## T1 — class nào thực sự có instance?

| Class | Instance thấy trong raw mới | Diễn giải |
|---|---:|---|
| Boss_1_Animation | 1 | Boss-39001/Enemy_Ingame/Body/Boss 1; component 674445 |
| Boss1_AnimationEvents | 0 (không có file raw) | chưa tìm thấy trong export, không đủ kết luận dead code |
| BossSpineEventHandler | 0 (không có file raw) | chưa tìm thấy trong export, không đủ kết luận dead code |

Boss_1_Animation.skeAnim → component 602882 → SDA 580611 → TextAsset 918.
8 tên state đúng bộ Xuathien/Baydi/Dead/Attack1–3/Chuyensangattack2–3.
`defeatEvent` có persistent call OnDefeated tới component 601110;
`burstEvent` có persistent call OnBusrtItems tới cùng component.
Giữ nguyên spelling OnBusrtItems trong game. Không suy hai callback này là
12 Action fields của Boss1_AnimationEvents: đó là hai cơ chế khác nhau.

Raw đầy đủ: animation-audit/legacy-boss-instances.json; bản typetree gốc giữ
call mode/arguments/callState. Cập nhật nhận định cũ: Boss-39001 có controller
Spine riêng Boss_1_Animation; không quy cả Boss-39001 và Boss-39002 về cùng
Boss1_Director chỉ vì dùng chung rig.

## T3 — Inspector-wired callbacks có thật

Sau tái xuất có 1.335 UnityEvent fields, 111 field không rỗng, 115 call;
114 call trong nhóm Enemy_/Boss/MB/MiniBoss. Report 39 giữ phép đếm đầy đủ.
Chỉ là tập class đã export, không gọi đó là toàn game.
Enemy_Movement có 2 instance moveEndedEvent không rỗng, không phải toàn bộ
981 movement đều có callback Inspector. UnityEvent inline, không phải PPtr
riêng; PPtr nằm trong m_Target của từng persistent call.

## T4 — controller graph đã có raw

Report 40: 52 controller trên 63 prefab filter CB-/Boss-/MB-, 303 parameter,
395 state, 357 transition, 302 có condition. Con số không cùng mẫu số với
roster 109/87 bên spec, chưa báo đã đóng coverage 87/87.
Raw full ControllerConstant 308 controller giữ ở
raw/typetrees/animator-controller-graphs.jsonl.gz; derived chỉ lọc 52 controller.
Parameter names lấy từ m_TOS bằng hash ID; transition conditions lấy từ
m_ConditionConstantArray, không phải đoán từ tên state.

## T2 — vẫn mở

Chưa có full-binary typed xref chứng minh ai gán 12 delegate fields. Không
coi str [xN,#0x20] toàn binary là bằng chứng nếu chưa biết type của xN.
Không tìm thấy xref trong tập exported methods cũng không chứng minh 0/12
gán trong toàn C# assembly. Cần resolve registration target hoặc mở rộng
đúng caller; không dùng kết luận vắng mặt vượt phạm vi dữ liệu.
