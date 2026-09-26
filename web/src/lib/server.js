// Utilitaires côté serveur uniquement (pages Astro)
const API = process.env.API_INTERNAL_URL || "http://api:8000";

export function site() {
  const e = process.env;
  return {
    name: e.SITE_NAME || "ContexteTech",
    origin: (e.PUBLIC_ORIGIN || "https://localhost").replace(/\/$/, ""),
    legal: {
      editeur: e.LEGAL_EDITEUR || "", forme: e.LEGAL_FORME || "", adresse: e.LEGAL_ADRESSE || "",
      siren: e.LEGAL_SIREN || "", email: e.LEGAL_EMAIL || "", directeur: e.LEGAL_DIRECTEUR || "",
      hebergeur: e.LEGAL_HEBERGEUR || "", majLe: e.LEGAL_UPDATED || "2026-09-25",
    },
  };
}

/** GET vers l'API interne en transmettant le cookie de session. Renvoie null si 404. */
export async function api(Astro, path) {
  const res = await fetch(API + path, {
    headers: { cookie: Astro.request.headers.get("cookie") || "", accept: "application/json" },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`API ${res.status} ${path}`);
  return res.json();
}

export const hasSession = (Astro) => /(?:^|;\s*)ctx_session=/.test(Astro.request.headers.get("cookie") || "");

/** Cache partagé (CDN/proxy) uniquement pour les visiteurs anonymes */
export function cachePublic(Astro, seconds = 60) {
  Astro.response.headers.set("Cache-Control", hasSession(Astro)
    ? "private, no-store"
    : `public, max-age=0, s-maxage=${seconds}, stale-while-revalidate=300`);
  Astro.response.headers.set("Vary", "Cookie");
}

/** Zone privée /a2/ : jamais en cache, ni chez le visiteur ni sur un proxy */
export function noCache(Astro) {
  Astro.response.headers.set("Cache-Control", "private, no-store");
  Astro.response.headers.set("X-Robots-Tag", "noindex, nofollow");
}

/** Adresse encodée en base64 pour les liens hors robots (data-o), décodés au clic par Base.astro */
export const b64 = (u) => Buffer.from(u).toString("base64").replace(/=+$/, "");
