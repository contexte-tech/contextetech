// Scripts du site (servis en un seul fichier /_astro/*.js, mis en cache). Chaque bloc ne s'active que si son élément est présent.

// Bouton de thème clair / sombre (le thème choisi est appliqué avant l'affichage par /theme.js)
document.getElementById("theme-toggle")?.addEventListener("click", () => {
  const r = document.documentElement;
  const next = (r.dataset.theme || "light") === "dark" ? "light" : "dark";
  r.dataset.theme = next;
  try { localStorage.setItem("theme", next); } catch (e) {}
});

// Liens hors robots (data-o = adresse en base64) : clic, Ctrl/Cmd+clic ou clic molette, et Entrée au clavier
{
  const go = (el, e) => {
    let u = atob(el.getAttribute("data-o"));
    if (/next=$/.test(u)) u += encodeURIComponent(location.pathname + location.search);
    if (e.ctrlKey || e.metaKey || e.button === 1) open(u, "_blank"); else location.href = u;
  };
  document.addEventListener("click", (e) => { const el = e.target.closest("[data-o]"); if (el) { e.preventDefault(); go(el, e); } });
  document.addEventListener("auxclick", (e) => { const el = e.target.closest("[data-o]"); if (el && e.button === 1) go(el, e); });
  document.addEventListener("keydown", (e) => { const el = e.target.closest?.("[data-o]"); if (el && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); go(el, e); } });
}

// Langue du contenu : filtre sur la page même (pas d'adresse), en masquant les cartes des autres langues
document.addEventListener("click", (e) => {
  const b = e.target.closest("button[data-clang]"); if (!b) return;
  const on = b.getAttribute("aria-pressed") !== "true";
  document.querySelectorAll("button[data-clang]").forEach((x) => x.setAttribute("aria-pressed", x === b && on ? "true" : "false"));
  document.querySelectorAll(".list .card[data-clang]").forEach((c) => { c.hidden = on && c.getAttribute("data-clang") !== b.getAttribute("data-clang"); });
});

// Onglets des types sur mobile : onglet actif centré, fondu sur le bord qui cache encore des onglets
{
  const n = document.getElementById("kinds");
  if (n) {
    const a = n.querySelector('[aria-current="true"]');
    if (a) n.scrollLeft = a.offsetLeft - (n.clientWidth - a.offsetWidth) / 2;
    const edge = () => {
      n.classList.toggle("more-right", n.scrollLeft + n.clientWidth < n.scrollWidth - 2);
      n.classList.toggle("more-left", n.scrollLeft > 2);
    };
    edge(); n.addEventListener("scroll", edge, { passive: true }); addEventListener("resize", edge);
  }
}

// Carrousel de l'accueil : défilement, points de navigation, rotation automatique
{
  const box = document.getElementById("slides");
  if (box) {
    const dots = [...document.querySelectorAll(".slider .dot")], n = dots.length;
    let cur = 0, timer;
    const go = (i) => { cur = (i + n) % n; box.scrollTo({ left: box.clientWidth * cur, behavior: "smooth" }); };
    const mark = () => { cur = Math.round(box.scrollLeft / box.clientWidth); dots.forEach((d, i) => d.setAttribute("aria-current", i === cur ? "true" : "false")); };
    const stop = () => clearInterval(timer);
    const start = () => { stop(); if (!matchMedia("(prefers-reduced-motion: reduce)").matches) timer = setInterval(() => go(cur + 1), 10000); };
    dots.forEach((d, i) => d.addEventListener("click", () => { go(i); start(); }));
    box.addEventListener("scroll", () => requestAnimationFrame(mark), { passive: true });
    box.parentNode.addEventListener("mouseenter", stop); box.parentNode.addEventListener("mouseleave", start);
    box.parentNode.addEventListener("focusin", stop);
    start();
  }
}
