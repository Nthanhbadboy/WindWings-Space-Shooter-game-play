# PARALLEL_TASKS — một lô **13 việc kiểm chứng** chạy **song song**

> **Đây là bản yêu cầu cho nhánh dữ liệu** (`arena/ef6b75ef-…`, bản `6109008c`).
> Tôi **không** commit sang nhánh đó; tôi chỉ fetch/đọc. File này nằm trong `docs/spec/` của tôi.
>
> **Ý của chủ dự án:** *"tổng hợp nhiều thứ, đưa ra nhiều giả định, báo bên kia chạy song song
> nhiều GitHub Action, đỡ phải đợi nhau từng việc."* ⇒ File này gom **13 việc độc lập** thành
> **một lô**, mỗi việc là **một giả định có thể sai** (không phải "xem có gì"), và mỗi việc
> chạy trong **một job riêng**.

---

## 0. Vì sao hiện tại **không** song song được — đo được, không phải phỏng đoán

Đọc 4 workflow của nhánh dữ liệu (`analyze-apk` · `ingest-apk` · `probe-apk-sources` · `probe-typetree`):

| Đặc điểm | Số | Hệ quả khi chạy 2 job cùng lúc |
|---|---|---|
| `permissions: contents: write` | **4/4** | mỗi job đều muốn ghi repo |
| có `git push` ở bước cuối | **4/4** | job thứ hai **fail non-fast-forward** |
| `git pull --rebase --autostash` trước push | 4/4 | giảm rủi ro nhưng **không loại bỏ** (rebase giữa 2 job cùng sửa `docs/apk-analysis/`) |
| `timeout-minutes` | 150 / 60 / 15 / 30 | job dài nhất quyết định, không phải job chậm nhất |

⇒ Muốn 13 việc chạy cùng lúc thì **phải bỏ đường "commit trong job"**. Đổi sang
**`upload-artifact`**: 13 job ghi 13 thư mục khác nhau, **không job nào chạm `git`**, rồi **một job
hợp nhất** chạy sau. Đây là thay đổi duy nhất bắt buộc.

---

## 1. Sáu nguyên tắc để song song **thật**

| # | Nguyên tắc | Vì sao |
|---|---|---|
| 1 | Job **không commit**, chỉ `upload-artifact` | không tranh chấp `git push` |
| 2 | Tên artifact = **mã task** (`T1`…`T13`) | gộp không cần merge file |
| 3 | Mỗi job **tự chứa** — chỉ đọc input đã có trong repo | không job nào `needs` job khác |
| 4 | `fail-fast: false` + `max-parallel: 13` | 1 job hỏng **không** giết 12 job còn lại |
| 5 | `permissions: contents: read` | job không thể vô tình sửa repo |
| 6 | **Exit code = phán quyết** (0 PASS · 2 LẬT NGƯỢC · 3 THIẾU INPUT) | job hợp nhất chỉ đọc `verdict.json`, không đọc log |

> GitHub Actions cho **20 job đồng thời** ở gói thường ⇒ 13 job nằm dưới trần, chạy thật sự
> cùng lúc. Thời gian cả lô = **job chậm nhất**, không phải **tổng 13 job**.

---

## 2. Ba tầng chi phí — 6 việc **không cần** APK

| Tầng | Cần gì | Việc | Số |
|---|---|---|---|
| **A** | chỉ đọc file đã có trong repo | T1 · T6 · T7 · T8 · T12 · T13 | **6** |
| **B** | Cpp2IL/asm từ XAPK đã cache (`cache@v4`, key sha) | T2 · T3 · T4 · T5 | **4** |
| **C** | AssetRipper / typetree của prefab + Animator | T9 · T10 · T11 | **3** |

> Tầng A chạy **local 1 phút** là xong — nếu muốn nhanh hơn nữa thì 6 việc này khỏi cần Action.
> Tầng B/C mới đáng đưa lên Actions, và chúng **dùng chung một cache XAPK** ⇒ không tải lại 4 lần.

---

## 3. Mười ba **giả định** — mỗi cái là một dự đoán **số**, sai được

