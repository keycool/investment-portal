# 引流版契约（teaser-contract）

## 定位

小红书/私域/引流入口。画布 3:4（1080×1440），轨道纸底 + 中央留白；只放「钩子 + 信号 + 判断 + 金句 + CTA」，刻意少、可快速读。

## 输入契约（poster-teaser-input-template.json）

| 字段 | 约束 |
|---|---|
| `date` / `display_date` / `issue` / `author` | ISO 日期 / 显示日期 / 通常 MMDD / 心猿意马的羊 |
| `title` | **恰好两行**：第一行事实或观点，第二行强调（暗金 `#D5A746`）；两行合成一个完整钩子 |
| `lead` | 一句导语：核心事实 + 主要矛盾 + 边界，两行半以内 |
| `signals` | **恰好 3 个**（动能/量能/广度），每项 `tag` + `val` + `desc` + `direction`（red/green/neutral） |
| `verdict` | 一句次日/下周判断，吊胃口不展开 |
| `quote` | 一句金句（个人感悟），可换行控节奏 |
| `cta` | 合规字面量（见下），不可自由发挥 |
| `source_text` / `disclaimer` | 数据来源（带 as_of）+ 免责声明 |

`direction` 只允许：`red`（走强/警示）、`green`（走弱）、`neutral`（无方向/事实）。

## 视觉规范

### 背景来源（数据驱动，不写死任何包）

- **背景唯一权威库**：`D:\CC\shared\assets\canvases\<pack-id>\`（用户维护，持续扩容）。
- **选背景流程**：
  1. 运行 `scripts/list_canvases.py` 或打开 `D:\CC\shared\assets\canvases\gallery.html` 视觉面板看可用背景；
  2. 按**内容氛围**选 pack + variant——优先看 `selection.json` 的默认记忆（daily/weekly/essay 各自的默认），用户要换按**中文名**（`name_cn`，如「专业轨道」「橘猫彩蛋」「星云随笔」）一句话切换；
  3. 读取所选 variant 的 `recommended_text_area`（来自该包的 `variants.json` 或 `canvas.json`）作为内容区基准；
  4. 把选中的 **pack 整包**（背景 PNG + canvas.json + variants.json + USAGE）拷进交接包目录，做 SHA 校验；
  5. 渲染。**同一篇复盘只用一种背景，不混搭。**
- 新包格式、mood/name_cn 规范、selection.json 与加包规则见 `docs/operations/canvas-library.md`；本契约不再写死具体包。

### 选背景对话协议（用户侧一句话）

每次出引流版前，agent 给一行提案，用户一个字/一个中文名回复：

> 今日氛围 = 严肃复盘 → 建议【专业轨道】｜可换：橘猫彩蛋 / 星云随笔

- 「过」或「好」= 用建议；「星云」「橘猫」= 换用对应 `name_cn`；
- 用户没指定时按 `selection.json` 对应内容类型的默认走；换用后 agent 更新 `selection.json` 记住。

### 布局与配色（通用规则）

- 背景**原图固定**，`center/cover` 铺满；文字、数字、图表全部在 HTML/SVG 可编辑层。
- 主字/强调色从所选画布的 `palette` 取：**亮底画布**用深主字 + 高对比强调；**深底画布**（如星云）用浅主字（cream/lilac 系）保证对比度。
- **方向色**：亮底画布红 `#A63A2B`（走强/警示）、绿 `#3D6B57`（走弱）；**深底画布改用高亮版**——红 `#E0655E`、绿 `#7FBF9D`，保证深底可读（中国习惯：红强绿弱，勿用美股配色）。
- 字体：PingFang SC / Microsoft YaHei / Noto Sans SC（无衬线，清晰优先）。
- **内容区**：以所选 variant 的 `recommended_text_area`（native 1086×1448 → 画布 1080×1440 约 ×0.9945 缩放）为基准；布局可适度向下伸展，但**必须保留底部留白**（默认 ≥300px；若变体有「不向下伸展」的注释（如橘猫），则严格约束在安全区内）。
- 排版不压缩中段：块间距拉开（eyebrow 顶距 ~36px、signals 顶距 ~46px、verdict ~44px、quote ~40px），钩子字级 60-62px、信号数值 40-42px；安全区较小时（如 500px 高）按比例压缩字级与间距。教训：v1 全挤在中段被否，向下伸展后通过。

## CTA 合规（硬约束）

- 唯一允许字面量：「关注『心猿意马的羊』 · 搜索站内」
- **禁止**：二维码、网址、微信/手机号、外链跳转、诱导关注话术以外的任何转化形式。

## QA 清单

1. PNG 像素 **1080×1440**（脚本核验）。
2. 安全区包围盒探针：白底 + overflow visible + 加高窗口渲染，扫描内容最左/最右/最上/最下像素，须落在**所选 variant** 的 `recommended_text_area` 换算区间内（X 严格；Y 上限看变体——默认可伸展到底边距 ≥300px，标注「不向下伸展」的变体（如橘猫）严格约束在安全区内）。
3. 背景 SHA-256 与所选 variant 的 `variants.json`/`canvas.json` 条目一致（以 `list_canvases.py` 输出为准）。
4. CTA 字面量逐字核对；无二维码/网址/微信号。
5. 目检：文字无乱码、无重叠、无触底装饰 / 无压到画布边缘元素（猫、星座等）；画布装饰不侵入正文。
