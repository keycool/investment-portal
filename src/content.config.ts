import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const sourceSchema = z.object({
  label: z.string().min(1),
  url: z.url().nullable(),
  data_as_of: z.iso.date(),
  note: z.string().min(1),
});

const posterSchema = z.object({
  src: z.string().nullable(),
  alt: z.string().min(1),
  qa_status: z.enum(["pending_migration", "missing_png", "pending", "passed", "failed"]),
});

const calibrationSchema = z.object({
  date: z.iso.date(),
  result: z.string().min(1),
  note: z.string().min(1),
  error_tags: z.array(z.string()).default([]),
  rule_adjustment: z.string().nullable().optional(),
});

const reviews = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/reviews" }),
  schema: ({ image }) =>
    z.object({
      id: z.string().min(1),
      slug: z.string().min(1),
      author: z.literal("心猿意马的羊"),
      type: z.enum(["daily", "weekly"]),
      status: z.enum(["draft", "confirmed", "preview", "public"]),
      date: z.iso.date(),
      week_id: z.string().nullable(),
      title: z.string().min(1),
      summary: z.string().min(1),
      data_as_of: z.iso.date(),
      completed_at: z.iso.datetime({ offset: true }).nullable(),
      published_at: z.iso.datetime({ offset: true }).nullable(),
      updated_at: z.iso.datetime({ offset: true }).nullable(),
      judgment_status: z.enum(["pending", "supported", "partial", "falsified"]),
      featured: z.boolean(),
      sources: z.array(sourceSchema).min(1),
      poster: posterSchema.nullable(),
      cover: z
        .object({
          image: image(),
          alt: z.string().min(1),
          credit: z.string().optional(),
          source: z.url().optional(),
          position: z.string().default("center"),
        })
        .optional(),
      calibrations: z.array(calibrationSchema),
      headline_stats: z
        .array(
          z.object({
            value: z.string().min(1),
            label: z.string().min(1),
            accent: z.boolean().default(false),
          }),
        )
        .max(4)
        .optional(),
      disclaimer: z.literal("personal_market_review"),
    }),
});

const researchNotes = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/research-notes" }),
  schema: ({ image }) =>
    z.object({
      id: z.string().min(1),
      slug: z.string().min(1),
      status: z.enum(["draft", "confirmed", "preview", "public"]),
      date: z.iso.date(),
      title: z.string().min(1),
      summary: z.string().min(1),
      source_author: z.string().min(1),
      source_title: z.string().min(1),
      source_url: z.url(),
      data_as_of: z.iso.date(),
      cover: z
        .object({
          image: image(),
          alt: z.string().min(1),
          credit: z.string().optional(),
          source: z.url().optional(),
          position: z.string().default("center"),
        })
        .optional(),
      disclaimer: z.literal("personal_market_review"),
    }),
});

export const collections = { reviews, researchNotes };
