import type { APIRoute } from "astro";
import { getCollection } from "astro:content";
import { byNewest, isVisible, noteHref, reviewHref } from "../lib/content";

// 静态构建期生成 /sitemap.xml，与站内实际可见页面（isVisible 放行 public）保持同源口径。
// 依赖 astro.config.mjs 的 site 字段取绝对地址。
export const GET: APIRoute = async ({ site }) => {
  const base = site ?? new URL("https://www.fupanxinyuan.com");

  const reviews = (await getCollection("reviews")).filter((entry) => isVisible(entry.data.status)).sort(byNewest);
  const notes = (await getCollection("researchNotes")).filter((entry) => isVisible(entry.data.status)).sort(byNewest);

  const routes: Array<{ loc: string; lastmod?: string; priority: string }> = [
    { loc: "/", priority: "1.0" },
    { loc: "/daily/", priority: "0.9" },
    { loc: "/weekly/", priority: "0.9" },
    { loc: "/archive/", priority: "0.6" },
    { loc: "/research/", priority: "0.6" },
    { loc: "/about/", priority: "0.5" },
  ];

  const months = [...new Set(reviews.map((review) => review.data.date.slice(0, 7)))].sort().reverse();
  for (const key of months) {
    const [year, month] = key.split("-");
    routes.push({ loc: `/archive/${year}/${month}/`, priority: "0.5" });
  }

  for (const review of reviews) {
    const stamp = review.data.updated_at ?? review.data.published_at ?? review.data.date;
    routes.push({ loc: reviewHref(review), lastmod: stamp.slice(0, 10), priority: "0.8" });
  }

  for (const note of notes) {
    routes.push({ loc: noteHref(note), lastmod: note.data.date, priority: "0.6" });
  }

  const body = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...routes.map((route) =>
      [
        "  <url>",
        `    <loc>${new URL(route.loc, base).toString()}</loc>`,
        route.lastmod ? `    <lastmod>${route.lastmod}</lastmod>` : null,
        `    <priority>${route.priority}</priority>`,
        "  </url>",
      ]
        .filter((line): line is string => line !== null)
        .join("\n"),
    ),
    "</urlset>",
    "",
  ].join("\n");

  return new Response(body, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
};
