"""Analoge Messuhr für den Passungswert — als Inline-SVG, ohne externe Abhängigkeiten."""

import math

_GRAU = "#5B6B82"
_AMBER = "#D9A441"
_GRUEN = "#3DBE8B"
_NADEL = "#E8EEF6"
_TEXT = "#E8EEF6"
_GEDAEMPFT = "#8FA3BF"

CX, CY, R = 170.0, 160.0, 118.0


def _punkt(winkel_grad: float, radius: float) -> tuple[float, float]:
    rad = math.radians(winkel_grad)
    return CX + radius * math.cos(rad), CY - radius * math.sin(rad)


def _bogen(von_prozent: float, bis_prozent: float, radius: float, farbe: str, breite: float) -> str:
    w1 = 180 - von_prozent * 1.8
    w2 = 180 - bis_prozent * 1.8
    x1, y1 = _punkt(w1, radius)
    x2, y2 = _punkt(w2, radius)
    gross = 1 if abs(w1 - w2) > 180 else 0
    return (
        f'<path d="M {x1:.1f} {y1:.1f} A {radius} {radius} 0 {gross} 0 {x2:.1f} {y2:.1f}" '
        f'fill="none" stroke="{farbe}" stroke-width="{breite}" stroke-linecap="round" />'
    )


def urteil(score: int) -> tuple[str, str]:
    """Beschriftung des Messwerts.

    Die Wörter benennen bewusst die *Abdeckung* der Anzeige und nicht die Eignung:
    Der Wert sagt, wie viel der ausgeschriebenen Anforderungen belegt ist. Ob daraus
    eine Einladung wird, entscheiden Erfahrungsjahre, Team und Gespräch — nicht diese
    Zahl. Ein Wort wie „Passung“ würde mehr versprechen, als hier gemessen wird.
    """
    if score >= 80:
        return "Hohe fachliche Abdeckung", _GRUEN
    if score >= 65:
        return "Gute fachliche Abdeckung", _GRUEN
    if score >= 50:
        return "Teilweise Abdeckung", _AMBER
    if score >= 30:
        return "Geringe Abdeckung", _AMBER
    return "Kaum Abdeckung", _GRAU


def messuhr(score: int) -> str:
    label, farbe = urteil(score)
    winkel = 180 - score * 1.8
    nx, ny = _punkt(winkel, R - 26)
    hx, hy = _punkt(winkel + 180, 16)

    teile = [
        f'<svg viewBox="0 0 340 210" width="100%" role="img" '
        f'aria-label="Passungswert {score} Prozent: {label}" '
        f'xmlns="http://www.w3.org/2000/svg">',
        _bogen(0, 100, R, "#1E3350", 16),
        _bogen(0, 50, R, _GRAU, 16),
        _bogen(50, 75, R, _AMBER, 16),
        _bogen(75, 100, R, _GRUEN, 16),
    ]

    # Skalenstriche alle 10 %
    for p in range(0, 101, 10):
        w = 180 - p * 1.8
        x1, y1 = _punkt(w, R - 11)
        x2, y2 = _punkt(w, R - (22 if p % 50 == 0 else 17))
        teile.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#44608A" stroke-width="{2 if p % 50 == 0 else 1}" />'
        )
    for p, dx in ((0, 6), (50, 0), (100, -6)):
        lx, ly = _punkt(180 - p * 1.8, R + 16)
        teile.append(
            f'<text x="{lx + dx:.1f}" y="{ly + 5:.1f}" fill="{_GEDAEMPFT}" '
            f'font-size="11" text-anchor="middle" font-family="sans-serif">{p}</text>'
        )

    teile += [
        f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{_NADEL}" '
        f'stroke-width="3.5" stroke-linecap="round" />',
        f'<circle cx="{CX}" cy="{CY}" r="9" fill="#16283F" stroke="{_NADEL}" stroke-width="2.5" />',
        f'<text x="{CX}" y="{CY - 44:.0f}" fill="{_TEXT}" font-size="46" font-weight="600" '
        f'text-anchor="middle" font-family="sans-serif">{score} %</text>',
        f'<text x="{CX}" y="{CY + 36:.0f}" fill="{farbe}" font-size="15" font-weight="600" '
        f'text-anchor="middle" font-family="sans-serif">{label}</text>',
        f'<text x="{CX}" y="{CY + 54:.0f}" fill="{_GEDAEMPFT}" font-size="10.5" '
        f'text-anchor="middle" font-family="sans-serif" letter-spacing="0.5">'
        f'FACHLICHE ABDECKUNG DER ANZEIGE</text>',
        "</svg>",
    ]
    return "".join(teile)
