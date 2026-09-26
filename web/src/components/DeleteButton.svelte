<script>
  let { id, label = "Delete", confirmText = "Delete?", redirect = "/" } = $props();
  let busy = $state(false);

  async function del() {
    if (!confirm(confirmText)) return;
    busy = true;
    const r = await fetch(`/api/resources/${encodeURIComponent(id)}`, { method: "DELETE" });
    busy = false;
    if (r.ok) location.href = redirect;
  }
</script>

<button class="btn sm" disabled={busy} onclick={del}>{label}</button>
