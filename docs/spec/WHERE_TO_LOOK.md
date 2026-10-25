# WHERE_TO_LOOK — 3 blocker, **3 nguyên nhân khác nhau**; và một phép thử tôi suýt tự lừa

> **Câu hỏi của chủ dự án:** *"vấn đề có nhỏ quá không? hay phải phân tích ngược chỗ khác mới ra?"*
>
> **Trả lời ngắn:** Ba việc còn mở **không cùng một loại bệnh**. Tôi từng gộp cả ba vào một câu
> *"chuỗi RVA bị đứt"* — **sai với hai việc trong ba**.
>
> Bản đọc: `68ce86a7`. Mọi số dưới đây đo trên file **đã có trong repo** — không chạy APK, không dump thêm.

---

## 0. Ba blocker — ba nguyên nhân, đo được

| Blocker | Dữ liệu nằm ở đâu | Bằng chứng | Loại việc |
|---|---|---|---|
| **A2 / T1** map→wave | **hằng `int` literal** trong `.cctor` của `Map_Get_Datas` | `.cctor` = **100.896 B · 3.444 hằng int** vs chỉ **40 `debug_rva`** (1,1 %) | **parser** — không cần APK |
| **B1 / T5** bảng stat device | **FieldRVA** (`InitializeArray`) | `.cctor` của `Device_Get_Data` = **1.636 B**: **43 int** vs **39 `debug_rva`** (47 %) | **relocation** — đúng chỗ `1.192/1.194` slot đọc ra `\x7fELF` |
| **B3** HP enemy runtime | **đã có** (`datas/enemy_hp_by_id.json`, 150 cặp) | `Enemy_Health` chỉ có **1 field `noDamage`**; `Enemy_Data_Balance` **8 method, 0 trả HP** — nhưng `Enemy_Get_Datas.cctor` có 150 insert | **đọc bảng**, không export |

**Tỉ lệ `debug_rva` / tổng hằng trong `.cctor` là phép thử phân loại:**

| Class | `int` | `debug_rva` | % RVA | Loại |
|---|---:|---:|---:|---|
| `Map_Get_Datas` | 3.444 | **40** | **1,1 %** | 1 — dữ liệu viết thẳng |
| `Device_Get_Data` | 43 | **39** | **47,6 %** | 2 — dữ liệu sau FieldRVA |

⇒ **Không phải "vấn đề nhỏ".** Mà là: **một việc tôi gán sai nguyên nhân**, và việc đó **rẻ hơn** tôi nói.

---

## 1. Chỗ tôi chẩn đoán sai

Tôi đã nói với chủ dự án: *"`T1`/`T5` vẫn MISSING vì 1.192/1.194 slot giải ra `\x7fELF`"*.

Con số đó **đúng**, nhưng nó **chỉ thuộc về T5**. `Map_Get_Datas` có đúng **40** `debug_rva`, không
phải 1.192. `T1` **không** đi qua relocation.

> **Đo lại trên pack 17 class @`68ce86a7` (kéo dữ liệu 23/10):** **1.929** slot `debug_rva`,
> **2** slot resolve (**0,1 %**) — cả 2 thuộc `Player_Health.TakeDamage`. Tức bản vá `.rela.dyn`
> **chưa** mở được `InitializeArray` cho 1.927 slot còn lại, gồm **`Player_Get_Datas.cctor` 0/40**
> (nơi giữ 3 mảng `pct`) và **`Device_Get_Data` 0/71** (bảng stat device).

### Phép thử tôi suýt tự lừa

Tôi trích 117 cặp `(A, B)` từ `.cctor` bằng một khuôn 8 lệnh lặp lại, rồi kiểm *"B có phải tên wave
không"*. Kết quả **117/117 hợp lệ** — nghe rất mạnh. Rồi tôi kiểm **phép thử đó có thể thất bại
không**:

```
wave id <= 212  có trong waves.json:   213 / 213
```

**`Wave_0000` … `Wave_0212` đều tồn tại.** Vậy với mọi `B ≤ 212`, câu *"B là wave hợp lệ"* **luôn
đúng bất kể B nghĩa là gì** — kiểu gì cũng pass. **Phép thử không có lực phân biệt.**

