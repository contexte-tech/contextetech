"""Tests unitaires sans base de données : identifiants courts, mots de passe, formats de datasets."""
from app.formats import detect_format, scan_jsonl, vars_of
from app.routes.resources import short_id
from app.security import hash_password, verify_password


def test_short_id_is_stable_and_matches_site():
    # Même valeur que web/src/lib/paths.js (adresse publique de la fiche)
    assert short_id("contextetech--anonymisation-rgpd") == "pekk5y"
    assert short_id("a--b") == short_id("a--b")
    assert short_id("a--b") != short_id("a--c")


def test_password_hash_roundtrip():
    h = hash_password("correct horse battery staple")
    assert h.startswith("$argon2")
    assert verify_password(h, "correct horse battery staple")
    assert not verify_password(h, "wrong")
    assert not verify_password("not-a-hash", "x")


def test_template_variables():
    assert vars_of("Résume {{notes}} pour {{public}}") == ["notes", "public"]


def test_jsonl_scan():
    lines = ['{"messages": [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]}'] * 3
    rows, fmt, preview = scan_jsonl(lines)
    assert rows == 3
    assert detect_format({"prompt": "a", "completion": "b"}) is not None
