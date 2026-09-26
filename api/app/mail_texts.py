"""Modèles des e-mails : HTML (gabarit email_templates/layout.html) + version texte de secours.
Français et anglais ; les autres langues reçoivent l'anglais. Les valeurs sont échappées avant insertion."""
from datetime import datetime
from html import escape
from pathlib import Path
from string import Template
from zoneinfo import ZoneInfo

LAYOUT = Template((Path(__file__).parent / "email_templates" / "layout.html").read_text())
P = '<p style="margin:0 0 14px;font-size:15px;line-height:1.6">{}</p>'
BTN = ('<table role="presentation" cellpadding="0" cellspacing="0" style="margin:6px 0 20px"><tr><td style="border-radius:8px;background:{bg}">'
       '<a href="{url}" style="display:inline-block;padding:12px 20px;font-size:15px;font-weight:600;color:#FFFFFF;text-decoration:none;border-radius:8px">{label}</a>'
       '</td></tr></table>')
ROW = ('<tr><td style="padding:7px 0;color:#5B6773;font-size:14px;width:38%;vertical-align:top">{}</td>'
       '<td style="padding:7px 0;font-size:14px;font-weight:600;vertical-align:top">{}</td></tr>')

T = {
    "fr": {
        "footer": "Vous recevez cet e-mail parce que vous avez un compte sur {site}.",
        "legal": "Mentions légales",
        "welcome": dict(
            subject="Bienvenue sur {site}", title="Bienvenue, {user} !",
            pre="Votre compte {site} est prêt.",
            paras=["Votre compte est créé. Vous pouvez maintenant aimer, commenter et publier des ressources pour LLM : contextes, prompts, agents, serveurs MCP…"],
            rows=[("Identifiant", "{user}"), ("Adresse e-mail", "{email}")],
            button=("Découvrir les ressources", "{origin}")),
        "login": dict(
            subject="Nouvelle connexion à votre compte {site}", title="Nouvelle connexion à votre compte",
            pre="Connexion le {date}.",
            paras=["Bonjour {user}, une connexion à votre compte vient d'avoir lieu. Si c'est bien vous, il n'y a rien à faire."],
            rows=[("Date", "{date}"), ("Adresse IP", "{ip}"), ("Appareil", "{agent}")],
            after="Si ce n'est pas vous, changez votre mot de passe tout de suite :",
            button=("Ce n'était pas moi", "{origin}/a2/mot-de-passe-oublie"), danger=True),
        "published": dict(
            subject="Votre fiche « {name} » est en ligne", title="Votre fiche est en ligne",
            pre="{kind} · {name}",
            paras=["Bonjour {user}, votre nouvelle fiche est publiée sur {site} et visible par tous."],
            rows=[("Fiche", "{name}"), ("Type", "{kind}")],
            button=("Voir la fiche", "{url}"),
            after="Pensez à compléter « Testé sur » : c'est ce qui donne confiance aux autres utilisateurs."),
        "reset": dict(
            subject="Réinitialiser votre mot de passe {site}", title="Choisir un nouveau mot de passe",
            pre="Lien valable 1 heure.",
            paras=["Bonjour {user}, vous avez demandé à réinitialiser votre mot de passe. Ce lien est valable 1 heure et ne sert qu'une fois."],
            button=("Choisir un nouveau mot de passe", "{link}"),
            after="Si vous n'avez rien demandé, ignorez cet e-mail : votre mot de passe ne change pas."),
        "date_fmt": "%d/%m/%Y à %H:%M (heure de Paris)",
    },
    "en": {
        "footer": "You are receiving this e-mail because you have an account on {site}.",
        "legal": "Legal notice",
        "welcome": dict(
            subject="Welcome to {site}", title="Welcome, {user}!",
            pre="Your {site} account is ready.",
            paras=["Your account has been created. You can now like, comment on and publish LLM resources: contexts, prompts, agents, MCP servers…"],
            rows=[("Username", "{user}"), ("E-mail address", "{email}")],
            button=("Explore resources", "{origin}")),
        "login": dict(
            subject="New sign-in to your {site} account", title="New sign-in to your account",
            pre="Signed in on {date}.",
            paras=["Hello {user}, your account was just signed in. If this was you, there is nothing to do."],
            rows=[("Date", "{date}"), ("IP address", "{ip}"), ("Device", "{agent}")],
            after="If this wasn't you, change your password right away:",
            button=("This wasn't me", "{origin}/a2/mot-de-passe-oublie"), danger=True),
        "published": dict(
            subject="Your resource “{name}” is live", title="Your resource is live",
            pre="{kind} · {name}",
            paras=["Hello {user}, your new resource is published on {site} and visible to everyone."],
            rows=[("Resource", "{name}"), ("Type", "{kind}")],
            button=("View the resource", "{url}"),
            after="Remember to fill in “Tested on”: it is what makes other users trust a resource."),
        "reset": dict(
            subject="Reset your {site} password", title="Choose a new password",
            pre="Link valid for 1 hour.",
            paras=["Hello {user}, you asked to reset your password. This link is valid for 1 hour and can be used once."],
            button=("Choose a new password", "{link}"),
            after="If you did not ask for this, ignore this e-mail: your password stays the same."),
        "date_fmt": "%Y-%m-%d %H:%M (Paris time)",
    },
}


def mail(template: str, lang: str, **kw) -> tuple[str, str, str]:
    """Renvoie (sujet, texte, html) pour welcome, login, published ou reset."""
    L = "fr" if lang == "fr" else "en"
    t, m = T[L], T[L][template]
    kw.setdefault("date", datetime.now(ZoneInfo("Europe/Paris")).strftime(t["date_fmt"]))
    f = lambda s: s.format(**kw)                                   # texte brut
    h = lambda s: s.format(**{k: escape(str(v)) for k, v in kw.items()})   # HTML échappé
    subject = f(m["subject"])
    # Version texte
    lines = [f(p) for p in m["paras"]] + [""] + [f"- {a} : {f(b)}" for a, b in m.get("rows", [])]
    if m.get("after"):
        lines += ["", f(m["after"])]
    lines += ["", f"{m['button'][0]} : {f(m['button'][1])}", "", f(t["footer"]), kw["origin"]]
    text = "\n".join(lines).replace("\n\n\n", "\n\n") + "\n"
    # Version HTML
    body = "".join(P.format(h(p)) for p in m["paras"])
    if m.get("rows"):
        body += ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:4px 0 18px;border-top:1px solid #E9EDF1;border-bottom:1px solid #E9EDF1">'
                 + "".join(ROW.format(escape(a), h(b)) for a, b in m["rows"]) + "</table>")
    if m.get("after") and m.get("danger"):
        body += P.format(h(m["after"]))
    body += BTN.format(url=h(m["button"][1]), label=escape(m["button"][0]), bg="#B91C1C" if m.get("danger") else "#0B7285")
    if m.get("after") and not m.get("danger"):
        body += P.format(h(m["after"])).replace("font-size:15px", "font-size:14px;color:#5B6773")
    html = LAYOUT.substitute(lang=L, subject=escape(subject), preheader=h(m["pre"]), origin=escape(kw["origin"]),
                             site=escape(kw["site"]), title=h(m["title"]), body=body, footer=h(t["footer"]),
                             domain=escape(kw["origin"].split("://")[-1]), legal=t["legal"])
    return subject, text, html
