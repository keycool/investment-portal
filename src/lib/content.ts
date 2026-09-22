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
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(`${date}T00:00:00+08:00`));
}
