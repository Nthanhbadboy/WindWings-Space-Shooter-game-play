# TUNING_KNOBS — toàn bộ núm vặn của game, và giá trị nằm ở đâu

> Mục đích: trả lời câu *"feel / cân bằng / art đào được tới đâu?"*.
> Trả lời ngắn: **đào được thêm, nhưng chưa đào xong** — và mục này chỉ rõ **còn bao nhiêu
> thứ chưa có giá trị**, không hứa hẹn một con số phủ.
> Mọi số dưới đây đọc từ `reverse-engineering/il2cpp/dump.cs` (18,8 MB, 10.910 block class).
> Suy luận đánh dấu `> Nhận định:`. Mục cuối: **Còn thiếu / phải đoán**.

---

## 0. Sửa lại ba kết luận trước — chúng sai vì đọc sai chỗ

| Kết luận cũ (sai) | Sự thật | Bằng chứng |
|---|---|---|
| "Không có damage/HP player" | `Player_Get_Datas.StartHp` · `BaseHpRecoverSpeed` · `StartMainCannonDamages[]` · `StartWingCannonDamages[]` · `StartSecretWeaponDamage` | `dump.cs`, class 178 field |
| "Không có giá" | `PlayerCosts[]` · `PlayerStarCosts[]` · `Tech_Datas.basePriceStatUpgrade[]` + `deltaPrice*[]` · `Droid_Data_Balance.UnlockCosts[]` · `Stage_Get_Datas.coinDelta/gemDelta/levelDelta[]` | " |
| "Feel nằm trong `libil2cpp.so`" | Phần lớn feel là **`[SerializeField]`** → nằm trong **prefab của `data.unity3d`** | `VibrateCamera.levelVibrate` · `Enemy_CameraVibrate.timeVibr/lvVibr` đều là `[SerializeField]` |

**Vì sao tôi sai:** exporter CSV chỉ lấy **ScriptableObject** (`reverse-engineering/scriptableobjects/`)
và một số `MonoBehaviour` có trong danh sách. Nó **không** quét hết component gắn trên prefab.
Trong khi đó `dump.cs` cho thấy game classes có **4.861 field `[SerializeField]`** — từng đó giá
trị đang nằm trong bundle và **chưa được xuất**.

> `> Nhận định (mức B):` phần lớn khả năng là **phạm vi export quá hẹp**, không phải APK thiếu dữ liệu.
> Nhưng **chưa kiểm chứng** — có thể một phần trong đó là giá trị mặc định, không mang thông tin.
> Tỉ lệ thật chỉ biết sau khi chạy AssetRipper.

---

## 1. Ba nơi giá trị sống — và chi phí lấy từng nơi

| Nơi | Có gì | Lấy bằng | Chi phí |
|---|---|---|---|
| **A. CSV đã có** | 91 ScriptableObject + `waves.json` | (đã xong) | **0** |
| **B. `[SerializeField]` trong prefab** | **4.861 field** — shake, tốc độ, size, màu, kéo dài (đếm regex, sai số vài chục) | **AssetRipper** (hoặc UnityPy + typetree) | ước lượng, mức **C** |
| **C. `static` field khởi tạo trong `.cctor()`** | **957** static tổng (riêng 8 class config: **259**) — HP, damage, giá, hệ số | **Ghidra + `script.json`** | ước lượng, mức **C** |
| **D. `const` khai báo** | 9905 const toàn dump; **900** ở game class — nhưng **875 là enum**, chỉ **25** hằng số thật | đọc trực tiếp `dump.cs` | **0** |
| **E. Hành vi lúc chạy** | giá theo mùa, A/B, server | Frida | tuần |

Nhóm **D** có sẵn giá trị trong `dump.cs` — nhưng chỉ **25** hằng số ngoài enum dùng được ngay. Ví dụ thật:

