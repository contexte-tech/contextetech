<script>
  let { id, likes = 0, liked = false, loggedIn = false, loginHref = "/" } = $props();
  let count = $state(likes);
  let on = $state(liked);
  let busy = $state(false);

  async function toggle() {
    if (!loggedIn) { location.href = loginHref; return; }
    busy = true;
    try {
      const r = await fetch(`/api/resources/${encodeURIComponent(id)}/like`, { method: "POST" });
      if (r.ok) { const d = await r.json(); count = d.likes; on = d.liked; }
    } finally { busy = false; }
  }
</script>

<button class="btn sm like" aria-pressed={on} disabled={busy} onclick={toggle}>♥ {count}</button>
