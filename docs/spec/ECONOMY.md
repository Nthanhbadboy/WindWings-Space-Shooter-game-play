# ECONOMY — phần thưởng, shop, giá

> Vòng 2. Nguồn sự thật: `reverse-engineering/scriptableobjects/*.csv`,
> `docs/apk-analysis/*.csv`, enum trong `dump.cs`.
> Mỗi bảng ghi `(nguồn: <file>)`. Mỗi khẳng định "không có số" đều kèm **bằng chứng đếm được**.

---

## 0. TL;DR — đọc trước

| Câu hỏi | Trả lời | Bằng chứng |
|---|---|---|
| Có giá coin/gem trong dump không? | **KHÔNG** — 0 giá trị | §4, §5 |
| `Box_Rewards` có phần thưởng không? | **KHÔNG** — `id = 0` và `number = 0` cho **800/800** dòng | `Box_Rewards.csv` |
| `Shop_Cell` có giá không? | **KHÔNG** — chỉ `indexCell` + ref TextMeshPro | `Shop_Cell.csv` |
| `DataShopPack` có giá không? | **KHÔNG** — 69 cột: **61 cột sprite/ref** + 8 metadata, 0 cột số | `DataShopPack.csv` |
| IAP có giá không? | **KHÔNG** — chỉ `type` (99 non-consumable / 71 consumable) + `product_id`, 170 dòng | `13-iap-products.csv` |
| Có **cái gì** là số thật? | `Sub_Item` **17 item id** + số instance; `Item_Movement` `isCoin`/`idle`; `Tech_Ability_Data` Level/TypeIndex; `Shop_Cell.indexCell`; `Stage/Map` count | §1, §3, §6 |
| `PurchaseType` có 6 loại? | **Có** (enum), nhưng **không** serialize vào data | §5.2 |

> ⚠ **Đính chính phân công:** `HANDOFF_AI_TASKS.md` (vòng 2) viết *"`Box_Rewards`/`Shop_Cell`
> có thưởng"*. **Sai.** Đã kiểm 800 + 315 dòng: `Box_Rewards.id` = 0 toàn bộ,
> `Box_Rewards.number` = 0 toàn bộ, `Shop_Cell` không có cột số nào ngoài `indexCell`.
> Chỉ phần **damage** trong phân công là đúng (458 giá trị, xem `COMBAT.md`).
>
> Nguyên nhân: `Shop_Cell` có field `private int id` **không có `[SerializeField]`**
> (xem `class Shop_Cell` trong `dump.cs`) ⇒ không được serialize. Giá được **truyền lúc chạy**
> qua `SetInfomations(int _id, Sprite, string _strvalues, string _strcost, ...)` —
> tức **giá là `string`, không phải số**, và không nằm trong asset.

---

## 1. `Sub_Item` — 17 item id (số thật duy nhất của item)

702 dòng, 12 cột; **không có cột hiệu ứng**. ID nằm trong **tên GameObject** `Item-NNNNN`.

| item id | Số instance | % | Suy luận |
|---|---:|---:|---|
| **70012** | 529 | 75,4% | item rơi phổ biến nhất (khả năng cao là **coin**) |
| **70011** | 145 | 20,7% | item phổ biến thứ 2 |
| 70010 | 14 | 2,0% | |
| 70001 – 70009, 70013 | 1 mỗi loại | 1,3% | |
| 71001 – 71003 | 1 mỗi loại | 0,4% | **3 droid** (khớp `Data_Items` index 101–103) |
| 72000 | 1 | 0,1% | không rõ |
| **Tổng** | **17 id / 702** | 100% | |

Nguồn: `Sub_Item.csv` + `Item_Movement.csv` (cùng 702 dòng, cùng phân bố id).

### 1.1 `Item_Movement` — phân biệt coin vs item

| Field | Giá trị | Số dòng | Nghĩa |
|---|---|---:|---|
| `isCoin` | `True` | **676** | 96,3% là coin |
| | `False` | 26 | item thật |
| `idle` | `True` | 688 | item đứng yên tại chỗ rơi |
| | `False` | 14 | item **di chuyển** (bị hút / trôi) |

