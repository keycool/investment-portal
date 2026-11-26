# 当前项目状态

- `investment-portal` 是唯一主项目，使用 Astro + MDX，已于 `https://www.fupanxinyuan.com` 通过 GitHub + Vercel 线上发布。
- 每日与每周复盘共用 `reviews` 内容集合；正式构建只包含 `public` 状态。
- 日报共创默认接入飞书「A股复盘中枢」三表多维表格（`VS4pbDYolabfgosl3CocJFiPnyh`）并生成 `YYYYMMDD` 归档文档，全流程编排见 `skills/daily-review-workflow/SKILL.md`；笔记本海报生产规范见 `skills/daily-review-notebook-poster/SKILL.md`。
- 博客详情页以 **标题 → 1080×2000 复盘海报** 直接开场，正文按 `2026-11-26` 精简口径去重并保留折叠事实表与个人感悟原句。
- 雪球分发采用纯文字三短段 + 边界 + 感悟（不配海报），先由 `skills/distribute/scripts/distribute.py` 派生骨架再按中枢 `STYLE-CARDS` 的卡兹克观察短文风润色至约 400 字。
- ERP、行业启动和估值罗盘通过 `src/data/researchTools.ts` 以外链接入，不复制生产数据，不自动改写判断，不接交易执行。
