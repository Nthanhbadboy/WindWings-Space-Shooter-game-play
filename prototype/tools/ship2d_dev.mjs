/**
 * Máy chủ xem trước cho bản thử 2D của tàu (shipdemo.html).
 *
 *   npm run dev:ship2d
 *
 * Vite middleware: mở "/" là ra thẳng trang thử 2D, tiện cho LIVE PREVIEW.
 */
import { createServer } from 'vite';

const PORT = Number(process.env.SHIP2D_PORT || 5190);
const HOST = '0.0.0.0';

const openDemoFirst = {
  name: 'ship2d-root',
  configureServer(s) {
    s.middlewares.use((req, _res, next) => {
      const url = req.url || '/';
      if (url === '/' || url.startsWith('/?')) req.url = '/shipdemo.html';
      next();
    });
  },
};

const server = await createServer({
  configFile: new URL('../vite.config.js', import.meta.url).pathname,
  server: { host: HOST, port: PORT, strictPort: true, allowedHosts: true, hmr: false },
  plugins: [openDemoFirst],
});

await server.listen();
console.log(`Thử tàu 2D: http://localhost:${PORT}/shipdemo.html`);
