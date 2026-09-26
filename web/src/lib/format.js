// Logique partagée serveur (Astro) / navigateur (îlots Svelte)

// Mots-clés techniques associés à chaque type (affichés sous le titre du catalogue, repris pour le référencement)
export const KEYWORDS = {
  context: ["in-context learning", "system prompt", "few-shot", "persona", "RAG"],
  prompt: ["prompt engineering", "template", "variables", "chain-of-thought", "zero-shot"],
  dataset: ["fine-tuning", "JSONL", "SFT", "instruction tuning", "ChatML"],
  lora: ["LoRA", "QLoRA", "PEFT", "Axolotl", "Unsloth"],
  tool: ["MCP", "Model Context Protocol", "function calling", "tool use", "AI connectors"],
  model: ["fine-tune", "merge", "quantization", "GGUF", "safetensors"],
  agent: ["AI agent", "agentic", "Claude Agent SDK", "LangGraph", "CrewAI"],
  skill: ["Claude Skills", "custom instructions", "workflow", "automation"],
  eval: ["LLM evaluation", "benchmark", "LLM-as-a-judge", "regression tests"],
  rag: ["RAG", "embeddings", "vector database", "chunking", "reranking"],
  harness: ["Claude Code", "CLAUDE.md", "agent config", "permissions", "hooks"],
};
// Niveau de risque d'un serveur MCP ou d'un harness d'après les accès déclarés
export const riskOf = (a) => !a ? "none" : a.exec ? "high" : a.write || a.network ? "mid" : a.read ? "low" : "none";
export const KINDS = ["context", "prompt", "dataset", "lora", "tool", "model", "agent", "skill", "eval", "rag", "harness"];
// Familles de types : comment chaque ressource adapte un modèle IA
export const FAMILIES = [
  ["fam_usage", ["context", "prompt", "agent", "rag"]],
  ["fam_training", ["dataset", "lora", "eval"]],
  ["fam_ext", ["tool", "skill", "harness"]],
  ["fam_models", ["model"]],
];
export const KCOLOR = { context: "var(--k-context)", prompt: "var(--k-prompt)", dataset: "var(--k-dataset)", lora: "var(--k-lora)", tool: "var(--k-tool)", model: "var(--k-model)", agent: "var(--k-agent)", skill: "var(--k-skill)", eval: "var(--k-eval)", rag: "var(--k-rag)", harness: "var(--k-harness)" };
export const SUB = {
  context: { field: "type", label: "f_type", opts: { fewshot: "st_fewshot", system: "st_system", knowledge: "st_knowledge", persona: "st_persona" } },
  dataset: { field: "format", label: "f_format", opts: { chat: "sf_chat", instruction: "sf_instruction", completion: "sf_completion" } },
  lora: { field: "method", label: "f_method", opts: { lora: "sm_lora", qlora: "sm_qlora" } },
  model: { field: "modelType", label: "f_modeltype", opts: { finetune: "mt_finetune", merge: "mt_merge", quantized: "mt_quantized", base: "mt_base" } },
};
export const TARGET_FAMILIES = { claude: "Claude", gpt: "GPT", gemini: "Gemini", llama: "Llama", mistral: "Mistral", qwen: "Qwen", deepseek: "DeepSeek", gemma: "Gemma", phi: "Phi", other: "fam_other" };
export const TARGET_KINDS = ["context", "prompt", "tool", "agent", "skill", "eval", "rag", "harness"];
export const VECTOR_STORES = { pgvector: "pgvector", qdrant: "Qdrant", chroma: "Chroma", weaviate: "Weaviate", pinecone: "Pinecone", faiss: "FAISS", other: "fam_other" };
export const HARNESSES = { "claude-code": "Claude Code", "claude-agent-sdk": "Claude Agent SDK", cursor: "Cursor", other: "fam_other" };
export const AGENT_FRAMEWORKS = { "claude-agent-sdk": "Claude Agent SDK", langgraph: "LangGraph", crewai: "CrewAI", "openai-agents": "OpenAI Agents SDK", other: "fam_other" };
export const EVAL_METRICS = ["contains", "exact", "regex", "llm-judge"];
export const targetName = (t, fam) => { const x = TARGET_FAMILIES[fam]; return !x ? "" : x.startsWith("fam_") ? t(x) : x; };
export const MODEL_FORMATS = ["safetensors", "gguf", "gptq", "awq", "mlx", "onnx"];
export const MODEL_FAMILIES = { llama: "Llama", mistral: "Mistral", qwen: "Qwen", gemma: "Gemma", deepseek: "DeepSeek", phi: "Phi", other: "fam_other" };

