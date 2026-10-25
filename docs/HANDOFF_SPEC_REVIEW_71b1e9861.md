# HANDOFF — 6 điểm review trên snapshot `25c367aca`

> **Phạm vi:** mình chỉ **đọc + sửa tài liệu trên nhánh `arena/20330d0e-…`**. Không merge, không push vào
> nhánh `ef6b75ef`, không sửa file raw nào của bạn. Mọi số dưới đây đo trên **snapshot đã pin** trong
> `docs/DATA_PIN.md`; con số ở nhánh bạn có thể đã đổi — khi đó **số của bạn thắng**, mình chỉ xin bạn đọc
> phần *cách đo*.

## 1. Sáu điểm, và đã sửa thành cái gì

| # | Điểm review | Sửa ở đâu | Cách kiểm (máy) |
|---|---|---|---|
| **R1** | Bảng `mode → mảng hệ số` ghi sai offset: `0xb78` không phải mảng #0 | `MISSIONS_STARS.md` §chú thích `0x14e5640`: mode `0`→`0xb78` **fallback** (0,50/0,80/1,00), `1`→`0xb80`, **mọi giá trị khác** → `0xb78`; nhánh `GameMode==4` là **ngoại lệ** đọc float `+0x78` | Claim **E12** (31 phần tử) đọc thẳng `Missions.asm.txt`; phần offset ghi **asm line** trong doc |
| **R2** | "Không dedup theo tên" bị nói như luật, trong khi dữ liệu chỉ có **1 mẫu** | `ENCOUNTERS.md` §5: nói rõ mẫu = **14 file wave đã export**, kết quả **0 pathID trùng**, và **không** suy ra "mọi wave khác cũng vậy" | **AQ3** — đếm `Call_Data` vs pathID trên 3 wave normal: **149 / 149 / 0 trùng** |
| **R3** | `67` page `sactx` bị dùng như `67` page **có rect** | `ASSET_TRIAGE.md` §2 tách: **67** page `sactx` theo **tên** · **56** trong số đó được gắn `category=atlas` · **11** page bị xếp nhầm nhóm | **Q1** (67 page · 31,05 MB · 60,0 M px²) + **AT1** (340 `unresolved` · 282 biết trang · 18 gán được) |
| **R4** | Luật phân loại asset bị "che" bởi nhãn cũ, và **643 nhãn cũ bị tính là mức A** | `ASSET_TRIAGE.md` §9.8: 643 nhãn **passthrough** nay có `confidence` **rỗng**, `label_source=category_passthrough`, `reviewed=false`; 5 luật mới ghi rõ **đất dùng = 0** vì vòng trước đã phủ | **AB4** (1.049 có nhãn · 643 passthrough **không mức** · 505 `unknown`) |
| **R5** | D3 (juice/feel) bị đóng sớm khi bằng chứng chỉ là **0 site trên 139 asm** | `DESIGN_READINESS.md`: 0 site = **chưa thấy trong mẫu**, **không** phải "tính năng không tồn tại"; D3 để **🟡 mở**, điều kiện lật ngược ghi rõ | Claim đếm site (`timeScale`, `WaitForSeconds`, `lvVibr`…) đọc 139 file asm — **CONST/sample**, không thành luật |
| **R6** | Lỗi **đo** bị biến thành **SKIP** ⇒ pipeline xanh trong khi dữ liệu hỏng | `tools/verify-claims.py`: `--no-skip` (rc=1 nếu có SKIP) và `--require AB,AT1,AQ7`; doc ghi rõ **PASS ≠ chứng minh hành vi** | `python3 tools/verify-claims.py --no-skip --require AB,AT1,AQ7` |

## 2. Một lỗi **của chính bản sửa trước** — nếu bạn đã copy thì sửa lại

Mình từng viết **"11.089 spawner"**. Sai đơn vị. Đo lại và chốt:

| đại lượng | số | đọc từ đâu |
|---|---:|---|
| **spawner object** (= `Σ copies`, = `len(Call_Data)`) | **23.757** | `datas/class-inventory.csv` · `datas/waves.json` |
| dòng cấu hình trong `waves.json` (dedup theo tên spawner) | **11.089** | `count_spawners` |
| quân thật (`Σ len(enemies) × copies`) | **45.659** | `waves.json` |
| `Σ len(enemies)` (không nhân copies) | **22.451** | `waves.json` |

Claim **AQ7** khoá `(23757, 23757, 11089)`; **WR7** khoá `(22451, 45659, 11089, 2, 63, 603)`.
Nếu tài liệu của bạn đang ghi "11.089 spawner" thì đó là **số dòng**, không phải số spawner.

## 3. Những gì mình **vẫn chưa** chứng minh (đừng đọc là đã xong)

- `rate = 0` **chưa** chứng minh là "cả wave cùng một frame" — chỉ biết **2.366 dòng (21 %)** có `rate=0`.
- `copies` là **cách export gộp**, không phải "số đợt spawn" (mức **B**) — báo cáo 54 bên bạn cũng viết vậy.
- **340** sprite `unresolved` vẫn chưa có nhãn; **4.250** mảnh sheet-split là **cận trên**, không phải số asset.
- **116** tên atlas không match **không** đồng nghĩa chưa tách được ảnh (nhiều ảnh đã có PNG riêng).
- Geometry: **join metadata** (`PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION`), **chưa** crop thử
  pixel; 6 chunk nguồn chưa kéo nên chưa tự kiểm `sha256`.
- Chưa đối chiếu được `02-ui-layout.csv` với canvas runtime — mọi tỉ lệ UI là **của một thiết bị**.

## 4. Kiểm trong 60 giây

```bash
python3 tools/verify-claims.py                                  # 0 FAIL (2 SKIP có chủ đích: B9, F4)
python3 tools/verify-claims.py --no-skip --require AB,AT1,AQ7   # rc=1 LÀ ĐÚNG — hai SKIP đó cố ý
python3 -m unittest discover -s tests -q                        # 30 test OK
python3 tools/refresh-readme-sizes.py --check                   # bảng tài liệu README khớp file
```

Nếu bạn chỉ muốn xem **số nào tái đo được**: `docs/spec/RAW_AUDIT.md` (sinh bằng `tools/raw-audit.py`)
phân loại 192 claim → **151 RAW · 4 DOC · 37 CONST**.
