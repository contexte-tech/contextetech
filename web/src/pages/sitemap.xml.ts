import type { APIRoute } from "astro";
import { LANGS } from "../lib/i18n.js";
import { site } from "../lib/server.js";

// Index des sitemaps : un sitemap par langue (sitemap-web-fr.xml, -en…). Seul cet index est déclaré dans robots.txt.
export const GET: APIRoute = () => {
  const S = site();
  const now = new Date().toISOString();
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${Object.keys(LANGS).map((l) => `<sitemap><loc>${S.origin}/sitemap-web-${l}.xml</loc><lastmod>${now}</lastmod></sitemap>`).join("")}</sitemapindex>`;
  return new Response(xml, { headers: { "Content-Type": "application/xml; charset=utf-8", "Cache-Control": "public, max-age=3600" } });
};
