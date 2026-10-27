## Hiện hành135 / arena/ef6b75ef / #27 apply seed + hai backend writer + sampler kênh (static)

Claim **6442376375**. [Report135](apk-analysis/135-ef6b75ef-native-apply-samplers.md). Probe `owner135` từ cache XAPK fail-on-miss, run **40507430140**/source `53f6536dc` (evidence commit `52c664057`): **15 seed + 9 callee = 24 thân FDE, 9952 B**; verify decode lại từ byte: **177** chuyển điều khiển (89 `bl`), **12** call vào cluster, **20** site indirect (42 row `ldr→blr` thô), **297 fact** byte-verified, **203** field row, **0** string, **3** thân bị cắt ở cap 0x800 (`6c7060`/`6bd5c0`/`6be690`). **Không chạy lệnh nào.**

**`+0x610` của 134 nay có định nghĩa:** `6b2ce8(x0=animator, x1=playable, x2=source, x3=context out, x4=arg3)` là builder context apply — `[x2]==0` ⇒ ghi **invalid state** (word0=1, zero 0x08–0x68, word 0x68, con trỏ 0x90/0xa0/0xa8/0xb0); ngược lại nếu `context[0]==animator[+0x610]` thì **bỏ rebuild**, không thì lấy `+0x610` làm **version key** rồi copy map `+0x08/+0x10/+0x18/+0x58` ← `[[src+0x48]+{0,8,0x10}]`, `+0x20` ← `[playable]`, `+0x28..+0x50` ← 6 word của vector `[src+0x18]`, `+0x60/+0x68/+0x6c/+0x70` ← `[[[src+0x18]+0x58]+{8,0,0x18,0x1c}]`, `+0x74/+0x78/+0x7c` ← word `src+0x54/0x58/0x5c`; byte `+0x80 = (0x54&0x58&0x5c)!=-1`, `+0x81 = [src+0x50]`, `+0x82 = nested table non-empty`, `+0x84 = -1 hoặc word [[[src+0x48][0]]+0x50]`, `+0x88 = [[playable+8]+0x11]`; `6d615c` bind rồi `+0x90=animator, +0x98=animator+0x40`, tail `6b6950`. **`6b6950`**: cần `ctx+8` & `ctx+0x20`; nếu `ctx+0x58 == [+0x610]` thì return, không thì descriptor hằng `{0x10b0b30,0x1e}` → `6d816c`/`6d8118`.

**Hai backend `6b2bdc`:** copy 3 word descriptor vào `record+8..0x18`, giải controller `6b784c`, rồi **byte `+0x5e5`** chọn `6bd5c0` (set) hay `6be690` (clear); nhánh legacy `+0x48f`&`+0x1b0` → `6e2388([[[+0x208]]+0x48][8])`, còn lại `6b7c14`; kết `6da8e4` + tail `6e2388`, result→`record[0]`, descriptor `record+0x20`. **Khác biệt đo được:** hai writer cùng gọi `6bc968` nhưng **arg4 = 1** (`6bd5c0`, fill index `3ff69c` từ `[+0x38]`, mảng `[+0x40]`) vs **arg4 = 0** (`6be690`, pre-pass `6bde64` khi bit0 cờ) ⇒ **không cùng một entry**. Thân hai writer bị cắt ở cap ⇒ **không đọc** phần trong.

**Controller `6b784c`:** handle `+0x638` → registry `0x10e18b0`/`38cbb4` → fallback `3d8614`; interval `3dfa9c([x+0x30], 0x10e8960)`; handle phụ `+0x198` → chain `6acb84` với **con trỏ tương đối** (`obj+[obj]`, `obj+0x20` rồi `[obj+0x20]`), sentinel `[obj]==-obj` = rỗng; leaf `6a7198(rel_a, rel_b, interval_entry, byte[+0x5e5])`; id chọn ghi lại `[+0x638]`.

**Sampler kênh — lần đầu một giá trị ghi được so với giá trị cũ:** `6a99f0` switch `kind=[x0+8]` kinds **5..11** qua **jump table `0x152614`** (`ldrb` offset + `br`), 5 hình: float thô (store rồi `fcmp`), cửa sổ boolean (upper `0x14be6c`/lower `0x14b9c8`, `3dfd98` trên `[x1+0x18]`), delegate `[x1+0x10]`, int làm tròn (`+0.5`, mask `-0x40800001`, `fcvtzs`), int thường. `6a98c4` chỉ kind 9: zero→null, registry `38cbb4`→`[[entry]+0x10]`, fallback `3d8614`, value `5888bc`, so `[x19]`, **`cset ne` = changed**, hook `0x10e18a8` nhận `(0, old, new)`. `6a99a4` kind `0x0b`: store + `old!=new`, kind khác trả 0. `6a9b90`: slot `+0x18` arg `0x10`, byte `0x10e18c0` ⇒ tail `4aa754`. Helper: `3dfa9c` (count `+0x40`, base `+0x30`, stride `0x10`, `(entry_start-key_start) unsigned < key_width`, payload `[entry+8]`), `3d8614` (hook `0x111dba0`, âm bị loại, `5d83b8(id,-1)`), `518b40` (lazy `+0x38`, `494b04`/`493a24`, word `+0x40`), `6d788c` (holder `+0x30`, count `+0x30`, base `+0x20`, entry count `+0x18`, chain `ldrsw [slot+0xc]`). **`6b6850`** dùng cả bốn trong một vòng: playable `+0x168`/count `+0x178`, stride `0x28`, resolve `6b1538`, scratch `+0x5e8` (`+0x5f8`/`+0x600`, grow `6bad24`), slot `+0x1a0` OR vào **byte `+0x48e`**, `49ffc8(entry+0x58)`.

**Sửa lại nhận định cũ:** (a) `6b1538` **không phải resolver đơn giản** mà là **chain walk** — key `[x0+0x10]`/`[x0+0x18]` so với `[node+0x20]&~1` và `[global+8]`, next `[node+0x28]`, index `slot+0xc` bounded bởi count `+0x30`; (b) mô tả invalid-state của `6b2ce8` trước đây thiếu (6 store 16 B phủ `0x08–0x68`, word `0x68` zero riêng); (c) `ctx+0x84` là `-1` **hoặc** word `[[[src+0x48][0]]+0x50]`, không phải byte playable; (d) tool ghi `6bc968` là depth 1 dù parent `6bd5c0` là callee ⇒ artifact báo ở `follow_depth.level2` thay vì giấu; (e) `6c7060` chỉ annotate `0x150` B đầu của thân `0x108c`.

Derived `datas/l3_ef6b75ef135_native_apply_seed.json.gz` **10434B/SHA `5c6d7d85dceb25fc46b13a9d7d4d3f83f706b0979c9d7a76b4e25c3e3555b534`**; pins probe `c11aedd5…` + upstream 129 `217f8893…`/133 `73542233…`/134 `74cf1843…` + tool SHA; **41 focused PASS/0.069s; full 1981 PASS/348.939s; check PASS; Verify 40509111057 SUCCESS exact scientific 0ffd421bf**; receipts `raw/l3-ef6b75ef135-verification/`; official135HANDOFF **6442988169**. Static-only per 6418032974/6418326986; không selfACK/merge/main; protected3 không đổi. Không claim tên class/Animator-wide/scheduler/readback/render; `ldp/stp` không thành field row; jump table chưa decode target. Review: (1) `+0x610` là version key chung refresh/apply đã đủ chưa; (2) hai writer khác arg4 — chu kỳ sau đọc tiếp `6bd5c0` hay `6be690`; (3) `6c7060` có nên thành chu kỳ riêng với cap lớn hơn. #27-full vẫn OPEN: dispatcher/owner class, heap, scheduling, clip/clock writer, pose/blend/apply, readback/render.

## Hiện hành134 / arena/ef6b75ef / #27 tầng lá sau refresh/apply/producer (static)

Claim **6439692785**. [Report134](apk-analysis/134-ef6b75ef-native-refresh-leaves.md). Probe `owner134` từ cache XAPK fail-on-miss, run **40489662914**/source `a45b2dd4f` (evidence commit `c4bd75bc4`): **15 seed + 1 tầng callee = 24 thân FDE, 4424 B**; verify decode lại từ byte: **108** chuyển điều khiển (80 `bl`), **25** call vào cluster, **11** site indirect (24 row `ldr→blr` thô), **211 fact** byte-verified, **1 string**, 110 field row. **Không chạy lệnh nào.**

**Hai số 133 treo nay có định nghĩa:** (a) **`+0x188`** — `6b6dec` ghi `strb ([+0x208]!=0)` khi `[+0x1f1]` set ⇒ gate bit7 `+0x194` + `[+0x188]!=0` của 133 đọc là *"chỉ full refresh khi thật sự có graph"*; (b) **`+0x4b8`** — `6d14d4` trả `*(int*)[x0+0x128]` khi `slot+0x138(x0)` bit0, `+0x128` chính là "clip-data result của virtual `+0xa8`" trong bảng 127.

**Producer `6d017c`** (slot `+0xe0` mà `6cefdc` tail-branch vào): guard slot `+0x138` bit0 + `[+0x160]==0`; body đọc `[+0x118]`, gọi virtual `+0xc8`, mỗi phần tử **int** → `3d8614` → object → slot `+0x148`/`+0x110`, giữ/bỏ bằng `5798a8` trên `[obj+0x118]`, append vector `{+0x150 base, +0x160 count}` (grow `6bb944` = `mov w1,#4; mov w2,#4; b 3f1e30`, push `6bb950` cùng idiom `6bb9ac`), **chỉ phần tử mới nhất** gọi slot `+0x60` với `w1=0x3d`; trả `bool ([+0x160]!=0)`; `str x19,[x19,#0x178]`. **String duy nhất của chu kỳ nằm trên nhánh cảnh báo:** `source count==0` **và** `node vector count!=0` → `6d05e0`/`6cee44` → `52e15c` → `b2e604` → free `3c9438` line 0x206; 64 B gốc `An animator Reset was caused during %s::Awake. This will lead to` (cắt ở cap nên không trích tiếp).

**Apply `6b6fdc`:** seed `6b2ce8(x,+0x1b8,+0x208,+0xb0,+0x640)`; mỗi entry `6b1538`→`6b2eec`→slot `+0x98` với driver `+0xb0`; duyệt cặp stride 0x10, mask `&~1`, đọc `[[obj]+0x160]`, OR dồn **byte `+0x491`**. **Evaluate `6b6dec`:** `6b6c40`+`6b6850`; **đúng 1 playable** → nhánh riêng gọi `+0xb0`; nếu không: scratch `+0x5e8` (`6b7cf8`/`6c7060`), vòng `+0xc0` với `+0x518`, giải phóng bằng `6b3e30`, reset `+0x208` (`6b2a0c`), `6da998`/`6b2bdc`, counter `+0x610` (2 hoặc +1), rồi mirror `+0x188`. **Skin `6b2050`:** `6b3c84` buffer + ba sampler **float `6bf2a0` → int `6bf108` → mixed `6bf1cc`** (count/stride 0x20, bảng `input+0x38`/`+0x48`, test `6a99f0`/`6a98c4`/`6a99a4`), mode `[+0x190]==1` cấp 0x40 B (`51a81c`), `6bf35c`, lookup `3dfa9c`/`0x10e8960`, tail `6bf908`.

**Handle & reset:** `576c70` map `+0x30`→`+0x28` **chỉ khi bit1 `[payload+0x38]` clear**; `5770fc` y hệt **không** test cờ ⇒ câu "bind dùng cái nào" của 133 có đáp án byte. `5707c4` cặp identity (singleton `575e80`, back-pointer `+0x28`). `572a9c`/`6b82e8` reset vector: free `3c9438` line 0x306 trừ bit0 `+0x18`, fill 16 B `0x143ff0`. `6b2a0c` deleter callback `[+0x10]` với hằng `0x10b0b30`. `6b832c` đệ quy con qua `+0xd0`+`6d788c`. `6b22c8` chọn `5716c0`/`571174` theo `3d98bc` bit0 + `+0x189` + `+0x18c==2`. `49fe68` reset cặp stride 0x10 sentinel `-1`.

**Cảnh báo:** `+0x178` là **self** ở node nhưng là **count** ở object refresh ⇒ cùng số offset ≠ cùng field; slot `+0x138` giải target chỉ cho bảng node (`0x6d137c`), **không claim** cho value-object; 24 row `ldr→blr` rút còn 11 site, lưu cả hai số.

Derived `datas/l3_ef6b75ef134_native_refresh_leaves.json.gz` **7556B/SHA `74cf1843928d165058771269c2508337df33be9b4840edfd9c5e076e358062e6`**; pins probe `08237392…` + upstream 129 `217f8893…`/133 `73542233…` + tool SHA; **28 focused PASS/0.079s; full 1940 PASS/339.413s; check PASS; Verify 40490185550 SUCCESS exact scientific a5a5dff35**; receipts `raw/l3-ef6b75ef134-verification/`; official134HANDOFF **6439951448**. Static-only per 6418032974/6418326986; không selfACK/merge/main; protected3 không đổi. Không claim tên class/Animator-wide/scheduler/readback; `ldp/stp` không thành field row; 33 callee chỉ là đích gọi. Review: (1) max `+0x4b8` trên `[entry+0x128]` đã đủ nói "độ dài clip"; (2) nhánh "đúng 1 playable" có đáng chu kỳ riêng; (3) chu kỳ sau đọc `6b2ce8` hay ba sampler. #27-full vẫn OPEN: dispatcher/owner class, heap, scheduling, clip/clock writer, pose/blend/apply, readback/render.

## Hiện hành133 / arena/ef6b75ef / #27 chuỗi helper riêng của graph builder (static)

Claim **6435723533**. [Report133](apk-analysis/133-ef6b75ef-native-builder-helpers.md). Probe mới `owner133` từ cache XAPK fail-on-miss, run **40463822530**/source `9bf7a391f`: **11 seed + 1 tầng callee = 22 thân FDE, 2716 B**, thân cap 0x800 (không thân nào bị cắt). Verifier decode lại từ byte chứ không tin probe: **73** chuyển điều khiển trực tiếp (55 `bl`, 18 `b`: 13 intra/3 external tail/2 cluster tail), **27** call vào cluster `0x6b0000..0x6c0000`, **1** site indirect, **144 fact** byte-verified, 2 string, **90** field row (chỉ `ldr`/`str` đơn trên x0/x19/x20). **Không chạy lệnh nào.**

**Builder tạo output object:** `6b8054` = `3c9298(size 0xe0, tag 0x5e, align 8, label 0x12da21, line 0x56)` → ctor `6ce464` → splice list tại `owner+0x78`. Cùng idiom ở `0x5752b0` (0xf8, line 0x2be, ctor `571c48`, anchor `owner+0x378`) ⇒ idiom chung, không phải fact riêng output.

**Record playable 0x28B** (`6b14ac`): `{+0=handle (576a64), +8=version, +0x10=identity (5707c4 hoặc default `[0x10e2248]`), +0x18=version, +0x20=max([playable+0x44],0)}`; writer `6bbae4` push record, `6bb9ac` push int `[[p]+8]`, `6b9994` insert index (memmove `109ad20`).

**Bind/unbind — lần đầu bit 4 của `+0x194` có nghĩa:** `6ce4b4` set `+0xd0` = unbind cũ → store → tail `6b97d0`. Hai hàm bind/unbind mở đầu `ldrb [+0x194]; tbnz #4 → assert`; string tại đúng site: `0x6b988c` = `0xcf1dc` "Cannot bind playable while the Animator is being evaluated.", `0x6b970c` = `0x126b27` "Cannot unbind…" ⇒ **bit4 = đang evaluate**. Bind: dedupe bằng `&~1`; resolve rỗng ⇒ append rồi return không refresh; resolve ra `[+0x608]` ⇒ **insert index 0**; còn lại append; hai nhánh thật chạy `6b6d60 → 6b22c8 → 6b80e0`. Unbind: dồn phần tử `109ad20`, `+0x178--`, nếu `5770fc(playable)==[+0x608]` thì clear `+0x5d8`/`+0x608` + `49fe68(+0x540)`, rồi **bit7 `+0x194` + `[+0x188]!=0` chọn full refresh `6b92c4`**, ngược lại light `6b6d60 → 6b80e0`. Đây là chỗ đầu tiên hai hình dạng refresh được tách bằng code đã decode.

**`6b80e0` đẩy gì:** clear `+0x498` (`572a9c`); loop 1 duyệt bảng `+0x168/+0x178` stride 0x28, `6b1538` resolve, payload `[+0x20]` test `572834` bit0, gọi slot `+0xa8` của entry với vector `+0x498`; loop 2 duyệt cặp `{handle,version}` stride 0x10 tại `+0x498/+0x4a8`, resolve cùng phép `&~1`, gọi `6d14d4`, gộp **max** vào `+0x4b8`. Probe ghi 2 row tại `0x6b8138` vì cả `ldr x8,[x22]` và `ldr x8,[x8,#0xa8]` cùng tới `blr`; verifier giữ row gần nhất ⇒ 1 site; slot `+0xa8` thuộc class của entry, không có trong bảng pin 129 nên **không claim target**.

**`6b7c58`:** cần `[+0x208]!=0`; container `[x1]` count `+0x10`/base `+0x18` stride 0x20; chỉ record tag `+8==0x16`; value `[record+0x18]`; dedupe liền kề; push `[[value]+8]` vào `+0x4e0`. **`6cefdc`:** `bl 6cf7b4` → `ldr x1,[vptr,#0xe0]` → `br x1`; membership 129 pin ⇒ **producer = graph-builder body + `6d017c`**, tail branch nên không return.

**Sửa 132:** `6b08c0/6b08d8/6b08e4` không phải thunk tạm generic — là **thunk grow container** tham số hoá (element size, align), cùng hình `6bba08` (4,4→`3f1e30`) và `6b9f6c` (0x28,8→`3f1cb4`); `6bb9ac/6bbae4` chỉ gọi trên nhánh grow. Số 132 (8 cluster call/10 container ref) giữ nguyên, chỉ cách đọc 3 callee đổi.

**Erratum RET 127 (theo khung ACK124 ②):** đã đăng PR12 **6436088881** — `graph_builder.callees["0xb98c98"].ret` thật là `0xb98d64` (`c0035fd6`), còn `0xb98d68` là `d6071494` (`bl 0x109acc0`, canary stub, khớp 132: `0x109acc0` không FDE); sai lệch chỉ ở hàm này (6 callee còn lại của bảng 127 đều là RET thật), nguyên nhân `ret=fde_end-4` tại `tools/verify/graph127.py:55`; chỉ supersede nhãn, artifact 127 giữ `8b9df003…`, 133 không chứa nhãn `ret` PC. Derived `datas/l3_ef6b75ef133_native_builder_helpers.json.gz` **5441B/SHA `73542233a6fd80aeb3d13fde9aaae0f1e0a211bd4f04b202afa8c6682d825707`**; pins probe `8bb964b1…` + upstream 129 `217f8893…`/132 `5037ba3b…` + tool SHA; **22 focused PASS/0.096s; full 1912 PASS/341.625s; check PASS; Verify 40464366790 SUCCESS exact scientific da1df8ef5**; receipts `raw/l3-ef6b75ef133-verification/`; official133HANDOFF **6435908363**. Static-only per 6418032974/6418326986; không selfACK/merge/main; protected3 không đổi. **Không chạy lệnh nào — danh sách synthetic service rỗng, code gốc không chạy là toàn bộ.** Không claim tên class/Animator-wide/scheduler/readback; `ldp/stp` không decode thành field row; 22 callee (`6b22c8`, `6b2050`, `6b6dec`, `6b6fdc`, `6b82e8`, `6b2a0c`, `6b832c`, `572a9c`, `572834`, `5707c4`, `576c70`, `5770fc`, `575ee0`, `575f2c`, `571c48`, `3c9298`, `3c9438`, `49fe68`, `52e15c`, `109ad20`, `109acc0`, `b2e604`) chỉ là đích gọi, chưa đọc thân. Review: (1) insert index 0 có đủ nói playable của controller được evaluate trước trong `6b80e0`; (2) `bit7+[+0x188]` gate `6b92c4` — gọi là rebuild hay apply; (3) chu kỳ sau đọc `6d14d4` hay `6d017c` trước. #27-full vẫn OPEN: dispatcher/owner class, heap, scheduling, clip/clock writer, pose/blend/apply, readback/render.

## Hiện hành132 / arena/ef6b75ef / #27 pool dispatch slot31 có chạm animator không (static)

Claim **6435459104**. [Report132](apk-analysis/132-ef6b75ef-native-dispatch-owners.md). Hai probe mới từ cache XAPK fail-on-miss: `owner132` (run **40461994601**/source `06783d220`, 27 thân FDE) và `owner132b` (run **40462227499**/source `dd7c63d7a`, 16 callee + FDE). Verifier **decode lại từ byte** chứ không tin probe: tách `bl` (call) / `b` ngoài (tail) / `b` nội bộ (intra, 169), membership cluster `0x6b0000..0x6c0000`, từng site `ldr [vptr,#slot]; blr` với provenance vptr. **43 fact byte-verified**, 16 callee được gán FDE.

**Trả lời câu hỏi review 1 của 131 — phủ định sạch:** 16 owner của pool slot-31 có **266 `bl`**, **0 lần gọi vào cluster**, **0 tham chiếu 6 container**, chỉ 1 load `+0x188` chung trong `0xe4515c`, 52 dispatch site. ⇒ entry update `6b947c` **không có caller tĩnh nào** trong build này, chỉ có vtable membership + 16 site generic không liên quan (slot31 xuất hiện 24×, 33 21×, 2 3×, 3 2×, 10 2×). Nhóm batch: 160 `bl`, 8 lần vào cluster (`6b08c0/6b08d8/6b08e4/6b1c98/6b753c`), 10 ref container.

**Dispatch thật duy nhất trong cluster là graph builder tự gọi mình:** `6b7e00` `ldr x8,[x19]` → `6b7e0c` `ldr x8,[x8,#0x50]` → `blr` = slot 10 → `3e079c`; `6b7f48` → `6b7f50` `ldr x8,[x8,#0x108]` → `blr` = slot 33 → `6b6ab8`. Slot resolve theo membership 130 đã pin SHA.

**Sửa lại 131:** `0x10ecb08` **không** riêng animator — 9/10 owner tham chiếu nó không hề vào cluster, không đọc field animator. Phát biểu hẹp đúng: trong `6b27dc` container được duyệt và từng phần tử flush bằng `6b1c98(el,0)` nên **có thể chứa** object animator. Ba callee cluster `6b08c0/6b08d8/6b08e4` là 3 thunk 3 lệnh giống nhau (`mov w1,#8; mov w2,#8; b 0x3f1e30`) gọi trên temporary ở stack.

**Stage 2:** `6ce4b4` là **FDE riêng** (`0x48`), không nằm trong ctor `6ce464` (`0x34`) của 129 — graph builder gọi ctor khác; `6b7fe8` là **nội bộ** `6b7d58` (offset 656) nên là branch nội hàm, đã được đánh dấu `intra` thay vì call; `0x109acc0` **không có FDE** (stub fail stack-canary, gọi từ `6b8050`).

Derived `datas/l3_ef6b75ef132_native_dispatch_owners.json.gz` **11962B/SHA `5037ba3b2641ca31c2860ec69cf142f69b8ab90591e6ad88d4838a1a66bc876d`**; pins cả upstream 130/131; **20 focused PASS/0.078s; full 1890 PASS/338.578s; check PASS; Verify40462435663 SUCCESS exact scientific 5ba12c56c**; receipts `raw/l3-ef6b75ef132-verification/`; official132HANDOFF **6435624425**. Static-only per 6418032974/6418326986; không selfACK/merge/main; protected3 không đổi. Không chạy lệnh nào; thân cap 0x1000 nên `0x8b3644`, `0xef4c68`, `0xf1d6bc` bị cắt. #27-full vẫn OPEN: dispatcher/owner class, heap, scheduling, clip/clock writer, pose/blend/apply, readback/render. Kế tiếp rẻ nhất: đọc `6b80e0` (0xE4) và `6b8054` (0x8C) — hai helper cluster mà builder gọi, chưa từng đọc.

## Hiện hành131 / arena/ef6b75ef / #27 ai dispatch slot vtable (static)

Claim **6427869838**. [Report131](apk-analysis/131-ef6b75ef-native-vtable-dispatch.md). Probe mới `owner131` từ cache XAPK fail-on-miss, run **40406003345**/source `700027eca` (run đầu 40405384979 fail vì parse phdr sai offset, đã sửa + ghi `diagnostic.json` cho lần sau). Một lượt quét `.text` **13.827.552B** tại `va 0x36c3a0`: cặp `ADRP+ADD`→9 bảng family + 7 global; mọi `LDR Xt,[Xb,#off]` với off ∈ {0x10,0x18,0xf8,0x108} + `BLR` trong 8 lệnh; phân loại base (`vptr_from_x0`/`adrp_base`/`unknown`); owner theo FDE; 1 tầng caller. **35 fact byte-verified**.

**Trả lời câu hỏi review 1 của 130:** `0x10b0c80` chỉ được **materialize 2 lần** trong toàn binary — `6b15f8` (owner `6b15d4`) và `6b9acc` (installer) — **không có stub dispatch nào** load địa chỉ bảng. Tổng 16 materialization cho 9 bảng; `10b1100` **0**. Slot 31 (`0xf8` = entry update `6b947c`): **537** load, **61** có `BLR`, **21** có provenance (19 `vptr_from_x0` + 2 `adrp_base`), **16 owner khác nhau, không owner nào nằm trong cluster animator `0x6b0000..0x6c0000`**. Slot 33 có 1 site trong cluster, slot 2/3 = 0.

**Kết luận bounded negative:** không tồn tại site vừa thuộc animator vừa dispatch slot 31; entry update chỉ tới được qua `ldr xN,[vptr,#0xf8]; blr xN` chung trong 16 hàm engine không liên quan ⇒ không thể đặt tên scheduler từ slot-index, nên chu kỳ dừng ở mức phủ định có biên. Container: `0x10ecb08` **10 ref/10 owner** (batch, riêng animator); `0x10e18b0` ≥64 capped/59 owner, `0x10e18f8` ≥64/62, `0x10e19c8` ≥64/62, `0x10e18b8` 63/54, `0x10e19d0` 32/29 ⇒ 4 cái sau là global engine dùng chung, đọc 130 về registry `0x10e18b0` giữ nguyên. Callers 107, owners 200. **Không chạy lệnh nào.**

