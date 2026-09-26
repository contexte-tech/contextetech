from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import get_settings
from .routes import admin, auth, comments, meta, profile, reports, resources, sample, users

app = FastAPI(title="ContexteTech API", version="0.1.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

UNSAFE = {"POST", "PUT", "PATCH", "DELETE"}


@app.middleware("http")
async def origin_check(request: Request, call_next):
    """Protection CSRF : toute requête d'écriture doit venir de notre origine."""
    if request.method in UNSAFE:
        origin = request.headers.get("origin") or request.headers.get("referer")
        allowed = urlparse(get_settings().public_origin)
        if origin:
            o = urlparse(origin)
            if (o.scheme, o.netloc) != (allowed.scheme, allowed.netloc):
                return JSONResponse({"detail": "bad_origin"}, status_code=403)
        elif request.cookies.get("ctx_session"):
            return JSONResponse({"detail": "missing_origin"}, status_code=403)
    return await call_next(request)


app.include_router(meta.router)
# Documentation /api/docs : seule la lecture publique du catalogue y figure
app.include_router(auth.router, include_in_schema=False)
app.include_router(resources.router)
app.include_router(sample.router, include_in_schema=False)
app.include_router(comments.router, include_in_schema=False)
app.include_router(profile.router, include_in_schema=False)
app.include_router(users.router)
app.include_router(admin.router, include_in_schema=False)
app.include_router(reports.router, include_in_schema=False)