> Quy ước: **H** = giả định, **T** = task kiểm nó. Cột "nếu SAI" là **điều kiện lật ngược** —
> bắt buộc phải có, để kết quả không bị đọc thành "chắc là đúng".

| H | Giả định (dự đoán cụ thể) | Nếu **SAI** thì đổi gì ở spec | Chặn mục nào |
|---|---|---|---|
| **H1** | `.cctor` của `Map_Get_Datas` (25.996 lệnh) dựng **bảng map→wave thật**: hợp các map phủ đúng **282** wave id, mỗi map **≥1** wave | nếu chỉ có **stride** (số wave mỗi map) ⇒ map→wave là **dải liên tiếp**, không phải bảng tra | `OPEN_ISSUES` A2 |
| **H2** | `RankManager` thiếu đúng **8 B** ở `ctor` (`0x127cb84`); export lại ⇒ gác cổng **17/17** | nếu vẫn thiếu ⇒ lỗi nằm ở **cấu hình dumper**, không phải file cụt | `ASM_INTEGRITY` §6 |
| **H3** | `GetSurvivalScore` chứa **≥4/5** hằng `6,0 · 3,0 · 1,1 · 0,2 · 0,5` và trả **hệ số ≥ 1** (nhân) | nếu là **cộng** ⇒ 467 dòng HP enemy phải đọc lại theo `StartHealthPoint + f(stage)` | `OPEN_ISSUES` B3 |
| **H4** | `stepLevel` có **4 ngưỡng 30/58/118/248** và 4 hệ số **0,168 · 1,0 · 1,05 · 1,15** | nếu ngưỡng khác ⇒ đường cong damage player vẽ lại; B3 không đóng | `DESIGN_QUESTIONS` B3 |
| **H4b** | `GetMainCannonDamage` gọi stat id **`10001 + playerIndex`** (`add w0,w19,#0x2711`) ⇒ **damage CÓ theo tàu**, dù **HP thì không** | nếu `0x2711` chỉ là hằng số thường ⇒ damage **không** theo tàu, và mắt ghép #1 mạnh hơn (1 tàu = 1 bộ số) | `BALANCE` §0.6.13 |
| **H5** | `Device_Get_Data` có **3 bảng Field RVA**: **5 loại × 2 stat**, `type 4` = phần trăm | nếu bảng là `int16`/curve ⇒ công thức `base[rank]+pct×(lv+1)` vẫn đúng nhưng **đơn vị** đổi (÷100 vs ÷1000) | `OPEN_ISSUES` B1 |
| **H6** | 13 dòng `20001–20013` trong `14-Data_Players.csv` là **tàu thật**, và **không** dòng nào có field HP | nếu có field HP/regen ⇒ **HP theo tàu** thành sự thật, mắt ghép #1 phải sửa | `OPEN_ISSUES` E2/B2 |
| **H7** | `GetCountEnemies` cộng theo **placement thật** ⇒ tổng ≈ **22.471** (Σ len) hoặc **45.659** (Σ len×copies), sai khác **<1%** | nếu ra số khác ⇒ "tổng quân" trong `ENCOUNTERS`/`DONE` phải đổi nhãn | `OPEN_ISSUES` B4 |
| **H8** | 43/305 trace chưa đối chiếu khớp với nhóm **bonus** (`GetBonusCoin` · `GetBonusExp` · `GetSurvivalScore`) | nếu không khớp ⇒ có **họ công thức thứ ba** chưa biết | `OPEN_ISSUES` B5 |
| **H9** | giải mã được **≥700/793** event có `time` hữu hạn, và join **≥280/308** controller → clip qua GUID | nếu `m_StreamedClip` rỗng ⇒ **C1 đóng ÂM** (không lấy được, phải tự thiết kế nhịp bắn) | `OPEN_ISSUES` C1·C2 |
| **H10** | 45 root `900xx` là prefab **test/debug**, **0** lần xuất hiện trong 45.659 quân | nếu có xuất hiện ⇒ chúng là nội dung thật bị bỏ sót trong roster | `OPEN_ISSUES` C7 |
| **H11** | damage của **19/37** class Director không khai báo field nằm ở **bullet prefab** (`Gun_Attack.bltDamage`); map được **≥15/19** | nếu không map được ⇒ 19 nhóm đòn boss phải **tự thiết kế** (không phải "chưa đọc") | `OPEN_ISSUES` B6 |
| **H12** | bộ đọc **thứ hai**, viết độc lập, cũng ra **`StartHp` = 2500,0** và **`stepCommon` = 0,18** liền nhau | nếu lệch ⇒ A1 **hạ từ A xuống C** và phải mở lại | `OPEN_ISSUES` A1 |
| **H13** | HP boss (đã ×`copies`): median **3,31M** (220–239) · **8,60M** (240–259) · **16,23M** (260–279) · **20,6M** (280–281); tỉ lệ **1,85–1,95** /20 wave | nếu ngoài khoảng ⇒ con số **1,89×** trong `BALANCE` phải bỏ nhãn A | `BALANCE` §2 |

