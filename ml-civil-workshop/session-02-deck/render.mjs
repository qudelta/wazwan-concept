import { createRequire } from "module";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.argv[2] || path.join(here, "export");
const scale = Number(process.argv[3] || 1);
fs.mkdirSync(path.join(outDir, "slides"), { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: scale });
await page.goto("file://" + path.join(here, "deck.html"));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(400);
const slides = await page.$$("section.slide");
for (let i = 0; i < slides.length; i++) {
  await slides[i].screenshot({ path: path.join(outDir, "slides", `slide-${String(i + 1).padStart(2, "0")}.png`) });
}
await page.pdf({ path: path.join(outDir, "Session-02_From-Raw-Engineering-Data-to-an-ML-Ready-Dataset_handout.pdf"), width: "1920px", height: "1080px", printBackground: true });
await browser.close();
console.log("rendered", slides.length, "slides");
