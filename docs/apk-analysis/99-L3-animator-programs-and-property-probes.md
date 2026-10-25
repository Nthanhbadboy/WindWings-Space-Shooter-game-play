# 99 — L3 tiếp: controller → state → clip → thuộc tính đúng object

**26/10/2026 — tạm thời. L3 CHƯA xong hoàn toàn.** Report98 đã có scene recipe,
nhưng một tập clips chưa nói được state nào mặc định, transition nào có điều kiện,
và thuộc tính đổi thế nào theo thời gian. Batch99 tiếp ngay phần đó, không quay lại
đếm inventory hoặc nhận tests xanh là đã giống hình game.

## Đã nối thêm vào recipe, không để controller là raw blob

`tools/verify/l3_animator_programs.py` sinh `datas/l3_animator_programs.json.gz`.
`tools/verify/l3_recipe.py` bây giờ xuất thêm controller_programs, animator_program_links
và binding_diagnostics cho root được chọn. Toàn bộ dùng qualified identity và source hashes:

- **232 controller /232 state machines /667 states**; mỗi controller hiện có1 layer.
- **1587 Animator** nối direct m_Controller, không lấy controller chỉ vì có cùng clip/name.
- **377 parameters**: tên theo chính m_TOS của controller, numeric type/index và typed default slot.
- **343 AnyState +125 state transitions**: destination, điều kiện/eventID/threshold, exit time,
  duration/offset/fixed-duration/interruption/self-transition đều giữ source.
- **666 motion leaf nodes**, tất cả nối được đúng m_AnimationClips[index] rồi scoped AnimationClip.
- State name/full path giữ tất cả m_TOS candidates nếu hash collision; không match-first.
- Có1 empty machine,1 state không có motion tree; không tự chèn clip để “đủ”.
- Destination mã hoá như30001/30000/UINT_MAX vẫn là encoded selector/exit destination,
  không ép thành local state index hay index ngoài mảng rồi bỏ đi.

Raw state/selector/transition/blend-node data, behaviour ranges, layer masks và parameter
arrays giữ cùng chương trình dẫn xuất. Snapshot này có666 single-leaf trees; không vì vậy
khẳng định mọi Animator của mọi version không bao giờ blend. Default state trong source
không chứng minh runtime đã bật GO, giữ nguyên default hoặc không bị script Play/CrossFade.

## Probe thuộc tính theo thời gian, nối thẳng tới target component

CLI hỗ trợ chọn rõ Animator/controller/state và **clip-local time**:

```sh
python3 -m tools.verify.l3_animator_programs --animator 495980 --controller 1974 --state 0 --time 0.25 --out /home/user/quit-popup-properties.json
```

Animator/controller IDs trong ví dụ thuộc `data.unity3d/resources.assets`.
Không tự biến0.25s này thành thời gian từ lúc load scene; không ngầm nhân speed, loop,
cycle offset, transition blend hay phát callback/audio. Nếu controller không gắn trực tiếp
vào Animator, probe từ chối thay vì tìm controller khác toàn cục.

### Ví dụ thực: Popup_QuitMissions trong Board_Pause

Node `Popup_QuitMissions`, GO57508, Animator495980. Source controller **Popup_Network:1974**
được tái sử dụng ở đây — tên controller không được dùng để đổi tên/identity popup.
State mặc định index0 là **Appear**, motion leaf nối clip1572; state1 **Hide** nối1573.
Recipe vẫn giữ cả AnyState transition và condition tới Hide.

Với state Appear đã chọn rõ, probe clip-local time cho scale XY và SpriteRenderer scalar
binding (CRC candidate m_Color.a):

| Clip-local time | Scale X/Y | Scalar alpha candidate |
|---|---:|---:|
|0|0 /0|0|
|0.25|~1.030399899 /~1.030399899|~0.831372559|
|0.5|1 /1|~0.831372559|

Các giá trị không phải tween dựng tay: lấy cubic coefficients/keys/constants của APK và
binding targets đã nối ở98. Không sửa alpha cuối thành1 theo cảm giác; serialized curve
cho giá trị trên. Z scale giữ1. Raw probe snapshots có full target_binding/component
identities/property candidates tại `raw/l3-playback-verification/local99.json`.
Đây là arithmetic model, **không phải Unity property readback hay ảnh popup đã render**.