/** Serveur MCP au format mcpServers (Claude Desktop, Claude Code, Cursor…) */
export function mcpConfig(it) {
  const env = Object.fromEntries((it.env || []).map((k) => [k, "…"]));
  if (it.transport === "http") return { mcpServers: { [it.toolName]: { type: "http", url: it.url } } };
  const [command, ...args] = String(it.command || "").trim().split(/\s+/);
  return { mcpServers: { [it.toolName]: { command, args, ...(Object.keys(env).length ? { env } : {}) } } };
}
/** Définition d'outil au format Anthropic */
export const toolAnthropic = (it) => ({ name: it.toolName, description: it.toolDescription || "", input_schema: it.schema || { type: "object", properties: {} } });
export const CLANGS = ["fr", "en", "es", "de", "it", "pt", "nl", "multi"];
export const LICENSES = { "": "lic_none", "MIT": "MIT", "Apache-2.0": "Apache 2.0", "CC-BY-4.0": "CC BY 4.0", "CC-BY-SA-4.0": "CC BY-SA 4.0", "CC-BY-NC-4.0": "CC BY-NC 4.0", "CC0-1.0": "lic_cc0", "proprietary": "lic_prop" };
export const licName = (t, v) => { const x = LICENSES[v || ""]; return x === undefined ? v : x.startsWith("lic_") ? t(x) : x; };
export const subOf = (it) => { const s = SUB[it.kind]; return s ? it[s.field] || "" : ""; };
export const subLabel = (t, it) => { const s = SUB[it.kind]; const o = s && s.opts[subOf(it)]; return o ? t(o) : ""; };

export const slugify = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
  .replace(/[^a-z0-9._]+/g, "-").replace(/^-|-$/g, "").slice(0, 60);
export const author = (it) => it.authorHandle || "community";
export const fullId = (it) => `${author(it)}/${it.name}`;

export const varsOf = (s) => [...new Set([...String(s || "").matchAll(/\{\{\s*([\w-]+)\s*\}\}/g)].map((m) => m[1]))];
export const fillTpl = (s, v) => String(s).replace(/\{\{\s*([\w-]+)\s*\}\}/g, (m, k) => v[k] ?? m);

export function parseJSONL(s) {
  const rows = [], errors = [];
  String(s || "").split(/\r?\n/).forEach((l, i) => {
    if (!l.trim()) return;
    try { const o = JSON.parse(l); if (o && typeof o === "object") rows.push(o); else errors.push(i + 1); }
    catch { errors.push(i + 1); }
  });
  return { rows, errors };
}
export function detectFormat(r) {
  if (!r || typeof r !== "object") return null;
  if (Array.isArray(r.messages)) return "chat";
  if ("instruction" in r || ("input" in r && "output" in r)) return "instruction";
  if ("prompt" in r && "completion" in r) return "completion";
  return null;
}
export function rowToPair(r) {
  const f = detectFormat(r);
  if (f === "chat") {
    const m = r.messages; let a = -1, u = -1;
    for (let i = m.length - 1; i >= 0; i--) if (m[i].role === "assistant") { a = i; break; }
    for (let i = a - 1; i >= 0; i--) if (m[i].role === "user") { u = i; break; }
    return { input: u >= 0 ? String(m[u].content) : "", output: a >= 0 ? String(m[a].content) : "" };
  }
  if (f === "instruction") return { input: [r.instruction, r.input].filter(Boolean).join("\n\n"), output: String(r.output ?? "") };
  if (f === "completion") return { input: String(r.prompt), output: String(r.completion) };
  return { input: "", output: "" };
}
export function datasetPairs(it) {
  const rows = it.jsonl ? parseJSONL(it.jsonl).rows : (it.preview || []);
  return rows.map(rowToPair).filter((p) => p.input && p.output);
}

