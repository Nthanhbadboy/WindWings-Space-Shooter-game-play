# BOSS_ANIM_TIMELINE — script animation của boss, đo bằng **giây**

> **Đây là script, không phải cảm nhận.** Mỗi dòng dưới đây là một `AnimationEvent` **có thật** trong
> bundle: biết **clip nào**, **giây thứ mấy**, gọi **hàm C# nào**. Nguồn duy nhất:
> `reverse-engineering/raw/animation-audit/event-receivers.json.gz` (**795** event). Bản CSV phẳng:
> `datas/boss_anim_events.csv` (795 dòng, sinh bằng `tools/boss-anim-timeline.py --csv`).
>
> Mức: **A** cho số · **B** cho suy luận ngữ nghĩa (hàm nào làm gì — vẫn là **T2**).

---

## 1. Tổng quan — một câu: **795 event trên 34 prefab**

| Chỉ số | Số | Ghi chú |
|---|---:|---|
| Prefab có event clip | **34** | **33** `Boss-*` + **1** `CB-30040` (enemy thường) |
| Event | **795** | mọi event đều có `time` |
| Clip phân biệt | **97** | tên clip trùng nhau giữa các boss (`attack1`, `idle`, …) |
| Cặp (prefab, clip) | **269** | đơn vị để dựng 1 state animation |
| Tên hàm phân biệt | **130** | xem §2 |
| Boss **chưa** có event | **13/46** | 46 dòng `14-Data_Boss.csv` − 33 prefab có event |

> **34 prefab · 795 event · 97 clip · 269 cặp (prefab, clip) · 130 tên hàm**
>
> `CB-30040` có **2** event trong clip `Die`, **cùng mốc 1,5 s**, đều gọi `Attack` — bản ghi duy
> nhất ngoài `Boss-*`.
>
> ⚠️ **Hai phạm vi, đừng tráo:** *chỉ boss* = **129** tên hàm / **268** cặp (đúng như
> `ANIMATION_SCRIPT.md`) · *cả 34 prefab* = **130** / **269** (file này). Chênh đúng 1 dòng:
> `CB-30040` · `Die` · `Attack`. Hai event trùng thời điểm nghĩa là **gây damage 2 lần** nếu port thẳng.

**Chia theo loại hàm:** **534** event là **state** (`OnStartAttack`, `OnAnimationEndedEvent`,
`OnStateExit`, `OnStopAttack`, …) · **215** là **đòn** (`AttackHand*`, `Shoot`, `Knife*`, `Banplasma`, …)
· **46** còn lại là tên riêng (`AttackBigBullet`, `EndShoot`, …).

⇒ Animation của boss **chủ yếu là máy trạng thái** (67 %), chỉ **27 %** event là "gây sát thương".
Điều này khớp với `ANIMATION.md`: code Unity không tự biết đòn trúng lúc nào — **clip nói**, qua event.

---

## 2. Mười hàm được gọi nhiều nhất

| Hàm | Số lần | Vai trò suy ra (mức B) |
|---|---:|---|
| `OnStartAttack` | **146** | mở cửa sổ tấn công (bật hitbox / cho phép bắn) |
| `OnAnimationEndedEvent` | **137** | kết thúc clip → trả state về idle, chọn đòn kế |
| `OnStateExit` | **56** | thoát state (dọn đạn, tắt FX) |
| `OnStopAttack` | **50** | đóng cửa sổ tấn công |
| `Shoot` | **31** | bắn 1 phát (súng gắn xương) |
| `OnAttackEnded` | **30** | hết chuỗi đòn (khác `OnAnimationEndedEvent`: đòn xong, clip có thể còn) |
| `AttackHandLeft` / `AttackHandRight` | **19** / **19** | vung tay trái/phải |
| `Attack1HandLeft` | **17** | vung tay theo *bộ đòn 1* |
| `EndShoot` | **13** | tắt trạng thái bắn liên thanh |
| `ShootOut` | **12** | nhả đạn ra khỏi nòng |

Ba hàm **state** (`OnStartAttack`, `OnAnimationEndedEvent`, `OnStateExit`) cộng lại **339/795 = 43 %**.
Nghĩa là: dựng lại boss **chỉ cần 3 callback này đúng** thì 43 % event đã chạy đúng chỗ.

