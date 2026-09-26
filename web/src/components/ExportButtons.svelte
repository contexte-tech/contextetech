<script>
  let { id, filename, text = "", downloadHref = "", copyLabel = "Copy", downloadLabel = "Download", copiedLabel = "Copied" } = $props();
  let copied = $state(false);

  const bump = () => fetch(`/api/resources/${encodeURIComponent(id)}/use`, { method: "POST" }).catch(() => {});

  async function copy() {
    try { await navigator.clipboard.writeText(text); copied = true; setTimeout(() => (copied = false), 1800); bump(); } catch {}
  }
  function download() {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type: "text/plain;charset=utf-8" }));
    a.download = filename;
    document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
    bump();
  }
</script>

{#if text}
  <button class="btn sm" onclick={copy}>{copied ? copiedLabel : copyLabel}</button>
{/if}
{#if downloadHref}
  <a class="btn sm" href={downloadHref} download={filename}>{downloadLabel}</a>
{:else}
  <button class="btn sm" onclick={download}>{downloadLabel}</button>
{/if}
