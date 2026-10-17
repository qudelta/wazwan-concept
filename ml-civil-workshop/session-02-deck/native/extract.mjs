// Reads the rendered deck (deck.html) and describes every slide as PowerPoint-ready objects:
//   shape  - a box with fill, border, rounded corners and shadow (cards, chips, bars, rules)
//   text   - a text box: lines as laid out by the browser, each line a list of styled runs
//   raster - something PowerPoint cannot draw natively (icons, logos, photo, charts, gradients),
//            captured as a transparent PNG at 2x
// Every object records which click (builds.json) reveals it and which card it belongs to, so the
// PowerPoint builder can group cards and animate each click.
//
// Usage: node native/extract.mjs <out_dir>
import { createRequire } from "module";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const deckDir = path.dirname(here);
const outDir = process.argv[2] || path.join(here, "out");
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(path.join(outDir, "img"), { recursive: true });
const spec = JSON.parse(fs.readFileSync(path.join(deckDir, "builds.json"), "utf8"));

const ISO = `
  html.iso, html.iso body{background:transparent !important}
  html.iso .slide.iso-on{background:transparent !important}
  html.iso .slide.iso-on, html.iso .slide.iso-on *{visibility:hidden !important}
  html.iso .slide.iso-on [data-on], html.iso .slide.iso-on [data-on] *{visibility:visible !important}
  html.iso .slide.iso-on [data-own]{visibility:visible !important}
  [data-nopseudo]::before,[data-nopseudo]::after{content:none !important}
`;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
await page.goto("file://" + path.join(deckDir, "deck.html"));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(400);

// tag build steps exactly as render_builds.mjs does
await page.evaluate((spec) => {
  const slides = [...document.querySelectorAll("section.slide")];
  for (const [key, steps] of Object.entries(spec)) {
    if (key.startsWith("_")) continue;
    const slide = slides[Number(key) - 1];
    steps.forEach((sels, i) => sels.forEach((sel) => slide.querySelectorAll(sel).forEach((el) => { el.dataset.step = String(i + 1); })));
  }
}, spec);

// turn ::before / ::after into real elements so they can be converted too
await page.evaluate(() => {
  for (const el of [...document.querySelectorAll("section.slide *")]) {
    for (const pseudo of ["::before", "::after"]) {
      const cs = getComputedStyle(el, pseudo);
      if (!cs.content || cs.content === "none" || cs.content === "normal") continue;
      const span = document.createElement("span");
      for (let i = 0; i < cs.length; i++) span.style.setProperty(cs[i], cs.getPropertyValue(cs[i]));
      span.style.setProperty("content", "normal");
      const m = cs.content.match(/^"(.*)"$/);
      span.textContent = m ? m[1] : "";
      span.dataset.pseudo = pseudo;
      if (pseudo === "::before") el.prepend(span); else el.append(span);
      el.dataset.nopseudo = "1";
    }
  }
});
await page.addStyleTag({ content: ISO });
await page.waitForTimeout(100);

