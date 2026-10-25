# 73 — TMP fonts, fallback riêng của asset và lookup localization first-index

**25/10/2026 — mọi kết luận vẫn tạm thời/static.** Không phải nghiệm thu renderer,
font shaping/RTL, playthrough hay độ phủ mọi chuỗi runtime.

## 1. Cập nhật và nguồn

- Nhánh extraction đã cập nhật từ remote; report72 Verify **40197021501 SUCCESS**,202tests.
- Peer đã tới **2d0a0e139981f1c38ace03e786237f210dbda1f1**: có typed Player starting
  arrays và sửa report69. Không lấy “chưa có Map/Player blob” làm blocker nữa.
  Snapshot ba tài liệu peer nằm ở `raw/peer-review/update-2d0a0e139.json.gz`, kèm git
  blob IDs/SHA. **Snapshot peer không phải bằng chứng APK**, không merge wholesale.
  Các summary gap/assets cũ vẫn phải đọc cùng report67–73, không phủ định raw mới.
- Recovery scoped **40197895269 SUCCESS**; bổ sung128bytes table lựa chọn ngôn ngữ
  ở **40198072388 SUCCESS**. Raw bot cuối **61083ec31**. Hai recovery này không chạy full asset export; lượt broad tự kích hoạt nhầm đã hủy, xem incident cuối report.
- Cùng XAPK SHA `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`;
  data.unity3d SHA `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7`;
  native SHA `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`;
  metadata SHA `449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69`.

Raw: `reverse-engineering/raw/font-language/`:

- `index.json`: hash inventory, dump hash; không tự index chính nó.
- `graph-index.json`,123chunks `objects-*.jsonl.gz`, `links.json.gz`: parsed header,
  owning serialized file/externals, full font/settings/language typetrees;
  text components chỉ projection font/layout + codepoint inventory/hash, không full UI dump.
- `native/{LanguageManager,LanguageAssets,LanguageTextMeshPro,LanguageTextMeshProUI,
  LanguageTextMeshProFormats,TMP_FontAsset,TMP_FontAssetUtilities,TMP_Settings}.{json,asm.txt}`:
  **34uncapped methods**; chỉ lấy selected TMP getters/character search.
- `native-data.json`: nativeVA `0x779fb8`,128bytes,32int32 LE cho system-language map.
- Native metadata references đối chiếu cùng nativeSHA với `raw/ui-audit/{metadata-index,
  native-relocations}.json.gz`. Chỉ dẫn format/metadata loads, không thực thi game.

Census125453MonoBehaviour headers có **1exception** resources.assets580792 do thiếu
built-in `unity default resources`. `all_MB_headers_classified=false` giữ nguyên.
Selected12296objects đọc thành công, **0read errors/0unresolved scoped links**.
Không đổi điều đó thành “tất cả font có thể xuất hiện runtime đã biết”.

## 2. Global fallback null không có nghĩa main font không fallback

TMP Settings `resources.assets:580789`:

- defaultFont PPtr **file4/path105**, resolve qua owning externals thành
  `data.unity3d/sharedassets0.assets:105` — **AGENCYB SDF**.
- global `m_fallbackFontAssets=[null]`, missingGlyphCharacter0,warningsDisabledtrue.
- Getter defaultFont `0x273adb8` đọcfield0x28; globalfallback `0x273aed8` đọc0x58.

**Asset105 có fallback table riêng**, khác list global đó. Thứ tự serialized/native search:

`105 → 110 → 106 → 108 → 109 → 111 → 107`

Tất cả dưới `data.unity3d/sharedassets0.assets`; sáu fallback đều là leaf trong graph này.
Native `TMP_FontAsset.get_fallbackFontAssetTable 0x270d114` đọcfield0x138;
`GetCharacterFromFontAsset_Internal 0x2715520` thử source, rồi list0x138 theoindex,
recurse vớiincludeFallbacks khi được phép. HashSet searched-assets hỗ trợ tránh lặp;
không suy toàn bộ thứ tự global/sprite/replacement fallback của renderer từ utility này.

