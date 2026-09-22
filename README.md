# 心猿意马的羊｜交易复盘

这是个人投资交易学习博客的唯一主项目。网站持续记录每日复盘、每周复盘、判断边界和后续校准；它是投资交易学习与研究记录，不提供个性化投资建议，不展示持仓、仓位、账户金额或具体买卖动作。

## 当前状态

- Astro + MDX 静态站已经建立。
- 非 `public` 内容只在本地开发或封闭预览构建中出现。
- 正式构建只包含 `status: public` 的内容；当前没有内容被擅自公开。
- `D:\CC\shared` 下不再保留平行博客项目、旧原型或本地策略数据副本。

## 本地运行

```bash
npm install
npm run dev
npm run check
npm run build
npm run build:preview
```

- `npm run dev`：本地开发，显示所有内容状态并标记草稿。
- `npm run build`：正式构建，只输出 `public` 内容。
- `npm run build:preview`：封闭预览构建，包含草稿并写入 `noindex`。

## 目录职责

```text
investment-portal/
├─ src/
│  ├─ content/reviews/       # 每日与每周 MDX；唯一复盘展示源
│  ├─ content/research-notes/# 研究笔记；无合格内容时保持为空
│  ├─ components/            # 列表卡片、封面、导航等
│  ├─ layouts/               # 全站与文章布局
│  └─ pages/                 # 稳定静态路由
├─ content-inbox/            # 外部复盘工作台唯一可写入区域
├─ skills/
│  └─ daily-review-notebook-poster/ # 可移植的日复盘与笔记本海报生产 Skill
├─ docs/                     # 产品、内容、运营与项目知识
└─ AGENTS.md                 # 项目代理执行规则
```

## 内容与封面

- 每日与每周内容共用 `reviews` 内容集合，以 `type` 区分。
- 文章有独立封面时使用 3:2 本地图片；没有封面时自动显示由栏目、日期、题眼和署名组成的排版卡片。
- 独立封面不是交接包进入 `ready` 的硬门槛，不得为了补图阻塞已确认正文。
- 海报是文章结论摘要，不作为列表封面的默认裁切来源，也不替代网站正文。
- 每篇已接入正式海报的复盘同时提供“文章版”和“海报版”；海报版使用独立稳定路由，正文区域只展示完整海报，便于快速阅读和比较两种体验。
- `public/og.png` 是站点级社交预览图；文章详情只有在存在合规独立封面时才输出文章级社交图片。

## 研究工具入口

首页与关于页保留三个独立工具链接：ERP 策略、行业启动和 PE 估值。它们是个人研究系统的一部分，但不作为博客内容源，不把生产数据复制进本站，也不会自动改写复盘判断。

## 跨工作台交接

负责飞书复盘和海报的另一工作台必须完整读取 [daily-review-notebook-poster/SKILL.md](./skills/daily-review-notebook-poster/SKILL.md)，需要正式投递时再读取它的 [handoff-contract.md](./skills/daily-review-notebook-poster/references/handoff-contract.md)，并且只向：

```text
D:\CC\shared\investment-portal\content-inbox\
```

新增交接包。它不能修改网站代码、MDX、文档或生产策略。

## 项目文档

完整文档入口见 [docs/README.md](./docs/README.md)，统一运行规范见 [blog-operating-standard.md](./docs/operations/blog-operating-standard.md)，产品总蓝图见 [product-blueprint.md](./docs/product/product-blueprint.md)。

## 永久边界

- 不下单、不代客、不承诺收益。
- 不公开持仓、仓位、账户金额、收益截图和具体买卖动作。
- 不把研究指标包装成自动买卖信号。
- 不自动覆盖原判断，不允许校准记录删除旧结论。
- 未经单独授权，不部署、不绑定域名、不接统计或外部账号。
