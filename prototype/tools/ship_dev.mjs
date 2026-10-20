/**
 * Máy chủ xem trước riêng cho xưởng máy bay (ship.html).
 *
 *   node tools/ship_dev.mjs
 *
 * Vite ở chế độ middleware: mở thẳng trang xưởng ở "/" để bản LIVE PREVIEW
 * hiện đúng màn hình máy bay thay vì menu game.
 */
import { createServer } from 'vite';

const PORT = Number(process.env.SHIP_PORT || 5180);
const HOST = '0.0.0.0';

// Plugin này chèn middleware TRƯỚC chuỗi xử lý HTML mặc định của Vite,
// nhờ vậy "/" trả về ship.html thay vì menu game.
const openShipFirst = {
  name: 'ship-lab-root',
  configureServer(s) {
    s.middlewares.use((req, _res, next) => {
      const url = req.url || '/';
      if (url === '/' || url.startsWith('/?')) req.url = '/ship.html';
      next();
    });
  },
};

const server = await createServer({
  configFile: new URL('../vite.config.js', import.meta.url).pathname,
  server: { host: HOST, port: PORT, strictPort: true, allowedHosts: true, hmr: false },
  plugins: [openShipFirst],
});

await server.listen();

console.log(`Xưởng máy bay: http://localhost:${PORT}/ship.html`);