---

## 3. Mười boss nhiều event nhất — chuỗi đòn và mốc thời gian

Cột cuối là **thời điểm (giây)** của các event trong clip, theo đúng thứ tự phát. Đây là thứ để dựng
lại **nhịp** của boss, không phải để copy số.

| Boss | Event | Clip | Mốc cuối | Chuỗi đòn (thời điểm giây) |
|---|---:|---:|---:|---|
| `Boss-39012` | 78 | 18 | 9s | `attack11` 0.33<br>`attack12.1` 0.33<br>`attack1` 0.37·0.65·0.93·1.22·1.5·1.77<br>`attack8` 0.6·4.77·5<br>`attack9` 0.63·3.3·4.48<br>`Chuyensangdot2` 0.67<br>`attack2` 0.75·0.92·1.08·1.25·1.42·1.58<br>`attack3` 0.75·0.92·1.08·1.25·1.42·1.58<br>`attack10` 0.82·1.2·1.98·2.37·3.27·3.65<br>`attack7` 0.97·4.8·6.12<br>`idle1` 1<br>`attack5` 2.5·2.83·3.17·3.83·4.17·4.5<br>`attack6` 2.5·2.83·3.17·3.83·4.17·4.5<br>`Die` 2.5<br>`attack12` 2.5<br>`Xuathien` 3<br>`Chuyensangdotcuoi` 6.5<br>`attack4` 9 |
| `Boss-39019` | 76 | 15 | 20s | `idle3` 0.5·1·2.02·3.52·5·6.5<br>`attack5` 0.5·6·10<br>`attack4` 0.92·8.53·10<br>`idle` 1·3·4·5.53·7·8.52<br>`attack2` 1·1.5·5.5<br>`attack6` 1·2.5·3.48·4.5·8.02·9.02<br>`idle2` 1.02·2.02·2.85·4.18·4.52·5.18<br>`attack1` 1.53·2·3·4.52·5.5<br>`attack7` 2.05·3.85·4.88·6·10<br>`attack3` 2.48·3.33·4.48·6.13·7.5·8.33<br>`chuyen sang dot 2` 4<br>`chuyen sang dot 3` 4<br>`attack8` 5<br>`appear` 5.5<br>`dead` 5.5 |
| `Boss-39020` | 75 | 12 | 13.32s | `idle1` 0.17·0.17·1·1·2·2<br>`idle2` 0.17·0.5·3·3.52·6·6.5<br>`attack4` 0.98·2.03·6.03·8.02·9<br>`attack3` 1·3.5·3.83·4.33·4.67·5.17<br>`idle3` 1.03·2.07·6·7.52·10<br>`attack2` 2·9<br>`attack6` 2.03·4.98·8.5·10<br>`attack1` 2.58·3.5·8.02·8.88·13.32<br>`attack5` 3.02·8·8<br>`dead` 4<br>`xuat hien` 6<br>`chuyen sang dot 2` 6.67 |
| `Boss-39021` | 75 | 13 | 40.67s | `attack1` 0·5.03·10.03·15.05·20.03·25.03<br>`idle` 0.35·1.37·2.5·3·5.5·6.02<br>`attack2` 0.5·1.03·3.05·5.08·7.5<br>`attack3` 0.5·1.5·1.67·2·2.17·5<br>`idle3` 0.5·3·5.52·8·9.5<br>`attack6` 1·14.5·15<br>`attack4` 1.02·7.03·8<br>`idle2` 1.03·2.98·4.02·7.02·8.05·11<br>`attack5` 3.33·7.5·8<br>`chuyen sang dot 2` 4<br>`dead` 4<br>`xuat hien` 7.5<br>`attack4.1` 8 |
| `Boss-39015` | 58 | 23 | 8s | `attack12` 0.5·1.32<br>`idle3` 0.5·1·1.5·2·2.5<br>`attack1` 0.67·1.97·2.9·3.83·4.75·5.67<br>`attack6` 0.67·4.67·5<br>`attack10` 0.67·2.05·2.42<br>`attack9` 0.75·2.13<br>`attack3` 0.78·1.17<br>`attack5` 0.78·1.27·1.63<br>`attack7` 0.78·1.17<br>`attack14` 0.78·2.38<br>`attack4` 0.8·1.17<br>`attack9.2` 0.83·1.8<br>`idle` 1<br>`attack2` 1·2.5·3<br>`idle2` 1<br>`attack8` 1·2.5·3<br>`attack11` 1·4<br>`attack13` 1·2.5·2.75<br>`attack15` 1.58·2.68<br>`attack16` 1.58·2.07·2.87<br>`Chuyensangdot3` 2.17·3.9<br>`dead` 2.32<br>`Chuyensangdot2` 2.85 |
| `Boss-39011` | 48 | 23 | 10.37s | `Attack2` 0.25·1.07·1.15·2.07·2.15·3.07<br>`Attack3` 0.45<br>`Attack5` 0.45<br>`Attack4` 0.47<br>`Mix` 0.5<br>`attack3` 0.58·2.5·3.07<br>`Attack6` 0.68·1.68·2.68·3<br>`Attack1` 0.83·1.63·2.68·4.13<br>`attack` 0.83·10.37<br>`attack1` 1·1.67<br>`attack2` 1·1.67<br>`attack2-2` 1·1.67<br>`attack1-1` 1·1.67<br>`chuyensangattack1` 1<br>`attack3-2` 1·1.67<br>`attack3-3` 1·1.67<br>`Die1` 1.33<br>`chuyensangattack3` 1.67<br>`Xuathien` 1.92·7.5<br>`chuyensangattack2` 2.02<br>`xuathien` 2.17<br>`Xuathien2` 2.97<br>`Die` 3.17 |
| `Boss-39017` | 42 | 16 | 17.53s | `attack2` 0.42·0.92·1.42·1.92·2.42·2.6<br>`Idle3` 0.5·0.58·1·1.08·1.5·1.58<br>`attack1` 0.6·0.93·1.27·1.6·1.93·2.27<br>`attack3` 0.75·10.5<br>`attack3-2` 0.75<br>`Chuyensangdot3` 1.42<br>`Idle2` 1.5·5.02<br>`Attack1` 1.58·2.25·5.9·8.57·12.07<br>`Chuyensangdot2` 3.52<br>`IdleMix2` 5.02<br>`attack5` 10.48<br>`attack8` 10.5<br>`attack6` 12.88<br>`attack7` 15.17<br>`attack9` 16.48<br>`attack4` 17.53 |
| `Boss-39003` | 36 | 3 | 1s | `Shoot` 0.05·0.05·0.05·0.05·0.05·0.05<br>`Launch` 0.5·0.5·0.5·0.5·0.5·0.5<br>`Attack` 0.83·0.83·0.83·0.83·0.83·0.83 |
| `Boss-39018` | 34 | 12 | 22.67s | `attack6` 0.43·1.77·3.1·6.6·8<br>`idle` 0.5·5.33<br>`attack5` 0.5·1.42·2.33·2.83<br>`attack7` 0.5·5.83·6.15<br>`attack9` 0.5·7·8.3<br>`Death` 2.35<br>`attack1` 2.48·2.98·6.25·6.67·10.28·13.72<br>`attack4` 2.83<br>`attack8` 4.25<br>`Xuathien` 5.82<br>`attack2` 8.5<br>`attack3` 10.8 |
| `Boss-39014` | 27 | 16 | 5.63s | `attack1` 0.45·0.81·1.31·1.67<br>`attack2` 0.45·0.81·1.31·1.67<br>`attack4` 0.58·1<br>`attack3` 0.6·1<br>`idle2` 0.67<br>`attack6` 0.78·1.17<br>`attack9` 0.83·1.83·2.25<br>`idle` 0.88<br>`idle3` 1<br>`xuathien` 1<br>`chuyensangdot2` 2<br>`attack10` 2<br>`chuyensangdot3` 2.5<br>`Die` 2.68<br>`attack7` 4.58<br>`attack8` 5.63 |
> Đọc bảng: `attack1` của `Boss-39012` có 8 event — 7 lần vung tay **cách nhau 0,28 s**, rồi
> `OnAnimationEndedEvent` ở **2,33 s**. Tức **một đòn 8 nhịp trong 2,33 giây**, không phải 1 đòn.

