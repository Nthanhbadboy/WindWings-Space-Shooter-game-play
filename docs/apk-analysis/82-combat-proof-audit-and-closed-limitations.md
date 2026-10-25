# 82 — Kiểm lại chứng cứ combat: đóng giới hạn sai/quá rộng

**Tạm thời nhưng không để “chưa runtime” thay việc đọc native.** Report này tái dùng raw81,
không cần dump/media mới. Kết quả máy đọc: `datas/combat_argument_audit.json`.

## 1. 72 đối số getter đã chứng minh, không còn chỉ là candidate

`tools/verify/combat_argument_audit.py` dựng CFG trong từng body được bound theo preserved
contract. Giữ cả hai cạnh conditional branch; hợp nhất must-value của w0; x0 alias w0;
BL/BLR và unknown writes giết giá trị; iterate tới fixed point, gồm cả back edge.
Không lấy “MOV cuối theo thứ tự text” làm proof và không đoán conditional predicate.

Kết quả **72/72** call sites:
- 24 `Player_Get_Datas.GetMainCannonRate`;
- 24 `GetMainCannonDamage`;
- 24 `GetWingCannonDamage`.

Tại mọi normal CFG path tới các call site này, đối số **w0 = N−1** cho
`Player_Attack_N`, N=1..24. JSON lưu method/RVA/site/bounds, source hash, số CFG/reachable nodes.
**Đóng caveat candidate-index của81 tại đúng72site này.** Không cần thiết bị để trả lời đối số.
Proof có điều kiện “nếu call site được tới”, không khẳng định lifecycle đã chạy trên máy.

Mapping vẫn phải tách hai namespace có bằng chứng khác nhau:
- Implementation1 → sourceID10003 → ba getter truyền0.
- Implementation3 → sourceID10001 → ba getter truyền2.
- Các sourceID/demo lấy từ snapshot81; bốn source implementation2 vẫn chỉ đọc prefix đã kiểm,
  chưa gọi suffix typetree của chúng là đã giải. Proof argument không cần full source tree đó.

Không phủ định công thức `id−10001` ở consumer save/load riêng; chỉ cấm áp mù nó thay
chuỗi source prefab→implementation→stat argument ở combat này.

## 2. Main-rate modifier không còn ghi chung chung “chưa đọc modifier”

Native `Player_Get_Datas.GetMainCannonRate0x14e3cd8`:

```
base = StartMainCannonRate[playerIndex]  # static array@0x80
percent = GetMainCannonRatePercent()
result = base * (1 - percent)
```

`GetMainCannonRatePercent0x14e3d6c` gọi **Tech_Datas.GetTechStatLevel(1)0x139d96c**,
không phải spawn rate, rank tàu hay giá trị tùy suy tên. Exact binary32 literals lấy từ
raw81 `referenced-cells.json.gz`, kiểm VA/width/bytes; nhánh đọc tại0x14e3db8..e18:

| Tech stat1 level | Literal bytes LE | Percent binary32 |
|---|---|---:|
| ≤0 | immediate zero | 0 |
| 1 | 8fc2f53c | 0.029999999329447746 |
| 2–3 | cdcc4c3d | 0.05000000074505806 |
| 4–6 | 0ad7a33d | 0.07999999821186066 |
| 7–8 | cdcccc3d | 0.10000000149011612 |
| ≥9 | 8fc2f53d | 0.11999999731779099 |

Base24 floats decode `<24f` từ `ia-resolved.json` record InitializeArray0x14e5eb4;
store0x14e5ec4 nối array vào field@0x80, getter0x14e3d28 đọc cùng field.
Raw field blob104bytes có8byte đuôi; array length24 tiêu thụ96bytes, giữ nguyên fullraw,
không unpack trailer như phần tử25/26. JSON giữ fullraw và24values.

**Đã đóng:** giá trị/nhánh của common getter rate và stat1 modifier tại các hàm trên.
**Việc khác chưa làm trong audit này:** theo giá trị trả về qua timer/coroutine của từng tàu,
bao gồm demo override hoặc transformation sau getter. Đó là consumer analysis cụ thể,
không phải “không có dữ liệu”, và không ảnh hưởng proof đối số hay tier table đã xong.

## 3. Offset0x2f đã có tên, không phải field mơ hồ

`dump.cs.gz` khai báo `Enemy_Datas.IsCaAttack //0x2F` và
`CurrentHealthPoint //0x28`. `Enemy_Controller.OnTakeDamage`:
0x1582b54/58/5c chặn currentHP≤0;0x1582b60/64 chặn IsCaAttack=false trước nhánh damage.
**Đóng câu81 “không tự đặt tên flag khi chưa đối chiếu”: dump đã đủ đối chiếu.**
Tên `IsCaAttack` giữ đúng chính tả source; không đổi thành invincible/IsAlive theo trực giác.

## 4. 38 ends_clean=false là kết quả heuristic, không phải38 body thiếu

Exporter `il2cpp_consts.py` kiểm có ret/b/br **trong12instruction cuối**. Audit từng record:
- **36 coroutine Reset**:56bytes, có call ctor `System.NotSupportedException`0x2107de0,
  instruction cuối BL0x110d11c. ELF usage `0x2adb940→0x2ba8e38` xác nhận exception type.
