# 106 — reachability & driven-coverage trên 232 controller (mục #14) — arena/a5a74747

**Tạm thời. Model output, không phải Unity readback, không render.** Câu hỏi của báo cáo này hẹp
hơn "composition": *graph animation đã decode có thật sự chơi được hết không, và nếu không thì
thuộc tính nào của game không bao giờ bị animate?*

Mục #14 trong BẢNG ĐIỀU PHỐI PR12 (đề xuất mới, đã CLAIM trước khi làm, comment `6411110604`).
Không lấy #12: xem §0.

## 0. Vì sao mục mới thay vì #12 (composition viewport)

#12 cần đưa state đã model qua camera → viewport. Tôi đã thử scoping và **nửa viewport bị chặn
thật**: đi ngược parent chain của chain UI thật (`Box_Gift (7)`, GO `96185`, Transform `277770`)
thì cha trực tiếp là GO `270123` **không có trong node index** (`nodes-00*.json.gz`, 37 361 node).
Không có node cha ⇒ không dựng được ma trận local→root từ artifact hiện có, và dựng lại projection
của digger khác là lấn miền. Vì vậy tôi **không claim #12** và ghi lại chặn này; phần "engine
transition" thì vẫn làm được trong miền AI-3 nên tách thành #14.

## 1. Nguồn và SHA pin

Artifact `datas/l3_transition_coverage.json.gz`
`84fcab6b6f2317e4c2a8c8392239821d2940314ef1c3fec510e966436d613175` (21 964 B, rebuild 2 lần
byte-identical). Tool `tools/verify/l3_transition_coverage.py` `64fafd0baf45f172`.

| Nguồn | sha256 (16) |
|---|---|
| `datas/l3_transition_model.json.gz` | `b02b766ceb15ba6b` |
| `datas/l3_driven_props.json.gz` | `ed3f51739a89df3a` |
| `datas/l3-scene-chains/motion-000.json.gz` | `b2036fe60a7bfef7` |
| `datas/l3-scene-chains/animation_bindings-000..017.json.gz` (18 shard) | `79982d83626c9fab`… |
| `datas/l3_animator_programs.json.gz` (qua `l3_driven_props`) | `114d8f442e07a073` |
| `tools/verify/{l3_transition_scheduler,l3_driven_props,l3_model_common}.py` | `548a5e55449b4e6a` / `5e5e0b53c3e90b76` / `6e0f5c589189f49c` |

25 input được băm trong `artifact['inputs']` (18 shard bindings + motion + 3 artifact + 4 tool).

## 2. Quy tắc model (mỗi quy tắc là model choice, ghi rõ)

| Quy tắc | Nội dung |
|---|---|
| closure | BFS trên edge serialized; `unconditional` = chỉ edge **không** condition; `parameterized` = mọi edge đích local (coi condition có thể thoả) |
| exit time | edge chỉ có `m_HasExitTime` vẫn được đi (state time hữu hạn sẽ vượt ngưỡng) — wrap của state loop là policy của `l3_transition_scheduler`, không chứng minh ở đây |
| encoded destination | `30000/30001/4294967295` không định danh state local ⇒ **chặn**, báo lý do, không đoán index |
| self transition | đích == nguồn và `m_CanTransitionToSelf = false` ⇒ không mở rộng closure |
| selector | chỉ selector `is_entry` mở rộng closure; selector khác đếm và liệt kê |
| start | tập start = `default_state_index` (nếu `valid_index`) ∪ đích của entry selector; ghi `start_sources`, không tự chọn |
| binding join | record binding → Animator component + clip; controller lấy từ `animator_attachments`; animator gắn nhiều controller ⇒ reachable nếu **bất kỳ** controller nào tới được clip, và số dòng mơ hồ được báo riêng |

**Không** làm: mô phỏng scheduling engine (việc của `l3_transition_scheduler`), đọc trace runtime,
dùng giá trị parameter thật, hay khẳng định trigger nào được script bật (đó là bằng chứng il2cpp
của report 100/103, không phải callback serialized).

## 3. Kết quả đo

### 3.1 State — 667

| Nhóm | Số | % |
|---|---:|---:|
| Reachable (khi parameter có thể được set) | **646** | 96.9 |
| Reachable **không cần parameter nào** | **254** | 38.1 |
| Không bao giờ tới được | **21** | 3.1 |

- 232 controller: **215** fully reachable (mọi state tới được), **139** fully reachable mà không
  cần parameter, **16** controller có state chết, **1** machine rỗng (không có default hợp lệ).
- **21/21** state chết có `incoming_local = 0` — tức **không có transition local nào trỏ tới**, chứ
  không phải "bị chặn gián tiếp". Vì vậy quan hệ nhân quả rất rõ: state tồn tại nhưng tác giả
  không nối vào graph.