const slides = await page.evaluate(() => {
  const METRICS = { Archivo: [0.878, 0.21], "JetBrains Mono": [1.02, 0.3] };  // hhea ascent / descent per em
  let eid = 0;
  const id = (el) => el.dataset.eid || (el.dataset.eid = String(++eid));

  function color(s) {
    if (!s) return null;
    let m = s.match(/rgba?\(([^)]+)\)/);
    if (m) { const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
    m = s.match(/color\(srgb ([^)]+)\)/);
    if (m) { const p = m[1].split(/[\s\/]+/).filter(Boolean).map(Number); return [p[0] * 255, p[1] * 255, p[2] * 255, p.length > 3 ? p[3] : 1]; }
    return null;
  }
  const visible = (c) => c && c[3] > 0.004;
  const fam = (cs) => cs.fontFamily.split(",")[0].replace(/["']/g, "").trim();
  const px = (v) => parseFloat(v) || 0;

  function clipRect(el, slide, r) {
    let { left: x0, top: y0, right: x1, bottom: y1 } = r;
    for (let a = el.parentElement; a && a !== slide.parentElement; a = a.parentElement) {
      const cs = getComputedStyle(a);
      if (cs.overflow !== "visible" || a === slide) {
        const ar = a.getBoundingClientRect();
        x0 = Math.max(x0, ar.left); y0 = Math.max(y0, ar.top); x1 = Math.min(x1, ar.right); y1 = Math.min(y1, ar.bottom);
      }
    }
    return { x0, y0, x1, y1 };
  }

  // rounded corners inherited from an overflow:hidden ancestor whose corner this box touches
  function corners(el, r, cs, slide) {
    const own = ["TopLeft", "TopRight", "BottomRight", "BottomLeft"].map((k) => {
      const v = cs[`border${k}Radius`];
      return v.includes("%") ? (px(v) / 100) * Math.min(r.width, r.height) : px(v);
    });
    for (let a = el.parentElement; a && a !== slide; a = a.parentElement) {
      const acs = getComputedStyle(a);
      if (acs.overflow === "visible") continue;
      const ar = a.getBoundingClientRect();
      const rad = ["TopLeft", "TopRight", "BottomRight", "BottomLeft"].map((k) => px(acs[`border${k}Radius`]));
      const near = (p, q) => Math.abs(p - q) < 1.5;
      const hit = [near(r.left, ar.left) && near(r.top, ar.top), near(r.right, ar.right) && near(r.top, ar.top),
                   near(r.right, ar.right) && near(r.bottom, ar.bottom), near(r.left, ar.left) && near(r.bottom, ar.bottom)];
      hit.forEach((h, i) => { if (h) own[i] = Math.max(own[i], rad[i]); });
    }
    return own.map((v) => Math.min(v, Math.min(r.width, r.height) / 2));
  }

  function shadow(cs) {
    if (!cs.boxShadow || cs.boxShadow === "none") return null;
    const first = cs.boxShadow.split(/,(?![^(]*\))/)[0];
    const c = color(first);
    const nums = first.replace(/rgba?\([^)]*\)|color\([^)]*\)/, "").trim().split(/\s+/).map(px);
    return c ? { color: c, x: nums[0], y: nums[1], blur: nums[2] || 0 } : null;
  }

  const items = [];
  let order = 0;

  function ctxFor(el, slide) {
    const step = el.closest("[data-step]");
    let card = null;
    for (let a = el; a && a !== slide; a = a.parentElement) {
      if (step && a === step) break;
      if (a.dataset.card) card = a.dataset.eid;   // outermost card below the step boundary
    }
    return { step: step ? Number(step.dataset.step) : 0, stepEl: step ? id(step) : null, card };
  }

  function push(slide, el, item) {
    item.order = order++;
    Object.assign(item, ctxFor(el, slide));
    items.push(item);
  }

  function runStyle(el, P, opacity) {
    const cs = getComputedStyle(el);
    let highlight = null, valign = "baseline";
    for (let a = el; a && a !== P; a = a.parentElement) {
      const acs = getComputedStyle(a);
      if (!highlight) {
        const bg = color(acs.backgroundColor);
        if (visible(bg)) highlight = bg;
        else if (acs.backgroundImage.includes("gradient")) {
          const cols = [...acs.backgroundImage.matchAll(/(rgba?\([^)]*\)|color\(srgb[^)]*\))/g)].map((m) => color(m[1])).filter(visible);
          if (cols.length) highlight = cols[cols.length - 1];
        }
      }
      if (acs.verticalAlign === "sub" || acs.verticalAlign === "super") valign = acs.verticalAlign;
      if (a.tagName === "SUB") valign = "sub";
      if (a.tagName === "SUP") valign = "super";
    }
    const c = color(cs.color);
    return {
      family: fam(cs), weight: Number(cs.fontWeight) || 400, stretch: px(cs.fontStretch) || 100,
      italic: cs.fontStyle === "italic", size: px(cs.fontSize), color: c ? [c[0], c[1], c[2], c[3] * opacity] : [0, 0, 0, 1],
      spacing: cs.letterSpacing === "normal" ? 0 : px(cs.letterSpacing), caps: cs.textTransform === "uppercase",
      wordSpacing: cs.wordSpacing === "normal" ? 0 : px(cs.wordSpacing),
      highlight, valign,
    };
  }

  function textGroup(slide, P, nodes, opacity, sr) {
    const pcs = getComputedStyle(P);
    const pre = pcs.whiteSpace.startsWith("pre");
    const chars = [];
    const range = document.createRange();
    const walk = (n) => {
      if (n.nodeType === 3) {
        const st = runStyle(n.parentElement, P, opacity);
        for (let i = 0; i < n.data.length; i++) {
          let ch = n.data[i];
          if (ch === "\n" && pre) continue;
          if (/\s/.test(ch)) ch = " ";
          range.setStart(n, i); range.setEnd(n, i + 1);
          const rs = range.getClientRects();
          if (!rs.length) continue;
          const r = rs[rs.length - 1];
          if (r.width === 0 && ch === " ") continue;
          let cst = st;
          if (ch === " " && st.wordSpacing) cst = { ...st, spacing: st.spacing + st.wordSpacing };
          chars.push({ ch, x: r.left - sr.left, y: r.top - sr.top, w: r.width, h: r.height, st: cst });
        }
      } else if (n.nodeType === 1) {
        if (n.tagName === "BR") chars.push({ br: true });
        else for (const c of n.childNodes) walk(c);
      }
    };
    nodes.forEach(walk);
    if (!chars.some((c) => !c.br && c.ch.trim())) return null;

    const lines = [];
    let cur = null;
    for (const c of chars) {
      if (c.br) { cur = null; continue; }
      const cy = c.y + c.h / 2;
      if (!cur || cy > cur.bottom) { cur = { chars: [], top: c.y, bottom: c.y + c.h }; lines.push(cur); }
      cur.chars.push(c);
      cur.top = Math.min(cur.top, c.y); cur.bottom = Math.max(cur.bottom, c.y + c.h);
    }
    const out = [];
    for (const ln of lines) {
      let cs = ln.chars;
      if (!pre) {
        while (cs.length && cs[0].ch === " ") cs = cs.slice(1);
        while (cs.length && cs[cs.length - 1].ch === " ") cs = cs.slice(0, -1);
      }
      if (!cs.length) continue;
      // baseline from the largest glyph set in a font we know the metrics of
      let base = null, size = 0;
      for (const c of cs) {
        const m = METRICS[c.st.family];
        if (m && c.st.valign === "baseline" && c.st.size >= size && Math.abs(c.h - (m[0] + m[1]) * c.st.size) < c.st.size * 0.08) {
          size = c.st.size; base = c.y + m[0] * c.st.size;
        }
      }
      if (base === null) { size = Math.max(...cs.map((c) => c.st.size)); base = ln.bottom - 0.21 * size; }
      const runs = [];
      for (const c of cs) {
        const last = runs[runs.length - 1];
        if (last && JSON.stringify(last.st) === JSON.stringify(c.st)) last.text += c.ch;
        else runs.push({ text: c.ch, st: c.st });
      }
      out.push({ runs, x0: cs[0].x, x1: cs[cs.length - 1].x + cs[cs.length - 1].w, base, size });
    }
    if (!out.length) return null;
    let lh = px(pcs.lineHeight) || Math.max(...out.map((l) => l.size)) * 1.2;
    if (out.length > 1) {
      const gaps = out.slice(1).map((l, i) => l.base - out[i].base);
      const unit = px(pcs.lineHeight) || Math.min(...gaps);
      let rows = 0;
      gaps.forEach((g, i) => { const k = Math.max(1, Math.round(g / unit)); out[i + 1].blankBefore = k - 1; rows += k; });
      lh = (out[out.length - 1].base - out[0].base) / rows;
    }
    let align = pcs.textAlign;
    if (align === "start" || align === "left" || align === "-webkit-left" || align === "justify") align = "l";
    else if (align === "center" || align === "-webkit-center") align = "ctr";
    else align = "r";
    // the solid colour behind this text, so semi-transparent text can be flattened to an opaque colour
    let under = null;
    for (let a = P; a; a = a.parentElement) {
      const c = color(getComputedStyle(a).backgroundColor);
      if (visible(c) && c[3] > 0.99) { under = c; break; }
      if (a === slide) break;
    }
    return { kind: "text", align, nowrap: pcs.whiteSpace === "nowrap" || pre, pre, lines: out, lineHeight: lh, under };
  }

  function isInlineRun(n) {
    if (n.nodeType === 3) return true;
    if (n.nodeType !== 1) return false;
    if (["IMG", "SVG", "svg"].includes(n.tagName)) return false;
    const cs = getComputedStyle(n);
    if (cs.display === "none") return false;
    return cs.display === "inline" && ![...n.querySelectorAll("*")].some((d) => ["IMG", "svg"].includes(d.tagName) || getComputedStyle(d).display !== "inline");
  }

  function walk(slide, el, opacity, sr) {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") return;
    const op = opacity * parseFloat(cs.opacity);
    if (op < 0.01) return;
    const r = el.getBoundingClientRect();
    const tag = el.tagName.toLowerCase();
    const isSlide = el === slide;
    const clip = clipRect(el, slide, r);
    if (clip.x1 - clip.x0 < 0.5 || clip.y1 - clip.y0 < 0.5) { if (tag === "svg" || tag === "img") return; }

    const mask = (cs.maskImage && cs.maskImage !== "none") || (cs.webkitMaskImage && cs.webkitMaskImage !== "none");
    const fullRaster = tag === "img" || tag === "svg" || mask || cs.transform !== "none" || cs.filter !== "none" || fam(cs) === "Amiri";
    const box = { x: clip.x0 - sr.left, y: clip.y0 - sr.top, w: clip.x1 - clip.x0, h: clip.y1 - clip.y0 };
    if (!isSlide && fullRaster) {
      const alt = el.getAttribute("alt") || el.getAttribute("aria-label") || (tag === "svg" ? "Icon" : "Decoration");
      push(slide, el, { kind: "raster", eid: id(el), own: false, alt, ...box });
      return;
    }
    if (!isSlide && cs.backgroundImage !== "none") push(slide, el, { kind: "raster", eid: id(el), own: true, alt: "Background", ...box });

    const bg = color(cs.backgroundColor);
    const sides = ["Top", "Right", "Bottom", "Left"].map((k) => ({
      w: px(cs[`border${k}Width`]), style: cs[`border${k}Style`], color: color(cs[`border${k}Color`]),
    })).map((b) => ({ ...b, on: b.w > 0 && b.style !== "none" && b.style !== "hidden" && visible(b.color) }));
    if (!isSlide && (visible(bg) || sides.some((s) => s.on))) {
      if (el.childNodes.length && !el.querySelector("[data-step]")) el.dataset.card = "1";
      const rad = corners(el, r, cs, slide);
      const fade = (c) => c && [c[0], c[1], c[2], c[3] * op];
      push(slide, el, {
        kind: "shape", eid: id(el), x: r.left - sr.left, y: r.top - sr.top, w: r.width, h: r.height,
        clip: box, fill: visible(bg) ? fade(bg) : null, radius: rad, shadow: shadow(cs),
        sides: sides.map((s) => (s.on ? { w: s.w, style: s.style, color: fade(s.color) } : null)),
      });
    }

    // children in order: runs of inline content become text boxes, everything else recurses
    let run = [];
    const flush = () => {
      if (!run.length) return;
      const t = textGroup(slide, el, run, op, sr);
      if (t) push(slide, run.find((n) => n.nodeType === 1) || el, t);
      run = [];
    };
    const flex = cs.display.includes("flex") || cs.display.includes("grid");
    for (const n of el.childNodes) {
      if (isInlineRun(n)) {
        if (flex && n.nodeType === 3) { flush(); run.push(n); flush(); }  // each loose text node is its own flex item
        else run.push(n);
      } else {
        flush();
        if (n.nodeType === 1) walk(slide, n, op, sr);
      }
    }
    flush();
  }

  const result = [];
  for (const slide of document.querySelectorAll("section.slide")) {
    items.length = 0; order = 0;
    const sr = slide.getBoundingClientRect();
    walk(slide, slide, 1, sr);
    const bg = color(getComputedStyle(slide).backgroundColor);
    result.push({ eid: id(slide), bg, items: items.map((i) => ({ ...i })) });
  }
  return result;
});

