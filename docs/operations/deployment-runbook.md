# 上线操作手册（Vercel + 阿里云云解析）

> 目标：把个人博客 + 三个存量策略站，从 `*.vercel.app`（国内 DNS 被污染）迁到自有域名
> `fupanxinyuan.com`，实现国内正常访问。
>
> 建立日期：2026-09-22｜执行人：【客户甲】与【小金】分工标注在每步标题后

---

## 0. 为什么必须做这件事（技术前提，已实测）

| 结论 | 实测证据 |
|---|---|
| `*.vercel.app` 被 DNS 污染，是**唯一**障碍 | 三个站解析到 173.208.182.68 / 157.240.13.8 / 199.16.158.9（Facebook、Twitter 等无关 IP）；阿里 DoH 返回的也是污染结果 |
| Vercel 本体在国内**完全可用** | nextjs.org / react.dev / svelte.dev / nuxt.com / vercel.com 全部 HTTP 200，`Server: Vercel`，`X-Vercel-Id: sin1::...`（新加坡节点） |
| Vercel 的 IP 未被封 | `76.76.21.241`、`216.198.79.65`、`66.33.60.193` 等 TLSv1.3 握手均成功 |
| CNAME 目标可用 | `cname.vercel-dns.com` 与 `cname.vercel-dns-017.com` 国内直连握手成功 |

**结论：绑自定义域名 = 根治。** 原 `vercel.app` 域名被污染不影响自有域名。

---

## 1. 域名规划（4 条记录 → 4 个项目）

| 用途 | 域名 | Vercel 项目 |
|---|---|---|
| 个人博客（主站） | `www.fupanxinyuan.com` | **待新建**（investment-portal） |
| 根域名跳转 | `fupanxinyuan.com` → 301 跳 www | 同博客项目 |
| ERP 策略 | `erp.fupanxinyuan.com` | `index-compare-analysis` |
| 行业启动 | `etf.fupanxinyuan.com` | `etf-core-constituent-watch` |
| 估值罗盘 | `valuation.fupanxinyuan.com` | `valuation-compass-web` |

---

## 2. 【客户甲】注册域名（含最大的坑）

### 2.1 注册步骤

1. 登录阿里云 → 进入「域名」→「域名注册」（也可直接访问阿里云万网域名页）
2. 搜索框输入 `fupanxinyuan.com`，确认显示「可注册」→ 加入清单
3. 结算前**先创建域名信息模板**（见 2.2，这一步最容易漏）
4. 选择注册年限（建议先 **1 年**，第二年再决定是否续多年）
5. 支付

### 2.2 ⚠️ 必须先做实名认证（否则 DNS 解析根本不生效）

阿里云按工信部要求，境内注册商注册的域名**必须实名**：

1. 阿里云控制台 →「域名」→ 左侧「**信息模板**」→ 创建模板
2. 类型选**个人**，填真实姓名 + 身份证号，上传身份证照片
3. 提交审核 → 个人实名通常**几小时**，最慢 1–3 个工作日
4. 实名通过后，回到域名列表确认域名状态为「**正常**」（不是「待实名认证」）

**关键：域名在「待实名认证」状态下，DNS 解析不会生效。**
如果你配好解析却一直不生效，先回来看域名状态，而不是怀疑 Vercel。

### 2.3 关于备案

**不需要备案。** 备案只在「用中国大陆境内服务器对外提供网站服务」时才要求。
本方案是 Vercel（境外）+ 阿里云只做 DNS 解析，阿里云控制台可能弹「去备案」提示，**忽略即可**。

---

## 3. 【客户甲】在 Vercel 给四个项目绑域名

对**每一个** Vercel 项目重复：

1. 打开 Vercel 控制台 → 选中项目 → **Settings** → **Domains**
2. 输入要绑的域名 → **Add**
3. Vercel 会显示**它要求的记录值和类型** → **以它实际显示的为准**（下面第 4 节给的是通用值）

