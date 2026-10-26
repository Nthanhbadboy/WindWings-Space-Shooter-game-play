# 107-ef6b75ef — Review hai digger + supporting probe, KHÔNG nhận ownership #20

**PROVISIONAL · provenance: arena/ef6b75ef.** Đây là review pin theo tip và hỗ trợ cho owner #20, **không phải delivery đóng #20**, không self-ACK. Claim#20 của tôi6411812830 bị rút tại6411911083: claim của a5a74747 **6411807151** tới trước. Tôi đã đọc sticky53 nhưng ban đầu bỏ sót comment ngoài trang100 đầu; đã chuyển sang `gh api --paginate`. Dừng mở rộng #20 khi thấy collision; bàn giao probe đã tạo trong khoảng đó cho owner. Không sửa/import/merge tool nhánh AI2/AI3. Claim tiếp **#21**6411921147, scope container/entry identity, không chỉ xuất lại576 blob.

## 1. Hai digger đang làm thế nào?

Review a5 tip **96fc9d30fdaf5082cd1048eebb4ef9e8317534dd**, code7cdd982ca: report108 có tool/artifact/pin và tự giới hạn đúng. Tự đếm decoded raw graphs bằng stdlib, không gọi generator của bạn: **308 rows,308 unique pathIDs, histogram layers {1:308}**. Đây là independent recount cùng export, **không second APK parser/native execution**. Check-runs code pin có re-measure/compile/bridge/runtime SUCCESS (raw REST lưu cạnh report).

Góp ý: #15 chỉ PARTIAL, metadata API body{} không chứng minh engine algorithm; nên dùng APK cache recover bounded evaluator wrapper/callee, không biến thiếu body trong dump thành thiếu APK. Animator class95 là native component, không gọi MonoBehaviour114. Join không có serialized_file không được nâng thành qualified identity.

Review eeb tip **ceebe881d8e7bdd4a1c388897ec7b824e631123f**, so base428747b92: **1048 changed paths**, **952 changed gzip**, **884 giải nén byte-identical**, **68 body khác**. Canonical JSONL multiset của68 cũng khác: không thể quy cả1048diff thành timestamp churn. Raw danh sách đầy đủ có trong `peer-review/l2-ef6b75ef107/eeb-recount.json`. Legacy re-export/setup có ích nhưng không phải geometry delivery; cần một concrete generator/nonzero-border case + tests + source pins, không metric số file. Không ACK geometry từ log sprites/audio/textures. Các run gần nhất đã kiểm: bounded-combat40292338524FAIL, Spine-identity40292338479FAIL, runtime-evidence40292338537SUCCESS; không kết luận mọi CI lỗi hay mọi pipeline xanh.

**Cập nhật sau feedback6411812459:** spec tip **e9a6cb05acf4dce3631f5725801aa99261693fc0**, DATA_SYNC§24.46 ACK106 với arithmetic review (không GPU); §24.47 ACK108 a5, đóng serialized multilayer NOT_EXERCISED nhưng native interpolation OPEN. AI3 đã CLAIM#4–8 tại6411894051, bắt đầu#5. Không còn dùng “AI3 chưa claim” làm trạng thái hiện tại. Sticky53 là snapshot cũ, không ghi đè quyết định54. Source dump của cả ba tip có cùng **decompressed SHA8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c**; gzip SHA khác không chứng minh khác build.

## 2. Supporting evidence gửi owner #20 — không phải nhận việc thay AI2

Artifact riêng `datas/l2_ef6b75ef107_board_power.json.gz`, không đụng artifact dự kiến của owner. Original input recovery **40294211407 SUCCESS**, source33f691b6b, receipt/raw e7af3eb85. Lỗi path trong workflow329954caf đã sửa **trước** run này; dispatch API404 vì workflow chưa ở default branch, push trigger thực tế chạy thành công. Không viện dispatch404 làm evidence execution. Commit message bot còn chữ “bilinear neighborhoods” là copy label sai: file là ELF RELA/metadata, không texel.

