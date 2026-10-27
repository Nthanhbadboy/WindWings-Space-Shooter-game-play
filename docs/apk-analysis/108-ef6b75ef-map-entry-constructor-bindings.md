# 108-ef6b75ef — 576 InitializeArray sites → constructor field/index identity

**PROVISIONAL · provenance: arena/ef6b75ef.** Claim#21 **6411921147**. Artifact `datas/l2_ef6b75ef108_map_entry_bindings.json.gz`. Đây là **constructor container/index binding**, không 576 stage, không chapter/UI numbering hoặc measured gameplay. Không lấn #20 của AI2 hay geometry AI3; không self-ACK.

## 1. Nguồn và phát hiện mới

Đã mở lại pinned APK qua Actions cache và lấy **nguyên Map_Get_Datas.cctor:100896bytes =25224 ARM64 instructions**, disassemble so toàn range với preserved asm. **550 RELA candidates** nối được tới source symbol records. Không chỉ grep endpoint rồi lấy thứ tự `map_table_segments` làm bằng chứng.

Recovery cuối **40296913805 SUCCESS**, source92baacb84, raw15aa4b8bc. Trước đó40295237073SUCCESS có548 candidates. Khi chạy actual code, fixture lỗi unmapped read tại1406764, x25=0: bộ dò GOT bỏ sót decimal-offset `ldr x25,[x25,#8]` (chỉ nhận hex). Sửa parser và recover lại ORIGINAL ELF ra550. Không lấp pointer thiếu bằng giá trị đoán. Lần đầu40295033775FAIL do parser source audit thiếu dotted mnemonic/operand-free ret; đã giữ lịch sử, không gọi failed run là evidence. Failed log download EOF, không bịa đã thấy traceback của run đó.

Payload values lấy từ existing decoded `field-defaults.json`/`ia-resolved.json`, kiểm mỗi payload SHA với PrivateImplementationDetails field name. **Không phải second independent metadata/APK parser**: nguồn mới độc lập ở bước mở lại ELF/cctor/RELA; metadata exports vẫn dùng chung nguồn cũ. Input SHA đầy đủ bên dưới.

## 2. Chạy hai đường container khác nhau

`map_entries108_native.run` execute nguyên cctor bằng unicorn2.1.4. Fixture cấp synthetic heap, resolved metadata, class-init flags và explicit allocator/List/Dictionary hooks. Không execute nguyên implementation IL2CPP allocator/GC/List/Dictionary.

- **Capacity0**: source đi các nhánh resize/helper, gọi List.Add hook **773** lần.
- **Capacity1024**: source đi inline `_items/_size` stores, gọi List.Add hook **0** lần; `UC_HOOK_MEM_WRITE` ghi thứ tự item writes trực tiếp từ instruction nguồn.
- Normalize object identities bằng **allocation callsite**, không synthetic heap address. Toàn cây root/indices/values/initializers khớp **bit-for-bit giữa hai execution**.
- **69 newobj** =68list +1dictionary; **716 newarray** =715 static leaf instances +1 external-sized array; **576 InitializeArray** calls.
- **12 static field stores** được bắt từ actual instruction writes vào static block của `Map_Get_Datas_TypeInfo` (TypeInfo join bằng original RELA + symbol record), rồi nối offset với dump declarations. Không gán tên field theo order của segment heuristics.

Đây là differential source execution dưới **hai container contracts**, không hai engine/runtime implementations độc lập. Capacity0/1024 là fixture choices, không quan sát dung lượng List của game. Cả hai còn dùng chung payloads/metadata hooks; agreement không chứng minh native container implementation.

## 3. Root thật và 576 entry identities

Mỗi binding có `root`, zero-based `index_path`, `array_new_site`, `initializer.pc`, `initializer.field`, `length`, toàn bộ `values`. **576 unique initializer sites,576 reachable leaf identities**; không dùng content hash làm instance identity vì cùng blob có thể được cấp lại.

| Root field | Static offset | Root count | IA leaf instances |
|---|---:|---:|---:|
| listMapTryPlayerDatas | 0x0 |1|1|
| AllArenaStartMaps |0x8|10|63|
| AllArenaRandomMaps |0x10|10|20|
| AllPvPStartMaps |0x18|10|100|
| listMapDatas |0x28|250|243|
| listMapBranchDatas |0x30|4|52|
| listIdBosses |0x38|20 dictionary entries|0|
| listMapFightBossDatas |0x40|20|0|
| listMapChallangeDatas |0x48|4|41|
| listMapEndlessDatas |0x50|28|28|
| listMapObstacleDatas |0x58|29|28|
| mapChallangeIndexs |0x60|external-size array|0|