### Toàn665 clips được probe, không chỉ ví dụ đẹp

Đã chạy đầu/giữa/cuối từng clip (gộp thời điểm trùng), **1853 clip-time probes**:
86905 streamed polynomial values,51926 constant values,69 discrete-step values,
1461 initial-constant values; **0 unknown channel values ở các điểm đã probe**.
Không suy0 unknown ở3điểm thành đã xác minh mọi timestamp hay engine equivalence.

Một lỗi mô hình đã được bắt và sửa trước bàn giao: bỏ hết frame -FLT_MAX làm1461 giá trị
ban đầu thành unknown giả. Bóc kỹ thấy các keys này có coefficients a=b=c=0, d là initial
value thật; polynomial hằng không phụ thuộc thời gian, lấy được an toàn. Ví dụ sprite
clip965: mapping index0 đã có ở initial frame, key hữu hạn đầu tiên0.233333s đổi sang1.
Không cần chờ key đầu để bắt đầu vẽ, không gọi đây là thiếu animation. Với sentinel có
nonconstant coefficients, probe vẫn giữ unknown chứ không extrapolate dt cực lớn.

Streamed probe dùng cubic theo dt từ key; dense grid linear, constant direct; integer/PPtr
là step. PPtr index nối đúng bảng mapping và qualified sprite, không blend pointer. Time
ngoài clip/NaN/Infinity bị từ chối; polynomial không hữu hạn giữ unknown. Source vẫn còn
nguyên coefficients và sample arrays; mô hình này chưa tái tạo Unity float32/FPCR/blending.

## Rà thiếu binding tới tận component thực, không gán giới hạn bừa

Audit tất cả410 non-unique binding instances, kèm actual component identities ở từng GO:

- **376**: required path không có trong Animator subtree đã bóc.
- **17**: path có, nhưng **thiếu hẳn required component class**:13 yêu cầu MonoBehaviour,
  target GO chỉ có Transform/SpriteRenderer;4 yêu cầu BoxCollider2D mà GO không có nó.
- **17**: nhiều target candidates; tiếp tục giữ ambiguity, không chọn đại.

**Làm rõ wording98:** nhóm13 không phải đã thấy MonoBehaviour khác script nhưng chưa giải
được inheritance; ở chính GO candidates này **không có MonoBehaviour** để xét script.
Không có cơ sở cứu bằng ancestor class match hoặc tìm component trên GO khác. Chưa chứng
minh runtime không add component/đổi hierarchy; cũng không giả định runtime sẽ làm vậy.
Không xoá clip dùng chung chỉ để làm số unresolved đẹp hơn.

## Kiểm chứng, phần còn thiếu thật

19 tests mới kiểm regenerate toàn artifact từ raw, typed default slots, state/layer indices,
encoded destinations, leaf clip indices, Animator ownership, binding diagnosis và recipe;
fixture cubic/dense/constant/integer/PPtr/sentinel/nonfinite/bounds; real popup selected-state
probe. Full suite/CI receipt ghi sau khi chạy. Raw98 và nguồn controller không bị sửa/xoá.

**L3 vẫn chưa hoàn tất.** Đã có compiled state graph và property probes dùng được, nhưng chưa
chạy script-driven runtime selection, transition scheduler/layer blending, driven RectTransform,
particle simulation, shader/stencil/culling và composition qua viewport để kiểm hình cuối.
5 header-only MonoBehaviours/52 default-mesh pointers ở98 vẫn ghi rõ; batch này không nhận
đã giải chúng. Clip events/callback/audio links còn giữ điều kiện, không invoke giả.

Bước công việc phải tiến từ recipe/program/property model sang composition/playback thực
với external original assets; không nhận những phần chưa chạy là xong, không lấy screenshot
mới hay người dùng capture làm điều kiện mới được tiếp tục bóc source. Peer review độc lập
vẫn cần, không self-ACK.

Local receipt: **940 tests PASS /131.369s** (19new). Remote CI receipt ghi riêng.
