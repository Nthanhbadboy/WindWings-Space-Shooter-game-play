# ENEMY_HP_RUNTIME — bạn đúng, tôi sai; và "treo máy" thì không phải vì HP

> **Bạn nói:** *"enemy thường không chết 1 phát nhưng theo tôi nghĩ rất nhiều enemy mà tính dame
> thông qua HP thì chắc treo máy."*
>
> **Tôi kiểm cả hai vế. Kết quả: vế 1 bạn đúng, vế 2 không đúng — và lý do rất cụ thể.**

---

## 0. Trả lời ngắn

| Vế | Kết quả | Bằng chứng |
|---|---|---|
| **Enemy thường KHÔNG chết 1 phát** | ✅ **BẠN ĐÚNG — tôi sai** | **109/109** prefab được spawn có HP bar (hai cơ chế, xem §1 của `DIFFICULTY_MODES.md`); **909** instance, **909/909 `m_Enabled = 1`**; con enemy bị spawn nhiều nhất `CB-30003` (**4.793** quân) có `CB-30003/Enemy_UI/HP_Bar` |
| **Tính damage qua HP sẽ treo máy** | ❌ **Không** | **12 quân/giây**, **~50–950 con cùng lúc**, **~40–100 phép tính damage/giây**. Điện thoại làm **10⁹** phép/giây. Cách nhau **7 bậc** |
| **Vậy phải tìm ở đâu?** | **2 class chưa dump** | `Enemy_Get_Datas` (`Dictionary<int,float> AllStartHealthPointEnemies`) + `Enemy_Controller` (`GetStartHealth`/`TakeDamage`/`UpdateHpBar`) |

**Câu quan trọng nhất:** HP enemy **có thật**, nhưng **không** nằm trong dữ liệu serialize —
nó nằm trong **một `Dictionary` dựng ở `.cctor`** của một class **chưa ai dump**.

---

## 1. Tôi sai ở đâu — và nó sai từ gốc

Trong `OPEN_ISSUES` B3 và `BALANCE` §2 tôi viết *"HP bar chỉ có trên boss"* làm **bằng chứng** cho
giả thuyết "enemy chết 1 phát". **Câu đó sai, và tôi chưa bao giờ kiểm nó.**

Kiểm bây giờ (`raw/typetrees/Enemy_Hp_Bar.jsonl.gz`):

| Phép đo | Số |
|---|---:|
| Instance `Enemy_Hp_Bar` | **909** |
| `m_Enabled = 1` | **909 / 909** |
| Root prefab **khác nhau** có HP bar | **256** |
| `Boss-*` có bar | **39 / 39** |
| **`CB-*` có bar** | **36 / 69** |
| **`CD-*` có bar** | **16 / 32** |
| W2- · XB- · GD · BB · H- | 25 · 6 · 4 · 4 · 2 |

Và quan trọng nhất — **trong 109 prefab thực sự được spawn**:

| Phép đo | Số |
|---|---:|
| Prefab được spawn **có** HP bar | **109 / 109 = 100 %** |
| Quân thuộc prefab **có** HP bar | **45.659 / 45.659 = 100 %** |
| Quân thuộc prefab **không** có bar | **0** |

> **Đính chính (23/10, sau khi kiểm lại):** bản đầu ghi **108/109** và để `W1-30031` (104 quân) làm
> ngoại lệ. **Sai.** Con đó có bar qua **đường thứ hai** — `Enemy_Display.hpProgressBarRenderer`
> (PathID `509616`), loại component mà `Enemy_Hp_Bar` không phủ. Hai cơ chế cộng lại:
> `Enemy_Hp_Bar` **909** instance · `Enemy_Display` có renderer **976/981**. Chi tiết: `DIFFICULTY_MODES.md` §1.

**Ví dụ cụ thể, con bị spawn nhiều nhất game:**

```json
{"gameobject": "CB-30003/Enemy_UI/HP_Bar",
 "tree": {"m_Enabled": 1, "hpProgressBarRenderer": {...}, "width": 1.0, "height": 0.12}}
```