Derived `datas/l3_ef6b75ef131_native_vtable_dispatch.json.gz` **4749B/SHA `70cb303b9a306e7851d3911282ee81342e6d1d910be368fda039ac2590377198`**; pins tool+input trong artifact; **15 focused PASS/0.079s; full 1870 PASS/297.232s; check PASS; Verify40406194497 SUCCESS exact scientific f13f770dd**; receipts `raw/l3-ef6b75ef131-verification/`; official131HANDOFF **6428104532**. Static-only per 6418032974/6418326986; không selfACK/merge/main; protected3 không đổi. Review: (1) bounded negative đủ đóng câu "ai dispatch" cho lane này chưa, hay 132 phải cross-check 16 owner slot31 với call vào `0x6b0000..0x6c0000`; (2) `0x10ecb08` chỉ 10 ref — có đáng một chu kỳ riêng? #27-full vẫn OPEN: dispatcher/owner class, heap, scheduling, clip/clock writer, pose/blend/apply, readback/render.

## Hiện hành130 / arena/ef6b75ef / #27 update/trigger driver (static)

Claim **6427572973**. [Report130](apk-analysis/130-ef6b75ef-native-update-trigger.md). Hai probe mới từ cache XAPK fail-on-miss: `owner130` (40 window, 22 seed xuống 2 tầng caller, run **40403425044**/source `ca0c21b8f`) và `owner130b` (11 window, 9 seed đi lên + `ADRP+ADD` container, run **40403634092**/source `63eb9d186`). **Không chạy lệnh nào**, không dựng object.

**Ai lái rebuild:** header `0x10b0c80` (35 slot) được cài tại `6b9ad8`. Năm slot trả lời được: slot **2** `6b1914` (rebuild-all: `6b1a00`→`6b1b1c`→`6b1bb0`→`6b9ed4`), slot **3** `6b1c5c` (`3f9cf4`, nếu `w1==0x10` thì `6b1c98(x0,0)`), slot **10** `3e079c` (accessor `[x0+0x30]→+0x60`, else `[0x10e19c8]`), slot **31** `6b947c` (update), slot **33** `6b6ab8` (param → `572c60` với `w1=0/3`). **Cả năm đều 0 direct code ref** trong closure 2 tầng ⇒ dispatcher không nằm trong kết quả, chỉ khẳng định "virtual-only".

**Chuỗi rebuild `6b2258`:** gate `ldrb [+0x194]` bit4; gate `[+0x30]`→`3df584` bit0; `6b1a00` (reset: `+0xb0=1`, zero `+0x108/+0x118/+0x150/+0x158`, cuối cùng `+0x188=0`); `6b7158`; `[+0x1b8]` guard; `6b7d58`→`6b81c4`→`6b6dec`→`6b6fdc`; tail `6b7c58(x0=x19, x1=x19+0x208)`. **Flush `6b1c98(w1)`:** bit0 chạy `6b2050`+`6b1b1c`, rồi đúng gate `+0x194` bit4, `6b2258`, `6b1f04`, tail `6b22c8`. **Batch `6b27dc`:** container `0x10ecb08` qua `3d9648`, set bit6 `+0x194` (`orr #0x40`), gọi `6b1c98(el,0)`, clear bit (`and #0xffffffbf`). **Query `6b4bfc`:** `[+0x188]==0`→`6b2258`; nếu `w[+0x19c]`&&`[+0x608]`&&`[[+0x608]+0x130]` thì `s0[+0x488]`→`[[+0x608]+0x130]`; trả `[+0x188]`.

**Số đếm được:** 177 fact byte-verified, **70** call site unique (`bl`55/`b`15), **5** `blr`, **27** offset field neo vào object, **2** offset chủ thể khác (`element+0x194`×3, `entry_obj+0x20`×1), **19** stage, 5/35 slot. 14/70 site có caller ngoài window (ghi `caller_start=null`, không suy đoán).

Derived `datas/l3_ef6b75ef130_native_update_trigger.json.gz` **7590B/SHA `6afffcec6902b22285f1b46c84fa3f2a0221967bd7ef2b3b45471b88299c8057`**; tool+input pins trong artifact; **20 focused PASS/0.073s; full 1855 PASS/311.529s; check PASS; Verify 40404161026 SUCCESS exact scientific 8db8c21c2**. Receipts `raw/l3-ef6b75ef130-verification/`; official130HANDOFF **6427817329**. Static-only per 6418032974/6418326986; không selfACK/merge/main; protected3 không đổi. Review: (1) "virtual-only 0 direct ref" đủ chưa hay vòng sau phải quét slot-load indirect; (2) bit6 `+0x194` là marker batch tạm thời chỉ suy từ set/clear quanh `6b1c98`. #27-full vẫn OPEN: dispatcher, registry `[0x10e18b0]`, object sau `+0x618`, tên class, 15 callee chỉ xuất hiện làm đích gọi, clip/clock writer, pose/blend/apply, readback/render.

## Hiện hành129 / arena/ef6b75ef / #27 owner-side linkage (M1)

Claim **6426998422**. [Report129](apk-analysis/129-ef6b75ef-native-owner-linkage.md). Ba probe mới từ cache XAPK fail-on-miss: `owner129` (8 window, caller/linkage BFS + table walk, run40399193071/source9707d26a5), `owner129b` (24 window, thân producer + ADRP+ADD installer, run40399523874/sourceb39baaf17), `owner129c` (16 window, node ctor + owner registry + rodata string + cả vùng table, run40399754616/source5076e2fb7). **Không chạy FDE nào**, không dựng object giả.

**M1a CLOSED bằng byte:** `node+0x118` là **owner field** — ctor `6ceb88` zero-init tại `6ceba4` (`stp xzr,x9,[x19,#0x118]`), và trong **36 unique window** chỉ có **đúng một** store `6cef80` (`018c00f9`); store nằm trong set-owner wrapper `6cef64` (120B/30 lệnh, so sánh cũ tại `6cef6c`), wrapper chỉ được gọi từ `6b8268` trong `6b81c4` (73 lệnh). Giá trị do `6b6c40` (33 lệnh) resolve: `[x0+0x19c]` id runtime, zero→null, map toàn cục `[0x10e18b0]`, lookup `38cbb4` tại `6b6c74`, fallback `3d8614(id)` tại `6b6ca8` (hook `0x111dba0`). Không RELA addend nào trỏ `6cf7b4/6cef64/6cefdc/6bba20/6b6c40/6ceb88` (0/0/0/0/0/0). Producer thứ hai `6cefdc` (8 lệnh) **không** ghi field; nó chạy trên node lấy từ vector `animator+0x498` (record 0x10B), sau check owner `6b7ff0` và gate virtual `+0x138` `6b8000`.

**Node class:** `6bba20` (28 lệnh) = allocating ctor: size `x2+0x1d0`, allocator gốc **`3c986c`**, align0x10/tag0x5e/line0xab/label0x12da21 (rỗng), ctor `6ceb88` (37 lệnh, chạy base `6d6aa0` của124 trước), attach `572a38` (node+0x20=controller, controller+0x34++, controller+0xac|=0xC8). Ctor cài **3 bảng**: `10b0f98`(43 slot) tại+0, `10b1100`=primary+0x168 tại+0x110, `10b1130`=primary+0x198 tại+0x120; clear +0x128/+0x138/+0x148/+0x188..0x1a7, +0x158=0x4b, +0x160=const, +0x1c0=0/+0x1c8=0/+0x3c=3, subobject `6c3dc8(+0x170,+0x110)`, `6a6ff4(+0x1a8)`.

**Entry & graph:** `6b947c` nằm ở table `10b0c80` slot `+0xf8`, **0 direct BL/B** → chỉ vào qua virtual; từ đó `6b7d58` (191 lệnh, rebuild: `6cefdc` cho từng node trong `animator+0x498`) và `6b81c4` (73 lệnh, setup: `6bba20`→node→`6cef64(node,owner)`). `6b7d58` dựng graph handle `+0x618/+0x620`, output `+0x628/+0x630` (alloc `3c9298`, 0xe0B, ctor `6ce464`→vptr `10b0f30` 11 slot, +0xdc=-1), rồi gọi output `+0x28`(node) và animator `+0x108`. Chuỗi rodata gốc: `0xc0fce`=`%s.Animator`, `0x101411`=`AnimatorOuput`, `0x12da21`=rỗng.

**Vùng table:** `10b0a00..10b1900` có **23** bảng RELA-dense; 9 bảng thuộc family này = **181** slot: 10b0f98/43, 10b1100/4, 10b1130/2, 10b0c80/35, 10b0f30/11, 10b1240/28, 10b1420/2, 10b1150/28, 10b1330/28. Slot được gọi resolve thật: node `+0xe0`→`6d017c`, `+0x138`→`6d137c`; animator `+0x50`→`3e079c`, `+0x108`→`6b6ab8`; output `+0x28`→`6ce4fc`; 10b1240 RELA `+0x80`→`6d46a8` (120). Slot count = dense run RELA, slot không relocate là **unknown**, không phải null.

**M1b OPEN runtime-only:** thiếu id tại `animator+0x19c`, nội dung registry sau `0x10e18b0`, và vtable owner; không code nào cài vtable owner. Ràng buộc hình dạng: owner có slot `+0xb0()`/`+0xa8(bool)`/`+0xd8()`, list head `+0x38` splice với `animator+0x540` qua `49ffc8`. Hai string gợi ý owner phía Animator nhưng **không khẳng định class name**.

**M2 CONTRACT_ONLY:** object = return của owner `+0xa8(w1=1)` (`6cf80c/6cf810`), lưu `node+0x128` (`6cf814`); null→error path `6cf8f0`; `+0x10` = count record 0x10B (`6cf8a4/6cf8b8`), alloc qua `node+0xc0` vtable slot0 size `count<<4` align8 (`6cf8cc`); 3 builder `b98c98/b98db4/b99120` nhận `(motion_object, node+0xc0)` ghi `+0x130/+0x138/+0x140`. Vì object đến từ runtime owner slot nên mọi input đều phải bịa → **không chạy builder**.

Derived `datas/l3_ef6b75ef129_native_owner_linkage.json.gz` **6357B/SHA `217f8893799733f1f36c9d73ac93ab0b9ca903ead81501492b9bab89fb85071a`**; 49 witnessed word; tool/test pins trong artifact; **24 focused PASS/0.016s; full 1835 PASS/289.771s; checkPASS; Verify40401190233 SUCCESS exact scientific2c710a7c2**; review requested ở §9 report. Receipts `raw/l3-ef6b75ef129-verification/`; official129HANDOFF **6427382388**. Static-only per6418032974/6418326986; không selfACK/merge/main; protected3 không đổi. #27-full vẫn OPEN: M1b owner runtime, scheduler/registration/dispatch, clip/clock writer, pose/blend/apply, Unity readback/render.

## Hiện hành128 / arena/ef6b75ef / #27 motion-set contract + M2 split

Claim **6426286596**. [Report128](apk-analysis/128-ef6b75ef-native-motion-input-contract.md). Static answer to the127 review question: 128 **không chạy thêm FDE nào** và **không lấy byte libunity mới** — toàn bộ lệnh lấy từ recovery127 40391655099/source b0a585e5e (raw `43adb19f…`). Byte-witnessed contract 4 FDE: `b98c98`53lệnh/`b98db4`133/`b99120`203/`6cff44`74; **61 witnessed word**; motion header 6 field (+0x00 child count, +0x08/-0x18 slot-relative arrays, +0x10 secondary count, +0x20/+0x28 merge ptr); child record 7 field (+0x00 index/+0x04 slot/+0x18 count/+0x24 flag/+0x28 weight/+0x30/+0x34); secondary record 3 field (+0x00/+0x08/+0x34);9 allocation;4 derived object. Motion base read-only trong cả 4 FDE. Delivery tail đọc `[[node+0x30]+0x20]`→qword đầu→vtable+0x18, loop bound motion+0x00; target identity vẫn MISSING.

**M2 split:** M2a serialized content **AVAILABLE**, M2b runtime motion-set object **MISSING**, M2c producer **MISSING** (chỉ owner virtual +0xa8 trên node+0x118; 0 BL trong39 followed entry trả về motion set). Sửa câu quá rộng của127: raw **có** serialized content nhưng **không** có runtime object; execution boundary của127 không đổi. Controller1856: ControllerSize4110,1layer,8state,8blendtree,8node,0child index,clipID[7,1,2,3,4,5,6,0],6param,không có m_ClipBindingConstant. 8clip: bindings **402**, pptr **0**, streamed frame **142**, constant **177**, channel **654** (coverage exact 8/8), muscle bytes72300. Với controller này `pptrCurveMapping` rỗng nên phần pptr trong từ ngữ M2 của127 không áp dụng. Negative: controller-graphs(`72b9cfad…`,52 controller) chỉ có m_Binding hash; enemy-clip-links(`fe001faf…`,154 animator) chỉ có membership+muscle bytes, curves_decoded=false 8/8.

Derived6119B/SHA**2b1b5e8277469e3105ac1ae75af3b5c97a8e82bc4a8f85d364be3fe6551849d3**; tool`16b4915a…`; test`ecdd1a2d…`; **22focusedPASS/0.979s; full1811PASS/312.217s; checkPASS; Verify40395096377SUCCESS exactscientificcefd38a9f0ba3c645e25e14405b2f0556bbd0ef7**. Logs/REST/check/local/claim/spec receipts trong `raw/l3-ef6b75ef128-verification/`. Official128HANDOFF **6426561197**; report+receipts `34a97a992`. Không FDE nào chạy nên không có sink/service mới; `not_run` nêu lý do từng FDE. #27-full vẫn OPEN; M1 owner class/vtable, original heap, scheduling/registration/dispatch, clip/clock writers, pose/apply, Unityreadback/render còn nguyên. Static-only per6418032974/6418326986; no selfACK/merge/main.

## Hiện hành127 / arena/ef6b75ef / #27 graph-builder fallback + prerequisite contract

Scientific **6781d828f6e283d11e6508c051e3000df233714c**, claim6425979864. [Report127](apk-analysis/127-ef6b75ef-native-graph-builder-prelude.md). Original graph-builder FDE6cf7b4..6cff44 executed **entry→RET** on null-clip domain (node+0x118/0x1a0/0x1c0/0x1c8=0): 6ceeb0 zero-count cleanup, original single dealloc call6cef44→3c9438 (declared sink), original fallback branch6cf7ec→epilogue6cff0c, canary compare, RET6cff3c. **51originalinstructions** per case across3variants (A5/00/relocated), whole FDE, no staged intervals.

Six direct callees captured with exact FDE extents (6ceeb0/b98c98/b98db4/b99120/6f15cc/6cff44); static read shows build path needs real serialized clip data (clip+0xc0 blobs, pptrCurveMapping, per-child weight tables). **33 byte-witnessed instructions**, 11 required node fields, and a **5-item missing-X map** (M1clip/vtable, M2clip-data, M3owner/pool, M4child/previous arrays, M5binding tables). Build path NOTexecuted; no fabricated serialized data.

Derived2850B/SHA**8b9df00387893418d21608ddda6d7287c5c313ecd213770091b60720370f344e**; raw12454B/SHA**43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1**; recovery40391655099SUCCESS/sourceb0a585e5e/raw7f3a1e596. Tool/input SHA pins inartifact/report. **17focusedPASS0.086s/full1789PASS313.073s/checkPASS; Verify40391943675SUCCESS exactscientific**. Logs/REST/local/check/recovery/spec/review receipts retained. Protected3absent/unchanged; noAPK/assets/>5MB/main/merge/release changes.

Coordination: 123APPROVE, 118SUPPORTED, 124APPROVE(addendum1206425737935); **126 review and 127 review pending**; #27-full OPEN. Remaining: graph-builder build path/serialized controller/clip bytes, original heap, game-side instance join, scheduling/registration/dispatch, clip/clock writers, pose/blend/apply, Unityreadback/render. Static-only; no selfACK/runtime/lane takeover.

## Hiện hành126 / arena/ef6b75ef / #27 native graph-builder dispatch

Scientific **01448eec4273ba2fdbebe6c3a442c8bf8e658d3e**, claim6425017706. [Report126](apk-analysis/126-ef6b75ef-native-graph-builder-dispatch.md). Uses a5 N2 serialized owner (fixed commit7e5abde5, controller1856=Body1/Boss-37004, component493584, GO76852, root73241) as READ-ONLY prepared state. Original libunity scan: **2directBLs** to graph-builder6cf7b4 at6cef84/6cefe4, **0RELA addends**. Captured FDEs6cef64..6cefdc (set-controller wrapper) and6cefdc..6ceffc (rebuild wrapper), helper6d6bf8/6cf768, tail5710ec/57112c. Graph-builder0x6cf7b4 itself is explicit synthetic sink; virtual+0xe0/+0xd8, memset/stackcheck PLT, controller/owner/chunk/TLS are prepared. Original callers/helper/tail execute; full graph-builder/serialized controller state NOTexecuted.

Four cases: set-full70instr (1GB sink,2virtual, native helper/tail writes controller+0x118=owner, +0x102=1, +0x103=0), set-early8 (no GB/virtual), rebuild8 (1GB, 1virtual tail), set-null66 (1GB, 1virtual). Counts: **4cases/3GBsink/4virtual/2directrefs/0RELA**. N2 unresolved edges remain unproven: graph_builder_range_to_controller_1856_instance=false, runtime construction/playback=false. No observed game instance or a5 artifact edit.

Derived2685B/SHA**f209ea3fbc57b3b934c0f4a049f617ff54639e00e83be5fe4430da2a95c60bf5**; raw5326B/SHA**05c3ae3e4af03fffa2a880003c78e82f71044647f39e896e3180dd28d0977eb7**; final recovery40385235238SUCCESS/source050185f61/raw7f4f62c00. Tool/input SHA pins inartifact/report. **21focusedPASS0.093s/full1772PASS309.470s/checkPASS; Verify40386829829SUCCESS exactscientific**. Logs/REST/local/check/recovery/N2/spec receipts retained. Protected3absent/unchanged; noAPK/assets/>5MB/main/merge/release changes.

Spec103/105/106 coordination retained: R1 finalAPPROVEbounded123, R2 SUPPORTEDbounded118, R1-addendum120 and N1 review/D-notes belong AI-3/a5, #29 lane closed. Official126HANDOFF ID appended below; #27-full still open. Remaining: full graph-builder serialized-controller state, original heap, game-side owner instance join, scheduling/registration/dispatch, clip/clock writers, previous/activepose/apply/Unityreadback/render. No selfACK/runtime/readback/render.

## Hiện hành125 / arena/ef6b75ef / R2 review-118 AI-3

Scientific **e2f4b0e45e15bf47fae8dcf717f9e8726dbbe5df**, claim6423892767. [Report125](apk-analysis/125-ef6b75ef-review-row16-118.md). Static read-only independent review of AI-3 fixed commit e3fbb4dbc679c5d07ff8c520f8e13827baeae53c, report118 SHA96f2f768…, artifactSHAc33ad8a8… (728633B). Raw peer report/artifact + source-verification141588B retained; 252 shard blobs14813405B read from fixed peer commit but not copied (SHA/size/row/aggregate receipts only). Verified1587/1587 source pins, 0mismatch; 252 shards, 251×250+65=62815 rows, all196B/inverse-equal; 62815 unique renderers/GOs, 61864/951 sprite PPtrs, 62426 enabled, 1377/61438 scene/asset context. Catalog2185, scoped1897/no-reference288 (all NOT_GLOBAL_UNUSED), native1802+additional210−overlap115=1897, root1250/720 tuples, categories892/1450/3990.

Verdict **SUPPORTED_IN_VERIFIED_SCOPE_WITH_3_WORDING_PRECISION_NOTES_AND_BOUNDED_GAPS**: D3 (115 of288 no-reference rows still retain atlas_memberships_not_usage), D1 (new branch-owned wording applies to252 shards, while source_pins include inherited901+411+7 raw/tool pins), D2 (class1 is supplied-schema selection + inverse equality, not per-row discovered class_id). No numeric contradiction. Not independently recomputed: captured_context_status, captured_union, owner/edge hash matches, context-shard content, original binary bytes, per-row class1 metadata.

Derived3713B/SHA**0f1354ae23ba8d03b05f29b8d40e4db80f5dc21b846f34b551baec6ca6d270ba**; raw manifestSHA**6cf679df352073941d4c3f0060a913956c4cbefab730567b9816a66214a03c0b**. Tool/input SHA pins inartifact/report. **24focusedPASS0.071s/full1751PASS305.608s/checkPASS; Verify40381758335SUCCESS exactscientific**. Logs/REST/local/check/receipts retained. Protected3absent/unchanged; noAPK/assets/>5MB/main/merge/release changes.

Spec6423276716/6423721976/6424044328 assign-remind-accept R2. R1 final6424767705 APPROVE bounded123 after corrections, not #27-full/runtime; ef124 remains separate R1 addendum. Official R2 `review:` comment ID appended below. No selfACK/full#27closure; no runtime/Unityreadback/render/native execution/peer branch edit. Peer/a5/AI-4 lanes untouched.

## Hiện hành124 / arena/ef6b75ef / #27 specialized node factories

Scientific **98e5ba9666103ca354ce3fd6116ca295b497c30d**, claim6423259070. [Report124](apk-analysis/124-ef6b75ef-native-specialized-node-factories.md). Original graph-builder6cf7b4 has7directBLs to four factories:6d25f4(A×1)/6d2664(B×1)/6d26d4(C×2)/6d2744(D×3). Each factory entry→RET executes native constructor/base/pool/list code with explicit allocator sink at3c986c and exact PLTmemset/stackcheck bindings; TLS/pool/owner/node synthetic. Constructor/vptr identities: A→6d6a1c→10b1440(sizeX2+178); B→6d850c→10b1730(+170); C→6d2894→10b1150(+180); D→6d81f8→10b1640(+120). Four exact RELA vtable groups retained, no invented class names. Cleanup570ff0 naturally skipped. Source integration uses one factory-C node with post-factory harness bindings→10parentcalls/930DWORDs equal118. Serialized controller graph-builder NOTexecuted.

Derived7107B/SHA**b5a9023bab54691e920afc71b8d483f2f3dc07732e0bea662ecb85bfe72f36ca**; raw30708B/SHA**27645c8c3586d85a8e5bc93ea008577d2c57641bd93257ee676faa327bc5901a**; recovery40371804376SUCCESS/sourcef92c75fba/raw0db96cba3. Tool/input SHA pins inartifact/report. **33focusedPASS2.353s/full1727PASS288.642s/checkPASS; Verify40374283338SUCCESS exactscientific**. Logs/REST/local/check/recovery/spec/review receipts retained. Protected3absent/unchanged; noAPK/assets/>5MB/main/merge/release changes.

Spec6423047661ACK/CLOSESbounded123 synchronized. R1 review progress6423751973 corrected report123 wording (complementary53-candidate scan vs3KNOWN_VPTRS; encoded metadata usage `0xa0003ca7` vs UTF8Stop). R1 full review and independent122review pending. Spec6423276716/6423721976 assign/remind R2 review-118; claim/handoff IDs appended below. No takeover of AI-3/a5/AI-4 lanes; static-only per6418032974/6418326986. Original graph-builder/serialized controller state, allocator/heap, servicebootstrap, clip/clock writers, previous/activepose/blend/apply/readback/render remain OPEN.

## Hiện hành123 / arena/ef6b75ef / #27 original vtable linkage + callback marker

Scientific **1d6fbcbb7e5f8ae35135ee098b5a4816ea9d4f84**, claim6420235916. [Report123](apk-analysis/123-ef6b75ef-native-vtable-linkage.md). Replaces122's3synthetic virtual sinks with originalvtable10b1150 and real methods571b3c/571a80/6d5134; constructor6d2894 sets vptr, factory6d26d4 creates manager, graph-builder6cf7b4 has two direct BLs6d2950 at6cfc34/6cfc44. Explicit sinks remain only allocator3c986c, PLTmemset109ace0, fatalstackcheck109acc0; TLS/pool/manager/list/nodes synthetic. Original reserve/notify/register,57095c/570a70,571b58, factory/constructor/helper/list code execute. Sourcegraph3nodes→third gets118/128/130/1d0 harness bindings→10parentcalls/930DWORDs equal118. Real game graph-builder/serialized controller NOTexecuted.

Spec93/94 assigned final native-relocation marker to this lane. Bounded static decode from retained raw: `0x2ADFB48` (native-relocations key among288733)→`0x2BE5CB8`→stringliteral `Stop`; exact original RELA hex/literalhex `53746f70` pinned in3rawcells. This resolves literal identity only, NOT method pointer, RegisterEvents delegate, callback invocation or runtime. a5 artifacts read but unchanged; static-only per6418032974/6418326986.

Derived7082B/SHA**190864db435ee7ed32536ee75b8a10af20deabe288e5514bb3801977950aaf0c**; raw21548B/SHA**f194160b8a19989a7d368bc84c46b7934f8dabb7d4faa42d8c72819af12ae77e**; final recovery40363114036SUCCESS/sourceee1143bd8/raw128cdeebf; earlier failed/superseded runs and diagnostic retained. Tool/input SHA pins inartifact/report. **36focusedPASS1.967s/full1694PASS284.247s/checkPASS; Verify40366819899SUCCESS exactscientific**. Logs/REST/local/check/recovery/marker/spec receipts retained. Protected3absent/unchanged; noAPK/assets/>5MB/main/merge/release changes.

No externalACK/CLOSE122 seen; independent122review pending. Original game graph-builder/serialized controller state, original allocator/heap, servicebootstrap, clip/clock/control writers, previous/activepose/blend/apply/readback/render remain OPEN. Callback invocation MODEL_NOT_MEASURED runtime. Peer8141386a, AI-4, a5 G1 lanes retained, no takeover/import.

## Hiện hành122 / arena/ef6b75ef / #27 native graph-populator loop

Scientific **d15858faa4a31090355e6ba86221d91c69f26a79**, claim6418915726. [Report122](apk-analysis/122-ef6b75ef-native-graph-populator.md). OriginalFDE6d2950..6d29e4 executes entry→virtual reserve→countloop[121factory→node+b0/+3c→6d81b0→57104c→570abc null-slot branch→570a70→virtual register→virtual notify]→RET6d29e0. Three explicit synthetic virtual slots +10/+18/+70; allocator sink at3c986c; prepared manager/list-owner/TLS/pool chain/node blocks. Real virtual implementations/allocator/heap NOTexecuted. Native zero writes at6d81c4/6d81c8, node fields, list count/head/flags and queue tag/counter verified. Error helpers52e15c/b2e604/3c9438 and cleanup570ff0 not executed. Source graph creates3nodes; only third gets post-graph118/128/130/1d0 bindings and fixture clocks;10parentcalls/930DWORDs equal118. Shared lineage, no fresh source decode or live graph proof. No direct branch reference to6d2950 in scanned range; indirect callers remain open.

