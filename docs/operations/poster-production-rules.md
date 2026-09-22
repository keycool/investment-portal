---
document_id: POSTER-PRODUCTION-RULES
document_role: external_review_workbench_instruction
version: "1.0"
updated_at: "2026-08-25"
applies_to:
  - skills/daily-review-notebook-poster/   # 复盘海报 1080×2000
  - skills/teaser-poster/                  # 引流版 1080×1440
---

# 海报生产规则总纲（poster-production-rules）

> 复盘海报（notebook 1080×2000）与引流版（orbit 3:4 1080×1440）**共用**的生成纪律。各 skill 的具体输入契约见各自 references；本文件只写跨版本必须遵守的规则与可复用经验。

## 1. 权威顺序与确认门槛（硬门槛）

权威顺序固定：**确认母稿 → 结构化输入 JSON → HTML → PNG → 交接包 → 网站编辑版**。

- 今日判断 / 收盘点评 / 个人感悟 **三段全部确认** + **一次性回填母稿** + **重新读取复核**，才允许 `ready`。
- 三段未全确认时只能出标记 `preview` 的候选；不得回填、不得写 `ready`、不得虚构回填状态。
- 缺失来源、日期或数值保持缺失，不得猜测；不能从旧 PNG 反推完整文章。

## 2. 题眼措辞（用户口径，反复校准的教训）

- 两段式：`已发生事实 / 当前状态`；**尽量简洁、偏事实、不偏观点**（2026-09-09 用户校准）：两段都用当日量价、涨跌结构、板块/风格状态的实义词（如「缩量普跌 / 热点隐身」），不写观点判断与解读（「钱往国债躲」「避险抢跑」这类归入正文）；观点、条件（尚未确认/边界）放正文，**不入标题**。
- **避免抽象词**：「广度回归」「结构性分化」这类被否过；改用**具体可感、口语化**的表达（如「缩量普涨 / 轮动无主」「群龙无首」「盲头苍蝇」）。
- 不把「修复」升级为「反转」，不把「待验证」改成「已确认」。
- 板块/风格用温和中性描述（「小票强于老登」「轮动无主」），不做过度定性。

## 3. 配色（中国习惯，勿用美股配色）

- 红 = 走强 / 警示；绿 = 走弱 / 下跌。
- 复盘海报（notebook）：深青底、红 `#e08aa0`、绿 `#7fc4a8`。
- 引流版（orbit）：奶白底、主字深青 `#16465B`、强调暗金 `#D5A746`、方向色红 `#A63A2B` / 绿 `#3D6B57`。
- 中性/无方向数据用主字色，不用红绿。

## 4. 背景与文字分层（硬约束）