绑定顺序建议：**先绑三个存量站（erp / etf / valuation），最后绑博客**。
理由：博客里的「研究工具」三个链接指向那三个站，三站先通，博客上线后点开就是活的。

### 各项目要绑的域名

| 项目 | 要添加的域名 |
|---|---|
| `index-compare-analysis` | `erp.fupanxinyuan.com` |
| `etf-core-constituent-watch` | `etf.fupanxinyuan.com` |
| `valuation-compass-web` | `valuation.fupanxinyuan.com` |
| 博客（新建） | `www.fupanxinyuan.com` **设为主域名**，再加 `fupanxinyuan.com` |

> 根域名 `fupanxinyuan.com` 加进博客项目后，Vercel 会自动 301 跳到主域名 `www`，
> 访客输裸域名也能到——这正是你要的「www 为主、根域名跳转」。

---

## 4. 【客户甲】阿里云云解析添加记录

路径：阿里云控制台 →「域名」→ 点进 `fupanxinyuan.com` →「**解析设置**」→ 添加记录

### 记录表（通用值，**以 Vercel 控制台实际显示为准**）

| 主机记录 | 记录类型 | 记录值 | TTL | 说明 |
|---|---|---|---|---|
| `www` | CNAME | `cname.vercel-dns.com` | 10 分钟 | 博客主域名 |
| `@` | A | `76.76.21.21` | 10 分钟 | 根域名跳转（Vercel 对根域名给 A 记录） |
| `erp` | CNAME | `cname.vercel-dns.com` | 10 分钟 | ERP 策略 |
| `etf` | CNAME | `cname.vercel-dns.com` | 10 分钟 | 行业启动 |
| `valuation` | CNAME | `cname.vercel-dns.com` | 10 分钟 | 估值罗盘 |

### ⚠️ 三个必须注意的点

1. **根域名 `@` 不能用 CNAME**。你原方案写「统一加 CNAME」——对子域名正确，但 `@` 上挂 CNAME
   会与 MX（域名邮箱）、TXT 等记录冲突，也不合 DNS 规范。根域名用 **A 记录**。
2. **CNAME 目标值以 Vercel 控制台为准**。Vercel 有时给 `cname.vercel-dns-017.com`。
   两者都已实测国内可用，不用纠结用哪个——照 Vercel 说的填。
3. **不要同时保留 `*.vercel.app` 的旧记录**。如果阿里云里已有指向 vercel.app 的记录，删掉。

---

## 5. 【客户甲】验证

每条记录加完，等 1–10 分钟（受 TTL 与递归缓存影响，最长可能几小时）后验证：

1. 浏览器无痕窗口打开 `https://erp.fupanxinyuan.com/` → 能打开即通
2. 同样验证 `etf.` / `valuation.` / `www.`
3. Vercel 项目页的 Domains 列表里，域名旁出现 ✅（证书已签发）
4. 手机**用 4G/5G 流量**（不要用 WiFi）再开一次 → 这一步最接近访客真实体验，
   **这个通过了才算真的通了**

**SSL 证书**：Vercel 会在 DNS 生效后自动签发，通常几分钟。若长时间显示 "Invalid Configuration"，
说明 DNS 还没生成为 Vercel 看得到的样子——回第 4 节核对记录值。

---

## 6. 【小金】博客部署到 Vercel（GitHub 私有仓库 + 导入）

已选方案：建 **GitHub 私有仓库** → Vercel 导入 → 以后 push 自动部署（与三个存量站同款管道）。

执行顺序：

1. 确认 [客户甲] 已完成 GitHub 授权（或自己建好空私有仓库并把地址给小金）
2. ✅ **已完成**：git 仓库已在 `investment-portal` 初始化并完成首次提交
   - 提交 `7b199ed`，239 文件 / 83.1 MB，分支 `main`
   - `.gitignore`：排除 `node_modules/`、`dist/`、`dist-preview/`、`.astro/`，以及
     `content-inbox/` 的 png/jpg/webp/gif/html（约 184 MB 生产中间产物，不入库，本地保留）
   - `.gitattributes`：文本统一 LF；**`.bat` / `.cmd` 强制 CRLF**（否则 `启动博客.bat` 会被转 LF 而失效）
   - 仓库级身份 `keycool <keycool@163.com>`
