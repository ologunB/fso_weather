// Build manuscript/manuscript.md into a typeset PDF.
// Usage: node build/build_pdf.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import katex from "katex";
import { marked } from "marked";
import { chromium } from "playwright-core";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(here);
const src = process.argv[2] ? path.resolve(process.argv[2]) : path.join(root, "manuscript", "manuscript.md");
const outHtml = path.join(here, path.basename(src, ".md") + ".html");
const outPdf = process.argv[3] ? path.resolve(process.argv[3]) : path.join(root, "manuscript", "FSO_Weather_Paper1_manuscript.pdf");

let md = fs.readFileSync(src, "utf8");

// Front matter
const fm = {};
md = md.replace(/^---\n([\s\S]*?)\n---\n/, (_, body) => {
  for (const line of body.split("\n")) {
    const m = line.match(/^(\w+):\s*"(.*)"$/);
    if (m) fm[m[1]] = m[2];
  }
  return "";
});

// Protect math before markdown parsing
const math = [];
const stash = (tex, display) => {
  let t = tex.trim();
  if (display) t = t.replace(/[,.]?\s*\\qquad\s*\((\d+)\)\s*$/, (m0, n) => (m0.trim().startsWith(",") ? "," : m0.trim().startsWith(".") ? "." : "") + ` \\tag{${n}}`);
  math.push(katex.renderToString(t, { displayMode: display, throwOnError: true, output: "html" }));
  return `@@MATH${math.length - 1}@@`;
};
md = md.replace(/\$\$([\s\S]+?)\$\$/g, (_, t) => "\n\n" + stash(t, true) + "\n\n");
md = md.replace(/\$([^$\n]+?)\$/g, (_, t) => stash(t, false));

// Figures with captions
md = md.replace(/^!\[([\s\S]*?)\]\((.+?)\)[ \t]*$/gm, (_, cap, href) => {
  const abs = pathToFileURL(path.resolve(path.dirname(src), href)).href;
  const wide = /fig1_|fig2_|fig5_|p2_range_sites/.test(href);
  return `<figure class="${wide ? "wide" : "narrow"}"><img src="${abs}"><figcaption>${marked.parseInline(cap)}</figcaption></figure>\n`;
});

// Fenced divs
md = md.replace(/^::: (\w+)[ \t]*$/gm, (_, c) => `\n<div class="${c}">\n\n`);
md = md.replace(/^:::[ \t]*$/gm, "\n</div>\n");

// Author placeholders
md = md.replace(/\[(AUTHOR[^\]]*)\]/g, '<span class="todo">[$1]</span>');

let html = marked.parse(md);
html = html.replace(/@@MATH(\d+)@@/g, (_, i) => math[+i]);
// A display equation sits alone in a paragraph
html = html.replace(/<p>(<span class="katex-display">[\s\S]*?<\/span>)<\/p>/g, "$1");
// Table captions: the bold caption paragraph inside div.table
html = html.replace(/<div class="table">\s*<p>([\s\S]*?)<\/p>/g, '<div class="table"><p class="tcap">$1</p>');

const katexCss = pathToFileURL(path.join(here, "node_modules", "katex", "dist", "katex.min.css")).href;
const title = fm.title || "Manuscript";
const page = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>${title}</title>
<link rel="stylesheet" href="${katexCss}">
<style>
@page { size: A4; margin: 20mm 18mm 20mm 18mm; }
:root { --ink:#111; --muted:#555; --rule:#999; --todo:#fff3bf; }
html { background:#fff; }
body { font-family: "Liberation Serif","Times New Roman","DejaVu Serif",serif; font-size: 10.5pt; line-height: 1.42; color: var(--ink); background:#fff; margin:0; }
h1.title { font-size: 17pt; line-height: 1.25; text-align:center; margin: 0 0 8pt; font-weight: 700; }
.authors { text-align:center; font-size: 11pt; margin-bottom: 2pt; }
.affil { text-align:center; font-size: 9.5pt; color: var(--muted); font-style: italic; margin-bottom: 12pt; }
.note { text-align:center; font-size: 8.5pt; color: var(--muted); margin-bottom: 14pt; }
.abstract, .keywords { font-size: 9.6pt; text-align: justify; margin: 0 6mm 6pt; }
.abstract { border-top: 0.6pt solid var(--rule); padding-top: 6pt; }
.keywords { border-bottom: 0.6pt solid var(--rule); padding-bottom: 8pt; margin-bottom: 12pt; }
.abstract p, .keywords p { margin: 0; }
h1 { font-size: 11pt; text-transform: uppercase; letter-spacing: 0.04em; text-align:center; margin: 16pt 0 6pt; break-after: avoid; }
h2 { font-size: 10.5pt; font-style: italic; font-weight: 600; margin: 11pt 0 4pt; break-after: avoid; }
p { margin: 0 0 6pt; text-align: justify; hyphens: auto; }
ol, ul { margin: 0 0 6pt; padding-left: 18pt; }
li { margin-bottom: 3pt; text-align: justify; }
.katex-display { margin: 6pt 0 8pt; overflow: hidden; }
.katex { font-size: 1.02em; }
figure { margin: 10pt auto 12pt; text-align: center; break-inside: avoid; }
figure.narrow img { width: 50%; }
figure.wide img { width: 100%; }
figcaption { font-size: 8.8pt; text-align: justify; margin-top: 4pt; line-height: 1.35; }
.table { margin: 10pt 0 12pt; break-inside: avoid; }
.tcap { font-size: 8.8pt; text-align: center; margin-bottom: 4pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.2pt; line-height: 1.25; }
thead th { border-top: 1pt solid var(--ink); border-bottom: 0.6pt solid var(--ink); padding: 3pt 4pt; text-align: left; font-weight: 600; vertical-align: bottom; }
tbody td { padding: 2.5pt 4pt; vertical-align: top; }
tbody tr:last-child td { border-bottom: 1pt solid var(--ink); }
.todo { background: var(--todo); font-family: "DejaVu Sans", sans-serif; font-size: 0.82em; padding: 0 2pt; }
h1#references ~ p { font-size: 8.8pt; text-align: left; padding-left: 22pt; text-indent: -22pt; margin-bottom: 3pt; }
</style></head><body>
<h1 class="title">${title}</h1>
<div class="authors">${(fm.authors || "").replace(/\[(AUTHOR[^\]]*)\]/g, '<span class="todo">[$1]</span>')}</div>
<div class="affil">${(fm.affiliation || "").replace(/\[(AUTHOR[^\]]*)\]/g, '<span class="todo">[$1]</span>')}</div>
<div class="note">${fm.note || "Literature restricted to sources published on or before 31 December 2021."}</div>
${html}
</body></html>`;
fs.writeFileSync(outHtml, page);

const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const pg = await browser.newPage();
await pg.goto(pathToFileURL(outHtml).href, { waitUntil: "load" });
await pg.evaluate(() => document.fonts.ready);
await pg.pdf({
  path: outPdf, format: "A4", printBackground: true, preferCSSPageSize: true,
  displayHeaderFooter: true, headerTemplate: "<span></span>",
  footerTemplate: '<div style="width:100%;text-align:center;font-size:8pt;color:#555;font-family:serif"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
});
await browser.close();
console.log("wrote", outPdf);