`CB-30003` = **4.793** quân — nhiều nhất trong 45.659. Nó **có thanh máu, đang bật**.
⇒ **Không thể chết 1 phát.**

> **Bài học:** tôi đã dùng một câu **chưa kiểm** làm *bằng chứng* cho một giả thuyết, rồi ghi nó vào
> hai file. Đúng loại lỗi mà tôi tự đặt quy tắc chống ở `ASM_INTEGRITY` §4 — nhưng lại áp dụng cho
> asm mà **không** áp dụng cho dữ liệu prefab.

---

## 2. Vì sao trước đó tôi "không thấy" HP — vì nó **không** nằm ở chỗ tôi tìm

Tôi đã tìm HP trong: `Enemy_Datas.StartHealthPoint` (0 ở enemy thường) · `Enemy_Health` (chỉ có
`noDamage` + `armor`) · `Enemy_Data_Balance` (8 method, 0 trả HP) · `Stage_Get_Datas` (11 method,
0 trả HP). **Tất cả đều đúng là không có HP.** Nhưng HP nằm ở class thứ năm:

### `Enemy_Get_Datas` — đọc từ `dump.cs` (**không** phải asm, nên đây là mức A)

```csharp
public class Enemy_Get_Datas : MonoBehaviour {
    private static Dictionary<int, float> AllStartHealthPointEnemies;   // 0x0

    public static float GetDamagePowered(float _crtDamage);   // RVA 0x157EEA0
    public static float GetStartHealthPoint(int _enemyId);    // RVA 0x157F6A8
    private static void .cctor();                             // RVA 0x157F7CC
}
```

**Đây là toàn bộ đáp án cho `B3`:** HP enemy là **bảng tra `id → float`**, dựng trong **`.cctor`**.
Không phải công thức, không phải scale theo stage — **một dictionary**.

### `Enemy_Controller` — nơi giữ HP, có sẵn trong `dump.cs`

```csharp
public float GetStartHealth();                    // 0x15828E4
public float GetCurrentHealth();                  // 0x1582900
public void  TakeDamage(Damager, bool);           // 0x1582938
private void UpdateHpBar();                       // 0x1582F10   ← cập nhật thanh máu
private void OnDieWhenZeroHp();                   // 0x15846F8   ← chết khi HP = 0
private void CacheComponents();                   // 0x158254C   ← cache, không GetComponent mỗi đòn
```

Và `Enemy_Health` — **HP không nằm trong `Enemy_Health`**, nó được truyền **`ref`**:

```csharp
public void CalculateDamage(float _dmg, ref float _hp, bool _igroneInvincible = False);  // 0x158479C
[SerializeField] private bool  noDamage;   // 0x30
private                  float armor;      // 0x34   ← field CÓ, nhưng KHÔNG serialize (0/981)
```

⇒ **Enemy có HP + callback damage.** `armor` là field **không serialize** (xem `UNITY_RULES` §1.1):
981/981 prefab **không** mang giá trị giáp ⇒ coi như **0** trừ khi mã gán lúc `Init`. Chuỗi đầy đủ:
`Enemy_Controller.GetStartHealth()` → `Enemy_Get_Datas.GetStartHealthPoint(id)` → `CalculateDamage(ref hp)` → `UpdateHpBar()` → `OnDieWhenZeroHp()`.

### Cả hai class này **chưa** nằm trong danh sách dump

`tools/apk-analyze/il2cpp_consts.py` → `TARGET_CLASSES` có **17 class**. Trong đó chỉ có **một**
class `Enemy_*` là `Enemy_Data_Balance` (điểm số). **`Enemy_Get_Datas` và `Enemy_Controller` không có.**

⇒ Đây chính là *"phân tích ngược chỗ khác"* mà bạn hỏi ở lượt trước — và nó **nhỏ**: 2 class,
~40 method, trong đó `.cctor` của `Enemy_Get_Datas` là cái đáng giá nhất (**RVA `0x157F7CC`**).

---

## 3. Vế 2 — "treo máy": tính ra thì **không thể**

### 3.1 Tải thật của game — đo từ `waves.json`

