/**
 * 渠道内容分发配置（单一来源）
 *
 * 分发结构（2026-08-31 调整）：
 *   个人博客 = 中心/最终承接（母版长文）
 *   → 雪球 = 主打引流战场（海报+短评，引回博客）【active】
 *   → 小红书 = 引流板暂停（先不搞，保留配置与模板供将来启用）【paused】
 * 分发脚本 skills/distribute/scripts/distribute.py 与分发模板 docs/distribution/ 读取此配置。
 * 修改渠道信息（尤其是博客链接、CTA、标签、状态）只改这里。
 */

export interface Channel {
  id: "blog" | "xueqiu" | "xhs";
  name: string;
  role: string;
  /** 渠道运行状态：active=正常产出；paused=暂停（保留配置，不默认产出） */
  status: "active" | "paused";
  /** 内容层级：越低越精简（1=完整母版，2=精编，3=钩子） */
  tier: 1 | 2 | 3;
  /** 该渠道配的海报（文件名模板，{} 会被日期 stem 替换） */
  posterFile: string | null;
  /** 是否放长文 */
  longForm: boolean;
  /** 合规 CTA（null 表示该渠道不设站外 CTA 限制或由模板决定） */
  cta: string | null;
  /** 默认话题标签（空格分隔） */
  tags: string[];
}

/** 博客主站链接 = 各渠道唯一通用入口。**站点已于 2026-09-22 上线**（阿里云 DNS + Vercel，国内可访问）。
 *  改域名只改这里，并同步 `skills/distribute/scripts/distribute.py` 的 `BLOG_URL`。 */
export const blogUrl = "https://www.fupanxinyuan.com";

/** 关于我（固定文案，各渠道通用）——**只写身份，不写博客指路** */
// 2026-09-24：原句尾「完整复盘、历史归档与后续校准见博客「心猿意马的羊｜交易复盘」。」
// 与分发模板的「我的博客 · 心猿意马的羊｜交易复盘：A 股每日复盘、历史归档与判断校准的唯一入口」
// 一行内容重复（都提完整复盘 / 历史归档 / 判断校准）。用户拍板合并为「身份一句 + 博客地址」，
// 故此处只留身份，指路与地址交给各渠道自己的 CTA 行（雪球见 distribute.py 的 BLOG_BRIDGE + blogUrl）。
export const aboutText =
  "一个持续记录市场、公开判断边界并回看错误的交易学习者。";

/** 固定免责声明 —— 与 docs/content/site-copy.md 第 7 节一字一致 */
export const disclaimerText =
  "本站内容仅为个人市场复盘、投资交易学习和研究记录，不构成投资建议、收益承诺、代客理财或具体买卖指令。市场有风险，任何决策都应基于独立判断并由决策者自行承担结果。";

export const channels: Channel[] = [
  {
    id: "blog",
    name: "个人博客",
    role: "中心/最终承接：完整 7 段正文 + 来源 + 估值 + 校准 + 关于我 + 研究工具 + 关注入口 + 免责声明",
    status: "active",
    tier: 1,
    posterFile: null,
    longForm: true,
    cta: null,
    tags: [],
  },
  {
    id: "xueqiu",
    name: "雪球",
    role: "主打引流战场（打造 IP）：海报 + 题眼/短评（摘要三句主干）/边界 + 关于我（含博客地址）/免责声明/标签，引回博客",
    // 2026-09-24：删去原 role 里的「研究工具」——派生脚本（distribute.py 的 build_xueqiu）从不输出研究工具块，
    // 且补回会明显加长帖子、与「帖子文字太多」的诉求相反。此处按脚本实际输出对齐；要加研究工具须同时改模板与脚本。
    status: "active",
    tier: 2,
    posterFile: "poster-{}.png", // 1080×2000 复盘海报
    longForm: true,
    cta: blogUrl,
    tags: ["#A股复盘", "#每日复盘", "#交易复盘"],
  },
  {
    id: "xhs",
    name: "小红书",
    role: "引流板暂停（2026-08-31 起，先不搞）：保留 3:4 引流版海报 + 钩子配置，恢复时把 status 改回 active",
    status: "paused",
    tier: 3,
    posterFile: "poster-{}-teaser.png", // 1080×1440 引流版
    longForm: false,
    cta: "关注『心猿意马的羊』 · 搜索站内",
    tags: ["#A股", "#每日复盘", "#ETF", "#投资日记"],
  },
];

/** 小红书禁用词（标题/正文不得出现） */
export const xhsForbiddenWords = ["抄底", "必涨", "翻倍", "稳赚", "荐股", "收益保证"];
