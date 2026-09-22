#!/usr/bin/env node
/**
 * 构建后步骤（只用于生产构建，不用于 build:preview）：
 * 把 `dist/` 里的成品图转成 WebP / JPEG，缩掉体积。
 *
 * 背景：海报由外部生产链路以 PNG 交付（1080×2000，单张 1.5–2.8 MB），
 * 放进 `public/images/posters/` 后随 `dist/` 原样上线；页面里其实只按
 * `max-width: 470px` 显示，却让访客下载了十几倍的字节。`public/og.png`
 * 更是 2.5 MB，且是每一页分享卡片的默认图。
 *
 * 做法：**只动 `dist/`，绝不改 `public/` 源文件**——
 *   1. `dist/images/posters/*.png|jpg` → 同尺寸 WebP（q82），删原文件；
 *   2. `dist/og.png` → `dist/og.jpg`（宽 1200、JPEG q86、mozjpeg），删原文件；
 *   3. 回写 `dist/**\/*.html` 里的引用路径（`*.png` → `*.webp`、`og.png` → `og.jpg`）。
 * 分辨率保持不变，所以海报放大细看仍然清晰；只是编码换了。
 *
 * 用法：
 *   node scripts/optimize-dist-images.mjs            # 执行
 *   node scripts/optimize-dist-images.mjs --dry-run  # 只报告，不落盘
 */

import { readdir, readFile, stat, unlink, writeFile } from "node:fs/promises";
import path from "node:path";

// sharp 是 astro 的图片依赖（astro 7 声明 `sharp: ^0.34.0 || ^0.35.0`），
// 由 npm 提升到顶层 node_modules，这里直接复用、不新增自己的依赖。
// 用动态 import 是为了在它缺失时给一句人话，而不是抛一堆栈。
let sharp;
try {
  sharp = (await import("sharp")).default;
} catch {
  console.error("[optimize-images] 找不到 sharp（astro 的图片依赖）。请先 npm install，再跑构建。");
  process.exitCode = 1;
  process.exit();
}

const ROOT = process.cwd();
const DIST = path.join(ROOT, "dist");
const POSTER_DIR = path.join(DIST, "images", "posters");

const DRY_RUN = process.argv.includes("--dry-run");

const POSTER_QUALITY = 82; // WebP：文字密集的长图，82 已接近无损
const OG_TARGET_WIDTH = 1200; // og 图目标宽度（社交平台推荐 ≥1200）
const OG_QUALITY = 86; // JPEG
const CONVERTIBLE = new Set([".png", ".jpg", ".jpeg"]);

const kb = (bytes) => `${(bytes / 1024).toFixed(0)} KB`;

async function walk(dir, filter) {
  const out = [];
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...(await walk(full, filter)));
    else if (!filter || filter(full)) out.push(full);
  }
  return out;
}

const exists = async (p) => {
  try {
    await stat(p);
    return true;
  } catch {
    return false;
  }
};

async function main() {
  if (!(await exists(DIST))) {
    console.error("[optimize-images] dist/ 不存在 —— 请先跑 astro build（本步骤只处理构建产物）");
    process.exitCode = 1;
    return;
  }

  let before = 0;
  let after = 0;
  const renames = []; // [旧引用片段, 新引用片段]

  // ── 1. 海报 → WebP ──────────────────────────────────────────────
  const posters = await walk(POSTER_DIR, (f) => CONVERTIBLE.has(path.extname(f).toLowerCase()));
  for (const file of posters) {
    const { size } = await stat(file);
    const webpName = `${path.basename(file, path.extname(file))}.webp`;
    const webpPath = path.join(path.dirname(file), webpName);
    const buf = await sharp(await readFile(file))
      .webp({ quality: POSTER_QUALITY, effort: 6 })
      .toBuffer();

    before += size;
    after += buf.length;
    renames.push([path.basename(file), webpName]);

    if (!DRY_RUN) {
      await writeFile(webpPath, buf);
      await unlink(file);
    }
  }

  // ── 2. og 图 → JPEG ─────────────────────────────────────────────
  const ogPng = path.join(DIST, "og.png");
  if (await exists(ogPng)) {
    const { size } = await stat(ogPng);
    const meta = await sharp(ogPng).metadata();
    const buf = await sharp(ogPng)
      .resize({ width: Math.min(OG_TARGET_WIDTH, meta.width), withoutEnlargement: true })
      .jpeg({ quality: OG_QUALITY, mozjpeg: true })
      .toBuffer();

    before += size;
    after += buf.length;
    renames.push(["og.png", "og.jpg"]);

    if (!DRY_RUN) {
      await writeFile(path.join(DIST, "og.jpg"), buf);
      await unlink(ogPng);
    }
  }

  // ── 3. 回写 HTML 引用 ───────────────────────────────────────────
  let rewritten = 0;
  if (renames.length) {
    const htmls = await walk(DIST, (f) => f.endsWith(".html"));
    for (const file of htmls) {
      const text = await readFile(file, "utf8");
      let next = text;
      for (const [oldName, newName] of renames) {
        // 只要出现在资源路径里的旧文件名（`.../poster-x.png`、`/og.png`）都换掉
        next = next.replaceAll(`/${oldName}`, `/${newName}`);
        next = next.replaceAll(`images/posters/${oldName}`, `images/posters/${newName}`);
      }
      if (next !== text) {
        rewritten += 1;
        if (!DRY_RUN) await writeFile(file, next, "utf8");
      }
    }
  }

  // ── 4. 报告 ────────────────────────────────────────────────────
  const label = DRY_RUN ? "[optimize-images] DRY RUN — 未落盘" : "[optimize-images]";
  console.log(`${label} 转换 ${renames.length} 个文件：${kb(before)} → ${kb(after)}（省 ${kb(before - after)}）`);
  console.log(`${label} 回写 ${rewritten} 个 HTML 文件`);

  if (DRY_RUN || renames.length === 0) return;

  // ── 5. 断言：旧文件已清、引用不悬空 ─────────────────────────────
  const leftovers = await walk(DIST, (f) => CONVERTIBLE.has(path.extname(f).toLowerCase()) && path.dirname(f) === POSTER_DIR);
  if (leftovers.length) {
    console.error(`[optimize-images] dist 海报目录仍有未转换文件：${leftovers.map((f) => path.basename(f)).join(", ")}`);
    process.exitCode = 1;
  }

  const htmls = await walk(DIST, (f) => f.endsWith(".html"));
  const missing = new Set();
  for (const file of htmls) {
    const text = await readFile(file, "utf8");
    for (const m of text.matchAll(/\/images\/posters\/([A-Za-z0-9._-]+)/g)) {
      if (!(await exists(path.join(POSTER_DIR, m[1])))) missing.add(m[1]);
    }
    if (text.includes("/og.png")) missing.add("og.png (仍被引用)");
  }
  if (missing.size) {
    console.error(`[optimize-images] 有 ${missing.size} 个引用找不到对应文件：${[...missing].slice(0, 10).join(", ")}`);
    process.exitCode = 1;
  }
}

await main();