---

## 4. Ba boss chi tiết đầy đủ (mọi clip, mọi mốc)

Đây là **toàn bộ** script animation của 3 boss nhiều event nhất (78 + 76 + 75 = **229/795 = 29 %** dữ liệu).
Ba boss này đủ để thấy **khuôn**: `Xuathien`/`appear` → `idle*` → `attack1..12` → `Chuyensangdot*` → `Die`/`dead`.

### `Boss-39012` — 78 event · 18 clip

| Clip | # | Timeline (`giây` → hàm) |
|---|---:|---|
| `attack11` | 1 | `0.33` OnAnimationEndedEvent |
| `attack12.1` | 1 | `0.33` OnAnimationEndedEvent |
| `attack1` | 8 | `0.37` AttackHand1Left · `0.65` AttackHand1Right · `0.93` AttackHand1Left · `1.22` AttackHand1Right · `1.5` AttackHand1Left · `1.77` AttackHand1Right · `2.05` AttackHand1Left · `2.33` OnAnimationEndedEvent |
| `attack8` | 3 | `0.6` StartAttack8 · `4.77` StopAttack8 · `5` OnAnimationEndedEvent |
| `attack9` | 3 | `0.63` StartAttack9 · `3.3` StopAttack9 · `4.48` OnAnimationEndedEvent |
| `Chuyensangdot2` | 1 | `0.67` OnAnimationEndedEvent |
| `attack2` | 9 | `0.75` AttackHandLeft · `0.92` AttackHandLeft · `1.08` AttackHandLeft · `1.25` AttackHandLeft · `1.42` AttackHandLeft · `1.58` AttackHandLeft · `1.75` AttackHandLeft · `1.92` AttackHandLeft · `6.5` OnAnimationEndedEvent |
| `attack3` | 9 | `0.75` AttackHandRight · `0.92` AttackHandRight · `1.08` AttackHandRight · `1.25` AttackHandRight · `1.42` AttackHandRight · `1.58` AttackHandRight · `1.75` AttackHandRight · `1.92` AttackHandRight · `6.5` OnAnimationEndedEvent |
| `attack10` | 8 | `0.82` KnifeLeft · `1.2` KnifeRight · `1.98` KnifeLeft · `2.37` KnifeRight · `3.27` KnifeLeft · `3.65` KnifeRight · `4.52` AttackCircle · `5.85` OnAnimationEndedEvent |
| `attack7` | 3 | `0.97` On2HandStartAttack · `4.8` On2HandStopAttack · `6.12` OnAnimationEndedEvent |
| `idle1` | 1 | `1` OnAnimationEndedEvent |
| `attack5` | 13 | `2.5` AttackHand5Left · `2.83` AttackHand5Left · `3.17` AttackHand5Left · `3.83` AttackHand5Left · `4.17` AttackHand5Left · `4.5` AttackHand5Left · `5.17` AttackHand5Left · `5.5` AttackHand5Left · `5.83` AttackHand5Left · `6.5` AttackHand5Left · `6.83` AttackHand5Left · `7.17` AttackHand5Left · `8` OnAnimationEndedEvent |
| `attack6` | 13 | `2.5` AttackHand5Right · `2.83` AttackHand5Right · `3.17` AttackHand5Right · `3.83` AttackHand5Right · `4.17` AttackHand5Right · `4.5` AttackHand5Right · `5.17` AttackHand5Right · `5.5` AttackHand5Right · `5.83` AttackHand5Right · `6.5` AttackHand5Right · `6.83` AttackHand5Right · `7.17` AttackHand5Right · `8` OnAnimationEndedEvent |
| `Die` | 1 | `2.5` OnAnimationEndedEvent |
| `attack12` | 1 | `2.5` OnAnimationEndedEvent |
| `Xuathien` | 1 | `3` OnAnimationEndedEvent |
| `Chuyensangdotcuoi` | 1 | `6.5` OnAnimationEndedEvent |
| `attack4` | 1 | `9` OnAnimationEndedEvent |