| Font ID / tên | Glyph rows | Character rows | Atlas texture ID | Kích thước | Padding |
|---|---:|---:|---:|---:|---:|
|105 AGENCYB SDF|234|234|33|512×256|1|
|106 Agency SDF-Cyrillic|66|66|14|256×256|2|
|107 Amiri-Bold SDF|329|329|29|512×256|1|
|108 NotoSansKR-Medium SDF|435|435|13|512×512|1|
|109 NotoSansSC-Medium SDF|1172|1174|31|1024×1024|2|
|110 Roboto-Medium SDF-Currency|19|19|30|128×128|1|
|111 SDF-Thai|97|97|32|256×256|1|

Tổng2352glyph rows/2354character rows, union **2285unique Unicode values**.
109 có character10/13 cùngglyph1; không ép sốcharacter=sốglyph.
Mỗi character glyph-index đều resolve trong owningglyph table; mọi glyphrect nằm trong
atlas texture đã bind, dimensions trùng serializedatlas. Không dùng basename global.

Cả7font assets:
- `m_AtlasPopulationMode=0` = **Static**, renderMode4165 = **SDFAA** từ dumpenum.
- sourceFontFile=null; multiAtlas=false; clearDynamicOnBuild=false; weight table
  regular/italic pointers đều null. Không tự tạo alternate source font.
- Utility chỉ gọi `TryAddCharacterInternal 0x270fc44` ở nhánhpopulationMode==1.
  Không được giả định7assetsstatic sẽ tự rasterize mọi ký tự chưa có từTTF.
  Đây là trạng thái serialized + consumer utility, không loại trừ runtime mutation khác.

**7TMPfont assets ≠7embedded TTFs.** V2 giữ1exported Font program;7SDFatlas PNGs đã có
trongTexture2D outputs. Tênfamily không thay sourceFontFile PPtr=null; không bịa thêm6TTFs.
Texture Font Texture0×0/resources535 của report70 không phải7SDFatlases này.

## 3. Serialized text/font assignment, không phải số label trên một màn hình

Recovered9789TextMeshPro +8TextMeshProUGUI = **9797components**:
- **9796nonnull font PPtrs đều resolve asset105**, dùfileID khác nhau theoowningfile.
- 1nullfont: `resources.assets:699094`. Không tự sửa nó thành105 trongraw.
- Tất cả9797serialized `m_isRightToLeft=false`. Không suy Arabic đã hiển thị đúng/sai
  trên runtime chỉ từflag; chưa audit renderer/shaping hoặc mọi writer thayflag.
- Language wrappers2440LanguageTextMeshPro +1UI +1Formats =2442components.
  Native wrappers gọiLanguageManager.GetText rồitext setter/formatting. Scope này không
  thấy chúng chọn mộtfont asset riêng cho mỗi language; không suy thành toànbuild không
  có runtimefont assignment khác.

Không glob prefab counts thành live-screen counts. Richtext/case-style flags có trongprojection;
chưa chạy style/case conversion, format arguments, normalization hoặc glyph layout.

## 4. Localization: first IndexOf, không last-wins dictionary

**19LanguageAssets**, mỗiasset1426paired listKey/listValue rows. Cả19cùngkey order:
1416unique keys gồmempty; **1415nonempty unique keys**;9empty-key rows.
Ba duplicate groups: emptykey9lần, `txt_free_after`2lần, `txt_free_gift`2lần.

`LanguageAssets.GetText 0x1437f14`:
1. listKey.Contains(key).
2. Nếu có, `listKey.IndexOf(key)` rồiindex listValue.
3. Không cókey →null.

Offsets listKey0x18/listValue0x20 bind từdump; metadata refs chứa
`List<string>.Contains`,`.IndexOf`,`.get_Item`. **Duplicate dùng occurrence đầu tiên**,
không last-wins, cũng không tìm occurrence đầu tiên cóvaluekhôngrỗng.

