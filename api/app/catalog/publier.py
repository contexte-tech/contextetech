"""Publie un fichier de catalogue (liste de fiches JSON) sur une instance ContexteTech, via l'API.

    ORIGIN=https://contextetech.com ADMIN_USERNAME=… ADMIN_PASSWORD=… python3 publier.py catalogue-initial.json
    VIDER=1 … : supprime d'abord toutes les fiches existantes (instance locale de démo uniquement)
"""
import http.cookiejar, json, os, sys, urllib.parse, urllib.request

origin = os.environ["ORIGIN"].rstrip("/")
api = os.environ.get("API", origin)
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def call(method, path, body=None, form=False):
    data = headers = None
    headers = {"Origin": origin}
    if body is not None:
        data = urllib.parse.urlencode(body).encode() if form else json.dumps(body).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
    req = urllib.request.Request(api + path, data=data, method=method, headers=headers)
    try:
        with op.open(req) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


call("POST", "/api/auth/login", {"username": os.environ["ADMIN_USERNAME"], "password": os.environ["ADMIN_PASSWORD"]}, form=True)
if os.environ.get("VIDER") == "1":
    st, raw = call("GET", "/api/resources?kind=all&page=1")
    for it in json.loads(raw)["items"]:
        print("suppression", it["id"], call("DELETE", "/api/resources/" + it["id"])[0])
ok = 0
for r in json.load(open(sys.argv[1])):
    body = {k: r[k] for k in ("kind", "name", "authorHandle", "description", "tags", "clang", "license", "sub", "sourceUrl", "data")}
    st, raw = call("PUT", f"/api/resources/{r['id']}?create=1", body)
    if st == 409:                                   # déjà publiée : mise à jour
        st, raw = call("PUT", f"/api/resources/{r['id']}", body)
    ok += st == 200
    print(f"{st} {r['kind']:8} {r['id']}" + ("" if st == 200 else f"  → {raw[:200].decode(errors='replace')}"))
print(f"{ok}/{len(json.load(open(sys.argv[1])))} publiées")
