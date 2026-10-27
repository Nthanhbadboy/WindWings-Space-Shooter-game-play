# PROMPTS — nhật ký sinh ảnh hero PLAYER ID 10001 (hướng A Ink & Ember)

Session: `arena/f2272cda-windwings-space-shooter-game-p` · ngày 2026-10-27 · VISION-ATTEST: CÓ
Công cụ: generate_image (text-to-image và image-edit). Mọi pass đều được tác giả TỰ XEM lại bằng
công cụ đọc ảnh trước khi quyết định giữ/sửa; không pass nào được nộp mà chưa nhìn.

## Reference nạp vào model (pass 3–4)
- `process/ref_tile01.png` = crop ô #1 của `docs/assets/contact-sheets/ships-01.jpg`
  (sheet sha256 `82862b8b1eef77159c4aa09ffb04a478f1b3307c1259eaf99600fc1be01a613b`),
  ô #1 = ID 10001 theo `docs/assets/sprites-index.csv` (`ships,10001,Sprite,3581,…,ships-01.jpg,1`)
  và `datas/ships.json` (`id 10001, sprite_path_id 3581`).
- Lưới sheet đo bằng pixel: tile 150×150, hàng bắt đầu y=26, cột x=0,150,…; crop theo bbox
  artwork, bỏ dải nhãn #n.

## Pass 1 — `hero_v1_raw.png` (text-only)
Prompt: top-down orthographic, một tàu, nền magenta phẳng; palette Ink & Ember; giáp 2–3 lớp;
canopy hổ phách; vent/rivet/panel-line; rim-light từ trên; không viền đen.
**Tự xem → loại:** planform cánh dài-thẳng giống máy bay thật (gốc #1 là delta cụp mũi tên);
hull xám trung tính chứ không ink xanh đen; canopy dạng khối đồng thiếu chất kính; rim-light yếu.

## Pass 2 — edit từ v1 (yêu cầu cụp cánh + đổi palette)
**Tự xem → loại:** model edit trả về gần như đúng ảnh v1 (cùng planform, cùng xám). Kết luận:
edit-pass không đáng tin cho thay đổi cấu trúc → chuyển chiến lược.

## Pass 3 — `hero_v3_raw.png` (reference #1 + prompt redesign)
**Tự xem → giữ hướng, sửa tiếp:** planform delta gọn đúng keluarga game, giáp lớp/vent/rivet/
nozzle glow đạt; NHẬN ĐỊNH MẮT ban đầu: "canopy quá to". **Kiểm chứng bằng số** (bbox connected
component màu hổ phách / bbox tàu): gốc #1 = 0.22 chiều dài × 0.15 chiều rộng; v3 = 0.22 × 0.15
⇒ **khớp gốc chính xác**, cảm giác "to" là do khung kính tối bao quanh. Sai lầm thị giác của tác giả
được số sửa → không thu nhỏ canopy nữa.

## Pass 4 — `hero_v4_raw.png` = **NGUỒN ĐƯỢC CHỌN** (`process/gen_raw_v4.png`)
Edit từ v3, chỉ yêu cầu: mũi có 2 lớp giáp + khe sensor; khối đuôi rộng hơn + 2 tab ember;
vent/nozzle sáng hơn; giữ nguyên phần còn lại.
**Tự xem → đạt:** mũi/đuôi có kết cấu; tỷ lệ đo được khớp gốc; vật liệu kim loại/kính/emissive
phân biệt; AO ở mối nối; rim-light trên; không viền đen dày.

## Pass 5 — `hero_v5_raw.png` (text-only, ràng buộc tỷ lệ cứng)
**Tự xem → loại:** model xoay tàu 90° (mũi trái) dù prompt nói mũi lên; canopy 0.08×0.12 (quá nhỏ
so chữ ký 0.22×0.15 của gốc). Giữ lại làm bằng chứng rằng ràng buộc tỷ lệ bằng lời là không đủ.

## Hậu kỳ bắt buộc (script, tái lập được — `build_hero.py`)
1. Key nền magenta → alpha bằng connected-component chạm biên (trông nhầm tông tím bóng đổ
   bên trong thân thành pixel bán trong suốt — lỗi đã tự phát hiện và sửa).
2. Khử halo noise magenta 2–8% quanh ship (ngưỡng 0.08/×1.12).
3. Unpremultiply/despill viền AA.
4. Crop bbox → pad vuông, subject chiếm 86.7% canvas (= 130/150 px đo từ ô gốc) → master 1024
   lossless → sprite 256 (LANCZOS) → bản kiểm 64.
5. Grade art-direction (S-curve 3 vùng + bão hoà ×1.02, tham số mặc định trong `build_hero.py`):
   nâng sàn gần-đen để bỏ viền/AO đen sì (dark_share 0.163 → 0.007), tăng trải sáng
   (val_std 0.199 → 0.241), val 0.339 → 0.505. Mục đích: hướng A tối nhưng ĐỌC ĐƯỢC trên nền
   gameplay ink900 — KHÔNG phải để lấy PASS (chỉ số `colors` vẫn lệch và sẽ luôn lệch, xem SELF_REVIEW).
