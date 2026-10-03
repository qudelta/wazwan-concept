import { createRequire } from "module";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.argv[2] || path.join(here, "export");
const scale = Number(process.argv[3] || 2);
const themes = (process.argv[4] || "light,dark").split(",");

const browser = await chromium.launch();
for (const theme of themes) {
  const dir = path.join(outDir, theme);
  fs.mkdirSync(dir, { recursive: true });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: scale });
  await page.goto("file://" + path.join(here, `carousel-${theme}.html`));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const slides = await page.$$(".slide");
  for (let i = 0; i < slides.length; i++) {
    await slides[i].screenshot({ path: path.join(dir, `slide-${String(i + 1).padStart(2, "0")}.png`) });
  }
  await page.pdf({ path: path.join(dir, `Qudelta_Apna-hi-toh-hai_${theme}.pdf`), width: "1080px", height: "1350px", printBackground: true });
  await page.close();
  console.log(theme, slides.length, "slides");
}
await browser.close();