3. ✅ 已推送到 GitHub 私有仓库：`https://github.com/keycool/investment-portal.git`
   - 本机无 `gh` CLI、无 SSH 私钥；但已装 Git Credential Manager，HTTPS 推送时应弹窗授权
4. ✅ 已在 Vercel 导入该仓库并完成首次部署：`investment-portal-kappa.vercel.app`
   - Framework 自动识别为 **Astro**；Build Command `npm run build`；Output `dist`
   - 本博客是 `output: "static"` 纯静态站，**不需要装任何 adapter**
5. [客户甲] 绑定 `www.fupanxinyuan.com` + `fupanxinyuan.com`，设 www 为主域名
6. 阿里云补上第 4 节里 www 与 @ 两条记录

---

## 7. 【小金】代码里的域名替换（4 处，必须最后做）

**前置条件：三个子域名已绑好并验证通过。** 否则博客上的研究工具链接会变成死链。

| 文件 | 位置 | 现值 | 改为 |
|---|---|---|---|
| `src/data/channels.ts` | 第 31 行 | `http://localhost:4321` | `https://www.fupanxinyuan.com` |
| `skills/distribute/scripts/distribute.py` | 第 29 行 | `http://localhost:4321` | `https://www.fupanxinyuan.com` |
| `src/data/researchTools.ts` | ERP 项 | `https://index-compare-analysis.vercel.app/` | `https://erp.fupanxinyuan.com/` |
| `src/data/researchTools.ts` | 行业启动项 | `https://etf-core-constituent-watch.vercel.app` | `https://etf.fupanxinyuan.com/` |
| `src/data/researchTools.ts` | 估值罗盘项 | `https://valuation-compass-web.vercel.app/` | `https://valuation.fupanxinyuan.com/` |

> `content-inbox/` 下历史草稿里的 localhost / vercel.app 属**已发布存档，不改**。

改完跑：`npm run check` → `npm run build` → 确认 26 页正常。

---

## 8. 上线验收清单（2026-09-22 20:10 实测结果）

- [x] `fupanxinyuan.com` 域名状态「正常」（实名已通过 2026-09-22 12:15:08；NS = `dns21/dns22.hichina.com`）
- [x] `www.` / 根域名 / `erp.` / `etf.` / `valuation.` 五个地址全部能打开（HTTP 200；根域名 308 → www）
- [x] 四个域名 TLS 证书均由 Vercel 自动签发，SAN 一一对应，有效期剩余 89 天
- [x] 博客首页显示 18 篇复盘（15 每日 + 3 每周）；`/daily/` 列表实测 15 条（08-24 → 09-14）
- [x] 博客「关于」页研究工具三张卡点进去都是新域名且能打开（**已无 vercel.app**）
- [x] 关于页、归档页、单篇复盘页、归档月页正常（16 条路径抽测全部 200）
- [x] `channels.ts` 与 `distribute.py` 两处 blogUrl 已换成正式域名（提交 `a10fa22`）
- [ ] 手机 4G 流量验证（**需【客户甲】本人执行**，这是最接近访客真实体验的一步）
- [ ] 三个存量站的 GitHub Actions 自动更新管道仍正常（按设计不需要改配置，等下一次自动提交验证）

**上线后实测发现的缺陷（已修，见第 10 节）**

- [x] `og:image` 曾指向 `http://localhost:4321/og.png`
- [x] 全站缺 `canonical`、`robots.txt`、`sitemap.xml`

---

## 9. 常见故障排查

