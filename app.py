"""
Passt Mesut? — Stellenanzeige einfügen, fachliche Abdeckung mit Belegen prüfen.

Eine Anwendung für Recruiterinnen und Recruiter: Anzeigentext einfügen, und die App
vergleicht die Anforderungen mit dem belegten Kompetenzprofil von Mesut Karagöz.
Jeder Treffer nennt den Nachweis. Lücken werden offen ausgewiesen.
"""

import streamlit as st

from src import analytics
from src.gauge import messuhr, urteil
from src.render import sicher as _sicher, sichere_url
from src.matcher import analysiere, lade_semantik
from src.profile_data import BELEGTE_BRANCHEN, PERSON, PROJEKTE, SKILLS, TRANSFER_SATZ

st.set_page_config(
    page_title="Passt Mesut?",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
  .block-container {padding-top: 2.2rem; max-width: 860px;}
  h1, h2, h3 {letter-spacing: -0.01em;}
  .pm-hero {border-bottom: 1px solid #1E3350; padding-bottom: 1.1rem; margin-bottom: 1.4rem;}
  .pm-hero h1 {margin: 0; font-size: 2.3rem;}
  .pm-hero p {color: #8FA3BF; margin: .35rem 0 0; font-size: 1.02rem;}
  .pm-card {background: #16283F; border: 1px solid #1E3350; border-radius: 10px;
            padding: .85rem 1rem; margin-bottom: .55rem;}
  .pm-card b {font-size: 1rem;}
  .pm-beleg {color: #8FA3BF; font-size: .87rem; margin-top: .25rem; line-height: 1.45;}
  .pm-quote {color: #6F86A6; font-size: .83rem; font-style: italic; margin-top: .3rem;}
  .pm-links {margin-top: .45rem; font-size: .86rem;}
  .pm-links a {color: #4DA3FF; text-decoration: none; margin-right: .9rem;}
  .pm-links a:hover {text-decoration: underline;}
  .pm-tag {display: inline-block; background: #1E3350; color: #8FA3BF; border-radius: 5px;
           padding: .08rem .45rem; font-size: .74rem; margin-left: .4rem; vertical-align: middle;}
  .pm-gap {background: #2A1F1A; border: 1px solid #4A3526;}
  .pm-foot {color: #6F86A6; font-size: .84rem; border-top: 1px solid #1E3350;
            padding-top: 1rem; margin-top: 2rem; line-height: 1.6;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown(
    f"""<div class="pm-hero">
      <h1>Passt Mesut?</h1>
      <p>Ihre Stellenanzeige einfügen — die App vergleicht die Anforderungen mit dem
      belegten Profil von {PERSON['name']} und nennt zu jedem Treffer den Nachweis.</p>
    </div>""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def _semantik_status():
    return lade_semantik()


def _einmal_zaehlen(ereignis: str) -> None:
    """Zählt ein Ereignis höchstens einmal pro Sitzung."""
    schluessel = f"_gezaehlt_{ereignis}"
    if st.session_state.get(schluessel):
        return
    st.session_state[schluessel] = True
    try:
        analytics.zaehle(ereignis, secrets=st.secrets)
    except Exception:
        pass


_einmal_zaehlen("geoeffnet")


# Bewusst OHNE st.cache_data: der eingefügte Anzeigentext würde sonst im
# Server-Cache liegen, obwohl die Oberfläche zusagt, dass er nicht gespeichert wird.
def _auswerten(text: str, semantik: bool):
    ergebnis = analysiere(text, semantik=semantik)
    return {
        "score": ergebnis.score,
        "treffer": [
            {
                "key": t.skill["key"], "label": t.skill["label"], "staerke": t.skill["staerke"],
                "kategorie": t.skill["kategorie"], "beleg": t.skill["beleg"],
                "projekte": t.skill["projekte"], "begriffe": t.begriffe,
                "fundstellen": t.fundstellen, "semantisch": t.semantisch, "pflicht": t.pflicht,
            }
            for t in ergebnis.treffer
        ],
        "luecken": [
            {"begriff": l.begriff, "fundstelle": l.fundstelle, "pflicht": l.pflicht}
            for l in ergebnis.luecken
        ],
        "offene": ergebnis.offene_zeilen,
        "semantik_aktiv": ergebnis.semantik_aktiv,
        "hinweis": ergebnis.hinweis,
        "belastbar": ergebnis.belastbar,
        "pflicht_luecken": ergebnis.pflicht_luecken,
        "standort": (
            {
                "orte": ergebnis.standort.orte,
                "modelle": ergebnis.standort.modelle,
                "passt": ergebnis.standort.passt,
                "begruendung": ergebnis.standort.begruendung,
            }
            if ergebnis.standort
            else None
        ),
        "sprachen": [
            {"sprache": s.sprache, "gefordert": s.gefordert, "vorhanden": s.vorhanden,
             "erfuellt": s.erfuellt, "fundstelle": s.fundstelle}
            for s in ergebnis.sprachen
        ],
        "branchen": [
            {"name": b.name, "fundstelle": b.fundstelle, "art": b.art}
            for b in ergebnis.branchen
        ],
    }


anzeige = st.text_area(
    "Stellenanzeige",
    height=230,
    placeholder="Text der Stellenanzeige hier einfügen — Aufgaben und Anforderungen genügen.",
    label_visibility="collapsed",
)

spalte_a, spalte_b = st.columns([1, 2.4])
with spalte_a:
    los = st.button("Anzeige abgleichen", type="primary", use_container_width=True)
with spalte_b:
    semantik = st.toggle(
        "Semantischer Abgleich",
        value=True,
        help="Erkennt zusätzlich Umschreibungen, die nicht wörtlich in der Synonymliste stehen "
             "(z. B. „Aufbereitung großer Datenmengen“ → ETL). Der erste Aufruf lädt dafür ein "
             "kleines Sprachmodell.",
    )

if anzeige.strip():
    _einmal_zaehlen("eingabe_begonnen")

if los and not anzeige.strip():
    st.warning("Bitte zuerst den Text einer Stellenanzeige einfügen.")

if los and anzeige.strip():
    _einmal_zaehlen("pruefung_gestartet")
    if semantik:
        with st.spinner("Sprachmodell wird vorbereitet …"):
            _semantik_status()
    try:
        with st.spinner("Anforderungen werden abgeglichen …"):
            e = _auswerten(anzeige, semantik)
    except Exception:
        _einmal_zaehlen("fehler")
        st.error(
            "Bei der Auswertung ist etwas schiefgelaufen. Bitte den Text erneut "
            "einfügen — er wurde nirgends gespeichert."
        )
        st.stop()
    _einmal_zaehlen("auswertung_fertig")
    if semantik and not e["semantik_aktiv"]:
        _einmal_zaehlen("semantik_nicht_verfuegbar")

    st.markdown("---")

    if not e["belastbar"]:
        st.warning(
            "**Zu wenig Text für eine belastbare Aussage.** Aus dieser Anzeige liessen sich "
            "nur wenige Anforderungen herauslesen. Ein Messwert wäre hier irreführend — "
            "bitte den vollständigen Anzeigentext mit Aufgaben und Profil einfügen.",
            icon="📐",
        )
        if e["treffer"]:
            st.caption(
                "Was sich bereits zuordnen liess: "
                + ", ".join(t["label"] for t in e["treffer"])
            )
        st.stop()

    links, rechts = st.columns([1.05, 1])
    with links:
        st.markdown(messuhr(e["score"]), unsafe_allow_html=True)
        # Der Wert misst Abdeckung, nicht Einstellungschance. Diese Grenze gehört
        # unter die Zahl und nicht ins Kleingedruckte — sonst liest sie jemand als
        # Prognose, und das wäre sie nicht.
        st.caption(
            "Der Wert ist der Anteil der belegten an allen erkannten Anforderungen. "
            "Er sagt, wie weit das dokumentierte Profil die Anzeige abdeckt — nicht, "
            "ob eine Einladung daraus wird. Darüber entscheiden Berufsjahre, Team "
            "und Gespräch."
        )
    with rechts:
        pflicht_luecken = [l for l in e["luecken"] if l["pflicht"]]
        erfuellt = len(e["treffer"])
        # Wie viele Treffer sind mit öffentlich einsehbarem Code oder einer laufenden
        # Demo hinterlegt? Das ist die harte Währung — nicht der Prozentwert.
        mit_link = sum(
            1 for t in e["treffer"]
            if any(PROJEKTE.get(pk, {}).get("repo") for pk in t["projekte"])
        )
        erkannt = erfuellt + len(e["luecken"])
        st.markdown(f"### {erkannt} Anforderungen erkannt")
        st.markdown(
            f"**{erfuellt} davon belegt** — durch Zertifikate, Weiterbildungs"
            f"nachweise oder veröffentlichte Projekte."
        )
        if mit_link:
            st.markdown(
                f"**{mit_link}** davon sind mit öffentlichem Code oder einer "
                f"laufenden Demo verlinkt und damit direkt überprüfbar."
            )
        if pflicht_luecken:
            st.error(
                f"**{len(pflicht_luecken)} Muss-Anforderung"
                f"{'en' if len(pflicht_luecken) > 1 else ''} ohne Nachweis:** "
                + ", ".join(l["begriff"] for l in pflicht_luecken)
                + ". Diese Zahl steht bewusst neben dem Wert und nicht darin — ein hoher "
                "fachlicher Deckungsgrad ersetzt keine fehlende Pflichtanforderung.",
                icon="⚠️",
            )
        elif e["luecken"]:
            st.markdown(
                f"**{len(e['luecken'])}** Punkte sind nicht abgedeckt, alle als „wünschenswert“ "
                f"formuliert."
            )
        else:
            st.markdown("Keine Anforderung blieb unbeantwortet.")
        if e["score"] >= 95:
            st.caption(
                "Alle erkannten Anforderungen sind belegt. Mehr als 95 % zeigt diese App "
                "bewusst nicht an — fachliche Abdeckung ist nicht dasselbe wie Eignung."
            )

    if e["hinweis"]:
        st.info(e["hinweis"], icon="ℹ️")

    # ---------------- Treffer ----------------
    st.markdown("### Belegte Anforderungen")
    nach_kategorie: dict[str, list[dict]] = {}
    for t in e["treffer"]:
        nach_kategorie.setdefault(t["kategorie"], []).append(t)

    for kategorie, eintraege in nach_kategorie.items():
        st.markdown(f"**{kategorie}**")
        for t in eintraege:
            tags = ""
            if not t["pflicht"]:
                tags += '<span class="pm-tag">wünschenswert</span>'
            if t["semantisch"]:
                tags += '<span class="pm-tag">semantisch erkannt</span>'
            links_html = ""
            for pk in t["projekte"][:2]:
                p = PROJEKTE.get(pk)
                if not p:
                    continue
                links_html += (
                    f'<a href="{sichere_url(p["repo"])}" target="_blank" '
                    f'rel="noopener noreferrer">{_sicher(p["name"])} · Code</a>'
                )
                if p["demo"]:
                    links_html += (
                        f'<a href="{sichere_url(p["demo"])}" target="_blank" '
                        f'rel="noopener noreferrer">Live-Demo</a>'
                    )
            quote = ""
            if t["fundstellen"]:
                quote = (
                    f'<div class="pm-quote">Aus Ihrer Anzeige: '
                    f'„{_sicher(t["fundstellen"][0], 150)}“</div>'
                )
            st.markdown(
                f'<div class="pm-card"><b>{_sicher(t["label"])}</b>{tags}'
                f'<div class="pm-beleg">{_sicher(t["beleg"])}</div>{quote}'
                f'<div class="pm-links">{links_html}</div></div>',
                unsafe_allow_html=True,
            )

    # ---------------- Lücken ----------------
    if e["luecken"]:
        st.markdown("### Offen — und das sagen wir hier lieber direkt")
        for l in e["luecken"]:
            art = "als Muss formuliert" if l["pflicht"] else "als wünschenswert formuliert"
            quote = (
                f'<div class="pm-quote">Aus Ihrer Anzeige: '
                f'„{_sicher(l["fundstelle"], 150)}“</div>'
                if l["fundstelle"] else ""
            )
            st.markdown(
                f'<div class="pm-card pm-gap"><b>{_sicher(l["begriff"])}</b>'
                f'<span class="pm-tag">{art}</span>'
                f'<div class="pm-beleg">Dafür liegt kein Nachweis vor. Mesut arbeitet sich in neue '
                f'Werkzeuge schnell ein — behauptet hier aber keine Erfahrung, die er nicht hat.</div>'
                f'{quote}</div>',
                unsafe_allow_html=True,
            )

    # ---------------- Sprachen ----------------
    if e["sprachen"]:
        st.markdown("### Sprachanforderungen")
        for s in e["sprachen"]:
            if s["erfuellt"]:
                st.markdown(
                    f'<div class="pm-card"><b>{_sicher(s["sprache"])} {_sicher(s["gefordert"])}</b>'
                    f'<span class="pm-tag">erfüllt</span>'
                    f'<div class="pm-beleg">Vorhanden: {_sicher(s["vorhanden"])}. '
                    f'Die gesamte Projektdokumentation ist auf Deutsch verfasst.</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="pm-card pm-gap"><b>{_sicher(s["sprache"])}: gefordert {_sicher(s["gefordert"])}, '
                    f'vorhanden {_sicher(s["vorhanden"])}</b>'
                    f'<span class="pm-tag">separat ausgewiesen</span>'
                    f'<div class="pm-beleg">Das aktuelle Niveau steht so im Lebenslauf und wird '
                    f'hier nicht schöngerechnet. Fachliteratur und Dokumentation sind kein Problem, '
                    f'Verhandlungsniveau wird nicht behauptet. Diese Differenz geht nur mit '
                    f'geringem Gewicht in den Wert ein — sie ist eine Frage der Einarbeitung, '
                    f'keine fehlende Fachkompetenz.</div></div>',
                    unsafe_allow_html=True,
                )

    # ---------------- Standort & Arbeitsmodell ----------------
    if e["standort"]:
        s = e["standort"]
        st.markdown("### Standort und Arbeitsmodell")
        teile = []
        if s["orte"]:
            teile.append("Ort: " + ", ".join(s["orte"]))
        if s["modelle"]:
            teile.append("Modell: " + ", ".join(s["modelle"]))
        st.markdown(
            f'<div class="pm-card{"" if s["passt"] else " pm-gap"}">'
            f'<b>{_sicher(" · ".join(teile)) or "Angaben zum Einsatzort"}</b>'
            f'<span class="pm-tag">fliesst nicht in den Wert ein</span>'
            f'<div class="pm-beleg">{_sicher(s["begruendung"])} '
            f'Wohnort Neuwied; offen für Vor Ort und Hybrid in NRW, Rheinland-Pfalz '
            f'und Hessen sowie für Remote.</div></div>',
            unsafe_allow_html=True,
        )

    # ---------------- Branchenkontext ----------------
    if e["branchen"]:
        st.markdown("### Branchenkontext")
        belegt = [b["name"] for b in e["branchen"] if b["art"] == "belegt"]
        namen = [b["name"] for b in e["branchen"] if b["art"] == "branche"]
        regeln = [b["name"] for b in e["branchen"] if b["art"] == "regelwerk"]

        if belegt:
            st.markdown(
                f'<div class="pm-card"><b>{", ".join(belegt)} — direkte Erfahrung vorhanden</b>'
                f'<div class="pm-beleg">Diese Branche ist im Portfolio mit eigenen Projekten '
                f'belegt, nicht nur über übertragbare Methodik.</div></div>',
                unsafe_allow_html=True,
            )

        if namen or regeln:
            kopf = ", ".join(namen) if namen else "Branchenspezifisches Regelwerk"
            regel_satz = ""
            if regeln:
                regel_satz = (
                    f'<div class="pm-beleg" style="margin-top:.5rem">In Ihrer Anzeige genannt: '
                    f'<b>{", ".join(regeln)}</b> — dort als wünschenswert formuliert, daher hier '
                    f'und nicht unter den Lücken. Regelwerke sind Einarbeitung, keine Methodik; '
                    f'die durchgängig dokumentierte und reproduzierbare Arbeitsweise in den '
                    f'Projekten ist genau die Grundlage, die regulierte Umfelder verlangen.</div>'
                )
            st.markdown(
                f'<div class="pm-card"><b>{kopf}</b>'
                f'<span class="pm-tag">fliesst nicht in den Wert ein</span>'
                f'<div class="pm-beleg">{TRANSFER_SATZ}</div>{regel_satz}'
                f'<div class="pm-beleg" style="margin-top:.5rem">Belegte Branchen: '
                f'{" · ".join(BELEGTE_BRANCHEN)}.</div></div>',
                unsafe_allow_html=True,
            )

    if e["offene"]:
        with st.expander(f"Nicht eindeutig zugeordnet ({len(e['offene'])} Zeilen)"):
            st.caption(
                "Diese Zeilen liessen sich keiner Kompetenz sicher zuordnen. Sie fliessen nicht "
                "als Treffer in den Wert ein, dämpfen ihn aber leicht — eine Anzeige, die zu "
                "grossen Teilen unverstanden bleibt, soll kein hohes Ergebnis erzeugen."
            )
            for z in e["offene"]:
                st.text(f"• {z}")

    # ---------------- Kontakt ----------------
    st.markdown("### Interesse?")
    k1, k2 = st.columns(2)
    with k1:
        st.link_button(
            "Direkt schreiben",
            f"mailto:{PERSON['email']}?subject=Ihre%20Stellenanzeige%20%E2%80%93%20Kontaktaufnahme",
            use_container_width=True,
        )
    with k2:
        st.link_button("LinkedIn-Profil", PERSON["linkedin"], use_container_width=True)
    st.caption(
        f"{PERSON['titel']} · {PERSON['standort']} · "
        f"Deutsch C1, Englisch B1 · offen für Vor Ort und Hybrid in NRW, Rheinland-Pfalz "
        f"und Hessen sowie für Remote"
    )

else:
    st.caption(
        "Hinweis zum Datenschutz: Der eingefügte Text wird nur für die Dauer des Aufrufs "
        "im Arbeitsspeicher des Servers verarbeitet. Er wird nicht gespeichert, nicht "
        "protokolliert und an keinen externen Dienst gesendet. Der Abgleich läuft "
        "vollständig auf diesem Server; es wird kein Sprachmodell-Dienst aufgerufen."
    )

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### Wie der Wert entsteht")
    st.markdown(
        "1. Die Anzeige wird in einzelne Anforderungen zerlegt.\n"
        "2. Eine gepflegte Synonymliste ordnet jeder Anforderung eine Kompetenz zu — "
        "„BI-Reporting“ etwa Power BI.\n"
        "3. Für alles, was dabei offen bleibt, vergleicht ein mehrsprachiges Sprachmodell "
        "die Bedeutung statt der Wörter.\n"
        "4. Der Wert ist der **Anteil der belegten an allen erkannten Anforderungen**. "
        "Im Nenner stehen auch die nicht belegten und die nicht zuordenbaren — sonst "
        "käme jede Anzeige ohne ausdrückliche Lücke automatisch auf den Höchstwert.\n"
        "5. Gewichtung: nach Belegstärke; Muss-Anforderungen zählen doppelt so stark wie "
        "wünschenswerte. Geforderte Berufsjahre und Senior-Positionen werden mitgerechnet.\n"
        "6. Sprachniveaus und Branchenerfahrung stehen **separat** — eine Sprachlücke ist "
        "eine Frage der Einarbeitung und halbiert das fachliche Ergebnis nicht.\n"
        "7. Die Obergrenze liegt bei **95 %**: gemessen wird die fachliche Abdeckung, nicht "
        "die Gesamteignung. Ob jemand ins Team passt, entscheidet sich im Gespräch."
    )
    st.markdown("---")
    st.markdown("### Profil in Zahlen")
    st.markdown(
        f"- **{len(SKILLS)}** belegte Kompetenzen\n"
        f"- **{len(PROJEKTE)}** dokumentierte Projekte\n"
        f"- **{sum(1 for p in PROJEKTE.values() if p['demo'])}** davon mit Live-Demo\n"
        "- Physikstudium (B.Sc.), über zehn Jahre Lehrerfahrung\n"
        "- Data Analyst (IHK), Okt. 2026"
    )
    st.markdown("---")
    st.markdown(
        f"[Portfolio]({PERSON['portfolio']}) · [GitHub]({PERSON['github']}) · "
        f"[LinkedIn]({PERSON['linkedin']})"
    )

    # ------------------------------------------------------------------ Nutzungsbericht
    with st.expander("Nutzungsbericht"):
        try:
            erwartet = st.secrets.get("ADMIN_PASSWORT", "")
        except Exception:
            erwartet = ""
        if not erwartet:
            st.caption(
                "Kein Passwort hinterlegt. Zum Aktivieren `ADMIN_PASSWORT` in den "
                "Streamlit-Secrets setzen."
            )
        else:
            eingabe = st.text_input("Passwort", type="password", key="_admin_pw")
            if eingabe and eingabe == erwartet:
                daten = analytics.bericht(secrets=st.secrets)
                if not daten.get("_dauerhaft"):
                    st.warning(
                        "Die Zahlen liegen nur im Arbeitsspeicher dieses Prozesses. "
                        "Nach einem Ruhezustand oder einem neuen Deploy beginnen sie "
                        "wieder bei null. Für dauerhafte Zahlen `SUPABASE_URL` und "
                        "`SUPABASE_KEY` in den Secrets hinterlegen (siehe README).",
                        icon="⚠️",
                    )
                for zeitraum, titel in (
                    ("tag", "Heute"), ("woche", "Letzte 7 Tage"), ("monat", "Letzte 30 Tage")
                ):
                    werte = daten[zeitraum]
                    st.markdown(f"**{titel}**")
                    st.markdown(
                        f"- Sitzungen geöffnet: {werte['geoeffnet']}\n"
                        f"- davon Text eingefügt: {werte['eingabe_begonnen']}\n"
                        f"- davon Prüfung gestartet: {werte['pruefung_gestartet']}\n"
                        f"- davon Auswertung abgeschlossen: {werte['auswertung_fertig']}\n"
                        f"- geöffnet, aber nie geprüft: {werte['ohne_auswertung']}\n"
                        f"- Text eingefügt, aber nicht geprüft: {werte['eingabe_ohne_pruefung']}\n"
                        f"- ohne semantische Stufe: {werte['semantik_nicht_verfuegbar']}\n"
                        f"- Fehler: {werte['fehler']}"
                    )
                st.caption(
                    "Jede Zahl ist eine Zahl von **Sitzungen**, nicht von Personen und nicht "
                    "von Einzelauswertungen: Wer in derselben Sitzung eine zweite Anzeige "
                    "prüft, zählt weiterhin als eine Sitzung. Gespeichert werden nur Datum, "
                    "Ereignisname und Anzahl — kein Anzeigentext, keine Namen, keine "
                    "IP-Adressen."
                )
            elif eingabe:
                st.error("Passwort stimmt nicht.")

st.markdown(
    f'<div class="pm-foot">Gebaut von {PERSON["name"]} — Python, Streamlit und ein '
    f'mehrsprachiges Embedding-Modell. Der Quellcode liegt offen auf GitHub: wer wissen will, '
    f'wie der Wert zustande kommt, kann ihn nachlesen.<br>'
    f'Die Bewertung ist eine Orientierung, kein Urteil. Sie ersetzt kein Gespräch.</div>',
    unsafe_allow_html=True,
)
