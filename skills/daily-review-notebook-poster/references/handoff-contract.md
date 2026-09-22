# 正式交接契约

只在判断、点评、感悟均确认，母稿已回填复核，HTML/PNG 一致且 QA 通过后生成 `ready` 包。

## 目录

```text
content-inbox/YYYY-MM-DD-daily/
├─ handoff.md
├─ poster-YYYYMMDD.html
├─ poster-YYYYMMDD.png
└─ notebook-background.png
```

确认后的稳定文件不得带 `preview` 或 `-vN`。候选版本留在临时工作目录，确认后删除被拒绝版本。

## handoff.md 模板

```markdown
# 复盘交接单

## 基本信息
- 类型：daily
- 内容日期：YYYY-MM-DD
- 飞书或母稿链接：
- 作者：心猿意马的羊
- 交接状态：ready / incomplete / preview
- 终稿确认时间：
- 交接包生成时间：

## 确认记录
- 今日判断：已确认 / 未确认
- 收盘点评：已确认 / 未确认
- 个人感悟：已确认 / 未确认
- 三段一次性回填：已完成 / 未完成
- 回填后复核：已通过 / 未通过

## 已确认题眼
<已发生事实> / <当前判断>

## 公开摘要
<主要事实、结构矛盾和最重要边界>

## 关键事实
| 指标 | 数值或状态 | 数据截止 | 具体来源 | 它说明什么 |
|---|---|---|---|---|
| | | | | |

## 当前判断
<确认原文>

## 边界与观察
- <条件一>
- <条件二>
- <条件三>

## 收盘点评
<确认原文>

## 个人感悟
<确认原文>

## 海报交付
- HTML：poster-YYYYMMDD.html
- PNG：poster-YYYYMMDD.png
- 背景：notebook-background.png
- 画布：1080×2000
- QA：passed / failed
- SHA-256：

## 合规检查
- 数据来源完整：是 / 否
- 含持仓或账户信息：否
- 含具体买卖动作：否
- 免责声明：已包含

## 未完成事项
- 无 / <逐项填写>
```

## 写入边界

- 只向用户指定的交接目录新增文件。
- 不修改网站 MDX、站点代码、策略仓库、生产数据或外部发布状态。
- 缺少具体来源时可保留 `incomplete`，不能升级为网站预览。
- 已接收的正式交接包属于内容证据，不作为可随意清理的视觉历史。

## 补录（poster 已交付但 handoff 缺失）

历史遗留日期需要补交接单时：

1. 重跑 QA，不沿用口头结论：`python scripts/render_poster.py <poster.html> --probe`（退出码 0 = 未溢出）+ 重算 PNG 尺寸与四个 SHA-256。
2. 底图 SHA 必须与画布库注册版本比对一致（`D:\CC\shared\assets\canvases\*\*.png`），确认用的是当初选定的那一版。
3. **时间字段不得补造**：`交接包生成时间` 填真实补录时间并标注「补录」；`海报定稿确认时间` 若当初未留痕，如实写「未单独记录」并在 `## 未完成事项` 复述，不推定、不回填一个看起来合理的时刻。
4. 补录后更新 `docs/operations/completion-log.md` 对应行的「交接包接收时间」与「当前状态或原因」；`distribution-log.md` 是 append-only 且只记发布状态，交接包补录不改变发布状态，不新增行。