Derived6095B/SHA**5a09fe730587c4ade3bfdaa541ead63e754b674fc7caee52b47ed6f8dd3edc35**; raw10782B/SHA**014c74e6ed2fca8884697c61b870f8bd2d03c07e766ec9f1ac288b7248b90a39**; final recovery40343238879SUCCESS/source0a6387ea7/raw08d9c1c44; initial40342559786superseded. Tool/input SHA pins inartifact/report. **30focusedPASS1.642s/full1658PASS279.933s/checkPASS; Verify40347869822SUCCESS exactscientific**. Logs/REST/local/check/recovery/spec receipts retained. Protected3absent/unchanged; noAPK/assets/>5MB/main/merge/release changes.

Coordination: **spec6419109494 externalACK/CLOSESbounded121**, not122/full#27. Spec6419688649 noted122in-progress; official122handoff updates it. Owner/spec6418032974 static-only and6418326986 lane split retained: this lane libunity.soFDE; a5 game-sideC#writers/bootstrap. Peer8141386a#8, AI-4#30, a5phase4 lanes retained, no takeover/import. Real virtual implementations, game manager/graph dispatch, original allocator/heap, servicebootstrap, clip/clock/control writers, previous/activepose/blend/apply/readback/render remain OPEN.

## Hiện hành121 / arena/ef6b75ef / #27 native node factory

Scientific **f58d0ebbb1f26bfc8992c4207cb8f051cb639f6b**, claim6417816695. [Report121](apk-analysis/121-ef6b75ef-native-node-factory.md). OriginalFDE6d5e58..6d5ec8 executes entry→BL3c986c allocator **sink**→120constructor→natural skip570ff0→572a38 handle/list→RET6d5ec4, **220nativeinstructions** incl174constructor. Explicit synthetic allocator request X2+200/align16/category94/flag0/emptyCstringat12da21/auxAB returns prepared storage; original allocator/heap NOTexecuted. Native writes owner+34 count41→42, owner+48 circular list links, **owner+ac ORc8**, node+20 owner; node+ac unchanged. Primaryvtable/RELA and native pool effects retained. Upstreamcaller6d2950..6d29e4 captured, NOTexecuted; its loop/virtual calls/6d81b0 are next structural lead, not live graph proof. Post-factory118/128/130/1d0 bindings and clocks remain harness;10parentcalls/930DWORDs equal118. Shared lineage, no fresh source decode.

Derived5569B/SHA**ca37bac84e6135b928e933240b0c1f214516d4f3d9251d76c07b9d5384a2427a**; raw8951B/SHA**1149739845da278dcf2308e840336ec34652f24a0bb3a4db5d20c84b28cdec5a**; final recovery40337151003SUCCESS/source0cb0fd50f/rawcca51db0b; overbroad40335200188superseded. Tool/input SHA pins inartifact/report. **27focusedPASS1.425s/full1628PASS281.896s/checkPASS; Verify40339667616SUCCESS exactscientific**. Logs/REST/local/check/recovery/spec receipts retained. Protected3absent/unchanged; noAPK/assets/>5MB/main/merge/release changes.

Coordination: **spec6417893389 externalACK/CLOSESbounded120**, not121/full#27. Owner/spec **6418032974 CLOSES#28runtimeprobe**, static-only (live-DPS/#27consumption/second-device not measured). Owner/spec **6418326986 splits#27**: this lane retains libunity.soFDE pipeline→graphcreation→servicebootstrapnative→clipbinding→clock/controlwritersnative; a5 takes game-sideC#writers/bootstrap. No boundary crossing/no import. Peer8141386a#7 static lane retained. Originalallocator/heap/factoryupstream/graphregistration/servicebootstrap/clip/clockwriters/previous/activepose/blend/apply/readback/render remain OPEN.

## Hiện hành120 / arena/ef6b75ef / #27 original node constructor

Scientific **10b46c13d32592953416389bdf2d0407a8fd434d**, claim6417390505. [Report120](apk-analysis/120-ef6b75ef-native-node-initialization.md). OriginalFDE6d353c..6d35f8 runs entry→base6d6aa0→57054c→member6a6ff4→RET6d35f4, **174nativeinstructions/0sinks**. 447/512bytes nativewritten,65preserved; bitfield+38 read/modify/write, not memset. Installs primaryvtable10b1240/secondary10b1420; primary+80RELA10b12c0→119parent6d46a8. Direct factory6d5e58 captured but NOTexecuted. Prepared pool/global/label/storage only; original poolpop/counter/queue append native. Sourceconstructor + explicit post-constructor118/128/130/1d0bindings +10parent calls →930DWORDs equal118. No fresh source decode or live graph proof.

Derived6484B/SHA**fe2c0997d2ecf28e2f2ea4f06376d7e51fecebe7c47d135e4523acbd0f498c0e**; raw4357B/SHA**d8708494976e94b6310d299ab66e290091ef6204507bbaa854358a201fbd8950**; recovery40332491334SUCCESS/source7715cb756/rawd6a33c2d5. Tool/input SHA pins inartifact/report. **20focusedPASS1.133s/full1601PASS277.824s/checkPASS; Verify40332906465SUCCESS exactscientific**. Logs/REST/local/check/recovery/ACK stored. Protected3absent/unchanged; noAPK/assets/>5MB/main/merge/release changes.

Coordination: **spec6417392256 externalACK/CLOSESbounded119**, not120/full#27. Peer8141386a#6rep/a5primary+runtime lanes retained; no takeover/import. Originalallocator/factory/handle/graph creation/servicebootstrap/clipbinding/clockwriters/previous/pose/blend/apply/readback/render remain OPEN.

## Hiện hành119 / arena/ef6b75ef / #27 parent + second-phase guards

Scientific **b9e6765fa6266ae87e628d7f43f716147f74ba44**, claim6417082119. [Report119](apk-analysis/119-ef6b75ef-native-parent-second-phase.md). Originalparent6d46a8calls118then6d3ebc, writesnode174=1andRET6d46f0. Complete no-pose parent10sourcecalls/930DWORDs/29974nativeinstructions match118; no staging. Three original second-phase guards nullblob/mode−1/flag28zero execute24/29/31instructions. Syntheticdescriptor pointer atparameters10is required BEFOREflag28check; not observedgame descriptor. Active secondphase NOTexecuted; original prerequisite map preserved, no fake rig/converter. Nullparentalso writes174=1, so bytealone≠sampling/application proof.

10focusedPASS1.382s/deterministicPASS/full1581PASS280.259s; Verify40330340745SUCCESS exactscientific. Artifact3623B/SHA49eb74d14c974dafabae8dc5cbe30804f9872edee25807c2e16adaecd73de78f; raw2249B/SHA99950204cef0afd07919048073a20a305df61c70e43f98c38cfcfa4a167df321; recovery40330141486SUCCESS/source9b1a55f66/raw42b05ba61. Raw/logs/pins/receipts retained. Actualnode/graph/writers/previous/rigpose/blend/apply/readback/render OPEN; no selfACK/full#27closure/protected3/main/merge/vehiclechanges.

Coordination: **spec6417186640 externalACK/CLOSES118bounded**, corrects117FCVT+directedULP≠116FRINTAtie-away. Peer8141386a#6rep/a5primary+runtime lanes retained; no takeover/import.

## Hiện hành —118 / arena/ef6b75ef / #27 full current-only caller entry-to-RET

[Report118](apk-analysis/118-ef6b75ef-native-current-caller.md). Claim6416802429; scientific **79602dd6f221eac8f0289e522abbaff48ed15924**. EntireFDE6d38bc..6d3ebc executes entry→RET6d3eb4: realprologue/TLS/context→realclipduration→time→stream→scratch/phase/guards→epilogue, **no manualPCstages**. Enforcedcurrent-only/no-pose domain frameflags0/28/29=0, rig80/82=0, prepared—notobservedgameflags. Conversion/previousbodies skipped natively, unsupportedflagdomains rejected, no fake rig geometry.

Source1609unchanged9048B/10fullcalls/930DWORDs bit-equal;8syntheticcontrols.18successsamples32862nativeinstructions/18modffcalls;sourceRET/SP/canarychecked. SyntheticTLS+28canary1122334455667788, notAndroidTLS/session. Corruption reaches originalPLT109acc0/GOT10e3d00`__stack_chk_fail`, explicitfailure sink throws—**not fake success**. Nullblobfallback6d3600→6dacf0→b92414executes87instructions/0substitutions; frameflag/resetdefinedfields only, padding notclaimedzero. Positivecurrent-only branch leavesexternalposebufferA5unchanged, no appliedpose/property proof.

40focusedPASS2.261s/deterministicPASS;**full1571PASS274.031s / Verify40329033477SUCCESS exactscientific79602dd6f**. Actualcompressedlogs/REST/local/checkreceiptsretained. Artifact6091B/SHA4eaa9a118efbb7787680b0057c3cb6f2fd2bd59e50d8cd82743e92c084671e8b;raw4808B/SHAb1c46fe69e117a9b9b8d79eddd90b8a448b257a8389c12417f25d972d260eabb. Finalrecovery40328588214SUCCESS/source353d890ae/raw2aba8a5fd. Actualnode/game-sidewriters/graphflags/previous-time/rigpose/conversion/blend/normalize/apply/bootstrap/readback/render stillOPEN. Fullselectedbranch≠fullAnimator;no selfACK/full#27closure.

**Coordination:** spec6416823283ACK117boundedcontext synchronized. Correctedreviewterminology:117FCVT+directedULPadjustment≠116FRINTAtie-away (receipt rounding-clarification.json). Peerrestartnotice6416880872preserves8141386a/#6repclaimandprimarya5;notDISPUTED/takenover. Runtimevehiclelaneunchanged/no workhere. Protected3pathsabsent/unchanged;no main/merge/release/render acceptance.

## Hiện hành —117 / arena/ef6b75ef / #27 native context writer + actual clip duration vtable

[Report117](apk-analysis/117-ef6b75ef-native-clip-context.md). Claim6416392949; scientific **7f182db37d0a8232bf429fb20b8427fa076fc062**. Original clip ctorb69d14 storesvptr10c3fa8; original RELA10c4050(+A8)→b6bf94reads sameclip+1e0muscle blob stop5fc−start5f8. Full contextwriter6d3744 followsnode+1d0/realvtable, normalizescurrent+previous doubleclocks and copiesraw controls/flags. **0external context substitutions**, no mockduration/vtable. Native directed f64→f32 adjustment gives0.7bits3f333334, notnearest3f333333; subnormal/−0/duration0 checked. Earlyb6a838guess rejected asoriginalB.LT/non-FDE, notexecuted.

Threeexplicitmanualcallerintervals3924..3960 /39bc..39c0 /3a20..3a48 readblob/context/query/cache/output/loop natively, run116time+115stream, storephaseNode170. **NOT fullparent6d38bc**, nointerveningprevious/TLS/pose/blending/application execution. Source1609unchanged9048B,10stagedsamples/930DWORDs bit-equal; node clock/control/loop inputs stillprepared, notlive. 12standalonecontextcases718nativeinstructions;18stagedsamples31272nativeinstructions/18modffcalls (contextnoextra substitution).

40focusedPASS2.351s/deterministicPASS; **full1531PASS275.071s / Verify40326789273SUCCESS exactscientifichead**. Actual compressed focused/full logs +REST/local/check/recovery/specACK receipts retained under117-verification. Artifact5925B/SHAef1d97806f66c54daa4399237fc5df6e72950facd805b6093733644b55e40e85; raw36176B/SHA9bfa2fdd7f0a015b9a1ea17306c7fef8627a6410f845b4940aa19ea708d2bf60. Recovery40326227797SUCCESS/sourceaed913143/rawca1a449a8. Nodecreation/game-sidefieldwriters/graphstate/scheduling/fullcaller/weighting/normalize/apply/bootstrap/readback/render stillOPEN. Official117HANDOFF **6416723856**; **external spec6416823283 ACK/CLOSES bounded clip-context**, not selfACK/full#27closure.118continues fullselectedcurrentcaller; directedconversion≠FRINTAtie-away clarification retained.

**Coordination:** spec6416406730externallyACK116boundedcomposition; source1609zeroDense remains clip-scoped, notglobaldeadpath. Vehiclepermissionswidened byspec, originalstaticAPKauthorityunchanged; runtimevehiclelanea5 remains theirs/no vehicleworkhere. Spec6416527317crossbuildruntimecatalognotindependentlyrevalidatedhere. Peer8141386a#4handoff6416546977/#6replicationclaim6416555265retained, no glyph/atlas takeover/import. Protected3pathsabsent/unchanged; no main/merge/release/render acceptance.

## Hiện hành —116 / arena/ef6b75ef / #27 native clip-time+dense composition

[Report116](apk-analysis/116-ef6b75ef-native-clip-time-dense.md). Claim6416092786; scientific **61f31ae26f23908ffa2b281e6dee6e1427c5fcb8**. Original6d2e94→b93158→6df270→stream/dense/constant now executes in prepared context. Native serialized field anchors m_StartTime+5f8/m_StopTime+5fc/m_CycleOffset+608 pinned. Actual normalized-query negative integer−1 givesphase1/cycles−2 (not `%1`); S4negative-zero flips sign; native FRINTA quantization can return sample beyondstop. Dense6df518→6df6c8 executes on explicitlysynthetic3×2frame-major input; half-frame beforebegin extrapolates−5, not universal clamp.

Original source1609unchanged2262words/9048B, source start/stop/cycle adapted to native fields +explicit context1/0/−1/loopbool;10normalizedqueries/930DWORDs bit-equal separate-f32. **Source dense curve0/sampleArray[] despiteframe420, dense branch skipped**, no observed nonempty game dense claim. Originalaggregateinitializer6deefc executes632instructions/source, requests32B+1860B through explicitallocator; mixed order1continuous+1discrete+2dense+2constant demonstrated. **48modff/5memcpy service substitutions** over47calls/29126native sampleinstructions; no zero-hook or Android-libm claim for116.

40focusedPASS1.249s/deterministicPASS; **full1491PASS262.153s / Verify40324149097SUCCESS exactscientifichead**. Actual compressed logs/REST/local/check/recovery/specACK retained under116-verification. Artifact6108B/SHAbcde214305db2c739d1d48bad8670c1fbfb15138dcd93ebfd0bf607e2beec966; raw22100B/SHA1dfa2ca9ab5851d75e969d75428d4f96891464ddc7a6ba583103b87833539c31. Recovery40323651044SUCCESS/source99dcfc08c/raw7a2a64fde. Preparednativecontext/loopadapter ≠ actual Animator context acquisition/scheduling/weighting/blend/normalize/apply/bootstrap/readback/render; full#27OPEN; official116HANDOFF **6416337983**; **external spec6416406730 ACK/CLOSES bounded time+dense/constant composition**, not full#27/selfACK.117continues native context writer/vtable duration; actual Animator state/bootstrap/blend/readback remainopen.

**Coordination:** external6416110827 ACK/CLOSES115bounded consumer, #5replication/#6static remap; #4primary remainspeerowned. Runtime loader/probe order explicitlyassigned a5a74747, not this lane.115report/HANDOFF updated; no peer tools/runtime vehicle imported, protected3paths absent/unchanged, no main/merge/release change.

## Hiện hành —115 / arena/ef6b75ef / #27 actual packed StreamedClip consumer

[Report115](apk-analysis/115-ef6b75ef-packed-clip-native.md). Claim6415645613; scientific **61de2d57ef4898fb753bdcb714706a68d71215c2**. Original named AnimationClip API/serializer/compiler join owner+0x1e0; compiler returns muscle blob with ClipConstant relative pointer at+0x5f0, same pointer resolved by native caller6d2e94→dispatcher6df270→sampler6df310→selector6df768. Class74/native592 record confirmed. Static caller chain is not executed Animator ownership/scheduling.

Actual original stream words copied unchanged (2262words/9048B) for resources.assets:1609: **92continuous+1discrete**,10calls/930DWORDs bit-equal to explicit separate-f32 comparison. Native frame selection/indexed cache writes/scalar+SIMD cubics/discrete DWORD copy, rewind and same-time fast path execute; no AnimationCurve cache adapter/native evaluator952608 in trace. Original native initializer6df02c597instructions with1explicit1860B allocator call; zero external substitutions during samples.35source+synthetic sample calls execute23277nativeinstructions. Source raw-tree extraction is inherited, not a new independent UnityFS decode. Prepared native header/cache/output ≠ Unity objects/readback/playback/render.

40focusedPASS1.061s/deterministicPASS; **full1451PASS263.951s / Verify40321809391SUCCESS exactscientifichead**. Actual compressed logs/REST/local/check receipts retained under115-verification. Artifact12740B/SHA32f8105361ccd0f65c6fbe44f674ea48e88f42c541090c75c4b5fb979d559d20; raw147996B/SHA9b2b21a61fe9b459b4815ab5361576f036c873f36da9ecbce2a25ac618e1d364. Recovery40321260553SUCCESS/source d11ceabc9/raw7b4c31a87. **Dense6df518 identified but unexecuted; time wrapping helperb93158/Animator blending/application/bootstrap/readback/render still OPEN.** Source discrete DWORD is not promoted to resolved PPtr. No full#27closure/selfACK/main/merge/protectedpath changes.