| Class | Field | Giá trị |
|---|---|---:|
| `GP_Controller` | `timeSlowed` | **0,1** (giây — slow-mo khi nhả tay) |
| `UIObjectAnchors` | `haftOfW` / `haftOfH` | **5,4 / 9,6** ⇒ canvas **10,8 × 19,2** unit |
| `VertexPath` | `accuracy` / `minVertexSpacing` | 10 / 0,01 |
| `SoxAtkJiggleBone` | `mc_tensionMul` | 0,1 (độ nảy xương Spine) |
| `SoxAtkTentacle` | `mc_freqMul` | 0,01 (tần số rung) |
| `IAPSystem` | `MaxProductFetchRetries` | 2 |
| `Board_Endgame` | `indexPackX20/35/50` | 10 / 25 / 26 |

Ngoài ra **`Ease`** enum có đủ **31 giá trị** (Linear, InBack, InBounce, InCirc, InCubic, InElastic,
InExpo, InQuad, InQuart, InQuint, InSine, OutBack, OutBounce, OutCirc, OutCubic, OutElastic,
OutExpo, OutQuad, OutQuart, OutQuint, OutSine, InOutBack, InOutBounce, InOutCirc, InOutCubic,
InOutElastic, InOutExpo, InOutQuad, InOutQuart, InOutQuint…) — tức **dùng DOTween**, và toàn bộ
đường cong animation UI đã biết tên.

---

## 2. Cân bằng player — `Player_Get_Datas` (178 field)

Đây là **toàn bộ model player**, không thiếu mảng nào. Nhóm theo chức năng:

### 2.1 Chỉ số gốc

| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `StartHp` | float | **HP khởi đầu của player** |
| `BaseHpRecoverSpeed` | float | tốc độ hồi HP |
| `StepCommon` (`stepCommon`) | float | bước tăng chỉ số chung |
| `StartMagnetRange` | float | bán kính hút item |
| `PercentFreeOverDrive` | float | % nạp Overdrive miễn phí |
| `StartMaxDuration` | float | thời lượng tối đa 1 lượt chơi |

### 2.2 Damage theo cấp pháo

| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `StartMainCannonDamages` | float[] | **damage pháo chính theo cấp** |
| `StartMainCannonRate` | float[] | **tốc độ bắn theo cấp** |
| `StartWingCannonDamages` | float[] | damage pháo cánh |
| `StartSecretWeaponDamage` | float | damage vũ khí bí mật |
| `StartSecretWeaponDuration` | float | thời lượng |

### 2.3 Tham số chiến đấu theo **loại tàu** — 20 archetype

Mỗi loại `pN` có bộ tham số riêng. Các `pN` **có mặt**:
`p1 p2 p3 p4 p5 p6 p7 p9 p11 p13 p14 p16 p17 p18 p19 p20 p21 p22 p23 p24` → **20 loại**
(khuyết `p8 p10 p12 p15` — dùng mặc định của base class).

Trường của mỗi loại:

| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `pN_idBltNormal` | int | id đạn thường (nối sang `Gun_Attack`) |
| `pN_idBltPowerUp` | int | id đạn power-up |
| `pN_startShotRate` | float | nhịp bắn |
| `pN_startBltSpeed` | float | tốc độ đạn |
| `pN_superPowerUpShotRate` | float | nhịp bắn khi super |
| `pN_superPowerUpBltSpeed` | float | tốc độ đạn khi super |
| `pN_speedMainCannonBlt` | float | tốc độ đạn pháo chính |

Tham số riêng lẻ: `p1_radiusCheck`, `p4_radiusCheck`, `p4_radiusCheckMainCannon`,
`p2_normalLifetime/Size`, `p2_supermodeLifetime` (`ParticleSystem.MinMaxCurve` — **dải ngẫu nhiên**
của particle), `p19_startShotRate`, `p21_zoneDuration`, `shipCloneLifeTime`, `shipCloneDamage[]`,
`forceFieldDuration`.

### 2.4 Kinh tế & tiến trình (player)

| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `PlayerCosts` | int[] | **giá mua tàu** |
| `PlayerStarCosts` | int[] | giá nâng sao |
| `PlayerTimeStars` | int[] | số sao theo thời gian |
| `listStarToTryLegendaryPlayers` | Dictionary | sao để **dùng thử** tàu huyền thoại |
| `listStarToBuyLegendaryPlayers` | Dictionary | sao để **mua** |
| `PercentToCompleteMissions222` | float[] | % hoàn thành nhiệm vụ |

### 2.5 Cảm giác (feel) ngay trong class này

| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `TimeResetInvincible` | float | thời gian hồi bất tử sau khi trúng đòn |
| `TimeCanActiveInvincible` | float | thời gian có thể kích hoạt bất tử |
| `TouchRanger` | float | bán kính va chạm của player |
| `shipCloneLifeTime` | float | thời gian tồn tại bản sao tàu |
| `forceFieldDuration` | float | thời gian khiên |
| `p21_zoneDuration` | float | thời gian vùng |

### 2.6 Hệ **ability/talent** — 22 ability

⚠ **Ability và Talent là HAI hệ khác nhau** (trước đây gộp làm một — sửa lại):

| | `Player_Ability` | `Player_Talent` |
|---|---|---|
| Bản chất | **skill runtime** | **cây điểm mua bằng coin** |
| Field chính | `shieldObject` · `shieldOneHit` · `shieldDroidObject101/103` · `drone7SkillObject` · `drone11SkillObject` · `revokeEfxIds` | `talentIndex` · `pointCount` · `points` · `coinPerPoint` · `List<Talent_Invisible> allZoneInvisible` · `listShipInvisible` |
| Nội dung | **khiên** và **skill của drone** (drone 7, 11, 101, 103) | **invisible + heal** (`SetInvisible(zone, p, invisible, heal)`) |
| Dùng chung mọi tàu? | ✅ (không có `playerIndex`) | ✅ (không có `playerIndex`) |

⇒ **"Né" là ability 8** (`abi8AddDodgeRate`), **"invisible" là talent** (`Talent_Invisible`).
Hai thứ khác hệ nhưng **cùng dùng chung cho mọi tàu**.

`Player_Get_Datas` chứa thẳng tham số của từng ability:

| Ability | Field | Tác dụng |
|---:|---|---|
| 5 | `abi5GainHp` | hồi HP |
| 7 | `abi7AddPlayerStartHp` | +HP khởi đầu — **đã nối**: nhân với `GP_Datas.GetNumberAbility(7)` |

> **Đã giải mã chuỗi HP player** (`BALANCE.md` §0.6, mức A — đọc từng lệnh arm64):
>
> ```
> GetStartHp() = StartHp × (1 + stepCommon × TechStatPoints(0)
>                               + abi7AddPlayerStartHp × GetNumberAbility(7))
> ```
>
> `stepCommon` (`@0x68`) = **0,18** — **khác** `stepLevel` (0,168) dùng cho damage.
> `StartHp` (`@0x6C`) = **2500,0** (đọc từ `.cctor`, bản `6109008c`).
> **Núm vặn HP gồm 3 cái:** `StartHp` (**2500,0** — đã có) · điểm tech stat **index 0** ·
> ability **7**. Giáp `Player_Health.Armor` là **núm thứ tư nhưng tách riêng** — nó giảm damage
> nhận vào, không cộng vào HP.
| 8 | `abi8AddDodgeRate` | +tỉ lệ né |
| 9, 10 | `abi9ReduceREDDmg`, `abi10ReduceREDDmg` | giảm damage nhận |
| 11 | `abi11AddWingCannonDmg` | +damage pháo cánh |
| 14 | `abi14ReduceCooldown` | giảm hồi chiêu |
| 17 | `abi17AddPowerPerKill` | +power mỗi kill |
| 19 | `abi19ReduceEnemyShotRate` | giảm nhịp bắn enemy |
| 20, 21 | `abi20AddDmgSkillDrone`, `abi21AddDmgDrone` | +damage drone |
| 22 | `abi22AddAgilityRate` | +nhanh nhẹn |
| 23 | `abi23AddItemRate` | +tỉ lệ rơi item |
| 24 | `abi24CritRate` | **tỉ lệ chí mạng** |
| 25 | `abi25AddDroneShotRate` | +nhịp bắn drone |
| 26, 27 | `abi26/27AddDmgMelee` | +damage cận chiến |
| 29 | `abi29Amount` | lượng |
| 30 | `abi30Rate` + `abi30Amount` | tỉ lệ + lượng |
| 31, 32, 34 | `abi31Rate`, `abi32Rate`, `abi34Rate` | tỉ lệ |