---

## 4. Mười ba task — đầu vào, đầu ra, tiêu chí

> Mọi lệnh giả định chạy trong **repo của nhánh dữ liệu**, thư mục `tools/verify/`.
> Mỗi script ~40–90 dòng; **không** script nào import script khác.

| T | Kiểm H | Input (đã có trong repo) | Output | PASS khi |
|---|---|---|---|---|
| **T1** | H1 | `reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.asm.txt` · RVA `GetListWaves 0x13fe86c` · `GetNumberWaves 0x13fe630` | `map_waves.csv` (`map_id,wave_index,order_in_map`) · `maps.csv` | mọi `wave_index < 282`; hợp **=282**; mỗi map ≥1 |
| **T2** | H2 | export lại `RankManager` (ctor `0x127cb84`) | `asm_guard.txt` · `rankmanager.<sha>.asm.txt` | gác cổng **17/17**, `size_capped` **0/425** |
| **T3** | H3 | `Enemy_Data_Balance.asm.txt` → `GetSurvivalScore` | `survival_score.txt` (pseudo-code ≤20 dòng) · `survival_score.csv` | ≥4/5 hằng đọc được; xác định được biến vào |
| **T4** | H4 + H4b | `Player_Get_Datas.asm.txt` (`stepLevel`, `GetMainCannonDamage`) · `datas/formula_traces.json.gz` | `step_level.csv` · `cannon_damage.txt` | 4 ngưỡng đúng thứ tự; 4 hệ số có mặt; `#0x2711` giải thích được |
| **T5** | H5 | `Device_Get_Data.asm.txt` + 3 Field RVA | `device_stats.csv` (`type,stat,rank,base,pct`) | ≥3 bảng; mỗi bảng ≥2 cột; tổng khớp `GetStatValue1` |
| **T6** | H6 | `docs/apk-analysis/14-Data_Players.csv` (38) · `datas/ships.json` (25) · SO asset | `ships_38.csv` (`id,name,prefab,star,source`) | ≥12/13 map được prefab; **0** field HP |
| **T7** | H7 | `Stage_Get_Datas.asm.txt` · `datas/waves.json` (282 wave / 11.095 spawner) | `stage_counts.csv` | xác định công thức; lệch <1% so với 22.471 **hoặc** 45.659 |
| **T8** | H8 | `datas/formula_traces.json.gz` (305 trace) · `Enemy_Data_Balance.asm.txt` | `trace_map.csv` (`trace_id,method,label`) | **305/305** có nhãn |
| **T9** | H9 | `datas/anim_clips.json.gz` · typetrees `AnimationClip`/`AnimatorController` | `anim_events.csv` · `controller_clips.csv` | ≥700/793 event có `time`; ≥280/308 controller resolve |
| **T10** | H10 | `reverse-engineering/raw/prefab-roots.csv` · `datas/waves.json` | `prefab_900.csv` | 45/45 có component; **0** trong 45.659 quân |
| **T11** | H11 | 19 class Director · `prefab_joins.csv.gz` · `Enemy_Datas.csv` | `director_damage_map.csv` | ≥15/19 map sang `Gun_Attack.bltDamage` |
| **T12** | H12 | `.cctor` `Player_Get_Datas` (97 hằng, 14 float) — **đọc bằng script mới** | `starthp_recheck.json` | khớp tuyệt đối **2500,0** + **0,18** |
| **T13** | H13 | `docs/apk-analysis/15-enemy-hp.csv` · `datas/waves.json` | `boss_hp_curve.csv` | 4 median khớp ±2%; tỉ lệ trong **1,85–1,95** |