export function buildTurns(it, input, pairs) {
  const pre = [];
  if (it.system) pre.push(`<instructions>\n${it.system}\n</instructions>`);
  if (it.knowledge) pre.push(`<knowledge>\n${it.knowledge}\n</knowledge>`);
  const head = pre.length ? pre.join("\n\n") + "\n\n" : "";
  const ex = (pairs || it.examples || []).filter((e) => e.input && e.output);
  if (!ex.length) return [{ role: "user", content: head + input }];
  const r = [];
  ex.forEach((e, i) => { r.push({ role: "user", content: (i === 0 ? head : "") + e.input }); r.push({ role: "assistant", content: e.output }); });
  r.push({ role: "user", content: input });
  return r;
}

export function axolotlYAML(it, ds) {
  const dt = { chat: "chat_template", instruction: "alpaca", completion: "completion" }[ds?.format] || "chat_template";
  return `base_model: ${it.baseModel}
${it.method === "qlora" ? "load_in_4bit: true\n" : ""}adapter: ${it.method}
lora_r: ${it.r}
lora_alpha: ${it.alpha}
lora_dropout: ${it.dropout}
lora_target_modules:
${(it.targets || []).map((x) => "  - " + x).join("\n")}

sequence_len: ${it.seqLen}
micro_batch_size: ${it.batch}
gradient_accumulation_steps: ${it.gradAcc}
num_epochs: ${it.epochs}
learning_rate: ${it.lr}
optimizer: adamw_torch
lr_scheduler: cosine
bf16: auto

datasets:
  - path: ${ds ? slugify(ds.name) + ".jsonl" : "data.jsonl"}
    type: ${dt}

output_dir: ./outputs/${slugify(it.name)}`;
}

export function peftPy(it) {
  const q = it.method === "qlora";
  return `from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM${q ? ", BitsAndBytesConfig" : ""}
${q ? `
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                         bnb_4bit_compute_dtype="bfloat16")` : ""}
model = AutoModelForCausalLM.from_pretrained(
    "${it.baseModel}"${q ? ", quantization_config=bnb" : ""}, device_map="auto")

config = LoraConfig(
    r=${it.r}, lora_alpha=${it.alpha}, lora_dropout=${it.dropout},
    target_modules=${JSON.stringify(it.targets || [])},
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, config)
model.print_trainable_parameters()
# lr=${it.lr}, epochs=${it.epochs}, batch=${it.batch}, grad_acc=${it.gradAcc}, max_seq_len=${it.seqLen}`;
}