// capture rasters slide by slide
let n = 0;
const handles = await page.$$("section.slide");
for (let s = 0; s < slides.length; s++) {
  const slide = handles[s];
  const sbox = await slide.boundingBox();
  for (const it of slides[s].items) {
    if (it.kind !== "raster") continue;
    const x = Math.floor(it.x), y = Math.floor(it.y);
    const w = Math.ceil(it.x + it.w) - x, h = Math.ceil(it.y + it.h) - y;
    Object.assign(it, { x, y, w, h });
    if (w < 1 || h < 1) { it.kind = "skip"; continue; }
    await page.evaluate(([e, own]) => {
      const el = document.querySelector(`[data-eid="${e}"]`);
      document.documentElement.classList.add("iso");
      el.closest("section.slide").classList.add("iso-on");
      el.setAttribute(own ? "data-own" : "data-on", "");
    }, [it.eid, it.own]);
    it.file = `r${String(++n).padStart(4, "0")}.png`;
    await page.screenshot({ path: path.join(outDir, "img", it.file), omitBackground: true, fullPage: true, clip: { x: sbox.x + x, y: sbox.y + y, width: w, height: h } });
    await page.evaluate(([e]) => {
      const el = document.querySelector(`[data-eid="${e}"]`);
      el.removeAttribute("data-on"); el.removeAttribute("data-own");
      el.closest("section.slide").classList.remove("iso-on");
      document.documentElement.classList.remove("iso");
    }, [it.eid]);
  }
}
fs.writeFileSync(path.join(outDir, "deck.json"), JSON.stringify(slides));
await browser.close();
const count = (k) => slides.reduce((a, s) => a + s.items.filter((i) => i.kind === k).length, 0);
console.log(`slides ${slides.length}: ${count("text")} text boxes, ${count("shape")} shapes, ${count("raster")} images`);