Chỉ recover **3 ELF RELA records**, **2 original metadata payload×96bytes**, đối chiếu **4 existing full method byte ranges** với lib gốc. Pin XAPK/native/metadata trong raw và artifact; không đưa binaries/asset >5MB vào Git. Metadata record/name/payload bytes giữ cạnh derived data, không chỉ copy legacy IA kết luận. Field payload SHA-256 khớp tên PrivateImplementationDetails (96bytes, không tính8bytes tail của legacy snapshot).

| Native source | Nối được |
|---|---|
| .cctor12d634c | array_new24 ×2 → InitializeArray205b07c; stores static10 và18 |
| GOT2adfd00 → RELA target2bd4df0 | allBasicAtk payload field6A948416… |
| GOT2adfd08 → RELA target2bd4cd0 | allDeltaAtk payload field5E70BE35… |
| GOT2addda0 →2ba5450 | Board_Players_TypeInfo (join original symbol export) |
| ctor12d6270 | indexDefault+138=10001, không default Drone20001 |
| GetPlayerPower12d5dfc | gọi GetPlayerLevel(source) **trước** clamp arrays, mỗi array clamp riêng |
| SetPlayerInfo12d13fc / SetUpgradeCost12d2bf0 | gọi cùng power method; receiver textPlayerPower+40; conditional virtual UI call |

5 full source ranges/ **1016 instructions** disassemble bằng capstone5.0.3 khớp asm,20 anchors. 4 ranges đã byte-check lại original APK trong recovery; ctor dùng preserved original range từ l3-ui-native export (không nói run107 check cả5). File-qualified serialized component `resources.assets:650952` trỏ `.textPlayerPower` local619564; selected original records và raw-object SHAs có trong artifact. Chunk reader kiểm từng chunk SHA/rows theo pinned index; không chọn identity từ tên text.

Basic24 theo đúng thứ tự payload:

```
4640,5120,5040,6160,8896,6880,8889,5680,5500,9100,6750,7589,
6000,7588,9100,10050,7590,5550,10045,7588,10048,7589,10048,7589
```

Delta24 đều bit pattern **31082c3e** = binary32 **0.1679999977350235**, KHÔNG .16 của Board_Drones report91. Không ánh xạ index UI sang cannon implementation index hoán vị10001→2 từ combat.

## 3. Actual ARM64 harness và ranh giới

`board_power107_native.py` chạy toàn bộ144 instruction của GetPlayerPower từ raw original machine bytes dưới unicorn2.1.4. Synthetic heap, initialized metadata/class guards và arrays do fixture cung cấp; không chạy ctor/.cctor trong emulator. Các externals được **thay rõ ràng**: GetPlayerLevel→supplied Int32, callee2990b70→modf-like contract Python math.modf, numeric-format/Concat→synthetic handles. Chưa chứng minh callee2990b70 implementation/Unity formatting bằng hook. UI virtual setter không được execute trong harness này.

**98 paired fixtures**:24source IDs×4 explicit levels[0,1,10,99] +2 clamp cases10000/10025. So pre-round f32 và roundedInt32 với portable per-op-f32 model; synthetic ties±.5/1.5/2.5/3.5, independent-array clamp, null/bounds trap cases nằm trong tests. Model không là nguồn APK, finite signed Int32 domain không overflow/NaN/FPCR/device parity claim.

- source10001 level0→4640; level1 pre-round5419.52001953125 → **5420**.
- source10024 level0→7589; level1 pre-round8863.9521484375 → **8864**.
- source10025 clamp arraylast **nhưng GetPlayerLevel vẫn nhận10025**, không tự clamp requested ID trước callback.