/** Fichier exporté ; pour les datasets, le téléchargement passe par l'API. */
export function exportOf(it, ds) {
  const n = slugify(it.name);
  const base = { id: fullId(it), description: it.description, tags: it.tags, license: it.license || null, language: it.clang || null };
  if (it.kind === "context") return { filename: n + ".json", text: JSON.stringify({ format: "contextec/context/v1", ...base, type: it.type, system: it.system || "", knowledge: it.knowledge || "", examples: it.examples || [], messages_template: buildTurns(it, "{{input}}") }, null, 2) };
  if (it.kind === "prompt") return { filename: n + ".json", text: JSON.stringify({ format: "contextec/prompt/v1", ...base, template: it.template, variables: varsOf(it.template) }, null, 2) };
  if (it.kind === "dataset") return { filename: n + ".jsonl", text: it.jsonl ? String(it.jsonl).trim() + "\n" : (it.preview || []).map((r) => JSON.stringify(r)).join("\n") + "\n", remote: true };
  if (it.kind === "model") return { filename: n + ".model.json", text: JSON.stringify({ format: "contextetech/model/v1", ...base,
    type: it.modelType, baseModel: it.baseModel, family: it.family, params: it.params, weightsFormat: it.format, quant: it.quant,
    contextLength: it.contextLength, weightsUrl: it.weightsUrl }, null, 2) };
  if (it.kind === "agent") return { filename: n + ".agent.json", text: JSON.stringify({ format: "contextetech/agent/v1", ...base, framework: it.framework, instructions: it.instructions, steps: it.steps || [], mcp: it.mcpIds || [], contexts: it.contextIds || [], guardrails: it.guardrails || "" }, null, 2) };
  if (it.kind === "skill") return { filename: "SKILL.md", text: `---\nname: ${it.skillName}\ndescription: ${(it.whenToUse || it.description || "").replace(/\n/g, " ")}\n---\n\n${it.instructions || ""}\n` };
  if (it.kind === "rag") return { filename: n + ".rag.json", text: JSON.stringify({ format: "contextetech/rag/v1", ...base, sources: it.sources, chunking: { size: it.chunkSize, overlap: it.chunkOverlap }, embedding: it.embedding, vectorStore: it.vectorStore, retrieval: { topK: it.topK, reranker: it.reranker || null }, promptTemplate: it.promptTemplate }, null, 2) };
  if (it.kind === "harness") return it.harness === "claude-code"
    ? { filename: "settings.json", text: JSON.stringify({ permissions: { allow: it.allow || [], deny: it.deny || [] }, ...(it.hooks ? { hooks: (() => { try { return JSON.parse(it.hooks); } catch { return it.hooks; } })() } : {}) }, null, 2) }
    : { filename: n + ".harness.json", text: JSON.stringify({ format: "contextetech/harness/v1", ...base, harness: it.harness, instructions: it.instructions, allow: it.allow, deny: it.deny, hooks: it.hooks, mcp: it.mcpIds }, null, 2) };
  if (it.kind === "eval") return { filename: n + ".eval.jsonl", text: (it.cases || []).map((c) => JSON.stringify(c)).join("\n") + "\n" };
  if (it.kind === "tool") return it.toolType === "mcp"
    ? { filename: n + ".mcp.json", text: JSON.stringify(mcpConfig(it), null, 2) }
    : { filename: n + ".json", text: JSON.stringify(toolAnthropic(it), null, 2) };
  return { filename: n + ".yaml", text: axolotlYAML(it, ds) };
}

