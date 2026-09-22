#!/usr/bin/env node
/**
 * 构建后步骤（只用于生产构建，不用于 build:preview）：
 * 从 `dist/images/posters/` 里删掉「不该上线」的海报。
 *
 * 背景：Astro 的 `output: "static"` 会把 `public/` 原样搬进 `dist/`，
 * 于是 `public/images/posters/` 里**所有**文件都会随站点公开，包括：
 *   1. 未发布篇目（draft / preview）的成品海报 —— 未公开内容被提前泄露；
 *   2. 从未被任何 MDX 引用的 teaser / 底图 —— 纯占部署体积。
 * 文件名有规律（`poster-YYYYMMDD.png` / `poster-YYYYWww.png`），可被猜测直达。
 *
 * 规则：**只有 `status: public` 的复盘在 frontmatter 里引用的海报才保留。**
 * 好处是自动跟随内容状态——某篇从 preview 升 public 后，其海报自动随下次构建上线，
 * 不需要维护任何白名单。
 *
 * 只读 `src/content/reviews/`、只写 `dist/`，**绝不改动 `public/` 源文件**。
 *
 * 用法：
 *   node scripts/prune-unpublished-posters.mjs            # 执行
 *   node scripts/prune-unpublished-posters.mjs --dry-run  # 只看会删什么
 */

import { readdir, readFile, rm, stat, unlink } from "node:fs/promises";
import path from "node:path";

const ROOT = process.cwd();
const CONTENT_DIR = path.join(ROOT, "src", "content", "reviews");
const POSTER_DIR = path.join(ROOT, "dist", "images", "posters");

const DRY_RUN = process.argv.includes("--dry-run");
const FRONTMATTER = /^---\r?\n([\s\S]*?)\r?\n---/;
const POSTER_REF = /posters\/([A-Za-z0-9._-]+\.(?:png|jpg|jpeg|webp|gif))/g;

async function walk(dir) {
  const out = [];
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...(await walk(full)));
    else out.push(full);
  }
  return out;
}

const kb = (bytes) => `${(bytes / 1024).toFixed(0)} KB`;

async function main() {
  // 1. 收集「已发布」篇目引用的海报文件名
  const keep = new Set();
  const unreleased = new Map(); // 文件名 → 引用它的未发布篇目
  let publicCount = 0;

  for (const file of await walk(CONTENT_DIR)) {
    if (!/\.mdx?$/.test(file)) continue;
    const text = await readFile(file, "utf8");
    const fm = text.match(FRONTMATTER);
    if (!fm) continue;

    const status = (fm[1].match(/^status:\s*(\w+)/m) || [])[1];
    const refs = [...fm[1].matchAll(POSTER_REF)].map((m) => m[1]);
    const rel = path.relative(ROOT, file).replace(/\\/g, "/");

    if (status === "public") {
      publicCount += 1;
      for (const ref of refs) keep.add(ref);
    } else {
      for (const ref of refs) unreleased.set(ref, `${rel} (${status})`);
    }
  }

  // 安全闸：解析异常导致 keep 为空时，宁可不动
  if (keep.size === 0) {
    console.error("[prune-posters] 未解析到任何 public 篇目的海报引用，疑似解析失败，已中止（未删除任何文件）");
    process.exitCode = 1;
    return;
  }
  if (publicCount === 0) {
    console.error("[prune-posters] 未发现任何 status: public 的复盘，疑似解析失败，已中止");
    process.exitCode = 1;
    return;
  }

  // 2. 比对 dist 里的实际文件
  const present = await walk(POSTER_DIR);
  if (present.length === 0) {
    console.log("[prune-posters] dist/images/posters/ 为空或不存在，无需处理");
    return;
  }

  const toRemove = [];
  const removedUnreleased = [];
  const removedOrphan = [];
  let freed = 0;

  for (const file of present) {
    const name = path.basename(file);
    if (keep.has(name)) continue;
    toRemove.push(file);
    if (unreleased.has(name)) removedUnreleased.push(`${name} ← ${unreleased.get(name)}`);
    else removedOrphan.push(name);
  }

  for (const file of toRemove) {
    const { size } = await stat(file);
    freed += size;
    if (!DRY_RUN) await unlink(file);
  }

  // 3. 报告
  const label = DRY_RUN ? "[prune-posters] DRY RUN — 未实际删除" : "[prune-posters]";
  console.log(`${label} public 篇目 ${publicCount} 篇，保留海报 ${keep.size} 张`);
  console.log(`${label} 移除 ${toRemove.length} 张，释放 ${kb(freed)}`);

  if (removedUnreleased.length) {
    console.log(`${label} 其中「未发布篇目的海报」（原来会提前泄露）：`);
    for (const line of removedUnreleased.sort()) console.log(`  - ${line}`);
  }
  if (removedOrphan.length) {
    console.log(`${label} 其中「从未被引用的文件」：`);
    for (const line of removedOrphan.sort()) console.log(`  - ${line}`);
  }

  // 4. 清理空目录
  if (!DRY_RUN) {
    for (const dir of [POSTER_DIR, path.join(ROOT, "dist", "images")]) {
      try {
        await rm(dir, { recursive: false });
      } catch {
        /* 目录非空或不存在，忽略 */
      }
    }
  }

  // 5. 断言：dist 里不再出现任何未发布篇目的海报
  if (!DRY_RUN) {
    const leftover = await walk(POSTER_DIR);
    const leaked = leftover.map((f) => path.basename(f)).filter((n) => unreleased.has(n));
    if (leaked.length) {
      console.error(`[prune-posters] 仍有未发布篇目的海报残留在 dist：${leaked.join(", ")}`);
      process.exitCode = 1;
    }
  }
}

await main();
