# 63 — BB: writer của movement state và ranh giới của pool reuse

> **Tạm thời, static original-APK; không phải replay.** A = asm/declaration/raw
> field; B = diễn giải/join; C = giả thuyết runtime. Không mở Premium.

## 1. Câu hỏi vòng này

Report61 còn thiếu state thực của BB khi AirFree kích hoạt. Vòng này không bóc
lại APK hoặc đếm asset: đọc **toàn bộ21method trong raw Enemy_Movement class**,
đối chiếu Enemy_Sub setters và exact early-wave joins, tìm writer và reset.

Collector: `tools/verify/movement_state_writers.py`.
Raw kết quả: `reverse-engineering/raw/balloon-animation/movement-state-writers.json.gz`.
Giữ21body/inventory, store hints,5Enemy_Sub setters, source SHA và9checks.
Nguồn trực tiếp là `ui-audit/extra-native/Enemy_Movement.{asm.txt,json}`,
`il2cpp-consts/Enemy_Sub.asm.txt`, và exact join có source chain trong
`early-waves/movement-completion.json.gz` (report59).
Không dùng screenshot hoặc báo cáo kế thừa làm bằng chứng số.

**Scanner chỉ là linear store hints**, theo alias `this` và invalidation qua call;
không phải CFG emulator, không chứng minh đã tìm mọi writer trong libil2cpp.
Có negative tests tránh nhầm `sp+4C` với `this+4C`, caller-saved x0 sau call,
và x0 sau khi w0 bị ghi. Các store quan trọng dưới đây đã đối chiếu asm riêng.

## 2. Writer trong đúng class Enemy_Movement

| Method | Ghi typeMove (offset4C) | Ghi path (offset50) | Bằng chứng |
|---|---:|---|---|
| SetPathFollower1583e2c | 0 | kết quả PathCreator.get_path | mode write1583e3c; path write1583e78 |
| SetWaypoints1583f0c | 1 | không thấy direct path write | mode write1583f48 |
| SetMoveLinearly1584200 | 2 | không thấy direct path write | mode write1584228 |
| RocketResumeMove1586714 | 2 | không thấy direct path write | mode write1586728 |

Đó là **4method có typeMove store hint và1method có path store hint trong class
này**. Không gọi đó là whole-program writer closure: code khác giữ reference,
coroutine, delegates/reflection hoặc native runtime chưa được bao phủ đầy đủ.

SetPathFollower còn reset dstTravelled58 trước khi lấy path, chọn speed từ
phần tử cuối listSpeeds, đặt world position rồi activate. Không tự thêm thao tác
clear waypoints/movein/moving mà body không ghi. Null path argument/invalid
speed array có nhánh exception, không được mô hình thành setup thành công.

SetMoveLinearly ghi moving=true và movein=false; RocketResumeMove đổi mode2 và
velocity từ parentRotate. Việc thấy setter tồn tại **không chứng minh AirFree gọi**.

## 3. Không có reset toàn bộ ở enable/stop/position

| Operation | Thay đổi liên quan đã đọc | Không được tự thêm |
|---|---|---|
| Enemy_Movement.OnEnable1586024 | zFixed48 từ GameLayer | reset typeMove/path/dstTravelled/movein |
| StopMove158474c | moving5C=false | clear path/waypoints/mode |
| StartMove1584888 | moving5C=true | setup lại path/mode |
| SetPosition1584070 | world position + SetActive(true) | reset mode/path/moving/movein trực tiếp |
| SetAngle15840f0 | nếu không fixedAngle: Euler trên parentRotate | đổi movement mode |
| SetPositionAndAngle1584140 | movein=false, moving=false trước position/rotation/activate | xem như tương đương SetAngle rồi SetPosition |

**Chỗ dễ dựng sai:** AirFree dùng **hai setter riêng**, không phải combined
setter. Nếu engine tái dựng gom chúng vào một helper combined thì có thể vô
tình tắt moving và reset movein mà native AirFree không làm trong các body đó.

Enemy_Sub.SetPosition/SetAngle lấy controller rồi đi tới movement setters;
combined setter đi tới1584140 riêng. Raw giữ các body để kiểm lại, không join
bằng tên method trùng nhau.

