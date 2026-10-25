# 86 — Review spec b8f72a412 + nối callback hồi sinh/heal

**Tạm thời.** Snapshot tài liệu peer là chứng cứ *peer đã viết gì*, không phải APK.
Nguồn gameplay vẫn native/metadata/ELF của cùng APK. Không merge/switch nhánh.

## 1. Đã cập nhật/kiểm tra bên kia

Fetch nhánh `arena/20330d0e-windwings-space-shooter-game-p`, tip chính xác
**b8f72a4127dbc2e7a24f8ff212172eb2f6eeb2ef**. Giữ snapshot 10 tài liệu + SHA
ở `raw/peer-review/review-b8f72a412.json.gz`. Đọc cả mục tổng kết, không chỉ changelog.
Peer **đã ACK report84** trên PR12; nhận đúng các correction7/9,17,18 và bind
combat implN→indexN−1. **Chưa có ACK report85** tại lần kiểm tra này.

### Các finding cần sửa, không đánh đồng với thiếu đồng bộ

| Ưu tiên | Vị trí ở tip peer | Vấn đề và sửa cụ thể |
|---|---|---|
| P1 | DATA_SYNC.md **2723–2725**, §24.17 | Ghi `11/13 = shotRate/number clamp .05`: **chỉ13.ShotAllBarrels** có công thức đó. **11** dùng descriptor rate=f32(.04), thời lượng theo rank rồi kiểm deadline. Chép riêng hai recipe report84; không gộp vì đều có wait. |
| P1 | DATA_SYNC.md **2724–2725** | `clone impl9 stop→wait .35→delay→về owner→pool` gộp **ControlMainCannonBullet của9** với **Player9_Clone**. Clone controller: StopAttack→cleanup wait **f32(.34)**→pool; projectile7/9: outbound arrival .1→wait.35→optional delay→return≤.5→pool+ended. SYSTEM_MANIFEST ghi clone .34 đúng nhưng DATA_SYNC lại khác. |
| P1 | COMBAT.md **355–365**, **§0 TL;DR**; BALANCE.md §1.1b | `damage × rate` khi rate là **interval** có đơn vị damage·seconds, không phải damage/seconds. Dán nhãn “proxy” không biến nó thành ước lượng TTK có ý nghĩa. Xóa việc dùng tích này để xếp tàu/tính TTK. Bảng HP/DPS **giả định do designer đặt** được giữ nếu nhãn rõ; cũng không tự thay bằng damage/rate rồi gọi DPS thật vì còn extra/nòng/hit/gates. |
| P1 | COMBAT.md **416–432**, §6.4 | Còn bảng800/189 trong khi đầu file đã sửa981/241; “noDamage không phải invulnerable, chỉ trang trí” và khuyên bỏ enemy không thể giết là vượt chứng cứ. Native gate thật: noDamage && !ignoreInvincible skip CalculateDamage; ignore có thể bypass. Không suy role trang trí/không-target từ thống kê root. Giữ scoped counts, chưa chứng minh dynamic assignments bằng snapshot. |
| P2 | COMBAT.md **490–500**, BALANCE.md **118**, **705–709**, UNITY_RULES.md §12 | Các mục “còn thiếu” vẫn xin damage/HP/asm đã có; còn phỏng đoán formula và khẳng định HP JSON chỉ đúng boss. Đánh dấu **superseded** ngay cạnh đoạn cũ hoặc thay worklist hiện hành bằng reports81–85. Không chỉ append correction ở cuối file rồi để cửa vào giao task sai. |
| P2 | START_HERE.md **7–12**, **83–85** vs SYSTEM_MANIFEST và VISUAL_DESIGN §5 | “Mọi logic/số/nhịp tra là có hết”, “input L3 đã đủ” là claim coverage, không suy được từ mục tiêu bắt chước. SYSTEM_MANIFEST tự ghi scoped unknown, boss transitions C, assets chưa import/render approval; VISUAL_DESIGN đúng khi coi metrics là **cổng phát hiện lệch**, không chứng nhận đẹp. Giữ mục tiêu bám bản gốc và art vẽ lại, bỏ cam kết không cần kiểm chứng. Không yêu cầu blind A/B hay playtest người thật; automated regression/render/reference checks vẫn cần. |

**Nhận report85 để bổ sung:** player hai truncations, events21/39 đồng bộ trước
HP reread; enemy cả hai callbacks/ref capture; Delayed=WaitUntil không phải2s;
MB ba Wait1 không base Pool; ability32 recursive requests không dedup. Đây là
**chưa đồng bộ report mới**, không quy thành peer cố ý dịch sai những body chưa nhận.

### Khối “mục đích” peer yêu cầu

Đã đồng bộ định hướng bám logic/nhịp/số bản gốc, chỉ art vẽ mới, không tự thêm
cơ chế và không hỏi lại quyết định đã có. **Không chép nguyên câu** “mọi dữ liệu
đã có/không test”: đó là lời tuyên bố coverage và nghiệm thu, không phải APK fact.
Chưa có raw → ghi scoped unknown và tiếp tục bóc, không lấy mục đích sản phẩm
để nâng giả định thành bằng chứng. Kiểm máy không đồng nghĩa phải có người playtest.

## 2. Việc tiếp đã làm: producer callback được chốt bằng RELA