| 现象 | 原因与处理 |
|---|---|
| 阿里云配好解析，一直不生效 | 域名**实名认证未通过**（域名状态为「待实名认证」）→ 回第 2.2 节 |
| Vercel 显示 "Invalid Configuration" | DNS 记录值/类型与 Vercel 要求不一致；或 `@` 误用了 CNAME |
| 域名邮箱收不到信 | 根域名 `@` 上挂了 CNAME，覆盖了 MX 记录 → 改回 A 记录 |
| 打不开但 Vercel 显示已绑定 | DNS 缓存未过期（等 TTL）；或本机 hosts / 代理残留 |
| 博客上线后只有 1 篇复盘 | 内容的 `status` 不是 `public`（生产构建只放行 public） |
| 博客上点研究工具跳 vercel.app 打不开 | 第 7 节的 `researchTools.ts` 替换还没做 |
| 雪球草稿里博客链接还是 localhost | `channels.ts` / `distribute.py` 的 blogUrl 还没替换 |
| 分享到微信/雪球，卡片图裂 | `astro.config.mjs` 缺 `site` 字段 → `Astro.url` 回退 localhost → 见第 10 节 |
| 搜索引擎不收录 | 缺 `robots.txt` / `sitemap.xml` → 见第 10 节 |

---

## 10. 上线后实测记录与缺陷修复（2026-09-22）

### 10.1 实测发现的缺陷（已修）

**① `og:image` 指向 localhost（严重）**

线上原值：`<meta property="og:image" content="http://localhost:4321/og.png">`

根因：`astro.config.mjs` **没有 `site` 字段**。`BaseLayout.astro` 用
`new URL(socialImage, Astro.url)` 取绝对地址，而静态构建期 `Astro.url` 在未设
`site` 时回退为 `http://localhost:4321`。

影响：分享链接到微信 / 雪球 / 小红书时，预览卡片的图抓不到。

修法：`astro.config.mjs` 加 `site: "https://www.fupanxinyuan.com"`。

**② 缺 `canonical` / `robots.txt` / `sitemap.xml`**

`canonical` 是 `www` 与根域名并存时的去重前提；`robots.txt` + `sitemap.xml` 是收录基础。
三者线上实测均为 404 / 缺失。

修法：
- `src/layouts/BaseLayout.astro`：输出 `<link rel="canonical">`、`og:url`、`og:site_name`、`og:locale`
- `public/robots.txt`：`Allow: /` + Sitemap 指向
- `src/pages/sitemap.xml.ts`：**构建期生成，不引第三方依赖**。口径与站内一致：
  用 `isVisible()` 过滤（只放行 public），静态路由 + 归档月页（由复盘日期 `slice(0,7)` 去重得出）
  + 每篇复盘 + 研究笔记，共 26 条 URL

> 为什么不用 `@astrojs/sitemap`：本仓只需覆盖 26 个页面，自建 endpoint 零依赖、
> 且能复用 `isVisible()` 与 `reviewHref()`，口径不会和站内可见性脱钩。

### 10.2 修复后复验

| 项 | 结果 |
|---|---|
| `npm run check` | 0 errors / 0 warnings / 0 hints |
| `npm run build` | **26 page(s) built**（含 `/sitemap.xml`） |
| `dist/` 内 `localhost:4321` 残留 | **0 个文件**（修复前首页命中） |
| 首页 og:image | `https://www.fupanxinyuan.com/og.png` |
| 单篇 canonical | `https://www.fupanxinyuan.com/daily/2026-09-14/` |
| `sitemap.xml` | 26 条 `<loc>`，全部绝对地址 |

### 10.3 DNS 与证书实测（修复前基线，证明域名层已通）

```
fupanxinyuan.com               A 216.198.79.1                    → 308 → https://www.fupanxinyuan.com/
www.fupanxinyuan.com           CNAME 97bc68645b9cd26f.vercel-dns-017.com.  A 216.198.79.65 / 64.29.17.65
erp.fupanxinyuan.com           CNAME 897f7c5a2940a2eb.vercel-dns-017.com.  A 216.198.79.65 / 64.29.17.65
etf.fupanxinyuan.com           CNAME 5cac2931691d1088.vercel-dns-017.com.  A 64.29.17.1  / 216.198.79.1
valuation.fupanxinyuan.com     CNAME 6ab485e728263455.vercel-dns-017.com.  A 64.29.17.65 / 216.198.79.65
```