### `Boss-39019` — 76 event · 15 clip

| Clip | # | Timeline (`giây` → hàm) |
|---|---:|---|
| `idle3` | 10 | `0.5` OnStartAttack · `1` OnStartAttack · `2.02` OnStartAttack · `3.52` OnStartAttack · `5` OnStartAttack · `6.5` OnStartAttack · `8.02` OnStartAttack · `9` OnStopAttack · `9.5` OnStartAttack · `10` OnStateExit |
| `attack5` | 3 | `0.5` OnStartAttack · `6` OnStartAttack · `10` OnStateExit |
| `attack4` | 3 | `0.92` OnStartAttack · `8.53` OnStopAttack · `10` OnStateExit |
| `idle` | 7 | `1` OnStartAttack · `3` OnStartAttack · `4` OnStartAttack · `5.53` OnStartAttack · `7` OnStartAttack · `8.52` OnStartAttack · `10` OnStateExit |
| `attack2` | 3 | `1` OnStartAttack · `1.5` OnStartAttack · `5.5` OnStateExit |
| `attack6` | 7 | `1` OnStartAttack · `2.5` OnStartAttack · `3.48` OnStartAttack · `4.5` OnStartAttack · `8.02` OnStartAttack · `9.02` OnStartAttack · `10` OnStateExit |
| `idle2` | 11 | `1.02` OnStartAttack · `2.02` OnStopAttack · `2.85` OnStartAttack · `4.18` OnStartAttack · `4.52` OnStopAttack · `5.18` OnStopAttack · `6.47` OnStartAttack · `7.5` OnStartAttack · `8.02` OnStopAttack · `8.5` OnStopAttack · `10` OnStateExit |
| `attack1` | 5 | `1.53` OnStartAttack · `2` OnStartAttack · `3` OnStartAttack · `4.52` OnStartAttack · `5.5` OnStateExit |
| `attack7` | 5 | `2.05` OnStartAttack · `3.85` OnStartAttack · `4.88` OnStartAttack · `6` OnStartAttack · `10` OnStateExit |
| `attack3` | 17 | `2.48` OnStartAttack · `3.33` OnStartAttack · `4.48` OnStopAttack · `6.13` OnStartAttack · `7.5` OnStartAttack · `8.33` OnStartAttack · `9.5` OnStopAttack · `11.32` OnStartAttack · `12.32` OnStartAttack · `13.05` OnStartAttack · `14.32` OnStopAttack · `15.93` OnStartAttack · `16.98` OnStartAttack · `17.77` OnStartAttack · `18.98` OnStopAttack · `19.88` OnStartAttack · `20` OnStateExit |
| `chuyen sang dot 2` | 1 | `4` OnStateExit |
| `chuyen sang dot 3` | 1 | `4` OnStateExit |
| `attack8` | 1 | `5` OnStateExit |
| `appear` | 1 | `5.5` OnStateExit |
| `dead` | 1 | `5.5` OnStateExit |