| Phép đo | Số |
|---|---:|
| Tổng quân cả campaign | **45.659** |
| Campaign | **63,5 phút** ⇒ **12 quân/giây** |
| Quân mỗi wave | median **131,5** · mean 162 · **max 951** |
| Wave > 300 quân | **33/282 = 12 %** |
| Wave > 500 quân | **14/282 = 5 %** |
| Wave > 700 quân | **8/282 = 3 %** |

**Số con cùng lúc trên màn** — phụ thuộc thời gian sống, hiện **chưa đo được** (`rate`=0 ở 2.371
spawner, `count`=0 ở 100 %):

| Giả định thời gian trên màn | Con cùng lúc (trung bình) |
|---|---:|
| 4 s (speed 5,0) | **~47** |
| 13 s (speed 1,5 — median) | **~157** |
| Wave đông nhất dồn trong 11,4 s | **tới 951** |

> Nhãn **C**: đây là **cận**, không phải số đo. `A7` (mật độ địch đồng thời) vẫn mở.

### 3.2 Chi phí của "tính damage qua HP" — đếm phép tính

| Việc | Số lần/giây |
|---|---:|
| Tra HP khi spawn (`GetStartHealthPoint`) | **12** |
| Trừ HP mỗi viên đạn trúng | **40 – 100** (12 quân/s × 3–8 viên tuỳ HP) |
| Cập nhật thanh máu (`UpdateHpBar`) | **40 – 100** |
| **TỔNG phép tính HP** | **≈ 10² /giây** |

Một điện thoại tầm trung làm **~10⁹** phép số học/giây. **10² / 10⁹ = 1/10.000.000.**

> Nói cách khác: nếu để **một con enemy có HP** tốn 1 giây CPU thì máy đã treo từ lâu **trước** khi
> tới phần HP. **HP không phải chỗ có thể gây lag.** Nó còn rẻ hơn cả một lần `GetComponent`.

### 3.3 Thứ **thật sự** có thể gây lag — và game đã chống bằng gì

| Nguồn tải | Số | Game chống bằng |
|---|---:|---|
| `GameObject` cùng lúc | ~50–950 × ~12 object/con = **600–11.400** | pooling (không thấy `Instantiate` mỗi đòn) |
| `Update()` mỗi frame | ~950 × 60 = **57.000 lời gọi/giây** | chia script nhỏ (`Enemy_Movement`, `Enemy_Rotate`…) |
| **Tra component mỗi đòn** | 40–100/giây | **`CacheComponents()`** — cache 1 lần |
| Va chạm 2D | ~950 collider + đạn | `Enemy_Physics` 981 instance |
| **Vẽ thanh máu** | 950 thanh | `hpProgressBarRenderer` = **SpriteRenderer** (1 sprite scale), **không** phải Canvas/con |

⇒ Hai chi tiết quyết định, và cả hai đều nằm trong `dump.cs`: **`CacheComponents()`** và
**HP bar là một `Renderer` chứ không phải `Canvas`**. Nếu HP bar là Canvas/con thì 950 con =
950 draw call và **đó** mới là "treo máy" — nhưng dữ liệu nói không phải vậy.

**Ngân sách cho bản clone (đề xuất, không phải số gốc):** pool **300** enemy (gấp 2× mức trung bình
157), HP bar là sprite scaling, cache component 1 lần trong `Awake`. Với 8 wave > 700 quân (3 %),
dùng **spawn có nhịp** thay vì dồn — đó là chỗ duy nhất cần để ý.

---

## 4. Điều này đổi gì trong SPEC

| Mục | Trước | **Sau** |
|---|---|---|
| `B3` (HP enemy) | **D** — hai giả thuyết, nghiêng "chết 1 phát" | **B** — HP **có** (dictionary runtime); thiếu **nội dung bảng**, không thiếu cơ chế |
| "HP bar chỉ trên boss" | bằng chứng cho "1 phát" | ❌ **SAI** — **109/109** prefab có bar (100 % quân) |
| Enemy có giáp? | chưa biết | ⚠ **CÓ field, KHÔNG có dữ liệu per-prefab** — `armor` @`0x34` là `private` **không** `[SerializeField]` ⇒ **0/981** prefab serialize; `noDamage` (có attribute) xuất hiện **981/981** (`UNITY_RULES` §1.1) |
| Damage enemy scale? | chưa biết | ✅ có `Enemy_Get_Datas.GetDamagePowered(float)` |
| `T14` (mới) | — | dump `Enemy_Get_Datas` → **bảng HP 981 enemy** |

