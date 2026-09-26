import type { APIRoute } from "astro";
import { site } from "../lib/server.js";

export const GET: APIRoute = () => {
  const S = site();
  const body = `User-agent: *
Disallow: /api/
Disallow: /a2
Disallow: /a3
Allow: /api/docs

Sitemap: ${S.origin}/sitemap.xml

# Présentation du site pour les assistants IA : ${S.origin}/llms.txt
`;
  return new Response(body, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
};