Nguồn: `Item_Movement.csv`.

⇒ Trong 702 lượt rơi được đặt sẵn: **676 coin + 26 item thật** (tỉ lệ **26 : 1**).
26 item thật gồm `70010` (14), `70003`…`70009`, `70013`, `71001`–`71003`, `72000`.

### 1.2 Ghép với `Data_Items` (6 item hiển thị)

`Data_Items` có 6 index: `1`, `2`, `3`, `101`, `102`, `103` (nguồn: `14-items.csv`).
Mapping `index → item id` **không có trong dump**.

> **Giả định (đánh dấu rõ):** `1/2/3` = Power / Super / HP ↔ id `70003/70002/70001`;
> `101/102/103` = 3 droid ↔ id `71001/71002/71003`. **Chưa kiểm chứng được** — thứ tự
> trong `Data_Items` không đảm bảo khớp số id. Phải đọc thân hàm `Sub_Item` trong IL2CPP.

Tên item từ `12-localization.csv`: Power Up · Super Power · Restore Hp · Get Droid ·
Gift Box · Lucky Star (`txt_item_powerup`, `_superpower`, `_gainhp`, `_getdroid`,
`_dronecard`, `_star`).

---

## 2. `Box_Rewards` — 800 dòng, **không có dữ liệu**

| Field | Giá trị | Số dòng | Kết luận |
|---|---|---:|---|
| `id` | **0** | **800 / 800** | không có id phần thưởng |
| `number` | **0** | **800 / 800** | không có số lượng |
| `borderNumber` | pathID ref | 800 | chỉ là `SpriteRenderer` viền |
| `boxRenderer` / `iconRenderer` / `objCards` | pathID ref | 800 | sprite |
| `textBonus` / `textNumber` | pathID ref | 800 | `TextMeshPro` — **chữ do code set** |

Nguồn: `Box_Rewards.csv`.

### 2.1 Nó là gì thì dùng được

Đây là **800 instance UI của khung phần thưởng**, phân bố theo board:

| Root | Số instance | Board/hệ thống |
|---|---:|---|
| `Parent_Rewards` | 109 | khung reward dùng chung |
| `Board_Shop` | 66 | shop |
| `Board_BattlePass` | 62 | battle pass |
| `Parent` | 46 | generic |
| `EndgameLoader` | 31 | **màn kết trận** |
| `Board_BattlePassNew` | 30 | battle pass 2 |
| `Board_GiftLogin` | 28 | gift login 30 ngày |
| `Board_PVP` | 28 | PvP |
| `Popup_HolidayGift` (+` 1`) | 48 | quà lễ |
| `ObjectMove` | 19 | scroll |
| `Popup_PremiumDailyCollect` | 19 | premium daily |

**Dùng được để:** biết **hệ thống nào có bao nhiêu ô thưởng** (ví dụ `EndgameLoader` = 31 ô →
màn kết trận hiển thị tối đa 31 phần thưởng; `Board_BattlePass` = 62 ô → BP có ≥ 62 mốc).

**Không dùng được để:** biết thưởng cái gì, bao nhiêu.

> Ví dụ path đầy đủ: `EndgameLoader/Pack_Spec (0)/Parent/Parent_Rewards/Box_Gift (1)`
> ⇒ có **nhiều `Pack_Spec`**, mỗi pack 1 nhóm `Parent_Rewards` ⇒ màn kết trận chia thưởng
> theo "pack" (thường: pack thường / pack premium / pack VIP).

---

## 3. `Shop_Cell` — 315 ô, không có giá *trong CSV*

> ⚠ **Bổ sung:** "không có giá trong CSV" **không** có nghĩa là game không có giá.
> Giá nằm ở 4 chỗ đã định vị (`TUNING_KNOBS.md` §2.4, §3):
> `Player_Get_Datas.PlayerCosts[]` / `PlayerStarCosts[]` · `Tech_Datas.basePriceStatUpgrade[]`
> + `deltaPrice*[]` · `Droid_Data_Balance.UnlockCosts[]` · `Stage_Get_Datas.coinDelta/gemDelta/levelDelta[]`.
> Tất cả là `static`, khởi tạo trong `.cctor()` — đọc được bằng Ghidra.

