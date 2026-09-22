---
document_id: CANVAS-LIBRARY
document_role: external_review_workbench_instruction
version: "1.0"
updated_at: "2026-08-26"
library_root: "D:\\CC\\shared\\assets\\canvases\\"
consumers:
  - skills/teaser-poster/        # 引流版 1080×1440（背景按内容氛围选择）
---

# 画布库规范（canvas-library）

> 引流版（3:4 1080×1440）背景的**唯一权威来源**是 `D:\CC\shared\assets\canvases\`。本文件定义库的结构、每个包必须满足的元数据契约（最小准入标准）、如何新增包、如何按内容氛围选择，以及 SHA 校验。用户会持续往库里加背景，读取流程必须数据驱动、零代码改动。

## 1. 库结构与包的最小准入标准

```
D:\CC\shared\assets\canvases\
├─ <pack-id>\
│  ├─ USAGE.md            # 使用说明 + 该包的添加规则（USAGE / USAGE.md 均可，大小写不敏感）
│  ├─ canvas.json         # 必填：包级元数据（见 §2）
│  ├─ variants.json       # 可选：多变体索引；单变体包可省略（回退用 canvas.json）
│  ├─ background.png      # 默认变体（或 <id>-v1.png 等命名）
│  └─ background-*.png    # 版本化 sibling 变体（新增背景=加文件+索引，不覆盖已有）
```

**新包准入（三个都满足才算合格）**：
1. 有 `USAGE.md`（或 `USAGE`）；
2. 有 `canvas.json`，且必填字段齐全（见 §2）；
3. 至少一个背景 PNG（native 尺寸建议与画布同比例，如 1086×1448 → 1080×1440 3:4）。

读流程的兜底：缺 `variants.json` 时自动退化用 `canvas.json` 单变体；缺 `canvas.json` 时报错并指明缺哪个文件；`list_canvases.py` 会列出所有不合格项。

## 2. canvas.json 必填字段与 mood 标签

```json
{
  "id": "pack-id",
  "version": "1.0.0",
  "role": "background-canvas",
  "aspect_ratio": "3:4",
  "native_size": [1086, 1448],
  "file": "background.png",
  "sha256": "HEX_UPPERCASE",
  "recommended_text_area": {"x": 0, "y": 0, "width": 0, "height": 0,
                            "note": "…"},
  "palette": ["#…"],
  "visual_elements": ["…"],
  "content_policy": {"text": "…", "logo_watermark": "…", "distortion": "…"},
  "recommended_engine": "hybrid",
  "mood": ["professional", "data-led", "clean"]
}
```

- **必填**：`id`、`aspect_ratio`、`native_size`、`file`、`sha256`、`recommended_text_area`、`palette`。
- **`mood`（建议必填）**：字符串标签数组，供 agent 按内容氛围自动建议。常用值：
  - `professional` / `data-led` / `clean` —— 严肃、数据密集（orbit-paper 默认）
  - `playful` / `light` —— 轻量、日常、彩蛋（orbit-paper 橘猫）
  - `dreamy` / `narrative` / `reflective` —— 叙事、随笔、梦幻（星云）
- **`name_cn`（建议必填，选择的关键）**：中文显示名，用户在对话里**只报这个名字**就锁定背景（如「专业轨道」「橘猫彩蛋」「星云随笔」）。缺省回退到 `pack-id`。
- **变体级 mood/name_cn**：`variants.json` 的每个 variant 可带自己的 `mood` 与 `name_cn`；缺省时分别继承包级 `canvas.json.mood` / 回退 pack-id。

## 3. variants.json 结构（多变体包必填）

```json
{
  "pack_id": "pack-id",
  "version": "1.1.0",
  "selection_rule": "Choose one background variant per output; never overwrite an existing variant.",
  "variants": [
    {"id": "pack-id", "file": "background.png", "metadata_file": "canvas.json",
     "name_cn": "专业轨道", "description": "…", "mood": ["professional"]},
    {"id": "pack-id-cats-v1", "file": "background-orange-cats-v1.png",
     "metadata_file": "variants.json", "derived_from": "pack-id",
     "native_size": [1086, 1448], "sha256": "…",
     "recommended_text_area": {"x": 0, "y": 0, "width": 0, "height": 0},
     "description": "…", "mood": ["playful", "light"]}
  ]
}
```

- 每个 variant 应有 `id` + `file` + `description`；**推荐**带 `sha256` + `recommended_text_area`（与默认不同的变体**必须**带，否则安全区用错会压到装饰元素）。
- 与默认不同的安全区、不同 mood 的变体（如橘猫）必须在条目里显式声明。

## 4. 如何新增背景（你的操作步骤）

1. 生成新背景 PNG（用 RVS hybrid 或其它工具），**保持与库内其它背景同比例**（如 3:4）；
2. 放入对应 pack 目录，**版本化命名**：`background-<特征>-v<N>.png`；不要覆盖已有文件；
3. 在 `variants.json` 的 `variants[]` 加一条（含 id / file / sha256 / recommended_text_area / mood / description）；
4. 若安全区与默认不同，**务必**在条目中写明 `recommended_text_area`（这是 QA 探针的依据）；
5. 也可在 `canvas.json` 更新包级 mood / palette 等。

**新 pack** 则新建目录 + 上面的最小准入三件套。

> 规则：**永不覆盖已验收的变体**；新背景永远是版本化 sibling + 索引条目（USAGE 中的 selection_rule）。

## 5. 如何选择背景（agent 流程）

1. 打开 `gallery.html`（视觉面板，`make_gallery.py` 生成）或运行 `skills/teaser-poster/scripts/list_canvases.py`（可用 `--mood` 过滤）列出全部可选背景；
2. 先看 `selection.json` 默认记忆（daily / weekly / essay 各自的默认变体）；
3. 按**内容氛围**映射到 mood：
   | 氛围 / 内容类型 | mood 关键词 | 参考包 |
   |---|---|---|
   | 严肃数据（复盘、估值） | professional / data-led | orbit-paper-3x4 默认 |
   | 轻量 / 日常 / 彩蛋 | playful / light | orbit-paper-3x4 橘猫 |
   | 叙事 / 随笔 / 梦幻 | dreamy / narrative | xiaohongshu-starry-text |
4. 读所选包的 `USAGE.md` 确认使用约束；
5. 读所选 variant 的 `recommended_text_area` 作为内容区基准（native → 画布 1080×1440 约 ×0.9945）；
6. 把该 pack **整包**拷进 `content-inbox/YYYY-MM-DD-daily/<pack-id>/`（交接包自包含），SHA 校验；
7. 渲染 + QA（安全区包围盒探针、SHA 比对、CTA 合规）。

## 5.5 视觉画廊与默认记忆（用户选择面板）

- **`gallery.html`**（画布库根目录）：卡片式视觉选择面板——每个变体一张卡（真实缩略图 + 中文名 + mood 芯片 + 安全区 + SHA + 描述）。用户打开它**一眼扫过、报中文名**即完成选择。库有变动后运行 `make_gallery.py` 重生成（缩略图内嵌 base64，单文件可双击打开）。
- **`selection.json`**（画布库根目录）：默认记忆——记录 daily / weekly / essay 各自上次选中的默认变体（`pack` + `variant` + `name_cn`）。agent 出图时先按默认提案，用户换用后 agent 更新此文件。
- **对话协议**：agent 每次给一行「今日氛围 → 建议【中文名】｜可换：a / b」，用户回「过/好」（用默认）或中文名（换）。规则见 `teaser-contract.md` 视觉规范段。

## 6. 校验

- 背景 SHA-256 必须与 `canvas.json`/`variants.json` 对应条目一致（`list_canvases.py` 输出即校验表）。
- `list_canvases.py` 会标记：缺 USAGE、缺元数据、PNG 实际尺寸与元数据不一致等不合格项。
- 交接包内的画布副本也要做 SHA 校验，避免中途被改。

## 7. 当前库清单（2026-08-27）

| pack | variant | name_cn | mood | 安全区（native） |
|---|---|---|---|---|
| notebook-paper | 默认 | 笔记本纸 | clean,paper,notebook | x128,y170,666×1450（主海报参考） |
| orbit-paper-3x4 | 默认 | 专业轨道 | professional,data-led,clean | x145,y245,796×640 |
| orbit-paper-3x4 | orange-cats-v1 | 橘猫彩蛋 | playful,light | x150,y390,770×500（不向下伸展） |
| xiaohongshu-starry-text | v1 | 星云随笔 | dreamy,narrative,reflective | x130,y260,826×820 |

> 主海报（notebook 1080×2000）背景也走库：`notebook-paper` 包，由 `daily-review-notebook-poster` skill 出图时按次拷入交接包（`build_poster.py` 默认从库读取，支持 `CANVAS_LIB`）。
> 此清单仅供参考——**以 `list_canvases.py` 实时输出为准**（库会持续扩容）。
