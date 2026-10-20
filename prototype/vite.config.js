import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';

const page = (name) => fileURLToPath(new URL(name, import.meta.url));

// Asset dùng trực tiếp từ ../assets_samples (không copy, không nhân đôi dung lượng).
export default defineConfig({
  publicDir: '../assets_samples',
  base: './',
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    allowedHosts: true,
    hmr: false,
  },
  build: {
    target: 'es2022',
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: page('index.html'),
        ship: page('ship.html'),
        // bản thử 2D đơn giản: tách bộ phận tàu omen + hoạt cảnh mặt phẳng
        shipdemo: page('shipdemo.html'),
        // phòng thử UI: dựng lại HUD/linh kiện WindWings từ ảnh chụp thật
        uikit: page('uikit.html'),
      },
    },
  },
});