Chỉ còn **giá trị ≥ 1000** là có nghĩa:

| Phép đo | Số |
|---|---:|
| Lần xuất hiện giá trị ≥ 1000 trong 117 cặp | **45** |
| Giá trị phân biệt ≥ 1000 | **17** (`7001…7017`, `9010`) |
| Trong đó là **tên wave** | **45 / 45** |

⇒ Kết luận **trung thực**: **vị trí** dữ liệu là chắc (literal, không RVA);
**nội dung bảng thì CHƯA chứng minh**. 117 cặp mới chỉ có **45 điểm dữ liệu có lực phân biệt**.

> **Bài học (ghi vào quy tắc):** trước khi tin một phép kiểm, phải hỏi *"phép kiểm này có thể cho ra
> kết quả khác không?"*. Nếu miền giá trị hợp lệ phủ gần hết miền thực tế thì phép kiểm **rỗng**.

---

## 2. Cấu trúc `.cctor` — cái bóc được và cái chưa

`.cctor` tạo **716 record**, chia theo số field (`mov w1,#N` trước `bl #0x110d09c`):

| `w1` | Số record | Dạng | Bóc được |
|---:|---:|---|---|
| **2** | **118** | cặp `(A,B)`, 2 field @`0x20`/`0x24` | **117** |
| 1 | 21 | một số đơn | 21 |
| **3** | **320** | có thêm `bl #0x205b07c` (ctor thật) | **0** |
| 7 | 104 | — | 0 |
| 4·5·6·8·9 | 21·12·9·4·5 | — | 0 |
| không xác định | 102 | `bl` không liền sau `mov w1` | 0 |

Khuôn dạng 2 (bóc được), lặp y nguyên **118 lần**:

```asm
ldr   x0, [x22]            ; class token
mov   w1, #2
bl    #0x110d09c           ; tạo object
mov   w9, #A
str   w9, [x1, #0x20]      ; field 0x20 = A
mov   w8, #B
str   w8, [x1, #0x24]      ; field 0x24 = B
```

**12 cặp đầu, theo đúng thứ tự trong code:**

```
(25, 9010) (113, 5) (2, 161) (92, 96) (6, 15) (11, 13)
(26, 1)  (5, 15)  (13, 19) (21, 7001) (94, 17) (23, 24)
```

`(21, 7001)` đáng chú ý: `7001` = `Wave_7001` = **wave boss đầu tiên** (`Boss-37001`).

### 2.1 Phép kiểm **thứ tự** — và nó **THẤT BẠI**

Nếu 117 cặp này thật là "map → wave" thì các wave boss phải xuất hiện **theo thứ tự** trong code.

| Nguồn | Thứ tự |
|---|---|
| `waves.json` (wave boss, theo file) | `7001, 7002, 7003, 7004, 7005, 7006, 7007, 7008, 7009, 7010, 7011, 7012, 7013, 7014, 7015, 7016, 7017, 7018, 7019, 7020, 7021, 7022, 9001…9024` (**45**) |
| `.cctor` (17 cặp có `B ≥ 1000`, theo thứ tự code) | `9010, 7001, 7003, 7002, 7004, 7005, 7006, 7005, 7006, 7010, 7009, 7011, 7013, 7010, 7017, 7016, 7015` |

Ba chỗ **lệch**:

1. **Không theo thứ tự** — `7003` đứng trước `7002`.
2. **Có lặp** — `7005` ×2, `7006` ×2, `7010` ×2 (nếu là "map → wave" thì một wave có thể thuộc nhiều
   map, nhưng cặp `A` cũng khác nhau: `(75,7005)` và `(71,7005)`).
3. **Phủ 17/45** wave boss, và **bỏ hẳn** dải `9001–9009`, `9011–9024`.

⇒ **Giả thuyết "117 cặp = map→wave" KHÔNG được dữ liệu ủng hộ.**

