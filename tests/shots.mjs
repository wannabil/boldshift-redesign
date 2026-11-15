// Full-page screenshots + basic QA (overflow, console errors, failed requests).
// Usage: node tests/shots.mjs <baseUrl> <outDir>
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';

const base = process.argv[2] || 'http://127.0.0.1:4823';
const out = process.argv[3] || 'tests/shots';
fs.mkdirSync(out, { recursive: true });
const pages = ['/', '/individuals', '/corporate-training', '/about', '/free-tools', '/contact', '/nope-404'];
const sizes = [{ n: 'desk', w: 1366, h: 900, m: false }, { n: 'phone', w: 390, h: 844, m: true }];
const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new', args: ['--no-sandbox', '--hide-scrollbars'],
});
let problems = 0;
for (const s of sizes) {
  for (const p of pages) {
    const page = await browser.newPage();
    await page.setViewport({ width: s.w, height: s.h, isMobile: s.m, hasTouch: s.m, deviceScaleFactor: 1 });
    const errs = [];
    page.on('console', (m) => { if (m.type() === 'error' && !(p.includes('nope-404') && m.text().includes('404'))) errs.push(m.text()); });
    page.on('pageerror', (e) => errs.push(String(e)));
    page.on('response', (r) => { if (r.status() >= 400 && !r.url().includes('nope-404')) errs.push(`${r.status()} ${r.url()}`); });
    await page.goto(base + p, { waitUntil: 'networkidle0' });
    // reveal everything for the full-page capture
    await page.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 500) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); }
      scrollTo(0, 0);
      document.querySelectorAll('.rv').forEach((e) => e.classList.add('in'));
      await document.fonts.ready;
    });
    await new Promise((r) => setTimeout(r, 900));
    const q = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth - innerWidth,
      h1: document.querySelectorAll('h1').length,
      title: document.title,
    }));
    const name = `${s.n}-${p === '/' ? 'home' : p.slice(1)}.png`;
    await page.screenshot({ path: `${out}/${name}`, fullPage: true });
    const bad = q.overflow > 0 || q.h1 !== 1 || errs.length;
    if (bad) problems++;
    console.log(`${bad ? '✗' : '✓'} ${s.n} ${p} overflow=${q.overflow} h1=${q.h1} errs=${JSON.stringify(errs)}`);
    await page.close();
  }
}
await browser.close();
console.log(problems ? `${problems} problem page(s)` : 'all clean');
process.exit(problems ? 1 : 0);