Ví dụEnglish:
- index690 `txt_free_after` → **`Free after`**.
- index1243 cùngkey →`Free After`, nhưng không thắng lookup này.
- index1410/1411 `txt_free_gift` đều`Free gift for newbies`.

ExportCSV cũ đã collapse duplicate last-wins. Đối chiếu tất cả1415English/Vietnamese keys:
chỉ1valueEnglish khácnativefirst-index;Vietnamese không khác. Đã sửa
`i18n/en.json` keytrên; không sửaCSV/raw. `tools/apk-analyze/data_pack.py` nay ưu tiên
preservedLanguageAssets arrays nếu có, tránh tái sinh lỗi từCSV đãdedup. Cảen/vi cập nhật
provenance; fallbackCSV vẫn là đường legacy nếu không có scopedraw.

`LanguageManager.GetText(key)` `0x14386a8`:
- Nếu cachelanguage asset chưa có, initializes từget_language/set_language.
- Lấy currentasset value; null hoặc **emptystring** →defaultLanguageasset.
- Defaultvalue vẫnnull/empty →trả **key gốc**. Whitespace không bị coi empty ởconsumer này.
- Overload `GetText(key,bool forceDefault)` `0x14384e8` bỏselectedasset khi booltrue.
- cctor `0x1438860` setdefaultLanguage **0=English**.

Trong2442serialized labelcomponents có11distinct keysliteral không nằm trongLanguageAssets,
33components; vídụ`add friend`,`txt_no_profile`. Nativekey-return fallback đã giải thích
đường này; không tự xóa/đổi label hoặc khẳng định tất cả đang visible/runtime dùngkeyđó.

### Selected language ban đầu khác English fallback

- Preference key **`Language`**, metadata slot0x2adc118/effective0x2be1850.
- getter `0x1438280` lấyApplication.systemLanguage, mapsanggameLanguage, rồi gọi
  PlayerPreferences.GetInt(key, mappedDefault). Savedint override defaultmap; không tự
  thêm range-validation vào fact gốc.
- Setter `0x1438068` load/cache `Resources.Load<LanguageAssets>("Language Assets/Language Assets "+enum.ToString())`,
  assigncurrentasset, invokeonChange, **sau đó**persistPreference.SetInt. Không tự đảoorder.
- Nativebounded32int table giải mãđầy đủ trongcontract. Ví dụVietnamese39→Language1,
  Arabic1→6, Czech7→13, Japanese22→11, ChineseSimplified40→18.
- **Generic Chinese6 vàChineseTraditional41 →English0** ởmissing-preference defaultmap
  đanginspected; không tự mapmọiChinese enumvàoSimplified18.

English0làdefaultLanguage fallback, không có nghĩa mọi newinstall luônselectedEnglish.

## 5. Coverage inventories không phải lỗi font đã thấy trên màn hình

Contract giữ Unicode sets của **stored first-value strings**, so với2285character-table
Unicode values trongchain. Đây không phải rendered glyph demand: chưaparse tags, expand
formatargs, đổicase theoFontStyles, normalize,shape, haychọnchuỗi đanglive.

Ví dụdeltas: English0;Vietnamese1(U+0340);Japanese45;Korean98;ChineseSimplified153.
Không kết luận “Vietnamese thiếu1glyph/runtime” hoặc tựchènreplacementfont từnhữngsốđó.
Cầnconsumer/render validation trước; thôngtinký tựthiếu **khỏi bảngstatic đãđọc** vẫn giữraw.

## 6. Deliverables / kiểm lại / bàn giao

- `datas/font_language_contract.json.gz`:7typedfonts/fullglyph+character+face metrics,
  atlasPNG identities/hashes, fallbackorder,19first-index/effective translation tables,
  duplicate evidence, serialized textfont census, systemmap/nativechecks/provenance.
