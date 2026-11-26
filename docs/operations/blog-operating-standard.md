# 个人投资博客运行规范

## 系统职责

- 飞书或等价母稿：保存完整事实、判断、点评和感悟，是思想终稿来源。
- 海报 Skill：负责确认门槛、结构化输入、HTML、PNG 与视觉 QA。
- `content-inbox/`：接收已确认的正式交接包，不保存候选稿。
- `src/content/reviews/`：网站每日与每周复盘的唯一展示源。
- `src/data/researchTools.ts`：外部研究工具的唯一链接注册表。

## 日常链路

1. 日报共创以飞书「A股复盘中枢」三表多维表格（`VS4pbDYolabfgosl3CocJFiPnyh`）+ 归档文档 `YYYYMMDD` 为母稿源；海报制作读取 `skills/daily-review-workflow/SKILL.md` 与 `skills/daily-review-notebook-poster/SKILL.md`。
2. 事实、当前判断、收盘点评和个人感悟经过人工确认并归档飞书母稿。
3. 生成 1080×2000 个人博客专属复盘海报，完成程序化 QA 与用户目检定稿（`2026-11-26` 起雪球不再配海报，引流短帖采用纯文字约 400 字卡兹克观察短文风）；生成纪律见 `poster-production-rules.md`。
4. 按 `references/handoff-contract.md` 投递到 `content-inbox/YYYY-MM-DD-daily/`。
5. 网站工作台验证状态、来源、日期、免责声明和文件完整性，按 `2026-11-26` 精简去重口径编辑 MDX（详情页标题下直接展示海报图）。
6. 运行 `npm run check` 与 `npm run build:preview`，人工预览通过后才允许升级内容状态。
7. 发布后的原判断不可覆盖；后续结果只以带日期的校准记录追加。

周复盘沿用相同交接门槛；涉及 PE、ERP、国债、波动率等事实时，额外读取 `valuation-data.md`。

## 研究工具

ERP、行业启动和 估值罗盘属于独立研究工具。博客只展示名称、说明和外部链接：

- 不复制它们的生产数据。
- 不让工具自动改写复盘判断。
- 不接入交易执行或个性化买卖建议。

新增工具时，在 `src/data/researchTools.ts` 增加一项，并核验首页、关于页、移动端和外链可访问性。

## 扩展接口

- 新复盘类型：先扩展内容模型与路由，再增加栏目，不建立旁路 JSON。
- 新研究文章：进入 `researchNotes` 集合，与作者复盘分开。
- 新海报风格：建立新的独立 Skill（如复盘海报=notebook、引流版=teaser-poster）；不得改写已有模板的稳定契约。
- 自动化：只能从已确认终稿生成草稿，主观判断、状态升级和外部发布始终人工确认。
- 会员或 Agent：必须在真实回访需求成立后单独立项，继续遵守研究辅助和不执行交易的边界。

## 验收

- `npm run check`
- `npm run build`
- `npm run build:preview`
- 正式构建只包含 `public` 内容。
- 海报、来源、日期、免责声明、归档和追加式校准均可核验。
