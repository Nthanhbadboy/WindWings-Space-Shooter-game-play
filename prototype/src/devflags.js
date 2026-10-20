/**
 * CỜ TEST TẠM THỜI — bật khi cần thử nhanh nội dung.
 *
 * Khi phát hành cho người chơi: đổi TẤT CẢ về `false`
 * (hoặc xoá file và các chỗ import).
 *
 *  - TEST_UNLOCK_ALL : mở hết 3 chương × 6 màn, không cần có sao
 *  - TEST_AUTO_FIRE  : luôn tự động bắn, bỏ qua lựa chọn trong Cài đặt
 *  - TEST_RICH       : (tuỳ chọn) tặng vàng/gem lúc khởi động để thử hangar
 *
 * Bộ test tự tắt các cờ này bằng `globalThis.__WW_TEST_OVERRIDE__`
 * (xem `tests/ui.mjs`) để vẫn kiểm tra được logic khoá màn thật.
 */
const override = (typeof globalThis !== 'undefined' && globalThis.__WW_TEST_OVERRIDE__) || null;
const flag = (name, fallback) => (override && typeof override[name] === 'boolean' ? override[name] : fallback);

export const TEST_UNLOCK_ALL = flag('unlockAll', true);
export const TEST_AUTO_FIRE = flag('autoFire', true);
export const TEST_RICH = flag('rich', false);

/** Số vàng/gem tặng khi TEST_RICH bật. */
export const TEST_RICH_COINS = 50000;
export const TEST_RICH_GEMS = 500;