---

### 2.7 Device — 5 loại × 2 stat, 4 slot/tàu

| Knob | Giá trị gốc | Nguồn |
|---|---|---|
| Số **loại** device | **5** (`type = id/100 − 1`, 0…4) | `GetStatValue1` `cmp w20, #4` |
| Số **stat** mỗi device | **2** (`GetStatValue1` / `GetStatValue2`) | `Device_Get_Data` |
| Số **slot** mỗi tàu | **4** | `GetPlayerUse` `cmp x8, #4` |
| Công thức stat | `base[type][rank] + pct[type] × (lv+1)`; `type==4` **÷ 100** | `GetStatValue1` |
| Hệ số `base` / `pct` | ❌ **chưa có** (nạp bằng `RuntimeHelpers.InitializeArray` từ RVA data) | — |

**Knob thiết kế:** số slot (4) · số loại (5) · có/không nhánh % · `lv+1` hay `lv`
(bản gốc dùng **`lv+1`** — device **lv=0 vẫn có** 1 bậc pct).

## 3. Cân bằng kinh tế — công thức giá **đã lộ hình dạng**

`Tech_Datas` (13 field) cho thấy giá nâng cấp là **cấp số cộng**, không phải bảng tra:

| Field | Kiểu | Vai trò trong công thức |
|---|---|---|
| `basePriceStatUpgrade` | int[] | giá **gốc** mỗi stat (theo index stat) |
| `deltaPriceTechStats` | float[] | **bước tăng** mỗi cấp |
| `basePriceTechStatUpgrade` | int[] | giá gốc theo cấp tech-lab |
| `CostUpgradeTechLab` | int[] | giá nâng tech-lab |
| `CostUnlockStats` | int[] | giá mở khoá stat |
| `maxUpgradePlayer` / `maxUpgradeTech` | int | **trần cấp** |
| `MAX_LV_TECHLAB` | int | trần tech-lab |
| `deltaPricePlayers` / `deltaPriceDrones` / `deltaPriceDroids` | float[] | hệ số giá theo loại |
| `StartStarCost` / `DeltaStarCost` | int | giá sao: khởi đầu + bước |

> `> Nhận định:` dạng công thức là `price(lv) = base[index] + delta[index] × lv`.
> Chỉ cần đọc **2 mảng** trong `.cctor` là dựng lại **toàn bộ 3 cây nâng cấp**
> (player / drone / tech), không cần bảng giá từng cấp.

Các class kinh tế còn lại:

| Class | Số field | Cho biết |
|---|---:|---|
| `Droid_Data_Balance` | 6 | `MaxLevelUpgrade` · `BaseDamages[]` · `DroidTimeOut[]` · `UnlockCosts[]` · `UnlockStarCosts[]` · `StartRanks[]` |
| `Stage_Get_Datas` | 5 | `startBonusValues[]` · `coinDelta` · `gemDelta` · **`levelDelta[]`** (đường cong thưởng theo cấp) · `listIgroneEnemies` |
| `Device_Get_Data` | 3 | `listStatValues` · `percentByLevels1` · `percentByLevels2` (nội suy theo cấp thiết bị) |
| `Map_Get_Datas` | 13 | `listMapDatas` · `AllArenaStartMaps` · `AllPvPStartMaps` · `listIdBosses` · `mapChallangeIndexs` — **dữ liệu map/arena** |