> **Nhận định (mức C) sửa lại:** danh sách này nhiều khả năng là **`listMapBranchDatas`** —
> các **nhánh** trỏ tới wave đặc biệt (trong đó có boss). Lớp `Map_Get_Datas` có **12 static field**,
> trong đó đã biết tên `listMapDatas` · `listMapBranchDatas` · `listIdBosses`.
> Nếu đúng, **bảng map→wave thật nằm ở dạng `w1=3` (320 record)** — nhóm lớn nhất và **chưa đọc**.
> **Điều kiện lật ngược:** nếu dạng `w1=3` cũng không cho block A lặp, thì map→wave **không** nằm
> trong `.cctor` và phải tìm ở `Stage_Get_Datas` (đã có 2.937 lệnh).

---

## 3. `B3` — dữ liệu **thật sự** không có

Ba lớp bằng chứng, không lớp nào là "không thấy trong file X":

| Bằng chứng | Số |
|---|---|
| `Enemy_Health` — MonoBehaviour, **981 instance** | **1 field duy nhất: `noDamage`**; không `StartHealth`, `hp`, `maxHp` |
| `Enemy_Data_Balance` | **8 method**: `GetBonusCoin` · `GetBonusExp` · `GetSurvivalScore` · `GetArenaScore` · `GetPVPPlayScore` · `GetArenaPlayScore` · `ctor` · `cctor` — **0 trả HP** |
| `Enemy_Datas.StartHealthPoint` | **467/981** > 0; enemy thường `CB-*` / `CD-*` = **0** |

> **Đính chính 25/10:** câu "KHÔNG có asm" bên dưới là bản ghi ngày 23/10. Hiện
> `reverse-engineering/raw/il2cpp-consts/` có 3 file asm · **41** method
> (`Enemy_Get_Datas` 4 · `Enemy_Controller` 33 · `Enemy_Health` 4 — claim **WRH3**).

Bản ghi 23/10: **`Enemy_Ingame`, `Enemy_Health`, `Enemy_Controller` KHÔNG có asm** — 17 class đã
export chỉ có **một** class `Enemy_*` là `Enemy_Data_Balance`. Khi ấy đây là blocker **duy nhất**
thật sự cần "chỗ khác": **export thêm class** mới đọc được đường gán HP. Export đã chạy xong.

> ### ✅ ĐÃ GIẢI NGAY SAU ĐÓ (23/10) — xem `ENEMY_HP_RUNTIME.md`
> Không cần đoán nữa: `dump.cs` có **`Enemy_Get_Datas`** với
> **`private static Dictionary<int, float> AllStartHealthPointEnemies`** và
> `GetStartHealthPoint(int)` (`RVA 0x157F6A8`), `.cctor` ở **`0x157F7CC`**. Cộng thêm
> `Enemy_Controller.GetStartHealth/TakeDamage/UpdateHpBar` và `Enemy_Health.armor @0x34`.
> **Bổ sung 23/10:** `armor` là `private` **không** `[SerializeField]` ⇒ **0/981** prefab có giá trị
> (đối chứng `noDamage` **981/981**). Xem `UNITY_RULES` §1.1.
>
> Và **khả năng (1) đã bị bác bằng dữ liệu**: **108/109** prefab được spawn có `Enemy_Hp_Bar`
> đang bật (**99,8 %** quân) ⇒ enemy **không** chết 1 phát. Câu *"HP bar chỉ trên boss"* ở bản trước
> của mục này là **sai** — tôi chưa kiểm nó.
>
> **Đính chính 25/10 — việc còn lại ĐÃ XONG:** `Enemy_Get_Datas` (4 method) đã có asm; `.cctor`
> parse ra **150 cặp `id → HP`** trong `datas/enemy_hp_by_id.json` (**không** phải 981 — 981 là số
> dòng serialize). `Enemy_Controller` + `Enemy_Health` cũng đã có. Cái còn mở là **bind**
> `StartHpPoint ← dict` và hệ số `kHp[mode]`. Xem `ENEMY_HP_RUNTIME.md` §5.

---

## 4. Trả lời trực tiếp: có phải "phân tích ngược chỗ khác"?

