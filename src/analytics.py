"""
Anonyme Nutzungszählung.

Was gezählt wird: wie oft die App geöffnet wurde, wie oft jemand angefangen hat zu
tippen, wie oft geprüft wurde, wie viele Auswertungen durchliefen, wie oft die
semantische Stufe nicht verfügbar war und wie oft ein Fehler auftrat.

Was NICHT gespeichert wird: der Anzeigentext, Namen, E-Mail-Adressen, IP-Adressen,
Browserdaten. Gespeichert werden ausschliesslich ein Datum und ein Zähler pro
Ereignisart. Aus diesen Zahlen lässt sich keine Person wiedererkennen; deshalb wird
auch nicht von „Besuchern“, sondern nur von Sitzungen gesprochen.

Jedes Ereignis wird pro Sitzung höchstens einmal gezählt. Streamlit führt das Skript
bei jeder Interaktion neu aus — ohne diese Sperre würde eine einzige Sitzung Dutzende
Zählungen erzeugen.

Ablage:
  * Ist in den Secrets ein Supabase-Projekt hinterlegt, gehen die Zählungen dorthin
    und überleben Neustarts.
  * Ohne diese Konfiguration zählt die App nur im Arbeitsspeicher des laufenden
    Prozesses. Auf Streamlit Community Cloud ist das NICHT dauerhaft: Beim
    Ruhezustand oder einem neuen Deploy sind die Zahlen weg. Die Oberfläche sagt
    das deutlich, statt eine Dauerhaftigkeit vorzutäuschen.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from threading import Lock

# Alle Zahlen sind SITZUNGEN, keine Personen und keine Einzelauswertungen: Jedes
# Ereignis wird pro Sitzung höchstens einmal gezählt. Wer in derselben Sitzung eine
# zweite Anzeige prüft, erscheint weiterhin als eine Sitzung. Die Bezeichnungen sagen
# das ausdrücklich, damit die Zahlen nicht überlesen werden.
EREIGNISSE = {
    "geoeffnet": "Sitzungen, in denen die App geöffnet wurde",
    "eingabe_begonnen": "Sitzungen, in denen Text eingefügt wurde",
    "pruefung_gestartet": "Sitzungen, in denen „Passung prüfen“ geklickt wurde",
    "auswertung_fertig": "Sitzungen mit mindestens einer abgeschlossenen Auswertung",
    "semantik_nicht_verfuegbar": "Sitzungen ohne semantische Stufe",
    "fehler": "Sitzungen mit einem Fehler bei der Auswertung",
}

_speicher: dict[tuple[str, str], int] = defaultdict(int)
_sperre = Lock()
_TABELLE = "passt_mesut_events"


def _heute() -> str:
    return datetime.now(timezone.utc).date().isoformat()


# --------------------------------------------------------------------------- Supabase

def _konfiguration(secrets) -> tuple[str, str] | None:
    try:
        url = secrets.get("SUPABASE_URL", "")
        key = secrets.get("SUPABASE_KEY", "")
    except Exception:
        return None
    return (url.rstrip("/"), key) if url and key else None


def _supabase(methode: str, pfad: str, daten=None, konfig=None, params: str = ""):
    url, key = konfig
    ziel = f"{url}/rest/v1/{pfad}{params}"
    kopf = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    rumpf = json.dumps(daten).encode() if daten is not None else None
    anfrage = urllib.request.Request(ziel, data=rumpf, headers=kopf, method=methode)
    with urllib.request.urlopen(anfrage, timeout=6) as antwort:
        inhalt = antwort.read().decode() or "[]"
    return json.loads(inhalt) if inhalt.strip().startswith(("[", "{")) else []


# --------------------------------------------------------------------------- API

def zaehle(ereignis: str, secrets=None) -> None:
    """Erhöht den Zähler für heute. Fehler beim Speichern bleiben folgenlos."""
    if ereignis not in EREIGNISSE:
        return
    tag = _heute()
    with _sperre:
        _speicher[(tag, ereignis)] += 1
    konfig = _konfiguration(secrets) if secrets is not None else None
    if not konfig:
        return
    try:
        # Reines Anhängen, kein Lesen-Ändern-Schreiben. Ein Zähler, der erst gelesen
        # und dann erhöht wird, verliert bei zwei gleichzeitigen Aufrufen eine Zählung.
        # Eine Zeile je Ereignis ist dagegen atomar; summiert wird erst beim Lesen.
        _supabase("POST", _TABELLE, daten={"tag": tag, "ereignis": ereignis}, konfig=konfig)
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError, TimeoutError):
        pass  # Zählung ist Nebensache und darf die App nie stören


def dauerhaft(secrets=None) -> bool:
    return _konfiguration(secrets) is not None if secrets is not None else False


def bericht(secrets=None) -> dict:
    """Aggregiert die Zählungen auf Tag, Woche und Monat."""
    zeilen: list[tuple[str, str, int]] = []
    konfig = _konfiguration(secrets) if secrets is not None else None
    geladen = False
    if konfig:
        try:
            # Eine Zeile je Ereignis; die Summe entsteht hier beim Lesen.
            for eintrag in _supabase(
                "GET", _TABELLE, konfig=konfig, params="?select=tag,ereignis&limit=100000"
            ):
                zeilen.append((eintrag["tag"], eintrag["ereignis"], 1))
            geladen = True
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError, TimeoutError):
            geladen = False
    if not geladen:
        with _sperre:
            zeilen = [(t, e, a) for (t, e), a in _speicher.items()]

    heute = datetime.now(timezone.utc).date()
    grenzen = {"tag": heute, "woche": heute - timedelta(days=6), "monat": heute - timedelta(days=29)}
    ergebnis = {zeitraum: {e: 0 for e in EREIGNISSE} for zeitraum in grenzen}
    for tag_text, ereignis, anzahl in zeilen:
        try:
            tag = date.fromisoformat(tag_text)
        except ValueError:
            continue
        if ereignis not in EREIGNISSE:
            continue
        for zeitraum, ab in grenzen.items():
            if tag >= ab:
                ergebnis[zeitraum][ereignis] += anzahl

    for zeitraum, werte in ergebnis.items():
        geoeffnet = werte["geoeffnet"]
        eingabe = werte["eingabe_begonnen"]
        gestartet = werte["pruefung_gestartet"]
        werte["ohne_auswertung"] = max(0, geoeffnet - gestartet)
        werte["eingabe_ohne_pruefung"] = max(0, eingabe - gestartet)
    ergebnis["_dauerhaft"] = bool(konfig and geladen)
    return ergebnis
