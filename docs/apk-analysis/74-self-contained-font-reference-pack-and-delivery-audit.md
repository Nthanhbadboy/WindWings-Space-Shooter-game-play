# 74 — Gói font tham khảo tự chứa, giữ nguyên media và kiểm tra sau upload

**25/10/2026 — tạm thời; không phải nghiệm thu Unity importer/render/RTL/shaping.**

## Cập nhật và mục tiêu

Nhánh extraction đã pull remote; peer vẫn ở `2d0a0e139981f1c38ace03e786237f210dbda1f1`,
không có commit mới sau mốc report73. Không merge spec vào nhánh extraction.
Report73 đã có 7 TMP font assets, nhưng browser trong Git cần copy cạnh media V2.
Follow-up này gom các nguồn đã xác định thành **một ZIP tự chứa** để tham khảo offline,
không cần tự chọn atlas theo basename hoặc tải toàn bộ V2 để xem font.

Không bóc lại APK, không tạo font mới, không resample atlas, không convert SDF thành TTF.
Nguồn vẫn là raw/font-language và audited `assets-v2.zip` của cùng APK report70–73.

## Deliverable đã tạo

Draft release **421174835**, tag `windwings-assets-1.3.118`, thêm duy nhất:

| Thuộc tính | Giá trị |
|---|---|
| Tên | `font-reference-v1.zip` |
| Asset ID | **675170630** |
| Kích thước | **1627375 bytes** |
| SHA256 | `1c20bda1b61d11bb3e4dd06ed07a64672978c66cec33592fb4c25a3b22901848` |
| ZIP members | **19**, không trùng tên |
| Assembly + readback | **40199471450 SUCCESS** |
| Raw bot commit | **25ea43c67** |

Cấu trúc:

- **7 folder riêng**, key bằng SHA của owning serialized-file + font pathID105–111.
  Mỗi folder có `atlas.png` và `font-reference.json`.
- Atlas PNG: **7 exact-byte copies**, đúng owning Texture2D từ report73, không chọn theo tên.
- Mỗi JSON giữ typed font identity, face/glyph/character/fallback metadata, full raw font
  projection và **primary material projection**. Có serialized font feature/kerning tables,
  atlas rects, saved material properties và parsed script pointer.
- `font-programs/`: **1 TTF exact-byte copy**, Font object2044,
  `data.unity3d/globalgamemanagers.assets`, **56312 bytes**.
- `font-programs.json`: inventory riêng của TTF; không gán nó thành sourceFontFile của
  7 TMP assets đang có sourceFontFile=null.
- `index.html`: xem 7 raw SDF atlas PNGs + metadata offline, đường dẫn nằm ngay trong ZIP.
- `README.txt`, `manifest.json`: phạm vi, provenance, từng member SHA/size và source path/hash.

Population: **8 original media copies +10 generated reference files +manifest =19members**.
JSON là reference projection, **không phải Unity .asset / prefab / package có thể import thẳng**.
Generated tree.m_Script sai đã biết không được dùng thay parsed_script_pointer.

### Metadata nào được giữ, metadata nào chưa phải kết luận runtime?

- Full raw font projection giữ `m_KerningTable` và `m_FontFeatureTable`, không chỉ danh sách Unicode.
- Cả7 serialized legacy kerning-pair lists và glyph-pair adjustment lists đều **0entries**.
  Đây là kết quả đọc bảng đã serialize, không kết luận game tuyệt đối không thể có kerning
  hoặc font-feature behavior khác ở runtime.
- Bundle có **7 primary materials** theo font assets. Không khẳng định đã đóng toàn bộ
  text-specific material variants, shader code, placement hoặc draw order của mọi component.
- Toàn bộ 7assets vẫn là static mode0/SDFAA, main105 và localfallback
  `105 →110 →106 →108 →109 →111 →107` như report73.
- Browser không chạy TMP shader, layout, richtext/style conversion, kerning hoặc shaping.
  SDF atlas nhìn trong browser không phải appearance của glyph sau material/shader.

## Kiểm tra integrity và delivery

Producer: `tools/recovery/font_reference_pack.py`.
Workflow: `.github/workflows/assemble-font-reference.yml`.

1. Semantic regeneration của contract phải bằng snapshot report73. Không lấy gzip bytes
   hoặc JSON key order làm thay thế kiểm tra nội dung.