四个项目各拿到 unique 前缀的 CNAME（与第 4 节「以 Vercel 显示为准」一致）；
根域名 A 记录 216.198.79.1 而非手册里写的 76.76.21.21 —— **Vercel 换过根域名 IP，以实际下发的为准**。

### 10.4 本机 git 推送通道（重要）

本机环境有 `https_proxy=http://127.0.0.1:9681`，git 走代理会报
`CONNECT tunnel failed, response 502`。**必须直连推送**：

```bash
git -c http.proxy= -c https.proxy= push origin main
```

（`git ls-remote` 同样要加这两个 `-c` 才能验证远端状态。）

---

## 附：已完成 / 待完成

**已完成（2026-09-22）**

- ✅ 技术前提全部实测验证
- ✅ 17 篇 preview 复盘升级为 public（public 18 / draft 4），备份于
  `D:\CC\shared\backups\reviews-20260922-before-promote\`
- ✅ 域名 `fupanxinyuan.com` **实名认证通过**（12:15:08），NS 已生效（`dns21/dns22.hichina.com`）
- ✅ git 仓库建立并推送：`https://github.com/keycool/investment-portal.git`（私有），分支 `main`
  - `7b199ed` 首次提交（239 文件 / 83.1 MB）
  - `bfedd1c` 同步上线手册状态并记录内容审查发现
  - `a10fa22` 第 7 节 5 处域名替换（channels.ts / distribute.py / researchTools.ts ×3）
- ✅ Vercel 导入博客仓库并部署：`investment-portal-kappa.vercel.app` → 已绑自定义域名
- ✅ 阿里云云解析 5 条记录全部生效；根域名 308 → www
- ✅ 五个地址 + 四个 TLS 证书实测通过；`/daily/` 列表 15 条；「关于」页研究工具已指向新域名
- ✅ 第 10 节两项缺陷已修（og:image localhost、缺 canonical/robots/sitemap）

**待客户甲**

- ⬜ **手机 4G/5G 流量**打开 `https://www.fupanxinyuan.com/` 复核（最接近访客真实体验）
- ⬜ 三项内容审查拍板（见下）
- ⬜ 三个存量站的 GitHub Actions 管道下次自动提交时，确认仍正常生效

**⚠️ 待客户甲拍板的两项内容审查发现（线上现状已确认存在）**

1. **每篇复盘的「数据与来源」段会渲染可点击的飞书母稿链接**
   `src/layouts/ReviewArticle.astro` 输出 `<a href="https://ikvq9lfu7s.feishu.cn/docx/...">`（`target="_blank"`）。
   实测匿名访问返回 **302**（跳登录页）→ **内容不泄露**，但暴露 workspace 域名与文档 ID，
   且访客点开是死链。**线上 09-14 页实测确实带有该链接。**
2. **同段落渲染出内部 SOP 用语**
   线上 09-14 页实测原文：`…文档 JvZjdShCKo4qKYx6nDXcevVinle，三段已回填并 fetch 复核通过（revision 509；506 → 507 判断 → 508 点评 → …）`。
   其中「三段已回填」「fetch 复核」为内部流程术语。
   **注**：`publishing-workflow.md` §6.1 本就要求「飞书母稿来源须逐项署名带 revision」，
   故 revision 可能是**刻意保留的可追溯信息**，与「公开判断边界」的定位一致 —— 未擅自改动。

**其他待定优化项**

- ⬜ `public/images/posters/` 有 18 个文件（**34.2 MB**）从未被任何 MDX 引用
  （teaser 引流版 / orange-cats / 背景图），可清理以减小仓库与部署体积
- ⬜ `public/og.png` 为 **2.5 MB**，超出社交平台抓取上限的常见经验值（建议压到 200 KB 内、1200×630）
- ⬜ `researchNotes` 集合为空，构建期会打印
  `The collection "researchNotes" does not exist or is empty.`（**非错误，构建正常完成**）