### `Boss-39020` — 75 event · 12 clip

| Clip | # | Timeline (`giây` → hàm) |
|---|---:|---|
| `idle1` | 24 | `0.17` OnStartAttack · `0.17` OnStartAttack · `1` OnStopAttack · `1` OnStopAttack · `2` OnStartAttack · `2` OnStartAttack · `3` OnStartAttack · `3` OnStartAttack · `3.83` OnStopAttack · `3.83` OnStopAttack · `5.33` OnStartAttack · `5.33` OnStartAttack · `6.13` OnStartAttack · `6.13` OnStartAttack · `7.15` OnStartAttack · `7.15` OnStartAttack · `8.17` OnStartAttack · `8.17` OnStartAttack · `8.83` OnStopAttack · `8.83` OnStopAttack · `9` OnStopAttack · `9` OnStopAttack · `10` OnStateExit · `10` OnStateExit |
| `idle2` | 8 | `0.17` OnStartAttack · `0.5` OnStartAttack · `3` OnStartAttack · `3.52` OnStartAttack · `6` OnStartAttack · `6.5` OnStartAttack · `7.62` OnStartAttack · `10` OnStateExit |
| `attack4` | 5 | `0.98` OnStartAttack · `2.03` OnStartAttack · `6.03` OnStartAttack · `8.02` OnStopAttack · `9` OnStateExit |
| `attack3` | 16 | `1` OnStartAttack · `3.5` OnStartAttack · `3.83` OnStopAttack · `4.33` OnStartAttack · `4.67` OnStopAttack · `5.17` OnStartAttack · `5.5` OnStopAttack · `6.5` OnStartAttack · `8.5` OnStartAttack · `8.83` OnStopAttack · `9.33` OnStartAttack · `9.67` OnStopAttack · `10.17` OnStartAttack · `10.5` OnStopAttack · `11.68` OnStartAttack · `13.32` OnStateExit |
| `idle3` | 5 | `1.03` OnStartAttack · `2.07` OnStartAttack · `6` OnStartAttack · `7.52` OnStartAttack · `10` OnStateExit |
| `attack2` | 2 | `2` OnStartAttack · `9` OnStateExit |
| `attack6` | 4 | `2.03` OnStartAttack · `4.98` OnStartAttack · `8.5` OnStartAttack · `10` OnStateExit |
| `attack1` | 5 | `2.58` OnStartAttack · `3.5` OnStartAttack · `8.02` OnStartAttack · `8.88` OnStartAttack · `13.32` OnStateExit |
| `attack5` | 3 | `3.02` OnStartAttack · `8` OnStateExit · `8` OnStopAttack |
| `dead` | 1 | `4` OnStateExit |
| `xuat hien` | 1 | `6` OnStateExit |
| `chuyen sang dot 2` | 1 | `6.67` OnStateExit |

