import { defineMiddleware } from "astro:middleware";
import { DEFAULT_LANG, KIND_SLUGS, familyOfSlug, OLD_LORA_SLUGS, OLD_MCP_SUBS, OLD_TOOL_SLUGS, OLD_TOOL_SUBS, PROFILE_SLUGS, kindOfDetailSlug, listPath, parseList, profilePath } from "./lib/paths.js";

const OTHER = new Set(["en", "es", "de", "it"]);
const OWN = /^\/(a2|a3|api|_astro|robots\.txt|sitemap\.xml|sitemap-web-[a-z]{2}\.xml|llms\.txt|favicon\.svg|healthz)(\/|$)/;
const KINDS = new Set(["prompt", "dataset", "lora", "tool", "model", "agent", "skill", "eval", "rag", "harness"]);

// - /fr/… n'existe pas publiquement : redirection permanente vers la racine.
// - Les catalogues ont des adresses lisibles (/prompts, /en/tools) ; l'ancien ?kind=… y redirige.
// - Tout le reste sans préfixe de langue est servi en interne par les pages [lang] en français.
export const onRequest = defineMiddleware((ctx, next) => {
  const { pathname, searchParams } = ctx.url;
  if (pathname === `/${DEFAULT_LANG}` || pathname.startsWith(`/${DEFAULT_LANG}/`)) {
    return ctx.redirect((pathname.slice(DEFAULT_LANG.length + 1) || "/") + ctx.url.search, 301);
  }
  if (OWN.test(pathname) || ctx.isPrerendered) return next();

  // Une seule adresse par page (SEO) : minuscules, pas de slash final, /en → /en/
  let clean = pathname.toLowerCase().replace(/\/{2,}/g, "/");
  if (OTHER.has(clean.slice(1))) clean += "/";
  else if (clean.length > 1 && clean.endsWith("/") && !OTHER.has(clean.slice(1, -1))) clean = clean.replace(/\/+$/, "");
  if (clean !== pathname) return ctx.redirect(clean + ctx.url.search, 301);

  const parts = pathname.split("/").filter(Boolean);
  const lang = OTHER.has(parts[0]) ? parts.shift() : DEFAULT_LANG;
  const internal = (rest) => `/${lang}${rest}`;

  // Anciennes adresses : « Outils » → « Serveurs MCP » (sans sous-type), « Configs LoRA » → « LoRA »
  {
    const pre = lang === DEFAULT_LANG ? "" : `/${lang}`;
    let seg = [...parts], moved = false;
    if (seg[0] === OLD_TOOL_SLUGS[lang] && OLD_TOOL_SLUGS[lang] !== KIND_SLUGS[lang].tool) { seg[0] = KIND_SLUGS[lang].tool; moved = true; }
    if (seg[0] === OLD_LORA_SLUGS[lang]) { seg[0] = KIND_SLUGS[lang].lora; moved = true; }
    if (seg[0] === KIND_SLUGS[lang].tool && (OLD_TOOL_SUBS[lang].includes(seg[1]) || seg[1] === OLD_MCP_SUBS[lang]) && seg.length !== 3) { seg.splice(1, 1); moved = true; }
    if (moved) return ctx.redirect(`${pre}/${seg.join("/")}` + ctx.url.search, 301);
  }

  // Listes : /outils/serveur-mcp/tag/mcp/langue/fr/tri/recents/page/2 … servies par la page d'accueil.
  // Les anciens paramètres (?kind, ?sub, ?tag, ?clang, ?sort, ?page) redirigent vers l'adresse lisible ; seul ?q reste.
  // Pages de famille : /usage, /entrainement, /extensions
  if (parts.length === 1 && familyOfSlug(lang, parts[0])) {
    ctx.locals.home = true;
    ctx.locals.family = familyOfSlug(lang, parts[0]);
    return next(internal("/" + ctx.url.search));
  }
  const list = parseList(lang, parts);
  if (list) {
    // Accueil : vitrine de tout le site (sauf anciens paramètres ?kind=…, redirigés plus bas)
    const LEGACY0 = ["kind", "sub", "tag", "clang", "sort", "page"];
    if (!parts.length && !LEGACY0.some((p) => searchParams.has(p))) {
      ctx.locals.home = true;
      return next(internal("/" + ctx.url.search));
    }
    // La langue du contenu se filtre sur la page même : aucune adresse /langue/… (pas de page en double)
    if (list.clang) return next(internal("/404"));
    // Anciennes listes de contextes à la racine (/few-shot, /tag/json…) → /contextes/…
    if (parts.length && !Object.values(KIND_SLUGS[lang]).includes(parts[0])) {
      return ctx.redirect(listPath(lang, list) + ctx.url.search, 301);
    }
    const LEGACY = ["kind", "sub", "tag", "clang", "sort", "page"];
    if (LEGACY.some((p) => searchParams.has(p))) {
      const g = (p) => searchParams.get(p) || "";
      if (!parts.length && KINDS.has(g("kind"))) list.kind = g("kind");
      if (g("sub")) list.sub = g("sub");
      if (g("tag")) list.tag = g("tag");
      if (g("clang")) list.clang = g("clang");
      if (["likes", "uses", "recent"].includes(g("sort"))) list.sort = g("sort");
      if (g("page")) list.page = Math.max(1, parseInt(g("page"), 10) || 1);
      else if (searchParams.has("sort")) list.page = 1;
      const q = g("q");
      return ctx.redirect(listPath(lang, list) + (q ? "?q=" + encodeURIComponent(q) : ""), 301);
    }
    ctx.locals.list = list;
    return next(internal("/" + ctx.url.search));
  }
  // Page d'un Lab : /labs/<nom>, servie par la page profil (qui redirige si le compte n'est pas un Lab)
  if (parts.length === 2 && parts[0] === "labs") {
    ctx.locals.lab = true;
    return next(internal(`/u/${parts[1]}` + ctx.url.search));
  }
  // Profils : /profil/<nom> (/en/profile/<nom>…) servi par la page [lang]/u ; l'ancien /u/<nom> y redirige
  if (parts.length === 2 && parts[0] === "u") {
    return ctx.redirect(profilePath(lang, decodeURIComponent(parts[1])) + ctx.url.search, 301);
  }
  if (parts.length === 2 && parts[0] === PROFILE_SLUGS[lang]) {
    return next(internal(`/u/${parts[1]}` + ctx.url.search));
  }
  // Fiches : /outils/<nom>-<court> (/en/tools/…) servies par la page [lang]/r, qui retrouve la fiche.
  if (parts.length === 2 && parts[0] !== "r") {
    const kind = kindOfDetailSlug(lang, parts[0]);
    if (kind) {
      ctx.locals.detailKind = kind;
      ctx.locals.byName = true;  // adresse publique /<type>/<nom>-<court>
      return next(internal(`/r/${parts[1]}` + ctx.url.search));
    }
  }
  if (lang !== DEFAULT_LANG) return next();
  return next(internal(pathname + ctx.url.search));
});
