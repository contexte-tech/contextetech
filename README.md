<p align="center"><img src="https://contextetech.com/logo.png" alt="ContexteTech" width="390"></p>

<p align="center">
<a href="https://www.bestpractices.dev/projects/14974"><img src="https://www.bestpractices.dev/projects/14974/badge" alt="OpenSSF Best Practices"></a>
<a href="https://github.com/contexte-tech/contextetech/actions/workflows/ci.yml"><img src="https://github.com/contexte-tech/contextetech/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0-blue" alt="AGPL-3.0"></a>
</p>

# ContexteTech

Open-source hub of LLM resources, in the spirit of Hugging Face:
**in-context learning contexts**, **prompts**, fine-tuning **datasets** and
**LoRA configs**. Publish, fork, test live with streaming, export to
Axolotl / PEFT / 🤗 datasets. Interface in 5 languages (fr, en, es, de, it).

## Architecture

```
            ┌──────────── Caddy (HTTPS, HTTP/3, compression) ────────────┐
            │  /api/*  ──►  api  : FastAPI async · Uvicorn               │
            │  /*      ──►  web  : Astro SSR (plain HTML) + Svelte islands│
            └────────────────────────────────────────────────────────────┘
   api ──► PostgreSQL (Scaleway Managed Database, TLS)
   api ──► Redis (sessions, list cache, rate limiting)
   api ──► Scaleway Object Storage (large datasets, optional)
   api ──► Sandbox LLM: Anthropic or an OpenAI-compatible API (Ollama, vLLM)
```

- **Rendering**: pages are served as HTML by Astro, with no JavaScript except for
  interactive islands (sandbox, likes, forms). Resource pages are indexable, with
  `hreflang`, schema.org structured data and a sitemap.
- **Cache**: lists and facets in Redis (30 s, invalidated on every write);
  anonymous pages with `s-maxage=60` for a CDN; `/_astro/*` assets immutable.
- **Streaming**: sandbox answers arrive over SSE, word by word.
- **Security**: sessions in an `HttpOnly` + `SameSite=Lax` cookie, origin check
  on every write, Argon2 password hashing.

## Production

contextetech.com runs in containers (API, site, Redis) behind Caddy (TLS, HTTP/3)
and the Bunny CDN, with managed PostgreSQL at Scaleway. The procedure specific to
this server is not published; `docker-compose.yml` and `deploy/Caddyfile` are
enough to install ContexteTech on your own machine.

## Getting started (dedicated machine)

```bash
cp .env.example .env     # Scaleway database, domain, API key, legal notice
docker compose up -d --build
docker compose logs -f api web
```

- Hub: `https://contextetech.com/en/` (English version; `https://contextetech.com/` redirects to the browser language)
- API documentation: `https://contextetech.com/api/docs`

### Scaleway database

1. Managed Databases → PostgreSQL 16 instance → `contextec` database + dedicated user.
2. **Allowed IPs**: only allow the Docker server's IP.
3. Copy the endpoint (IP, port) and credentials into `.env`.
4. Enable automatic backups for the instance.

Alembic migrations run when `api` starts.

Local test without Scaleway: `POSTGRES_HOST=db`, `POSTGRES_PORT=5432`,
`POSTGRES_SSLMODE=disable`, `COOKIE_SECURE=0`, then
`docker compose --profile local-db up -d`.

### Large datasets

Up to 256 KB, a dataset is stored in the database. Beyond that (up to `MAX_DATASET_MB`),
it goes to Scaleway Object Storage: create a private bucket and an API key, then
fill in `S3_*`. Downloads use a pre-signed URL.

### Sandbox

| Mode | `.env` |
|---|---|
| Anthropic | `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY` |
| Ollama on a local GPU | `LLM_PROVIDER=openai`, `LLM_BASE_URL=http://ollama:11434/v1`, `docker compose --profile ollama up -d`, then `docker compose exec ollama ollama pull qwen2.5:7b-instruct` |
| vLLM / other | `LLM_PROVIDER=openai` + `LLM_BASE_URL` + `LLM_API_KEY` |
| Disabled | `LLM_PROVIDER=` |

### Oracle Linux 9 / RHEL 9

```bash
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
sudo firewall-cmd --permanent --add-service=http --add-service=https --add-port=443/udp
sudo firewall-cmd --reload
```

## Development

```bash
# API
cd api && pip install -r requirements.txt
uvicorn app.main:app --reload
# Web
cd web && npm install && API_INTERNAL_URL=http://localhost:8000 npm run dev
```

## Images

```bash
IMAGE_PREFIX=ghcr.io/<account> IMAGE_TAG=0.1.0 docker compose build
IMAGE_PREFIX=ghcr.io/<account> IMAGE_TAG=0.1.0 docker compose push api web
```

## License

To be chosen before publication, then add the `LICENSE` file.

## License

ContexteTech's code is distributed under the **GNU AGPL-3.0** license (see [LICENSE](LICENSE)):
you may use, modify and redistribute it, provided that you publish the code of any
modified version under the same license, including when it is offered online.

Resources published on contextetech.com each keep the license chosen by their author
(shown on the resource page); the AGPL-3.0 license only covers the software.

## Trademarks and logos

The ContexteTech and Contexthèque names, logos and visuals are not covered by the AGPL-3.0: see [TRADEMARKS.md](TRADEMARKS.md). Any reuse must credit ContexteTech as the source, with a link, in its legal notice.
