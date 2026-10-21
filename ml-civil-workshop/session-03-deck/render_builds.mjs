// Renders the click-by-click builds defined in builds.json.
//
// For every slide it writes
//   slides/slide-NN.png          the full slide (handout view)
//   builds/slide-NN-0.png        the slide with all build steps hidden (what the first view shows)
//   builds/slide-NN-K.png        a transparent overlay holding only what click K reveals,
//                                cropped to its bounding box (position recorded in builds/manifest.json)
// and a presenter PDF in which every click is its own page.
import { createRequire } from "module";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.argv[2] || path.join(here, "export");
const spec = JSON.parse(fs.readFileSync(path.join(here, "builds.json"), "utf8"));
const PAD = 36; // room for shadows and anti-aliasing around revealed elements

for (const d of ["slides", "builds"]) {
  fs.rmSync(path.join(outDir, d), { recursive: true, force: true });
  fs.mkdirSync(path.join(outDir, d), { recursive: true });
}

const CSS = `
  .hide-steps [data-step]{visibility:hidden !important}
  html.iso, html.iso body{background:transparent !important}
  html.iso .slide.iso-on{background:transparent !important;overflow:visible !important}
  html.iso .slide.iso-on, html.iso .slide.iso-on *{visibility:hidden !important}
  html.iso .slide.iso-on [data-on], html.iso .slide.iso-on [data-on] *{visibility:visible !important}
  .probe{position:absolute;z-index:999;pointer-events:none;background:transparent}
`;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto("file://" + path.join(here, "deck.html"));
await page.addStyleTag({ content: CSS });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(400);

// tag every build element with its step number, failing loudly on selectors that match nothing
const tagged = await page.evaluate((spec) => {
  const slides = [...document.querySelectorAll("section.slide")];
  const problems = [];
  for (const [key, steps] of Object.entries(spec)) {
    if (key.startsWith("_")) continue;
    const slide = slides[Number(key) - 1];
    if (!slide) { problems.push(`slide ${key} does not exist`); continue; }
    steps.forEach((sels, i) => sels.forEach((sel) => {
      const els = slide.querySelectorAll(sel);
      if (!els.length) problems.push(`slide ${key} step ${i + 1}: "${sel}" matched nothing`);
      els.forEach((el) => { el.dataset.step = String(i + 1); });
    }));
  }
  return { count: slides.length, problems };
}, spec);
if (tagged.problems.length) { console.error(tagged.problems.join("\n")); process.exit(1); }

const manifest = {};
const slides = await page.$$("section.slide");
for (let i = 0; i < slides.length; i++) {
  const n = i + 1, nn = String(n).padStart(2, "0");
  const slide = slides[i];
  await slide.screenshot({ path: path.join(outDir, "slides", `slide-${nn}.png`) });
  const steps = (spec[String(n)] || []).length;
  if (!steps) continue;

  await slide.evaluate((s) => s.classList.add("hide-steps"));
  await slide.screenshot({ path: path.join(outDir, "builds", `slide-${nn}-0.png`) });
  await slide.evaluate((s) => s.classList.remove("hide-steps"));

  manifest[n] = [];
  for (let k = 1; k <= steps; k++) {
    const box = await slide.evaluate((s, args) => {
      const [k, pad] = args;
      const sr = s.getBoundingClientRect();
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      s.querySelectorAll(`[data-step="${k}"]`).forEach((el) => {
        const r = el.getBoundingClientRect();
        x0 = Math.min(x0, r.left - sr.left); y0 = Math.min(y0, r.top - sr.top);
        x1 = Math.max(x1, r.right - sr.left); y1 = Math.max(y1, r.bottom - sr.top);
        el.dataset.on = "";
      });
      const b = { x: Math.max(0, Math.floor(x0 - pad)), y: Math.max(0, Math.floor(y0 - pad)) };
      b.w = Math.min(1920, Math.ceil(x1 + pad)) - b.x;
      b.h = Math.min(1080, Math.ceil(y1 + pad)) - b.y;
      const probe = document.createElement("div");
      probe.className = "probe";
      probe.dataset.on = "";
      Object.assign(probe.style, { left: b.x + "px", top: b.y + "px", width: b.w + "px", height: b.h + "px" });
      s.appendChild(probe);
      document.documentElement.classList.add("iso");
      s.classList.add("iso-on");
      return b;
    }, [k, PAD]);
    const file = `slide-${nn}-${k}.png`;
    await (await slide.$(".probe")).screenshot({ path: path.join(outDir, "builds", file), omitBackground: true });
    await slide.evaluate((s) => {
      s.querySelector(".probe").remove();
      s.querySelectorAll("[data-on]").forEach((el) => delete el.dataset.on);
      document.documentElement.classList.remove("iso");
      s.classList.remove("iso-on");
    });
    manifest[n].push({ step: k, file, ...box });
  }
}
fs.writeFileSync(path.join(outDir, "builds", "manifest.json"), JSON.stringify(manifest, null, 1));

// presenter PDF: before each built slide, insert one copy per earlier click state
await page.evaluate(() => {
  for (const s of [...document.querySelectorAll("section.slide")]) {
    const max = Math.max(0, ...[...s.querySelectorAll("[data-step]")].map((e) => Number(e.dataset.step)));
    for (let k = 0; k < max; k++) {
      const c = s.cloneNode(true);
      c.querySelectorAll("[data-step]").forEach((e) => { if (Number(e.dataset.step) > k) e.style.visibility = "hidden"; });
      s.before(c);
    }
  }
});
await page.evaluate(() => document.fonts.ready);
const pages = await page.evaluate(() => document.querySelectorAll("section.slide").length);
await page.pdf({ path: path.join(outDir, "Session-03_Your-First-Engineering-Prediction-Model_presenter-builds.pdf"), width: "1920px", height: "1080px", printBackground: true });
await browser.close();
console.log(`slides: ${tagged.count}; slides with builds: ${Object.keys(manifest).length}; clicks: ${Object.values(manifest).reduce((a, b) => a + b.length, 0)}; presenter pages: ${pages}`);
