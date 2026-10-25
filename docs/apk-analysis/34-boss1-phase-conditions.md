# 34 — Điều kiện chuyển pha Boss-39002 (PROVISIONAL)

Đọc trực tiếp Boss1_Director.asm.txt và field offsets dump.cs; script kiểm
bằng chứng `tools/verify/boss1_conditions.py` assert 11 instruction tại RVA.
Raw diễn giải và SHA256 asm: `raw/animation-audit/boss1-conditions.json`.

## Kết quả chính

Trong `OnGunDie` không thấy ngưỡng phần trăm HP hoặc chờ bộ đếm súng về zero.
0x150052c–0x1500538 đọc countGunCanHit @0xc0, trừ 1, chỉ lưu nếu kết quả >=0.
Sau đó nhánh 0x1500598 đọc **countTurn @0xc4**, không phải countGunCanHit.
Không có kiểm tra zero của countGunCanHit trước ClearGuns trong hàm này.
Đây chỉ là kết luận phạm vi hàm; không loại trừ điều kiện HP ở caller.

Pseudocode đường normal (bỏ null/bounds exceptions và side FX):

```
if countGunCanHit - 1 >= 0:
    countGunCanHit -= 1
Disable collider Behaviours
if countTurn == 0:
    StopAllCoroutines()
    disable gun1Static, gun1Rotate, gun1Head
    disable allHpParents[0]
    redirect Obj_Collider target to allHpParents[1].transform
    Obj_Collider.Init(true)
    SetAttachmentDefeatGun1(0..3)
elif countTurn == 1:
    disable allHpParents[1]
    redirect Obj_Collider target to allHpParents[2].transform
    Obj_Collider.Init(true)
    SetAttachmentDefeatShields(0), SetAttachmentDefeatShields(1)
    disable gun2Slots
else:
    SetAttachmentDefeatBigGun()
    disable gun3Slots
    disable allObjColliders' gameobjects
ClearGuns(countTurn)   // 0x15008e0
countTurn += 1         // 0x15008e4–0x15008f0
```

`ClearGuns` chọn state trước khi tăng turn:

| old countTurn | State field | Tên prefab | Track / loop | Tiếp theo khi Complete |
|---|---|---|---|---|
| 0 | +0x58 | Chuyensangattack2 | 0 / false | BossWork → Attack2 → loop Attack2 |
| 1 | +0x60 | Chuyensangattack3 | 0 / false | BossWork → Attack3 → loop Attack3 |
| khác (kể cả 2) | +0x38 | Dead | 0 / false | BossWork → Defeat |

Đường nhánh normal đi qua các cleanup loop. Null/bounds exception không tăng
turn. Chưa loại trừ callback lặp/reentrant; không giả định turn chỉ có 0..2.

## HP source được đổi theo pha

- Attack1 gọi SetHpSource(0) và StartCoroutine(IEAttack1).
- Attack2 bật allHpParents[1], dựng Action<GameObject> rồi đăng ký bằng
  interface dispatch; enable lại Behaviour của collider, bật gun2Slots.
- Attack3 tương tự với allHpParents[2], bật gun3Slots.
- SetHpSource(index) bật HP parent và cũng có delegate/interface registration.

Prefab serialize 3 allHpParents và một allObjColliders. Chưa quy số phần tử
này thành 3 thanh HP trên UI; cần nối object/component cụ thể.

## Còn cần chứng minh

1. Delegate metadata tại registration trỏ method nào; slot interface nào là
   sự kiện death. Assembly có `blr x8`; không đặt tên target chỉ từ suy đoán.
2. Bóc component HP của từng allHpParents, callback được gọi khi nào và có
   guard tránh gọi lặp không. Vì vậy chưa nói chắc "mỗi súng chết = một pha".
3. Wait/yield của IEAttack1 và điều kiện dừng; các boss khác dùng Director
   khác không tự kế thừa kết luận Boss-39002.