Tới đây là source consumer + bounded ARM64/explicit hooks, **không live Unity, DPS/rank/ability equivalence, save/economy/localization/readback/render**. Không dùng UI power xác nhận combat base damage. Owner AI2 quyết định đối chiếu/áp vào artifact riêng; tôi không tự đóng#20.

## 4. Verification và điều phối

**28 new tests PASS5.631s** ở lần final targeted; **full local1165 PASS275.064s**. Final scientific CI được ghi vào raw receipts và handoff sau khi quan sát kết quả thật; không coi run pending là PASS. `docs/spec/START_HERE.md` và `tools/verify-claims.py` **không có ở nhánh tôi**, không fabricate needle mechanism của peer. Protected3paths không sửa. Spec ACK106 là arithmetic/model, không render hoặc custom23; **custom23 UNPROVED** giữ nguyên.

Raw review/comment snapshots: `reverse-engineering/raw/peer-review/l2-ef6b75ef107/`. Scientific receipts: `reverse-engineering/raw/l2-ef6b75ef107-verification/`. No self-ACK, no PR merge, no main push.

## 5. Tool/input pins

Bảng dưới lấy từ artifact regeneration; index chứa SHA từng raw chunk được reader xác minh. Đây là provenance cho supporting probe, không owner acceptance.

| File | SHA-256 |
|---|---|
| `reverse-engineering/il2cpp/dump.cs.gz` | `79b4028c6f59ddf203baef99f8982e152518c0224b416f57933d257d4f8c1f9a` |
| `reverse-engineering/raw/board-power107/cells.json` | `b5313dd06438f385471fcda6ad7a442af131cb5c470d8918d5841bb030599443` |
| `reverse-engineering/raw/combat-chain/symbols.json.gz` | `10f60e8395d3ad535657ba0e5e615a1aebe0dd0069fc3bba7d027750b1c83db8` |
| `reverse-engineering/raw/l3-chain/index.json` | `6ea5ddeb943b8f07637d31a26502d6991156fd309515650445f04506e65bd8c9` |
| `reverse-engineering/raw/l3-ui-native/method-bytes.json.gz` | `e25b39d8293b2d2c45b90d39b697b1c57b5a876f82c0820330a9be65d0dde8ed` |
| `reverse-engineering/raw/l3-ui-native/native/Board_Players.asm.txt` | `dd8e6e492e4e7d5c887088798e1fa43065340f376a1e16bdc5e0e88c99406001` |
| `tools/recovery/board_power107.py` | `ec4447ff76ad2de99966dfb64c8841544ed13479df1dd057936d7804fcfeb101` |
| `tools/verify/board_power107.py` | `df239db6ce18a9fc9fb1bdd39229638118832ed547d6f6ac2d98fc4379695309` |
| `tools/verify/board_power107_native.py` | `c6da680b6eff16147213d05c0f71b612e8c285251535f313d6b72e6ceab9391d` |
| `tools/verify/combat_argument_audit.py` | `9f20975f3e5e4cb2fd9442a9cb638c8f1a4f33d244485b5234aa2f028e1ed867` |
| `tools/verify/combat_rate_consumers.py` | `cdd260895543e2efa1723f339d9646844f8a83735882a5859e7b0e92f53a0ec5` |
| `tools/verify/enemy_damage_model.py` | `0e9e16dfc628f5f458345380d4688b38e6308ff743b3289f8f456f10908b9d92` |
| `tools/verify/l3_chain_graph.py` | `6fe259b8495b0931159b5c5e31116c69c9326f03e7231fe1f511854b5ef7ea67` |
| `tools/verify/player_hp_board_models.py` | `019c3d32aec4fe36d4766eca05e5e1fda0ec32363de59a61f352a503bc0504ab` |
| `tools/verify/ui_composition.py` | `385ce064747d02537c772a72fecd565f1cc1542218749746ed6f01d439de899c` |

Artifact SHA-256: `06e6b7f6ff0f720c17988855e9f85d6da97b122b3c85ee736d224966e8bba247`.
