// Le français est la langue par défaut : il vit à la racine (/outils/…), les autres sous /en/, /es/…
export const DEFAULT_LANG = "fr";
// Une fiche n'est indexée que dans la langue de son contenu (multilingue ou autre langue : langue par défaut) ;
// les autres versions ne traduisent que l'interface et pointent vers celle-ci en canonique.
export const contentLang = (clang) => (["fr", "en", "es", "de", "it"].includes(clang) ? clang : DEFAULT_LANG);
export const pre = (lang) => (lang === DEFAULT_LANG ? "" : `/${lang}`);

// Adresses lisibles des catalogues, traduites : /prompts, /outils, /en/tools… (les contextes sont l'accueil)
export const KIND_SLUGS = {
  fr: { context: "contextes", prompt: "prompts", dataset: "datasets", lora: "lora", tool: "serveurs-mcp", model: "modeles", agent: "agents", skill: "skills", eval: "evaluations", rag: "rag", harness: "harness" },
  en: { context: "contexts", prompt: "prompts", dataset: "datasets", lora: "lora", tool: "mcp-servers", model: "models", agent: "agents", skill: "skills", eval: "evals", rag: "rag", harness: "harness" },
  es: { context: "contextos", prompt: "prompts", dataset: "datasets", lora: "lora", tool: "servidores-mcp", model: "modelos", agent: "agentes", skill: "skills", eval: "evaluaciones", rag: "rag", harness: "harness" },
  de: { context: "kontexte", prompt: "prompts", dataset: "datensaetze", lora: "lora", tool: "mcp-server", model: "modelle", agent: "agenten", skill: "skills", eval: "evaluierungen", rag: "rag", harness: "harness" },
  it: { context: "contesti", prompt: "prompt", dataset: "dataset", lora: "lora", tool: "server-mcp", model: "modelli", agent: "agenti", skill: "skills", eval: "valutazioni", rag: "rag", harness: "harness" },
};
export const kindPath = (lang, kind) => {
  const slug = (KIND_SLUGS[lang] || KIND_SLUGS[DEFAULT_LANG])[kind];
  return `${pre(lang)}/${slug || ""}`;
};
/** Type correspondant à un slug d'une langue donnée, ou null */
export const kindOfSlug = (lang, slug) => {
  const m = KIND_SLUGS[lang] || {};
  return Object.keys(m).find((k) => m[k] === slug) || null;
};

// Profil public : /profil/<nom>, /en/profile/<nom>…
export const PROFILE_SLUGS = { fr: "profil", en: "profile", es: "perfil", de: "profil", it: "profilo" };
export const profilePath = (lang, name) => `${pre(lang)}/${PROFILE_SLUGS[lang] || PROFILE_SLUGS[DEFAULT_LANG]}/${encodeURIComponent(name)}`;

// Fiche d'une ressource : /<type>/<id> (/outils/…, /en/tools/…). Les contextes ont leur propre segment.
export const CONTEXT_SLUGS = { fr: "contextes", en: "contexts", es: "contextos", de: "kontexte", it: "contesti" };
const detailSlug = (lang, kind) => kind === "context"
  ? CONTEXT_SLUGS[lang] || CONTEXT_SLUGS[DEFAULT_LANG]
  : (KIND_SLUGS[lang] || KIND_SLUGS[DEFAULT_LANG])[kind];
// Identifiant court d'une fiche : FNV-1a 32 bits en base 36 (même calcul côté API : short_id)
export const shortId = (id) => {
  let h = 0x811c9dc5;
  for (const b of new TextEncoder().encode(String(id))) h = Math.imul(h ^ b, 0x01000193) >>> 0;
  return h.toString(36);
};
// Adresse d'une fiche : /<type>/<nom>-<identifiant court> (sans l'auteur ; deux auteurs peuvent choisir le même nom).
// L'identifiant interne reste « auteur--nom ».
export const resourcePath = (lang, kind, id) => {
  const i = String(id).indexOf("--");
  return `${pre(lang)}/${detailSlug(lang, kind)}/${encodeURIComponent(i > 0 ? id.slice(i + 2) : id)}-${shortId(id)}`;
};
/** Type dont le segment de fiche vaut `slug` dans la langue donnée, ou null */
export const kindOfDetailSlug = (lang, slug) =>
  ["context", "prompt", "dataset", "lora", "tool", "model", "agent", "skill", "eval", "rag", "harness"].find((k) => detailSlug(lang, k) === slug) || null;