Tổng IA **1+63+20+100+243+52+41+28+28=576**. Ngoài IA có **139 literal-array instances +1 external-size zero-initialized array**; không trừ3 opening literals khỏi576. `listMapFightBossDatas` có array entries nhưng đều literal-built, không vì IA0 mà nói list rỗng.

**Campaign listMapDatas**: allocation1406bf0→x28 assignment1406bf8→static store **140e19c,offset28**,250zero-based entries. 243IA +7literal:

| Constructor index | Payload |
|---:|---|
|0|[25,9010]|
|1|[164]|
|2|[113,5]|
|3|[2,161]|
|249|[43,12,9024]|

So **toàn715 static leaf payloads** theo array-new callsite với `map_segments_full.json`:0 value/length mismatch. Đây kiểm lại values đã có, **không dùng candidate để tạo root/path**. Existing segment35 đúng bằng campaign ở scope này; không nhầm `segments[35]` là `index==35` (list position35 thực tế là segment40 vì index trống bị lọc).

**716 instances không phải thay số614 structural classification cũ:** đơn vị khác nhau. Legacy segment export chứa715 static array records + standalone unknown-size array; số576 chỉ riêng IA; trước khi so tiến độ phải ghi đúng mẫu/đơn vị.

## 4. Consumer route và chỗ vẫn mở

Đọc lại8 anchors trong `GetListWaves` tại **13feb84–13febb0**: load static28 chính `listMapDatas`, read list count, subtract1, signed min/max bằng CSEL, truyền index qua đường13feacc. Route này dùng **clamp(requested_mapIndex,0,count−1)** khi control tới block đó. Constructor tree vì vậy cung cấp identity rõ cho field mà route đọc.

Đây là **static consumer-source audit**, chưa execute full GetListWaves/mode dispatch/get_Item native implementation. Không tự gọi entry0 là màn/chapter/UI stage1, không giả định mọi mode đi cùng root. Các Arena/PvP/branch/challenge rows hiện được định danh bằng **field + zero-based nested indices**, không bịa semantic rank/mode/chapter labels.

`mapChallangeIndexs` length load từ **Board_Challange.NumberChallanges static+4**; classinit bên ngoài không execute trong fixture. Artifact ghi rõ **fixture external length0, không recovered APK default**. Test đổi length7: chỉ dynamic array thành7zeroes, tất cả576binding/roots còn lại không đổi. Không làm mất boundary này khi spec trích root table.

**Disposition xin review:** #21 constructor field/index identities cho576IA có artifact đầy đủ. Stage/chapter/mode semantic end-to-end và runtime consumer parity **không được đóng nhờ report này**. Không custom23/GPU/readback/render acceptance.

## 5. Review hai AI trong cùng vòng

Feedback PR12 **6412200891**, raw `peer-review/l2-ef6b75ef108/`:

- AI2 tip **f246e4bd621d26cc5193b011edb579640589c827**, report109:16anchors từ dump/asm/IA, hai payload SHA khớp original metadata probe107 (6a948416…/5e70be35…). Kết luận reader UI đúng nguồn, không từ tên field. Góp ý spec giữ APK identity-note từ PHAN_TICH là note, không raw APK validation; clamp riêng từngarray và level requestedID phải ghi đúng. **Re-measure documented numbers FAIL**, compile/bridge/preflight/ramusSUCCESS; spec c2db940f §24.48 đã nhắc RD1related, cần final successful CI trước gọi cả delivery xanh. Không bác đúng source conclusion vì lỗi docs nhưng không che red check.
- AI3 tip vẫn **ceebe881d8e7bdd4a1c388897ec7b824e631123f**, không commit geometry mới ở lần review này. Chỉ ghi CLAIMED/setup, không kết luận đào sai khi chưa có delivery. Nhắc #5nonzero-border5739 concrete generator+tests+pins, không bulk reexport làm acceptance.
- Cập nhật sau vòng đầu: AI2 **5ed3328f87ea3ef0c8319ed02bbd2305b4897e3d** /report110, spec **cf3d464b9032431b39240e13137557ab5a0a4790** §24.50. Source save/load bounded có căn cứ nhưng spec nói GetDevice “chỉ dump declaration” quá rộng: full200byte body12546d0 đã nằm trong own raw `pickup-currency/native/Device_Saved_Data.asm.txt` (khác Device_Get_Data), chưa có trên tip AI2. Đã gửi source pointer/pins tại **6412391042**, không bịa callee lookup semantics hay làm thay#22. RD1 vẫnFAIL tại tip mới; #23 đã AI2claim, tôi không làm.
- Spec pinned **c2db940f311125add5a74c3b250c3625a415f387** ở vòng đầu: first-claim #20 AI2; tôi #21. Không sửa tool của hai bạn hoặc3paths shared. Own START_HERE/verify-claims không có, không fabricate needle sync.