| Controller | state chết | tên state |
|---|---:|---|
| `BuyCards` 1776 | 1 | Idle |
| `Efx_90007_Boss` 1811 | 2 | Bienmat |
| `Body` 1813 | 1, 13 | pose2, Pose |
| `Parent` 1815 | 1, 3 | Idle, Test |
| `Body` 1819 | 17 | UILock |
| `Body 2` 1822 | 21 | test |
| `Body` 1823 | 6, 7 | Dead2, Dead3 |
| `Body` 1828 | 1, 2 | Xuathien, Test |
| `Mini` 1829 | 2 | Attack2 |
| `New` 1834 | 13 | attack4_1 |
| `Parent` 1846 | 10, 11 | Attack6, Attack7 |
| `W2-30033` 1924 | 1 | Active |
| `DS-20013` 1983 | 1 | a |
| `Player_10024_Tentacles` 1994 | 1 | Setup |
| `Tentacle (1)` 1995 | 1 | Setup |
| `Parent2` 2041 | 1 | idle |

Nhóm tên `Test`/`test`/`pose2`/`Pose`/`Dead2`/`Dead3`/`Setup` gợi ý state tác giả bỏ dở; **không**
kết luận được vì sao (không có script evidence ở đây), chỉ đo được là không có edge vào.

### 3.2 Transition — 932

| Lớp | Số | Ghi chú |
|---|---:|---|
| unconditional | 464 | = 232 `entry` + 232 `selector` (mỗi cái 1 transition) |
| parameter_gated | 376 | `any` 343 + `state` 33 — **khớp đúng** 376 condition của report 105 |
| exit_time_gated | 92 | toàn bộ là `state` scope |
| **tổng** | **932** | = 468 (any+state) + 464 selector, khớp `l3_transition_model` |

- **234 encoded destination bị chặn** (232 × `30000`, 1 × `30001`, 1 × `4294967295`); cross-check
  đếm lại số hop thật sự dùng transition bị chặn = **0**.
- Không có transition nào `self_transition_disallowed` trong dữ liệu (0), nên nhánh policy đó chưa
  được exercise — ghi nhận, không suy diễn.

### 3.3 Clip — 665

| Nhóm | Số |
|---|---:|
| Clip được ít nhất 1 state tham chiếu | 665 |
| Clip không controller nào tham chiếu | **0** |
| Clip reachable (parameterized) | 646 |
| Clip reachable (không cần parameter) | 254 |
| Cặp (controller, clip) không reachable | **19** |

19 cặp chết (đúng bằng 19 clip chỉ nằm trong state chết):

| Controller | Clip |
|---|---|
| `BuyCards` 1776 | 966 Idle |
| `Efx_90007_Boss` 1811 | 1048 Bienmat |
| `Parent` 1815 | 1077 Idle · 1084 Test |
| `Body` 1819 | 1106 UILock |
| `Body 2` 1822 | 1175 test |
| `Body` 1823 | 1180 Dead2 · 1181 Dead3 |
| `Body` 1828 | 1223 Test · 1237 Xuathien |
| `Mini` 1829 | 1221 Attack2 |
| `New` 1834 | 1279 attack4.1 |
| `Parent` 1846 | 1351 Attack6 · 1352 Attack7 |
| `W2-30033` 1924 | 1491 Active |
| `DS-20013` 1983 | 1685 a |
| `Player_10024_Tentacles` 1994 | 1602 Setup |
| `Tentacle (1)` 1995 | 1603 Setup |
| `Parent2` 2041 | 1687 idle2 |

### 3.4 Binding — 52 400

| Tier | Số | % |
|---|---:|---:|
| Animator map được sang controller | 52 400 | 100 |
| Trên cặp (controller, clip) **reachable** | **51 632** | 98.53 |
| — trong đó không cần parameter | 13 867 | 26.5 |
| Trên cặp **unreachable** | **768** | 1.47 |
| Animator không map được | 0 | 0 |
| Animator gắn >1 controller (mơ hồ) | **0** | 0 |

768 binding chết theo route kind: `alpha` 237 · `local_position` 221 · `euler` 129 · `active` 90 ·
`local_scale` 58 · `renderer_state` 26 · `particle_module` 4 · `renderer_size` 2 · `unresolved` 1.

Đọc kèm: **26.5% binding của game có thể chạy mà không cần bật trigger nào** (auto/exit-time), phần
còn lại phụ thuộc parameter do script bật — chưa chứng minh được trigger nào thực sự được bật.

### 3.5 Parameter — 377

| Nhóm | Số |
|---|---:|
| Khai báo (Bool + Trigger) | 377 |
| Được dùng làm điều kiện trong chính controller khai báo | 357 |
| **Không bao giờ dùng làm điều kiện** | **20** |
| Tên phân biệt thực sự xuất hiện trong condition | **108** |

Top tên: `Appear` 42 lần (state-gate), `Attack1` 20, `Attack` 12, `Action` 7, `Active` 7.
377 khai báo nhưng chỉ 108 tên phân biệt ⇒ rất nhiều Trigger trùng tên giữa các controller; mọi
thống kê theo "số parameter" phải nói rõ là khai báo hay tên.

