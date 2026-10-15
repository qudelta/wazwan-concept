import { createRequire } from "module";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.argv[2] || path.join(here, "export");
const scale = Number(process.argv[3] || 2);
const NAMES = ["A_converging-roads", "B_the-list"];
fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch();
for (const theme of ["dark", "light"]) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: scale });
  await page.goto("file://" + path.join(here, `post-${theme}.html`));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const posts = await page.$$(".post");
  for (let i = 0; i < posts.length; i++) {
    const file = path.join(outDir, `Qudelta_All-roads-lead-to-sales_${NAMES[i]}_${theme}.png`);
    await posts[i].screenshot({ path: file });
    console.log("rendered", path.basename(file));
  }
  await page.close();
}
await browser.close();