OnEnable của Controller và Appeared còn liên quan tới delegate/moving (report59).
Field-contract model ở đây **không mô phỏng thứ tự callback activate**. Ví dụ
`airfree_set_position` trong model chỉ có nghĩa “không direct reset các field
đang xét”, không có nghĩa toàn bộ SetActive không gây lifecycle side effects.

## 4. Phát hiện mới: SetWaypoints quá ngắn không phải no-op

Asm A/B:

```text
1583f44: w8=1
1583f48: typeMove=1
1583f4c: dstTravelled=0
... null guard / đọc length
1583f58: compare length với2
1583f5c: length>=2 →1583f84
1583f80: nhánh length<2 tail-call logger rồi return
1583f84: waypoints = input
```

Với **array khác null nhưng length0hoặc1**, mode/distance đã đổi **trước** nhánh
log-return; old waypoints chưa bị overwrite. Do đó gọi SetWaypoints([]) có thể
để lại **mode1 + old waypoint array/state**; không được viết validator giả rằng
“input ngắn thì không thay đổi gì”. Các index/cached segment chỉ được setup ở
nhánh valid; không coi chúng đã reset ở nhánh log.

Null input có đường exception khác, chưa mô hình side effects sau exception.
Không khẳng định exact early BB gọi input ngắn: đây là **method contract mới
được đọc**, không phải tình huống gameplay đã quan sát.

## 5. Áp vào exact BB và câu hỏi tự thoát

Join exact3wave vẫn chỉ có1AirFree reference:
`datas/maps/waves/wave_0164` → `Wave_0164/w15/Boss_2`, Call_Data599908 →
root **resources.assets/185704 BB-36001**.
Đó là tên node serialized, không tự biến BB thành stage boss hoặc boss phải diệt.
`spawnType` tại Call_Data này là0 và concrete spawner làAirFree; không chỉ phân
loại theo enum khi component spawner thực có thể khác (report54/59).

Kết hợp raw59–61 với writer table hiện tại:

- **Không thấy AirFree setup path/waypoints/linear trong OnSpawn đã đọc**;
  root animation là một nguồn chuyển động riêng (report60).
- OnEnable không reset mode/path; separate setters cũng không direct reset
  các field đó. Vì vậy pool reuse không thể mặc định là “fresh movement state”.
- Một ví dụ **field-contract có điều kiện**, không phải live BB:
  prior(typeMove2,pathold,distance42,moveintrue) → enable/separate setters →
  Appeared có thể vẫn giữ mode2/pathold/distance42/moveintrue và movingtrue,
  nếu không có writer/lifecycle side effect khác.
- Ngược lại, nếu state đangPath0/pathnull/nonturret, PathFollow return và
  FixedUpdate không có generic boundary completion route (report61).

Hai trạng thái trên có thể cho hành vi khác dù dùng **cùng animation position**.
Không thể chốt autoescape/mustdie chỉ bằng curve bounds, applyRootMotionfalse,
spawner name hoặc prefab serialized fields.

**Chưa chứng minh BB thực sự từng mang prior mode2/pathold.** Muốn nâng kết luận
phải nối instance history, callers/writers bên ngoài class, exact live state và
alternate remove/death/collision routes. Không lấy unit test tạo state giả làm
bằng chứng tình huống đó reachable trong stage2.

## 6. Kiểm thử và bước tiếp

```sh
python3 tools/verify/movement_state_writers.py
python3 -m unittest discover -s tests -q
```

Thêm8tests: source/rebuild, stack-vs-object, call/word register clobber,
separate-vs-combined setters, short waypoint partial state, successful path
contract, stop/start không reset, unsupported/null contract fail rõ.

Các model chỉ kiểm field effects đã giới hạn; không engine scheduling/collision.
Không cần recovery APK/full export mới trong vòng này vì raw cần thiết đã có.
Tiếp theo ưu tiên caller/instance history và alternative removal; T9pixelcrop/
mask40fractionalrect ở report62 vẫn mở, Premium vẫn deferred.