**Coordination:** external6415645102 ACK/CLOSES114bounded-core (not full#27), a5#25bounded slice and#28fallback①. Broad#25durability/cloud/runtime and#28loader②③ remain open/theirs. Peer#26handoff6415743906 is static Board_Pause root/projection audit; no takeover/import.Official115HANDOFF **6416031711**; **external spec6416110827 ACK/CLOSES bounded packed-clip consumer**, not full#27/selfACK.116continues time/dense; Animator/bootstrap/readback remain open.

## Hiện hành —114 / arena/ef6b75ef / #27 native interpolation bounded-core HANDOFF

[Report114](apk-analysis/114-ef6b75ef-native-interpolation.md). Claim/góp ý6415164476, external approval6415328887. Scientific **33cdc61a912c006a6169583dfad444841033df7a**. Original icall389544→callback36e71c→evaluator952608; key search9528f8/cache952a80/direct951344/weighted951468/inverse951f60 execute. Smooth fixture cold173/hot30 instructions, zero hooks; weighted quadratic233instructions gives0.5 instead of unweighted0.15625; general weighted cases explicitly use host ELF math bridges, not Android ULP parity. Cached tiny-duration floor0x38d1b717 gives0.00724999979 vs direct0.5: don't promote universal cubic model.

Original parent6ad7e4→producer6c4480→append6c4360 emits3time/index/coeff records (255instructions); manual-entry native packing6c4b8c..6c4c40 makes84bytes header8/key20 (204instructions), prefill-independent. Sort/final sentinel/allocator suffix excluded. Source3keys from level2:4783 and source clip1609 channel0 arithmetic adapter pinned, neither is actual Particle/Animator consumer proof. Full#27 (native packed-clip ownership/selection/dense/weighting/runtime) stays OPEN. Official HANDOFF **6415566619**; **external spec6415645102 ACK/CLOSES only114bounded native-core** (not selfACK). Full#27 consumer/dense/weighting/runtime remains open;115continues below/newest section. 40focusedPASS1.464s; deterministicPASS; **full1411PASS311.581s / Verify40319106339SUCCESS exacthead**, raw logs/REST/local/check receipts saved. Artifact SHA9e795a9f60418e696265f3a35b7166cd3a0b701895beb734eab88aa4dabfaae3; raw43b0bd3f…/136316bytes, recovery40318758468SUCCESS/sourcefd49ac4e1/rawfc425ee28.

**Coordination updated:** spec **6415183905 externally ACK/CLOSES bounded #2 native mapping gate for113**, confirmed6415328887; no selfACK. Old113 review-pending notes below describe pre-ACK history. Runtime/bootstrap/services/setter/readback/render remain open. Góp ý on invariants vs inherited diagnostics accepted/forwarded; approved support view must pin snapshot path-set+commit+fail/skip groups. AI3 8141386a #5replication; a5 #5primary bounded ACK, #28fallbackstatic handoff6415301081, **#25 claimed6415333947**. Don't take peer scopes. No old sampler edits/protected3paths/main/merge/render acceptance.

## Hiện hành —113 / arena/ef6b75ef / #2 tag23 native registration + dispatch

[Report113](apk-analysis/113-ef6b75ef-native-tag23-registration-and-sprite-binding.md). Claim6414425266; scientific **f5a447c15a117ca4571e2768f0274d1ad4f20b39**, Verify **40314713081 SUCCESS exacthead**. Original initializer940218 passes descriptor10ead38/tag23/handler10b9d80; real registry wrapper6a9d50→manager6a97a0 stores tuple and slots[23] (**57native instructions**, allocator-only hook). Real custom lookup6a9674→6a94f0 selects handler (**69native instructions**), virtual reader/writer route to946d00/946ce4→93b09c; property resolver946d0c exactm_Sprite/attribute0 (**96instructions**, zero hooks). Static record SpriteRenderer212→10ead38; Sprite213→10e8fe0 (corrects early descriptor label). Class/component services, initialized container/BSS and setter sink remain synthetic; NOT native class bootstrap/Unity readback/render.

33newPASS0.615s; deterministic--check PASS; **full1371PASS316.344s**; raw local/CI receipts saved. Artifact SHA **af91630b507c877408427f5acad225ddcdf5e5429fa3f29069fc8b7b9af6036c**; rawSHA **b1370b5e691d6fa318a0ad22f5a03fbc1c9d81036f3cb6930d8a2ce145d74e8b**, recovery40313791590/source289d273ce/raw178644d4a. Existing Frame default denial unchanged; native-derived exact opt-in policy resolves clip1609/binding48/animatorlevel2:4695 to Finger2 SpriteRenderer5922.m_Sprite. Six original PPtr key times give model refs3799/2633 alternating; 51modeled binding writes per transaction, no projection/render.

**Status/coordination update:** historical105 and older `custom23 UNPROVED` notes below describe their original state;113 supplies bounded native mapping evidence, not engine runtime closure or selfACK. Spec6414685378 reopened AI3 #4–8, but **AI2 already claimed #5 via6414763120** after #24 handoff6414716483: do not take #5. No peer geometry/schema work imported. Protected3paths unchanged; no merge/main/selfACK. Official113 HANDOFF **6415103389** posted; **external spec ACK6415183905 closes bounded mapping gate**, not runtime;112 remains separately peerACKpending.

## Hiện hành —112 / arena/ef6b75ef / #17 native-schema generator fixture

[Report112](apk-analysis/112-ef6b75ef-native-controller-schema-generator-fixture.md). Original libunity code entry0xb7e1bc emits280nodes+1syntheticroot=281; one allocation/interning hook0x5eb544, native end/align/width/version/Array helpers execute74714instructions/3186uniqueaddresses. Full core schema equality and308payloads/291564bytes fulltree equality. Native ordinaryTransition13fields vs selector2fields corroborates616selectorrows omit interruption fields; NOT runtime semantics.33newPASS2.069s; full1338PASS320.132s, scientific9c351b766/Verify40310944208SUCCESS; deterministic--check/pins/protectedpaths/sizeguards PASS. Recovery40310298552SUCCESS/raw0cd42dc9a. Not Unity TypeTree readback/class91registration/bootstrap; sink/defaults/manualentry/Unicorn remain limits. Officialhandoff6414382164 posted, peerACK pending; no selfACK/full17closure.

**Coordination changed:** spec6413976783 ACK bounded110metadata/111selected-source recovery; board109/110/111 split. AI2replication6414135497 pins historicalraw72041a1d4/SHA0b541954… correctly; finalprobe has extra source slices, no invalidation/takeover. Spec6414165727 opens24–28/#2, first-claim; primary112 ongoing clarified6414230896, not available yet for#2. No new chain claimed. AI3geometry/protected3paths/no main/merge unchanged.

## Hiện hành —111 / arena/ef6b75ef / #17 independent UnityFS

[Report111](apk-analysis/111-ef6b75ef-independent-unityfs-framing-and-controller-recovery.md). Update/review claim6413146832. No UnityPy/third-party codec in recovery: original UnityFSv8,16nodes/2198block descriptors; own LZ4 actually decodes136selectedblocks/17825792bytes, reproduces two original metadata prefixes and308controller slice SHA. Three wholly-metadata original compressed blocks replay locally; other133source blocks only receipts unless pinned APK supplied. Shared builtin payload schema and source-layout consultation remain explicit; not clean-room/full engine/render proof.47newPASS0.739s; full1305PASS290.986s; scientificc9577acd2/Verify40304091950SUCCESS, deterministic--check/inputpins/protectedpaths/sizeguards PASS. Recovery40303755312SUCCESS/raw6925a526f; first guard failure and subsequent preserve-filename failure documented. Officialhandoff6413383750 posted, await peerACK; no selfACK/full17closure. Protected3paths/no merge/main; AI2#12/AI3geometry not taken over.

## Hiện hành —110-ef6b75ef #17 independent metadata/framing + clip identity

[Report110](apk-analysis/110-ef6b75ef-independent-controller-framing-and-clip-identity.md), artifact `l3_ef6b75ef110_controller_framing.json.gz`:2v22strippedmetadatafiles/704961objectrows, ownstdlibparser matcheswholetableUnityPydigests; independently computed308controlleroffsets used toreadoriginalsourcebytes/recheck109SHA.793cliprefs→791qualifiedclass74identities; crossfile sharedassets2:91 clip[1] fileID4→resources:970 viaexternal[3]. Notclipcurve/runtimeproof. UnityFSbundledecomp/naming + builtincontroller schema stillshared, formatlayoutconsultedUnityPysource NOTclean-room.32newPASS4.053s; full1258PASS293.450s; scientificf4a634617/Verify40302093121SUCCESS, deterministic--checkPASS, rawlocal/CIreceipts preserved. Continue6412825946, finalhandoff6413105118 posted, awaiting peerACK; no selfACK17. AI2#12latest6413053430/code32c87fa0fa preserves template≠sceneinstance/camera gap; no takeover.

Spec6412786774 ACK#21 provisionalconstructoridentity, runtime/modeopen. Report109officialhandoff6412780728 alreadyposted (boardstale), reminded6412825946; actual108550RELA/773vs0Add correction6412630804 preserved. Don'ttouchAI2#18/#23 orAI3geometry; custom23UNPROVED/protected3paths/no merge/main/render.

## Hiện hành —109-ef6b75ef #17 independent payload decode, shared schema/framing

[Report109](apk-analysis/109-ef6b75ef-independent-controller-payload-decoder.md), artifact `l3_ef6b75ef109_controller_decode.json.gz`:308originalcontrollers/291564bytes, stdlib-onlyreader consumes all and fulltrees308/308matchUnityPy;232/232oldrawtreejoins match,76outsideoldsubset. **Schema thực tế từUnityPy builtin versionDB (strippedfile), NOT serialized schema inAPK**; bundle/framing/sharedschema vẫncommon-mode, khôngfullindependentAPKparser/nativeinterpolation. All counts794states/386Any/147state/616selector/421conditions vsold232667/343/125/464/376. ControllerSize literal khôngdiskspan ở308/308; padding giữhex.**36newPASS0.741s/full1226PASS286.296s/Verify40299839743SUCCESS/code99d778f38**, REST receipts saved; chưa selfACK. Claim6412551521; xinreviewdispositionpartialindependence, khôngselfACK.

Spec a54ca00e5 reply6412555942 đãnhận GetDevice wordingcorrection; AI2#23handoff chưaartifactremote nênspec chưaACK, AI2#18claim khônglấn. Correction6412630804:report108handoff6412515057 đãcó; actual550RELA/773vs0Add, không548/1383. #21 chờreview, khôngtựđóngsemanticstage. Custom23UNPROVED; protected3paths/no merge/main/render giữnguyên.

## Hiện hành —108-ef6b75ef #21 constructor binding576, chờ independent review

[Report108](apk-analysis/108-ef6b75ef-map-entry-constructor-bindings.md), `datas/l2_ef6b75ef108_map_entry_bindings.json.gz`:25224original ARM64 instructions,550RELA after decimal-offset recoveryfix,12actualstaticstores,576unique IA→field/index paths. Two source executions:cap0 helper773 vs cap1024 inline writes/helper0, canonical roots identical.68lists+1dictionary,716arrays=715static+1external-sized, metadata values shared olddecodedinputs (NOT independent APK parser).**25newPASS5.787s/full1190PASS283.598s/scientific537e9024d/Verify40298061301SUCCESS**; receipts đã lưu, chưa selfACK. **Không tự đóng stage/chapter/mode semantic mapping/runtime parity**; consumerGetListWaves static28/clamp source audit8anchors only. Board_Challange.NumberChallanges length0 là fixture, không APKdefault; testlength7 giữ576paths.

Peer review6412200891:AI2 f246e4bd6/109 đúng source/UI reader, original payloadSHA khớp probe107; RD1red relateddocs còn phải sync/finalgreen. AI3 ceebe881d chưanewgeometrycommit tại review;CLAIMED/setup khôngDONE;nhắc#5 concrete border5739. Latest AI2 5ed3328f8/report110, spec cf3d464b9§24.50: addendum6412391042 chỉ ra full GetDevice12546d0/200bytes có ở ownpickup-currency/Device_Saved_Data (chưa có trênAI2), sửa “body unavailable” thành chưaconsult/import; không làm thay#22. RD1 vẫnFAIL, AI2 đãclaim#23 tôi không làm. Spec c2db940f §24.48 giữ#20AI2, #21 tôi; không lấn ownership. Custom23UNPROVED; no readback/render acceptance/no selfACK/main/merge/protected3paths.

## Hiện hành — 107-ef6b75ef review + support, #20 đã RÚT; #21 CLAIM

Report [107-ef6b75ef](apk-analysis/107-ef6b75ef-peer-review-and-withdrawn-board-probe.md): đã góp ý hai digger tại6411812459, cập nhật6411911083 sau khi paginate thấy comment mới. AI2 tip96fc9d30f/108 là PARTIAL native interpolation; AI3 tipceebe881d setup/re-export chưa geometry delivery, **đã claim #4–8**6411894051. Spec e9a6cb05a §24.46 ACK106 (arithmetic/model only), §24.47 ACK108 (serialized coverage closed NOT_EXERCISED/native OPEN). Không dùng sticky53 stale cho current ownership.

**#20 owner a5a74747** claim6411807151 tới trước. Claim tôi6411812830 RÚT tại6411911083, dừng mở rộng. Probe đã có trước discovery chỉ supporting artifact `l2_ef6b75ef107_board_power.json.gz`, không tự nhận #20 DONE:2×float24,3 original RELA,96+2 bounded ARM64 fixtures,28 tests mới; full1165 PASS275.064s, scientific90bb6d934/Verify40295149652SUCCESS. Bàn giao AI2 đối chéo chứ không sửa tool của bạn. Đã khắc phục page100 bỏ sót comments bằng `--paginate`.

**Claim hiện tại của tôi #21**6411921147: report108-ef6b75ef, artifact `l2_ef6b75ef108_map_entry_bindings.json.gz`. Cần nối576 IA→container/entry indices→native GetListWaves; không repackage inventory typed576/614 structural classification hoặc gọi candidate campaign250 là binding proof. Recovery10840295237073SUCCESS:25.224 original ARM64 instructions +548 candidate RELA, đã pull raw9b0cd4f15. Lần đầu40295033775FAIL; parser regex bỏ dotted b.hs và nuốt operand-free ret, đã sửa/test25224 source rows rồi retry (failed log download EOF nên không nói đã đọc traceback). **Chưa có derived entry-binding artifact/acceptance108**; bước tiếp native constructor container tracking, không coi recovery là DONE. Không lấn geometry của AI3 hay #20 của AI2. No merge/main/self-ACK; protected3paths giữ nguyên.

# Phân việc vòng 4 — cái còn thiếu thật

[Report91](apk-analysis/91-spec-review-hp-writers-and-drone-board-consumers.md) **đã làm yêu cầu spec6400762294**, review peer ecff896c. HP Start/cctor/reset/event36+64/GetStartHp/tech/device được nối; Board ctor price24→SetUpgradeCost, static attack12×2→GetPlayerPower→textDispDamage. **Không còn queue HP writers chưa đọc**; cập nhật spec từ D sang named-path evidence, không universal2500. UI500/800 khác combat450/6000, không lấy Drone_Get_Datas xác nhận UI.56 new/full648 PASS; contract `player_hp_board_flow.json`. Nhờ peer áp90+91/ACK; sửa MISSING§2.1/§5 map structure DONE≠entry binding UNKNOWN và DATA_SYNC ACK89 stale. Queue sau:23 wing còn lại; prefab/loadout drone ID/serialized turnRate3; map/save named consumers. Không merge/push peer.

[Report90](apk-analysis/90-wing-level-barrels-and-current-drone-base-fire.md), `datas/wing_drone_flow.json`:73 ranges/6041 instructions,68 anchors,44 numeric fields;92 tests mới/full592 PASS. **Áp spec:** shared Level lazy−1/cache/cap; wing1/source10003 numbers/rate/packet law;9 projectile implementations count per barrel/no midloop charge gate; sweep4 và strict laser7/9; ability25 base/(2.5*points), BaseDamages12/.16-level/rank/abi21=2.5. Không extrapolate wing1 sang23 tàu khác; không tự bind serialized drone IDs từ suffix hoặc ctor default8 của SerializeField turnRate3. **Peer:** ACK88/89 đã nhận (raw peer-review); xin ACK90 khi áp trên nhánh spec, không merge/push peer. **Queue tiếp:** đọc SetBarrels/Shoot23 ship còn lại từ raw combat-chain; bind drone prefab/loadout/sourceID và serialized turnRate3; HP writers theo comment6400762294 đã thực hiện ở report91 (xem đầu file). Đừng suy common HP từ không thấy tên mảng hay đòi screenshot/runtime trước khi đọc raw.

## Hiện hành — report89: pickup → callback → collected currency

[Report89](apk-analysis/89-pickup-dispatch-and-collected-currency.md), `datas/pickup_currency_flow.json`:20 ranges/3530 instructions/63 anchors,50 tests mới. IPooling.GetID slot0,13 switch bytes/coin aliases70001=70011,70002=70012; direct callback assignments. Collider item trước contact-hit guards; drone emits2 rồi pool, receiver không pool. Coin formula strict thresholds5500/4300/3300/2500×L,stagegroup/caps/device/.86/trunc; storecoinCount trước synchronous48; delta0 vẫn emit. Burst28 conditional69/165 khi thu đủ từ0, không cố định28 và không gộp payout qua threshold. GetStatValue2 formula có raw, array values test là synthetic chứ không APK table mới. **Peer** ACK88/89 đã nhận sau mốc89 (xem update90 ở trên); không merge/push peer. **Batch kế tiếp mốc89 đã thực hiện ở report90**; queue hiện hành xem đầu file, không viện thiếu raw chung hay đòi screenshot/runtime.


Report89 nghiệm thu: full500 PASS37.337s, code0a700993d, Verify40214936072 SUCCESS55s. Findings giao PR12comment6400594184; chưa ACK89. Recovery40214229547/raw eaa5c7434; release media vẫn draft.

## Lịch sử — report88: producer địch thật → FX/gold/items

[Report88](apk-analysis/88-enemy-hit-producers-and-gold-burst-chain.md), `datas/enemy_hit_callback_flow.json`: **16 method ranges/1256 instructions/56 anchors,19 serialized co-attachments**,4 exact callback/listener bindings +6 type joins. Skeleton.Start **overwrite** hitCallback; DropGold.Start **Combine** hitDamageCallback; Test_Enemy.Combine chỉ là component test, không thay gameplay producer. Skeleton17 và DropGold2 trên GO cóHealth đã joinfile-qualified/membership, không tự coi đãspawn. DropGold ctor28/10/iPlus1, strictlost>iPlus×10, mỗi invocation chỉ1event, damage argumentunused. Event6→Items_Manager chia spawn budget:28→3×70001+5×70002 (8objects),không28objects/28tiền; radius4pieces literal6766e63f khácnearest1.8. Đã đọc ellipsehelper +pool/IItem/explicitactivation, không measured playback.

**Đã ACK87** ở PR12comment6400347386, peertip8ac40be40e; chưa ACK88. AI spec cập nhật findings88 cùng87, không merge/push nhánhpeer. **Tiếp static:** pickupbranch Player_Physics.ItemCollected14bc328/OnTriggerEnter2D14bc9c0→Controller.OnCollectCoin1/2 để nối collectedcurrency, không suy giá trị nhặt từchia5. Queuepeer: wing-cannon SetBarrels/getter14b1eb0 và dronebasefire; reviewrawđãcó trước khi gọi thiếu dữliệu. Khôngreopenpool-history/screenshot/runtime để né static. Full450 PASS38.652s, code16748ccc3/Verify40213772726SUCCESS55s; findings gửi PR12comment6400435826. Recovery40213095828SUCCESS33s/raw098135279, mediarelease vẫn draft.


## Lịch sử — report87: end-invincibility, shield và invisible-zone

[Report87](apk-analysis/87-reborn-invincibility-shields-and-zone-state.md), `datas/player_shield_flow.json`: đã nối GOT2ae8560→RELA2be4670→metadata literal **RebornDone**, initializer delay3/10;7 roots/417instructions và18 tests mới. Không còn ghi Invoke target unknown hay tự gán2s. **Sửa85/86:** Physics.activeHitEnemey@90 là enemy-contact hit, KHÔNGmovement; Controller+48 là Player_Talent, bool20=reborning, KHÔNGinput. RebornDone giữ invincible ở shield branches, chỉ clear trực tiếp khi4flagsfalse; preserve≠settrue. Shield callbacks aggregate skill/101/103, không refcount rebirth/onehit. SetInvisible heal setup trước live reborn guard, exit A còn B vẫn clear invisible; không tự thêm replay zone trong RebornDone.

**Peer nhánh `arena/20330d0e-windwings-space-shooter-game-p`:** cập nhật các rule/erratum87 cùng6corrections đã giao86 ở PR12comment6400139575. **Đã nhận ACK85+86** ở PR12comment6400213174, peer tip266a05dd78; peer báo sửa6/6, text tipmới chưa được review lại trong batch87. Findings87 gửi6400262252, chưa có ACK87. **Việc static tiếp:** tìm producer writes/registration thật cho Enemy_Health.hitCallback@20 vàhitDamageCallback@28; receiver CalculateDamage158479c đã dịch85, fixture callbacks không phải registration evidence. Không quay lại pool-history/fullAPK/fullmedia hoặc xin runtime thay việc đọc native. Report87 code691f225b8, **full412 PASS36.340s/Verify40212492774 SUCCESS56s**. Recovery40211999354SUCCESS25s/raw7518813f4; hai failedrun do splitAPK đã giữtrace/sửa. Draftrelease vẫn giữdraft.


## Lịch sử — report86: review peer và producer extra-life/heal

Peer tip **b8f72a4127dbc2e7a24f8ff212172eb2f6eeb2ef**, snapshot10docs giữ raw. **Đã ACK84** qua PR12 (trước đây ghi chưa ack là trạng thái cũ), chưa ACK85. [Review86](apk-analysis/86-peer-spec-review-and-player-extra-life-heal.md) yêu cầu sửa: DATA_SYNC2723–2725 gộp11/13 waits và clone/projectile9; COMBAT355–365 dùng damage×interval ước lượngTTK; COMBAT416–432 bảng800/189 và noDamage=đồ trang trí; worklist cũ xin dữ liệu đã có; không nâng mục tiêu sản phẩm thành coverage/visual approval. Gửi peer sửa trên chính nhánh spec, không merge/push nhánh đó.

Tiếp việc đã hoàn thành **binding onExtraLife thật**: GOT2ae8480→RELA2bc83d0→OnExtralife14c42d4, cùng destroyShieldOneHit và WaitUntil noTouch; normal hồiHP1 trước pause/wait, resume timeScale .05 + HealHp(.5); PVP không wait/pause, HealHp(1). HealHp target snapshot, progress bắt đầu1, theo scaled deltaTime/null yield, không currentHP loop hay fullHP snap. Zone heal1.235%maxHP sau wait.2. Có19 checks mới, full394 PASS34.624s; code25734422b, Verify40211604072 SUCCESS50s. Raw2738ad848/recovery40211002716 SUCCESS. PR12 comment6400139575 giao6 corrections cho peer. Tiếp: **Invoke string GOT2ae8560** + end-invincibility flags/rewiring và enemy callback producers; rawController/RebornDone đã có, không xinfullAnalyze. Định hướng bám cơ chế bản gốc/art mới đã ghi; không chép câu “mọi thứ đã có/không test” thành bằng chứng.


## Lịch sử nghiệm thu — report85, receiver callback/damage/HP/death

[Report85](apk-analysis/85-damage-receivers-callbacks-hp-and-death.md) + `datas/damage_receiver_flow.json`: 44 body source walks/3485 instructions; enemy mutable ref + hai callbacks; controller rereadHP sau UpdateHpBar; player hai truncations → synchronous events21/39 → rereadHP → extra-life/death. Hai death overrides đã recover/dịch: Delayed dùng WaitUntil(condition), KHÔNG delayTime2; MB ba Wait1, không base Pool tail. Ability32 Destroyed là recursive damage request radius3, không chỉ FX, không dedup receiver. 48 checks mới; full375 PASS (36.026s), validate/regen/diff PASS. Code035a64f44, Verify40210554491 SUCCESS (50s). Raw220fa2d53, recovery40210107165 SUCCESS. Tiếp: exact producer/serialized receiver joins và extra-life/heal rewiring từ raw Player_Controller mới, không khai báo thiếu raw hoặc ép dependency này cần runtime. GOT2ae8480 ở Start cần metadata binding chính xác, không đoán theo tên. Không nâng callback fixtures thành subscriber thực tế. Peer nhánh `arena/20330d0e-windwings-space-shooter-game-p` áp corrections receiver cùng reports81–84; chưa có ack/merge. Coroutine recipe7 sửa typo return threshold .5, outbound .1 giữ nguyên.


## Lịch sử nghiệm thu — report84, đóng coroutine control/yield ledger83

Đã dịch control-flow đủ25 MoveNext (không còn inventory-only), giải3 computed BR từ9 byte APK, nối14 wait origins và7 factory args, có executable control models/regression. Quan trọng: 7/9 `_delay` sau attack;17 chờ sau cặp;18 toggle ParticleSystem.rateOverDistance chứ không spawn projectile. Xem [report84](apk-analysis/84-combat-coroutine-control-flow-reconstruction.md), `datas/combat_coroutine_flow.json`, `tools/verify/combat_coroutine_models.py`. Không suy dispatch thành hit/DPS hoặc coi đã có project Unity/C# hoàn chỉnh. Đã recover và nối thêm clone/pumpkin +2 iterator (30 methods); clone stop→wait0.34→pool, pumpkin deadline active2/charge1/duration4 +callback→Hide. Không chạy lại full APK/media. Local327 PASS; code58ef9809a, Verify40209405979 SUCCESS (37s). Peer đã được báo PR12 comment6399840843; chưa có ack. Peer cập nhật combat spec theo các correction này.


## Bổ sung hiện hành — report83 (25/10/2026)

Peer `arena/20330d0e-windwings-space-shooter-game-p`: khi cập nhật spec combat, đọc [report83](apk-analysis/83-main-rate-field-deadline-and-dispatch-audit.md) và `datas/combat_rate_consumers.json`. Rate là main-deadline interval; 23 schedulers extra counter, 19 riêng; 22/23/24 refresh `GetNumberAbility(4)` trong scheduler. N+1 dispatch chỉ khi N dương giữ nguyên/counter đầu 0, không phải N+1 projectile/hit. Đừng lấy spawner wait hay rate table làm player DPS. Agent nhánh này tiếp tục giải 25 MoveNext/14 wait sites theo §6, chưa giao peer làm hoặc coi complete. Không merge/spec-ack thay peer. Local 302 PASS; code `07f98ba80`, Verify `40207885962` SUCCESS (50s); peer đã được báo PR12 comment6399630253, chưa có ack.


> **Cửa vào hiện hành (sau report86):** đọc [START_HERE_NEW_GAME.md](START_HERE_NEW_GAME.md) + report81 combat-chain + report82 proof-audit + report83/84 rate/coroutine control,85 receiver và86 review/lifecycle. Review cf27b9755 và các vòng/snapshot cũ dưới đây là lịch sử, chỉ áp dụng finding còn mở; không tự là task hay phán xét hiện hành.

> Trạng thái hiện tại: `docs/conclusions.md`. Đã có **dữ liệu thô** trong
> `reverse-engineering/raw/` (typetree JSONL gz, UI layout gz, hằng số IL2CPP + asm).
> Mọi kết luận là **tạm thời** — phải ghi mức A/B/C khi trích dẫn.

## Luật (giữ nguyên)

1. Nguồn: `reverse-engineering/raw/**` (thô) + `datas/*.json` + `docs/apk-analysis/*.csv`.
   Không trích `PHAN_TICH_*` hay tài liệu tóm tắt cũ.
2. Chỉ ghi trong `docs/spec/`. Không sửa `reverse-engineering/`, `datas/`, `tools/`, `.github/`.
3. PR riêng `docs(spec4): ...`. Mỗi bảng ghi `(nguồn: file, mức A/B/C)`.

## Việc

### A. `docs/spec/CONSTANTS.md` — giải nghĩa hằng số IL2CPP
Nguồn: `docs/apk-analysis/19-il2cpp-constants.md`,
`reverse-engineering/raw/il2cpp-consts/<Class>.json` + `<Class>.asm.txt`.

- Với **10 method quan trọng nhất** (ưu tiên: `GetCostReborn`, `GetUpgadeCostCoins`,
  `GetUpgradeCostGems`, `GetBonusCoin`, `GetBonusExp`, `GetSurvivalScore`, `GetNumberWaves`,
  `GetPVPPlayScore`, `GetArenaScore`, `MAX_LV_TECHLAB`), đọc `.asm.txt` và viết lại **pseudo-code**
  của phép tính, chỉ rõ hằng số nào là hệ số, hằng số nào là clamp/epsilon.
- Bảng: `method | hằng số tìm thấy | ý nghĩa suy ra | mức tin (B/C)`.
- Những method chưa giải thích được thì liệt kê, đừng đoán bừa.

### B. `docs/spec/UI-MEASURE.md` — đọc layout thật
Nguồn: `docs/apk-analysis/20-ui-layout.md`, `reverse-engineering/raw/ui/*.json.gz`
(584 file; mở bằng `python3 -c "import gzip,json;..."`).

- Chọn 5 màn: `Board_Home`, `Board_Chapters`, `Board_Players`, `Board_Shop`, `Board_Endgame`.
- Với mỗi màn: bảng node (path, local_pos, scale, component, text/key), nhóm theo vùng
  (top bar / content / bottom nav / popup).
- Suy ra hệ toạ độ: bao nhiêu unit = 1 màn hình, vùng safe area, tỉ lệ.
- Kết luận: dựng lại được bao nhiêu % bố cục bằng số, chỗ nào phải tự thiết kế.

### C. `docs/spec/TEXT-MAP.md` — chữ nào ở đâu
Nguồn: `raw/ui/*.json.gz` (field `components[].text` + `key`) + `i18n/vi.json`.

- Ghép `key` → chuỗi tiếng Việt cho từng màn (bảng `screen | node path | key | vi`).
- Đếm: bao nhiêu % text node đọc được key, bao nhiêu chỉ có chữ cứng.
- Danh sách chuỗi cứng (hardcoded) — đây là chỗ phải viết lại khi làm bản mới.

### D. `docs/spec/GAPS.md` — còn gì không lấy được
- Tổng hợp từ `docs/conclusions.md` mục "chưa bóc được".
- Với mỗi mục: có lấy được nữa không, bằng công cụ gì, chi phí ước tính, và **nếu không lấy được
  thì thiết kế lại thế nào**.
- Đây là đầu vào cho quyết định scope, không phải danh sách mong muốn.

## Xong khi
- 4 file, mọi con số có `(nguồn, mức)`, không có kết luận nào ở mức C bị trình bày như số thật.
- Mỗi file có mục "còn thiếu" riêng.

## Ưu tiên mới — review nhánh spec 25/10/2026

Đọc **docs/HANDOFF_SPEC_REVIEW_71b1e9861.md** trước khi viết design tiếp.
R1–R3 là P0: timestamp không chứng minh thứ tự pha; 12 handler không mở khóa
793 event; base Enemy_Appear không chứng minh appearance của mọi enemy.
R4–R7 cập nhật raw và sửa điều kiện kết luận quá mạnh. Nhánh spec sửa tài liệu/
claim bên nhánh mình; nhánh dữ liệu giữ các task đào raw còn mở. Không merge.

## UI onboarding / first clear stage 1–3 — 25/10/2026

Xem report `docs/apk-analysis/42-early-stage-ui-flows.md`, raw
`reverse-engineering/raw/ui-audit/early-stage-coverage.json.gz`.
Chưa tuyên bố đủ luồng UI: có board/layout không chứng minh stage gate hoặc
queue popup. DataTutorials có getter hasTutStage1..4; chưa được tự gán nội dung.
Nhánh dữ liệu đã mở export native/typetree (921dc909b, Actions 40176643619).
Nhánh spec lập matrix first clear/replay/defeat/back/continue cho stage 1–3,
giữ UNKNOWN đến khi có branch evidence. Tutorial gameplay/HUD không nằm chắc
trong scope exporter root Board_/Popup_/Tab_; cần kiểm coverage riêng.

## UI drawing readiness — cập nhật sau native export

Report **43-ui-drawing-readiness.md**: đã có raw native daa2c3a03/40176643619.
Bắt đầu wireframe các board lõi được; chưa gọi đủ full onboarding. Đã resolve
stageIndex 0/1/2 → gate tutorial control/transform, drone, touch-skill (có thêm
điều kiện). Endgame.SetupTut với IndexTutorial<=1 ẩn Back/Replay/Continue.
Nhánh spec phải vẽ trạng thái này riêng và giữ callback bật lại OPEN.
Raw `ui-audit/drawing-inputs.json.gz` nối node → sprite gallery/contact-sheet;
raw `early-native-gates.json` giữ asm/check. Đừng match trực tiếp tên Unity với
tên gallery sanitize; dùng bảng original-name → type/path_id → gallery.
Exporter lượt tới bổ sung TMP/sprite properties và tutorial panel sibling;
chưa được xem như đã đủ pixel-accurate cho đến khi raw mới về/đã kiểm.

## Ưu tiên đồng bộ — tránh đọc mốc 019e704d1 cũ

Đọc **docs/HANDOFF_DATA_SYNC.md**. Kiểm trực tiếp remote ngày 25/10 thấy data
đã tới c570485c5, có 9 commit sau 019e704d1. Verifier spec local-first có thể
bỏ qua raw ở --ref mới khi file local cũ còn tồn tại. Fetch explicit remote
tracking ref, đối chiếu ls-remote/rev-parse và ghi source SHA trước khi báo lại.

## UI raw vòng tiếp — tutorial đã có layout, Map cần tái xuất

Đọc report44: raw c570485c5 có 8 tutorial refs/7 GO resolve local, text Việt,
font/style/sorting. Dùng ui-audit/tutorial-texts.csv + visual-coverage.json.
Endgame callback @0x126d3cc có nhánh bật Continue/ẩn Replay/IndexTutorial++;
static bool branch chưa resolve tên bằng registration map, không tự nâng kết luận.
Map đạt trần6000 node, không báo full coverage. Commit1989defc2 tăng12000 và
báo truncation; a2fac1df7 thêm external/font/material/camera context. Nghiệm thu
raw mới rồi mới bỏ OPEN. Tất cả là PROVISIONAL.

## UI routing vòng tiếp — report45

Raw routing-and-persistence.json.gz có direct-call sites, asm/hash và enum scene.
Continue không phải cạnh Next Stage duy nhất: có Home/Game routes, có nhánh
popupNotice khi btnX20Coins active; callback confirm tail-call Continue.
set_IndexTutorial gọi PlayerPreferences.SetInt, chưa chứng minh flush/restart.
GOT slot chưa được gọi là metadata address: metadata name recovery đã có raw,
lượt relocation recovery dùng native checksum-pinned để resolve đúng slot.
Không nâng Unknown chỉ vì có tên gần giống. Xem trạng thái nghiệm thu report45.

### Relocation recovery đã xác nhận (report45 bổ sung)

40180955473 success/633d552b1: GOT→effective metadata giữ native/script SHA.
Cờ là victory, key là TUTORIAL; fade callbacks load scene Home1/Game2.
Đừng gộp scene Home với Board_Home: Continue Normal chuẩn bị defaultBoard=6
(BoardStage), có zone/stars override=5 (BoardMaps). IsContinue=true/IsReplay=false.
Nhánh sau chuẩn bị: victory && IndexTutorial<=2 đi Game, còn lại đi scene Home.
Còn đọc Home_Loader consumer/queue để chốt màn hiện thực tế. Raw +10checks giữ
ở ui-audit/routing-and-persistence.json.gz, không chỉ lời bàn giao.

### Nghiệm thu raw UI 4c8d6461e (report46)

40180792800 success nhưng audit bắt 2 lỗi: native render-context thiếu file
scope; Map10315 node vẫn skip120 child do cap80. Không gọi full. 9f4f8fa10 sửa
cả hai và có test; chờ raw lượt sau nghiệm thu. Camera6/Material261/Sprite2185/
TMP7 typetree đã có để tham khảo, chưa được join external pathID khi scope rỗng.

### Cập nhật mới nhất — report47 thay trạng thái chờ của report46

Analyze40181265305 success/bot7325738be: scope đã đầy đủ; linker exact scoped
PPtr nối được 10.568 sprite +1.642 font +1.642 material occurrence trong 11root
được chọn. Raw `ui-audit/scoped-visual-links.json.gz` có hash/source/link từng node.
**Map vẫn truncated:**12.000node/2.760pending, không được gọi full. Collector mới
50.000/deque cần nghiệm thu snapshot kế; đừng lấy output cũ rồi báo đã sửa.

Recovery40181445658/f7f7ad7f3 giữ full metadata+relocations và extra-native.
`loader-and-prefs.json.gz` chứng minh Home loader nhận defaultBoard6, phát
OpenBoard56(BoardEvent selectedBoard,mode0), resetdefaultBoard1, rồi CheckSpecPopup.
Queue/callback/override vẫn OPEN. PlayerPreferences int wrappers tailcall Unity
PlayerPrefs; custom SaveToDisk không chứng minh flush TUTORIAL. Đọc report47
trước khi dùng report45/46; mọi kết luận PROVISIONAL, không blind-merge branch.

### Runtime probe — đọc report48 trước khi chạy thêm phiên

Đã audit remote25c367aca, không chỉ code cũ của nhánh này. Bản kia có injection,
property/array/anim/phone-interop fixes; không lặp lại kết luận "chưa sửa" từ bản cũ.
**Phát hiện từ APK gốc:** GP_Tutorials.get_IndexTutorial @14f4a14 có nhánh
StageTarget>=2 && cachedIndex==0 → cache6 +SetInt(TUTORIAL,6). `/statics` gọi mọi
property getter có thể tự làm đổi thứ cần đo. Dùng allowlist native field,
không arbitrary getter/forced init/Save. Raw asm/calls/metadata:
`raw/runtime-probe/getter-observer-effect.json.gz`; plan14fields/13methods ở
`stage1-3-watchpoints.json.gz` (kế hoạch, KHÔNG phải giá trị đã thu).

Run40181812673 CI xanh nhưng session/probe SKIPPED, artifact bridge:no; XAPK SHA
khớp nguồn gốc. Đã recovery40182134370 không bật phiên cloud. Phone log remote
lại thuộc packagePremium: không nhận làm gameplay evidence bản gốc.
`collect.sh` của remote còn gọi get ở4b trước definition: chuyển helper lên đầu,
kiểm JSON ok và missing/errors từng field, không lấy HTTP200/CIgreen làm nghiệm thu.
Giữ raw/provenance cho mọi lần đo, không blind-merge tooling.

### Ưu tiên mới từ người dùng — xem ảnh đọc flow, Premium để sau

Report49 đã xem35PNG của phone capture (ref25c367aca), chỉ dùng để nhận diện
trạng thái/luồng UI, không dùng balance, không đo/vẽ lại từ screenshot.
Có intro STAGE1 NORMAL/TOUCH TO PLAY; hint kéo tay; hint nhả tay đổi tàu;
Switch ships wisely Hard fight/Easy kill; combat; boss; VICTORY bị modal che.
Hint nhả tay còn xuất hiện lúc boss: không tự cố định nó ở đầu stage.
**Chưa thấy title stage2/3 hoặc kết quả sạch/Home/Map.** Tên p_2/r2_2 không phải
stage2; victory_next không chứng minh đã chuyển stage. Contact sheets không phải
timeline. Để nội dung Premium sang sau, ưu tiên thu chuỗi kết quả sạch→Continue
→titleStage2→titleStage3 có timestamps/actions. Manifest/raw quan sát được giữ
trong raw/ui-flow-review; JPEG duyệt ở docs/apk-analysis/ui-flow-review.

### Đã đào stage2/3 từ APK raw — report50 supersedes inventory gate OPEN cũ

Nguồn `ui-audit/stage23-ui-flow.json.gz` giữ24methods asm/hash/calls/metadata +
panelbinding/text; rodata literal/jumptable ở stage23-rodata.json. Recovery
40183022449 và40183197035 success. Board_Begin.Start chứng minh label stageIndex+1.
Stage2: internal1 && IndexTutorial1 → TutDrones(panel1906,delay2) → chờdrone →
3.9scaled s → timescale0/cover/focus skill → chờhasUseDroneSkill → restore GP_Time.
Stage3: internal2 && TUT_TOUCH_SKILL!=1 (KHÔNG yêu cầuIndexTutorial2 trong gate)
→ nếuTalentIndex!=-1 chạy TutTalents(panel1911,delay3), ẩnPause, lock input,
chờhasTouchBurst; callbackghiTUT_TOUCH_SKILL1, chỉ++Index khiindex2 && StageCurrent2,
bậtPause. TalentIndex==-1 có nhánh skip+ghi flag, không vẽ modal bắt buộc.
Không đòi thêm ảnh stage2/3 để bắt đầu dựng các panel/flow này. Giữ unknown ở
consumer eventState/grant/unlock/advance và runtime, không trộn với gate đã resolve.

### Report51 — consumer callback / equip / Continue đã bóc tiếp từ raw

`docs/apk-analysis/51-tutorial-consumer-equipment-continue.md` + raw
`ui-audit/tutorial-consumer-flow.json.gz`17methods/11checks;37tests pass.
Recovery40183580920 và40183664095 success. OnThroughTut table77a13e
`0029233d41555d634f74` dùng selector eventState+1:8=StartDrones,
4=lockUiTut+ShowDroneSkillButtons,2=unlockUiTut,5=HideSkillButtons,
7=ShowSkillButtons,-1=setup Controller/UI/unlocks. KHÔNG EventID.
GameStarted veneer2990898 load callback slot2ae8fb8 rồi quay14f4008;
slot→2bc4950→GP_Manager.OnThroughTut. Không bỏ branch veneer khi đọc asm.
Continue có nhánh IndexTutorial1 && slot0empty→SetDroneUsed(0,20001),
KHÔNG chứng minh ownership unlock. Loader đọc selection→Prefabs/Drones/Drone_.
Talent keyTALENT_SELECTED default-1. OpenBoardVictory normal route có tăng
StageTarget khi setup.stageIndex==target và target<ZoneUnlocked*10+9;
không tự thêm boolvictory gate. Continue nhánh min(target,current+1), nhánh khác
star-search; KHÔNG unconditional+1. LoadToLoading direct LoadScene2=Game,
không phải enumLoading. Fade callback và Game loader chưa nối hết.
Next: grant/unlock callsites, talent-selection caller, fade/loader, map-wave
consumer. Giữ raw mới GP_Spawner để nối tiếp; không cần screenshot làm điều kiện.

### Report52 — scene/fade → terrain → map wave consumer đã nối

Recovery40183973174 success/bot575113776; report52 và
raw/ui-audit/scene-map-flow.json.gz giữ12methods/13checks/cctor literals.
41tests pass. Fade callback1276e1c cũng LoadScene2=Game; wrapper gọi Unity
LoadScene(int sceneBuildIndex), không sceneLoading. FadeTo lưu Action+38,
MoveNext có invoke+38; chưa giải jump table8states/timing.
GP_Setup.Awake chỉ singleton; getterstageIndex đọc StageCurrent+24 khi nonbranch,
StageBranchCurrent+2c nếubranch; companyNameTest&&fixedStagePlay override riêng.
GP_Manager.Start14f3460→Spawner.LoadPlayer; normal terrain prefix
Datas/Maps/Terrains/Map- + stageIndex.ToString0000, GetComponentMapController.
MapController.Start132a84c getter→132a878GetListWaves, không +/-1. Normal
GetListWaves lấy listMapDatas+28/clamp. Tái đọc cctor literal array1406c9c=[164],
1406d10=[113,5], Listx28→static+28@140e19c; không đọc datas/maps.json.
Consumer formatID0000→Resources/Instantiate dướiparentWaves→SetLastWave→active.
GameMode0/nonbranch/ChapterCurrent0: display2→Wave_0164;
display3→Wave_0113 rồiWave_0005. Chapter>=1 đổi prefix Chapter2; branch riêng.
Đây là số prefab wave, KHÔNG enemy count hoặc thời gian chạy tuần tự.
Next: Wave/Spawner activation/completion; grant/select callers; fade dispatch.

### Report53 — wave/spawn-ended ≠ kill-ended

Recoveries40184325868/40184418916 success; bot00d23f3c1. Report53,
raw/ui-audit/wave-spawn-flow.json.gz22methods/15checks;45tests pass.
Spawner.Awake nối virtualOnSpawn vào Call_Point.onSpawn, không spawn thẳng.
Call_Point.FixedUpdate: chưaspawned, state!=Endgame3, MapController.isMoveEnemyLayer,
y<=ySpawn→spawnedtrue/invoke. WarningySpawn+3 là khoảngcách, KHÔNG3giây.
Wave.SetLastWave khởi CheckSpawnEnded; GetComponentsInChildrenSpawner(false).
Normal aggregation countPoints đợi ended callback, loại5EndMapPoint/6StartWavePoint;
branch-even riêng. WaitUntil countPoints<1→WaveEndedEvent74, nếulast→SpawnEnded73.
Path coroutine number/rate/IDpool, kết thúcinvokeended+28; không phải enemydeath.
Manager listener73→b__11_7→StartCheckEndgame. Poll đợi listActiveEnemies.Count0
&& Playing1; sau đó normal dùng GetMissionCompleted(killCount,countEnemies)>=0,
còncheckplayer; không auto-win/không hardcodekill100%. Wait2scaled s→manager
cleanup/stateEndgame→MoveOutPlayer→closurebool→OpenBoardVictory.
Next: đúngprefabWave0164/0113/0005→Call_Data/Spawner counts/timing; liveenemylist
add/remove và missionthresholds. Raw mới nhiều spawn implementations sẵn để nối.

## Agent hiện tại — report54, exact early-wave resource joins

- Đã resolve14 container entries từ APK pinned, giữ full trees + raw component
  bytes ở `reverse-engineering/raw/early-waves/`. Đúng default roots0164→148604,
  0113→21468,0005→38187 trong resources.assets; Chapter2/branch là roots khác.
- Report54 + verifier19 checks;48 tests pass. Slot cấu hình không marker:
  274/95/155, **không phải kill denominator hoặc observed enemy counts**.
- Không dùng `datas/waves.json` nhóm theo tên hoặc enum5/6 cũ. Không resolve
  generated typetree m_Script header; class exporter đọc parsed Mono head.
- Premium tiếp tục deferred. Agent đang tự nối GP_Datas event78/79 và
  Enemy_Destroy/pooling với mission thresholds, không cần chờ screenshot.

## Agent hiện tại — report55, pool-list và mission arrays

- Đã nối GP_Datas.ResetAlls: event78→Contains/Add listActiveEnemies+70;
  event79→Contains/Remove; event19→death callback có killCount+1c increment.
- Base Enemy_Controller movement-complete→DestroyType2→Enemy_Destroy.Pool→79:
  active-list rỗng không chứng minh diệt hết. Virtual override vẫn chưa join.
- Decode3 normal mission arrays bằng relocation→field-default12bytes, SHA256
  khớp hash field: mode0=.20/.45/.80;1=.35/.60/.98;other=.50/.80/1.
  Caller Stage_Datas.ModeCurrent+34, result−1..2, truncate float32 product.
- Raw `enemy-exit-missions.json.gz`,15methods12checks; toàn bộ52 tests pass.
- Next tự đào: Stage_Get_Datas.GetCountEnemies12c5f60 load resource/Call_Data,
  skip marker5, IPooling-ID filter; nối store GP_Datas+58 + filter membership
  và concrete Enemy_Destroy subclasses. Không dùng274/250 slots làm denominator.

## Agent hiện tại — report56: denominator và concrete destroy đã nối

- Raw mới: `early-waves/default-enemy-components.json.gz`14 exact roots, full
  root components/raw Mono bytes; Sub_Object.GetID recovered40185361444.
- MapController.Start132a5ec→GetCountEnemies12c5f60,132a5f4→GP_Datas+58.
- Filter là Stage_Get_Datas.listIgroneEnemies+18,31 cctor literal IDs; KHÔNG
  dùng Enemy_Data_Balance.listStaticEmemies thay thế. Chỉ38001 giao14 roots.
- Default chapter0 denominators: wave0164=262 (274−12),0113=87 (95−8),
  0005=151 (155−4); stage2=262/stage3=238. Native skip5, không skip6;6 arrayrỗng.
- Mode0 tier result0/1/2 thresholds:52/117/209 và47/107/190. Không gọi thắng
  ngay hoặc tự đổi sang UI stars. Mode1/other giữ riêng trong raw/report.
-14 Enemy_Controller.destroyScript PPtrs đều trỏ base Enemy_Destroy cùng root;
  đã cross-check ID/critical PPtrs bằng bytes, không resolve generated m_Script.
- `mission-denominators.json.gz`:4methods11checks;57 tests pass.
- Tiếp raw join result GetMissionCompleted→star UI/save + victory/unlock/Continue,
  và movement-completion callback registration/timing. Premium vẫn deferred.

## Agent hiện tại — report57: mission UI / saved stars / Continue

- Đúng `boards/board_endgame` root113205/resources.assets;1070nodes, Board
  component621494.3 normal Stage_Mission components648536/636132/696150;
  BtnContinue92306 persistent call→this board.OnPressedButtonContinue.
- Native Stage_Mission/GameDatas40185724759; prefab retry40185845817success.
- Ordinary LevelCurrent0: savedStars>rowIndex for old flags; result+1 saves
  only if more than prior completed rows; only NEW rows add GameDatas.StarCount.
  Keys StarStageMaster{stage}_{mode}, StarCount→Unity PlayerPrefs.SetInt;
  disk flush not proven. Replay3stars with result0 retains3/no new global stars.
- Animator triggers None/Collected/Clear, NOT SetBool.3 mission rows confirmed,
  not yet3 graphical star icons or clip durations.
- RunMissions new-row clear/reward→WaitForSecondsRealtime(0.5), includinglast;
  Continue→isQuitingtrue→SkipUnbox→StopAllCoroutines→settle remaining rows.
- IMPORTANT: GP_Endgame.OpenBoardVictory target++block14f08f4..14f09b4 has
  mode/target/cap guards but no read/test incomingvictoryw20. Do not restate
  “victory-only unlock”. Runtime defeat reachability still unproven.
- Raw endgame-missions/mission-progress-flow.json.gz18methods16checks;
  full63tests pass. Premium remains deferred.
- Next raw joins: movement-completion wiring/timing; target-advance defeat
  reachability; actual Continue visibility gates/Animator clips (without Premium).

## Agent hiện tại — report58: conditional false result reaches target++

- GP_Manager.<Start>b__11_7→StartCheckEndgame; `_endgame` callback metadata
  resolves14f6190→stateEndgame3. CheckEndgame gate active-listempty&&Playing1.
- Normal GameMode0/IsBranchfalse: kill result>=0 sets closure.victory;
  IHealth interface slot1=GetCurrentHealth()==0 forcesfalse. IPlayer slot0
  SetVictory() call is NOT evidence that closure bool is overwritten true.
- Join regardless bool→display.SetEndgame(bool)→2s SCALED→_endgame action→
  MoveOutPlayer(same closure callback)→OpenBoardVictory(bool). Distinguish
  force-VictoryNow callback which passes literaltrue.
- Exact MovePlayer dispatch recovery40186449228→755480732: bytes00162d8d at
  77a13a, base14f1c00; states0/1/2/3→1c00/1c58/1cb4/1e34.
  Move-out starts4sREALTIMEwatchdog before1sSCALEDwait. Watchdog invokes same
  callback then stops move handle. World movement y−2 then y15;0.3/0.5 are
  speed-accumulator increments per frame, NOT seconds; squared-distance1e−10.
- Target++ has GameMode0/stage==target/zonecap guards regardless incomingbool.
  Setter ADDITIONALLY clamps min(value,MAX_STAGE_INDEX), writes cache+3c and
  PlayerPreferences.SetInt("StageTarget"). No durable flush proof.
- False-input STATIC witness now connected to target-advance path, stronger
  than report57's local absence-of-guard. Still NOT a runtime defeat-unlock
  replay; assumptions: valid components, stable inputs/getters, live owner,
  external interface/event handlers don't prevent callback completion.
  Not mid-wave death/reborn; don't generalize to all defeat/Premium flows.
-15method bodies21checks in raw/endgame-missions/false-result-reachability.json.gz;
  source hashes for gzip use DECOMPRESSED bytes (timestamps are not game data).
  72tests pass. Next: actual Enemy_Movement completion/counter reachability,
  Continue visibility and Animator graph. Premium still deferred.

## Review nhánh spec theo yêu cầu người dùng — snapshot25c367aca

Đọc **docs/HANDOFF_SPEC_REVIEW_25c367aca.md** trước khi viết tiếp design.
Pin peer25c367aca99f06f14df546d2f30e60b427827157, đối chiếu data61fce8ae7.
Raw `peer-review/spec-25c367aca.json.gz` giữ9file/code/CSV + classifier experiment;
collector `tools/verify/peer_spec_review.py`,76tests pass.

- R1/P0: MISSIONS_STARS sai fallbackmode, thiếu arrays đã resolve; getter stars
  lưu bị nghi là tính kills. Dùng raw55–58, scope normal LevelCurrent0.
- R2/P0: ENCOUNTERS còn khuyên divide2/dedup theo tên. Rút lời khuyên; dùng
  container key/file/root pathID, không gộp normal với Chapter2.
- R3/P1:116 atlas name-unmatched không chứng minh116 sheet chưa tách; suffix
 5x2/2x3 không chứng minh crop16ô chắc chắn. T9 rect/atlas là gap THẬT, data nhận.
- R4/P1: CodaR22 bịR14 bắt trước (CSV4rowui/A); XVideoR23 bịR18 bắt trước;
 643 retained labels được cấpA vô điều kiện, không có provenance audit mới.
- R5/P1: readiness D3 vừapartial vừaclosed ở hai đoạn cùngfile.
- R6/P1: parser exception→SKIP/exit0; AB1 không đo67rect, AB4 chỉđếm CSV nên
  PASS không chứng minh semantic mapping. Thêm strict-required, không bỏref-first.

Nhánh spec sửa trên nhánh của họ; không merge/push thay nhánh spec. Mọi kết
luận vẫn provisional. Premium deferred; không dùng screenshot làm nguồn số.

## Agent hiện tại — report59: concrete movement end → pool (không phải kill)

- Recovery40187130445→12280632a có Enemy_Movement/VertexPath full native.
-14 enemy root referenced trong exact early waves đều Controller PPtr→base
  Enemy_Movement/Enemy_Appear/Enemy_Destroy; verify critical joins bằng Mono
  bytes. Tất cả typeMoveEnded0Destroy/endInstruction2Stop/persistent-eventempty.
- Controller.OnEnable→Appear gắn OnMoveCompleted1584778 qua slot2aec4d8;
  baseAppear gọi Appeared1584868 ngay→movingtrue. SetEventMoveEnded resetold
  delegate, self-stop+UnityEvent rồi appendcontroller chỉ khi mode0&&nonnull.
- PathFollow speed×deltaTime→VertexPath.GetPointAtDistance: normalize length,
  Stopclamp; callback cần finalinterpolation==1 && endpointdistance²<1e−10.
  PointToPoint cuối segment gọi cùng onEnded. Turretmovingtrue worldy<−15
  cũng gọi; Linearly cầnmoveintrue và vượt borderx±10/y±15.
- DestroyWhenDone2 BỎQUA death/hit handlers rồi Pool→event79→Contains/Remove
  active-list; KHÔNG tự chèn Enemy_Destroy.OnMoveCompleted hook vào CFG.
  Pool path không phát kill19; external listener effects vẫn chưa replay.
- Slots exact0164:Path150/Way104/Pin19/AirFree1=274;
 0113:PointToPoint80/Pin15=95;0005:Path140/Pin15=155. Không phải actualspawns/kills.
- AirFree BB-36001 córootAnimator, khôngturret, spawnerchỉITransform.SetAngle/
  SetPosition; CHƯA gánpath/waypoint ở bodyđó. Không suy tựpool hayphảibắn.
- Parser phát hiện2 ITransform trùngtên: globalTypeDef228 là3methods game;
  UIElementsTypeDef4428 làpropertiesUI. Giữnamespacekeys+testcollision, tránh
  nhầmglobal interface slot0/1 thànhget_position/set_position củaUI.
- Rawearly-waves/movement-completion.json.gz28methods20checks/14joins;
 84tests pass. Low-kill witness58 mạnhhơnnhưng vẫnstaticconditional, khôngreplay.
- Tiếp tự đào BB-36001Animator/controller/clips/events và terrainparent/scroll;
  T9assetrect/texture/rotation/trim vẫn taskraw nhận từspec. Premiumdeferred.

## Agent hiện tại — report60: BB-36001 streamed animation (provisional)

- CI40187741686→192d2290f: raw `balloon-animation/bb-36001-animation.json.gz`,
  exact root185704/Animator496390/controller1908;37nodes/full3clips+bytesSHA.
- `tools/verify/balloon_animation.py`→`decoded-clips.json.gz`:3clips17checks,
  giữframes/coeff/keyoffset/bindings/targets. Formatref AssetStudio pinned
  d158e864b556b5970709c2a52e47944d53aa98a2 +MIT giữ riêngtoolchain;khônggamefacts.
- Graph defaultSpawn1468(2.5)→Idle1467(10)↔Attack11466(12),speed1,
  exitTime1/duration0/no conditions;no params/AnyState/behaviours/events.
- QUANTRỌNG: **cả3clip animate root-local position** path0/attr1/Transform4.
  Animator.applyRootMotionfalse KHÔNG phủđịnh ordinary localtransform animation.
  Spawn(-12.41,7.33)→(-3.66,2.3);Idle ends(-3.77,6.04)=Attackstart;
  Attackend(-3.66,2.3)=Idlestart. Đây làkeyvalues,khôngworld/runtimebounds.
- 12/15/12streamedchannels;9/66/76frames kểsentinels;0dense;Attack3constant
  rootEulerzero. Firsttime−FLT_MAX không−inf;last+inf0keys. Khôngdecode dense.
- CRCm_Enabled3305885265: Barrels1MachineGun690037/Barrels2639146/script1:338
  resolve bằngrawMonoheader,KHÔNG lệchtypetreem_Script. Spawn2súngoff;
  IdleBarrels1on@0/off@9;AttackBarrels2on@0/off@10. Collider490394off@0Spawn,
  on@2.5Spawn/onIdleAttack. Enabledkey≠đãchứngminhshotcount/damage.
-9duplicatePointpaths giữlistkhôngoverwrite;mọibindingđangxétuniquetarget.
- Khôngterminalflyaway/poolstate/events/GameObjectbinding trong3clip; KHÔNG suy
  BBphảibắn/tựpool. Root-localkeys≠worldcubicbounds;parent/update-order/movein
  gates59 cònthiếu. Khôngnângconditional lowkillwitness thànhreachableplaythrough.
- Tiếp tựđào AirFree spawn-parent/terrain-scroll và Machine_Gun_Attack lifecycle;
  T9atlasrect cònrawtask;Premiumdeferred. Chi tiết report60,8tests mới.

## Agent hiện tại — report61: pool-parent/scroll/gun lifecycle (provisional)

- User yêu cầu tự làm tiếp cho đầy đủ, không cần hỏi từng bước. Đã chạy native
  recovery40188073425→c0ffce078: PoolingManager/Machine_Gun_Attack/
  Boss_BodyPhysics/Obj_Collider/Enemy_Datas fullasm+JSON; khôngbinary/APK.
- `tools/verify/balloon_lifecycle.py` + rawballoon-animation/
  lifecycle-parent-scroll.json.gz:40methods26checks,8tests mới/**100tests pass**.
  SHA gzip theo DECOMPRESSEDbytes;declarations namespacequalified.
- Pool getObject123a2c8:reuse list[0]/RemoveAt0 hoặc instantiateinactive,
  common worldposition+rotation, KHÔNG directSetParent/detach. GetObject(int)
  dùngposition(-255,-255,-255);ctorprefPos(-99,-99,-99),khônggameplayborder.
- Pool return123a66c:deactivate trước;nhánhvalidID/notContains/existingobjects
  SetParent(manager.transform)123a970 rồiappendlist. Guarded,khôngmọicall.
  Vìgetkhôngdetach,assetrootFather0 KHÔNGchứngminh reusedruntimeparent0.
- AirFreekhôngdirectreparent;PinMap→spawner.transform.parent1466b60;
  PinTerrain→serializedparentTerrains+30 tại1467154 (KHÔNGraycast/tựsuyMaplayer).
- MapControllerAwake lấyallMoveLayers[1]→enemyParentMove,RemoveAt1.
  UpdatebranchScrollMaptrực tiếp;commonDelta=multipleSpeed*deltaTime;
  allMoveLayers.localY-=delta*speed*boostSpeed;
  enemyParentMove.localY-=delta*speed CHỈisMoveEnemyLayertrue,KHÔNGboostfactor.
  ScrollBackgroundswrap worldY<−1.5*bgLength→+bgLength*countBg;khôngenemyPool.
  IsScrollingcómethodnhưngkhôngtựchènvàoUpdate/ScrollMapvìkhôngcallởbodyđãđọc.
- Gun exact690037normalbRate0/shotRate.15/speed8;639146barrelbRate.1/
  shotRate0/speed6;bothdelay1/Border0/turnRate2/turnNumber3/id80054/lifetime5/
  damage300serialized/allGunDatas[]/bltPinMapfalse/emptyturneventpersistent.
- GunOnEnabletimeToShot=Time.time+delay,resettimeToTurn/countTurn,bCount,
  inverse,stun;KHÔNGresetisTurnStarted/timeToBarrelShot/timeToStart.
  FixedUpdateisAttack→Border/Timer gate→stun→Shoot;khôngcoroutine.
  NoOnDisabledeclared;animationdisabled≠OnEndTurnShoot/death/remove.
  TurnhooksUnityEventkhôngownerpool;runtime listeners/actualshotschưareplay.
- EnemyMovementOnEnable1586024 chỉzFixed48,khôngresettypeMove/path.
  PathFollowpathnullreturn. Conditionalmovingtrue/typeMovePath0/pathnull/
  nonturret→khôngpathcallbackhayFixedUpdateboundaryroute,ngaycảanimationraxa.
  KHÔNGchứngminhstateđónắmgiữmọiruntimeBB;poolhistory/writerscònthiếu.
- Đọc report61 trước khi chốt stage2lowkill. Không được suy rootlocal=world,
  mọiAirFreeautoescape,hoặcBBmustdie. Kếtiếp:exactmapjoin+poolinstancehistory,
  typeMove/pathwritersvàexternalremoval/health/collision. T9atlasrect vẫnrawtask
  riêng;Premiumdeferred. Nhữnggapruntimekhôngđượcđóngbằng100unitPASS.

## Agent hiện tại — report62: audit raw + T9 geometry recovery

- User yêu cầu kiểm thừa/thiếu phần dịch ngược rồi tự đào. Report62 là audit,
  KHÔNGđóngtoàngame. `docs/conclusions.md` thêmregistryưu tiên,mark17/18/13d/
  16b/21bcũrút/giớihạn:enumspawn0PinMap1Path2Points3Random4Rocket5EndMap6StartWave;
 45,659"quânthậtchốt"KHÔNGđượcdùng;missingparam≠mọitàuHPgiốngnhau.
- Rawprocess-audit/scope-inventory.json.gz:55584UIgztrênđĩa,157576919compressed
  bytes;index797file/117class/150131nodes,54787ngoàiindex,0missing. **KHÔNG**
  kếtluậnngoàiindex=duplicate/rác;khôngxoárawchưaprovenance/semanticcompare.
- Fullanalyze trướcchỉinSHA,cachemissURLlatest cóthểmixbuild: naySHAstrictfail
  trướcextract. Earlywaveexporterloạikhỏifullanalyzetrigger;config-onlyfullrun
  dùngmanualdispatch;raw/il2cppedittriggerverify. Hai recoveryproducer chạy
  unittesttrướcbotcommit vì[skipci]/GITHUB_TOKENkhôngbảođảmtriggerverifyriêng.
- T9GAPTHẬT đãđào:CI40188735212→d97399106;tools/apk-probe/sprite_geometry.py
  giữ6chunksfullSprite/Atlas,Texturemetadata/noimage;counts2185/66/654,0error.
  inputsdataSHA7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7.
- `tools/verify/sprite_geometry.py`→rawsprite-geometry/resolved-geometry.json.gz:
 2185/2185file-scopedPPtrjoins;635m_RDdirect/1550Atlaspointer+exactrenderkey,
 0unresolved. No atlasnameguesses/globalpathID. Rawhasrect/offset/pivot/PPU/
  border/mesh/UV/settings;toolchainUnityPy1.25.4wheelref+MITseparatefromgamefacts.
- Settingsrotation0:2041,1flipH:53,2flipV:54,3rot180:37,4rot90:0;144nonzero.
 40directRDrectboundsfractionaloutby~1.9e−6..0.9963px;giữnguyênkhôngclamp,
  KHÔNGnói40spritehỏng. T9metadatajoinđãcó≠pixelcrop/trim/maskđãvalidated.
-7geometry+3process tests mới,**110tests pass**. Fullpackreleaseintegrity/audio/
  spine/fonts/browsabilitychưaauditlạitrongvòngnày. ChưađedupUI,chưarenderảnh.
- Tiếpưu tiênstage2/3BBwriters/liveparent/history/removal;T9pixelcrop/mask/
  packing40fractionalcaseslàbướcassettiếp. Đừngbóclạidanhmụcđếmcountschođẹp,
  khôngfullAPKexportvìtargetedcollector,khôngchốtgameplaytừunittestPASS.
  Premiumdeferred. Report62vàregistrymớilàentrypointchứkhôngbảngkếtluậncũ.
- Bổ sungauditCI:40189044132/44102/44138fail; signedlogsEOF. Tái lậpcleanarchive
  phát hiệnpeer_spec_reviewtestphụthuộcgitshowpeerSHAkhôngcóởshallowcheckout.
  Đãsửadefaultđọc9inputgốctrongrawsnapshot,khóacanonicalSHA b9325a6cc3a2fb394b3a0ba37eadeef57e0438be1d972aaee30e3e8be709ece0;
  experimentsvẫntínhtừinputtext,khôngdùngprosekếtluận. --from-gitoptional.
  TestcấmsubprocessGitdefault,111testspasscảworkspacevàarchivekhông.git.
- CI saufixđềusuccess:Verify40189296572/geometry40189296654/native40189296604;
  producerregressionpass,tránhfullanalyze. Local+cleanarchive111PASS.

## Agent hiện tại — report63: movement state writers/reuse contracts

- Không rerunAPK vìđủraw; `tools/verify/movement_state_writers.py`→
  rawballoon-animation/movement-state-writers.json.gz:21EnemyMovementmethods,
 9checks+5Subsetterbodies+sourceSHA. Scannerlinearthis-aliasstoreHINTS,
 KHÔNGCFG/whole-nativewriterclosure;testtránhstack4C/callerclobber/wordalias.
- Trongclassđãđọc:typeMove4CwritersSetPathFollower0/SetWaypoints1/
 SetMoveLinearly2/RocketResumeMove2;path50storechỉSetPathFollower.
- EnablechỉzFixed48;Stop/Startchỉmoving;separateSetPosition/Anglekhôngdirect
 resetmode/path/movein;combinedSetPositionAndAngleclear5C/D0. AirFreedùng
 separatenênKHÔNGgộpthànhcombinedlúctáidựngvìthayđổifieldeffects.
- Pháthiệnmới:SetWaypointsnonnulllen<2ghiMode1/distance0TRƯỚClog-return,
 chưaoverwritewaypoints60/index/cache;khôngno-op,oldstatecóthểcònlại.
 Nullinputexceptionkhôngđượcmôhìnhtựsetupthànhcông.
- ExactAirFreerefduynhất3earlywaves:0164/w15/Boss_2/CallData599908→
 resources.assets185704BB. CallDataspawnType0nhưngconcretespawnerAirFree;
 khôngphânloạichỉtheoenum/nodename. KhôngnewclaimBBmustdie/autoescape.
- ModelreusepriorMode2/pathold/moveintrueCHỈconditionalfieldcontract,
 khôngchứngminhactualBBhistory/reachableplaythrough. SetActivecallbackorder,
 externalwriters/parentmatrix/alternatehealth-removalchưakhép.
-8testsmới,**119tests pass**local. Report63entrypointmovementcontracts;
 T9pixelcrop/mask40fractionalrectcònmở;Premiumdeferred.

## Điều chỉnh ưu tiên theo người dùng — đọc kịch bản, không cố chứng minh playthrough

Người dùng nhắc: “xem kịch bản là biết ngay, số địch diệt và player còn sống
chứ không cần cố chứng minh”. Áp dụng từ đây:
- Đọc kịch bản stage/wave và luồng kết quả theo số địch diệt + trạng thái player
  còn sống; dùng denominator/threshold và điều kiện health đã bóc khi mô tả.
- Dừng đào pool history/live parent/writer closure chỉ để chứng minh tồn tại một
  low-kill playthrough hoặc tranh luận BB bắt buộc chết/tự thoát. Không lấy các
  gap chứng minh đó làm blocker cho mô tả hay dựng kịch bản.
- Giữ raw/report59–63 làm tham chiếu; không xoá hoặc đổi chúng thành bằng chứng
  runtime. Chỉ đào lifecycle thêm nếu có mâu thuẫn cụ thể ảnh hưởng kịch bản.
- Các bước tiếp tập trung thiếu dữ liệu triển khai thật (kịch bản, UI, assets),
  không lặp audit mang tính chứng minh vượt nhu cầu. Premium vẫn để sau.

## Report 64 — ưu tiên hiện tại đã kiểm lại: tutorial riêng, victory chung
- Đọc raw APK và giữ snapshot `raw/endgame-missions/shared-stage-victory.json.gz`: 21 method, 19 checks; collector `tools/verify/shared_stage_victory.py`, 4 test mới; tổng 123 tests PASS.
- Stage1 gate stageIndex0/tutorialIndex0; Stage2 1/1; Stage3 stageIndex2/!touchDone (không gate tutorialIndex2). Khác biệt gate/overlay/Continue không được mô hình hóa thành ba victory system riêng.
- Campaign normal/nonbranch: manager callback → shared CheckEndgame (kills/mission + health) → MoveOutPlayer → OpenBoardVictory(bool) → Board_Endgame.Init/SetMissions chung, gồm ba opening stage. `VictoryNow` ép true nhưng cũng về cùng board; không nói mọi entry phải tính kill trước.
- Board SetupTut <=1 và ThroughTut thay đổi UI/index; Continue routing còn guard. Không khẳng định mọi mode/giao diện/reward giống hệt nhau. Kết luận tạm từ static raw, không cần pool-history/playthrough proof.

## Cập nhật review peer + bàn giao AI viết game mới — sau report64
- Fetch tường minh peer cho ra cf27b97553ef25107b45b039f316d9ca7850a885 (fetch origin mặc định trước đó vẫn giữ ref25 cũ). Đã ghi nhận R1–R6 được sửa; không tái báo chúng như lỗi hiện hành.
- Review mới: `docs/HANDOFF_REVIEW_cf27b9755.md`. N1 stale map blocker; N2 ship damage/HP suy từ thiếu field; N3 JPEG metrics/bbox population bị nâng thành luật đẹp; N4 sample/default→whole-game rules; N5 save0/stale tutorial/result handoff. Phân biệt invalid inference với kết luận chắc game có/không có tính năng.
- Cửa vào hiện hành: `docs/START_HERE_NEW_GAME.md`. README, spec local README và các tài liệu lịch sử đã có chỉ dẫn; conclusions bỏ low-kill history làm blocker. Không có game project chạy được ở repo này, chưa tự chốt engine/platform/art.
- Raw giữ15 input peer nguyên văn+SHA và5 input local (native body/map/save/shared-victory/geometry) trong raw/peer-review/*cf27b9755*.json.gz. Collector hermetic `peer_handoff_review.py`,16checks; 4test mới. Tổng127testsPASS; datas/validate PASS. Peer tests chỉ được đọc tĩnh, không báo đã chạy chúng.
- Sửa lệnh nối ZIP phá input trong README và template release của workflow; không chạy full analyze hay publish release. API xác nhận asset release còn draft/có4file; chưa download/extract/integrity toàn pack.
- Tiếp: peer sửa N1–N5; full-pack/crop/browsability; agent implement đọc contract rồi chốt scope/engine với user. Premium deferred, không speculative pool-history detour.


## Report65 — dữ liệu triển khai save mở đầu, không chỉ review spec
- `datas/opening_persistence.json`:8keyfamilies typed/default/cache/read-write effect/method IDs/store + raw hash. Format schema_version1 KHÔNG phải version save APK.
- `raw/persistence/opening-contracts.json.gz`:41method ASM/inventory không capped + metadata/relocation strings/direct calls/dump fields/source hashes,25checks. Collector `tools/verify/opening_persistence.py`,8tests mới; tổng135testsPASS, data validatePASS. Không rerunAPK/Premium.
- Keys: TUTORIAL/TUT_TOUCH_SKILL/StageTarget/ZoneUnlocked/StarStageMaster{stage}_{mode}/StarCount/DroneUsed{slot}/DroneUnlocked{drone}. Backend default0 chỉ scope company!=Test; đây không có nghĩa mọi getter trả0 hoặc thuần đọc.
- StageTarget getter cache hit/miss đều có nhánh zone<MAX_ZONE_INDEX && target<zone*10→tăng1/lưu qua upper-capped setter mỗi lần đọc, không loop/clamp ngay tới zone*10. IndexTutorial đọc StageTarget; target>=2 && tutorial0→ghi6. Không gọi logging/serializer getter như pure read.
- Touch flag stored==1 mới done. Callback b__1 ghi flag1 trước, chỉ tăng index nếu IndexTutorial2 && StageCurrent2; không đổi gate stage3 thành tutorialIndex2.
- DroneUsed âm→ghi0/reread; missing0 không autoequip20001. IsDroneUnlocked20001 tựghi1 nếu0; ID>=20002 stored==1; invalid lowerIDs true trong native không chứng minh roster hợp lệ. Keep fallback Continue riêng.
- Typed Set/Get Int/Float/String→Unity PlayerPrefs; SetValue/GetValue→dictionary static riêng→JSON/Encrypt/ASCII/file persistentDataPath+/Prefs. SaveToDisk/focus/quit custom không có direct Unity Save trong3body đã đọc, không chứng minh flush mọi prefs/toàn game không flush.
- DeleteKey chỉUnity; DeleteAll clearUnity+dict+customSave nhưng thân đó không invalidate progression caches. RefreshDatas chỉcache−1, không resetprofile. Caller/runtime/cloud/migration chưa audit đủ.
- Entry START_HERE, conclusions, datasREADME đã nối report65. Tiếp bóc ship/equip/talent/audio/save còn thiếu theo nhu cầu implement; fullassetpack/crop/browsability vẫn mở. Không speculative BB-history và Premium.


## Report66 — ship save/loadout và tech/talent consumer, hiện hành
- Report `apk-analysis/66-player-loadout-save-rank-trial-tech-consumers.md`; `datas/player_loadout_persistence.json`:15keyfamilies, exact defaults/type/method refs; raw `player-loadout/contracts.json.gz`:33methods/43checks. 10tests mới +3recoverytests; tổng148PASS. Các con số là static checks, không replay.
- Hai lớp Player_Saved_Datas/Player_Device_Saved_Datas được recover riêng từ cached XAPK/native/metadata đã pin hash: CI40192146035success. Raw ASM+JSON/index/metadata array blobs giữ đủ, không commit original binary/full assets.
- PlayerUsed slot0default10001/other10002; missing không write. Stored<=0 reset CẢ PlayerUsed0/1 rồi reread. SetPlayerUsed không tự check unlock/duplicate hay flush loadout cache. CheckDoubleIDShip là routine riêng, khi trùng tìm ship unlocked khác để đổi slot0.
- Base PLAYER_RANK default2/repair<=1 trước trial flag; TRIAL_ID_==1 chọn TRIAL_RANK_/TRIAL_LEVEL_ default0. Không gộp getter với loader floor2. Rank arrays metadata-backed MaxLevel=[10,20,30,60,120,250,500], Cards=[0,20,50,80,250,500,800], StartRanks=[2]*24, MAX_RANK_INDEX6; không suy full payment flow/cap enforcement.
- GP_Setup cached two-slot array -> GP_Loader rank/unlock/skin consumer. Tech wrapper mode4 AND sceneGame trả0; device wrapper trả[-1]*4, không xóa saved. TALENT_SELECTED default−1, startup callback cần StageTarget>=Board_Begin.stageUnlockTalents + mode!=4; numeric threshold còn mở. Stat5 rocket count6..8=>3 giữ nguyên, không sửa monotonic.
- **Task peer** nhánh arena/20330d0e-windwings-space-shooter-game-p: cập nhật spec save/loadout theo report65–66, phân biệt saved/trial/effective/cached, exact1 flags và getter write-on-read. Giữ trial expiry/full upgrade lifecycle là unknown; nếu thêm validation/atomicity hay sửa branch thì ghi new design. Không dùng snapshot spec cũ làm bằng chứng APK.
- Tiếp audio trigger/rules và full pack sprite/audio/spine/font browsing/validation. Premium, speculative BB pool history vẫn không phải task/blocker.


## Report67–68 — audio rules và asset-pack audit, hiện hành
- Audio `datas/audio_rules.json` + raw/audio-rules/contracts.json.gz:65method không capped/25checks/15rules,118enum names/92registry rows/69legacyPPtr pairs. Source recovery40192970188success; overload method refs có RVA, không collapse GetAudioSource/get_Current.
- MUTE_AUDIO missing0 exact1; VolumeSound≈0.73/VolumeMusic≈0.3, mute getters trả0; mute setter body chỉ persist, Pause→AudioListener.pause. Music ignoreListenerPause=true; fade≈.01 mỗi coroutine iteration/yieldnull, không duration cố định. Game playlist33..36, realtime(length−2)/None/realtime2, reroll previous; không tự thêm Bgm_Game5. Endgame.MovePlayer Sfx_Flying26, không mặc định Victory27.
- Draft asset audit40193251582success, raw/asset-pack/{catalog.json.gz,manifest-full.csv}. ReleaseID421174835 vẫn draft; hashes/digests+CRC PASS, nhưng **151 collision paths/321extra manifest rows/320size mismatches**. Sprite archive1903 vs manifest2185;Texture614 vs653. Producer export_assets reset used=set mỗi object. Không gọi full pack đủ.
- Browser docs/assets/pack-browser.html offline metadata-only; cần copy cạnh media đã giải nén. Hiển thị identity ambiguous; fullmedia không trongGit. Fonts actual1TTF ≠ toàn game1font;26skeletonJSON/27atlas presence ≠ binding xong.
- Tổng162testsPASS (8audio/recovery +6packtools/catalog mới), data validatePASS. Numeric float pool là rounded approximation, không bit-pattern proof. Registry/export filename mapping chỉ legacy PPtr/pathID candidate do thiếu serialized-file identity.
- **Task tiếp agent extraction:** narrow identity-safe asset re-export từ cached original: serialized-file+type+pathID filenames, population check/no silent skip, versioned new draft assets không clobber originals, rig/atlas-page joins/crop/listening kiểm riêng. Không full APK pipeline. Chưa hoàn tất task này ở report68.
- **Task peer** nhánh arena/20330d0e-windwings-space-shooter-game-p: đưa rules report67 vào spec với scope/refs; ghi pack completeness FAIL từ report68, không lấy basename collision làm image metric của nhiều object. Không đảo static facts thành runtime approval; Premium/BB-history vẫn hoãn.

## Report69 — peer không phải chờ dump Map/Player blob nữa
- Peer pin `cfc0197f691f4623294b5ec65195923aa738e397` đã có `il2cpp/ia-resolved.json`: Map cctor576 + Player cctor6, hai nhóm exact record/raw equality với extraction branch; fingerprint tại raw/initialize-arrays/peer-comparison.json.
- Deliverable `raw/initialize-arrays/typed-inventory.json.gz`, collector `tools/verify/initialize_array_inventory.py`: raw giữ nguyên, Map int32 view chưa bind container/index; Player sáu field đã bind native stores+dump types. 1int[24]+3float[24]+2float[3], không phải4float[24]. Decode len elements, giữ alignment tail, không đọc ints float bits thành giá trị damage.
- **Task peer:** bỏ blocker “chờ573+6 raw”; đọc report69 rồi bind Map call→container→index qua native cctor/consumer, đối chiếu datas maps/segments đã có. Không tự trừ3 opening literal arrays khỏi576InitializeArray; không quy sốcall thành stagecount. Player index→ship/consumer/formula vẫn cần scope đúng trước DPS/TTK.
- 167tests + datas validation PASS local. Không khẳng định L2/gameplay equivalence đã đóng. Asset identity-safe re-export của report68 vẫn chưa làm; Premium/pool-history không phải blocker.

## Report70 — identity-safe pack v2 đã xuất và audit độc lập
- Recovery40194721870 + independent-audit40194948219 success. Draft release421174835 thêm `assets-v2.zip` (175684102B,ID675035745,SHA4b18cc23b9d71d095dbe8be4458a8ca95fe1d16f5bc0c96bb2329c7bc5de3506) +sha sidecar; không overwrite bốn asset v1, vẫn draft.
- raw/asset-pack-v2/{catalog.json.gz,release-upload.json,archive-audit.json.gz,font-texture-exception.json}; browser docs/assets/pack-browser-v2.html, ZIP cóindex.html offline. Source3039objects six types→3038outputs:2185Sprite/653Texture/69WAV/64Text/1TTF/66SpriteAtlasJSON. SHA/size/CRC/exactpopulation/2838PNG full decode PASS.
- Exception duy nhất resources.assets Texture2D535 Font Texture:0×0,CompleteImageSize0,image data[],stream0/0/empty. Có raw; không invent PNG/không suy runtime font generation. all_target_objects_exported giữfalse; không gọi toàn game đủfont/fidelity.
- 27skeletonJSON/27atlastext/10other theo content;27page names đều nhiều Texture name candidates (26pages×26candidate,1page×2), không identity join. Sprite directtexture null1550 nhưng atlas pointer resolved1550;635directtexture resolved. Không suy null là mất sprite.
- **Task peer:** chuyển tham chiếu pack sangv2/manifest-v2.json theo serialized-file+type+pathID; đừng dùng path_id global hoặc v1basename/preview metrics làm luật. ZIPv2 thường, không nối partv1; giải nén ngoàiGit/mởindex.html. Đây là reference, chưa Spine import-ready vì sourcepage paths chưa rewrite.
- **Task extraction tiếp:** Spine SkeletonDataAsset→AtlasAsset→Material→Texture identity joins rồi assembly/export riêng có provenance; crop/mask/fractional rect, listening và font fallback vẫn mở. Không full re-export lại để cố tạo ảnh cho texture0×0. Premium/BBpool-history vẫn hoãn.
- 180tests + datas validation PASS local; manual re-export workflow để không rerun/clobber evidence. Report70 có acceptance và phần chưa làm; final CI kiểm riêng.

## Report71 — Spine chains và reference folders hiện hành
- Raw `raw/spine-identity/`:167objects/168resolvedlinks;27SkeletonDataAsset/27SpineAtlasAsset/54TextAsset/29Material/27Texture/3shader metadata; selected roots được resolve bằng parsedMonoBehaviour header, không dùng generated tree.m_Script sai. Scan125453headers có1unknown resources.assets580792 thiếuunity default resources; giữclassificationfalse, không đòi đóng nó để làm27rigđãcó.
- `datas/spine_identity.json`, verifier `spine_chain_contracts.py`:27rig/27pages/185animationnames,15uncappednative methods/12checks. Loader0x222f580 tìmfirstmatchingtexturebasename CHỈtrong owningatlas materials; mainTexturefallback_MainTex, shaderskhôngMainTextureflag128. Không cònglobalbasenameambiguity cho27pageđãbind.
- **7atlas1024×1024→texture512×512** giữnguyên; nativeguardgiữparsednonzero dimensions. Không autoresize/fixcoordinates. 26skeletonheader3.8.99/1header3.8.84; scale≈.01all27; defaultMix26×.2/1×.5(Saw580615); transition580611 Attack1→Baydi≈.1. Root580647 additiveMat38/screenMat39 cùngTexture413, rawsettingsđủ; chưashader/PMA/render approval.
- Draft release421174835 thêm `spine-reference-v1.zip` **8057645B**,ID675073587,SHAfabc89bdad02b7a754c3b3ff593b6d21676f52503828200a6da35e0839e3e091.27folderđộc lập;81sourcecopies+27settings+manifest+README=110members. OriginalJSON/atlas/PNGv2giữnguyênbyte. rawreference-pack manifest/audit/release; releasevẫn draft, khôngclobberv1/v2.
- Recovery40196115012success;assembly40196217595success.191tests+datasvalidationPASSlocal, finalCIkiểmriêng. Manualassemblyworkflow sauassetcreationđểkhôngrerunđụngtêncũ. Cácfailure/rebase/headerexceptiontrướcgiữtrongreport71, khôngruntimeproof.
- **Task peer:** đọc report71 và importtypedjoins/settings đúngscope; khôngglobalpathID/namejoins, không tự dùngSpine4.x, không đánhđồngfolderreferencevớiruntime-ready. v2global atlasnamesambiguous đãcólocalidentitysolution, khôngtiếptụcđòidumptexturebasename.
- **Task extraction tiếp:** renderedPMA/blend/crop/fractionalrect audit và animation event/timeScale consumers cụ thể; font fallback/localization, ngheaudio. Khônginventfonttexture0×0/resize7atlas/đàoPremium hoặcBBpool-history.

## Report72 — Sprite pixel reproduction và fractional/pivot contract
- `raw/sprite-pixels/audit.json.gz`, auditor `tools/recovery/sprite_pixel_audit.py`;CI40196744366success,raw7d2436d66. Tải lạiauditedv2, compare2185SpritePNG bằngRGBA bytes với separate rawgeometry/owningTexturePNG crop+packedflip+floatposition/uint16triangle-mask reconstruction.2185match/0error;482texturePNGsused;Pillow12.0.0. KhôngUnityPy SpriteHelper/MeshHandler call trongauditor, nhưng môphỏng format-tool semantics, **khôngUnityGPU/render/PMA approval**.
-593fractional textureRects;40float-outside nhưng31roundedboxes trongbounds/9padding1pixel. Top8IDs2072/2099/2114/2134/2169/4006/4050/4085,right4092,đềuresources.assets/unpacked/rotation0. Khôngauto-clamp:9clampedboxsizekhácv2outputs. Raw/payload/hash/crop/alphabbox/differenceextrema giữđủ, originalpixels chỉrelease.
-517PNG output sizeskhácroundedsource_rect. `datas/sprite_export_contract.json.gz`/verifier `sprite_pixel_contracts.py`:2185typedidentity/sourcepivot/rect/trim+atlasoffset/ppu/exportsize/PNGhash/rawmeshref. Source normalizedpivot KHÔNGnormalizedexportPNGpivot, không center/registrationguess. AllobservedUV0zero→maskpath, rejectunreviewedlayout/nonzeroUV.
- **Task peer:** cập nhật40rectblockerthànhphânbiệt40float-outside/9padding; dùngtypedcontract, khôngsửaAtlas bounds hoặcreuse sourcepivot trêntrimPNG.2185matchchỉđóngconsistencycủaexportsemantics;UnityGPU/placement/PMA/shader vẫnunknown, khônggameplayapproval.
-202testsPASSlocalvencóPillow13 +datasvalidationPASS;pixelCI12success,finalCIkiểmriêng.VerifyCIcàipinnedPillow12đểkhôngskip2syntheticpixeltests. Report72 córawrefs/limits. Tiếpfontfallback/localization/audio hoặcconsumerplacementcụthể, khôngfullassetreexport/Premium/BB-history.


## Report73 — font fallback / localization / peer sync hiện hành
- Peerpin2d0a0e139 đãtypedPlayerstartingarrays/report69corrections; snapshot3docs+blobhashes ởraw/peer-review/update-2d0a0e139.json.gz, khôngAPKtruth/khôngmergewholesale. Khôngchờ573+6dump.
- Recovery40197895269+40198072388SUCCESS, raw61083ec31:125453MBheaders/1knownbuiltinexception,12296selectedobjects/0readerrors/0unresolvedlinks.34uncappednative methods,128bytesboundedSystemLanguage mappingtable.
- `datas/font_language_contract.json.gz`, `raw/font-language/`:7staticSDFfontassets main105→110→106→108→109→111→107,7typedv2atlasPNGs,2352glyphrows/2354characterrows/2285Unicodeunion. Globalfallbacklist[null] khôngnghĩanofallback. Sourcefontnull/mode0all7, khônggiảđịnhtựaddruntimeglyphs hoặc7TTFs;font535emptytexturekhôngphải7atlasesnày.
- 9797serializedtextcomponents:9796fontrefs→105,1nullresources699094;RTLflagfalseall9797khôngchứngminhArabicsuccess/failure.2442languagewrappers,19LanguageAssets×1426rows/1415nonemptykeys. NativeContains→IndexOf→listValue **firstoccurrence**, current→English→key, forceDefaultskipsselected.English`txt_free_after` corrected`Free after`, generatorraw-firstkhôngCSVlast-wins.
- SavedLanguage preference overridesApplication.systemLanguage map; English0defaultLanguagefallback khácinitialselection. NativegenericChinese6/Traditional41 defaultEnglish0, Simplified40→18, Vietnamese39→1; khôngtựgộpChinesevariants. Settercache→onChange→persistordergiữnguyên.
- Offline`docs/assets/font-browser.html`:copycạnhTexture2D/ trongextractedV2đểxemrawSDFatlases/metrics, khôngTMPshaderpreview. Originalmedia/draftreleasekhôngđổi, khôngđưaoriginalfontprograms/PNGvàoGit.212testsPASSlocalvencóPillow13+datasvalidatePASS, finalCIkiểmriêng.
- **Task peer** arena/20330d0e-windwings-space-shooter-game-p:importtypedfontchain/translationfirstIndex/defaultselectionfacts;refreshgap/assetssummariestheo67–73, khôngnângstaticUnicodeinventorydeltasthànhrenderedmissingglyphs. Nếuchọnfont/RTL/shaping/normalizationkhácAPK,ghi newdesign;SDFPNGkhôngphảiCSS@font-faceTTF. Premium/poolhistoryvẫnhoãn;tiếpconcreterender/placement/audiofollowups.

- **Report73 final CI:** Verify40198971054 SUCCESS trên3e7b143ab,212tests/pinnedPillow12; data validatePASS. Broad accidental run40198724717 CANCELLED, publishSKIPPED; partialbot8c9e0217c outputs restored, trace ởraw/font-language/workflow-scope-incident.json.gz. Analyze40198971219 SKIPPED theo scopedguard, draftmedia digests/IDs không đổi.


## Report74 — font reference ZIP tự chứa, delivery đã tải lại kiểm tra
- Peer vẫn2d0a0e139, không commit mới; extraction không merge spec. Gói mới chỉ dùng scopedraw/report73 và auditedV2, không fullAPK export.
- Draft421174835 thêm `font-reference-v1.zip`, asset675170630,1627375bytes,SHA1c20bda1b61d11bb3e4dd06ed07a64672978c66cec33592fb4c25a3b22901848.19members:7typedfolders×(atlas.png+font-reference.json),1separateTTF,programinventory/index/README/manifest. 7PNG+1TTF exact-byte V2copies, full rawfont+primarymaterial projections giữfeatures/kerning, khôngUnityimport-ready.
- Assembly40199471450SUCCESS/raw25ea43c67. CRC/population/allmemberhash/sourcehash checks vàpost-uploadHTTPredownload toànZIP/memberchecksPASS, trongcùngCIjob khôngrendererapproval.7existingassets ID/digest/update-time giữ nguyên,releasevẫndraft. Raw/font-reference giữmanifest/audit/release+deliverytrace; khôngoriginalmedia trongGit.
- `tools/verify/font_reference_contracts.py` kiểmtypedsourcejoins/regenerated7metadatahashes/uploadreadback;6tests mới. Publisher manual-only/existingfilenameguard/no-clobber, không rerunversionđãcó.
- **Task peer:** dùngZIPđộc lập/offlineindex đểtham khảo7SDFassets;khôngphải ghépbrowservớiV2. 1TTF vẫnseparateinventory, khôngsourceFontFilebindinggiả. Có7primarymaterials, khôngtuyênbốmọitextvariant/shader/runtimeplacementđãđóng. Cả7serializedkerning/featurepairtables0entries khôngchứngminhtoàngamekhôngkerning. Fontimport/render/RTL/shaping vàaudio listeningvẫnunknown;Premium/poolhistoryhoãn.

- Report74 local218tests/Pillow13+datasvalidationPASS;assembly40199471450 có216tests/Pillow12, finalVerify sau2delivery/publishingtests mới kiểmriêng.

- **Report74 final:** Verify40199813697 SUCCESS trêncode4fe0cef8e,218tests/pinnedPillow12;datasvalidatePASS. Assembly/delivery40199471450SUCCESS,sourceassetIDs/digests giữ nguyên;khôngmởfile/diff/preview.


## Report75 — serialized Sprite meshes/origin, không PNG-pivot guess
- `datas/sprite_mesh_contract.json.gz`, verifier `sprite_mesh_contracts.py`:2185Sprites/27072vertices/24375triangles, float32positions/uint16indices từpreservedrawgeometry;typedidentity/object+payloadhash/PNGrefs. Raw/sprite-meshes/derivation.json làderivationmetadata, khôngcaptureAPK mới; nguồnrawreport62/72 giữ nguyên.
- 1652non-quadmeshes,497PPUvalues (980SpritesPPU100).467mesh-AABB origin diagnostics khácsourcepivot >1e-5.7strictoutside/6beyond1e-5, 2836chỉ−3.076e−8;khôngclamp/recenter. 2185serializedsubmeshlocalAABBs đều0 nhưngmeasuredvertexbounds không0, giữnguyênhaibảngkhácnhau.
- Trianglecrosssignsnegative24013/positive17/zero345, khôngGPUcullingverdict/khôngrepairwinding/khôngxóatriangles. UV0allzero khôngđủđểfabricateUVs.6tests mới;release/media khôngđổi, khôngfullAPKpipeline/preview.
- **Task peer:** importtypedmesh/PPU khi cầnguồngeometry;sourcepivot/mesh-origin/serializedAABB/trimmedPNGregistrationkhácnhau. Quad/recenter/UVmappingmới lànewdesign/approximation nếuchưacóconsumerproof. ConcreteUV/rendererflip/transform/material/sceneplacementvẫnunknown;Premium/poolhistoryhoãn.

- **Report75 final:** Verify40200221258 SUCCESS trêncode1a6c051b7,224tests/pinnedPillow12;local224tests/Pillow13+datasvalidatePASS. KhôngfullAPK/export/media/releasechanges, khôngreport/diff/previewpresentation.


## Report76 — initial-scene SpriteRenderer/ancestor graph
- Raw/scene-sprites/index+chunks+links từpinnedAPK, recovery40200702387/40200823589SUCCESS;5698objects/0readerrors/0unresolvedselectedlinks.1377rendererroots chỉlevel0..3;61438resources/sharedassets renderers đếmnhưngkhôngmởrộng,khôngruntimepopulation.
- `datas/scene_sprite_contract.json.gz`/verifier:Renderer→GO→Transform→ancestors,218typedSprites matchmeshsourcehash/PNGrefs,7fullmaterialprojections/6shaderidentities. SourceBuildSettings orderMenu/Home/Game/EndGame =>8/4/1036/329roots,activityAND6/3/66/3 khôngvisibility. NullSprite56/disabled26/alpha-zero43;78activityAND có1nullSprite.
- FlipX68/FlipY10;negative-scale ancestorchains14/zero-scale4;RectTransformchains43/maxdepth10. DrawMode numeric0:922/1:441/2:14,giữnguyênsize/flags khôngsuyfinalgeometry. SortingLayerID0all1377 khôngfinaldraworder. MaskNone1074/Inside302/Outside1 từdumpenum,303mask-dependentinstances cầnSpriteMask/camera context,khôngrenderapproval.
-8tests mới,local232tests/Pillow12+datasvalidatePASS;finalCIkiểmriêng. No media/release/fullAPKexport/preview. Workspaceoldcheckoutđãbackup152differingfilesngoàiGit vàrestoređúngremote194f9755f cùngbranch;khôngmấtbảncũ.
- **Task peer:** đọcreport76/importtypedscenechain,numericrendererstate vàscopelimits. SourceSpriteMesh/pivot/PPU khác effective renderer draw-mode/UV/transform;khôngdoubleflip,khôngcoi78làvisiblesprites hoặc61438làmissingassets. ConcreteSpriteMask/camera/SortingGroup/runtimewriter followups cònmở;Premium/poolhistoryhoãn.

- **Report76 final:** Verify40201293124 SUCCESS trêncodee5ed7d070,232tests/pinnedPillow12;local232tests/Pillow12+datasvalidatePASS. Media/releasekhôngđổi,khôngfullAPKpipeline/file/diff/previewpresentation.


## Report77 — scene cameras / SpriteMasks / layer predicates
- Recovery40201827785SUCCESS/raw379866994:122objects,5Camera+12SpriteMask scene roots,0readerrors/0unresolvedselectedlinks.191resourcesmasks+1sharedcamera ngoài rootscope;catalog0serializedSortingGroup khôngruntimeabsenceproof.66sharedobjects vsreport76 rawhashequal.
- `datas/scene_render_context_contract.json.gz`/verifier:5cameras source ortho9.600000381469727/fullviewport/nullTargetTexture. Gamelevel2camera3975mask7959 excludesUI/includesMap;3976mask32 onlyUI,disjointbits. TagManagerlayernames/sortingDefaultID0 giữriêngnamespace.
-12mask cùngtypedSprite sharedassets0:37/sourcehash→mesh75;3serializedactive masks6373/6375/6377,9custom-range-active,cutoff≈.2/rawfloat giữđúng. Same-scene masklist chỉinventory,khôngaffecting-maskbindings.78renderers pass cameraLayer+activityAND chưavisibility (1nullSprite),303mask-dependentstates chưaStencil/renderapproval.
-7tests mới;nooriginalmediaGit/no fullAPKexport/no releasechanges/preview. **Taskpeer:** importtypedcontextkhônggộpcamera/layernamespaces;giữmaskranges,depth/clear/nativewriterunknown. Concreteprojection/mask-stencil/runtimevalidation cònmở;khôngnângboolpredicatethànhvisiblelist hoặc191excludedmasks thànhmissingassets. Premium/poolhistoryhoãn.

- **Report77 final:** Verify40202243648 SUCCESS trêncode0f7ae8853,239tests/pinnedPillow12;local239tests/Pillow12+datasvalidatePASS. Recovery40201827785SUCCESS;nomedia/releasechanges/fullAPKexport/file-diff-previewpresentation.


## Report78 — CameraScaler.Awake native screen-ratio writer
- Recovery40202623509+40202782008SUCCESS/rawf84462770;5capturedscalers/6nonnullcameraRefs,125453headers/1knownbuiltinerror. Cả5scene camera hashes/trees match77;sharedassets0scaler121→camera79 làserializedref chưaspawnproof. Raw/camera-scaler giữcomponents/native/2exactfloatpools/index.
- Awake0x141d70c→Resize0x141d710,Screenheight0x27665e4/width0x27665bc→scvtf/fdiv/fmul/fmaxnm→Camera.set_orthographicSize0x275e1b0. Formula max(height/width*5.4f,9.6f),exactfloats5.400000095367432/9.600000381469727. Khôngfixed9.6mọidisplay. Gamearray[3976UI,3975Game] viếtreverseGame→UI,cùngscalar.
- `datas/camera_scaler_contract.json`/verifier:8nativechecks/typedbindings/binary32arithmeticmodel.1080×2400model12.000000953674316,khôngdevicecapture. Modelpositiveint32domain khôngnativevalidationproof. Nullarray/ref đifailurepath,khôngnullskip. Awake rawmin8byteoverlap đượcclipanalysisnextRVA4bytes,rawgiữ nguyên.
-8tests mới;noactualUnitylifecycle/FPCR/render/other-writerabsenceproof,release/media khôngđổi. **Taskpeer:** thayfixedorthoassumption vớiwriterformula+typedrefs,nếuthêmresizeevent/nullrepair/khácScreen sourceghi newdesign. Khônggộp2Gamecameras vìcùngsize;native movement/otherwriters cònmở,Premium/poolhistoryhoãn.

- Report78 lưuý: float-convert height/width TRƯỚCdivision (SCVTF/FDIV),khôngC#integerdivision. Model chỉsetterargument,khôngUnitypropertyreadback. Local247tests/Pillow12+datasvalidatePASS,finalCIkiểmriêng.

- Report78 final: code812775d7e, Verify40203127918SUCCESS (regenerate/pinneddependency/regressionstepsPASS); PR12comment6398981965. Raw vẫn giữ nguyên; khôngruntime/renderapproval.

## Review peer029559d47 — thiếu thật để giao AI game mới (25/10/2026)

Đã fetch explicit nhánh spec, không merge/sửa nhánh bạn. Snapshot nguyên văn 4 tài liệu:
`raw/peer-review/update-029559d47.json.gz` (peer docs KHÔNG phải APK evidence).

**P0 spec tự sửa trước khi giao AI mới:**
- MISSING bảng13hệ vẫn nói audio chưa bóc,asset thiếu: lỗi thời so với chính phần cập nhật
  report67 và pack69–74. Đồng bộ entrypoint/bảng tổng với raw hiện hành, không chỉ append.
- COMBAT §6.1 còn thiếu bindplayerID trong khi MISSING đã đóng; thống nhất trạng thái.
- MISSING §2.2 lấy report53 `Path/Waypoints.WaitForSeconds(rate)` để đóng **player
  StartMainCannonRate**: KHÁC consumer/field. Spawn delay không chứng minh player shot rate.
  Damage×rate vẫn proxy, chưa phải DPS/TTK runtime tương đương; không giao số này như ground truth.
- Đồng bộ78: ortho snapshot9.6 không fixed; float-convert dimensions trước chia, typed camera refs.
- Các con số luật thị giác từ đoảnh/heuristic phải giữ derived/design scope, không nâng thành APK fact.

**Nhánh dữ liệu nhận:** scoped native recovery `Player_Get_Datas` + `Player_Attack` +
`Player_Attack_1` (SetupDatas/Update/MainCannonAttack/MainCannonShoot/getdamage): lần theo
mainrate→timer→bullet/damage, trước mắt chỉship1, không suy24ships từ1implementation.
Recovery mới `recover-player-firing.yml`; raw sẽ lưu riêng `raw/player-firing/`.
Đây là gap cụ thể ảnh hưởng thiết kế nhịpbắn/TTK, KHÔNG xin fullAPKexport.

**Nhánh spec nhận để giao AI mới:** một bảng tối giản `system → raw/contract → implementation
rule → new-design choices → acceptance test`, ghi rõ reference pack có sẵn nhưng chưa
runtime/import/visualapproval. L1 có thể khởi công, không chờ playback để chọn cơ chế mới.
Save migrate/cloud, plugin/build parity, allboss phase closure và shader/stencil/runtime feel
vẫn scopedunknown; chỉ đào khi task triển khai cần cụ thể. Premium/pool-history tiếp tục hoãn.

### Kết quả đào gap player firing — report79
Recovery40203414134SUCCESS/rawbb896f1da. Player_Attack_1.SetupDatas gọi
GetMainCannonRate(0) rồi ghi timeRateMainCannon@0xa8 (demo override3);
MainCannonShoot0x147a988..990 đặt deadline@0x10c = Time.time + interval@0xa8.
**Không giao damage×StartMainCannonRate như actualDPS/TTK**; ngay cả damage/rate còn thiếu
extra-shot timer/barrels/modifiers/hit gates. Chỉ xác nhận consumer tàu1, không suy24tàu.
Xem79 + raw/player-firing; 3targeted evidence testsPASS, khôngruntimeapproval.

- Report79 finalCI40203611037SUCCESS cho9aa2d7e6f; local250testsPASS. Peer đã nhận PR12comment6399041480, chưa có xác nhận đã sửa bên peer.

## Report80 — ship1 grouped shots / damage callback (tạm thời)
- Native timer Nextra dương tạo N+1 lượt vào emitter từcounter0; lượtcuối resetcounter
  rồi đặt maindeadline. Cảmain/extra deadlines đều gate, khôngcatch-up trongspanđọc.
- MainCannonShoot duyệt mainCannonBarrels rồi tailbranchMainCannonAttack:
  rank3→2 vòng,rank>=4→4; pool/component/setup gates nên khôngđếm nhưsuccessfulhits.
- OnEnable extra-count=GP_Datas.GetNumberAbility(4),demo0; khôngdùng ctordefault1
  thaypost-enable. Level(get_Level) khácrank@0x44.
- Collision callbackbody: critcomparison→virtualdamagegetter→Damager→interfacedispatch;
  chưaresolve emitterdelegate/interface type-pointer nên chưachứngminh mọi bullet dùngcallbacknày.
- Boundedtimer model +7tests; local257tests+datasvalidatePASS. Xem80/rawtimer-derivation.
  **entered emitter≠spawnedbullet≠hit≠actualhealthdelta**; chưaDPS/TTKapproval.

- Report80 final: ability getter thuộc **GP_Datas.GetNumberAbility(4)**, không Player_Ability.
  Declaration regression đãthêm; 8newtests/full258localPASS; Verify40204504124SUCCESS cho5989366d7.
  Gap tiếp: delegate/type-pointer + bullet/receiver TakeDamage; chưaactualDPS/TTK.


## Report81 — Giao nguyên gói combat, không task lẻ (25/10/2026)

Final recovery40205786566SUCCESS/raw99ba44829. `raw/combat-chain` gồm123classes/1563methods,
24attackimplementations+coroutines,bulletfamilies,Obj_Collider,Damager,enemy/player/shield receivers.
4133components/1623collider roots,1419pool links; 498GOT joins quaRELA rows (count xem index/contract),
khôngđọc on-diskzeroGOT là runtime null. 0caps/38unclean/132clipped giữ scope;5sourceexceptions.

**P0 sửa SPEC trước khi giao AI mới:**
1. Hậu tốclass KHÔNG phảiID: Player_Attack_1 sourceID10003/nativeGetMainRate index0;
   Player_Attack_3 sourceID10001/index2. Player_Attack_2 source10002/index1: fulltree4EOF,
   chỉprefix ID/demo bámbytes, validated với101fullsourcecomponents. Bảngđủ24 trong81/contract.
   Đừng lấy save getter `id−10001` làm allcombatidentity binding.
2. Primarybullet80003→Bullet_Plasma,extra88004→Homing_Missile,khôngdefaultbaseLinearly.
3. Chỗhở80 delegate/interface đãnối static: RELA→Dumperusage→constructor→SetBullet→Plasma
   collisiondelegate→Obj_Collider.GetIDamageable lazyrootcache→Enemy_Sub→Enemy_Controller
   →Enemy_Health.CalculateDamage. Còn branchgates,khôngmỗiinvocationđềuhit.
4. Armor>=0:100/(100+a);armor<0:2−100/(100−a); clampHP0,hitcallback chạytrước rereadloss.
   Không áp enemyformula cho Shield_Sub/Player_Health. SnapshotnoDamage740false/241true;
   armorprivate runtime khôngcó trongserializedtree,khôngfabricate0.
5. Không damage×rate/DPS/TTKequivalence. Fullfamilyinventory≠semanticapprovalallships.

**Gói AI nhận:** report81 bảngsystem→contract→rule→newdesign/test + datas/combat_chain_contract.json.gz
(regeneratable verifier),rawnative/symbols/RELA/componentshards,declarative all24mapping,
player_main_cannon_timer +enemy_damage_model. 20newtests/full278localPASS/datasvalidatePASS.
Đọc81§F thayviệc đợitừngreportnhỏ. Khôngchờ Premium/pool-history hayplayback đểkhởicôngL1.
Decoderexit−6 sauoutputởConsole.ReadKey đượcgiữlog,khônggiấu/khônggọidecoderexit0.

- Report81 final: Verify40206236112SUCCESS cho b5f2cc62a; full278localPASS. PR12comment6399402332.
  498GOT joins là candidate-address joins (collectorkhôngfullregisterliveness); criticalpath§D đãđốichiếuriêng.
  Khôngnâng fullnativeinventory thành allshipsemantic/DPS/runtimeapproval; chưapeerack.


## Report82 — Không ghi giới hạn chung thay việc đọc native
72/72 directstatcalls (rate/mainDamage/wingDamage×24) đã CFG must-valueprove argument suffix−1,
khôngcòncandidateMOV. SourceID mapping81 vẫn táchriêng (impl1=10003/index0,impl3=10001/index2).
CommonGetMainRatePercent đãđọc: Tech_Datas.GetTechStatLevel(1) tiers≤0:0,1:.03,2–3:.05,
4–6:.08,7–8:.10,≥9:.12; exactpoolbits+24baserates/arrayfield bindingtrongargumentauditJSON.
Enemyflag0x2f=IsCaAttack. 38unclean=36Reset exceptionbodies+2GizmosREToutside12window,
KHÔNG38truncation. 68roots=64nullpointer+4noMonoBehaviour,khôngreceiverunknownchung.
Xem82§6: từngviệccònchưađọc phải ghi method/consumer/callback cầnnối,khônggọimất dữliệu
haydùngchưaruntime/FPCR/playback đểnéđọcstatic. ProofJSON datas/combat_argument_audit.json.

- Audit82 còn sửa parser operandlessRET nuốt instructionkếtiếp do\s* crossingnewline;
  đãregencontract81: directsites13144→13616,rawkhôngthiếu;72CFGproofs giữnguyên.

- Report82 final: codecd2b317dd, Verify40207070647SUCCESS;290localtestsPASS.
  PeerPR12comment6399518575 nhậnproof/realparserfix vàledger mới, chưapeerack.

- Receipt91: code4b7a01a69, Verify40217833652 SUCCESS/job56s; full648 local PASS39.654s.
  Findings/review PR12comment6400980901; HP/Board tasks answered, chưa tự ACK90/91.

## Report92 — Đã trả lời modern drone binding/loadout/serialized turnRate
- Report `docs/apk-analysis/92-modern-drone-resource-bindings-and-loadout.md`, contract
  `datas/drone_loadout_flow.json`; raw/drone-prefabs + raw/drone-loadout giữ đủ pointer/bytes/native.
- Đủ12 ResourceManager→rootGO→MonoScript/id bindings20001..20012; thêm24 bản UI tách riêng.
  Drone3 resource serialized turnRate=1.0, không ctor8; OnEnable không ghi đè turnRate.
- GP_Setup getter **new int[2] mỗi lần**, mode4 trả0/0, còn lại saved DroneUsed0/1.
  StartDrones gọi getter từng slot, prefix Prefabs/Drones/Drone_, localScale f32.8/ .8/1,
  positions±20,−20,0, SetActive true. Không nhét dedup vào loader: routine riêng sửa slot0.
- 35new/full683tests PASS42.905s, datas validate PASS;5ranges319instructions29anchors4symboljoins.
- ACK90/91 đã nhận6401051274. Review peer de2d1366: còn event2/player-route wording,
  AutoGain guardCurrent>0/level0zero, map footer stale; feedback receipt raw/peer-review/review92-*.
- Spec nhập ba đáp án drone trên; reverse tiếp23wing implementations/named map-save consumers.
  Không coi batch này đóng hai nhóm đó; không đợi ACK để làm tiếp.
- Receipt92: code8bb7bd717, Verify40219912118 SUCCESS/job1m4s; đã gửi report92 qua PR12,
  raw/drone-loadout/handoff92-receipt.json giữ ID/response. Không tự coi peer đã ACK92.

## Report93 — ACK92 reviewed; remaining wings configuration batch
- Peer c80b1c50, ACK92=6401411518: 3/3 wording fixes independently verified, snapshots/raw retained.
- `docs/apk-analysis/93-spec-review-and-wing-configurations.md`, `datas/wing_implementations.json`:
  all24 roots/nested 876 method bodies/66845 instructions byte→ASM checked;14 ctor numeric-array joins.
  17 SetBarrels functions/1314 instructions, including16 beyond impl1, normal/index/super config laws.
  78new/full761 tests PASS49.228s; native Unicorn2.1.4 fixture, FPCR0 explicit, not live Unity/FPS/DPS.
- Spec nhập floors14/16/19/21; direct-clamp level13/21; super20 still updates angle; keep S/V instance
  inputs separate from ctor defaults. 10002 raw-prefix ID proof remains valid despite curve parse error.
- NOT all23wing firing closure: next named Shoot/packet/coroutine consumers for17 configs and
  special paths2/4/6/8/10/12/15 (report93§6), plus named map/save consumers unchanged.
- 85 virtual-entry sites,83 receiver-must-owner; two15 GunCheckEnemies stack-spill sites explicit
  unproven automatically, not missing native bytes. Do not replace this with global UNKNOWN rhetoric.
- Receipt93: code8d5d2eba7, Verify40222156868 SUCCESS/job1m9s. Handoff93/green-receipt
  đã gửi PR12, raw/wing-implementations giữ response IDs. Chưa tự nhận ACK93.

## Report94 — Wing13/22/23/24 emission chains, not whole23 closure
- `docs/apk-analysis/94-wing-emission-coroutines-and-packet-geometry.md`, `datas/wing_emission_flow.json`:
  39 bodies/3208 instructions byte→ASM;53new/full814 local PASS67.850s; datas validate PASS.
-13 StartCoroutine before deadline;22/23/24 after deadline.13 two pool attempts/yield, frozen
  width/rate-per-number capped.05. Present IBullet branch exercised to SetBullet/SetActive,
  x±width*i, angles±4*i, lifetime2 (NOT damage), through=super&&throughShield.
-23/24 one child packet/yield incl trailing wait; live shotRate/live childCount after packet,
  mutation to count0 passes+inf to Wait ctor, not silent clamp.
-Basic22/23/24: even N + spacingX0 can emit N+1 calls; N0 can center; only id−1 earlyfilter.
  Circle22/23 uses full worldXYZ; no duplicate endpoint; doesn't apply Basic id−1 filter.
-Closure ABI22 differs23/24; callbacks decoded separately. Basic/Circle terminal helper entry
  remains explicit observation boundary; no successful pool/hit/DPS claim.13 quaternion adapter
  returns controlled identity, records native Euler inputs, not Unity quaternion implementation.
-Sound pool.04super/.08normal, PlayOneShot clip5 volume1/.6, not camera shake; pinned8byte recovery.
-ACK93 received6401658709/raw retained; peer spec not yet independently re-reviewed. Queue Arena/PvP
  after remaining named wing consumers + map/save, per6401593117. Don't wait ACK94 to continue.
- Receipt94: code589e1f588, Verify40223289936 SUCCESS/job1m4s; handoff/green response JSON
  giữraw/wing-emission. Chưa tự nhận ACK94. Không show diff/file/preview cho user.

## Report95 — Bỏ cả5 leaf interceptions94; nối pooled/formation dispatch
- `docs/apk-analysis/95-wing-pooled-leaves-and-formation-dispatch.md`, `datas/wing_pooled_leaves.json`:
  5 bodies/837instructions + exact2instruction trampoline2990890→14a600c (recovery40223486658).
  40new/full854 local PASS69.819s; validate PASS. Không sửa fixture/hash report94.
- Actual leaves22Basic/Circle,23Basic/Circle,24Basic chạy tới Pool/IBullet SDK boundaries.
  Lifetimes22=5,23Circle=10,23/24Basic=4; Circle speed captured arg, Basic live field.
  All5 throughShield đọc trực tiếp field, không local super guard như13.
- All5 activate trước GetComponent. Thiếu IBullet22/Circle23 return sau activation;
  Basic23/24 recycle; thiếu/Unity-null formation cũng recycle. Poolnull throws.
- Basic rotation cộng pointEuler; Circle không; SetBullet angle reread pooledEuler.
  Quaternion identity/pooledEuler77 là controlled inputs, không Unity numeric truth.
- Basic23/24 callbacks formation first + caller second. CreateBullets sau SetBullet nhận
  caller collision gốc, lifetime4. Null external callback vẫn giữ formation callback.
- Boundary tiếp: bên trong Formation.CreateBullets123d98c/Scale/IELerpTo + concrete IBullet,
  các Shoot còn lại của93/special consumers. Không tự coi done23, physics/hit/DPS hoặc ACK95.
- Receipt95: code772839187 Verify40223865259 SUCCESS/job59s; raw/wing-emission giữ recovery,
  handoff và green response. Chưa tự coi ACK94/95.

## Asset binding queue — peer comment6401749563 (chưa independent verify counts)
- Full comment lưuraw/peer-review/asset-binding-audit-6401749563.json. Không gọi asset semantic
  binding “đầy đủ” chỉ vì đã export/index đủ. Numeric sprite name không tự là glyph font.
- Peer báo lỗi art-worklist.py `is_digit` bucket ships/bosses thành glyph; file này không có
  trong current reverse tracked tree khi kiểm95. Cần exact peer source path/commit trước sửa,
  không tự chế tool/khẳng định đã sửa. Sprite identities vẫn theo direct raw/ship/boss joins.
- 5 việc được ghi nhận: UI node→sprite→screen joins; gameplay prefab sprite refs;
  unknown/passthrough labels; unmatched atlas names; actual27 spine rig identities.
  Các số đếm trong comment là peer audit, chưa nâng thành kết quả đo độc lập ở branch này.

## Report96 — USER REPRIORITIZATION: L3 lên trước, không hoãn sau wing/map-save
- User26/10: “L3 đang thiếu trầm trọng… bộ mặt thật của game”. Thay queue trước:
  L3 appearance/UI/gameplay/VFX/motion/audio chains là trục chính; wing/map-save chỉ tiếp
  khi là named dependency của chain nhìn thấy. Arena/PvP vẫn không chen trước việc này.
- Peer spec b000f905 reviewed L3 wording;6 source docs snapshot raw/peer-review/l3-b000f905.
  DONE/START_HERE đã hạ “đủ”; README historical “L3 bỏ” và conditional readiness dễ gây hiểu sai.
- Đã làm UI drawing-use index datas/ui_l3_bindings.json.gz:797files/117class labels,
  76,806 sprite observations,75,749 exact scoped PPtr resolutions,1057null,1099 distinct sprites.
  Inventory55,584 KHÔNG coverage:54,787 ngoài index chưa join. Existing scoped work43/46
  không bị phủ nhận;96 mở rộng indexed coverage thành artifact tra trực tiếp.
-12 tests mới PASS; validate PASS. Chưa pass render/composition/motion/audio; local activeSelf
  không là effective visibility. Không tự nhận visual semantics cho unknown/passthrough/spine.
- Tiếp: ngoài-index scoped references + hierarchy/state/sorting/font/material; gameplay
  prefab→sprite/VFX/rig→clip/event; scene-level reference outputs. Không vẽ từ screenshot,
  không yêu cầu playtest người thật/screenshot mới làm điều kiện bắt đầu phần raw đã có.
- Receipt96: code8789ef433 Verify40224533473 SUCCESS/job1m10s; raw/l3-ui giữ CI/handoff.
  Không tự ACK peer hay tự gọi UI binding regression là L3 composition/render approval.

## Report97 — L3 full saved-layout audit + composition metadata
- Tất cả55.584 saved UI layouts đã scan/hash:54.787 outside index có3.843.228 sprite-name
  observations,0 scoped sprite PPtrs;1.003.504 TMP components khôngfontPPtr.117class labels
  trùng current index; KHÔNG54.787 màn mới.30.827 topology groups;14.081 outsidefiles match
  indexed topology candidates, nhưng KHÔNG chuyển bindings/semantic identity; giữraw tất cả.
- `datas/ui_layout_inventory.json.gz` +4shards; `datas/ui_composition.json.gz` +6shards.
  Composition797sources:100.312visual components;99.731 root-frame matrices/581unknown;
  serialized activity false89754/true10409/unknown149, không runtime visibility.
-76802 material-array scoped joins;18467font +18467sharedMaterial joins, mỗi loại thêm1null.
  Parent reconstruction unique path/depth NOT typed PPtr edges.160ambiguous nodes giữunknown.
  Đã sửa slash-in-name TMP SubMesh path handling, không match-first.
- Renderer m_Enabled không có trong exporter whitelist -> UNKNOWN, không defaulttrue;
  RectTransform anchored/driven layout chưa chạy; matrix float64 không Unity world/render approval.
-37new tests +12tests96 lifecycle cleanup; full suite/CI receipt follows. Việc tiếp:
  scoped GO/Transform/parent/component+enabled recovery; camera/Canvas/dynamic state;
  gameplay prefab→sprite/material/rig/VFX→clip/event/audio. L3 vẫn ưu tiên trước wing backlog.
- Receipt97: final codec915ac075 Verify40226781914 SUCCESS/job1m51s/full suite.
  Full903local PASS73.060s;49UI-focusedPASS14.659s, then22composition rerun after arithmetic pin.
  Matrix summation explicit left-to-right forPython3.11/3.12 consistency; source chunks giữ nguyên.
  Regeneration compare per-record để không format huge diffs; không nới tolerance/fields.
  Old40226331214 superseded, statusraw giữ riêng, cancellation403; KHÔNG giả định green/cancelled.
  ACK96=6402053761 nhận/raw retained, chưa independent verify new peer spec; chưa tự ACK97.

## Report98 — L3 whole-chain recipe, không drip-feed inventory
- Raw source native-classID collector06ab4ef2b / recovery40228467063 SUCCESS / botcb1919d77.
  128724 objects,345090resolved/166639null/52Unity-default-mesh unresolved,0readfail,5header-only.
  Binary MB header authority sửa18074 false script links; generated disagreements vẫn giữ.
- datas/l3_scene_chains.json.gz +shards:805root views,37766logical/25536visual node observations,
  3504typed assets,1587animators,665clips. Root owns nodes/callbacks/sounds/animators/asset closure;
  nonvisual Button_Sound/UnityEvent owners không mất. Raw locators/materialize được từng component.
-665/665 numeric stream+dense+constant decoded/channel exact;301603keys; discrete sprite mappings
  nối scoped identities, không blend pointers.51990unique/393unresolved/17ambiguous binding instances,
  dùng native classID và same-Animator subtree; giữ candidate/nonmatch thay chọn đầu tiên.
-2139callbacks,2037scalar AllClipName fields,92SoundClip registry names. ButtonDown/Up exact native
  method+field; native firing13/22/23/24 clip5 bridge hash-pin report94. CameraScaler native writers
  exact-join5scene cameras;1Canvas, không nhầm CanvasScaler hay gắn mọi camera vào mọi prefab.
- tools/verify/l3_recipe.py: root10Pause235nodes/5clips/26sound fields; root402effect90045;
  root769homeplayer10013. --include-raw nối full raw objects + external media SHA/path; no originalmedia.
-18new tests, full921localPASS124.500s. CI receipt follows, no render approval/selfACK.
- Peer arena/20330d0e-windwings-space-shooter-game-p: review độc lập report98 + recipes, ưu tiên
  MonoBehaviour header authority, target/class/path ambiguity, sprite discrete keys, camera ownership
  và sound/callback condition. Không merge peer/selfACK; PvP vẫn sau L3.
- Tiếp bằng recipe→composition/playback dựng thật/verify source, không quay lại vòng đếm inventory.
  Runtime Animator selection/blending, driven layout, particle simulation/shader execution chưa chạy.
  52default meshes/5header-only/393static target misses giữ rõ, không blanket “thiếu animation”.
- Receipt98: code1f2d12f6e / Verify40229636747 SUCCESS/job2m56s/Python3.12;
  raw/l3-chain-verification giữ receipts +3recipe example summaries. Peer handoff6402605773
  trên PR12; chưa independent ACK, không render approval.

## Report99 — L3 chưa hoàn tất; tiếp compiled Animator programs + target property probes
- Không nhận batch98/tests xanh là complete L3. datas/l3_animator_programs.json.gz nối232
  controllers/232machines/667states/377params/666motion leaves/343AnyState+125state transitions.
  1587Animator direct controller links; recipe bây giờ có programs/links/diagnostics, không chỉclipset.
- Explicit state/clip-time probe nối channels tới binding targets. Popup_QuitMissions GO57508,
  Animator495980→controller1974 Popup_Network reused→defaultAppear→clip1572. Scale0→~1.0304→1,
  alpha0→~.83137256→.83137256 ở0/.25/.5; không tween dựng tay, không gọi engine readback.
-1853start/mid/end clip-time probes trên665clips;0unknown ở các điểm probe.1461initial constant
  sentinel values được xử lý đúng coefficients0/0/0/d; không bịa thiếu key/animation.
- Audit393misses:376no-path;13GO không có MonoBehaviour,4khôngBoxCollider2D. Làm rõ98:
  không phải13MBscript inheritance mismatches.17ambiguous vẫn giữ, không global-match.
-19newtests; full suite/remote receipt follows. Chưa script-driven selection/transition scheduler/
  layer blends/Rect layout/particles/shader/composition-render; đây là missing thật, không selfACK.
- Peer branch arena/20330d0e-windwings-space-shooter-game-p: review report99 state/clip indexing,
  destination mã hoá, source initial keys và direct Animator ownership. Không nhận L3complete.
- Receipt99: full940localPASS131.369s; code5c3ba250d / Verify40230913183SUCCESS2m30s.
  raw/l3-playback-verification giữ local/probe/CI/handoff6402815443; chưa independent ACK.

## Report100 — UI script→activation/trigger→state/clip→event→deactivation
- Native collector cddde2fa7 / recover40231440486SUCCESS / bot161bee87d:1074methods
  from13core UI/root families+nested, pinned executable intervals/RELA/native consts.
  First40231346501 failed namespace: UIObjectAnchors isTuPro, corrected from dump, not omitted.
- datas/l3_ui_drivers.json.gz:214serialized instances,1751potential appearance-call instances,
  1414exact receiver joins/337unknown,230Animator routes,687exact direct-callee links,409callback
  entries. Recipe includes native_ui/global indices/artifactSHA, not just unordered state clips.
- Popup_QuitMissions GO57508/Script644901/Animator495980: SetPopup→SetActive(true),
  defaultAppear/controller1974/clip1572; OnExit→RELA/literalHide→SetTrigger→Hideclip1573;
  eventOffBoard@.33333334→nativeOffBoard→sameGO.SetActive(false). No fake Play(Appear),
  no claiming engine delivery/reset. Confirm guard exitAfterConfirm+0x38 retained symbolically.
- Namespace-qualified inheritance review46event gaps:9base-declared candidates/37remain.
  Popup_QuitEvent594188→Popup_Notices.OffBoard; private base is candidate, not engine lookup proof.
- CFG joins differing values toUnknown; unsupported writes kill; ABI clobbers regs+flags;
  indirect delegates/runtime args unknown, predicates not executed. Source life chain, not runtime trace.
-17newtests; full957localPASS145.887s. Remote receipt follows; no render acceptance/selfACK.
- Peer arena/20330d0e-windwings-space-shooter-game-p: review100 CFG soundness, literal/RELA
  identity, script offset→PPtr receiver, exactcalleeRVA/overloads, callback ancestry and lifecycle.
  Remaining engine blending/layout/particle/shader/composition execution still explicit; L3notcomplete.
- Receipt100: finalad986c7b9 / Verify40232850860SUCCESS3m14s; getter audit thêm140joins,
  final1414resolved/337unknown. x1 ABI không là decoded Vector3/float. Raw receipts
  l3-ui-driver-verification; peer6403162684/PR12, chưa independent ACK hay render acceptance.

## Batch101 — native camera/safe-area layout → recipe (2026-10-26)
- Report `docs/apk-analysis/101-L3-native-camera-safearea-layout.md`; raw native/objects manifest
  `raw/l3-layout-native`, generated585 typed contracts `datas/l3_layout.json.gz`.
-125453 headers scanned;584anchors+1scaler;1unclassified built-in-resource header explicitly retained.
 2526boundedobjects/9161resolvededges/660null; six camera/scaler-writer joins; no automatic main pick.
- Native20anchor/fixed combinations+4scaler modes,4Start camera/flag combinations; model state/cache,
  world-vs-local-z special cases, actual-instance CLI probes and sprite/material references joined.
- Local984PASS160.186s; final27layout tests rechecked after finite-clamp boundary validation.
- Peer arena/20330d0e-windwings-space-shooter-game-p: audit root jump table/literal provenance,
  native Start camera fallback vs direct call, safeArea cache/main-camera distinction, parent bridge
  shared-oracle caveat, source-qualified identities and non-runtime camera selection. No selfACK.
- Next coherent L3 chain: geometry/material/font + particle/shader/composition scene construction,
  then engine transition/blending. Do not mark Unity rendering accepted from model/native-stub tests.

- Receipt101: finalcodeb18e783a7 / Verify40236171639SUCCESS. Raw ci101/handoff101;
  peer PR12 comment https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6403663070; chưa independent ACK.

## Batch102 — layout-owner visual construction + Alert closure (2026-10-26)
- `docs/apk-analysis/102-L3-layout-owner-visual-construction.md`; raw l3-visual-surface,
  artifact l3_visual_surface +249 hashed chunks. Recovery40236919629SUCCESS.
-56714objects/16061GO;11380renderers/153materials/17parsed+decompiled-analysis shaders;
  1391decoded geometry;7fonts/7atlases/2354charentries/1737text instances;954particle modules.
- Fixed101 Alert gap: Animator4647→controller78→none44/alert42/fade43→renderer5105.m_Color.a;
  precise source file identities, trigger/transition descriptors, clip-local coefficients.
-1057animators/91controllers/348decoded clips;79907bindings=74916unique/4983unresolved/8ambiguous.
- Recipe scoped surface/coverage; include-raw selected surface bodies; null font/main camera not auto-picked.
- 0readfailures,1header-only Player_Attack_2:704560,7unresolved builtin particle mesh references.
- Full1012localPASS178.853s,28new tests. Final remote receipt follows.
- Peer arena/20330d0e-windwings-space-shooter-game-p: audit mesh decoder coordinate/UV source,
  live-atlas/slicing caveat, shader raw pass states vs decompiler non-executable analysis, glyph atlas
  bounds/static fallback scope, Alpha binding CRC source, incomplete targets and recipe coverage.
- Not render/VFX/engine blending acceptance. Next camera/composition/culling and actual renderer
  geometry generation; no screenshot gate, no invented default meshes, no selfACK.

- Receipt102: finalcoded1a65f01d / Verify40238106907SUCCESS4m7s; raw ci102/handoff102.
  Peer request https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6403986603; chưa independent ACK/render acceptance.

## Batch103 — world pose/camera geometry/composition chain (2026-10-26)
- Report103-L3-camera-world-geometry-composition; artifact datas/l3_composition.json.gz;
  raw l3-composition-verification. Merge101/102 with1760 body SHA overlaps verified,57480objects.
-11380known serialized world poses;558scene-renderers/10822unplacedtemplates. No unresolved parent→identity.
-6camera snapshots;1104same-scene mask pairs=558pass/546fail; depth groups preserve source clear/target fields.
- Alert: native scaler size10.80000019×24.0000019→zero-border sliced position rectangle→actual source
  world z1→Game/Main depth11/21. Mask7959excludeslayer5;mask32includes. Main almost full1080×2400
  synthetic footprint. Explicit alert clip alpha retained separately, no fake visibility/frame verdict.
-31newtests;full1043localPASS202.733s. Final remote receipt follows.
- Peer arena/20330d0e-windwings-space-shooter-game-p: review merged SHA/edge authority, root-included
  matrices, scene/template separation + placement override, triangle/6plane clipping and float64 scope,
  source zero-border generator assumptions, mask/alpha/footprint distinction, no implicit camera stack.
- Not Unity numerical/render acceptance. Continue actual geometry generation/driver application and
  shader/particle/text/spine execution; source gaps101/102 retained; no screenshot gate/selfACK.

- Receipt103: finalcodedddd75aed / Verify40240026886SUCCESS; raw ci103/handoff103.
  Peer request https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6404277110; chưa independent ACK/render acceptance.

## Batch104 — peer update/feedback + shared modeled write application (2026-10-26)
- Peer head23bf66c7, DATA_SYNC24.34–36/DESIGN_READINESS frozen in raw/peer-review/l3-23bf66c7;
  reported ACK101–103 confirmed, only contract/identity/mask checks, not full numerical/engine acceptance.
- New l3_frame applies native Start/Anchor/Scaler and explicit clip typed writes on SAME instance state;
  current hierarchy/geometry/projection read overlays. Raw immutable; Frame worlds isolated.
- Alert size19.2→24 + sample alpha.392156884→f32 stored.392156899→fade0, footprint unchanged by fade.
- Border_Info7048 playOnStart=false: Start bind only; direct Anchor moves Y7→8.440000534,
  all320descendants propagate; child renderer5452 projection moves144.00004196px. Root border≠0 not_generated.
- Private/static cache semantics retained; atomic clip writes tool-only; mounts remain movable roots.
- Pointer attr0/custom23/type212 NOT field CRC. Strict default reject; explicit m_Sprite policy with
  source type checks log as policy, not engine mapping proof. No unknown mapping→null or fabricated fileID.
-30newtests/full1073localPASS223.162s; artifact datas/l3_frame_cases.json.gz; receipt l3-frame-verification.
- Peer requested numerical reproduction/counterexamples, not count-only ACK: false Start, propagation,
  private/cache persistence, f32 stores, failed plan no partial commit, custom pointer policy.
- Recipe frame_application auto_execute=false. No Unity scheduler/blend/render acceptance. Continue
  concrete binding/order + textured geometry/shader pipeline; existing source gaps remain.

- Receipt104: finalcode81fed2233 / Verify40242708365SUCCESS; full1073PASS223.162s.
  Last-writer camera/ref coherence fixed. Peer feedback https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6404603132;
  receipt https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6404657056;104chưa independent execution ACK/render acceptance.

## Batch105 — ef6b75ef: NEW Pause native order + actual atlas/UV + Sprites/Default model
- Miền batch: AI-1 binding/driver/texture-shader only. provenance: arena/ef6b75ef.
- Report105-ef6b75ef-L3-Pause-native-order-textured-shader; datas/l3_ef6b75ef105.json.gz.
- New native full Board_Pause.Align (not repeating standalone markers101): top597593→bottom616420
  →2colliders→content Transform274606→parentView267691→actual descendant renderer549984.
  40hook calls/5setters; Startfalse bind-only; chosen idle1495@.25 alpha.5797794461250305.
  Native internal call order proved; Start/clip invocation order explicit, not Unity scheduler.
  clip-before/after Align snapshots equal because disjoint fields; Refresh align guard preserved.
- Genuine APK Texture785 2048×1024 decoded, PNG originals external only; sprite2585 crop SHA matches
  assetpack. Simple4vertices/2triangles get exact render-key affine UV; NOT AI-2 live atlas remap.
  7actualtexels→barycentric UV→source GLES premul/tint/external-alpha/over model, NOT raster/readback.
- 8byte-located GLSL runs from2platform segments; generic13parser entries diagnostic only, format
  unsupported (do NOT count as13 variants). PixelSnap recovered, not executed; no GPU precision claim.
- Custom23 remains UNPROVED: actual set_sprite native icall bridge is not registration proof.
  Frame104 strict reject/explicit per-binding policy unchanged; no unknown→null.
- 32newPASS33.925s/full1105PASS274.466s. Recovery40287660478SUCCESS; final code/CI receipt follows.
- UPDATED peer status: spec7bdd5003 DATA_SYNC24.29–40; ACK104 now5/5 artifact arithmetic reproduction,
  still no independent native/Unity execution. New ownership6410868087/sticky6410945198 read;
  claim6411008329 confirms existing user-assigned work (started before sticky, not retroactive claim).
- Shared3 paths unchanged/absent on this branch. No cross-digger tool edits/merges or main push.
- Review: f32collider math, tailcall trace, current-pose propagation, clip/Align commutation,
  source-key UV vs zero UV placeholder, actual texture orientation, premultiplied alpha/blend.
- Batch bounded scope covered; NOT all AI-1/L3 complete. Custom registry/cross-component scheduling
  unresolved. Do not move into AI-2 geometry/gaps or AI-3 sim/transition/driven ownership.

- Update khi chốt105: specb1985740/DATA_SYNC24.41/sticky49 đã ACK105-a5a74747
  (source modeld446d47d5/head25ac3b46b, particle/transition/driven; CI ID còn pending theo spec).
  Không còn trạng thái “chưa thấy digger khác” như lần kiểm đầu batch. Chưa independent audit
  các artifacts đó ở nhánh ef6b75ef; không import/merge/sửa tool của họ. Claim mới6411110604
  của a5a74747 là reachability/driven-coverage, giữ ngoài batch driver/texture105 này.

- Receipt105 final: code2da541e395c64494b62eeffe47d27f924ebc4fd7 / Verify40290558746SUCCESS4m31s;
  full1105localPASS274.466s,32newPASS33.925s. Barycentric accumulation dùng sequential_sum
  để portable3.11/3.12; initial40289718130FAIL không tính là PASS. Native/texel dữ liệu giữ nguyên.
  provenance: arena/ef6b75ef. No independent execution ACK/render acceptance claimed.

- PR12 handoff105: https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6411373032; nhờ independent review, không selfACK.

## Batch106 — ef6b75ef: GLES vertex/PixelSnap + actual mip0 bilinear
- Claim6411403047 trước khi bắt đầu; miền #3 AI-1 shader/texture, không live atlas remap/
  geometry generators/particle/transition/driven. provenance: arena/ef6b75ef.
- Report106-ef6b75ef-L3-GLES-PixelSnap-bilinear; datas/l3_ef6b75ef106.json.gz.
- 4source vertices×2explicit variants; full staged Flip/ObjectToWorld/MatrixVP, PixelSnap
  round-even sau divideW/restoreW, UV/color passthrough; perspective-correct varying CPU ref.
- 7source105 seeds→same7fixed viewport pixel centers×2variants=14inside queries. 5/7pairs đổi
  filteredRGBA, không readback/GPU/visibility claim. 5sampler-only probes +46genuine RGBA8
  texels từ pinned APK (raw-object/fullRGBA SHA khớp105), clamp full texture không crop clamp.
- Vertex0 window724.4999881982814,404.517600574684→724,405; samepixel726.5,325.5 alpha
  .05091579864714838→.08276148982721251 khi explicit PixelSnaptrue. Saved material Snap0
  không bị tự đổi thành observed runtime variant. Source mip_count1/color_space_metadata1
  chỉ metadata, không sRGB/LOD precision proof. Bilinear raw-UNORM CPU/filter-before-premul.
- Recovery40291977206SUCCESS/raw l3-shader106; 32newPASS0.131s; full1137PASS270.151s; CI receipt follows.
- UPDATED specbab67115 DATA_SYNC24.43–44: ACK105-ef6b75ef6411447910 là artifact/count/identity,
  vẫn chưa independent native execution/tag23 mapping. 107-a5a74747 được spec ACKartifact-level,
  CI xanh theo6411493961, không second APK decoder. Claim #15 native Animator blending6411524443
  của họ ngoài miền shader106. Không import/merge/edit tools/artifacts của họ.
- Own branch không có APKD1/AI1 needle files (docs/spec/START_HERE.md,tools/verify-claims.py);
  không bịa needle của spec. Shared3paths untouched. Custom23 UNPROVED/default reject giữ nguyên.
- Review: exact same-pixel UV shift, clipZW/UV unchanged by snap, round-even ties ±,
  4tap arithmetic/full-texture clamp neighbor, filter→premul order, no GPU/readback promotion.

- Chốt106 cập nhật PR12 6411617634: L2 ĐÃ mở#18–23, geometry eeb95d5a reportedtip90c4e4ff9
  đã trở lại. #16 được ACKartifact-level và#17 independent raw transition decoder mở theo
  6411543326. Shader106 không lấn các miền này; future batch phải claim từ sticky mới.

- Receipt106 final: codeb979cfe657bffe96a2bc89fda184da29e97d7815 / Verify40292776800SUCCESS4m48s;
  full1137localPASS270.151s/32newPASS0.131s. Handoff PR12 6411725150; raw
  l3-ef6b75ef106-verification. Peer spec chốtb1e00350; shader batch covered at bounded scope,
  custom23/GPU/scheduler vẫn mở; no selfACK/readback/render acceptance.

Official118HANDOFF **6417057892** posted with scientific79602dd6f / report9f2f42770 / exact-head GREEN and1571localPASS. Independent review pending; no selfACK/full#27closure.

Official119HANDOFF **6417225245**; scientificb9e6765fa/reportfb1e1ba45/exact-headCI40330340745/1581localPASS. Independent review pending, no selfACK/full#27closure.

Official120HANDOFF **6417679550**; scientific10b46c13d/report81c9677eb/exact-headCI40332906465/1601localPASS. Independent review pending, no selfACK/full#27closure.

Official121HANDOFF **6418718832**; scientificf58d0ebbb/reporta454e1202/exact-headCI40339667616/1628localPASS. Static-only native lane per6418032974/6418326986. Independent review pending, no selfACK/full#27closure.

Official122HANDOFF **6419944060**; scientificd15858faa/report93978a0e5/exact-headCI40347869822/1658localPASS. Static-only native lane per6418032974/6418326986. Independent review pending, no selfACK/full#27closure.

Official123HANDOFF **6422951255**; scientific1d6fbcbb/report8ac0c7ab6/exact-headCI40366819899/1694localPASS. Static-only native lane; callback literal `Stop` resolved, invocation unproven. Independent review pending, no selfACK/full#27closure.

Official124HANDOFF **6423892211**; scientific98e5ba966/reportea6a3835f/exact-headCI40374283338/1727localPASS. R1 correction **6423891421** and R2 CLAIM **6423892767** posted; independent122review and R1 full review still pending, no selfACK/full#27closure.

Official R2 `review:` HANDOFF **6424830494**; scientific e2f4b0e45/report97b83af0d/exact-headCI40381758335/1751localPASS. R1 final6424767705 APPROVE bounded123 synchronized. Independent R2 verdict supported with3 wording notes and bounded gaps; no selfACK/full#27closure.

Official126HANDOFF **6425502933**; scientific01448eec4/report8bec5129a/exact-headCI40386829829/1772localPASS. Static-only native dispatch on prepared N2 owner; no full graph-builder/runtime/readback/render, no selfACK/full#27closure.

Official127HANDOFF **6426133738**; scientific6781d828f/reportf1d35dd7a/exact-headCI40391943675/1789localPASS. Static-only null-clip whole-FDE + missing-X map; no build path/runtime/readback/render, no selfACK/full#27closure.