---

## 5. Đọc ra **luật** gì (mức B — đừng đóng đinh)

| Luật | Số đo | Cách dùng khi dựng lại |
|---|---:|---|
| **Nhịp multi-hit** | **93** khoảng, trung vị **0,17 s** | đòn liên hoàn ~6 hit/giây; muốn "nặng" thì tăng damage/hit, **không** tăng số hit |
| **Cửa sổ gây sát thương** | chỉ **2** cặp `StartX`→`StopX`: **4,17 s** (attack8) và **2,67 s** (attack9) | hầu hết boss **không** có cửa sổ dài; damage nằm ngay tại event đòn |
| **Mốc cuối clip** | trung vị **3,52 s**, dài nhất **73,17 s** (`Lite_Appear` của `Boss-39006`/`39010`) | clip `Appear` rất dài: đừng chờ nó xong mới cho player bắn |
| **Số clip / boss** | **1–23**, trung vị **6** | một boss cần ~6 state animation, không phải 30 |
| **Phân bố event** | 3 boss đầu chiếm **29 %** | đừng lấy `Boss-39012` làm khuôn cho *mọi* boss |

**Cảnh báo:** `Lite_Appear` 73 s là **clip chờ**, không phải clip hoạt ảnh — event cuối nằm ở 73,17 s
nhưng boss vẫn đứng yên. Nếu dựng lại đúng số này, boss sẽ "đứng im 73 giây". Đây là chỗ **phải làm
khác** bản gốc (dùng `StartHp`/`WaitForSeconds` đã có trong `BOSSES.md`).

---

## 6. Còn thiếu gì (nối vào T2)

| Thiếu | Chặn? | Ai làm |
|---|---|---|
| **Thân 130 hàm** làm gì (damage bao nhiêu, hitbox nào) | không — nhưng quyết định **cảm giác** | **T2** — nhánh dữ liệu (hero `Boss1_AnimationEvents`, 12 handler) |
| **13/46 boss** không có event clip | không | nhánh dữ liệu (có thể là boss dùng Spine — xem `38-spine-prefab-links.md`) |
| Clip → **file animation** nào (bake vào prefab) | không | đã có: `datas/anim_clips.json.gz` + `datas/animator_map.csv.gz` |

---

## 7. Chạy lại

```bash
python3 tools/boss-anim-timeline.py --stats
python3 tools/boss-anim-timeline.py --prefab Boss-39012                 # mọi clip
python3 tools/boss-anim-timeline.py --prefab Boss-39012 --clip attack1  # 1 clip
python3 tools/boss-anim-timeline.py --doc Boss-39012 Boss-39019         # bảng markdown
python3 tools/boss-anim-timeline.py --detail Boss-39012                 # bảng chi tiết
python3 tools/boss-anim-timeline.py --csv datas/boss_anim_events.csv    # 795 dòng phẳng
python3 tools/verify-claims.py --only R                                 # 6 claim neo số trong file này
```
