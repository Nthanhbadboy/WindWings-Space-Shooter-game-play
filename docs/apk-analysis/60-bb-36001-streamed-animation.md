# 60 — BB-36001: root position, súng và collider trong streamed animation

> **Tạm thời — static original-APK, không phải replay Unity.** A = trường/bytes trực tiếp;
> B = giải mã/join từ các trường đó; C = giả thuyết cần kiểm tra tiếp.
> Premium vẫn để sau. Không dùng screenshot hoặc mô tả kế thừa làm nguồn số.

## 1. Nguồn và cách tái lập

- Raw: `reverse-engineering/raw/balloon-animation/bb-36001-animation.json.gz`.
  Recovery CI **40187741686**, bot commit **192d2290f**. Có 37 node subtree,
  component typetrees/header script identity, full controller và 3 clip typetrees,
  bytes base64 + SHA256 cho controller/clips; không đưa APK/assets gốc vào Git.
- Định danh A: `resources.assets` root **185704**, Animator **496390**,
  controller **1908**. Input `data.unity3d` SHA256
  `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7`.
  Hash native/metadata cũng nằm trong raw; source hash dùng bytes giải nén gzip.
- Decoder: `tools/verify/balloon_animation.py`; output giữ từng frame/key,
  coefficient, offset, binding, component target và keyed range tại
  `reverse-engineering/raw/balloon-animation/decoded-clips.json.gz`.
- Tham chiếu **format**, không phải nguồn dữ kiện game: Perfare/AssetStudio
  `d158e864b556b5970709c2a52e47944d53aa98a2`, `AnimationClip.cs`, giữ nguyên source
  và MIT license ở `raw/balloon-animation/toolchain/`. Stream frame là float time,
  int keyCount; key là int curveIndex + 4 float coefficient; value = coefficient[3].
  Width binding Transform: position/scale/Euler 3, quaternion 4; loại khác 1.
- `python3 tools/verify/balloon_animation.py`: **3 clip / 17 checks**.
  Tests thêm 8 case: tái lập output, graph, root/constant channel, sentinel,
  Mono header identity, duplicate paths, malformed stream, channel coverage.
  Chưa hỗ trợ decode dense channel: gặp chúng sẽ fail, không im lặng bỏ qua.

## 2. Graph thật: Spawn → Idle ↔ Attack1

Mức A/B, controller1908:

| State index | State | Clip pathID | Độ dài clip | Đi tới |
|---|---|---:|---:|---|
| 0 (default) | Spawn | 1468 | 2.5 | Idle (1) |
| 1 | Idle | 1467 | 10 | Attack1 (2) |
| 2 | Attack1 | 1466 | 12 | Idle (1) |

Cả ba speed=1; transition condition-array rỗng, hasExitTime=true, exitTime=1,
transitionDuration=0. Không parameters, AnyState transitions hay
StateMachineBehaviours. Mỗi state dùng đúng một clip index 0/1/2.
Tất cả sampleRate=60, loopTime=true, events-array rỗng.
Đây là **graph tuần hoàn theo serialized state**, không phải chứng minh chu kỳ
22 giây wall-clock: activation/reset, Animator speed, timescale, culling,
external script và vòng đời instance chưa được replay.

## 3. Không có ordinary curves ≠ không chuyển động

Các `m_PositionCurves/m_FloatCurves/...` rỗng ở summary cũ, nhưng binding và
`m_MuscleClip.m_Clip.data` chứa dữ liệu thực:

| Clip | Streamed channels | Frames gồm sentinel | Dense channels | Constant channels |
|---|---:|---:|---:|---:|
| Spawn | 12 | 9 | 0 | 0 |
| Idle | 15 | 66 | 0 | 0 |
| Attack1 | 12 | 76 | 0 | 3 |

Frame đầu là **−FLT_MAX**, không phải −Infinity và không phải thời gian playable.
Frame cuối +Infinity có 0 key. Decoder giữ sentinel riêng, keyed range chỉ tính
key time từ 0 đến stopTime. Không được coi sentinel là thời điểm spawn.

**Cả 3 clip có Transform position binding `path=0, attribute=1, typeID=4`.**
Hash0 resolve về chính Animator root, không phải child `Enemy_Ingame`.
`m_ApplyRootMotion=false` của Animator **không phủ định** local-position binding
này. Kết luận B: có animation root-local, không chỉ animation cánh.

### Các key position trên root (làm tròn để đọc)

