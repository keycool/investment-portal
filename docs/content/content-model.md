# Astro MDX 内容模型与封面契约

状态：2026-08-23 Astro 实现版

## 1. 内容集合

Astro 站点使用 `reviews` 和 `researchNotes` 两个职责明确的内容集合。

- `reviews` 是每日与每周复盘的唯一展示源，通过 `type: daily | weekly` 区分。首页、栏目页、归档、上一篇/下一篇和校准全部由它生成，不再维护硬编码列表或运行时 JSON 的第二展示源。
- `researchNotes` 只保存有明确外部来源和作者独立理解的研究笔记，不得混入每日或每周判断链，也不迁移旧 portal JSON 作为公开内容。

长正文保存在 MDX 语义章节中；frontmatter 只保存身份、状态、日期、来源、海报和校准等结构化信息。这样避免同一段判断同时存在 YAML 与正文两份副本。

## 2. Frontmatter 字段

| 字段 | 类型 | 阶段要求 | 规则 |
|---|---|---|---|
| `id` | string | 始终必填 | 稳定 ID：`YYYY-MM-DD-daily` 或 `YYYY-Www-weekly` |
| `slug` | string | 始终必填 | 发布后不因标题改变；建议 `daily/YYYY-MM-DD`、`weekly/YYYY-Www` |
| `author` | string | 始终必填 | 固定为“心猿意马的羊” |
| `type` | enum | 始终必填 | 只能是 `daily` 或 `weekly` |
| `status` | enum | 始终必填 | `draft`、`confirmed`、`preview`、`public` |
| `date` | date string | 始终必填 | 日复盘为交易日；周复盘为周日或统一周标识对应日期 |
| `week_id` | string/null | 周复盘必填 | ISO 风格 `YYYY-Www`；日复盘为 `null` |
| `title` | string | 始终必填 | “事实 / 当前判断”，不含 URL 逻辑 |
| `summary` | string | 始终必填 | 两至三句，含主要矛盾和边界 |
| `data_as_of` | date string | 始终必填 | 文章主要事实的数据截止日 |
| `completed_at` | datetime/null | 真实生产时填写 | 不允许回填虚假完成时间 |
| `published_at` | datetime/null | `public` 必填 | 首次公开时间；后续修改不覆盖 |
| `updated_at` | datetime/null | 有追加时填写 | 编辑或校准更新时间 |
| `judgment_status` | enum | 始终必填 | `pending`、`supported`、`partial`、`falsified` |
| `featured` | boolean | 始终必填 | 手工精选；依据判断链和校准价值，不依据“猜对” |
| `sources` | array | 始终至少一项 | 每项含 `label`、`url`、`data_as_of`、`note`；进入 preview 前 `label` 必须具体 |
| `poster` | object/null | preview 起必填 | `src`、`alt`、`qa_status`；QA 状态必须为 `passed` |
| `cover` | object/缺省 | 可选 | 独立 3:2 封面；存在时必须含本地 `image` 和 `alt`，可含 `credit`、`source`、`position` |
| `calibrations` | array | 可为空 | 只追加；含日期、结果、说明、错误标签和规则调整 |
| `disclaimer` | enum | 始终必填 | 固定为 `personal_market_review` |

所有日期时间使用 `+08:00`。未知时间写 `null`，不能为了通过校验猜一个时间。

## 3. 建议 Frontmatter

```yaml
---
id: 2026-08-13-daily
slug: daily/2026-08-13
author: 心猿意马的羊
type: daily
status: draft
date: "2026-08-13"
week_id: null
title: 放量回撤 / 反弹承压
summary: 成交放大但普跌扩散，反弹节奏承压；短期结构尚未完全破坏，继续观察关键均线承接。
data_as_of: "2026-08-13"
completed_at: null
published_at: null
updated_at: null
judgment_status: pending
featured: true
sources:
  - label: 公开市场数据
    url: null
    data_as_of: "2026-08-13"
    note: 行情数据取自公开市场行情，按既有口径不署名具体提供方（2026-09-10 定稿）。
poster:
  src: null
  alt: 2026-08-13 每日复盘海报
  qa_status: pending_migration
calibrations: []
disclaimer: personal_market_review
---
```

## 4. 封面契约

- 推荐原图为 1200×800，使用 JPG、PNG、WebP 或 AVIF。
- 只接受作者自有、项目生成或明确授权的素材。外部素材填写 `credit` 与 `source`。
- `cover.alt` 描述图片表达的内容，不能只写“封面图”。
- 使用真实行情截图时，在正文或交接单记录数据日期与来源。
- 缺少独立封面不影响正文状态，列表自动显示由栏目、日期、题眼和署名组成的排版卡片。
- 自动排版卡片只使用文章公开字段和抽象装饰，不伪造行情图或价格数据。
- 竖版复盘海报不作为列表封面的默认裁切来源。

建议格式：

```yaml
cover:
  image: ./cover-20260813.webp
  alt: 深色背景上的“放量回撤”文章题眼
  credit: 心猿意马的羊
  position: center
```

## 5. MDX 正文契约

两类文章均必须出现以下语义章节，标题可以按日/周语境微调，但不能缺少其含义：

1. `## 导语`
2. `## 关键事实`（**默认折叠渲染**：MDX 里写成 `<details class="facts-fold"><summary>关键事实</summary>` + 表格 + `</details>`，读者点开才展开）
3. `## 当前判断`
4. `## 边界与观察`
5. `## 收盘点评`或`## 周度点评`
6. `## 个人感悟`
7. 海报、结构化来源、免责声明和校准由文章布局根据 frontmatter 统一渲染，不在 MDX 正文重复维护。

> 2026-09-24 变更：删除原第 3 章 `## 结构解释` —— 它与 `## 收盘点评` 的各条（指数与个股／大小盘／行业轮动／机构／债市／商品／外围）内容几乎逐字重复，用户判定冗余，全库 24 篇已移除。

关键事实建议使用“指标／数值／数据截止／来源”表格。正文不得重复一份 frontmatter 判断字段；页面渲染时把元数据和正文组合为完整文章。

## 6. 状态升级校验

### draft → confirmed

- 已找到飞书已确认终稿并逐段核对。
- 判断、点评和感悟含义未改变。
- 事实、判断、边界可以清楚区分。

### confirmed → preview

- `completed_at` 记录真实时间。
- 来源具体、日期可见，没有过期数据冒充当前值。
- 海报已经迁移且 `qa_status: passed`。
- 免责声明、上一篇/下一篇和移动端预览通过。

### preview → public

- 获得单独公开授权。
- `published_at` 写入真实时间。
- 稳定 URL 已确认；不得因标题修改改变 slug。

## 7. 研究笔记字段

`researchNotes` 至少包含 `id`、`slug`、`status`、`date`、`title`、`summary`、`source_author`、`source_title`、`source_url`、`data_as_of` 和免责声明；封面字段与复盘一致。

正文必须把“外部观点摘要”和“我的理解/验证记录”分开，不直接保留外部材料中的具体交易动作。

## 8. 不可变规则

- `id`、`slug`、首次 `published_at` 和原判断发布后不可覆盖。
- `calibrations` 只允许追加；任何更新不得删除旧记录。
- 飞书是母稿，网站不能反向覆盖飞书。
- 内容集合不接收 `NaN`、非标准日期或隐式过期数据；异常值在采集边界转为标准值或 `null`。