`Stage_Get_Datas.levelDelta[]` chính là **đường cong độ khó theo cấp stage** — thứ tôi từng nói
"không thể tái tạo".

---

## 4. Feel — đã định vị từng cơ chế

| Cơ chế | Class | Tham số | Nơi giá trị |
|---|---|---|---|
| **Camera shake** | `VibrateCamera` | `tVibrate` (số frame) · `levelVibrate` (biên độ) · `timeVibrate` static | `[SerializeField]` → **prefab** |
| **Shake theo từng enemy** | `Enemy_CameraVibrate` | `timeVibr` · `lvVibr` | `[SerializeField]` → **prefab**. **Đã đo** (241 instance): `0,10 · 20` ×**185** · `0,05 · 15` ×**46** · `0,15 · 30` ×**6** · `0,10 · 30` ×**3** · `0,10 · 40` ×1 |
| **Slow-motion** | `GP_Controller` / `GP_Time` | `timeSlowed = 0,1` · `timeMulti` · `rawTimeScale` | **const + .cctor** — ⚠️ **nghi field chết**: chuỗi `timeScale` **0 lần** trong 69 file asm; riêng `GP_Controller` **không có** file asm nên chưa đọc được hàm dùng nó; người chơi **không thấy** slow-mo ⇒ coi như **không có** |
| **Hit flash** | `Enemy_HitSkeletonRenderer` | `hitColor` (Color) | `[SerializeField]` |
| **Glow / shine** | `EffectGlow` | `speedLight` · `timeRepeat` · `randomShine` | `[SerializeField]` |
| **Trail** | `TimedTrailRenderer` | `timeTrail` | `[SerializeField]` |
| **Jiggle xương (Spine)** | `SoxAtkJiggleBoneSimple` | `mc_tensionMul = 0,1` | **const** |
| **Tentacle wobble** | `SoxAtkTentacle` | `mc_freqMul = 0,01` | **const** |
| **Easing UI** | `Ease` | 31 đường cong DOTween | **const** |
| **Độ trễ bắn** | `Player_Attack_N` | `timeToShotMainCannonDelay` (mỗi tàu) | `[SerializeField]` |
| **Đạn giảm tốc** | `Bullet_SlowDown` / `Ball` | `startSlowDelta` · `addSlowDelta` · `minSlowDelta` | `[SerializeField]` |
| **Đạn trễ** | `Bullet_DropDown` · `Bullet_Rocket` · `Homing_Missile1/2/3` | `timeDelay` · `timeDelayMin/Max` · `timeDelayLaunch` · `lerpSlow` | `[SerializeField]` |
| **Cháy** | `Enemy_Burned` | `burnDuration` | `[SerializeField]` |
| **Khiên / lerp** | `ShipProtect` | `LerpTo(...)` — nội suy vị trí | code (Ghidra) |
| **Frame rate** | `GameSetupTargetFrameRate` | target FPS | scene |
| **Rung máy (haptic)** | *(không có class)* | — | không dùng |

> **Điểm mấu chốt:** 11/16 mục trên là **`[SerializeField]`** ⇒ giá trị nằm trong **prefab**,
> tức **đã có trong `data.unity3d`** — chỉ chưa export. **Không** cần decompile để lấy feel.

---

## 5. Art — quy đổi ra đơn vị thế giới đã có