| Field | Kiểu | Giá trị trong CSV |
|---|---|---|
| `indexCell` | `int` (public) | **0** × 272, 1–5 × 43 |
| `isVideoBox` | `bool` | `True` × **1** (duy nhất) |
| `iconRenderer` | SpriteRenderer | pathID |
| `textValues` · `textCost` · `textBonus` · `textStock` · `textPrice` · `textVipPoint` · `textFirstPurchaseValue` | TextMeshPro | pathID |
| `id` | `private int` **không `[SerializeField]`** | **không có trong CSV** |
| `fc` | GameObject | pathID = 0 (null) |

Nguồn: `Shop_Cell.csv` + `class Shop_Cell` (`dump.cs`).

### 3.1 `indexCell` là gì

`indexCell` khác 0 chỉ xuất hiện ở các cell **nằm trong tab con** của shop
Arena/PvP/Devices/Drones/Items:

| `indexCell` | Số ô | Vị trí |
|---:|---:|---|
| 0 | 272 | cell mặc định / chưa gán |
| 1–5 | 43 | tab thứ 1…5 trong `Parent_Players`, `Parent_Drone`, `Parent_Devices`, `Parent_Items` |

⇒ `indexCell` = **chỉ số tab/nhóm trong shop**, không phải giá.

### 3.2 315 ô thuộc board nào

**20 board** (`Board_*`) chứa **208 ô (66%)**; 15 root còn lại chứa 107 ô.

| Root | Số ô | Shop |
|---|---:|---|
| `Special_Packs` | 31 | pack đặc biệt (IAP) |
| `Board_Shop` | 28 | shop chính |
| `Board_Arena` | 24 | shop arena |
| `Board_PVP` | 22 | shop PvP |
| `Popup_NoGems` (+ ` 1`) | 21 | **popup "hết gem" cũng có shop** (upsell) |
| `Board_Drones` | 11 | shop drone |
| `Board_FightBoss` | 10 | shop boss |
| `Board_Survival` | 10 | shop survival |
| `Board_Upgrades` | 10 | shop nâng cấp |
| `Board_RebornIAP` / `Board_Ranks` | 9 / 9 | IAP hồi sinh · shop rank |
| `Parent_Cells` | 9 | container trong tab |
| `Board_Obstacle` / `Board_SelectMode` / `Board_Maps` / `Board_Stage` / `Board_WinnerBenefits` / `Group 3` / `ObjectMove` | 8 mỗi root | |
| `Board_BeginPlay` / `Board_Players` / `Board_Reborn` / `Board_QuestRewards` | 7 mỗi board | mua trước trận · tàu · hồi sinh · quest |
| `Popup_WatchVideosNew` / `ScrollView` | 6 / 6 | |
| `Popup_NoCoins` / `Board_ShopEnergy` | 4 / 4 | |
| `Board_Vip` | 3 | |
| `Normal_Packs` / `Parent_Drones` | 2 / 2 | |
| `Parent` / `Parent_Players` / `Parent_Drone` / `Shop_PVP` / `Popup_NoGems (1)` | 7 / 1 / 1 / 1 / 1 | |

Nguồn: `Shop_Cell.csv`, cắt `_gameobject` trước `/` đầu tiên.

**Đọc ra:** shop không tập trung 1 chỗ — **20 board đều có cell bán hàng**, cộng thêm
7 popup. Đây là monetization rải rác (contextual offer), khác hoàn toàn mô hình
"1 shop duy nhất".

### 3.3 `PurchaseType` — 6 loại, chỉ tồn tại trong code

```
PurchaseType { Free = 0, Pro = 1, IAP = 2, IAPBeginner = 3, Gem = 4, Coin = 5 }
```
Nguồn: enum `PurchaseType` trong `dump.cs`.