// Page d'un tag : /contextes/tag/json, /serveurs-mcp/tag/mcp…
export const tagPath = (lang, kind, tag) => listPath(lang, { kind, tag });

// ---- Listes : toutes les options dans l'adresse, traduites ----
// /<type>/<sous-type>/modele/<famille>/tag/<t>/langue/<code>/tri/<ordre>/page/<n> (chaque partie facultative, dans cet ordre)
export const SUB_SLUGS = {
  fr: { context: { fewshot: "few-shot", system: "instruction-systeme", knowledge: "connaissances", persona: "persona" },
        dataset: { chat: "chat", instruction: "instruction", completion: "completion" }, lora: { lora: "lora", qlora: "qlora" },
        model: { finetune: "fine-tune", merge: "merge", quantized: "quantifie", base: "base" } },
  en: { context: { fewshot: "few-shot", system: "system-prompt", knowledge: "knowledge", persona: "persona" },
        dataset: { chat: "chat", instruction: "instruction", completion: "completion" }, lora: { lora: "lora", qlora: "qlora" },
        model: { finetune: "fine-tune", merge: "merge", quantized: "quantized", base: "base" } },
  es: { context: { fewshot: "few-shot", system: "instruccion-sistema", knowledge: "conocimiento", persona: "persona" },
        dataset: { chat: "chat", instruction: "instruccion", completion: "completion" }, lora: { lora: "lora", qlora: "qlora" },
        model: { finetune: "fine-tune", merge: "merge", quantized: "cuantizado", base: "base" } },
  de: { context: { fewshot: "few-shot", system: "system-prompt", knowledge: "wissen", persona: "persona" },
        dataset: { chat: "chat", instruction: "instruktion", completion: "completion" }, lora: { lora: "lora", qlora: "qlora" },
        model: { finetune: "fine-tune", merge: "merge", quantized: "quantisiert", base: "base" } },
  it: { context: { fewshot: "few-shot", system: "istruzione-sistema", knowledge: "conoscenze", persona: "persona" },
        dataset: { chat: "chat", instruction: "istruzione", completion: "completion" }, lora: { lora: "lora", qlora: "qlora" },
        model: { finetune: "fine-tune", merge: "merge", quantized: "quantizzato", base: "base" } },
};
export const LIST_KEYS = {
  fr: { tag: "tag", target: "modele", clang: "langue", sort: "tri", page: "page" },
  en: { tag: "tag", target: "model", clang: "language", sort: "sort", page: "page" },
  es: { tag: "tag", target: "modelo", clang: "idioma", sort: "orden", page: "pagina" },
  de: { tag: "tag", target: "modell", clang: "sprache", sort: "sortierung", page: "seite" },
  it: { tag: "tag", target: "modello", clang: "lingua", sort: "ordine", page: "pagina" },
};
export const SORT_SLUGS = {
  fr: { uses: "plus-utilises", recent: "recents" }, en: { uses: "most-used", recent: "recent" },
  es: { uses: "mas-usados", recent: "recientes" }, de: { uses: "meistgenutzt", recent: "neueste" },
  it: { uses: "piu-usati", recent: "recenti" },
};
const L = (m, lang) => m[lang] || m[DEFAULT_LANG];

/** Adresse d'une liste filtrée ; f = { kind, sub, tag, clang, sort, page } */
export const listPath = (lang, f = {}) => {
  const kind = f.kind || "context";
  const k = L(LIST_KEYS, lang);
  const segs = [];
  if (f.sub) segs.push(L(SUB_SLUGS, lang)[kind]?.[f.sub] || f.sub);
  if (f.target) segs.push(k.target, f.target);
  if (f.tag) segs.push(k.tag, encodeURIComponent(f.tag));
  if (f.clang) segs.push(k.clang, f.clang);
  if (f.sort && f.sort !== "likes") segs.push(k.sort, L(SORT_SLUGS, lang)[f.sort] || f.sort);
  if (f.page > 1) segs.push(k.page, String(f.page));
  const base = kindPath(lang, kind);
  return segs.length ? `${base}/${segs.join("/")}` : base;
};

