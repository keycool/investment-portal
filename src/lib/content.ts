import type { CollectionEntry } from "astro:content";

export const isPreviewMode = import.meta.env.DEV || import.meta.env.MODE === "preview";

export function isVisible(status: "draft" | "confirmed" | "preview" | "public") {
  return status === "public" || isPreviewMode;
}

export function byNewest<T extends { data: { date: string } }>(a: T, b: T) {
  return b.data.date.localeCompare(a.data.date);
}

export function reviewHref(review: CollectionEntry<"reviews">) {
  return `/${review.data.slug}/`;
}

export function reviewTypeLabel(type: "daily" | "weekly") {
  return type === "daily" ? "每日复盘" : "每周复盘";
}

export function judgmentLabel(status: "pending" | "supported" | "partial" | "falsified") {
  const labels = {
    pending: "待验证",
    supported: "已支持",
    partial: "部分支持",
    falsified: "已否定",
  } as const;

  return labels[status];
}

export function noteHref(note: CollectionEntry<"researchNotes">) {
  const segment = note.data.slug.replace(/^research\//, "");
  return `/research/${segment}/`;
}

export function formatDate(date: string) {
  // 必须显式指定 timeZone：本站日期语义均为东八区日界（frontmatter 以 +08:00 构造 Date），
  // 不指定时 Intl 会在「运行时区」格式化——Vercel 构建机是 UTC，会把每个日期提前一天
  // （2026-09-24T00:00+08 → 2026-09-23T16:00Z → 显示 2026/09/23）。本机（+08）看不出来，
  // 只在线上暴露（2026-09-26 发现：全站文章头部/列表日期均 -1 天，W38 实测头部 09/17 应为 09/18）。
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    timeZone: "Asia/Shanghai",
  }).format(new Date(`${date}T00:00:00+08:00`));
}
