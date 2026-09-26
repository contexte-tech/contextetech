import { defineConfig } from "astro/config";
import node from "@astrojs/node";
import svelte from "@astrojs/svelte";

export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  integrations: [svelte()],
  // Les formulaires postent vers l'API, qui vérifie elle-même l'origine
  security: { checkOrigin: false },
  // CSS servi en fichier (/_astro/*.css, en cache un an) plutôt que recopié dans chaque page
  build: { inlineStylesheets: "never" },
  compressHTML: true,
  // Lancement local sans Docker ni Caddy : /api et /healthz relayés vers l'API (API_PROXY=http://127.0.0.1:8201)
  vite: {
    // Scripts et petits fichiers toujours servis en fichiers (/_astro/*, en cache), jamais recopiés dans la page
    build: { assetsInlineLimit: 0 },
    ...(process.env.API_PROXY ? { server: { proxy: { "/api": process.env.API_PROXY, "/healthz": process.env.API_PROXY } } } : {}),
  },
});