### Ba task cần nói rõ cách làm (không hiển nhiên)

**T1 — đọc bảng inline.** `.cctor` dựng list bằng `bl <List<T>.Add>` trên các mảng `int[]` là
**literal** (`movz/movk` + `str`). Cách rẻ nhất: quét mọi cặp `(str wN,[xM,#off])` theo **cùng base
register**, gom thành dãy int; mảng dài nhất là bảng wave; `GetListWaves(int)` trả **con trỏ tới
mảng con** ⇒ `map_id` = thứ tự trong mảng ngoài. **Không cần** chạy lại APK: file asm đã đủ
(`958,4 KB`, `26.013` dòng).

**T9 — thời gian event.** `m_Events` cho **tên hàm + tham số**, `m_StreamedClip` cho **thời gian**;
hai danh sách **cùng thứ tự**. Nếu `m_StreamedClip` rỗng ⇒ **dừng**, ghi `REVERSED`, đừng suy diễn.
Đây là chỗ dễ tự lừa nhất: **793 event** là con số *có event*, không phải *có thời gian*.

**T12 — chống tự xác nhận.** Script T12 **không được** dùng lại bất kỳ dòng nào của tôi; nó phải
tự parse `.cctor`, tự tìm cặp `str d` liền nhau, và in ra **cả 14 float** chứ không riêng 2500.
Nếu in riêng 2500 thì test này vô nghĩa.

---

## 5. Workflow — **một file**, 13 job, không job nào ghi repo

```yaml
name: verify-batch
on:
  workflow_dispatch:
    inputs:
      tasks:
        description: 'T1,T2,... hoặc all'
        default: all
permissions:
  contents: read            # ← khác 4 workflow hiện tại (contents: write)

jobs:
  plan:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.m.outputs.matrix }}
    steps:
      - id: m
        run: |
          ALL='["T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12","T13"]'
          if [ "${{ inputs.tasks }}" = "all" ]; then echo "matrix={\"task\":$ALL}" >> $GITHUB_OUTPUT
          else
            SEL=$(echo '${{ inputs.tasks }}' | sed 's/,/","/g')
            echo "matrix={\"task\":[\"$SEL\"]}" >> $GITHUB_OUTPUT
          fi

  verify:
    needs: plan
    runs-on: ubuntu-latest
    timeout-minutes: 25
    strategy:
      fail-fast: false        # 1 task hỏng không giết 12 task
      max-parallel: 13
      matrix: ${{ fromJson(needs.plan.outputs.matrix) }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      # 7 task tầng A không cần dòng này; 6 task B/C dùng cache chung 1 key
      - name: Restore XAPK (tầng B/C)
        if: ${{ contains(fromJson('["T2","T3","T4","T5","T9","T10","T11"]'), matrix.task) }}
        uses: actions/cache@v4
        with:
          path: /tmp/apk/windwings.xapk
          key: windwings-xapk-1.3.118-f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e
      - name: Run
        run: |
          mkdir -p out
          python3 tools/verify/${{ matrix.task }}.py --out out/ || code=$?
          echo "exit=$code" >> $GITHUB_OUTPUT
        id: run
      - uses: actions/upload-artifact@v4
        if: always()            # giữ cả log khi REVERSED
        with:
          name: ${{ matrix.task }}
          path: out/
          if-no-files-found: warn

  merge:
    needs: verify             # job duy nhất chạy sau
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with: { path: art, merge-multiple: true }
      - run: python3 tools/verify/merge.py --in art --out summary.md
      - uses: actions/upload-artifact@v4
        with: { name: SUMMARY, path: summary.md }
```