## 6. Verification

**25 new tests PASS5.787s**: regeneration/pins,576unique paths,root histogram,first3/campaign250/243+7,zero-based indices,actual field stores,773vs0helper paths,allocationcensus715+1,existing715payloaddifferential,dynamiclength0vs7,invalidfixtureparams,consumer8anchors,boundaries.

**Full local1190 PASS283.598s; final scientific Verify40298061301SUCCESS**, code **537e9024dfb9cd8eaac3fc9d6b2bf7fcafba40c2**. REST receipt đã assert head/conclusion;25targetedPASS5.787s. Local full trước final consumer audit đã dừng chủ động, không count làmPASS; chỉ final full được ghi nhận. Toolchain capstone5.0.3/unicorn2.1.4; deterministic gzip mtime0; không binary/media>5MB. Raw scientific receipts lưu `reverse-engineering/raw/l2-ef6b75ef108-verification/`.

## 7. Tool/input SHA pins

| File | SHA-256 |
|---|---|
| `datas/map_segments_full.json` | `1b6fe5a776419b1846e0ced64499f62e1408f9780edb46d84336410260298250` |
| `reverse-engineering/il2cpp/dump.cs.gz` | `79b4028c6f59ddf203baef99f8982e152518c0224b416f57933d257d4f8c1f9a` |
| `reverse-engineering/il2cpp/field-defaults.json` | `05a51c9bc32bd5f0c42ef4822e36f838dab931ec2213298a56d3aaf6e7be4d27` |
| `reverse-engineering/il2cpp/ia-resolved.json` | `2583a4c472400fe85f96b96f0a8d2839963eddae95760483424119501d989e37` |
| `reverse-engineering/raw/combat-chain/symbols.json.gz` | `10f60e8395d3ad535657ba0e5e615a1aebe0dd0069fc3bba7d027750b1c83db8` |
| `reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.asm.txt` | `a95539643a1d0a17e546c5fde41cf1a12a7230f934cc12a30807bcdf644edae6` |
| `reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.json` | `1b588f39932d2ffee3de214c76fa927fa58e6d4fddf70a8426dba95de7c5b249` |
| `reverse-engineering/raw/map-entries108/native.json.gz` | `34adfd2b15249381726a91617154a3ca5c2e8be089f54f0d46bfc307a2accc81` |
| `tools/recovery/combat_coroutine_cells.py` | `67802e1df85dd8e613fffe37f099fcc976ed099083ed05621ad3b24b62054760` |
| `tools/recovery/map_entries108.py` | `4e8755711ad4a4bb8d863a578b797cf2ab8b71b67a8b2a7d87d8509186c69780` |
| `tools/verify/combat_argument_audit.py` | `9f20975f3e5e4cb2fd9442a9cb638c8f1a4f33d244485b5234aa2f028e1ed867` |
| `tools/verify/combat_rate_consumers.py` | `cdd260895543e2efa1723f339d9646844f8a83735882a5859e7b0e92f53a0ec5` |
| `tools/verify/map_entries108.py` | `0c2905c5f481a6bd210d3b62980d7ef7fb99ddb1033a8ce7bdfc1a1f69b932d5` |
| `tools/verify/map_entries108_native.py` | `39934f6fd47dc951e0475eebf40bf73de8aa763d0f1788b92476ddb370d28ac7` |

Artifact SHA-256 `ccf8309e0503dd504d651abb4c6df658fb68a4836f91b2711d236797905f09cd`.
Original XAPK `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`; original lib `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`.
