# ANCHOR M5 — baseline cho "multi-wave loader" (đo lại từ dữ liệu, trước khi coder viết code)

**Vai:** build-spec/verifier (`ef6b75ef`) · **Trạng thái:** PROVISIONAL · **Chưa kiểm code M5 nào**
(coder chưa bàn giao). Mục đích: chốt **định nghĩa** các con số chấp-nhận *trước* khi viết loader, theo
**Nguyên tắc số 0** của director lần 157 (*nguyên mẫu là thước*).

Nguồn duy nhất: `datas/waves.json` sha256 `dde007618b7cbc83f0702298f7744609f8b25b2d7479ab15964b1fb6fa8abc73`
(2.796.955 B) và `datas/maps.json`. Receipt máy đọc: `anchor_waves.json` (`61cd8a51…`) sinh bằng
`anchor_waves.py` (`f6d26e6b…`) — cả hai trong `reverse-engineering/raw/verify-ef6b75ef-m5/`.

## 1. Board nói gì — và dữ liệu đếm được gì

| Board (lần 157, M5 anchor) | Đo được | Khớp | Định nghĩa đúng |
|---|---:|---|---|
| **282 wave** | **282** | ✅ | số phần tử `waves[]` |
| "**23.757** spawner" | **11.089** | ❌ | 11.089 = **số row spawner** (= `datas/waves.json:count_spawners`). **23.757 = Σ `copies`** |
| "**22.451** entry" | **45.659** | ❌ | 22.451 = **Σ len(enemies)** (bỏ hệ số copies). **45.659 = Σ (copies × len)** = số *lượt spawn* theo cách M2 đã dùng cho Wave_0000 (883) |
| **250 map** | **250** | ✅ | `datas/maps.json:maps[]` |
| **299 stage** | 299 | ✅ (nguồn khác) | không có trong `waves.json`; 299 = `Stage_Behaviour.csv` — spec BALANCE: Normal 199 + Boss 26 + Combat 49 + MiniBoss 25 |

**Kết luận:** 3/5 anchor đúng nguyên văn; 2 số còn lại **đúng giá trị nhưng sai nhãn**. Nếu coder/verifier
dùng nguyên câu "nạp đủ 23.757 spawner / 22.451 entry" thì **không ai đạt được** — ngay cả dữ liệu gốc cũng
không có 23.757 spawner.

## 2. Bộ đếm chuẩn (dùng cho M5)

| Tên | Công thức | Tổng toàn bộ 282 wave |
|---|---|---:|
| `waves` | `len(waves)` | **282** |
| `spawner_rows` | `Σ len(wave.spawners)` | **11.089** |
| `sum_len_enemies` | `Σ Σ len(spawner.enemies)` | **22.451** |
| `sum_copies` | `Σ Σ copies` | **23.757** |
| `spawn_events` | `Σ Σ (copies × len(enemies))` | **45.659** |
| `distinct_enemy_prefabs` | `len(set(enemies))` | **109** |
| `distinct_spawner_names` | `len(set(spawner.spawner))` | **1.015** |
| wave rỗng | `count(spawners == [])` | **0** |

Kiểm chéo Wave_0000: 42 row · Σlen 237 · Σcopies 150 · **883** spawn event — khớp đúng con số M2 mà
`VERIFY_M1_M4_BA257B36.md` đã xác nhận ⇒ định nghĩa `spawn_events` là định nghĩa **đang chạy trong code**,
nên chấp-nhận M5 phải dùng nó.

## 3. Điều kiện chấp-nhận M5 — bản đo được (đề nghị thay câu trong board)

1. Loader nạp **282/282** wave, **0** wave bị bỏ, **0** wave rỗng giả tạo.
2. Với **từng** wave: `spawner_rows`, `sum_len_enemies`, `sum_copies`, `spawn_events` khớp **từng wave** với
   `anchor_waves.json:per_wave` (282 dòng đã phát hành) — lệch 1 đơn vị là fail.
3. Wave rỗng: `waves_without_spawners = 0` ⇒ không wave nào được phép "xong ngay".
4. 5 wave lấy mẫu replay: thứ tự spawn phải bằng đúng thứ tự `copies → enemies[]` của dữ liệu.
   Đề nghị mẫu: `Wave_0000` (42 row) · `Wave_0163` (**nhiều row nhất: 257**) · `Wave_0114`
   (**ít nhất: 3**) · `Wave_9024` (tên không theo chuỗi số) · 1 wave boss cuối chương (coder chọn + ghi lý do).
5. Đếm bằng script, không bằng mắt: dùng `anchor_waves.py` sinh lại receipt rồi `diff` với bản đã pin.

## 4. Cái bảng này **không** nói

- Không nói map → wave binding: spec `COVERAGE_AUDIT.md` §7 ghi chỉ **7/250** map chắc chắn ⇒ phần "stage/map
  flow" của M5 vẫn phải ghi `UNKNOWN`/`INFERRED`, không được bịa thứ tự.
- Không nói rate/thời lượng trận: "2,5–4 phút" là `INFERRED` từ rate × spawner, chưa có runtime.
- Không thay verdict M5: verdict chỉ được viết khi coder bàn giao code + CI theo headSha.

## 5. Tái lập

```bash
cd reverse-engineering/raw/verify-ef6b75ef-m5
python3 anchor_waves.py --canonical ../../.. --out /tmp/anchor.json
diff <(python3 -c "import json;print(json.dumps(json.load(open('/tmp/anchor.json')),sort_keys=True))") \
     <(python3 -c "import json;print(json.dumps(json.load(open('anchor_waves.json')),sort_keys=True))") && echo IDENTICAL
```

Kỳ vọng: `IDENTICAL` (không lệch một byte sau khi chuẩn hoá JSON).
