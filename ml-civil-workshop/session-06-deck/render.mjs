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
// the handout shows each slide's final state: remove what exit clicks (builds.json) take away
const spec = JSON.parse(fs.readFileSync(path.join(here, "builds.json"), "utf8"));
await page.evaluate((spec) => {
  const all = [...document.querySelectorAll("section.slide")];
  for (const [key, steps] of Object.entries(spec)) {
    if (key.startsWith("_")) continue;
    for (const st of steps) if (!Array.isArray(st) && st.fx === "exit") st.sel.forEach((sel) => all[Number(key) - 1].querySelectorAll(sel).forEach((e) => { e.style.visibility = "hidden"; }));
  }
}, spec);
await page.pdf({ path: path.join(outDir, "Session-06_Artificial-Neural-Networks_Engineering-Prediction_handout.pdf"), width: "1920px", height: "1080px", printBackground: true });
await browser.close();
console.log("rendered", slides.length, "slides");