| Thông số | Giá trị | Nguồn |
|---|---|---|
| Canvas nửa chiều | **5,4 × 9,6** unit ⇒ **10,8 × 19,2** | `UIObjectAnchors` const |
| Tỉ lệ màn | 10,8 / 19,2 = **0,5625** = **9:16** | suy ra |
| Vùng chơi enemy | **20 × 25** unit | `Enemy_Movement.csv` border |
| Bán kính va chạm đạn | **15** unit | `Gun_Attack.csv` (`border.w`) |
| Số mesh toàn game | **2** | `04-unity-assets.md` |
| Atlas page | **67** page / 31,0 MB · max 3,09 MB | `04-asset-manifest.csv` |
| Kích thước page | 1024² 21 · 512² 17 · 512×1024 9 · 1024×512 6 · 1024×2048 4 · 2048×1024 4 · 2048² 2 | " |
| Shader | **70** | `04-unity-assets.md` |
| Font | TextMeshPro (TMP_Settings, TMP_StyleSheet, TMP_ColorGradient) | 91 CSV |

**Hệ quả cho art thay thế:** tỉ lệ **9:16**, sprite được thiết kế theo **bội số của 19,2 unit**,
và vì cả game chỉ có **2 mesh**, mọi thứ hiển thị là **sprite billboard phẳng**.
Nghĩa là art mới chỉ cần: **sprite PNG trong suốt + 1 atlas**, không cần model, không cần
normal map, không cần rig 3D.

> `> Nhận định:` "phong cách tương tự" là khả thi **về mặt kỹ thuật** vì ràng buộc rất ít:
> 9:16, billboard, tối đa 2048² mỗi page. Không có ràng buộc nào về shader PBR, ánh sáng,
> hay vật liệu — đúng như bạn nói.

---

## 6. Thứ tự khai thác — rẻ trước, đắt sau

| Bước | Việc | Lấy được | Công |
|---:|---|---|---|
| 1 | Đọc `const` trong `dump.cs` | **25** hằng số thật (`Ease` 31 giá trị enum, `timeSlowed` 0,1, `haftOfW/H` 5,4/9,6) | **0** — đã có |
| 2 | **AssetRipper** trên `data.unity3d` | 4.861 `[SerializeField]`: shake, tốc độ, damage/súng, màu, size (chưa biết đọc được bao nhiêu) | chưa đo |
| 3 | **Ghidra + `script.json`** đọc 1.359 `.cctor` | 259 static field: HP, damage, giá, hệ số | ngày |
| 4 | **Frida** hook lúc chạy | giá server, A/B, giá IAP thật | tuần |
| 5 | Playtest | cảm giác cuối — **luôn** phải tự làm | liên tục |

> Bước 2 là bước **chưa ai làm** và nhiều khả năng cho giá trị nhất: 4.861 field, tất cả đã nằm trong
> bundle, chỉ cần đổi công cụ export.

---

## 7. Còn thiếu / phải đoán

Chỉ liệt kê cái **thật sự** chưa có đường lấy:

| # | Thứ | Vì sao vẫn thiếu |
|---:|---|---|
| 1 | **Giá trị số cụ thể** trong `.cctor` | cần chạy Ghidra; hiện chỉ có **tên + kiểu** của 259 field |
| 2 | **Giá trị `[SerializeField]`** | cần chạy AssetRipper; hiện chỉ có **tên + kiểu** của 4.861 field |
| 3 | Giá IAP / doanh thu thật | nằm trên **server**, không có trong APK |
| 4 | Nội dung enemy trong wave | `waves.json` để `"?"` — cần resolve `m_PathID` (`ENCOUNTERS.md` §9) |
| 5 | Cảm giác "đã tay" | không có trong bất kỳ file nào — **phải chơi** |

> Ghi chú: #1 và #2 **không phải "không thể"**, mà là **"chưa chạy công cụ"**. Phần lớn còn lại
> của game đã có tên biến, kiểu dữ liệu và vị trí — tức **đã biết phải tìm gì**.
>
> **Nhưng chưa biết tìm được bao nhiêu:** biết tên field **không** bảo đảm đọc được giá trị
> (có thể bị strip, có thể chỉ là giá trị mặc định). Con số thật chỉ có sau khi chạy.