- `docs/assets/font-browser.html`: offline **metadata + rawSDFatlas** guide cho7assets.
  Copyfile này cạnhTexture2D/ trong extractedassets-v2 đểxemPNG. HTMLkhôngnhúngmedia,
  khôngdùngbrowserfont đểgiảrenderAPK, khôngserver/preview nàođượcmở.
- No APK/nativebinary/original fontprogram/atlaspixel mới vàoGit. Draft releasev2 và
  Spine pack giữnguyên; khôngoverwrite/reuploadmedia chỉđểthêmmetadata.

```bash
python3 tools/verify/font_language.py
python3 tools/verify/font_browser.py
python3 -m unittest discover -s tests -v
python3 datas/validate.py
```

Verifier kiểmhashinventory/owningexternals/links/glyphindices/rect bounds/native34methods,
10static checks, metadata loads/direct-call signatures vàregeneratecontract.10tests mới;
**212testsPASS local cóPillow13**, datasvalidationPASS. RecoveryCI40198072388 vàexisting
Verify40198072652success trước10tests mới; finalVerify củacommitbàn giao kiểmriêng.

**Task peer** `arena/20330d0e-windwings-space-shooter-game-p`:
1. Cập nhậtspec nguồnfont: default105+6localfallback, khôngglobalnull→nofallback,
   không“chỉ1fonttoàngame” dođếmTTF; dùngowningtypedjoins.
2. Localization lookupfirstIndex, current→English→key; sửaEnglish`txt_free_after`
   nếuđãcopyCSV-last-wins. Defaultselection dùngsystemmap/savedLanguage, khácEnglishfallback.
3. KhôngcopySDF PNG vàoCSS@font-face nhưTTF. Importer cầnretainedmetrics/material/shader;
   browserpagechỉreference. Nếuappchọnfont/normalization/RTL/shaping khác, ghi **newdesign**.
4. Refreshsummarygap/assetcounts theo67–73, khôngđòi573+6dump hayglobalSpinebasename
   đãcólocalchain; giữfidelity/render/listening unknown. Premium/poolhistory vẫnhoãn.

Tiếp phù hợp: consumer placement/material/render hoặc audio listening riêng; không biến
fontstaticdeltas thành yêu cầudumpfullAPK hay tựvẽlạigame.


### CI scope incident và khôi phục, không đổi kết luận game

Commit56d05126d sửa offline `data_pack.py` đã vô tình kích hoạt workflow fullAnalyze
40198724717 qua pathfilter rộng. CancelAPI trả403 vìintegration không cóactions-write.
Workflow-level concurrency đã hủy lượt đó khi run40198794947 thay thế; runthaythế
**SKIPPED** với marker `[scoped-only]`. Releasepublish step của lượt cũ **SKIPPED**;
đối chiếu releaseAPI xác nhận IDs/digests/update-times của media giữ nguyên, releasevẫn draft.
Không gọi fullpipeline đó là fontrecovery success.

Step Commit reports cũ dùngalways() nên vẫn push partialbot8c9e0217c gồm3historicalreports
vàgzipdump. Đã khôi phục cả4file vềbaseline7bcc14f10; giữpartial3texts/jobstatus/digests
ở `raw/font-language/workflow-scope-incident.json.gz` (operational provenance, không
bằngchứnggame). Dumpdecompressed bytes trước/sau giống hệt.

Đã loại `data_pack.py` khỏifullAnalyze pushfilter, thêm nó vàoofflineVerify; scopedmarker
guard cho maintenance workflow, và Commit reports nay khôngchạy khi cancelled.
**Verify40198724636 và40198794930 SUCCESS** đều211tests vớipinnedPillow12.
**Final Verify40198971054 SUCCESS** trên codecommit3e7b143ab saukhôi phục:212tests PASS,
pinnedPillow12; runAnalyze40198971219 SKIPPED đúngguard. Không thayrawfontgraph/contract.
