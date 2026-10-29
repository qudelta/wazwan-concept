import { createRequire } from "module";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.argv[2] || path.join(here, "export");
const scale = Number(process.argv[3] || 2);
const W = 1080;

async function open(browser, file, w, h, dsf) {
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: dsf });
  await page.goto("file://" + path.join(here, file));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  return page;
}

// Pages of PNGs → one PDF (so the PDF matches the PNGs exactly)
async function pdfFrom(browser, files, w, h, out) {
  const page = await browser.newPage();
  const imgs = files.map((f) => `<img src="file://${f}" style="display:block;width:${w}px;height:${h}px;break-after:page">`).join("");
  await page.setContent(`<style>@page{size:${w}px ${h}px;margin:0}body{margin:0}</style>${imgs}`, { waitUntil: "load" });
  await page.pdf({ path: out, width: `${w}px`, height: `${h}px`, printBackground: true });
  await page.close();
}

const browser = await chromium.launch();

// Carousel: one 12960 × 1350 panorama, cut into 1080 × 1350 slides
{
  const dir = path.join(outDir, "carousel");
  fs.mkdirSync(dir, { recursive: true });
  const page = await open(browser, "carousel.html", W, 1350, scale);
  const n = await page.evaluate(() => document.querySelectorAll(".s").length);
  const files = [];
  for (let i = 0; i < n; i++) {
    await page.evaluate((x) => { document.querySelector(".pano").style.transform = `translateX(${-x}px)`; }, i * W);
    const file = path.join(dir, `slide-${String(i + 1).padStart(2, "0")}.png`);
    await page.screenshot({ path: file, clip: { x: 0, y: 0, width: W, height: 1350 } });
    files.push(file);
  }
  await page.close();
  await pdfFrom(browser, files, W, 1350, path.join(outDir, "Qudelta_The-rest-of-the-menu_carousel.pdf"));
  const pv = await open(browser, "carousel.html", n * W, 1350, 0.25);
  await pv.screenshot({ path: path.join(outDir, "Qudelta_The-rest-of-the-menu_panorama-preview.png") });
  await pv.close();
  console.log(`carousel: ${n} slides`);
}

// Stories: separate 1080 × 1920 frames
if (fs.existsSync(path.join(here, "story.html"))) {
  const dir = path.join(outDir, "stories");
  fs.mkdirSync(dir, { recursive: true });
  const page = await open(browser, "story.html", W, 1920, scale);
  const els = await page.$$(".story");
  const files = [];
  for (let i = 0; i < els.length; i++) {
    const file = path.join(dir, `story-${String(i + 1).padStart(2, "0")}.png`);
    await els[i].screenshot({ path: file });
    files.push(file);
  }
  await page.close();
  await pdfFrom(browser, files, W, 1920, path.join(outDir, "Qudelta_The-rest-of-the-menu_stories.pdf"));
  console.log(`stories: ${els.length} frames`);
}
await browser.close();
