<script>
  import { buildTurns, datasetPairs, fillTpl, varsOf } from "../lib/format.js";

  let { it, s, enabled = false, loggedIn = false, loginHref = "/" } = $props();
  const t = (k, v) => { let x = s[k] ?? k; if (v) for (const [a, b] of Object.entries(v)) x = x.split("{" + a + "}").join(String(b)); return x; };

  const kind = it.kind;
  const vars = kind === "prompt" ? varsOf(it.template) : [];
  const pairs = kind === "dataset" ? datasetPairs(it) : [];
  const shotOptions = [1, 3, 5, 10, 20].filter((x) => x <= Math.max(1, pairs.length));

  let input = $state("");
  let values = $state(Object.fromEntries(vars.map((v) => [v, ""])));
  let shots = $state(Math.min(5, Math.max(1, pairs.length)));
  let tier = $state("default");
  let compare = $state(false);
  let out1 = $state(""), out2 = $state("");
  let running = $state(false);
  let controller = null;

  function errorText(code) {
    return code === "auth" ? t("login_required") : code === "rate_limited" ? t("e_rate") : t("e_generic", { m: code });
  }

  async function stream(payload, set) {
    set(t("thinking"));
    let text = "";
    try {
      const r = await fetch("/api/sample", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: payload, tier }), signal: controller.signal,
      });
      if (!r.ok) { set(errorText(r.status === 401 ? "auth" : r.status === 429 ? "rate_limited" : String(r.status))); return; }
      const reader = r.body.getReader(), dec = new TextDecoder();
      let buf = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let i;
        while ((i = buf.indexOf("\n\n")) >= 0) {
          const line = buf.slice(0, i).trim(); buf = buf.slice(i + 2);
          if (!line.startsWith("data:")) continue;
          const ev = JSON.parse(line.slice(5));
          if (ev.delta) { text += ev.delta; set(text); }
          if (ev.error) { set((text ? text + "\n\n" : "") + errorText(ev.error)); return; }
          if (ev.done && ev.truncated) set(text + "\n\n" + t("truncated"));
        }
      }
    } catch (e) {
      set(e?.name === "AbortError" ? text + "\n" + t("stopped") : errorText("network"));
    }
  }

  async function run() {
    let main, raw;
    if (kind === "prompt") {
      if (vars.some((v) => !String(values[v]).trim())) { out1 = t("fill_vars"); return; }
      main = fillTpl(it.template, values);
    } else {
      raw = input.trim();
      if (!raw) { out1 = t("enter_input"); return; }
      main = kind === "context" ? buildTurns(it, raw) : buildTurns({}, raw, pairs.slice(0, shots));
    }
    controller = new AbortController();
    running = true; out2 = "";
    const jobs = [stream(main, (x) => (out1 = x))];
    if (compare && raw) jobs.push(stream(raw, (x) => (out2 = x)));
    await Promise.all(jobs);
    running = false;
  }
</script>

<div class="play">
  {#if kind === "context"}
    <label for="pin" class="note">{t("play_ctx")}</label>
    <textarea id="pin" bind:value={input} placeholder={t("input_ph")}></textarea>
  {:else if kind === "prompt"}
    <p class="note">{t("play_prompt")}</p>
    <div class="vars">
      {#each vars as v}
        <div><label for={"v-" + v}>{v}</label><input id={"v-" + v} bind:value={values[v]} /></div>
      {:else}
        <p class="note">{t("no_vars")}</p>
      {/each}
    </div>
  {:else}
    <p class="note">{t("play_ds")}</p>
    <label class="note">{t("shots")}
      <select bind:value={shots}>{#each shotOptions as n}<option value={n}>{n}</option>{/each}</select>
    </label>
    <textarea class="u-mt8" id="pin" bind:value={input} placeholder={t("ds_ph")}></textarea>
  {/if}

  <div class="row">
    {#if !enabled}
      <p class="note">{t("sample_off")}</p>
    {:else if !loggedIn}
      <span class="btn primary" role="link" tabindex="0" data-o={btoa("/a2/?next=").replace(/=+$/, "")}>{t("login")}</span>
      <span class="note">{t("login_required")}</span>
    {:else}
      <button class="btn primary" disabled={running} onclick={run}>{t("run")}</button>
      {#if running}<button class="btn" onclick={() => controller?.abort()}>{t("stop")}</button>{/if}
      <label class="note">{t("model")}
        <select bind:value={tier}>
          <option value="quick">{t("tier_quick")}</option>
          <option value="default">{t("tier_default")}</option>
          <option value="complex">{t("tier_complex")}</option>
        </select>
      </label>
      {#if kind !== "prompt"}
        <label class="note"><input type="checkbox" bind:checked={compare} /> {t(kind === "dataset" ? "cmp_ex" : "cmp_ctx")}</label>
      {/if}
    {/if}
  </div>

  <div class="block">
    <h2 class="h4">{t(kind === "prompt" ? "h_answer" : kind === "dataset" ? "h_with_ex" : "h_with_ctx")}</h2>
    <div class="out" class:idle={!out1}>{out1 || t("out_idle")}</div>
  </div>
  {#if compare && kind !== "prompt"}
    <div class="block">
      <h2 class="h4">{t(kind === "dataset" ? "h_wo_ex" : "h_wo_ctx")}</h2>
      <div class="out" class:idle={!out2}>{out2}</div>
    </div>
  {/if}
</div>
