import { createRequire } from "module";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.argv[2] || path.join(here, "export");
const scale = Number(process.argv[3] || 2);
const SETS = [
  { file: "carousel", sel: ".slide", w: 1080, h: 1350, dir: "carousel", pdf: "Qudelta_The-rest-of-the-menu_carousel.pdf" },
  { file: "story", sel: ".story", w: 1080, h: 1920, dir: "stories", pdf: "Qudelta_The-rest-of-the-menu_stories.pdf" },
];

const browser = await chromium.launch();
for (const s of SETS) {
  if (!fs.existsSync(path.join(here, `${s.file}.html`))) continue;
  const dir = path.join(outDir, s.dir);
  fs.mkdirSync(dir, { recursive: true });
  const page = await browser.newPage({ viewport: { width: s.w, height: s.h }, deviceScaleFactor: scale });
  await page.goto("file://" + path.join(here, `${s.file}.html`));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  const els = await page.$$(s.sel);
  for (let i = 0; i < els.length; i++) {
    const file = path.join(dir, `${s.dir === "carousel" ? "slide" : "story"}-${String(i + 1).padStart(2, "0")}.png`);
    await els[i].screenshot({ path: file });
  }
  await page.pdf({ path: path.join(outDir, s.pdf), width: `${s.w}px`, height: `${s.h}px`, printBackground: true });
  console.log(`${s.file}: ${els.length} frames`);
  await page.close();
}
await browser.close();