Không đoán binding theo tên hàm. Recovery nhỏ **40211002716 SUCCESS**, raw
**2738ad848**: 7 exact cells, 3 ELF RELA records; dùng **đủ ScriptMetadataMethod**
đã giữ trong symbols.json.gz, không cần chạy lại Dumper/Analyze/media.

| Site / field | GOT → effective metadata usage | Method thật |
|---|---|---|
| Player_Controller.Start **14c20b4** ghi Health.onExtraLife@40 | 2ae8480→**2bc83d0** | **OnExtralife 14c42d4** |
| Start **14c2074** ghi Health.destroyShieldOneHit@38 | 2ae8418→**2bc8020** | **Player_Ability.DestroyShieldOneHit 1471884** |
| normal extra-life WaitUntil delegate | 2ae85a8→**2bc8350** | **<DoExtraLife>b__62_0 14c52e4** → noTouch14c4690 |

Start dùng **STR gán trực tiếp**, không Delegate.Combine ở hai site trên. Không
khẳng định callback bất biến suốt đời; reassignment sau Start vẫn có thể đổi field.
`datas/player_lifecycle_flow.json`: bindings, 43 native anchors, 4 binary32 literals,
SHA input. Script check `python3 -m tools.verify.player_lifecycle_flow --check`.

## 3. Extra-life: HP=1 trước, normal/PVP khác nhau

OnExtralife: mode6→DoExtraLifePVP; còn lại StartCoroutine DoExtraLife.

**Normal, state0:** prepare animation .3 → GainHealth(**1**, hasFx=false) →
Invincible=true → movement disabled/particles stopped/UI flags → schedule Invoke
→ Time.timeScale=**0**, bool pair store0x0101 → effect90066 → **WaitUntil(noTouch)**.
noTouch kiểm cả mouse-up→down→held button0 và touchCount==0, short-circuit.
State1: effect90031 → Time.timeScale=**f32(.05)** (không phải1) →
StartCoroutine HealHp(**.5**) → clear bool pair → finish.

**PVP:** event86 **OnExtraLife trước GainHealth(1)** → Invincible=true/move disabled
→ schedule Invoke → effect90031 → StartCoroutine HealHp(**1**). Body không có
Time.timeScale=0 hay WaitUntil. Không ép cơ chế chờ nhả touch của normal lên PVP.

Điều này nối report85 zeroHP→onExtraLife tới producer thật: với callback chuẩn
đã gán và dependencies trả về bình thường, hồi **1 HP sớm**, không hồi full ngay.
GainHealth phát thêm event21; callback của event này vẫn có thể sửa HP.
Không lấy fixture “callback null vẫn return” làm mô tả mặc định sau Start.

## 4. HealHp: stop theo accumulator, không theo current HP

Native MoveNext **14c6520**:

- Snapshot `target = f32(StartHealth * percent)`; `percent` là fraction **.5 hoặc1**.
- `perSecond = f32(f32(target / 100) / f32(.02))`.
- Local progress khởi tạo **1**, không0. Nếu progress>=target, finish luôn.
- Mỗi reached tick: nếu progress<target, `amount=f32(perSecond*deltaTime)`;
  progress+=amount; gọi GainHealth(amount,false); yield **null**, kể cả tick cuối.
- Resume đọc progress/target đã lưu; **không đọc currentHP để quyết định kết thúc**.
  MaxHP thay đổi không làm target tự cập nhật. deltaTime là scaled; 0 vẫn yield,
  gain0, không progress. Không tự thêm fixed20ms timer/catch-up hay fullHP snap cuối.
- Target có thể overshoot theo frame. **Không tuyên bố đúng2 giây runtime**:
  phụ thuộc deltaTime, progress bắt đầu1, timeScale .05 và scheduler/Invoke khác.

GainHealth **14c63b4** = min(currentHP+amount, live StartHealth), chỉ upper clamp;
negative gain có thể HP<0. Optional FX trước khi reload HP để box event21. Khác
TakeDamage path có max(HP-damage,0), không dùng chung một clamp cho hai hàm.

**Zone-heal iterator** là chuỗi khác: **Wait f32(.2) trước lần heal đầu**, rồi
GainHealth(`live StartHealth * f32(.01235)`, true), lặp. Exact cell **756b7c =
a8574a3c**, không làm tròn thành1% hay1.25%. Đọc maxHP live mỗi resume.

## 5. Kiểm thử, ranh giới còn lại và bước tiếp

`tools/verify/player_lifecycle_models.py` có HP/extra-life/HealHp/zone fixtures;
`tests/test_player_lifecycle_flow.py` nối cả zeroHP receiver85→concrete extra-life
callback→HP1 và event21 mới. Model không giả lập Unity clock/Invoke/input/physics.

**Còn việc cụ thể**, không phải thiếu toàn bộ raw: decode **Invoke string GOT2ae8560**
và state flags quanh RebornDone/Reborning, join những scene/runtime writes ảnh hưởng
end-of-invincibility; enemy hitCallback/hitDamageCallback producers vẫn riêng. Không
đoán Invoke target=RebornDone chỉ vì có hàm cùng chủ đề, hoặc tự nói invincible2s.
Raw của Player_Controller và RebornDone **đã có**, không xin full export lại.

**394 tests PASS (34.624s local), validate/regen/diff checks PASS;19 tests mới.**
Receipt tests/CI và artifact hashes ở `raw/player-lifecycle/derivation.json`.
