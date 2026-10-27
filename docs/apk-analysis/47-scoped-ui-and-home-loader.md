# 47 — Nghiệm thu scope UI và đào tiếp Home loader

**PROVISIONAL — chỉ bằng chứng tĩnh bóc từ APK, không phải chứng nhận runtime/pixel-accurate.**

## Nguồn mới và cách tái kiểm

- Analyze run `40181265305`, success, bot commit `7325738be`: UI raw mới.
- Recovery run `40181445658`, success, `f7f7ad7f3`: metadata, native relocation,
  Home_Loader/coroutine và PlayerPreferences native bodies. Không dùng bản APK mod.
- Gốc APK pinned như report45; hash native/script nằm trong `metadata-index.json.gz`
  và `native-relocations.json.gz` tại `reverse-engineering/raw/ui-audit/`.
- Các kết quả dẫn xuất giữ raw/callsite/hash, không chỉ ghi prose:
  `render-context-audit.json`, `scoped-visual-links.json.gz`, `loader-and-prefs.json.gz`.

```sh
python3 tools/verify/ui_render_audit.py
python3 tools/verify/ui_reference_links.py
python3 tools/verify/ui_loader_analysis.py
python3 -m unittest discover -s tests -q
```

## 1. Scope asset đã sửa được; Map vẫn chưa đủ

Snapshot mới có Camera6, Font1, Material261, Sprite2185, TMP_FontAsset7:
**không còn row thiếu serialized_file**, toàn bộ row báo exported.

Linker ghép đúng `(serialized_file, path_id)`, đi theo `m_FileID` trong external
của owner. Không fallback theo pathID trần hay tên font. Trên **11 root record**
của 10 class được chọn (Tut_Settings1 có hai root):

| Thuộc tính | Tham chiếu nối đúng scope | Null |
|---|---:|---:|
| m_Sprite | 10.568 | 311 |
| m_fontAsset | 1.642 | 0 |
| m_sharedMaterial | 1.642 | 0 |

Đây là **số occurrence trong phần cây đã xuất**, không phải số asset khác nhau,
không bao hàm các thuộc tính khác hay font đổi động theo ngôn ngữ.
Không có unresolved trong ba nhóm này ở phạm vi đã chọn.

- Home: 277 node, không truncated; 27 font +27 material +96 sprite nối được.
- GP_Tutorials: 126 node, không truncated; 25 font +25 material +49 sprite nối được.
- **Map: 12.000 node, còn 2.760 transform trong queue; truncated=true.**
  Không được suy ra chỉ thiếu đúng 2.760 node vì chúng còn có thể có con.
- Lỗi cap80/con đã hết; nay chạm **global node budget**. Sửa tiếp default lên
  50.000, dùng deque để BFS không tốn O(n) mỗi lần pop. Giữ báo truncation và
  giới hạn gzip4MB; đây là thay đổi collector **chưa nghiệm thu raw lượt kế**.

## 2. Home_Loader thực sự tiêu thụ defaultBoard

`Home_Loader._Start_d__5.MoveNext @0x13be3a8` có nhánh nhận defaultBoard=6 và
chọn BoardID6. Common block:

1. `0x13be9a0...`: tạo BoardEvent với selectedBoard và LoadBoardMode0;
   constructor `0x123eac8` là `.ctor(BoardID id, LoadBoardMode mode)`.
2. `0x13be9c4`: eventID `0x38` = OpenBoard56; `0x13be9d4` gọi
   EventDispatcherExtension.PostEvent `0x1434cb4`.
3. `0x13be9f8`: reset defaultBoard về1.
4. Có FadeIn `0x13bb080`, rồi `0x13bea58` gọi CheckSpecPopup `0x13bd244`.

Điều này nối được phần **producer Continue → Home loader phát OpenBoard**, không
còn chỉ suy từ tên biến. Nhưng phát event chưa chứng minh board đã mở/render
xong; chưa chốt toàn bộ override và thứ tự popup hiển thị thực tế.

`CheckSpecPopup` raw đã giữ: exact metadata loads có Board_Endgame, Board_Home,
Shop_Gifts, Popup_WeekSales, Gift_Pack và hai callback CheckSpecPopup b__13_0/1.
**Chưa nâng lên một bảng ưu tiên popup** chỉ từ danh sách này: còn phải lần theo
nhánh điều kiện, callback, queue và trạng thái first-clear.

## 3. Sửa kết luận về persistence tutorial

- PlayerPreferences.SetInt `0x13f1a04` tailcall UnityEngine.PlayerPrefs.SetInt
  `0x277cc10`; GetInt `0x13f1a1c` tailcall PlayerPrefs.GetInt `0x277cca0`.
- Kết hợp evidence setter IndexTutorial ở report45: key TUTORIAL nằm trên
  **Unity PlayerPrefs**, không tự động thuộc dictionary lưu mã hóa riêng.
- SaveToDisk `0x13f1ab8` là nhánh khác:
  GetRawData → Encrypt → Encoding → File.WriteAllText `0x2077620`.
  OnApplicationQuit/OnApplicationFocus gọi nhánh này không chứng minh nó flush
  các int Unity PlayerPrefs.
- **OPEN:** callsite PlayerPrefs.Save hoặc bằng chứng vòng đời flush; đặc biệt
  không kết luận chống mất tutorial khi crash/kill chỉ vì có SaveToDisk.

## 4. Còn thiếu để tái dựng stage1–3 đáng tin

1. Nghiệm thu Map đầy đủ sau tăng global budget (không chỉ CI xanh).
2. Đọc hết Home_Loader overrides + CheckSpecPopup callback/queue/first-clear.
3. Đường PlayerPrefs.Save/reentry: tách thoát bình thường, focus và crash.
4. Active/enable, animation events, callback overlay và camera/viewport conversion
   ở runtime; binding font/sprite tĩnh đúng chưa đủ bảo đảm nhìn đúng mọi frame.
5. Đối chiếu end-to-end stage1→2→3: gate mở khóa, endgame re-enable và navigation
   trong từng nhánh thắng/thua/replay/continue. Không dùng screenshot để đoán.

26 unit tests pass ở lượt này; kiểm metadata chỉ là scanner ADRP/LDR bảo thủ,
không thay thế decompiler/control-flow analysis hay chạy APK thật.
