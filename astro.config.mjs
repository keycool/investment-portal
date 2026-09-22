import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";

export default defineConfig({
  // 生产域名：决定 og:image / canonical / sitemap 的绝对地址。
  // 未设此项时 Astro.url 在静态构建期回退为 http://localhost:4321，会把 og 元数据写坏。
  site: "https://www.fupanxinyuan.com",
  integrations: [mdx()],
  output: "static",
  trailingSlash: "always",
});