> **Ai chạy:** 1 lần `workflow_dispatch` với `tasks=all` ⇒ 13 job song song.
> **Kết quả:** 14 artifact (`T1`…`T13` + `SUMMARY`). **Không** commit nào ⇒ không cần `pull --rebase`.

---

## 6. Hợp đồng artifact — để tôi ingest **một lần**, không hỏi lại

Mỗi task ghi **đúng hai file**, không thêm file lạ:

```
out/<T>.csv            # header bắt buộc, UTF-8, phân cách ','
out/<T>.verdict.json   # {task, verdict, rows, seconds, sha, tool, note}
```

`verdict` chỉ nhận **3 giá trị**:

| verdict | nghĩa | tôi làm gì |
|---|---|---|
| `PASS` | số khớp dự đoán trong §3 | nâng nhãn lên **A** + ghi `Điều kiện lật ngược`, đóng mục `OPEN_ISSUES` tương ứng |
| `REVERSED` | số **lệch dự đoán** | sửa `BALANCE`/`ENCOUNTERS` theo số mới, **giữ nguyên dự đoán cũ** trong bảng "đã sai" |
| `MISSING` | thiếu input, không kết luận | ghi vào §7 `ASM_INTEGRITY` là **chưa kiểm**, **không** đóng mục nào |

`schema` của `verdict.json`:

```json
{"task":"T5","verdict":"PASS","rows":148,"seconds":23.4,
 "sha":"6109008c","tool":"python3 tools/verify/T5.py",
 "note":"3 bảng, 5 loại × 2 stat; type 4 chia 100"}
```

---

## 7. Luật hợp nhất — **một lần**, không từng việc

Khi có đủ 13 artifact, tôi cập nhật **một commit** chạm đúng 6 file, theo bảng:

| Artifact | File tôi sửa | Mục |
|---|---|---|
| `T1` | `ENCOUNTERS.md` · `OPEN_ISSUES.md` A2 | bảng map→wave |
| `T2` · `T12` | `ASM_INTEGRITY.md` · `OPEN_ISSUES.md` A1/E3 | baseline 17/17 · StartHp |
| `T3` · `T4` · `T7` | `BALANCE.md` §2 · `COMBAT.md` §2 · `DESIGN_QUESTIONS.md` B3 | đường cong HP enemy / damage |
| `T5` · `T6` | `BALANCE.md` §0.6.7 · `TUNING_KNOBS.md` | device · 38 tàu |
| `T8` | `DATA_SYNC.md` | 305/305 trace |
| `T9` | `ANIMATION.md` · `OPEN_ISSUES.md` C1/C2 | nhịp bắn |
| `T10` · `T11` | `BOSSES.md` §7 · `ASSETS.md` | prefab `900xx` · damage 19 class |
| `T13` | `BALANCE.md` §2 | HP boss 1,89× |

> **Không** dùng kết quả `MISSING` để đóng mục. **Không** đổi nhãn A→B mà không ghi lý do.
> **Không** merge PR của tôi.

---

## 8. Kết quả vòng 1 — **6/13 task đã chạy** (`68ce86a7`, 23/10)

> Chi tiết kiểm chéo: `VERIFY_ROUND1.md`. Ở đây chỉ ghi **phán quyết** và **việc còn lại**.