| Blocker | Cần chỗ khác? | Cần gì | Chi phí |
|---|---|---|---|
| **T1** | ❌ **Không** | parse `.cctor` đã có (25.224 lệnh) | ~60–120 dòng, **ngay trong repo này** |
| **T5** | ⚠ **Không phải chỗ khác** — vẫn `libil2cpp.so`, khác **khâu**: đọc `.rela.dyn` thay vì `.data` | 1 dòng sửa + chạy lại | **1 dòng** |
| **B3** | ❌ **Không còn cần chỗ khác** | 3 class đã có asm; bảng 150 cặp đã parse | 0 lần dump |

⇒ **Không blocker nào cần "mở một mảng phân tích mới".** T1 là **parser**, T5 là **1 dòng**,
B3 là **1 class** — và B3 là cái duy nhất thật sự nằm ngoài dữ liệu đang có.

---

## 5. Vì sao lần trước tôi nói "T1/T5 đều bị chặn" — và cách tránh lặp lại

| Bước | Đã làm | Lẽ ra phải làm |
|---|---|---|
| Đo `debug_rva` | đo **toàn bộ 17 class** → 1.194 | đo **từng class** — `Map_Get_Datas` chỉ có **40** |
| Kết luận | "cả T1 và T5 bị chặn bởi relocation" | "**T5** bị chặn; **T1** chưa kiểm" |
| Phép kiểm | chứng minh **dương tính** (B là wave) | thêm **phép thử rỗng** (B có thể KHÔNG là wave không?) |

**Quy tắc bổ sung vào `ASM_INTEGRITY`:** mọi phép kiểm phải kèm **một ca có thể thất bại**. Nếu
không nêu được ca đó, phép kiểm là **trang trí**.

---

## 6. Bốn việc làm được **ngay**, không cần ai

| # | Việc | Ở đâu | Chặn |
|---:|---|---|---|
| 1 | Bóc dạng `w1=3` (320) + `w1=7` (104) | repo này | T1 |
| 2 | Tìm **ca có thể thất bại** cho bảng: một giá trị `B` **không** phải wave → nếu không tìm được, đổi phép kiểm | repo này | T1 |
| 3 | ~~Đối chiếu thứ tự~~ ✅ **đã làm — THẤT BẠI** (§2.1). Bảng 117 cặp **không** phải map→wave | repo này | T1 |
| 4 | Kiểm 39 slot RVA của `Device_Get_Data` có trùng slot với lần đọc ra `\x7fELF` không | repo này | T5 |

**Việc 3 đã chạy và cho kết quả âm** — đúng như thiết kế: phép kiểm này **có thể** thất bại, và nó
đã thất bại. Nhờ vậy tôi **không** ghi bảng 117 cặp vào SPEC như một kết luận.

---

## 7. Còn thiếu / phải đoán

- **117/716 record = 16 %** đã bóc. **Không** nói bảng đã xong. Và trong 16 % đó, chỉ **45/117**
  điểm dữ liệu có lực phân biệt (giá trị ≥1000). Phần còn lại **không chứng minh được gì**.
- **Giả thuyết "bảng 117 cặp = map→wave" đã bị phép kiểm thứ tự bác** (§2.1). Cách đọc thay thế
  (`listMapBranchDatas`) là **mức C**, chưa kiểm.
- **Chưa đọc dạng `w1=3` (320 record)** — đây là nơi khả năng cao chứa bảng thật. Nếu ở đó cũng không
  có, thì map→wave **không nằm trong** `Map_Get_Datas.cctor`, và phải sang `Stage_Get_Datas`.
- **T5 39 slot** suy từ `.cctor` 1.636 B của `Device_Get_Data`; nếu bảng được nạp trong class khác
  (`GameDatas` 73 method?) thì 39 chỉ là một phần — **chưa kiểm**.
- **Phép thử ở §0 chỉ đúng với 2 mẫu.** Chưa đủ gọi là quy luật cho 17 class; chỉ đủ để **phân biệt
  hai cái đang chặn**.
- **B3 đã đổi hai lần** — 23/10: "chưa biết" → "biết cơ chế, thiếu bảng số"; **25/10: có bảng số**
  (`datas/enemy_hp_by_id.json`, 150 cặp `id → HP`). Việc **duy nhất** còn lại: **bind** bảng vào
  `StartHpPoint` + đọc hệ số `kHp[mode]` — không phải dump (`ENEMY_HP_RUNTIME.md` §5).
