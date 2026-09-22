# 分发状态追踪（distribution-log）

> append-only。记录每个日期 × 三渠道的发布状态。
> 状态值：`草稿` / `已发布` / `未发` / `链接待回填`。发布后把「已发布」+ 链接填上，不覆盖历史行。

| 日期 | 类型 | 博客主站 | 雪球 | 小红书 | 备注 |
|---|---|---|---|---|---|
| 2026-08-24 | daily | 未发 | 草稿待生成 | 草稿待生成 | 主站部署后统一走 preview→public |
| 2026-08-25 | daily | 未发 | 草稿（手写示例） | 草稿（手写示例） | 08-25 为分发模板与脚本的参照基准 |
| 2026-08-26 | daily | 未发 | 草稿待生成 | 草稿待生成 | |
| 2026-08-27 | daily | 未发 | 草稿待生成 | 草稿待生成 | |
| 2026-W34 | weekly | 未发 | 草稿待生成 | 草稿待生成 | |
| 2026-08-31 | daily | 未发 | 草稿 | 未发（paused） | 小红书 2026-08-31 起暂停；雪球草稿已生成（distribute.py） |
| 2026-09-01 | daily | 未发 | 草稿 | 未发（paused） | 雪球海报用橘猫彩蛋背景（用户选定）；草稿已生成 |
| 2026-09-02 | daily | 未发 | 草稿 | 未发（paused） | 雪球海报用向水而行·增强对比度版背景（09-03 定版方案：文字压底图+增强对比度）；handoff/MDX/雪球草稿 09-03 收尾完成 |
| 2026-09-03 | daily | 未发 | 草稿 | 未发（paused） | 雪球海报用稿子汇编背景（用户选定）；首次超界 88px 经方案 A（缩 quote/summary 字面+CSS 收紧）收回，总结框两次上移定稿 v4；三段起草后回填+感悟缩写同步 revision 554 |
| 2026-09-04 | weekly | 未发（preview ready） | 草稿 | 未发（paused） | W36 周报：2026-09-08 用户「周报定稿」；MDX weekly/2026-W36 已建（draft），build:preview 通过；雪球草稿 distribute.py 生成后按周稿口径修正 |
| 2026-09-08 | daily | 未发（preview ready） | 草稿 | 未发（paused） | 雪球海报用向水而行·增强版背景（用户选定 09-08）；三段已回填 revision 611；MDX daily/2026-09-08 已建、build:preview 通过；雪球草稿 distribute.py 已生成；海报 v1 待目检，通过后生成 handoff |
| 2026-09-09 | daily | 未发（preview ready） | 草稿 | 未发（paused） | 雪球海报用星云随笔背景（用户选定 09-09，深底浅色主题）；三段已回填 revision 579；MDX daily/2026-09-09 已建、build:preview 通过；雪球草稿 distribute.py 已生成；交接包 ready（poster SHA 4533c929…） |
| 2026-09-10 | daily | 未发（preview ready） | 草稿 | 未发（paused） | 雪球海报用橘猫彩蛋背景（用户选定 09-10，浅底深色主题）；三段已回填 revision 618（用户要求清理母稿乱码后 619）；MDX daily/2026-09-10 已建、build:preview 通过；雪球草稿 distribute.py 已生成；交接包 ready（poster SHA b681983b…） |
| 2026-09-11 | daily | 未发（preview ready） | 草稿 | 未发（paused） | 雪球海报用星云随笔背景（用户选定 09-11，深底浅色主题 `--theme dark`）；三段已回填 revision 740（737 → 738 判断 → 739 点评 → 740 感悟）；MDX daily/2026-09-11 已建、build:preview 通过；雪球草稿 distribute.py 已生成；交接包 ready（poster SHA 95846a84…） |
| 2026-09-11 | weekly | 未发（preview ready） | 草稿 | 未发（paused） | W37 周报：雪球海报用星云随笔背景（用户选定 09-12，深底浅色主题 `--theme dark`）；题眼「周线转弱 / 逼向右肩颈线」；估值栏 revision 339、三段文末追加 revision 340；MDX weekly/2026-W37 已建、build:preview 通过（/weekly/2026-W37/），首页「最新周报」已切至 W37；雪球草稿 distribute.py 已生成；交接包 ready（poster SHA 3b3076d2…） |
| 2026-09-14 | daily | 未发（preview ready） | 草稿 | 未发（paused） | 雪球海报用雾海微明背景（用户选定 09-14；画布库新增背景首次启用，浅底深色主题）；题眼「地量弱修复 / 指数仍在阴线下影里」；三段已回填 revision 509（506 → 507 判断 → 508 点评 → 509 感悟）；MDX daily/2026-09-14 已建、build:preview 通过（/daily/2026-09-14/，全站 30 页），首页「最新」已切至 0914；雪球草稿 distribute.py 已生成；交接包 ready（poster SHA 80b7f4f9…）；**页脚对比度 2.01:1 遗留** → 2026-09-22 统一回补加衬底后 5.58:1，poster SHA 更新为 5ed65c0b… |
| 2026-W38 | weekly | 未发（preview ready） | 草稿 | 未发（paused） | W38 周报：雪球海报用星云随笔背景（用户 2026-09-22 立约定「周报无特别即用星云」，本稿即星云，深底浅色主题 `--theme dark`）；题眼「缩量收阳 / 缺口未补」；估值栏 revision 297→303（按用户选择「按周四」口径，data_as_of 2026-09-17）、三段文末追加 revision 304；MDX weekly/2026-W38 已建（status preview）、build:preview 通过（/weekly/2026-W38/，全站 31 页）；雪球草稿 distribute.py 已生成；交接包 ready（poster SHA 83684381…） |

> **2026-09-10 内容状态升级（不改本表发布状态列）**：14 篇 MDX 由 `draft` 升级为 `preview`——13 篇 daily（0824 / 0825 / 0826 / 0828 / 0831 / 0901 / 0902 / 0903 / 0904 / 0908 / 0909 / 0910）+ 2 篇 weekly（W34 / W36），条件为均已交接（`content-inbox/<id>/handoff.md` 在位）且 `build:preview` 通过。2026-08-27 维持 `public`（不回退已发布）；0810 / 0812 / 0813 / W32 因无交接包维持 `draft`。同时按 `publishing-workflow.md` §6.1 统一来源口径：`label` 由「公开市场数据（具体提供方待补）」改为「公开市场数据」，删去「进入 preview 前补齐」TODO——含已 `public` 的 2026-08-27（**只改来源、不动状态**，它是唯一上线页，原本挂着「待补」字样）。0810 / 0812 / 0813 / W32 保留原样，它们不只是缺标签，第二来源仍是「待飞书确认终稿复核」，待母稿确认后再处理。本表各行的发布状态（未发）未变——升级到 `preview` 不等于上线，生产构建只含 `public`。

## 规则

1. 发布状态只增不改；同一日期同一渠道的重复发布记新行（带日期戳）。
2. 博客主站「已发布」= MDX 走到 `public` 且 `npm run build` 部署成功。
3. 雪球/小红书「已发布」= 发布核对清单逐项通过后实际发出。
4. 博客链接（`src/data/channels.ts` 的 `blogUrl`）未就绪前，雪球/小红书列记为「链接待回填」。
