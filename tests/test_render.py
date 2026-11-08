"""Tests für die Ausgabemaskierung — genau die Funktion, die die App verwendet."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.render import enthaelt_rohes_html, sicher, sichere_url  # noqa: E402


def test_script_tag_wird_maskiert():
    assert "<script>" not in sicher("<script>alert(1)</script>")


def test_bild_mit_onerror_wird_maskiert():
    roh = '<img src=x onerror="alert(1)">'
    aus = sicher(roh)
    assert "<img" not in aus and 'onerror="' not in aus


def test_anfuehrungszeichen_werden_maskiert():
    assert '"' not in sicher('abc" onmouseover="x')


def test_kuerzung_behaelt_maskierung():
    aus = sicher("<b>" + "x" * 300, grenze=50)
    assert len(aus) <= 80 and "<b>" not in aus


def test_none_und_leer_sind_unproblematisch():
    assert sicher(None) == "" and sicher("") == ""


def test_javascript_url_wird_verworfen():
    assert sichere_url("javascript:alert(1)") == ""
    assert sichere_url("data:text/html,<script>") == ""


def test_https_url_bleibt_erhalten():
    assert sichere_url("https://github.com/Mst-KrgZ") == "https://github.com/Mst-KrgZ"


def test_app_nutzt_dieselbe_funktion():
    """Die App importiert sicher() aus diesem Modul — kein zweiter Maskierungspfad."""
    quelltext = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    assert "from src.render import sicher" in quelltext
    assert "def _sicher(" not in quelltext, "Es darf keine zweite Maskierfunktion geben"


def test_echte_fundstelle_aus_der_analyse_wird_sauber():
    from src.matcher import analysiere

    boese = """Data Analyst (m/w/d)
Profil: Sehr gute SQL-Kenntnisse <img src=x onerror="alert(1)"> und Power BI.
Datenqualität und Reporting."""
    r = analysiere(boese, semantik=False)
    rohe = [f for t in r.treffer for f in t.fundstellen]
    assert any(enthaelt_rohes_html(f) for f in rohe), "Testvoraussetzung: Rohtext enthält HTML"
    for f in rohe:
        assert not enthaelt_rohes_html(sicher(f))