## 4. Case chạy được (từ artifact, không tự bịa)

| Case | Kết quả |
|---|---|
| `Box_Gift (0)` 1792 — chu trình trigger | 3/3 state reachable; không cần parameter chỉ tới state 0; `gates`: 1←`Flick`, 2←`Change`; selector 1 transition `30000` bị chặn |
| `BB-36002` 1910 — tự chạy | 3/3 reachable **không cần parameter** (`gates` rỗng); controller không khai báo parameter nào |
| `Body` 1813 — nhiều state chết nhất | 13 reachable / 14; chết 1 (`pose2`) và 13 (`Pose`); state 2..14 cần `Attack1..6`, `Idle1..3`, `Mix2`, `Appear`, `Die` |
| `Warning_Boss_Appear` 1857 — nhiều transition bị chặn | 2 encoded bị chặn (`30001` + `30000`); 3/3 state vẫn reachable qua entry + transition local |

## 5. Cross-check đã chạy trong artifact

`artifact['cross_checks']`: `edge_classes_sum_to_transitions` 932 = 932 · `state_partition`
646 + 21 = 667 · `binding_tiers_partition_totals` 51 632 + 768 + 0 = 52 400 ·
`unconditional_closure_is_a_subset` 232/232 machine, 0 vi phạm ·
`encoded_destinations_never_traversed` blocked 234, traversed **0** · `clip_tiers_are_nested` true.

Một lỗi tự bắt được: transition id dạng `m0:state2:0` **không unique toàn cục** (lặp giữa các
controller) — cross-check đầu tiên đếm sai 13 "blocked bị đi qua" vì key theo id trần. Đã sửa thành
key theo (controller identity, id) và ghi thành `decode_limits`; có test regression cho đúng bẫy này.

## 6. Recipe

```sh
python3 -m tools.verify.l3_transition_coverage --build
python3 -m tools.verify.l3_transition_coverage --list --filter Body
python3 -m tools.verify.l3_transition_coverage --controller 1813
python3 -m unittest tests.test_l3_transition_coverage -v
```

**25 test mới**; **full local 147 PASS (21.153 s)** (45 baseline + 77 của report 105 + 25 mới).
`tools/verify-claims.py --require AB,AO,AP` → PASS 209 · FAIL 0 · SKIP 2 · ERROR 0 (thêm 1 file
`datas/` ⇒ đồng bộ needle `AI1` 69→70).

## 7. Chưa hoàn tất, điểm cần review

1. **Chưa chứng minh trigger nào được bật**: closure "parameterized" là *có thể*, không phải *đã*.
   Cần join sang bằng chứng `SetTrigger`/`Play` của report 100/103 (il2cpp) để biến 646 thành con số
   "thực sự chơi được"; đó là việc của AI-1/spec, tôi không tự làm.
2. **21 state không có edge vào** là phát hiện graph, nhưng *lý do tác giả* (bỏ dở, dùng cho tool,
   hay do decode thiếu transition) chưa chứng minh được. Nếu ai tìm được transition trong typetree
   mà artifact motion/transition bỏ sót thì con số này phải giảm.
3. **Encoded destination**: 232 selector `30000` bị chặn theo policy; nếu source thật của Unity cho
   `30000` một nghĩa cụ thể (ví dụ "any state"), policy này cần thay bằng bằng chứng native. Đây là
   điểm dễ tranh luận nhất trong báo cáo.
4. **Join clip-level** dùng `animator_attachments` (1587 animator); 0 dòng mơ hồ trong dữ liệu này
   nhưng nếu artifact animator đổi thì phép join phải chạy lại.
5. **Không** kết luận gì về thứ tự ưu tiên khi nhiều transition cùng thoả (việc của scheduler, vẫn
   `proven:false`).
6. Report này **không** render, **không** screenshot, **không** sửa tool digger khác, không đụng
   3 path shared.

## Receipt106

- Branch: `arena/a5a74747-windwings-space-shooter-game-p`
- Code: `d9ce29e7b` (tool + artifact + test), report ở commit riêng sau đó.
- Artifact: `datas/l3_transition_coverage.json.gz` `84fcab6b…6d613175` (21 964 B), rebuild 2× byte-identical.
- Local: **147 PASS** (`python3 -m unittest discover -s tests -q`, 21.153 s), 25 test mới.
- Claims: **209 PASS · 0 FAIL · 2 SKIP · 0 ERROR** (chạy tay đúng step `docs-verify`).
- CI: workflow `docs-verify` không trigger trên push branch này và token phiên không có
  `actions:write` (403) ⇒ **không có run ID**; đã chạy tay toàn bộ step.
- `provenance: arena/a5a74747-windwings-space-shooter-game-p`
- Không self-ACK, không merge, không push `main`.