Enum này **không** xuất hiện ở bất kỳ cột CSV nào (đã `grep` toàn bộ 91 file SO + 56 file
apk-analysis: 0 kết quả). ⇒ loại thanh toán được chọn **lúc chạy**, không phải dữ liệu.

| Loại | Nghĩa | Nơi dùng (suy từ tên board) |
|---|---|---|
| `Free` | nhận miễn phí | gift login, quest reward |
| `Pro` | cần tài khoản premium | `Popup_PremiumDailyRewards` |
| `IAP` | mua bằng tiền thật | `Special_Packs`, `Board_RebornIAP` |
| `IAPBeginner` | gói người mới (1 lần) | `Popup_FirstPurchase` |
| `Gem` | trả bằng gem | shop drone/device/ship |
| `Coin` | trả bằng coin | nâng cấp |

---

## 4. `DataShopPack` — 69 cột, **không cột nào là số**

| Nhóm cột | Số cột | Cấu trúc | Nội dung | Có số? |
|---|---:|---|---|---|
| `allRankSprites[]` | 11 | 5 × (FileID+PathID) + len | khung rank | ❌ |
| `allSpriteRewards[]` | 11 | 5 × 2 + len | icon phần thưởng | ❌ |
| `listSpritePlayers[]` | 11 | 5 × 2 + len | icon tàu | ❌ |
| `listSpriteDrones[]` | 11 | 5 × 2 + len | icon drone | ❌ |
| `listAvatars[]` | 11 | 5 × 2 + len | avatar | ❌ |
| `cardPlayerRandomSprite` · `cardDroneRandomSprite` · `itemRandomSprite` | 2 mỗi cái | 1 × 2 | icon "random" | ❌ |
| metadata Unity | 8 | `path_id`, `_gameobject`, `m_Enabled`, `m_Name`, `m_Script.*`, `m_GameObject.*` | | — |

**Kiểm chứng tổng cột:** 5 nhóm × 11 = **55** sprite + 3 sprite lẻ × 2 = **6** + metadata
**8** (`path_id`, `_gameobject`, `m_Enabled`, `m_Name`, `m_Script` ×2, `m_GameObject` ×2)
= **69** ✓.
Lọc cột không chứa `sprite|avatar|path_id|fileid` → còn **3 cột**: `_gameobject`,
`m_Enabled`, `m_Name`. **Không có** `price`, `cost`, `rate`, `weight`, `amount`, `count`.
Mọi mảng chỉ có **5 phần tử** (không phải 7/27/24/12 như bảng cũ ước lượng sai).

Nguồn: `DataShopPack.csv` (2 dòng, `_gameobject` = `DataShop` cả 2 → **bản trùng**, dedup = 1).

**Kết luận:** `DataShopPack` chỉ là **bảng tra icon** cho 5 nhóm × 5 sprite. Không có kinh tế.

## 5. IAP — 170 sản phẩm, **không có giá trong APK** (giá thật nằm trên store)

| Field | Kiểu | Giá trị |
|---|---|---|
| `type` | string | `NonConsumableProducts` **99** · `ConsumableProducts` **71** |
| `product_id` | string | 170 id duy nhất, prefix `windwings.` |

Nguồn: `13-iap-products.csv`, `IAPProduct.csv` (cùng 170 dòng).

### 5.1 Nhóm product theo prefix (đếm chính xác)

| Prefix | Số SKU | Loại |
|---|---:|---|
| `playerunlock` | **96** | mở tàu |
| `gems` | **19** | túi gem |
| `gifts` | 11 | quà |
| `shipfull` | 6 | mua trọn tàu |
| `vippack` 1–6 | 6 | VIP |
| `coinevent` | 4 | coin theo event |
| `pro` | 4 | premium account |
| `select` | 4 | chọn tàu |
| `coins` | 3 | coin |
| `combo` | 3 | combo |
| `x` (không rõ nghĩa) | 3 | |
| `battlepass` + `battlepass2` | 2 | BP |
| `timereward` | 2 | quà theo giờ |
| `winner` | 2 | thưởng thắng |
| `giftlogin` · `penalty` · `techlab` · `unlockzone` · `droneunlock` | 1 mỗi loại | |
| **Tổng** | **170** | |

