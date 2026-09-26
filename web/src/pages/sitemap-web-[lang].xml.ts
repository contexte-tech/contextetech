import type { APIRoute } from "astro";
import { contentLang, docsPath, familyPath, labPath, SUB_SLUGS, kindPath, listPath, pre, profilePath, resourcePath, tagPath } from "../lib/paths.js";
import { LANGS } from "../lib/i18n.js";
import { site } from "../lib/server.js";

// Un sitemap par langue : /sitemap-web-fr.xml, /sitemap-web-en.xml… (déclarés uniquement dans l'index /sitemap.xml)
export const GET: APIRoute = async ({ params }) => {
  const lang = String(params.lang || "");
  if (!(lang in LANGS)) return new Response("Not found", { status: 404 });
  const S = site();
  const res = await fetch((process.env.API_INTERNAL_URL || "http://api:8000") + "/api/sitemap");
  const { items, authors = [], tags = [] } = res.ok ? await res.json() : { items: [] };
  const langs = Object.keys(LANGS);
  // Chaque URL avec ses équivalents dans les autres langues ; `at(l)` donne l'adresse dans la langue l
  const addAt = (at: (l: string) => string, lastmod?: number) => {
    const alt = langs.map((l) => `<xhtml:link rel="alternate" hreflang="${l}" href="${S.origin}${at(l)}"/>`).join("");
    urls.push(`<url><loc>${S.origin}${at(lang)}</loc>${lastmod ? `<lastmod>${new Date(lastmod).toISOString()}</lastmod>` : ""}${alt}</url>`);
  };
  const urls: string[] = [];
  const add = (path: string, lastmod?: number) => addAt((l) => `${pre(l)}${path}`, lastmod);
  add("/");
  for (const k of ["context", "prompt", "dataset", "lora", "tool", "model", "agent", "skill", "eval", "rag", "harness"]) addAt((l) => kindPath(l, k));
  add("/open-source");
  // Pages de sous-type : /few-shot, /outils/serveur-mcp…
  for (const [k, subs] of Object.entries(SUB_SLUGS.fr)) for (const sub of Object.keys(subs)) addAt((l) => listPath(l, { kind: k, sub }));
  for (const g of tags) addAt((l) => tagPath(l, g.kind, g.tag));
  add("/labs");
  for (const fam of ["fam_usage", "fam_training", "fam_ext"]) addAt((l) => familyPath(l, fam));
  addAt((l) => docsPath(l));
  for (const k of ["context", "prompt", "dataset", "lora", "tool", "model", "agent", "skill", "eval", "rag", "harness"]) addAt((l) => docsPath(l, k));
  for (const a of authors) addAt((l) => (a.lab ? labPath(l, a.name) : profilePath(l, a.name)), a.updatedAt);
  // Fiches : uniquement dans la langue de leur contenu, sans hreflang (contenu non traduit)
  for (const it of items) if (contentLang(it.clang) === lang)
    urls.push(`<url><loc>${S.origin}${resourcePath(lang, it.kind, it.id)}</loc>${it.updatedAt ? `<lastmod>${new Date(it.updatedAt).toISOString()}</lastmod>` : ""}</url>`);
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">${urls.join("")}</urlset>`;
  return new Response(xml.replace(/&(?!amp;)/g, "&amp;"), {
    headers: { "Content-Type": "application/xml; charset=utf-8", "Cache-Control": "public, max-age=3600" },
  });
};
