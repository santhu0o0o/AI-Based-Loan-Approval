// Visual check: screenshots every page/state at desktop and phone widths.
//   npm run build && npm run mock    (in one shell)
//   node scripts/screenshots.mjs [baseUrl] [outDir]
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = require('playwright'));
} catch {
  ({ chromium } = require('/opt/npm-tools/node_modules/playwright'));
}

const BASE = process.argv[2] || 'http://localhost:5055';
const OUT = path.resolve(process.argv[3] || '../docs/screenshots');
fs.mkdirSync(OUT, { recursive: true });
const only = process.env.ONLY ? process.env.ONLY.split(',') : null;

const exe = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome', '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));
const browser = await chromium.launch(exe ? { executablePath: exe } : {});
const sizes = [
  ['desktop', { width: 1440, height: 900 }],
  ['mobile', { width: 390, height: 844 }],
];

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const tap = (page, text) => page.locator('label.choice', { hasText: text }).first().click();

async function fillAll(page, { good = true } = {}) {
  await page.goto(`${BASE}/check`);
  await page.evaluate(() => sessionStorage.clear());
  await page.goto(`${BASE}/check`);
  await tap(page, 'Woman');
  await tap(page, 'Yes, married');
  await tap(page, '1 person');
  await tap(page, 'Yes, I graduated');
  await tap(page, 'I get a salary');
  await page.getByRole('button', { name: /Next: Your money/ }).click();
  await wait(400);
  await page.locator('[data-field="applicant_income"] input').fill(good ? '48000' : '16000');
  await page.locator('[data-field="coapplicant_income"] input').fill(good ? '22000' : '0');
  await tap(page, good ? 'Yes, always on time' : 'No, I was late');
  await page.getByRole('button', { name: /Next: Your loan/ }).click();
  await wait(400);
  await page.locator('[data-field="loan_amount"] input').fill(good ? '2500000' : '3000000');
  await tap(page, good ? '20 years' : '10 years');
  await tap(page, good ? 'Near a city' : 'In a city');
}

const shots = {
  async home(page) {
    await page.goto(`${BASE}/`);
    await wait(3200);
  },
  async 'check-empty'(page) {
    await page.goto(`${BASE}/check`);
    await page.evaluate(() => sessionStorage.clear());
    await page.goto(`${BASE}/check`);
    await wait(500);
  },
  async 'check-errors'(page) {
    await page.goto(`${BASE}/check`);
    await page.evaluate(() => sessionStorage.clear());
    await page.goto(`${BASE}/check`);
    await tap(page, 'Man');
    await page.getByRole('button', { name: /Next: Your money/ }).click();
    await wait(900);
    await page.evaluate(() => window.scrollTo(0, 0));
    await wait(200);
  },
  async 'check-money'(page) {
    await fillAll(page);
    await page.getByRole('button', { name: 'Back', exact: true }).click();
    await wait(500);
    await page.locator('[data-field="applicant_income"] .help-btn').click();
    await page.locator('[data-field="coapplicant_income"] input').fill('1');
    await page.locator('[data-field="coapplicant_income"] input').fill('');
    await page.locator('[data-field="coapplicant_income"] input').blur();
    await tap(page, 'I never had a loan');
    await wait(500);
    await page.evaluate(() => window.scrollTo(0, 0));
    await wait(200);
  },
  async 'check-loan-ready'(page) {
    await fillAll(page);
    await wait(400);
    await page.evaluate(() => window.scrollTo(0, 0));
  },
  async 'result-approved'(page) {
    await fillAll(page, { good: true });
    await page.getByRole('button', { name: 'See my result' }).click();
    await page.waitForURL(/result/);
    await wait(1700);
  },
  async 'result-rejected'(page) {
    await fillAll(page, { good: false });
    await page.getByRole('button', { name: 'See my result' }).click();
    await page.waitForURL(/result/);
    await wait(2600);
  },
  async 'how-it-works'(page) {
    await page.goto(`${BASE}/how-it-works`);
    await wait(800);
    await page.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 400) {
        window.scrollTo(0, y);
        await new Promise((r) => setTimeout(r, 120));
      }
      window.scrollTo(0, 0);
    });
    await wait(1200);
  },
  async 'how-it-works-no-api'(page) {
    await page.route('**/api/model-info', (r) => r.fulfill({ status: 502, body: '' }));
    await page.goto(`${BASE}/how-it-works`);
    await wait(1500);
  },
  async history(page) {
    await page.goto(`${BASE}/history`);
    await wait(900);
  },
  async 'history-confirm'(page) {
    await page.goto(`${BASE}/history`);
    await wait(700);
    await page.getByRole('button', { name: 'Delete all' }).click();
    await wait(600);
  },
  async 'history-empty'(page) {
    await page.route('**/api/history*', (r) => r.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true,"items":[]}' }));
    await page.goto(`${BASE}/history`);
    await wait(900);
  },
  async 'network-error'(page) {
    await page.goto(`${BASE}/check`);
    await page.evaluate(() => sessionStorage.clear());
    await page.route('**/api/**', (r) => r.abort('connectionrefused'));
    await page.goto(`${BASE}/check`);
    await page.getByRole('button', { name: /Fill an example/ }).click();
    await wait(900);
  },
  async 'server-422'(page) {
    await fillAll(page);
    await page.locator('[data-field="loan_amount"] input').fill('404040');
    await page.getByRole('button', { name: 'See my result' }).click();
    await wait(1200);
  },
  async 'mobile-menu'(page, kind) {
    if (kind !== 'mobile') return false;
    await page.goto(`${BASE}/`);
    await wait(400);
    await page.getByRole('button', { name: /Menu/ }).click();
    await wait(500);
  },
  async 'not-found'(page) {
    await page.goto(`${BASE}/nope/this/is/missing`);
    await wait(800);
  },
};

const fullPage = new Set(['home', 'check-empty', 'check-errors', 'check-money', 'check-loan-ready', 'result-approved', 'result-rejected', 'how-it-works', 'history', 'history-empty', 'server-422', 'not-found']);
const errors = [];
for (const [kind, viewport] of sizes) {
  for (const [name, fn] of Object.entries(shots)) {
    if (only && !only.includes(name)) continue;
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    page.on('pageerror', (e) => errors.push(`${name}/${kind}: ${e.message}`));
    page.on('console', (m) => m.type() === 'error' && !/Failed to load resource/.test(m.text()) && errors.push(`${name}/${kind} console: ${m.text()}`));
    try {
      const r = await fn(page, kind);
      if (r !== false) {
        const file = path.join(OUT, `${name}-${kind}.png`);
        await page.screenshot({ path: file, fullPage: fullPage.has(name) });
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        console.log(`${file}${overflow > 0 ? `  (HORIZONTAL OVERFLOW ${overflow}px)` : ''}`);
      }
    } catch (e) {
      errors.push(`${name}/${kind}: ${e.message.split('\n')[0]}`);
    }
    await ctx.close();
  }
}
await browser.close();
if (errors.length) console.log('\nISSUES:\n' + errors.join('\n'));