| Clip | Key time | x | y | z |
|---|---:|---:|---:|---:|
| Spawn | 0 | -12.41 | 7.33 | 0 |
| | 0.666667 | -0.29 | 5.36 | 0 |
| | 1.333333 | 2.34 | 3.71 | 0 |
| | 2.5 | -3.66 | 2.30 | 0 |
| Idle | 0 | -3.66 | 2.30 | 0 |
| | 2.3 | 1.79 | 7.98 | 0 |
| | 3 | 3.21 | 5.39 | 0 |
| | 5 | 1.70 | 0.52 | 0 |
| | 8.516667 | -2.97 | 8.59 | 0 |
| | 10 | -3.77 | 6.04 | 0 |
| Attack1 | 0 | -3.77 | 6.04 | 0 |
| | 2.5 | -0.28 | 8.05 | 0 |
| | 5 | 3.21 | 6.04 | 0 |
| | 7.5 | -0.28 | 8.05 | 0 |
| | 10 | -3.77 | 6.04 | 0 |
| | 12 | -3.66 | 2.30 | 0 |

Cuối Spawn = đầu Idle; cuối Idle = đầu Attack1; cuối Attack1 = đầu Idle
(theo keyed values). Điều này hỗ trợ B: một entry animation rồi pattern lặp,
**không thấy terminal fly-away state trong graph này**.
Không suy từ đó rằng instance tồn tại vô hạn hoặc bắt buộc phải chết.

Root Euler có binding ở Idle (streamed) và Attack1 (3 constant zero channels).
WingL/WingR có Euler bindings ở cả 3 clip. Các binding đều resolve đúng một target.
Subtree có **9 đường dẫn child Point trùng tên dưới Barrels1**; decoder giữ list
candidates, không overwrite bằng dictionary một-nút-mỗi-path. Không binding
nào trong 3 clip này rơi vào các đường dẫn trùng đó.

## 4. Animation còn điều khiển component enabled

CRC32(`m_Enabled`) = **3305885265**, trùng attribute trên 3 nhóm binding.
TypeID114 + script pointer `{fileID:1,pathID:338}` join bằng **raw Mono header**
đến `SpaceShooter.Machine_Gun_Attack`, không dùng `m_Script` typetree bị lệch.
Targets: Barrels1 component **690037**, Barrels2 **639146**.
TypeID61 join đến `Enemy_Ingame/BoxCollider2D` component **490394**.

Các thay đổi **key value** theo clip-local time:

| Clip | Barrels1 enabled | Barrels2 enabled | BoxCollider2D enabled |
|---|---|---|---|
| Spawn | 0 tại 0 | 0 tại 0 | 0 tại 0; 1 tại 2.5 |
| Idle | 1 tại 0; 0 tại 9 | 0 tại 0 | 1 tại 0 |
| Attack1 | 0 tại 0 | 1 tại 0; 0 tại 10 | 1 tại 0 |

Không có AnimationEvent **không có nghĩa** clip không gây tác động gameplay:
component enabled có thể gọi lifecycle code. Bảng trên không chứng minh số
đạn, thời điểm bắn thực, sát thương, hay invulnerability tuyệt đối; native của
Machine_Gun_Attack và collision/death path cần đọc riêng. Cũng không tự nâng
các keyed 0/1 thành bảo đảm thời gian bật/tắt ở mọi frame/transition.

## 5. Liên hệ với completion/pooling ở report59

- AirFree gọi riêng SetAngle/SetPosition; không setup Path/Waypoints trong body
  đã đọc. Nay có thêm nguồn chuyển động rõ ràng: **root animation** (B).
- Animator graph không có state terminal exit/pool, clips không có events;
  binding targets chỉ gồm Transform, Machine_Gun_Attack, BoxCollider2D.
  Không có GameObject-active binding trực tiếp trong 3 clip này.
- **Chưa chứng minh BB tự pool hoặc phải bắn chết.** Report59 FixedUpdate xét
  world-space border và các gate moving/movein; bảng này là root-local key.
  Spawn x=-12.41 ở ngoài ±10 ngay từ đầu không đủ để suy callback khi spawn.
  Parent transform, inter-key interpolation/overshoot, update-order và script
  khác vẫn có thể làm khác kết quả.
- Keyed extrema **không phải mathematical bounds của đường cubic**. Decoder
  chưa evaluate/interpolate curve, không mô phỏng transition hay Unity runtime.
  Do đó không được dùng Idle/Attack1 keyed ranges để khẳng định không bao giờ
  ra khỏi border, hoặc đưa ra số kills tối thiểu chắc chắn cho stage2.

## 6. Đào tiếp (không đòi screenshot mới)

1. Raw/native AirFree spawn/parent chain, terrain scroll và transform world/local;
   xác định parent của instance thay vì suy từ prefab asset root.
2. Machine_Gun_Attack OnEnable/OnDisable/coroutine + BoxCollider/health route:
   animation-enabled có liên hệ nào tới removal/death/pool không?
3. Nếu cần chứng minh boundary, giải cả interpolation và movement gates;
   kiểm tra script viết transform, reset/Animator lifecycle, rồi mới nâng kết luận.
4. T9 atlas rect/texture/rotation/trim vẫn là task raw riêng; Premium chưa mở lại.
