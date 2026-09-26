import type { APIRoute } from "astro";
import { KINDS, author } from "../lib/format.js";
import { docsPath, kindPath, resourcePath } from "../lib/paths.js";
import { translator } from "../lib/i18n.js";
import { site } from "../lib/server.js";

// llms.txt (https://llmstxt.org) : présentation du site pour les assistants IA, en Markdown
export const GET: APIRoute = async () => {
  const S = site();
  const t = translator("fr", S.name);
  const en = translator("en", S.name);
  const res = await fetch((process.env.API_INTERNAL_URL || "http://api:8000") + "/api/resources?kind=all&sort=recent&page=1").catch(() => null);
  const items = res && res.ok ? (await res.json()).items || [] : [];
  const L = [
    `# ${S.name}`,
    "",
    `> Hub open source de ressources pour LLM : contextes, prompts, datasets de fine-tuning, configurations LoRA, serveurs MCP, modèles, agents, skills, évaluations, pipelines RAG et harness. Site en français, avec des versions en anglais, espagnol, allemand et italien. Open-source hub of LLM resources.`,
    "",
    "Chaque fiche s'exporte au format de l'outil visé (JSON, JSONL, YAML, SKILL.md, configuration MCP) depuis son onglet « Utiliser ».",
    "",
    "## Catalogues",
    "",
    ...KINDS.map((k) => `- [${t("k_" + k)}](${S.origin}${kindPath("fr", k)}): ${t("d_" + k)}`),
    "",
    "## Documentation",
    "",
    ...KINDS.map((k) => `- [${t("dq_" + k)}](${S.origin}${docsPath("fr", k)})`),
    "",
  ];
  if (items.length) {
    L.push("## Ressources récentes", "");
    for (const it of items) L.push(`- [${author(it)}/${it.name}](${S.origin}${resourcePath("fr", it.kind, it.id)}): ${(it.description || t("o_" + it.kind)).replace(/\s+/g, " ")}`);
    L.push("");
  }
  L.push("## Optional", "",
    `- [English version](${S.origin}/en/): ${en("meta_desc")}`,
    `- [Sitemap](${S.origin}/sitemap.xml)`,
    `- [Open source](${S.origin}/open-source)`, "");
  return new Response(L.join("\n"), { headers: { "Content-Type": "text/markdown; charset=utf-8", "Cache-Control": "public, max-age=3600" } });
};
