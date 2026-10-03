import { createRequire } from "module";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.argv[2] || path.join(here, "export");
const scale = Number(process.argv[3] || 2);

const designs = [
  { prefix: "poster", out: "AI-ML-for-Civil-Engineers_poster" },
  { prefix: "poster-minimal", out: "AI-ML-for-Civil-Engineers_poster-minimal" },
  { prefix: "web-landscape", out: "web/AI-ML-for-Civil-Engineers_website_16x9", width: 1600, height: 900 },
  { prefix: "web-portrait", out: "web/AI-ML-for-Civil-Engineers_website_4x5" },
  { prefix: "group", out: "AI-ML-for-Civil-Engineers_group-pricing" },
];

const browser = await chromium.launch();
for (const d of designs) for (const theme of ["light", "dark"]) {
  const w = d.width || 1080, h = d.height || 1350;
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
  await page.goto("file://" + path.join(here, `${d.prefix}-${theme}.html`));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const out = path.join(outDir, `${d.out}_${theme}`);
  await page.screenshot({ path: `${out}.png`, clip: { x: 0, y: 0, width: w, height: h } });
  await page.pdf({ path: `${out}.pdf`, width: `${w}px`, height: `${h}px`, printBackground: true, pageRanges: "1" });
  await page.close();
  console.log("rendered", out);
}
await browser.close();
