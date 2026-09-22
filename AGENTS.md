# Project agent rules

## Read order

1. Read `README.md` for project scope and directory ownership.
2. If the task creates a daily market review or notebook-style poster (end-to-end: find master draft, draft and confirm three sections, write back to Feishu, build poster, hand off), read `skills/daily-review-workflow/SKILL.md` completely before acting; it is the orchestration layer and routes to `skills/daily-review-notebook-poster/SKILL.md` and the operations docs it references.
3. If the task receives a formal daily or weekly review package, read `skills/daily-review-notebook-poster/references/handoff-contract.md` completely before acting.
4. If the task fills or verifies valuation data (broad-index PE, ERP, bond yield, volatility, concentration, dividend), read `docs/operations/valuation-data.md` — it maps data sources, update/refresh diagnosis, and Feishu write-back.
5. For site content, read `docs/content/editorial-spec.md` and `docs/content/content-model.md`.
6. If the task touches site copy, layout text, the disclaimer, footer links or navigation labels, read `docs/content/site-copy.md` — it is the single source of truth for all fixed copy and terms.
7. For publishing or calibration, read `docs/operations/publishing-workflow.md`.

## Workspace roles

- The external review workbench owns fact analysis, user confirmation, Feishu final copy, poster generation and poster QA.
- This project owns intake, public editing, MDX, archives, previews and append-only calibrations.
- Feishu confirmed copy is the thought source of truth. Website content must never overwrite Feishu.

## External review workbench write boundary

When producing or handing off a review, write only inside:

```text
D:\CC\shared\investment-portal\content-inbox\
```

Do not modify `src/content/reviews`, `docs`, site source code, strategy repositories, GitHub workflows or production data. A ready package contains `handoff.md`, the final poster HTML and the final poster PNG. A 3:2 cover image is optional and never blocks a ready handoff.

## Content gates

- Judgment, commentary and personal reflection must all be explicitly confirmed before Feishu write-back or a `ready` handoff.
- Preview or lead-generation copy, especially anything marked “未回填飞书”, is not confirmed source material.
- Missing facts, sources and timestamps stay missing or pending; never infer them.
- Original published judgments are immutable. Calibration records are append-only.
- Never expose positions, allocation, account values, returns screenshots or specific buy/sell actions.

## Project boundaries

- No trading, order execution, personalized investment advice or return promises.
- No public deployment, domain, analytics, external publishing or account connection without separate approval.
- Keep the Astro `reviews` collection as the only display source for daily and weekly content; do not create a hard-coded or JSON second source.
- Keep `researchNotes` separate from reviews. External viewpoints must be attributed and separated from the author's own judgment.
- A cover must be owned, generated for this project or clearly licensed. If it is missing or invalid, use the built-in fallback card and preserve the review body.