- 背景是**固定资产**：复盘海报背景走画布库 `notebook-paper` 包（`daily-review-notebook-poster` 的 `build_poster.py` 默认从 `D:\CC\shared\assets\canvases\notebook-paper\` 读取，支持 `CANVAS_LIB` 环境变量）；引流版背景**只从** `D:\CC\shared\assets\canvases\` 画布库选取（库规范见 `canvas-library.md`，用 `teaser-poster/scripts/list_canvases.py` 列出并选 variant）。
- **不重绘背景**：不得让图像模型再画一张；背景必须保持精确时用「固定背景 + 可编辑文字层」的 hybrid 方式。
- **文字永不进位图**：中文/数字/表格一律在 HTML/SVG 可编辑层；不得在 AI 位图上涂改修补错误文字（改 prompt 重生成或走精确渲染）。
- 引流版文字必须尊重**所选 variant** 的安全区（`recommended_text_area` 换算到 1080×1440）；标注「不向下伸展」的变体（如橘猫）严格约束在安全区内；notebook 文字不得越出纸面（以 `notebook-poster-template.html` 的 .sheet 布局为准）。
- **变体规则**（USAGE/canvas-library）：新背景 = 加版本化 sibling PNG + 在 `variants.json` 加条目（含 SHA + safe area + mood + name_cn）；**永不覆盖已有变体**，除非用户明确要求替换。

## 5. 备份纪律（血泪教训）

- **改任何底图/背景前先备份原图**（copy 一份 `-original` 或进 archive）。
- 2026-08-24 教训：notebook 原底图未备份，用户整理目录时被清掉，image-to-image 重绘后原图不可恢复。

## 6. QA 探针（模型看不了图时的程序化兜底）

当前会话模型可能无法直接查看 PNG，视觉 QA 必须**程序化探针 + 用户目检**双轨：

| 探针 | 做法 | 通过标准 |
|---|---|---|
| 像素核验 | `render_poster.py` 读 PNG IHDR | notebook 1080×2000；引流版 1080×1440 |
| 内容高度 | `render_poster.py <poster.html> --probe`（脚本自动注入白底 + 解除裁切，在 2600px 高画布渲染并扫最底内容像素，退出码 0=PASS） | 底部余量 ≥0（notebook 建议留 20-40px 视觉留白） |
| 安全区包围盒 | 同上，扫内容 min/max x/y | 以所选 variant 的 `recommended_text_area` 换算区间为准；标注「不向下伸展」的变体严格约束 |
| 背景 SHA | sha256(背景) vs 所选 variant 的 `variants.json`/`canvas.json` | 一致（以 `list_canvases.py` 输出为准） |
| CTA 字面量 | 逐字核对 | 仅「关注『心猿意马的羊』 · 搜索站内」 |

目检项（用户兜底）：字体无乱码、无重叠、装饰（钢笔/轨道/弧线）不遮正文与页脚。

## 7. CTA 合规（引流版硬约束）

- 唯一允许：`关注『心猿意马的羊』 · 搜索站内`
- **禁止**：二维码、网址、微信号/手机号、外链跳转、任何站外转化形式。

## 8. 估值数据回填

- 周复盘或含估值栏母稿：按 `docs/operations/valuation-data.md` 读取本地 `D:\CC\pe\data` + 线上 ERP merged_signal.json。
- **只填事实数字 + 数据日期，不生成「偏贵/便宜」判断**；断档保持缺失不补造；用 lark-cli `block_replace` 逐个回填并重新 fetch 复核（当前 binary 只支持单 `--block-id`）。

## 9. 交接包

- 统一投递 `content-inbox/YYYY-MM-DD-daily/`（或 `YYYY-Www-weekly/`）。
- 复盘海报：`poster-YYYYMMDD.{html,png}`；引流版：`poster-YYYYMMDD-teaser.{html,png}`（画布整包随附）。
- handoff.md 按 `handoff-contract.md` 模板，登记双海报 SHA-256 + QA 结果 + CTA 合规检查。
- 稳定文件名不带 `preview`/`-vN`；候选留在临时目录，确认后清理。

## 10. 局部修订

- 只修改用户指出的对象；调整视觉变量时**每次只改一个**，不重生成整套内容。
- 调整钢笔/装饰位置时保持纸张、线圈、木桌、绿植、光线、比例、角度不变（可整体右移出画）。
- 候选阶段用 `-vN` 防止误覆盖；用户确认后删除被拒绝版本，避免旧逻辑再次被选中。

## 11. 临时文件与进程清理纪律（防垃圾泄漏）

**根源**：Chrome headless 截图时，`--user-data-dir` 临时 profile 由多进程子进程（renderer/GPU/utility）持有句柄；主进程退出后子进程延迟释放句柄，Windows 下被占用目录/文件无法删除，`shutil.rmtree` 失败即残留垃圾。叠加「固定名 CWD 临时文件 + `&& rm -f` 链」的写法，链中任一步失败（渲染超时、探针报错、回填 `rm` 意外执行）就泄漏 `_p*.html` / `_probe_tmp.*` / `_seg_*.xml` / `_0*.json` 等固定名垃圾。

**硬规则**：

1. **临时文件一律用 `tempfile`**（`mkdtemp` / `NamedTemporaryFile` / `TemporaryDirectory`），禁止在项目根 / skill 目录写固定名临时文件（`_p827.html`、`_probe_tmp.png` 之类）。
2. **渲染/探针一律走 `render_poster.py`**，禁止 inline Python + `&& rm -f` 链手工清理；脚本内部已做进程树终止 + `finally` 清理 + 失败时删半成品截图。
3. **清理必须放 `finally`**，并显式捕获 `subprocess.TimeoutExpired` 杀进程树、删半成品；`rmtree` 兜底失败时打 stderr 警告，不静默吞错。
4. **产物只进交接目录**（`content-inbox/YYYY-MM-DD-daily/` 或 `--output-dir`），探针中间产物放临时目录，不落项目根。
5. **lark 回填的分段 XML / 中间 JSON** 用 `tempfile` 临时文件，回填完成后在 `finally` 中清理，不与海报产物混放。
6. 每轮海报收尾时自检一次根目录与 skill 目录是否出现 `_*` / `__pycache__` 残留，发现即清理。
