import { createRequire } from "module";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.argv[2] || path.join(here, "export");
const scale = Number(process.argv[3] || 2);

const designs = [
  { prefix: "poster", out: "NPS-Qudelta_AI-Technology-session", width: 1080, height: 1350 },
  { prefix: "poster-b", out: "NPS-Qudelta_AI-Technology-session_centered", width: 1080, height: 1620 },
];

const browser = await chromium.launch();
for (const d of designs) {
  for (const theme of ["light", "dark"]) {
    const page = await browser.newPage({ viewport: { width: d.width, height: d.height }, deviceScaleFactor: scale });
    await page.goto("file://" + path.join(here, `${d.prefix}-${theme}.html`));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(300);
    const out = path.join(outDir, `${d.out}_${theme}`);
    await page.screenshot({ path: `${out}.png`, clip: { x: 0, y: 0, width: d.width, height: d.height } });
    await page.pdf({ path: `${out}.pdf`, width: `${d.width}px`, height: `${d.height}px`, printBackground: true, pageRanges: "1" });
    await page.close();
    console.log("rendered", out);
  }
}
await browser.close();