export function snippetsOf(it, t, origin = "") {
  const n = slugify(it.name);
  if (it.kind === "context") return [[t("sn_ctx"), `import json, anthropic

ctx = json.load(open("${n}.json"))

def build(ctx, user_input):
    return [{**m, "content": m["content"].replace("{{input}}", user_input)}
            for m in ctx["messages_template"]]

client = anthropic.Anthropic()
resp = client.messages.create(model="claude-sonnet-5", max_tokens=1024,
                              messages=build(ctx, "${t("your_input")}"))
print(resp.content[0].text)`]];
  if (it.kind === "prompt") return [[t("sn_prompt"), `import json, re

p = json.load(open("${n}.json"))

def render(p, **values):
    return re.sub(r"\\{\\{\\s*([\\w-]+)\\s*\\}\\}", lambda m: str(values[m[1]]), p["template"])

prompt = render(p, ${varsOf(it.template).map((v) => `${v.replace(/-/g, "_")}="…"`).join(", ")})`]];
  if (it.kind === "dataset") return [[t("sn_ds"), `# wget ${origin}/api/resources/${it.id}/download -O ${n}.jsonl
from datasets import load_dataset

ds = load_dataset("json", data_files="${n}.jsonl", split="train")
ds = ds.train_test_split(test_size=0.1, seed=42)
print(ds)`]];
  if (it.kind === "model") return it.format === "gguf" ? [
    [t("sn_model_dl"), `curl -L -o ${n}.gguf "${it.weightsUrl}"`],
    ["llama.cpp", `llama-cli -m ${n}.gguf -p "${t("your_input")}"`],
    ["Ollama", `echo 'FROM ./${n}.gguf' > Modelfile\nollama create ${n} -f Modelfile\nollama run ${n}`],
  ] : [
    [t("sn_model_dl"), `# ${it.weightsUrl}`],
    ["Transformers (Python)", `from transformers import AutoModelForCausalLM, AutoTokenizer

path = "./${n}"   # dossier des poids téléchargés
tok = AutoTokenizer.from_pretrained(path)
model = AutoModelForCausalLM.from_pretrained(path, device_map="auto")
inputs = tok("${t("your_input")}", return_tensors="pt").to(model.device)
print(tok.decode(model.generate(**inputs, max_new_tokens=200)[0]))`],
  ];
  if (it.kind === "rag") return [[t("sn_rag"), `import json
cfg = json.load(open("${n}.rag.json"))

# 1. Découper les documents : morceaux de ${it.chunkSize} caractères, chevauchement ${it.chunkOverlap}
# 2. Vectoriser chaque morceau avec « ${it.embedding} » et l'enregistrer dans ${it.vectorStore}
# 3. À chaque question : retrouver les ${it.topK} morceaux les plus proches${it.reranker ? ", les reclasser avec « " + it.reranker + " »" : ""}
# 4. Remplir le gabarit et l'envoyer au modèle
prompt = cfg["promptTemplate"].replace("{{context}}", "\\n\\n".join(extraits)).replace("{{question}}", question)`]];
  if (it.kind === "harness") return it.harness === "claude-code" ? [
    ["CLAUDE.md", it.instructions || ""],
    [".claude/settings.json", JSON.stringify({ permissions: { allow: it.allow || [], deny: it.deny || [] } }, null, 2)],
  ] : [[t("sn_harness"), it.instructions || ""]];
  if (it.kind === "skill") return [
    ["Claude Code", `mkdir -p ~/.claude/skills/${it.skillName}\n# enregistrez SKILL.md dans ~/.claude/skills/${it.skillName}/SKILL.md`],
    [t("sn_skill_project"), `mkdir -p .claude/skills/${it.skillName}\n# enregistrez SKILL.md dans .claude/skills/${it.skillName}/SKILL.md`],
  ];
  if (it.kind === "eval") return [[t("sn_eval"), `import json, re

cases = [json.loads(l) for l in open("${n}.eval.jsonl")]

def score(answer, expected, metric="${it.metric}"):
    if metric == "exact": return answer.strip() == expected.strip()
    if metric == "regex": return re.search(expected, answer) is not None
    return expected.lower() in answer.lower()   # contains (llm-judge : faire noter par un modèle)

def run(ask):  # ask(input) -> réponse du modèle
    ok = sum(score(ask(c["input"]), c["expected"]) for c in cases)
    print(f"{ok}/{len(cases)} réussis ({100 * ok // len(cases)} %), seuil ${it.threshold} %")`]];
  if (it.kind === "agent") return [[t("sn_agent"), `import json, anthropic

agent = json.load(open("${n}.agent.json"))
system = agent["instructions"] + "\\n\\nÉtapes :\\n" + "\\n".join(f"{i+1}. {s}" for i, s in enumerate(agent["steps"]))
if agent["guardrails"]: system += "\\n\\nRègles : " + agent["guardrails"]

client = anthropic.Anthropic()
resp = client.messages.create(model="claude-sonnet-5", max_tokens=1024, system=system,
                              messages=[{"role": "user", "content": "${t("your_input")}"}])
print(resp.content[0].text)`]];
  if (it.kind === "tool" && it.toolType === "mcp") return [
    [t("sn_mcp_code"), `claude mcp add ${it.toolName} ${it.transport === "http" ? "--transport http " + it.url : "-- " + it.command}`],
    [t("sn_mcp_desktop"), JSON.stringify(mcpConfig(it), null, 2)],
  ];
  if (it.kind === "tool") return [
    [t("sn_tool_anthropic"), `import json, anthropic

tool = json.load(open("${n}.json"))
client = anthropic.Anthropic()
resp = client.messages.create(model="claude-sonnet-5", max_tokens=1024, tools=[tool],
                              messages=[{"role": "user", "content": "${t("your_input")}"}])
for block in resp.content:
    if block.type == "tool_use":
        print(block.name, block.input)`],
    [t("sn_tool_openai"), JSON.stringify({ type: "function", function: { name: it.toolName, description: it.toolDescription || "", parameters: it.schema || {} } }, null, 2)],
  ];
  return [[t("sn_peft"), peftPy(it)]];
}