| Task | Trạng thái | Họ báo | Tôi kiểm lại |
|---|---|---|---|
| **T2** | ✅ đã chạy | PASS — "không thiếu byte nào" | ⚠ **Kết luận đúng, cơ chế sai.** `RankManager.asm` **vẫn** thiếu 8 B; `ends_clean` = **True rỗng** (method vắng mặt ⇒ điều kiện vacuous). Nhưng ctor rỗng ⇒ **không mất gì** |
| **T3** | ✅ đã chạy | PASS — 5/5 hằng | ✅ đúng, nhưng **tiền đề H3 của tôi sai**: `GetSurvivalScore` là **điểm**, không phải HP ⇒ **không đóng `B3`** |
| **T4** | ✅ đã chạy | PASS — `cmp [30,58,118,248]`, float `[0,168·1,0·1,05·1,15]` | ✅ phần `stepLevel` **đúng từng số**. ❌ **H4b sai chiều**: asm là `adds w19,w19,#-0x2711` = **trừ 10001**, không phải `add` |
| **T6** | ✅ đã chạy | **REVERSED** — `200xx` là drone | ✅ **đúng**. `drones.json` 13 item · `star` 1,0–5,02 · `actived` 12/13 ⇒ **`E2` đóng: tôi đọc sai** |
| **T10** | ✅ đã chạy | PASS — **48** root `900xx` | ✅ "0 lần trong waves" đúng. ⚠ **48 là do regex không neo**; `^900\d\d$` = **45** (đúng số tôi ghi) |
| **T12** | ✅ đã chạy | PASS — `VA 0x757bc0: [0,18 · 2500,0]` | ✅ **đúng** ⇒ `A1` nay là **A hai nguồn độc lập** |
| **T13** | ⚠ **tôi tự làm** | *(họ để MISSING vì thiếu định nghĩa bin)* | ❌ **REVERSED**: 8,60 M giữ nguyên · 260–279 **15,40 M** · 280–282 **18,30 M** · tổng **480,89 M** · tỉ lệ **1,79×** (không 1,89×) |
| **T1 · T5** | ❌ **vẫn MISSING** | *(chờ `field-defaults.json`)* | **1.192/1.194** hằng `debug_rva` giải ra `a=0x0` + `a_bytes = 7f454c46` (`\x7fELF`) ⇒ chuỗi RVA **vẫn đứt** |
| **T7 · T8 · T9 · T11** | ⬜ chưa chạy | — | tầng B/C, cần AssetRipper/asm đọc sâu |

**Tỉ lệ:** **6/13** task chạy xong · **1** tôi tự làm (`T13`) · **2** vẫn MISSING (`T1`·`T5`) · **4** chưa chạm.

**Ba điều đáng giữ từ vòng này:**

1. **Cờ tự kiểm phải kiểm chính nó.** `ends_clean` của họ trả `True` cho method **vắng mặt** — nếu tôi
   không đếm "method có mặt" thì đã tin `T2` = PASS. **Cờ 4** nay nằm trong `ASM_INTEGRITY` §1.
2. **Dự đoán của tôi sai 3 chỗ** (`H3` tiền đề · `H4b` chiều phép toán · `H13` số). Tỉ lệ đúng
   10/13 nếu tính cả "đúng một phần" — nhưng **chỉ số đo mới đáng tin**, không phải tỉ lệ này.
3. **`T1`/`T5` là 2 mục chặn thiết kế thật**, và lý do chúng chưa xong **đo được**: pipeline đang
   đọc **header ELF** thay vì **VA sau relocation**. Đây là bug 1 dòng, không phải "chưa tới lượt".

---

## 9. Còn thiếu / phải đoán

- **`tools/verify/` chưa tồn tại.** Tôi chỉ đưa *hợp đồng* (argv, exit code, schema); viết 13 script
  là việc của nhánh dữ liệu. Ước lượng: **13 × ~60 dòng**.
- **Tầng C (T9–T11) chưa chắc chạy được**: phụ thuộc AssetRipper dựng được prefab; nếu không,
  `verdict` phải là `MISSING`, **không** phải `REVERSED`.
- **13 job đồng thời** dưới trần 20 của GitHub, nhưng nếu repo dùng runner tự trả tiền thì trần khác.
- **Chưa có** ước lượng thời gian cho `T1` (`.cctor` 25.996 lệnh) — có thể 5–30 s, cũng có thể
  phải viết bộ giải mã arm64 nhỏ. Đây là task **duy nhất** có rủi ro vượt `timeout-minutes: 25`.
- **Giả định nền:** bản `6109008c` là bản đúng. Nếu nhánh dữ liệu đã đi tiếp, mọi `sha` trong
  `verdict.json` khác ⇒ tôi phải fetch lại trước khi hợp nhất.