---

## 5. Việc cần làm — **1 class**, không phải một mảng mới

| # | Việc | Chi phí | Ra được gì |
|---:|---|---|---|
| 1 | Dump **`Enemy_Get_Datas`** (4 method, `.cctor` `0x157F7CC`) | 1 mục `TARGET_CLASSES` | **981 giá trị HP** — đóng `B3` hoàn toàn |
| 2 | Dump **`Enemy_Controller`** (`TakeDamage` `0x1582938` 1.344 B) | cùng lần chạy | thứ tự cổng chặn damage của enemy; có bất tử theo thời gian không (`_igroneInvincible`) |
| 3 | **`Enemy_Health.CalculateDamage`** `0x158479C` | cùng lần chạy | enemy dùng `100/(100+armor)` giống player hay công thức khác |

Cả ba cùng một lần export ⇒ **rẻ hơn** việc tôi suy luận thêm một vòng.

> **Điều kiện lật ngược:** nếu `AllStartHealthPointEnemies` được nạp **lúc runtime** (không phải
> trong `.cctor`) thì dictionary rỗng trong asm, và HP phải lấy từ `Enemy_Datas` asset theo id —
> khi đó 467/981 dòng `StartHealthPoint > 0` mới là nguồn, và **40/109** prefab được spawn mới có HP.
> **Cách phân biệt:** đếm số lệnh `Dictionary.Add`/`set_Item` trong `.cctor` — nếu ≥ 900 thì bảng
> nằm trong `.cctor`; nếu 0 thì nạp runtime.

---

## 6. Còn thiếu / phải đoán

- **Số con cùng lúc (§3.1) là cận, không phải số đo** — `A7` vẫn mở vì `rate`=0 ở 2.371 spawner và
  `count`=0 ở 100 %. Muốn đo thật phải chạy game hoặc đọc `Spawner` code.
- **Tôi chưa chứng minh được `GetStartHealth()` gọi `GetStartHealthPoint()`** — hai method cùng tồn
  tại và cùng trả `float`, nhưng **call graph này là suy luận**, chưa đọc lệnh `bl`. Nhãn **B**.
  **Điều kiện lật ngược:** đọc `Enemy_Controller.GetStartHealth` (`0x15828E4`, 28 B) — 7 lệnh là đủ.
- **Chưa biết HP bao nhiêu** cho từng enemy ⇒ **chưa tính được TTK thật**. Đây là con số duy nhất
  còn thiếu để cân bằng, và nó nằm trong **một** `.cctor`.
- **HP thực tế = HP bảng × `kHp[mode]`** — người chơi kiểm chứng khó hơn thì **nhiều máu hơn** (A, chơi
  game). Phép nhân **không** nằm trong `.cctor`/bảng (HP là **1 số/prefab**, `StartHpPoint = 0` ở
  **981/981** ⇒ HP ghi lúc spawn) mà ở **tầng spawn** — xem `DIFFICULTY_MODES.md` §5. ⇒ Mọi TTK tính từ
  bảng HP là **TTK của Normal**.
- ~~`Enemy_Hp_Bar` 909 / 981 ⇒ 72 enemy không có thanh máu~~ — **đã giải**: `Enemy_Display`
  `hpProgressBarRenderer` phủ **976/981**; hợp hai cơ chế ⇒ **109/109 prefab spawn có bar**. Xem
  `DIFFICULTY_MODES.md` §1.
- **Không** kết luận "damage enemy không scale": `GetDamagePowered(float)` tồn tại, nhưng
  **chưa biết** nó áp cho damage của enemy hay cho damage **nhận vào**.
