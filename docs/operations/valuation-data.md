---
document_id: VALUATION-DATA-STANDARD
document_role: external_review_workbench_instruction
parent_document: skills/daily-review-notebook-poster/references/handoff-contract.md
version: "1.0"
updated_at: "2026-08-23"
data_root: "D:\\CC\\pe\\data\\"
erp_live_url: "https://index-compare-analysis.vercel.app/data/merged_signal.json"
---

# 周复盘「估值」数据运行规范

> 本文件覆盖周复盘里「宽基估值 / 估值证据」这一栏的完整链路：从哪读数据、数据不新时怎么排查、怎么回填飞书。复盘确认、笔记本海报和交接门槛统一由 `skills/daily-review-notebook-poster/` 管理；本文件只负责估值数据。

## 0. 快速结论

- **估值数据读本地**：`D:\CC\pe\data\` 下的 JSON（宽基 PE / 国债 / 波动率 / 换手集中度 / 红利股息率）。
- **ERP 读线上，不建本地副本**：博客工作区中的同步副本已经删除，直接读取 Vercel 正式站的数据。
- **数据断在某天 = 那天晚上 GitHub Actions 没等到当天数据**（preflight skip），不是策略坏了。
- **回填飞书用 lark-cli**，`block_replace` 只能单 block 逐个改，改完必须重新 fetch 核验。
- **只填事实，不替你写"偏贵/便宜"判断**（SOP 永久边界）。

## 1. 数据源清单

| 数据 | 文件（相对 `D:\CC\pe\data\`） | 关键字段 | 口径 |
|---|---|---|---|
| 宽基指数 PE | `tushare-index-pe-daily.json` | `indexes[code].latest`（当前 PE）、`.median`（中位数）、`.p70`（70 分位）、`.percentile`（历史分位 %） | 日度 |
| 10 年国债收益率 | `chinabond-10y-yield.json` | `latest`、`median`、`p30`（30 分位 = 危险阈值）、`percentile` | 日度 |
| 波动率 | `tushare-index-volatility-daily.json` | `indexes[code].latest.{amplitude, ma5, ma20, ma60}` | 日度 |
| 换手集中度 | `tushare-market-turnover-concentration.json` | `latest.concentration`（%） | 日度 |
| 红利股息率 | `tushare-dividend-strategies.json` | `strategies[key].latest.yield`（%） | **月度快照（月末）** |
| ERP | 线上 `merged_signal.json`（见下） | `components.erp.latest_signal.{equity_premium, bond_yield, pe_ttm, earnings_yield, csi300_close}` | 日度 |

**指数代码映射**：`hs300`=沪深300、`sz50`=上证50、`cyb`=创业板、`zz500`=中证500、`zz1000`=中证1000、`kcb50`=科创50、`zz2000`=中证2000。

### 1.1 ERP 必须读线上

```bash
curl -s "https://index-compare-analysis.vercel.app/data/merged_signal.json"
```

- 取 `components.erp.latest_signal`（含 `equity_premium`=ERP、`pe_ttm`、`bond_yield` 等）。
- 不要在 `D:\CC\shared` 重新建立 `merged_signal.json` 等同步副本；它们容易断同步，权威口径始终以线上正式数据及其日期为准。

## 2. 数据不新时怎么排查

两套数据都靠 GitHub Actions + `TUSHARE_TOKEN` 自动更新：

| 项目 | repo | workflow | 自动时间（北京） | 可见性 |
|---|---|---|---|---|
| 估值罗盘 | `keycool/valuation-compass` | `Refresh daily market data` | 工作日 21:18、22:38 | 私有 |
| ERP | `keycool/index-compare-analysis` | `erp-relative-master-scheduler` | 工作日 23:18 | **公开** |

**判断断因**：数据停在 T 日 = T 日晚上 workflow 没等到当天数据，preflight 判定数据未就绪而 skip，用了 T-1 日。休市日正常没有新数据。

**查运行记录**：
- ERP 仓库公开，可匿名查（无需 token）：
  ```bash
  curl -s "https://api.github.com/repos/keycool/index-compare-analysis/actions/runs?per_page=20"
  ```
  看每次 run 的 `event` / `conclusion`（success / failure / skipped）。也可以直接 `curl` 线上 `merged_signal.json` 看 `latest_date` 和 `generated_at` 判断它实际更新到哪。
- PE 仓库私有，匿名查不到，需要 GitHub PAT 或去网页看。

**补数据**：手动触发对应 workflow（`workflow_dispatch`，选 `latest_complete`），或等下一个工作日自动跑。本地 `.venv` 有 pandas+tushare、本地也有 `TUSHARE_TOKEN` 能跑 fetch 脚本，但**这算改生产数据，需用户明确授权**。

## 3. 回填飞书（lark-cli）

```bash
# 1) 定位（拿 block id）
lark-cli docs +fetch --doc "<token>" --scope keyword --keyword "沪深300" --detail with-ids --as user

# 2) 逐 block 替换（当前版本只支持单 --block-id）
lark-cli docs +update --doc "<token>" --command block_replace \
  --block-id <block_id> --content '<li>沪深300【估】：14.62；中位数：13.54；70分位数：15.31</li>' --as user

# 3) 核验
lark-cli docs +fetch --doc "<token>" --scope keyword --keyword "沪深300" --as user
```

**关键坑（已实测）**：当前 lark-cli binary 1.0.87 的 `docs +update` **不支持** `--start-block-id` / `--end-block-id`（旧 skills 文档 1.0.84 里写过，会报 `unknown flag`）。所以连续多个 `<li>` 必须**逐个 `--block-id` 替换**，不能一次替换区间。

**飞书模板**（周复盘宽基估值栏，字段与数据对应）：

```text
沪深300【估】：<latest>；中位数：<median>；70分位数：<p70>
上证50【估】：<latest>；中位数：<median>；70分位数：<p70>
创业板【估】：<latest>；中位数：<median>；70分位数：<p70>
中证500【估】：<latest>；中位数：<median>；70分位数：<p70>
中证1000【估】：<latest>；中位数：<median>；70分位数：<p70>
十年期国债收益率：<latest>；中位数：<median>；30分位数（危险阈值）：<p30>
```

精度：PE、分位与国债收益率统一保留 **2 位小数**（如国债 `1.69`）——2026-09-12 校正：原写「国债保留 3 位小数」，但 W36 先例与 W37 实际口径均为 2 位，经用户确认改为 2 位，与已回填历史行保持一致。

## 4. 数据日期口径提醒

- PE / 国债 / 波动率 / 集中度：日度，通常到最近一个完整交易日；**周一至周五晚上自动跑，休市日无新数据**。
- 红利股息率：**月度快照**（月末更新，如 07-31），8 月底才出 08-31，属正常。
- ERP：可能比 PE 滞后（它 preflight 更严格，需港股 HSI/HKTECH + 全A股完整日线）。
- 周复盘若要求"整周口径到周五"，而数据只到周四，需向用户确认是否接受缺最后一天，不要擅自补造。

## 5. 边界（不可越）

- 不运行或修改 ERP、PE、相对比价策略和生产数据。
- 自动估值摘要只提供**事实底稿**（数值 + 数据日期），不替用户生成"偏贵 / 便宜 / 该买该卖"的趋势判断。
- 回填飞书只填事实数字，不覆盖用户已确认的判断、点评、感悟原文。