2. Download **V2 đã audit**, đối chiếu toàn archive SHA
   `4b18cc23b9d71d095dbe8be4458a8ca95fe1d16f5bc0c96bb2329c7bc5de3506`.
3. Check từng selected source member SHA/size trước khi tạo folder output; reject duplicate
   source ZIP names, unsupported multi-atlas layout và destination đã tồn tại.
4. Reopen ZIP thành phẩm: CRC, exact member population, no duplicate names, manifest equality,
   toàn bộ member SHA/size; media hashes phải bằng source records V2.
5. Chỉ upload filename mới; **không `--clobber`**, release phải còn draft.
6. Query release sau upload: ID/size/digest đúng; **7 existing release assets giữ nguyên**
   ID/name/size/digest/update-time.
7. **Tải lại ZIP đã upload bằng HTTP download mới**, chạy lại toàn bộ archive/member checks.
   Kết quả bằng pre-upload audit. Đây là readback từ delivery trong **cùng CI job**,
   không gọi là một renderer validation hoặc một independently derived font export.

Raw cùng deliverable:

- `reverse-engineering/raw/font-reference/manifest.json.gz`
- `reverse-engineering/raw/font-reference/archive-audit.json`
- `reverse-engineering/raw/font-reference/release.json` — có previous assets và readback audit.
- Nguồn game/font vẫn giữ nguyên ở `reverse-engineering/raw/font-language/`.

Không có original PNG/TTF/ZIP mới trong Git. Gói media ở artifact/release draft, không publish.

### Recovery/workflow note

Lượt đầu **40199397252 FAIL** ở step gộp contract-check/download; không assemble/upload.
Log archive download trả EOF, annotation chỉ cho exit1, vì vậy không khẳng định stacktrace
hoặc nguyên nhân byte-level chưa giữ được. Đã tách semantic contract check khỏi download,
loại kiểm tra `git diff` trực tiếp trên gzip regenerated; lượt40199471450 thành công.
Không coi failure đó là game-data discrepancy.

Workflow xuất bundle nay **manual-only** sau lần tạo asset; guard existing filename vẫn còn.
Rerun cùng version không được overwrite. Nếu đổi bundle phải dùng version mới, không sửa media V1.

## Cách dùng / tái kiểm

Tải `font-reference-v1.zip` từ draft release, đối chiếu SHA ở trên, giải nén rồi mở `index.html`.
Không cần ghép với V2; không đổi tên 7 font folders. Copyright/quyền sử dụng tài nguyên gốc
không thay đổi vì đã tạo gói tham khảo. Không nhúng vào game mới chỉ vì tải được.

Kiểm metadata offline, không cần media gốc:

```bash
python3 tools/verify/font_reference_contracts.py
python3 -m unittest discover -s tests -v
python3 datas/validate.py
```

Verifier đối chiếu contract/source-graph/catalog hashes, typed PNG/TTF identities, regenerated
7font-reference JSON hashes, population19, upload digest và readback equality. Không tải ZIP
trong unit tests và không giả vờ chạy lại pixel/font renderer từ metadata.
**6tests mới**: synthetic assembly/audit, corruption rejection, no overwrite, retained feature
metadata, real preserved delivery contracts, manual/no-clobber publishing guard.

**Local:218tests PASS** vớiPillow13; datasvalidation PASS. AssemblyCI40199471450
đã chạy216tests/Pillow12 trước2delivery/publishing tests cuối. FinalVerify của
commitbàn giao **40199813697 SUCCESS**,218tests với pinnedPillow12 trêncode4fe0cef8e.

## Task peer và giới hạn tiếp theo

Nhánh `arena/20330d0e-windwings-space-shooter-game-p`, xem `docs/HANDOFF_AI_TASKS.md`:
- Có thể mở font-reference ZIP độc lập để xem 7font/atlas/material metadata, không còn phải
  tự ghép browser report73 với175MB V2.
- Giữ 1TTF inventory riêng; sourceFontFile=null không được thay bằng name-matching heuristic.
- Import/render actual cần pipeline/engine tương thích và kiểm material/placement/style;
  đổi font/RTL/shaping/normalization là new design nếu không có APK consumer proof.
- Static glyph/codepoint inventories không phải rendered missing-glyph conclusions.
- Audio listening, UnityGPU/PMA/font render và concrete placement consumers vẫn mở.
  Premium/pool-history không trở lại thành blocker; không full APK re-export.
