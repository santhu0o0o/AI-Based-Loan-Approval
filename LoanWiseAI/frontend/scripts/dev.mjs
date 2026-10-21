// Dev server: rebuilds on change, serves the SPA, proxies /api -> Flask.
//   npm run dev                      (API at http://localhost:5000)
//   API_TARGET=http://localhost:5055 npm run dev   (point at the mock)
import * as esbuild from 'esbuild';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { options, renderHtml, root } from './esbuild.config.mjs';

const PORT = Number(process.env.PORT || 5173);
const API = new URL(process.env.API_TARGET || 'http://localhost:5000');
const out = path.join(root, '.dev');
fs.mkdirSync(out, { recursive: true });

const writeHtml = {
  name: 'html',
  setup(build) {
    build.onEnd((r) => {
      if (!r.metafile) return;
      const tpl = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
      const reload = `<script>new EventSource('/esbuild').addEventListener('change',()=>location.reload())</script>`;
      fs.writeFileSync(path.join(out, 'index.html'), renderHtml(tpl, r.metafile, out).replace('</body>', reload + '</body>'));
    });
  },
};

const ctx = await esbuild.context({ ...options({ dev: true }), plugins: [writeHtml] });
await ctx.watch();
const { port: esPort } = await ctx.serve({ servedir: out, port: PORT + 1000, fallback: path.join(out, 'index.html') });

const pub = path.join(root, 'public');

http
  .createServer((req, res) => {
    const target = req.url.startsWith('/api')
      ? { host: API.hostname, port: API.port || 80 }
      : fs.existsSync(path.join(pub, req.url.split('?')[0])) && req.url !== '/'
        ? null
        : { host: '127.0.0.1', port: esPort };
    if (!target) return fs.createReadStream(path.join(pub, req.url.split('?')[0])).pipe(res);
    const p = http.request({ ...target, path: req.url, method: req.method, headers: req.headers }, (r) => {
      res.writeHead(r.statusCode, r.headers);
      r.pipe(res);
    });
    p.on('error', () => {
      res.writeHead(502, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ ok: false, message: "We couldn't reach the server. Is it running?" }));
    });
    req.pipe(p);
  })
  .listen(PORT, () => console.log(`\n  LoanWise dev server: http://localhost:${PORT}  (api -> ${API.origin})\n`));
