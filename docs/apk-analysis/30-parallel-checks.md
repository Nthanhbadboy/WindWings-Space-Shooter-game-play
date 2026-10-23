# 30 — Kiểm chứng song song tầng A (kết luận tạm thời)

> Đáp lô `PARALLEL_TASKS.md` của nhánh spec. Mỗi mục là một giả định **sai được**,
> kiểm bằng script độc lập `tools/verify/parallel_checks.py` đọc thẳng file thô.
> Phán quyết: **PASS** khớp · **REVERSED** sai · **MISSING** thiếu input/định nghĩa.

| task | giả định | phán quyết | chi tiết |
|---|---|---|---|
| T2 | RankManager thiếu 8B ở ctor; export lại thì gác cổng đạt | **REVERSED** | ctor = 8 byte; ends_clean True toàn bộ nhưng còn 25 method vắng mặt khỏi file asm (cờ ends_clean không bắt được — đã sửa exporter: luôn ghi asm, chờ tái export). |
| T3 | GetSurvivalScore chứa >=4/5 hằng 6/3/1.1/0.2/0.5 | **PASS** | có 5/5 hằng ([0.2, 0.5, 1.1, 3.0, 6.0]); phép tính thấy: chưa rõ nhân/cộng. |
| T4 | stepLevel: 4 ngưỡng 30/58/118/248, hệ số 0.168/1.0/1.05/1.15; id tàu = 10001+playerIndex | **PASS** | stepLevel cmp=[30, 58, 118, 248], float=[0.168, 1.0, 1.05, 1.15]; hằng 10001 có mặt. Chiều đúng (VERIFY_ROUND1 §1): asm là TRỪ 10001 khỏi id để lấy index (adds w19,w19,#-0x2711), không phải cộng. |
| T6 | 20001-20013 là tàu thật và không có field HP | **REVERSED** | 38 dòng Data_Players chỉ có cột ['Actived', 'Sprite', 'Star', 'id'] — không field HP nào (phần này khớp H6); nhưng 20001-20013 nằm ở datas/drones.json (13 drone: 20001-20013), không phải tàu bị mất. H6 sai ở nửa đầu, đúng ở nửa sau. |
| T10 | root 900xx là prefab test, 0 lần trong tổng quân | **PASS** | 48 root 900xx trong prefab-roots; xuất hiện trong waves: 0. |
| T12 | đọc độc lập .cctor vẫn ra StartHp=2500,0 cạnh 0,18 | **PASS** | 15 cặp ldr d trong .cctor. VA 0x757ce0: [3.0, 10.0]; VA 0x757bc0: [0.18, 2500.0]; VA 0x758140: []; VA 0x757788: [18.0, 5.6]; VA 0x757550: []; VA 0x757b08: []; VA 0x757ce8: [25.0, 3.0]; VA 0x757a38: []; VA 0x757558: []; VA 0x757398: [] |
| T13 | đường cong HP theo bin 20 wave (định nghĩa VERIFY_ROUND1 §4.2) | **PASS** | median các bin cuối — 120-139: 2,440,000; 220-239: 5,580,000; 240-259: 8,600,000; 260-279: 14,900,000; 280-281: 20,600,000. Tổng HP toàn game: 474,696,000 (đo độc lập, đối chiếu 480,89M của nhánh spec). |

## Chưa làm ở vòng này

- **T1 (map→wave)**: chờ `field-defaults.json` từ CI (script.json của Il2CppDumper).
- **T13**: đã có định nghĩa bin (VERIFY_ROUND1 §4.2) — xem phán quyết ở trên.
- T5/T7/T8/T9/T11: tầng B/C, cần đọc sâu asm hoặc AssetRipper.
