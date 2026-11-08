"""Tests für die anonyme Nutzungszählung."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import analytics  # noqa: E402


def setup_function():
    analytics._speicher.clear()


def test_nur_bekannte_ereignisse_werden_gezaehlt():
    analytics.zaehle("geoeffnet")
    analytics.zaehle("voellig_erfunden")
    assert analytics.bericht()["tag"]["geoeffnet"] == 1


def test_bericht_enthaelt_keinen_anzeigentext():
    analytics.zaehle("auswertung_fertig")
    text = repr(analytics.bericht())
    for verraeter in ("Power BI", "SQL", "@", "http", "Profil"):
        assert verraeter not in text


def test_offen_ohne_pruefung_wird_berechnet():
    for _ in range(5):
        analytics.zaehle("geoeffnet")
    for _ in range(2):
        analytics.zaehle("pruefung_gestartet")
    assert analytics.bericht()["tag"]["ohne_auswertung"] == 3


def test_ohne_konfiguration_ist_die_ablage_nicht_dauerhaft():
    assert analytics.dauerhaft(secrets={}) is False
    assert analytics.bericht(secrets={})["_dauerhaft"] is False


def test_gespeichert_wird_nur_tag_ereignis_anzahl():
    analytics.zaehle("geoeffnet")
    for schluessel in analytics._speicher:
        tag, ereignis = schluessel
        assert len(tag) == 10 and ereignis in analytics.EREIGNISSE


def test_zaehlung_ohne_lesen_aenderen_schreiben():
    """Der Supabase-Pfad hängt nur an und liest vorher nichts — sonst gingen bei
    gleichzeitigen Aufrufen Zählungen verloren."""
    quelltext = (Path(__file__).resolve().parents[1] / "src" / "analytics.py").read_text(
        encoding="utf-8"
    )
    anfang = quelltext.index("def zaehle(")
    ende = quelltext.index("def dauerhaft(")
    koerper = quelltext[anfang:ende]
    assert '"GET"' not in koerper, "zaehle() darf vor dem Schreiben nichts lesen"
    assert '"anzahl"' not in koerper, "zaehle() darf keinen vorberechneten Zählerstand senden"


def test_eingabe_ohne_pruefung_wird_getrennt_ausgewiesen():
    for _ in range(4):
        analytics.zaehle("geoeffnet")
    for _ in range(3):
        analytics.zaehle("eingabe_begonnen")
    analytics.zaehle("pruefung_gestartet")
    werte = analytics.bericht()["tag"]
    assert werte["eingabe_ohne_pruefung"] == 2
    assert werte["ohne_auswertung"] == 3


def test_bezeichnungen_sprechen_von_sitzungen():
    for text in analytics.EREIGNISSE.values():
        assert "Sitzung" in text, f"irreführende Bezeichnung: {text}"