**Không có `price`** — giá lấy từ Google Play Console lúc chạy (`IAPProduct` chỉ giữ id).
`playerunlock` chiếm **56%** SKU: mỗi tàu là 1 SKU riêng, đúng mô hình bán tàu rời.

### 5.2 `Shop_Cell` vs `IAPProduct`

```
Shop_Cell (layout)  →  SetInfomations(id, icon, strValues, strCost, onClick)
                              ↑            ↑          ↑
                         runtime id    chuỗi hiển thị   chuỗi giá
IAPProduct (id)  ─────────────┘
```
⇒ Muốn clone: **giá phải tự thiết kế**, không có số nào để tham chiếu.

---

## 6. `Tech_Ability_Data` — 6 bảng, 30 mốc (số thật)

6 instance, mỗi cái `listDatas[5]` với `{Level, TypeIndex, Sprite}`.

| # | Level (5 mốc) | TypeIndex | Sprite pathID |
|---:|---|---|---|
| 1 | 1, 2, 3, 2, 4 | 2, 1, 1, 2, 1 | 3893, 2700, 2700, 3893, 2700 |
| 2 | 1, 2, 1, 3, 2 | 0, 0, 0, 0, 0 | 2543, 2543, 2463, 2543, 2463 |
| 3 | 1, 2, 1, 3, 2 | 0, 0, 0, 0, 0 | 2601, 2601, 2959, 2601, 2959 |
| 4 | 1, 2, 1, 3, 2 | 1, 1, 2, 1, 2 | 3298, 3298, 2493, 3298, 2493 |
| 5 | 1, 1, 2, 3, 2 | 0, 0, 0, 0, 0 | 3827, 3308, 3827, 3827, 3308 |
| 6 | 1, 2, 1, 3, 4 | 0, 0, 0, 0, 0 | 3852, 2930, 3852, 2930, 3852 |

Nguồn: `Tech_Ability_Data.csv`.

**Đọc ra:**
- `Level` không tăng đơn điệu (bảng 1 có `1,2,3,2,4`) → đây **không phải** đường cong nâng cấp
  mà là **5 biến thể ability** ở các cấp khác nhau, hiển thị theo thứ tự nhất định.
- `TypeIndex` chỉ 3 giá trị (0, 1, 2) → 3 **kiểu hiệu ứng** (không phải 12 stat).
- Có **6 bảng** nhưng vòng 1 ghi 12 stat tech → 6 bảng này phục vụ 6 nhóm, 12 stat chia 2.

**Không có** `%`, `duration`, `cooldown` — toàn bộ nằm trong `Player_Get_Datas.abi*`.

---

## 7. `RankManager` — 3 dòng, chỉ UI

| `_gameobject` | Field có thật |
|---|---|
| `Board_Maps/Board_Ranks` | `loadingObject`, `popupNoInternet` |
| `BOARD_ENDGAME` | `btnExitCover`, `loadingObject`, `popupNoInternet`, `popupUploadFailed` |
| `Board_Ranks` | `loadingObject`, `popupNoInternet` |

Nguồn: `RankManager.csv`.

Không có ngưỡng rank, không có điểm, không có thưởng. `RankManager` chỉ gọi Firebase.

---

## 8. Tổng hợp: cái gì là số thật

