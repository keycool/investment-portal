---
name: teaser-poster
description: 将已确认的 A 股每日/每周复盘制作为 3:4 引流版（1080×1440，引流入口），背景从共享画布库（D:\CC\shared\assets\canvases）按内容氛围选择，HTML 可编辑文字层 + 固定画布，完成安全区、CTA 合规、像素核验与交接。用于引流版、引流板、3:4 复盘卡、钩子+信号+CTA 卡；不用于下单、投顾、策略修改或从未确认材料生成正式结论。
---

> ⏸ **渠道状态（2026-08-31）**：引流版当前面向**雪球（active，主打引流战场）**；**小红书 paused**，不产出小红书草稿。恢复小红书时以 `src/data/channels.ts` 中 `xhs.status` 为准。

# 每日复盘引流版（teaser-poster）

把已确认复盘做成**可快速阅读、可转发的 3:4 引流卡**。背景从共享画布库 `D:\CC\shared\assets\canvases\<pack-id>\` 按内容氛围选择（数据驱动，可扩容），所有文字放可编辑 HTML 层，永不重绘画布、永不往 PNG 上写字。

## 必读资源

1. 每次完整读取 [references/teaser-contract.md](references/teaser-contract.md)，执行输入契约、背景选择、安全区、配色与 CTA 合规。
2. 画布库规范与加包规则：读取 [../../docs/operations/canvas-library.md](../../docs/operations/canvas-library.md)。
3. 用 `scripts/list_canvases.py` 列出可选背景（pack / variant / 尺寸 / 安全区 / SHA / mood），再读所选包的 `USAGE.md` 与 `canvas.json`/`variants.json`。
4. 使用 [assets/poster-teaser-template.html](assets/poster-teaser-template.html) 与 [assets/poster-teaser-input-template.json](assets/poster-teaser-input-template.json)；不要从历史输出反推模板。
5. 生成规则总纲（确认门槛、题眼措辞、QA 探针、备份纪律）：读取 [../../docs/operations/poster-production-rules.md](../../docs/operations/poster-production-rules.md)。

## 标准流程

1. **发现母稿**：与复盘海报共用同一份已确认母稿（三段 + 题眼 + 代表数据），按日期确认。
2. **映射输入**：复制 `poster-teaser-input-template.json`，只填已确认文字与可核验数字：两行钩子、一句导语、3 个信号（动能/量能/广度）、一句次日判断、一句金句、合规 CTA。
3. **选背景**：运行 `scripts/list_canvases.py`（可按 `--mood` 过滤）→ 按内容氛围选 pack + variant → 读所选 variant 的 `recommended_text_area` 作内容区基准 → 把该 pack 整包拷进交接包目录并做 SHA 校验（流程见 `teaser-contract.md` 视觉规范）。
4. **构建 HTML**：按 `poster-teaser-template.html` 填充，文字严格落在所选 variant 的安全区内（可适度向下伸展，但保留底部留白；标注「不向下伸展」的变体严格约束在安全区内）。
5. **渲染 PNG**：在安装 Chrome/Chromium/Edge 的环境运行：

   ```text
   python scripts/render_poster.py <poster.html> <poster.png> --width 1080 --height 1440
   ```

   脚本必须验证 PNG 为 `1080×1440`。没有兼容浏览器时交付 HTML 并明确报告缺失依赖。
6. **完整视觉 QA**：查看最终 PNG；确认文字在安全区内、未触画布底部/边缘装饰、钩子与信号不重叠、CTA 完整。
7. **局部修订**：只修改用户指出的对象；调整间距/字级时只动对应 CSS 变量，保持画布不变。
8. **交接**：按复盘海报同一 `content-inbox/YYYY-MM-DD-daily/` 目录投递 `poster-YYYYMMDD-teaser.{html,png}`（画布整包随附），在 handoff.md 的海报交付段登记 SHA-256 与 QA 结果。

## 不可变规则

- 固定画布 `1080×1440`（3:4）；HTML 是可编辑源，PNG 是渲染结果。
- 背景**只从** `D:\CC\shared\assets\canvases\` 画布库选取；**不重绘、不裁字入位图**；同一篇只用一种背景。
- 文字、数字、图表全部在 HTML/SVG 层；安全区以所选 variant 的元数据为准。
- CTA 只允许合规字面量：「关注『心猿意马的羊』 · 搜索站内」；**禁止二维码、网址、微信号、跳转外链**。
- 方向色：红=走强/警示 `#A63A2B`、绿=走弱 `#3D6B57`、中性用主字色（中国习惯，勿用美股配色）。
- 不公开持仓、仓位、账户金额、收益截图或具体买卖动作。
- 不运行或修改 ERP、PE、相对比价策略及交易执行。

## 失败汇报

真正卡住时报告：当前阶段、输入日期、涉及文件、完整错误、已尝试方案、当前可交付物、缺失工具或材料，以及未执行的越界动作。