- **2 OnDrawGizmos** (Bullet_Reflex1/Bullet_SpiderSilk): có RET ở0x1596608/0x1599578,
  nhưng suffix failure block tới BL0x110d250 làm RET rơi ngoài cửa sổ12instruction.

JSON giữ đủ38 start/end/tail/ret/ctor sites. **Không dùng cờ38 này làm lý do xin dump lại
hoặc nói gameplay methods bị cắt.** Cờ gốc vẫn giữ nguyên để có thể tái kiểm tool.
Nhận diện pattern không yêu cầu suy rằng exception helper là một normal returned call;
CFG argument audit ở§1 vẫn bảo thủ, không tự cho helper là noreturn để làm proof dễ hơn.

132 minimum-span overlap records của81 là vấn đề khác: đã clip bằng next declared RVA.
Không trộn chúng với ends_clean heuristic; audit này không tự tuyên bố mọi body toànbuild exact.

## 5. 68 collider root không có receiver: đã phân loại cụ thể

Không gọi chung “receiver chưa biết”:
- **64 rootTransform pointer null** trong serialized source.
- **4 Obj_Collider** trỏ tới root chỉ có Transform/Animator, **không có MonoBehaviour**:
  resources.assets pathIDs588115,606116,666810,697928. Hai pathIDs cuối chung root166515.

Native Obj_Collider.Init ghi init=true trước root check; nếu root null, nhánh return không
resolve interface; GetIDamageable trả cached@0x28. Với fresh zero-initialized object và không
có forceinit/đổi root thì đường null/cache này đã xác định — không cần gọi là mystery.
Nếu runtime sửa root/cached state thì cần đúng writer/callsite đó, không đòi pool-history rộng.
Với4 root không MonoBehaviour, static source không có implementation để GetComponent tìm;
không dựng receiver giả, cũng không nói người chơi chắc chắn đã va chạm các prefab này.

## 6. Sổ việc còn lại phải chỉ đối tượng, không ghi giới hạn chung

| Câu hỏi | Trạng thái sau audit | Việc đúng nếu cần tiếp |
|---|---|---|
| Đối số3getter×24tàu | CLOSED static72/72 | Dùng proof JSON, không đòi video |
| MainRatePercent/common base array | CLOSED branch/bytes/field binding | Consumer timer không đồng nghĩa getter |
| Tên enemy flag@0x2f | CLOSED IsCaAttack | Giữ nguyên source spelling |
|38unclean có phải thiếu code? | CLOSED heuristic classification | Không gọi38truncation |
|68roots không receiver | CLOSED serialized classification | Chỉ reopen nếu có concrete runtime writer contradiction |
| Concrete bullet/callback implementation1 | CLOSED static81§D | Không gỡ proof vì chưaplayback |
| Nhịp đủ24 implementation | SOURCE PRESENT, consumer semantics chưa audit hết | Đọc SetupDatas→Update/MoveNext→SetBullet của từng family trong raw81, không xin lại dump |
| HP delta với user callbacks | Native order CLOSED; callback bodies cần theo từng binding | Enemy_Health0x1584820 gọi callback trước rereadHP0x158482c; phải nối callback cụ thể nếu cần delta sau callback |
| Số hit/TTK của một encounter | Chưa chọn encounter/loadout/input schedule để tính | Pin stage/wave,source ship,tech/rank,collision policy rồi tính; không kết luận chỉ từ damage×rate |

Đây là trạng thái công việc có phạm vi, không phải tuyên bố “không thể bóc”. Không lấy
FPCR/render/playback làm điều kiện tiên quyết cho những câu hỏi static đã giải được.
Các unit tests có case phản chứng bypass-MOV, disagreeing branches, loop backedge, alias/call
clobber; không chỉ hardcode expected24index. Cảhai loại bằng chứng (raw và algorithm scope)
đều phải giữ khi chuyển cho AI thiết kế mới.

## 7. Audit phát hiện và sửa lỗi parser thật, không che bằng caveat

Kiểm contiguous4-byte instruction span cho các body proof phát hiện regex cũ dùng `\s*`
sau mnemonic có thể ăn newline của `ret` không operand, nuốt instruction kế tiếp vào text
operand. Sửa cả verifier81 và audit82 dùng space/tab-only. Raw assembly **không thiếu**.
Thêm test `ret`→`bl` và buộc body proof liên tục, không có computed `br` chưa resolve.
Sau sửa, inventory direct sites **13.144→13.616** (+472); số method/indirect/caps và
**72/72 CFG argument proofs không đổi**. Contract81 đã regenerate, không sửa raw để hợp test.
Con số13.144 trong báo cáo81 là lịch sử trước parser fix; lấy contract hiện hành làm inventory.

## 8. Kiểm tra bàn giao

12tests mới, full **290tests local PASS** (Pillow12,28.503s); datasvalidate/diffcheckPASS.
Raw/derived provenance giữ `raw/combat-chain/argument-audit-derivation.json`;81derivation
được cập nhật hash sau parserfix, raw input không sửa. FinalCI ghi riêng sau push.

**Final Verify40207070647 SUCCESS** cho codecd2b317dd: regenerate/pinneddependency/regressionsteps
PASS. Peer notification PR12comment6399518575; gửi task chưa phải peer đã áp dụng sửa.