/** Lit une adresse de liste (segments sans la langue) ; renvoie les filtres, ou null si ce n'est pas une liste */
export const parseList = (lang, parts) => {
  const f = { kind: "context", sub: "", target: "", tag: "", clang: "", sort: "likes", page: 1 };
  let i = 0;
  const kind = parts.length ? kindOfSlug(lang, parts[0]) : null;
  if (kind) { f.kind = kind; i = 1; }
  const subs = L(SUB_SLUGS, lang)[f.kind] || {};
  const sub = i < parts.length && Object.keys(subs).find((s) => subs[s] === parts[i]);
  if (sub) { f.sub = sub; i++; }
  const k = L(LIST_KEYS, lang);
  const sorts = L(SORT_SLUGS, lang);
  while (i < parts.length) {
    const key = parts[i], val = parts[i + 1];
    if (val === undefined) return null;
    if (key === k.tag) f.tag = decodeURIComponent(val);
    else if (key === k.target && /^[a-z]{2,10}$/.test(val)) f.target = val;
    else if (key === k.clang && /^[a-z]{2,5}$/.test(val)) f.clang = val;
    else if (key === k.sort && Object.values(sorts).includes(val)) f.sort = Object.keys(sorts).find((s) => sorts[s] === val);
    else if (key === k.page && /^[1-9][0-9]{0,2}$/.test(val)) f.page = Number(val);
    else return null;
    i += 2;
  }
  return f;
};

// Labs : annuaire /labs et page d'un lab /labs/<nom> (même mot dans toutes les langues)
export const labsPath = (lang) => `${pre(lang)}/labs`;
export const labPath = (lang, name) => `${pre(lang)}/labs/${encodeURIComponent(name)}`;

// Anciennes adresses du type « Outils » (avant son renommage en « Serveurs MCP »)
export const OLD_TOOL_SLUGS = { fr: "outils", en: "tools", es: "herramientas", de: "werkzeuge", it: "strumenti" };
export const OLD_MCP_SUBS = { fr: "serveur-mcp", en: "mcp-server", es: "servidor-mcp", de: "mcp-server", it: "server-mcp" };
export const OLD_LORA_SLUGS = { fr: "configs-lora", en: "lora-configs", es: "configuraciones-lora", de: "lora-konfigurationen", it: "configurazioni-lora" };
export const OLD_TOOL_SUBS = { fr: ["mcp", "fonction"], en: ["mcp", "function"], es: ["mcp", "funcion"], de: ["mcp", "funktion"], it: ["mcp", "funzione"] };
/** Accueil d'une langue : / (français), /en/, /es/… */
export const homePath = (lang) => `${pre(lang)}/`;

// Documentation : /docs (sommaire) et /docs/<type> (/docs/serveurs-mcp, /en/docs/mcp-servers…)
export const docsPath = (lang, kind) => `${pre(lang)}/docs${kind ? "/" + (KIND_SLUGS[lang] || KIND_SLUGS[DEFAULT_LANG])[kind] : ""}`;

// Pages de famille : /usage, /entrainement, /extensions (la famille Modèles utilise /modeles)
export const FAMILY_SLUGS = {
  fr: { fam_usage: "production", fam_training: "entrainement", fam_ext: "extensions" },
  en: { fam_usage: "production", fam_training: "training", fam_ext: "extensions" },
  es: { fam_usage: "produccion", fam_training: "entrenamiento", fam_ext: "extensiones" },
  de: { fam_usage: "produktion", fam_training: "training", fam_ext: "erweiterungen" },
  it: { fam_usage: "produzione", fam_training: "addestramento", fam_ext: "estensioni" },
};
export const familyPath = (lang, fam) => {
  const slug = (FAMILY_SLUGS[lang] || FAMILY_SLUGS[DEFAULT_LANG])[fam];
  return slug ? `${pre(lang)}/${slug}` : kindPath(lang, "model");
};
export const familyOfSlug = (lang, slug) => {
  const m = FAMILY_SLUGS[lang] || {};
  return Object.keys(m).find((f) => m[f] === slug) || null;
};
