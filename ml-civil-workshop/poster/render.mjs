import { createRequire } from "module";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const out = process.argv[2] || path.join(here, "export");
const scale = Number(process.argv[3] || 2);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: scale });
await page.goto("file://" + path.join(here, "poster.html"));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);
await page.screenshot({ path: `${out}.png`, clip: { x: 0, y: 0, width: 1080, height: 1350 } });
await page.pdf({ path: `${out}.pdf`, width: "1080px", height: "1350px", printBackground: true, pageRanges: "1" });
await browser.close();
console.log("rendered", out);
