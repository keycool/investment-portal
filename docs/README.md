# 项目文档索引

本目录只保存网站建设与运营知识。跨工作台生产与海报指引统一由项目 Skill 提供，入口是 [daily-review-notebook-poster/SKILL.md](../skills/daily-review-notebook-poster/SKILL.md)。

## 产品

- [信息架构](./product/information-architecture.md)：首页、栏目、归档、研究笔记、关于、封面列表和文章页的职责、URL 与移动端规则；首页顺序为 2026-08-25 定稿版（hero 纯文案 → 全部复盘统一列表 → 研究工具 → 复盘原则 → 首页底部免责声明）。
- [产品总蓝图](./product/product-blueprint.md)：定位、内容系统、产品路线、商业化边界和阶段验收。

## 内容

- [站点固定文案与条款](./content/site-copy.md)：品牌站名、导航、hero、全部复盘列表、研究工具、复盘原则、固定免责声明唯一文本、页脚链接与公开边界条款；全站固定文案的单一来源。
- [公开复盘编辑规范](./content/editorial-spec.md)：事实、解释、判断、边界、来源、免责声明与校准规则。
- [Astro MDX 内容模型](./content/content-model.md)：`reviews`、`researchNotes`、封面字段、正文契约和状态升级。
- [历史材料审计与首批选择](./content/historical-content-selection.md)：现有来源、3+1 选择、缺口和冲突。

## 运营

- [人工发布与校准工作流](./operations/publishing-workflow.md)：交接包进入网站后的编辑、预览和追加校准流程。
- [内容完成时间记录](./operations/completion-log.md)：分别记录终稿确认、交接包接收和网站预览时间。
- [博客统一运行规范](./operations/blog-operating-standard.md)：从复盘、海报、交接到网站发布的完整职责与扩展接口。
- [海报生产规则总纲](./operations/poster-production-rules.md)：复盘海报与引流版共用的生成纪律（确认门槛、题眼措辞、配色、QA 探针、CTA 合规、备份）。
- [画布库规范](./operations/canvas-library.md)：引流版背景库的位置、包元数据契约、如何新增背景、按 mood 选择与 SHA 校验。
- [估值数据规范](./operations/valuation-data.md)：周复盘 PE、ERP、国债、波动率等事实数据的读取与回填边界。

## 项目状态

- [当前项目状态](./project/current-state.md)：唯一主项目、内容源、研究工具和授权边界。
- [本地构建与视觉验收](./qa/README.md)：正式/封闭构建、断链、桌面与 390px 截图结果。

## 文档职责

- 稳定执行规则写入根目录 `AGENTS.md`。
- 人类总览和入口写入根目录 `README.md`。
- 外部复盘工作台先读 `skills/daily-review-notebook-poster/SKILL.md`，正式投递时再读其 `references/handoff-contract.md`。
- 产品、内容与运营知识写入本目录对应分类。
- 日常交接内容只进入 `content-inbox/`，不混入文档目录。
