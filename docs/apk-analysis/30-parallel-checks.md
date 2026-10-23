# 30 — Kiểm chứng song song tầng A (kết luận tạm thời)

> Đáp lô `PARALLEL_TASKS.md` của nhánh spec. Mỗi mục là một giả định **sai được**,
> kiểm bằng script độc lập `tools/verify/parallel_checks.py` đọc thẳng file thô.
> Phán quyết: **PASS** khớp · **REVERSED** sai · **MISSING** thiếu input/định nghĩa.

| task | giả định | phán quyết | chi tiết |
|---|---|---|---|
| T2 | RankManager thiếu 8B ở ctor; export lại thì gác cổng đạt | **PASS** | ctor = 8 byte (method rỗng), ends_clean mọi method: True, size_capped: 0. Không thiếu byte nào. |
| T3 | GetSurvivalScore chứa >=4/5 hằng 6/3/1.1/0.2/0.5 | **PASS** | có 5/5 hằng ([0.2, 0.5, 1.1, 3.0, 6.0]); phép tính thấy: chưa rõ nhân/cộng. |
| T4 | stepLevel: 4 ngưỡng 30/58/118/248, hệ số 0.168/1.0/1.05/1.15; id tàu = 10001+playerIndex | **PASS** | stepLevel cmp=[30, 58, 118, 248], float=[0.168, 1.0, 1.05, 1.15]; GetMainCannonDamage có mov #0x2711 (=10001): True. |
| T6 | 20001-20013 là tàu thật và không có field HP | **REVERSED** | 38 dòng Data_Players chỉ có cột ['Actived', 'Sprite', 'Star', 'id'] — không field HP nào (phần này khớp H6); nhưng 20001-20013 nằm ở datas/drones.json (13 drone: 20001-20013), không phải tàu bị mất. H6 sai ở nửa đầu, đúng ở nửa sau. |
| T10 | root 900xx là prefab test, 0 lần trong tổng quân | **PASS** | 48 root 900xx trong prefab-roots; xuất hiện trong waves: 0. |
| T12 | đọc độc lập .cctor vẫn ra StartHp=2500,0 cạnh 0,18 | **PASS** | 15 cặp ldr d trong .cctor. VA 0x757ce0: [3.0, 10.0]; VA 0x757bc0: [0.18, 2500.0]; VA 0x758140: []; VA 0x757788: [18.0, 5.6]; VA 0x757550: []; VA 0x757b08: []; VA 0x757ce8: [25.0, 3.0]; VA 0x757a38: []; VA 0x757558: []; VA 0x757398: [] |

## Chưa làm ở vòng này

- **T1 (map→wave)**: chờ `field-defaults.json` từ CI (script.json của Il2CppDumper).
- **T13 (đường cong HP boss)**: giả định chưa định nghĩa cách chia bin (282 wave gồm cả campaign HP=0) — cần nhánh spec chốt định nghĩa trước khi kiểm.
- T5/T7/T8/T9/T11: tầng B/C, cần đọc sâu asm hoặc AssetRipper.

## T1 (map→wave) — tiến triển sau vòng tầng A

- Nguồn dữ liệu đã tìm thấy: `reverse-engineering/il2cpp/field-defaults.json`
  (10.493 field có giá trị mặc định, parse thẳng từ `global-metadata.dat` v31:
  header → typeDefinitions 88B/type → fields → fieldDefaultValueData; tổng
  fieldCount khớp 50.606/50.606). Trong đó 982 blob
  `<PrivateImplementationDetails>` là các mảng literal của InitializeArray.
- `.cctor` của Map_Get_Datas dựng 69 List (576 mảng InitializeArray + các
  mảng immediate): cấu trúc segment đã trích vào `datas/map_table_segments.json`
  (`tools/verify/map_table.py`). **Segment 35 có 250 mảng** (7 immediate +
  243 mảng int[3]) — ứng viên `listMapDatas`: mỗi map ~3 wave, giá trị dạng
  wave id (0–999, boss 7xxx/9xxx). Đã ghép thử vào
  `datas/map_waves_candidate.json` (`tools/verify/map_waves.py`).
- **Chưa chốt**: phép nối token (0x80000xxx trong mã máy) → blob cụ thể nằm ở
  bảng metadata-usage trong binary (MetadataRegistration), chưa parse được.
  Ghép hiện tại dựa trên thứ tự blob theo field_index (đã kiểm đơn điệu
  982/982) + mỏ neo immediate — xếp hạng TẠM THỜI, cần xác thực chéo.