| Nguồn | Số thật | Dùng được cho |
|---|---|---|
| `Gun_Attack` | 458 damage, 5 tham số burst, speed/lifetime | **COMBAT** (`COMBAT.md`) |
| `Enemy_Datas` / `15-enemy-hp` | **800** HP (394 > 0) | **BALANCE** |
| `Boss_BodyPhysics` | 251 hitbox `dmgFirst`/`dmgPerSec` | **COMBAT** §6.3 |
| `Sub_Item` + `Item_Movement` | 17 item id + 702 lượt rơi (676 coin / 26 item) | **tỉ lệ rơi tương đối** |
| `Box_Rewards` | **0** | chỉ đếm số ô thưởng |
| `Shop_Cell` | 0 giá, chỉ `indexCell` | đếm số ô shop/board |
| `DataShopPack` | **0** | tra icon |
| `IAPProduct` | 0 giá, 170 id | danh mục SKU |
| `Tech_Ability_Data` | 30 mốc Level/TypeIndex | số mốc ability |
| `RankManager` | **0** | — |

### 8.1 Suy ra tỉ lệ rơi (mức C)

Từ `Item_Movement`: 676 coin / 26 item = **96,3% : 3,7%**. Nhưng đây là **số instance đặt sẵn
trong prefab wave**, không phải trọng số random lúc chạy.

> **Giả định:** tỉ lệ rơi thực tế ≈ **1 item thật / 26 lượt rơi**. Dùng làm mốc thiết kế:
> mỗi 25–30 enemy chết → 1 item có ý nghĩa. Không nên dùng làm trọng số tuyệt đối.

### 8.2 Ngân sách kinh tế đề xuất (không phải số gốc)

| Nguồn | Coin/trận | Gem/ngày | Item/trận |
|---|---:|---:|---:|
| Thắng stage thường | 300 | 5 | 0–1 |
| Thắng stage boss | 900 | 15 | 1–2 |
| Quest ngày (5 quest) | 500 | 20 | 1 hộp |
| Battle pass free | — | 10 | — |
| Ads (5 vị trí) | 250 | 15 | 1 |

> Bảng này là **đề xuất**, không có cơ sở từ APK — dùng để đội cân bằng có mốc ban đầu,
> thay bằng số thật khi có thiết kế riêng.

---

## 9. Nguồn

`reverse-engineering/scriptableobjects/`: `Box_Rewards.csv` · `Shop_Cell.csv` ·
`Sub_Item.csv` · `Item_Movement.csv` · `DataShopPack.csv` · `RankManager.csv` ·
`Tech_Ability_Data.csv` · `IAPProduct.csv` · `Data_Items.csv`
`docs/apk-analysis/`: `13-iap-products.csv` · `14-items.csv` · `12-localization.csv` ·
`DataShopPack.csv` · `Shop_Cell.csv` · `Sub_Item.csv` · `Box_Rewards.csv`
`reverse-engineering/il2cpp/dump.cs.gz`: `class Shop_Cell`, `class Box_Rewards`,
enum `PurchaseType`, `class Tech_Ability_Data`, `class RankManager`.

---

## 10. Còn thiếu / phải đoán

| # | Điều | Trạng thái | Cách lấy |
|---:|---|---|---|
| 1 | **Giá mọi thứ** (coin/gem/IAP) | **D — không thấy trong 91 CSV** (chưa kết luận về IL2CPP) | tự thiết kế, **hoặc** đọc `Shop_Cell.SetInfomations` trong IL2CPP |
| 2 | `Box_Rewards.id` / `number` | **A — luôn 0** | là UI template, không phải data |
| 3 | `Shop_Cell.id` | **A — không serialize** (`private`, không `[SerializeField]`) | runtime |
| 4 | `PurchaseType` của từng ô | **D** | runtime |
| 5 | Mapping `item id 70001–72000` ↔ hiệu ứng | **C — giả định** §1.2 | thân hàm `Sub_Item` |
| 6 | Trọng số random của hộp quà | **D** | `Box_Rewards` không có weight |
| 7 | Số lượng reward mỗi hộp | **D** | `number` = 0 |
| 8 | Giá IAP thật | **D** | Google Play Console, không có trong APK |
| 9 | Ngưỡng VIP 1–6 | **D** | `GameDatas.GetVipLevel` |
| 10 | `72000` là item gì | **D** | 1 instance duy nhất |
| 11 | Tỉ lệ rơi theo loại enemy | **D** | cần `Enemy_Data_Balance` |

---
