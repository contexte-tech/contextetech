<script>
  import { kindPath, pre, resourcePath } from "../lib/paths.js";
  import { AGENT_FRAMEWORKS, CLANGS, EVAL_METRICS, HARNESSES, LICENSES, VECTOR_STORES, MODEL_FAMILIES, MODEL_FORMATS, SUB, TARGET_FAMILIES, TARGET_KINDS, detectFormat, parseJSONL, slugify, varsOf } from "../lib/format.js";

  let { kind, initial = null, mode = "new", lang = "fr", s, datasets = [], cfg = {}, defaultHandle = "", clangNames = {}, isAdmin = false, knownTags = [], loras = [], models = [], mcps = [], contexts = [], evaluables = [] } = $props();
  const t = (k, v) => { let x = s[k] ?? k; if (v) for (const [a, b] of Object.entries(v)) x = x.split("{" + a + "}").join(String(b)); return x; };
  const sf = SUB[kind];
  const src = initial || {};
  const licLabel = (v) => { const x = LICENSES[v]; return x.startsWith("lic_") ? t(x) : x; };

  // Champs communs
  let name = $state(mode === "fork" ? (src.name || "") + "-fork" : src.name || "");
  // Un membre publie sous son nom ; l'admin peut en choisir un autre
  let handle = $state(isAdmin ? src.authorHandle || defaultHandle : mode === "edit" ? src.authorHandle : defaultHandle);
  let description = $state(src.description || "");
  let tags = $state((src.tags || []).join(", "));
  let clang = $state(src.clang || lang);
  let license = $state(src.license || "");
  let sourceUrl = $state(src.sourceUrl || "");
  let sub = $state(sf ? src[sf.field] || Object.keys(sf.opts)[0] : "");
  let accept = $state(mode === "edit");

  // Contexte
  let system = $state(src.system || "");
  let knowledge = $state(src.knowledge || "");
  let examples = $state((src.examples && src.examples.length ? src.examples : kind === "context" ? [{ input: "", output: "" }] : []).map((e) => ({ ...e })));
  // Prompt
  let template = $state(src.template || "");
  // Dataset
  let jsonl = $state(src.jsonl || "");
  let bigFile = $state(null);
  // LoRA
  let lora = $state({
    baseModel: src.baseModel || "Qwen/Qwen2.5-7B-Instruct", r: src.r ?? 16, alpha: src.alpha ?? 32, dropout: src.dropout ?? 0.05,
    lr: src.lr ?? 0.0002, epochs: src.epochs ?? 3, batch: src.batch ?? 4, gradAcc: src.gradAcc ?? 4, seqLen: src.seqLen ?? 2048,
    targets: (src.targets || ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]).join(", "),
    datasetId: src.datasetId || "", notes: src.notes || "",
  });

  // Commun : version, historique, « Testé sur », accès (serveurs MCP et harness)
  let meta = $state({ version: src.version || "", changelog: src.changelog || "",
    tests: (src.tests || []).map((x) => ({ ...x, score: x.score ?? "" })),
    access: { read: false, write: false, network: false, exec: false, ...(src.access || {}) } });
  // Agent
  let agent = $state({ instructions: src.instructions || "", steps: (src.steps || [""]).join("\n"), framework: src.framework || "claude-agent-sdk",
    mcpIds: [...(src.mcpIds || [])], contextIds: [...(src.contextIds || [])], guardrails: src.guardrails || "" });
  // Skill
  let skill = $state({ skillName: src.skillName || "", whenToUse: src.whenToUse || "", instructions: src.instructions || "", resources: src.resources || "" });
  // Évaluation
  let ev = $state({ cases: (src.cases && src.cases.length ? src.cases : [{ input: "", expected: "" }]).map((c) => ({ ...c })),
    metric: src.metric || "contains", criteria: src.criteria || "", threshold: src.threshold ?? 80, evaluatesId: src.evaluatesId || "" });
  // RAG
  let rag = $state({ sources: src.sources || "", chunkSize: src.chunkSize ?? 800, chunkOverlap: src.chunkOverlap ?? 100, embedding: src.embedding || "",
    vectorStore: src.vectorStore || "pgvector", topK: src.topK ?? 5, reranker: src.reranker || "",
    promptTemplate: src.promptTemplate || "Réponds à partir des extraits ci-dessous.\n\nExtraits :\n{{context}}\n\nQuestion : {{question}}" });
  // Harness
  let hn = $state({ harness: src.harness || "claude-code", instructions: src.instructions || "", allow: (src.allow || []).join("\n"),
    deny: (src.deny || []).join("\n"), hooks: src.hooks || "", mcpIds: [...(src.mcpIds || [])] });
  const pick = (arr, v) => (arr.includes(v) ? arr.splice(arr.indexOf(v), 1) : arr.push(v));
  // Modèle cible (contextes, prompts, outils) : "" = général
  let target = $state({ family: src.targetFamily || "", model: src.targetModel || "", modelId: src.targetModelId || "" });
  // Modèle (Labs)
  let model = $state({
    baseModel: src.baseModel || "", family: src.family || "qwen", params: src.params || "", format: src.format || "safetensors",
    quant: src.quant || "", contextLength: src.contextLength || "", weightsUrl: src.weightsUrl || "", notes: src.notes || "",
    datasetIds: [...(src.datasetIds || [])], loraId: src.loraId || "", epochs: src.epochs ?? "", trainedAt: src.trainedAt || "",
    vramGb: src.vramGb ?? "", cpuOk: !!src.cpuOk, speed: src.speed || "",
    languages: [...(src.languages || [])], chatTemplate: src.chatTemplate || "", useCases: src.useCases || "", limits: src.limits || "",
    benchmarks: (src.benchmarks || []).map((b) => ({ ...b })), version: src.version || "", releasedAt: src.releasedAt || "", changelog: src.changelog || "",
  });
  const toggle = (arr, v) => (arr.includes(v) ? arr.splice(arr.indexOf(v), 1) : arr.push(v));
  // Outil
  let tool = $state({
    toolName: src.toolName || "", toolDescription: src.toolDescription || "",
    schema: src.schema ? JSON.stringify(src.schema, null, 2) : '{\n  "type": "object",\n  "properties": {\n    "ville": { "type": "string", "description": "Nom de la ville" }\n  },\n  "required": ["ville"]\n}',
    transport: src.transport || "stdio", command: src.command || "", url: src.url || "",
    env: (src.env || []).join(", "), notes: src.notes || "",
  });

  // Suggestions : tags déjà utilisés, filtrés sur le mot en cours de saisie
  const current = $derived(tags.split(",").map((x) => slugify(x)).filter(Boolean));
  const typing = $derived(slugify(tags.split(",").pop() || ""));
  const suggestions = $derived(knownTags.map(([g]) => g).filter((g) => !current.includes(g) && (!typing || g.includes(typing))).slice(0, 12));
  function addTag(g) {
    const parts = tags.split(",").map((x) => x.trim());
    if (typing && !knownTags.some(([k]) => k === typing)) parts.pop(); else if (typing) parts.pop();
    tags = [...parts.filter(Boolean), g].join(", ") + ", ";
  }

  let error = $state("");
  let busy = $state(false);

  const tplVars = $derived(varsOf(template));
  const jstat = $derived.by(() => {
    if (bigFile) return { ok: true, text: t("big_file", { mb: cfg.maxDatasetMb }) };
    if (!jsonl.trim()) return null;
    const { rows, errors } = parseJSONL(jsonl);
    if (errors.length) return { ok: false, text: t("bad_lines", { l: errors.slice(0, 5).join(", ") + (errors.length > 5 ? "…" : "") }) };
    const f = rows.length ? detectFormat(rows[0]) : null;
    return { ok: true, fmt: f, text: `${t("valid_rows", { n: rows.length })}, ${f ? t("fmt_found", { f: t(SUB.dataset.opts[f]) }) : t("fmt_unknown")} · ${Math.round(jsonl.length / 1024)} KB` };
  });
  $effect(() => { if (kind === "dataset" && jstat?.fmt) sub = jstat.fmt; });

  function onFile(e) {
    const f = e.currentTarget.files[0];
    if (!f) return;
    const inlineMax = (cfg.maxResourceKb || 256) * 1024 * 0.9;
    if (f.size > inlineMax) {
      if (!cfg.objectStorage) { error = t("no_storage"); e.currentTarget.value = ""; return; }
      if (f.size > (cfg.maxDatasetMb || 50) * 1024 * 1024) { error = t("too_big"); e.currentTarget.value = ""; return; }
      bigFile = f; jsonl = ""; error = "";
    } else {
      bigFile = null;
      f.text().then((x) => (jsonl = x));
    }
  }

  const apiError = (code) => ({
    auth_required: t("login_required"), forbidden: t("e_rights"), too_large: t("e_ds_big"), invalid_source_url: t("e_src"),
    empty_context: t("e_ctx"), empty_template: t("e_tpl"), missing_base_model: t("e_base"), invalid_name: t("e_name"), empty_instructions: t("e_instr"), invalid_skill_name: t("e_skillname"), empty_cases: t("e_cases"), empty_rag: t("e_rag"), invalid_weights_url: t("e_weights"), lab_only: t("e_lab_only"), exists: t("e_exists"), rate_limited: t("e_pub_rate"), invalid_tool_name: t("e_toolname"), invalid_schema: t("e_schema"), missing_command: t("e_cmd"), invalid_mcp_url: t("e_mcpurl"),
  })[code] || (String(code).startsWith("invalid_json_line") ? t("e_ds_bad") : String(code).startsWith("unknown_format") ? t("e_ds_fmt") : t("e_save", { m: code }));

  async function save() {
    error = "";
    const slug = slugify(name);
    if (!slug) return (error = t("e_name"));
    if (!accept) return (error = t("e_accept"));
    let data = {};
    if (kind === "context") {
      data = { system: system.trim(), knowledge: knowledge.trim(), examples: examples.map((e) => ({ input: e.input.trim(), output: e.output.trim() })).filter((e) => e.input || e.output) };
      if (!data.system && !data.knowledge && !data.examples.length) return (error = t("e_ctx"));
    } else if (kind === "prompt") {
      if (!template.trim()) return (error = t("e_tpl"));
      data = { template: template.trim() };
    } else if (kind === "dataset") {
      if (!bigFile) {
        if (!jsonl.trim() && mode !== "edit") return (error = t("e_ds_empty"));
        if (jstat && !jstat.ok) return (error = t("e_ds_bad"));
      }
      data = { jsonl: bigFile ? "" : jsonl.trim() };
    } else if (kind === "model") {
      if (!/^https?:\/\/\S+$/.test(model.weightsUrl.trim())) return (error = t("e_weights"));
      data = { ...model, weightsUrl: model.weightsUrl.trim(), contextLength: Number(model.contextLength) || 0,
               epochs: model.epochs === "" ? null : Number(model.epochs), vramGb: model.vramGb === "" ? null : Number(model.vramGb),
               benchmarks: model.benchmarks.filter((b) => b.name.trim()) };
    } else if (kind === "agent") {
      if (!agent.instructions.trim()) return (error = t("e_instr"));
      data = { ...agent, steps: agent.steps.split("\n").map((x) => x.trim()).filter(Boolean) };
    } else if (kind === "skill") {
      if (!/^[a-z0-9-]{1,64}$/.test(skill.skillName.trim())) return (error = t("e_skillname"));
      if (!skill.instructions.trim()) return (error = t("e_instr"));
      data = { ...skill, skillName: skill.skillName.trim() };
    } else if (kind === "eval") {
      const cases = ev.cases.filter((c) => c.input.trim());
      if (!cases.length) return (error = t("e_cases"));
      data = { ...ev, cases, threshold: Number(ev.threshold) || 80 };
    } else if (kind === "rag") {
      if (!rag.embedding.trim() || !rag.promptTemplate.trim()) return (error = t("e_rag"));
      data = { ...rag };
    } else if (kind === "harness") {
      if (!hn.instructions.trim()) return (error = t("e_instr"));
      const lines = (x) => x.split("\n").map((l) => l.trim()).filter(Boolean);
      data = { ...hn, allow: lines(hn.allow), deny: lines(hn.deny) };
    } else if (kind === "tool") {
      if (!/^[a-zA-Z0-9_-]{1,64}$/.test(tool.toolName.trim())) return (error = t("e_toolname"));
      if (tool.transport === "stdio" && !tool.command.trim()) return (error = t("e_cmd"));
      if (tool.transport === "http" && !/^https?:\/\/\S+$/.test(tool.url.trim())) return (error = t("e_mcpurl"));
      data = { toolName: tool.toolName.trim(), transport: tool.transport, command: tool.command.trim(), url: tool.url.trim(),
               env: tool.env.split(",").map((x) => x.trim()).filter(Boolean), notes: tool.notes.trim() };
    } else {
      data = { ...lora, targets: lora.targets.split(",").map((x) => x.trim()).filter(Boolean), datasetId: lora.datasetId || null };
      if (!data.baseModel.trim()) return (error = t("e_base"));
    }
    if (kind !== "model") data = { ...data, version: meta.version.trim(), changelog: meta.changelog.trim(),
      tests: meta.tests.filter((x) => x.model.trim()).map((x) => ({ ...x, model: x.model.trim(), score: x.score === "" || x.score == null ? null : Number(x.score) })) };
    if (kind === "tool" || kind === "harness") data = { ...data, access: { ...meta.access } };
    if (TARGET_KINDS.includes(kind)) data = { ...data, targetFamily: target.family, targetModel: target.family ? target.model.trim() : "", targetModelId: target.family ? target.modelId : "" };
    const id = mode === "edit" ? src.id : `${slugify(handle || "anon")}--${slug}`;
    const body = {
      kind, name: slug, authorHandle: slugify(handle), description: description.trim(),
      tags: tags.split(",").map(slugify).filter(Boolean).slice(0, 10), clang, license, sourceUrl: sourceUrl.trim(), sub: kind === "tool" ? "mcp" : sf ? sub : "", data,
    };
    busy = true;
    try {
      let r = await fetch(`/api/resources/${encodeURIComponent(id)}${mode === "edit" ? "" : "?create=1"}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      if (r.ok && bigFile) {
        error = t("uploading");
        const fd = new FormData(); fd.append("file", bigFile);
        r = await fetch(`/api/resources/${encodeURIComponent(id)}/dataset`, { method: "POST", body: fd });
      }
      if (!r.ok) {
        let code = String(r.status);
        try { const d = await r.json(); code = typeof d.detail === "string" ? d.detail : code; } catch {}
        error = r.status === 401 ? t("login_required") : apiError(code);
        busy = false; return;
      }
      location.href = resourcePath(lang, kind, id);
    } catch (e) {
      error = t("e_save", { m: "network" }); busy = false;
    }
  }
</script>

<div class="form">
  <h1 class="h2">{t(mode === "edit" ? "t_edit" : mode === "fork" ? "t_fork" : "t_new", { k: t("o_" + kind) })}</h1>

  <div class="two">
    <div class="field"><label for="f-name">{t("fm_name")}</label><input id="f-name" bind:value={name} maxlength="60" /></div>
    {#if isAdmin}    <div class="field"><label for="f-handle">{t("fm_author")} <span class="hint">{t("fm_author_h")}</span></label><input id="f-handle" bind:value={handle} maxlength="30" placeholder={t("fm_ph_author")} /></div>{:else}<div class="field"><span class="lbl-strong">{t("fm_author")}</span><p class="note u-m6t">{handle}</p></div>{/if}
  </div>
  <div class="two">
    {#if sf}
      <div class="field"><label for="f-sub">{t(sf.label)}</label>
        <select id="f-sub" bind:value={sub}>{#each Object.entries(sf.opts) as [v, l]}<option value={v}>{t(l)}</option>{/each}</select></div>
    {/if}
    <div class="field"><label for="f-clang">{t("f_clang")}</label>
      <select id="f-clang" bind:value={clang}>{#each CLANGS as c}<option value={c}>{clangNames[c] || c}</option>{/each}</select></div>
    <div class="field"><label for="f-tags">{t("f_tags")} <span class="hint">{t("fm_tags_h")}</span></label><input id="f-tags" bind:value={tags} autocomplete="off" />
      {#if suggestions.length}<div class="tags u-m6t">{#each suggestions as g}<button type="button" class="tag" onclick={() => addTag(g)}>#{g}</button>{/each}</div>{/if}</div>
    <div class="field"><label for="f-lic">{t("license", { l: "" }).replace(/[:：]\s*$/, "")} <span class="hint">{t("fm_lic_h")}</span></label>
      <select id="f-lic" bind:value={license}>{#each Object.keys(LICENSES) as v}<option value={v}>{licLabel(v)}</option>{/each}</select></div>
    <div class="field"><label for="f-src">{t("source")} <span class="hint">{t("fm_src_h")}</span></label>
      <input id="f-src" type="url" inputmode="url" maxlength="500" placeholder="https://" bind:value={sourceUrl} /></div>
  </div>
  <div class="field"><label for="f-desc">{t("fm_desc")}</label><input id="f-desc" bind:value={description} maxlength="240" placeholder={t("fm_desc_ph")} /></div>

  {#if kind === "context"}
    <div class="field"><label for="f-sys">{t("h_system")}</label><textarea id="f-sys" bind:value={system} placeholder={t("fm_sys_ph")}></textarea></div>
    <div class="field"><span class="lbl-strong">{t("h_examples")} <span class="hint">{t("fm_ex_h")}</span></span>
      {#each examples as e, i}
        <div class="exedit">
          <button class="btn sm rm" type="button" onclick={() => examples.splice(i, 1)}>{t("remove")}</button>
          <div class="note u-mb6">{t("example_n", { n: i + 1 })}</div>
          <div class="two">
            <textarea bind:value={e.input} placeholder={t("lbl_in")} aria-label={t("lbl_in")}></textarea>
            <textarea bind:value={e.output} placeholder={t("lbl_out")} aria-label={t("lbl_out")}></textarea>
          </div>
        </div>
      {/each}
      <button class="btn sm" type="button" onclick={() => examples.push({ input: "", output: "" })}>{t("add_ex")}</button>
    </div>
    <div class="field"><label for="f-kn">{t("h_knowledge")} <span class="hint">{t("fm_kn_h")}</span></label><textarea class="u-h120" id="f-kn" bind:value={knowledge}></textarea></div>
  {:else if kind === "prompt"}
    <div class="field"><label for="f-tpl">{t("h_template")} <span class="hint">{t("fm_tpl_h")}</span></label>
      <textarea class="u-h200" id="f-tpl" bind:value={template}></textarea>
      <p class="note">{tplVars.length ? t("vars_found", { v: tplVars.join(", ") }) : t("no_vars_found")}</p></div>
  {:else if kind === "dataset"}
    <div class="field"><label for="f-jsonl">{t("fm_jsonl")} <span class="hint">{t("fm_jsonl_h")}</span></label>
      <textarea class="u-h220" id="f-jsonl" bind:value={jsonl} disabled={!!bigFile}
        placeholder={'{"messages":[{"role":"user","content":"…"},{"role":"assistant","content":"…"}]}'}></textarea>
      <div class="u-row10 u-center u-wrap u-mt6">
        <label class="btn sm">{t("import")}<input type="file" accept=".jsonl,.json,.txt" hidden onchange={onFile} /></label>
        {#if jstat}<span class="note {jstat.ok ? 'ok' : 'ko'}">{jstat.text}</span>{/if}
      </div></div>
  {:else if kind === "model"}
    <div class="two">
      <div class="field"><label for="m-base">{t("fm_mbase")} <span class="hint">{t("fm_mbase_h")}</span></label><input class="u-mono" id="m-base" bind:value={model.baseModel} /></div>
      <div class="field"><label for="m-fam">{t("s_family")}</label>
        <select id="m-fam" bind:value={model.family}>{#each Object.entries(MODEL_FAMILIES) as [v, l]}<option value={v}>{l.startsWith("fam_") ? t(l) : l}</option>{/each}</select></div>
    </div>
    <div class="three">
      <div class="field"><label for="m-par">{t("s_mparams")} <span class="hint">7B, 70B…</span></label><input id="m-par" bind:value={model.params} maxlength="20" /></div>
      <div class="field"><label for="m-fmt">{t("s_mformat")}</label>
        <select id="m-fmt" bind:value={model.format}>{#each MODEL_FORMATS as v}<option value={v}>{v.toUpperCase()}</option>{/each}</select></div>
      <div class="field"><label for="m-q">{t("fm_mquant")} <span class="hint">Q4_K_M, 4-bit…</span></label><input id="m-q" bind:value={model.quant} maxlength="40" /></div>
      <div class="field"><label for="m-ctx">{t("s_ctx")} <span class="hint">tokens</span></label><input id="m-ctx" type="number" min="0" bind:value={model.contextLength} /></div>
    </div>
    <div class="field"><label for="m-w">{t("fm_mweights")} <span class="hint">{t("fm_mweights_h")}</span></label><input id="m-w" type="url" placeholder="https://" bind:value={model.weightsUrl} /></div>

    <fieldset class="mgroup"><legend>{t("mg_train")}</legend>
      <div class="field"><span class="lbl-strong">{t("mg_datasets")} <span class="hint">{t("optional")}</span></span>
        <div class="tags u-m6t">{#each datasets as d}<button type="button" class="tag" aria-pressed={model.datasetIds.includes(d.id)} onclick={() => toggle(model.datasetIds, d.id)}>{model.datasetIds.includes(d.id) ? "✓ " : ""}{(d.authorHandle || "community") + "/" + d.name}</button>{/each}</div></div>
      <div class="three">
        <div class="field"><label for="m-lora">{t("mg_lora")}</label>
          <select id="m-lora" bind:value={model.loraId}><option value="">{t("none")}</option>{#each loras as l}<option value={l.id}>{(l.authorHandle || "community") + "/" + l.name}</option>{/each}</select></div>
        <div class="field"><label for="m-ep">{t("hp_epochs")}</label><input id="m-ep" type="number" min="0" bind:value={model.epochs} /></div>
        <div class="field"><label for="m-td">{t("mg_trained")}</label><input id="m-td" type="date" bind:value={model.trainedAt} /></div>
      </div>
    </fieldset>

    <fieldset class="mgroup"><legend>{t("mg_hw")}</legend>
      <div class="three">
        <div class="field"><label for="m-vram">{t("mg_vram")} <span class="hint">Go</span></label><input id="m-vram" type="number" min="0" step="0.5" bind:value={model.vramGb} /></div>
        <div class="field"><label for="m-speed">{t("mg_speed")} <span class="hint">{t("mg_speed_h")}</span></label><input id="m-speed" bind:value={model.speed} maxlength="80" /></div>
        <label class="field accept u-self-end"><input type="checkbox" bind:checked={model.cpuOk} /> {t("mg_cpu")}</label>
      </div>
    </fieldset>

    <fieldset class="mgroup"><legend>{t("mg_usage")}</legend>
      <div class="field"><span class="lbl-strong">{t("mg_langs")}</span>
        <div class="tags u-m6t">{#each CLANGS.filter((c) => c !== "multi") as c}<button type="button" class="tag" aria-pressed={model.languages.includes(c)} onclick={() => toggle(model.languages, c)}>{model.languages.includes(c) ? "✓ " : ""}{clangNames[c] || c}</button>{/each}</div></div>
      <div class="field"><label for="m-tpl">{t("mg_template")}</label>
        <select id="m-tpl" bind:value={model.chatTemplate}><option value="">—</option>{#each ["chatml", "llama3", "mistral", "gemma", "phi", "alpaca", "other"] as v}<option value={v}>{v === "other" ? t("fam_other") : v === "chatml" ? "ChatML" : v === "llama3" ? "Llama 3" : v.charAt(0).toUpperCase() + v.slice(1)}</option>{/each}</select></div>
      <div class="two">
        <div class="field"><label for="m-use">{t("mg_uses")}</label><textarea id="m-use" bind:value={model.useCases} maxlength="2000"></textarea></div>
        <div class="field"><label for="m-lim">{t("mg_limits")}</label><textarea id="m-lim" bind:value={model.limits} maxlength="2000"></textarea></div>
      </div>
    </fieldset>

    <fieldset class="mgroup"><legend>{t("mg_eval")}</legend>
      <div class="two">
        <div class="field"><label for="m-ver">{t("mg_version")}</label><input id="m-ver" bind:value={model.version} maxlength="30" placeholder="1.0" /></div>
        <div class="field"><label for="m-rel">{t("mg_released")}</label><input id="m-rel" type="date" bind:value={model.releasedAt} /></div>
      </div>
      <div class="field"><span class="lbl-strong">{t("mg_bench")}</span>
        {#each model.benchmarks as b, i}
          <div class="two u-mt6"><input bind:value={b.name} placeholder="MMLU, GSM8K…" aria-label={t("mg_bench")} />
            <div class="u-row6"><input bind:value={b.score} placeholder="72.4" aria-label="Score" /><button type="button" class="btn sm" onclick={() => model.benchmarks.splice(i, 1)}>{t("remove")}</button></div></div>
        {/each}
        <button type="button" class="btn sm u-mt6" onclick={() => model.benchmarks.push({ name: "", score: "" })}>+ {t("mg_bench_add")}</button></div>
      <div class="field"><label for="m-cl">{t("mg_changelog")}</label><textarea id="m-cl" bind:value={model.changelog} maxlength="4000"></textarea></div>
    </fieldset>

    <div class="field"><label for="m-notes">{t("h_notes")} <span class="hint">{t("fm_mnotes_h")}</span></label><textarea class="u-h140" id="m-notes" bind:value={model.notes}></textarea></div>
  {:else if kind === "agent"}
    <div class="field"><label for="a-ins">{t("ag_instr")} <span class="hint">{t("ag_instr_h")}</span></label><textarea class="u-h140" id="a-ins" bind:value={agent.instructions}></textarea></div>
    <div class="field"><label for="a-steps">{t("ag_steps")} <span class="hint">{t("ag_steps_h")}</span></label><textarea id="a-steps" bind:value={agent.steps}></textarea></div>
    <div class="field"><label for="a-fw">{t("ag_fw")}</label>
      <select id="a-fw" bind:value={agent.framework}>{#each Object.entries(AGENT_FRAMEWORKS) as [v, l]}<option value={v}>{l.startsWith("fam_") ? t(l) : l}</option>{/each}</select></div>
    {#if mcps.length}<div class="field"><span class="lbl-strong">{t("ag_mcp")} <span class="hint">{t("optional")}</span></span>
      <div class="tags u-m6t">{#each mcps as m}<button type="button" class="tag" aria-pressed={agent.mcpIds.includes(m.id)} onclick={() => pick(agent.mcpIds, m.id)}>{agent.mcpIds.includes(m.id) ? "✓ " : ""}{(m.authorHandle || "community") + "/" + m.name}</button>{/each}</div></div>{/if}
    {#if contexts.length}<div class="field"><span class="lbl-strong">{t("ag_ctx")} <span class="hint">{t("optional")}</span></span>
      <div class="tags u-m6t">{#each contexts as c}<button type="button" class="tag" aria-pressed={agent.contextIds.includes(c.id)} onclick={() => pick(agent.contextIds, c.id)}>{agent.contextIds.includes(c.id) ? "✓ " : ""}{(c.authorHandle || "community") + "/" + c.name}</button>{/each}</div></div>{/if}
    <div class="field"><label for="a-g">{t("ag_guard")} <span class="hint">{t("ag_guard_h")}</span></label><textarea id="a-g" bind:value={agent.guardrails}></textarea></div>
  {:else if kind === "skill"}
    <div class="field"><label for="s-n">{t("sk_name")} <span class="hint">{t("sk_name_h")}</span></label><input class="u-mono" id="s-n" bind:value={skill.skillName} maxlength="64" /></div>
    <div class="field"><label for="s-w">{t("sk_when")} <span class="hint">{t("sk_when_h")}</span></label><textarea id="s-w" bind:value={skill.whenToUse} maxlength="1024"></textarea></div>
    <div class="field"><label for="s-i">{t("sk_instr")} <span class="hint">Markdown</span></label><textarea class="u-h220 u-mono" id="s-i" bind:value={skill.instructions}></textarea></div>
    <div class="field"><label for="s-r">{t("sk_res")} <span class="hint">{t("optional")}</span></label><textarea id="s-r" bind:value={skill.resources}></textarea></div>
  {:else if kind === "eval"}
    {#if evaluables.length}<div class="field"><label for="e-t">{t("ev_target")} <span class="hint">{t("optional")}</span></label>
      <select id="e-t" bind:value={ev.evaluatesId}><option value="">{t("none")}</option>{#each evaluables as x}<option value={x.id}>{t("o_" + x.kind)} · {(x.authorHandle || "community") + "/" + x.name}</option>{/each}</select></div>{/if}
    <div class="two">
      <div class="field"><label for="e-m">{t("ev_metric")}</label>
        <select id="e-m" bind:value={ev.metric}>{#each EVAL_METRICS as m}<option value={m}>{t("evm_" + m.replace("-", "_"))}</option>{/each}</select></div>
      <div class="field"><label for="e-th">{t("ev_thr")} <span class="hint">%</span></label><input id="e-th" type="number" min="0" max="100" bind:value={ev.threshold} /></div>
    </div>
    <div class="field"><label for="e-c">{t("ev_crit")} <span class="hint">{t("optional")}</span></label><textarea id="e-c" bind:value={ev.criteria}></textarea></div>
    <div class="field"><span class="lbl-strong">{t("ev_cases")}</span>
      {#each ev.cases as c, i}
        <div class="exedit"><button class="btn sm rm" type="button" onclick={() => ev.cases.splice(i, 1)}>{t("remove")}</button>
          <div class="two"><textarea bind:value={c.input} placeholder={t("lbl_in")} aria-label={t("lbl_in")}></textarea><textarea bind:value={c.expected} placeholder={t("ev_expected")} aria-label={t("ev_expected")}></textarea></div></div>
      {/each}
      <button class="btn sm" type="button" onclick={() => ev.cases.push({ input: "", expected: "" })}>+ {t("ev_add")}</button></div>
  {:else if kind === "rag"}
    <div class="field"><label for="r-src">{t("rg_sources")} <span class="hint">{t("rg_sources_h")}</span></label><textarea id="r-src" bind:value={rag.sources}></textarea></div>
    <div class="three">
      <div class="field"><label for="r-cs">{t("rg_chunk")} <span class="hint">{t("chars")}</span></label><input id="r-cs" type="number" min="50" bind:value={rag.chunkSize} /></div>
      <div class="field"><label for="r-co">{t("rg_overlap")}</label><input id="r-co" type="number" min="0" bind:value={rag.chunkOverlap} /></div>
      <div class="field"><label for="r-k">{t("rg_topk")}</label><input id="r-k" type="number" min="1" max="100" bind:value={rag.topK} /></div>
    </div>
    <div class="three">
      <div class="field"><label for="r-e">{t("rg_emb")}</label><input id="r-e" bind:value={rag.embedding} placeholder="multilingual-e5-large" /></div>
      <div class="field"><label for="r-vs">{t("rg_store")}</label>
        <select id="r-vs" bind:value={rag.vectorStore}>{#each Object.entries(VECTOR_STORES) as [v, l]}<option value={v}>{l.startsWith("fam_") ? t(l) : l}</option>{/each}</select></div>
      <div class="field"><label for="r-rr">{t("rg_rerank")} <span class="hint">{t("optional")}</span></label><input id="r-rr" bind:value={rag.reranker} /></div>
    </div>
    <div class="field"><label for="r-p">{t("rg_prompt")} <span class="hint">{"{{context}} {{question}}"}</span></label><textarea class="u-h160" id="r-p" bind:value={rag.promptTemplate}></textarea></div>
  {:else if kind === "harness"}
    <div class="field"><label for="h-h">Harness</label>
      <select id="h-h" bind:value={hn.harness}>{#each Object.entries(HARNESSES) as [v, l]}<option value={v}>{l.startsWith("fam_") ? t(l) : l}</option>{/each}</select></div>
    <div class="field"><label for="h-i">{t("hn_instr")} <span class="hint">CLAUDE.md, Markdown</span></label><textarea class="u-h180 u-mono" id="h-i" bind:value={hn.instructions}></textarea></div>
    <div class="two">
      <div class="field"><label for="h-a">{t("hn_allow")} <span class="hint">{t("ag_steps_h")}</span></label><textarea class="u-mono" id="h-a" bind:value={hn.allow} placeholder="Bash(npm test)"></textarea></div>
      <div class="field"><label for="h-d">{t("hn_deny")} <span class="hint">{t("ag_steps_h")}</span></label><textarea class="u-mono" id="h-d" bind:value={hn.deny} placeholder="Read(.env)"></textarea></div>
    </div>
    <div class="field"><label for="h-hk">Hooks <span class="hint">JSON, {t("optional")}</span></label><textarea class="u-mono" id="h-hk" bind:value={hn.hooks}></textarea></div>
    {#if mcps.length}<div class="field"><span class="lbl-strong">{t("ag_mcp")} <span class="hint">{t("optional")}</span></span>
      <div class="tags u-m6t">{#each mcps as m}<button type="button" class="tag" aria-pressed={hn.mcpIds.includes(m.id)} onclick={() => pick(hn.mcpIds, m.id)}>{hn.mcpIds.includes(m.id) ? "✓ " : ""}{(m.authorHandle || "community") + "/" + m.name}</button>{/each}</div></div>{/if}
  {:else if kind === "tool"}
    <div class="field"><label for="f-tname">{t("fm_toolname")} <span class="hint">{t("fm_toolname_h")}</span></label>
      <input class="u-mono" id="f-tname" bind:value={tool.toolName} maxlength="64" /></div>
      <div class="field"><label for="f-tr">{t("fm_transport")}</label>
        <select id="f-tr" bind:value={tool.transport}><option value="stdio">stdio</option><option value="http">HTTP</option></select></div>
      {#if tool.transport === "stdio"}
        <div class="field"><label for="f-cmd">{t("fm_command")} <span class="hint">{t("fm_command_h")}</span></label>
          <input class="u-mono" id="f-cmd" bind:value={tool.command} /></div>
      {:else}
        <div class="field"><label for="f-murl">{t("fm_mcpurl")}</label>
          <input id="f-murl" type="url" bind:value={tool.url} placeholder="https://" /></div>
      {/if}
      <div class="field"><label for="f-env">{t("fm_env")} <span class="hint">{t("fm_env_h")}</span></label>
        <input class="u-mono" id="f-env" bind:value={tool.env} /></div>
      <div class="field"><label for="f-tnotes">{t("h_notes")}</label><textarea id="f-tnotes" bind:value={tool.notes}></textarea></div>
  {:else}
    <div class="field"><label for="f-base">{t("hp_base")} <span class="hint">{t("fm_base_h")}</span></label><input id="f-base" bind:value={lora.baseModel} /></div>
    <div class="three">
      <div class="field"><label for="f-r">{t("s_rank")}</label><input id="f-r" type="number" min="1" bind:value={lora.r} /></div>
      <div class="field"><label for="f-alpha">Alpha</label><input id="f-alpha" type="number" min="1" bind:value={lora.alpha} /></div>
      <div class="field"><label for="f-drop">Dropout</label><input id="f-drop" type="number" step="0.01" min="0" max="1" bind:value={lora.dropout} /></div>
      <div class="field"><label for="f-lr">{t("hp_lr")}</label><input id="f-lr" type="number" step="0.00001" min="0" bind:value={lora.lr} /></div>
      <div class="field"><label for="f-ep">{t("hp_epochs")}</label><input id="f-ep" type="number" min="1" bind:value={lora.epochs} /></div>
      <div class="field"><label for="f-seq">{t("fm_seq")}</label><input id="f-seq" type="number" min="128" step="128" bind:value={lora.seqLen} /></div>
      <div class="field"><label for="f-bs">{t("fm_batch")}</label><input id="f-bs" type="number" min="1" bind:value={lora.batch} /></div>
      <div class="field"><label for="f-ga">{t("fm_ga")}</label><input id="f-ga" type="number" min="1" bind:value={lora.gradAcc} /></div>
    </div>
    <div class="field"><label for="f-tgt">{t("hp_targets")} <span class="hint">{t("fm_tgt_h")}</span></label><input class="u-mono" id="f-tgt" bind:value={lora.targets} /></div>
    <div class="field"><label for="f-ds">{t("fm_ds")} <span class="hint">{t("optional")}</span></label>
      <select id="f-ds" bind:value={lora.datasetId}><option value="">{t("none")}</option>{#each datasets as d}<option value={d.id}>{(d.authorHandle || "community") + "/" + d.name}</option>{/each}</select></div>
    <div class="field"><label for="f-notes">{t("h_notes")} <span class="hint">{t("fm_notes_h")}</span></label><textarea id="f-notes" bind:value={lora.notes}></textarea></div>
  {/if}

  {#if TARGET_KINDS.includes(kind)}
    <fieldset class="mgroup"><legend>{t("target")}</legend>
      <div class="three">
        <div class="field"><label for="t-fam">{t("target_scope")}</label>
          <select id="t-fam" bind:value={target.family}><option value="">{t("target_general")}</option>{#each Object.entries(TARGET_FAMILIES) as [v, l]}<option value={v}>{l.startsWith("fam_") ? t(l) : l}</option>{/each}</select></div>
        {#if target.family}
          <div class="field"><label for="t-mod">{t("target_precise")} <span class="hint">{t("optional")}</span></label><input id="t-mod" bind:value={target.model} maxlength="80" placeholder="qwen-3.8, claude-sonnet-5…" /></div>
          {#if models.length}<div class="field"><label for="t-mid">{t("target_catalog")} <span class="hint">{t("optional")}</span></label>
            <select id="t-mid" bind:value={target.modelId} onchange={() => { const m = models.find((x) => x.id === target.modelId); if (m && !target.model) target.model = m.name; }}><option value="">{t("none")}</option>{#each models as m}<option value={m.id}>{(m.authorHandle || "community") + "/" + m.name}</option>{/each}</select></div>{/if}
        {/if}
      </div>
    </fieldset>
  {/if}

  {#if kind === "tool" || kind === "harness"}
    <fieldset class="mgroup"><legend>{t("ac_title")}</legend>
      <p class="note u-m6b">{t("ac_h")}</p>
      {#each ["read", "write", "network", "exec"] as a}<label class="accept u-m4y"><input type="checkbox" bind:checked={meta.access[a]} /><span>{t("ac_" + a)}</span></label>{/each}
    </fieldset>
  {/if}
  {#if kind !== "model"}
    <fieldset class="mgroup"><legend>{t("ts_title")}</legend>
      <p class="note u-m6b">{t("ts_h")}</p>
      {#each meta.tests as x, i}
        <div class="exedit"><button class="btn sm rm" type="button" onclick={() => meta.tests.splice(i, 1)}>{t("remove")}</button>
          <div class="three">
            <div class="field"><label for={"ts-m" + i}>{t("ts_model")}</label><input id={"ts-m" + i} bind:value={x.model} maxlength="80" placeholder="claude-sonnet-5, qwen-3.8…" /></div>
            <div class="field"><label for={"ts-r" + i}>{t("ts_result")}</label><select id={"ts-r" + i} bind:value={x.result}>{#each ["pass", "partial", "fail"] as r}<option value={r}>{t("tr_" + r)}</option>{/each}</select></div>
            <div class="field"><label for={"ts-s" + i}>{t("ts_score")} <span class="hint">% · {t("optional")}</span></label><input id={"ts-s" + i} type="number" min="0" max="100" bind:value={x.score} /></div>
          </div>
          <div class="two">
            <div class="field"><label for={"ts-d" + i}>{t("ts_date")}</label><input id={"ts-d" + i} type="date" bind:value={x.date} /></div>
            <div class="field"><label for={"ts-n" + i}>{t("ts_note")} <span class="hint">{t("optional")}</span></label><input id={"ts-n" + i} bind:value={x.note} maxlength="300" /></div>
          </div></div>
      {/each}
      <button class="btn sm" type="button" onclick={() => meta.tests.push({ model: "", result: "pass", score: "", date: new Date().toISOString().slice(0, 10), note: "" })}>+ {t("ts_add")}</button>
    </fieldset>
    <fieldset class="mgroup"><legend>{t("mg_changelog")}</legend>
      <div class="field"><label for="v-v">{t("mg_version")}</label><input id="v-v" bind:value={meta.version} maxlength="30" placeholder="1.0" /></div>
      <div class="field"><label for="v-c">{t("vs_changes")} <span class="hint">{t("optional")}</span></label><textarea id="v-c" bind:value={meta.changelog} maxlength="4000" placeholder={"1.1 — …\n1.0 — …"}></textarea></div>
    </fieldset>
  {/if}

  <label class="accept"><input type="checkbox" bind:checked={accept} />
    <span>{@html t("accept", { cgu: `<a href="${pre(lang)}/legal/cgu" target="_blank">${t("accept_link")}</a>` })}</span></label>
  {#if error}<div class="err" role="alert">{error}</div>{/if}
  <div class="u-row8">
    <button class="btn primary" disabled={busy} onclick={save}>{t(mode === "edit" ? "save" : "publish")}</button>
    <a class="btn" href={mode === "edit" ? resourcePath(lang, kind, src.id) : kindPath(lang, kind)}>{t("cancel")}</a>
  </div>
</div>

