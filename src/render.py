"""
Sichere Ausgabe von Text, der aus der eingefügten Stellenanzeige stammt.

Die Oberfläche baut einige Karten als HTML. Alles, was aus der Anzeige kommt, muss
vorher durch `sicher()`. Diese Funktion liegt bewusst in einem eigenen Modul, damit
die Tests genau den Code prüfen, den die App auch wirklich benutzt — und nicht
ersatzweise `html.escape` aus der Standardbibliothek.
"""

from __future__ import annotations

from html import escape

# Nach dem Maskieren darf keines dieser Zeichen mehr im Text stehen. Das kaufmännische
# Und gehört bewusst nicht dazu: maskierte Ausgabe besteht gerade aus &lt; und &quot;.
_GEFAEHRLICH = ("<", ">", '"', "'")


def sicher(text: str | None, grenze: int | None = None) -> str:
    """Maskiert HTML-Sonderzeichen und kürzt optional auf eine Höchstlänge."""
    text = "" if text is None else str(text)
    if grenze and len(text) > grenze:
        text = text[: max(0, grenze - 1)].rstrip() + "…"
    return escape(text, quote=True)


def sichere_url(url: str | None) -> str:
    """
    Gibt eine URL nur zurück, wenn sie http oder https ist.

    Damit lassen sich weder javascript: noch data: Adressen in ein href schmuggeln,
    falls hier je eine Adresse aus fremder Quelle landet.
    """
    url = (url or "").strip()
    if not url.lower().startswith(("http://", "https://")):
        return ""
    return escape(url, quote=True)


def enthaelt_rohes_html(text: str) -> bool:
    """Hilfsfunktion für Tests: steckt in diesem Text noch unmaskiertes HTML?"""
    return any(z in (text or "") for z in _GEFAEHRLICH)
