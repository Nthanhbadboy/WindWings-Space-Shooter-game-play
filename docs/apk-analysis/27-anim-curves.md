# 27 — Keyframe của AnimationClip (kết luận tạm thời)

> **Kết luận tạm thời.** Đọc bằng UnityPy `parse_as_object()` trên file gốc,
> khác với typetree ở `26-native-animation.md` (nơi mọi curve đều = 0).

- clip đọc được: **791**, lỗi parse: **0**
- clip có keyframe: **0**, tổng keyframe: **0**

**Reader này cũng không thấy keyframe nào** — curve nằm trong streamed clip
ở định dạng nén riêng; muốn lấy phải giải mã `m_StreamedClip` thủ công.
Kết luận thực dụng: dựng lại chuyển động Mecanim bằng số nhịp ở `26-native-animation.md`
(tên + thời lượng + loop + event), không chờ curve.
