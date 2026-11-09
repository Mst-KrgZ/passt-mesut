"""
Matching-Engine: vergleicht den Text einer Stellenanzeige mit dem belegten Kompetenzprofil.

Zwei Stufen:
  1. Lexikalischer Abgleich über eine gepflegte Synonymliste — präzise, sofort verfügbar
     und vollständig nachvollziehbar (jeder Treffer nennt den gefundenen Begriff).
  2. Semantischer Abgleich für Anforderungszeilen, die Stufe 1 nicht erfasst hat —
     ein mehrsprachiges Embedding-Modell erkennt Umschreibungen wie
     "Aufbereitung von Massendaten" → ETL.

Stufe 2 ist optional: Lässt sich das Modell nicht laden, arbeitet die App mit Stufe 1
weiter und sagt das im Interface offen.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from .profile_data import (
    BRANCHEN_SIGNAL,
    BRANCHEN_SKILLS,
    FREMDE_BRANCHEN,
    NICHT_VORHANDEN,
    REGELWERKE,
    SKILLS,
)

# Generische Analysephrasen: "Analyse von Produktionsdaten", "Auswertung der Netzdaten".
# Das Fachwort wechselt mit der Branche, die Tätigkeit bleibt dieselbe.
_ANALYSE_PHRASE = re.compile(
    r"\b(analyse|auswertung|aufbereitung|untersuchung|betrachtung)\s+(von\s+|der\s+|des\s+)?"
    r"[\wäöüß\- ]{0,40}daten\b",
    re.IGNORECASE,
)

# ----------------------------------------------------------------------------
# Textaufbereitung
# ----------------------------------------------------------------------------

_OPTIONAL_MARKER = re.compile(
    r"(wünschenswert|von vorteil|idealerweise|nice[- ]to[- ]have|plus\b|bonus|"
    r"erste erfahrung|grundkenntnisse|optional|gerne auch|kenntnisse in .{0,30} sind von vorteil|"
    # Ausdrückliche Verneinung: „(kein Muss)“, „nicht zwingend“, „keine Voraussetzung“
    r"kein\s*muss|nicht\s*zwingend|keine\s*voraussetzung|kein\s*erfordernis|"
    r"nicht\s*erforderlich|von\s*vorteil,?\s*aber\s*kein)",
    re.IGNORECASE,
)

# „SPSS oder Python“, „SQL bzw. R“ — eine erfüllte Alternative erledigt die Zeile.
_ALTERNATIVE = re.compile(r"\b(oder|bzw\.?|alternativ|wahlweise|beziehungsweise)\b", re.IGNORECASE)

# Eine Technologie gilt nur dann als Pflichtanforderung, wenn die Zeile sie auch
# verlangt. Wird sie bloss beschreibend erwähnt ("unsere Daten liegen in Azure"),
# ist das kein Muss — und darf das Ergebnis nicht unnötig drücken.
_FORDERUNG = re.compile(
    r"(kenntnis|erfahrung|erforderlich|vorausgesetzt|voraussetzung|beherrsch|vertraut|"
    r"sicherer umgang|sicher im umgang|routiniert|fundiert|versiert|zwingend|must[- ]have|"
    r"sie bringen mit|du bringst mit|idealerweise|wünschenswert|von vorteil|profil)",
    re.IGNORECASE,
)

# Sätze, die die Umgebung des Unternehmens beschreiben, nicht die Anforderung an die
# Bewerberin oder den Bewerber: „Unser Team nutzt Python“ verlangt kein Python.
_UMFELD = re.compile(
    r"\b(unser|unsere|unserem|unseren|wir)\b[^.\n;]{0,60}?"
    r"\b(nutzen|nutzt|setzen|setzt|arbeiten|arbeitet|verwenden|verwendet|einsetzen|"
    r"einsetzt|liegen|liegt|läuft|laufen|betreiben|betreibt|basiert|besteht)\b"
    r"|\b(zum einsatz|im einsatz|unser stack|unsere systeme|unsere landschaft|"
    r"technologiestack|tech[- ]stack|systemlandschaft|bei uns)\b",
    re.IGNORECASE,
)

# Reine Selbstdarstellung: „Wir sind …“, „Wir haben ein Umfeld geschaffen …“. Solche
# Sätze beschreiben den Arbeitgeber, nicht die Erwartung an die Bewerberin. Sie dürfen
# den Nenner nicht füllen — sonst bestraft ein ausführlicher Imagetext die Passung.
_SELBSTDARSTELLUNG = re.compile(
    r"^(?:[^.\n]{0,60}?\b)?(?:wir|unser\w*|uns)\b"
    r"(?![^.\n]*\b(sie|du|dich|dir|ihnen|ihre|deine)\b)"
    r"|^(als\s+\w+|bei uns|die von uns\w*|das von uns\w*)\b"
    r"(?![^.\n]*\b(sie|du|dich|dir|ihnen|ihre|deine)\b)",
    re.IGNORECASE,
)

# Aufzählung von Zusatzleistungen ohne Abschnittsüberschrift — Jobportale stellen sie
# oft als Stichwortzeile über die Anzeige („Firmenfahrrad-Leasing, Flexible Arbeitszeiten“).
_BENEFIT_LISTE = re.compile(
    r"\b(jobrad|firmenfahrrad|fahrradleasing|dienstrad|firmenwagen|fahrzeugleasing|"
    r"altersvorsorg\w*|urlaubstage|\d+\s*tage urlaub|gleitzeit|homeoffice|home[- ]office|"
    r"remote[- ]working|kantine|obstkorb|betriebssport|sportangebot|jobticket|"
    r"deutschlandticket|mitarbeiterrabatt\w*|corporate benefits|weihnachtsgeld|"
    r"urlaubsgeld|vermögenswirksame|weiterbildungsprogramm\w*|schulungsacademy|"
    r"gestaltungsfreiheit|unternehmenskultur|büroausstattung)\b",
    re.IGNORECASE,
)

# Satzform, die typisch für eine Anforderung ist, auch ohne Signalwort
_ANFORDERUNG_FORM = re.compile(
    r"\b(sie|du)\s+(verfügen|bringen|haben|besitzen|beherrschen|arbeiten|kennen)\b|"
    r"\b(abgeschlossene|abgeschlossenes|mehrjährige|fundierte|sichere|gute|sehr gute)\b",
    re.IGNORECASE,
)

_SECTION_OPTIONAL = re.compile(
    r"^(wünschenswert|wuenschenswert|nice[- ]to[- ]have|von vorteil|optional|"
    r"darüber hinaus|idealerweise|zusätzlich von vorteil)\s*:?\s*$",
    re.IGNORECASE,
)

# Abschnitte, deren Zeilen immer Anforderungen sind — unabhängig von Signalwörtern.
# Was unter „Deine Aufgaben“ oder „Dein Profil“ steht, verlangt die Stelle; es als
# unverbindlichen Fliesstext zu behandeln, schönt das Ergebnis.
_SECTION_ANFORDERUNG = re.compile(
    r"^(ihre|deine|ihr|dein)?\s*(aufgaben|profil|qualifikation\w*|anforderung\w*|"
    r"verantwortung\w*|tätigkeit\w*|aufgabengebiet|das bringen sie mit|"
    r"das bringst du mit|was sie mitbringen|was du mitbringst|damit überzeugen sie uns|"
    r"das zeichnet sie aus|das macht dich aus|das erwartet (sie|dich)|"
    r"so (kann|sieht) (deine|ihre) (arbeitswoche|woche|arbeit)|"
    r"das bringst du (idealerweise )?mit|das bringen sie (idealerweise )?mit|"
    r"dein alltag|ihr alltag|deine rolle|ihre rolle)\b",
    re.IGNORECASE,
)

# Abschnitte, die nichts verlangen — Benefits, Unternehmensvorstellung, Bewerbungsweg
_SECTION_NEUTRAL = re.compile(
    r"^(?:ihre|deine|unsere|unser|dein|ihr|was)?\s*"
    r"(vorteile|benefits|wir bieten|wir dir bieten|bieten wir|angebot|"
    r"über uns|unternehmen|kontakt|bewerbung|ansprechpartner|ansprechperson|"
    r"das sind wir|warum wir|weg zu uns|das erwartet (?:dich|sie)|"
    r"rahmenbedingungen|arbeitgeber|leistungen|zusatzleistungen)\b",
    re.IGNORECASE,
)

# Signalwörter dafür, dass eine Zeile Erfahrungsquellen aufzählt statt zu fordern.
_ERFAHRUNGSQUELLE = re.compile(
    r"\b(etwa durch|durch|z\.\s?b\.|beispielsweise|erworben|gesammelt|"
    r"gerne auch|auch aus|sei es|ob durch|erste erfahrung\w*|vorerfahrung\w*)\b",
    re.IGNORECASE,
)

# Stellen, die ein laufendes Studium voraussetzen — Praktikum, Werkstudium, duales
# Studium. Das ist kein Kompetenzthema, sondern eine formale Hürde: Mesut studiert nicht.
_STUDIERENDEN_STELLE = re.compile(
    r"\b(während deines studiums|während ihres studiums|für dein studium|"
    r"immatrikuliert|eingeschrieben\w*\s+(an|student)|werkstudent\w*|duales studium|"
    r"dualer student|pflichtpraktikum|praxissemester|studienbegleitend|"
    r"notenschnitt im studium|noch mindestens \d+ semester)\b",
    re.IGNORECASE,
)

# Überschriften, die wieder in den Pflichtteil zurückführen
_SECTION_PFLICHT = re.compile(
    r"^(ihr profil|dein profil|das bringen sie mit|das bringst du mit|anforderungen|"
    r"ihre qualifikation|zwingend erforderlich|must[- ]have|voraussetzungen)\s*:?\s*$",
    re.IGNORECASE,
)

_NOISE = re.compile(
    r"^(wir bieten|unser angebot|benefits|deine vorteile|ihre vorteile|das bieten wir|"
    r"über uns|unternehmen|kontakt|bewerbung|haben wir dein interesse|dein ansprechpartner|"
    r"standort|einsatzort|arbeitsort|vollzeit|teilzeit|stellen-?id|kennziffer|referenznummer|"
    r"ihre aufgaben|deine aufgaben|ihr profil|dein profil|das bringen sie mit|das bringst du mit|"
    r"ihre qualifikation|anforderungen|was dich erwartet|was wir erwarten)",
    re.IGNORECASE,
)

# Oberfläche von Jobportalen und Bewerbungsfloskeln. Diese Zeilen werden VOR der
# Abschnittserkennung verworfen: Indeeds Widget „Qualifikationen: 5 von 9“ hat sonst
# die gesamte Anzeige zum Anforderungsteil erklärt und den Nenner gefüllt.
_PORTAL = re.compile(
    r"^\s*(?:"
    r"weiter zur bewerbung|jetzt bewerben|vollständige stellenbeschreibung|"
    r"stellenbeschreibung\s*$|keine gehaltsinformationen|befristeter vertrag|"
    r"übersicht über die übereinstimmung|hier sehen sie einen abgleich|"
    r"qualifikationen:\s*\d|\+\s*\d+\s*weitere|teilen|merken|"
    # LinkedIn
    r"vor \d+ (minute|stunde|tag|woche|monat)|einfach bewerben|speichern$|"
    r"noch keine insights|sie sind (kaum|gut|sehr gut) für diesen job|"
    r"in ihrem profil und lebenslauf fehlen|details zur eignung|"
    r"haben ihnen diese informationen|\d+ bewerber|unternehmenslogo|"
    r"details zum jobangebot$|sehen sie sich (die details|weitere jobs)|"
    r"vom arbeitgeber gesponsert|außerhalb von linkedin|ausserhalb von linkedin|"
    r"mehr als \d+ personen|\d+ personen haben auf|mit ki ihre eignung|"
    r"derzeit werden keine bewerbungen|personen, die sie kontaktieren|"
    r"und weitere kontakte|alle anzeigen$|erneut veröffentlicht|"
    r"ihr profil (passt|stimmt)|bewerbungsfrist|jetzt schnell bewerben|"
    r"erschienen:|veröffentlicht:|aktualisiert:|\d[\d.]*\s*€\s*-|"
    r"passt (hervorragend|weniger|gut|teilweise)|du erfüllst alle anforderungen|"
    r"basierend auf \S+\.(docx|pdf)|slide number|\S+ logo$|"
    r"feste anstellung|homeoffice möglich|bitte reiche deine bewerbung|"
    r"bewerbungen, die per e-?mail|ansprechpartner:|recruiting ?prozess$|"
    # Schluss- und Bewerbungsfloskeln
    r"wir freuen uns (auf|über)|bei fragen (steht|wenden)|"
    r"wir haben (dein|ihr) interesse|haben wir (dein|ihr) interesse|"
    r"dann starte durch|interessiert\?|neugierig geworden|"
    r"werde (teil|mitarbeiter)|bewirb dich|senden sie (uns|ihre)|"
    r"für (unser\w*)\b[^.\n]{0,40}?suchen wir|"
    r"wir suchen\b[^.\n]{0,40}?zum nächstmöglichen"
    r")",
    re.IGNORECASE,
)

# Stellentitel wie "Data Analyst (m/w/d) – Vertriebssteuerung"
_TITEL = re.compile(
    r"\(\s*(gn|g\*n|m[/|]w[/|]d|w[/|]m[/|]d|d[/|]m[/|]w|m[/|]f[/|]d|a\*|"
    r"[mwdfx]\s*[/|]\s*[mwdfx](\s*[/|]\s*[mwdfx])?)\s*\)",
    re.IGNORECASE,
)

# Geforderte Berufsjahre: "mindestens 3 Jahre Berufserfahrung", "5+ Jahre Erfahrung"
_JAHRE = re.compile(
    r"(?:mind(?:estens)?\.?\s*)?(\d{1,2})\s*\+?\s*(?:bis\s*\d{1,2}\s*)?jahre?\b[^.\n]{0,60}?"
    r"(berufserfahrung|erfahrung|praxis)",
    re.IGNORECASE,
)

# Jahresforderung in Worten statt in Zahlen. „Mehrjährige Erfahrung in
# Softwareentwicklungsprojekten“ ist genauso eine Hürde wie „3 Jahre Erfahrung“ —
# sie nicht zu erkennen hiesse, die häufigste Formulierung zu übersehen.
_JAHRE_WORT = re.compile(
    r"\b(mehrjährig\w*|langjährig\w*|mehrere jahre|einige jahre)\b"
    r"[^.\n]{0,70}?(berufserfahrung|erfahrung|praxis|tätigkeit)"
    r"|\b(berufserfahrung|erfahrung)\b[^.\n]{0,30}?\b(mehrjährig\w*|langjährig\w*)\b",
    re.IGNORECASE,
)

# Seniorität, die ein Quereinsteiger mit sieben Monaten Praxis nicht behaupten kann
_SENIOR = re.compile(
    r"\b(senior|lead\s|teamlead|head of|principal|expert[ei]n?\s|führungserfahrung|"
    r"personalverantwortung|disziplinarische)\b",
    re.IGNORECASE,
)

# Tatsächliche einschlägige Berufspraxis in Monaten (IME-Praktikum Aug. 2025 – Feb. 2026)
PRAXIS_MONATE = 7

# Eine Teilanforderung innerhalb einer Zeile: „SQL, Power BI und Spark“ sind drei
# Anforderungen, nicht eine. Sonst verschwindet das Unerfüllte hinter dem Erfüllten.
_TEILUNG = re.compile(r",|;|\bsowie\b|\bund\b|\boder\b|/", re.IGNORECASE)

# Orte und Arbeitsmodelle — getrennt ausgewiesen, nie im Score
ERREICHBARE_REGIONEN = {
    "nrw", "nordrhein-westfalen", "rheinland-pfalz", "hessen", "koblenz", "köln", "bonn",
    "neuwied", "düsseldorf", "frankfurt", "wiesbaden", "mainz", "siegburg", "wetzlar",
    "leverkusen", "aachen", "dortmund", "essen", "duisburg", "limburg", "montabaur",
    "andernach", "bad honnef", "troisdorf", "hennef", "remagen", "sinzig", "mendig",
    "darmstadt", "offenbach", "hanau", "gießen", "marburg", "fulda", "kassel",
    "trier", "kaiserslautern", "ludwigshafen", "worms", "bingen", "bad kreuznach",
    "neuss", "mönchengladbach", "krefeld", "wuppertal", "solingen", "bergisch gladbach",
    "euskirchen", "brühl", "hürth", "pulheim", "bornheim", "königswinter",
}
FERNE_ORTE = {
    "münchen", "hamburg", "berlin", "stuttgart", "nürnberg", "leipzig", "dresden",
    "bremen", "hannover", "kiel", "rostock", "freiburg", "karlsruhe", "augsburg",
    "regensburg", "münster", "osnabrück", "wien", "zürich", "basel",
}
_MODELLE = {
    "remote": "Remote", "homeoffice": "Homeoffice", "home office": "Homeoffice",
    "hybrid": "Hybrid", "vor ort": "Vor Ort", "präsenz": "Vor Ort",
    "mobiles arbeiten": "Mobiles Arbeiten",
}

# Sprachniveaus: aktueller Stand laut Zeugnissen, nicht laut früherer Selbsteinschätzung.
NIVEAU_RANG = {"a1": 1, "a2": 2, "b1": 3, "b2": 4, "c1": 5, "c2": 6}
EIGENE_SPRACHEN = {"deutsch": "C1", "englisch": "B1", "türkisch": "C2"}

SPRACHNAMEN = ["deutsch", "englisch", "französisch", "spanisch", "niederländisch"]

# Häufige englische Funktionswörter. Die Synonymliste ist deutsch; bei einer
# englischen Anzeige findet sie nur vereinzelt Technologienamen und würde daraus
# einen hohen Wert auf winziger Grundlage bilden. Das wäre irreführend.
_ENGLISCH = re.compile(
    r"\b(you|your|we|our|the|and|with|for|will|have|are|is|of|to|in|as|"
    r"experience|skills|team|role|work|about|join|apply)\b",
    re.IGNORECASE,
)
_DEUTSCH = re.compile(
    r"\b(und|oder|mit|für|die|der|das|sie|du|wir|uns|ihre|deine|ein|eine|"
    r"erfahrung|kenntnisse|aufgaben|profil|bieten|suchen|arbeiten)\b",
    re.IGNORECASE,
)


def ist_englisch(text: str) -> bool:
    """Überwiegt Englisch deutlich, ist das deutsche Wörterbuch nicht anwendbar."""
    en = len(_ENGLISCH.findall(text))
    de = len(_DEUTSCH.findall(text))
    return en >= 12 and en > de * 2


def _belastbar(treffer, luecken, zeilen, anzeige: str) -> bool:
    """Reicht die Grundlage für einen Prozentwert?

    Ein Wert aus zwei erkannten Punkten ist keine Aussage, sondern Zufall: Wer einen
    Lebenslauf oder einen englischen Text einfügt, bekäme sonst 95 % auf winziger
    Grundlage. Verlangt werden deshalb genug erkannte Anforderungen UND genug
    Zeilen, die überhaupt nach einer Anforderungsliste aussehen.
    """
    if ist_englisch(anzeige):
        return False
    # Genug erkannte Anforderungen sind die Grundlage. Die Zeilenzahl ist nur ein
    # Hilfsmaß und darf eine gut erkannte Anzeige nicht verwerfen.
    erkannt = len(treffer) + len(luecken)
    return erkannt >= 5


def _satz_um(text: str, start: int, ende: int) -> str:
    """Der Satz, in dem eine Fundstelle steht — für Zusatzsignale wie „zwingend“."""
    links = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    rechts = min(
        x for x in (text.find(".", ende), text.find("\n", ende), len(text)) if x != -1
    )
    return text[links + 1:rechts]


# Formulierungen, die ein Sprachniveau ausdrücklich zur Bedingung machen.
# Nur nachdrückliche Formulierungen gelten als Ausschluss. Ein blosses „erforderlich“
# steht in deutschen Anzeigen hinter fast jedem Profilpunkt und sagt nichts über die
# Härte der Anforderung — „zwingend“ oder „vorausgesetzt“ dagegen schon.
_SPRACHE_ZWINGEND = re.compile(
    r"\b(zwingend|zwingende\w*|vorausgesetzt|voraussetzung|unabdingbar|"
    r"unerlässlich|verpflichtend|must[- ]have|k\.?\s?o\.?[- ]kriterium|"
    r"unbedingt erforderlich|absolut notwendig)\b",
    re.IGNORECASE,
)

# Pro Sprache einzeln suchen. Ein gemeinsamer Ausdruck verschluckt sonst die zweite
# Sprache in Sätzen wie „Deutsch und Englisch verhandlungssicher“.
_SPRACHE = {
    name: re.compile(
        rf"\b{name}\w*\b[^.\n;]{{0,60}}?"
        r"(\b[abc][12]\b|verhandlungssicher|fliessend|fließend|muttersprach|sehr gut|"
        r"\bgut\b|grundkenntnis)",
        re.IGNORECASE,
    )
    for name in SPRACHNAMEN
}

# Umgekehrte Reihenfolge: „Sehr gute Deutschkenntnisse“, „verhandlungssicheres Englisch“
_SPRACHE_VORAN = {
    name: re.compile(
        r"(\b[abc][12]\b|verhandlungssicher\w*|fliessend\w*|fließend\w*|"
        rf"sehr gute?\w*|gute?\w*|grundkenntnis\w*)[^.\n;]{{0,25}}?\b{name}\w*",
        re.IGNORECASE,
    )
    for name in SPRACHNAMEN
}

# „Deutsch und Englisch verhandlungssicher“ — das Niveau steht hinter beiden Sprachen
_SPRACHE_PAAR = re.compile(
    r"\b(deutsch|englisch|französisch|spanisch)\w*\s+und\s+(deutsch|englisch|französisch|spanisch)\w*"
    r"[^.\n;]{0,40}?"
    r"(\b[abc][12]\b|verhandlungssicher|fliessend|fließend|sehr gut|\bgut\b)",
    re.IGNORECASE,
)

_NIVEAU_WORT = {
    "muttersprach": "C2", "verhandlungssicher": "C1", "fliessend": "C1", "fließend": "C1",
    "sehr gut": "C1", "gut": "B2", "grundkenntnis": "A2",
}


def _normalise(text: str) -> str:
    """
    Kleinschreibung, Satzzeichen zu Leerzeichen.

    Umlaute bleiben erhalten; zusätzlich werden die Umschreibungen ae/oe/ue/ss auf
    Umlaute zurückgeführt. Kopierte Anzeigen enthalten je nach Quelle „München“ oder
    „Muenchen“, und beides soll gefunden werden.
    """
    text = unicodedata.normalize("NFC", text.lower())
    text = re.sub(r"[^\wäöüß/+#.\- ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    ersetzt = (
        text.replace("muenchen", "münchen").replace("koeln", "köln")
        .replace("duesseldorf", "düsseldorf").replace("osnabrueck", "osnabrück")
        .replace("zuerich", "zürich").replace("muenster", "münster")
        .replace("nuernberg", "nürnberg").replace("datenqualitaet", "datenqualität")
        .replace("qualitaet", "qualität").replace("praesentation", "präsentation")
        .replace("auswertungen", "auswertungen").replace("wuenschenswert", "wünschenswert")
        .replace("verfuegen", "verfügen").replace("einschlaegig", "einschlägig")
        .replace("fuer", "für").replace("ueber", "über").replace("moeglich", "möglich")
    )
    return f" {ersetzt} "


def split_requirements(text: str) -> list[str]:
    """Zerlegt die Anzeige in einzelne Anforderungszeilen (ohne Abschnittsinfo)."""
    return [z for z, _, _ in split_requirements_markiert(text)]


# Firmenbezeichnungen: „FTSolutions OHG, Wetzlar“ ist eine Absenderzeile, keine
# Anforderung. Nur in kurzen Zeilen angewandt, damit echte Sätze erhalten bleiben.
_RECHTSFORM = re.compile(
    r"(?<![\wäöüß])(?:gmbh|mbh|ohg|kgaa|kg|ag|se|gbr|ug|e\.?\s?v|e\.?\s?k|"
    r"co\.?\s?kg|partg|inc|ltd|llc|plc|b\.?v|s\.?a)(?![\wäöüß])", re.IGNORECASE)


# Zeile, die wie eine Abschnittsüberschrift aussieht: kurz, ohne Satzende, oft mit
# Doppelpunkt. Dient nur dazu, einen neutralen Abschnitt zu beenden.
_IST_UEBERSCHRIFT = re.compile(
    r"^(?:[A-ZÄÖÜ][^.!?]{0,60})(?::|\s*$)"
)


def _entmarkiere(line: str) -> str:
    """Markdown- und Icon-Reste aus Portal-Exporten entfernen.

    StepStone-Exporte liefern Zeilen wie „#### Ihre Aufgaben“, „**Deine Aufgaben“
    oder „svgErschienen: vor 1 Woche“. Ohne Bereinigung greift die
    Abschnittserkennung nicht und die Zeile landet als Anforderung im Nenner.
    """
    line = re.sub(r"&#x[0-9a-fA-F]+;|&[a-z]{2,8};", " ", line)
    line = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", line)      # Markdown-Links
    line = line.replace("\\", " ")
    line = re.sub(r"^\s*(?:#{1,6}|>|\|)\s*", "", line)
    line = re.sub(r"^\s*svg(?=[A-ZÄÖÜ#*]|\s)", "", line)         # Icon-Platzhalter
    line = line.replace("**", "").replace("__", "")
    line = re.sub(r"\s{2,}", " ", line)
    return line.strip(" \t-*·•…:|")


def split_requirements_markiert(text: str) -> list[tuple[str, bool, bool]]:
    """
    Wie oben, liefert zusätzlich je Zeile, ob sie in einem optionalen Abschnitt steht.

    Die Überschrift „Wünschenswert:“ wird selbst herausgefiltert — ihre Wirkung muss
    deshalb vor dem Filtern festgehalten werden, sonst gelten die Punkte darunter
    fälschlich als Pflicht.
    """
    raw = re.split(r"[\n\r•·▪–—]|(?<=[.!?;])\s+(?=[A-ZÄÖÜ])", text)
    out: list[tuple[str, bool, bool]] = []
    im_optionalen_abschnitt = False
    im_anforderungsteil = False
    im_neutralen_abschnitt = False
    for line in raw:
        line = _entmarkiere(line)
        if not line:
            continue
        if _PORTAL.match(line):     # Oberfläche des Jobportals, kein Anzeigeninhalt
            continue
        # Abschnittsüberschriften steuern den Zustand und fliegen danach raus — sie
        # sind Navigation, keine Anforderung, und dürfen den Nenner nicht füllen.
        if _SECTION_ANFORDERUNG.match(line):
            im_anforderungsteil = True
            im_neutralen_abschnitt = False
            if len(line.split()) <= 8:
                continue
        elif _SECTION_NEUTRAL.match(line):
            im_anforderungsteil = False
            im_neutralen_abschnitt = True
            if len(line.split()) <= 8:
                continue
        elif im_neutralen_abschnitt and _IST_UEBERSCHRIFT.match(line):
            # Eine neue Überschrift beendet den neutralen Teil, auch wenn die Liste
            # ihre Formulierung nicht kennt („Deine Mission bei uns:“).
            im_neutralen_abschnitt = False
            if len(line.split()) <= 8:
                continue
        if _SECTION_OPTIONAL.match(line):
            im_optionalen_abschnitt = True
            continue
        if _SECTION_PFLICHT.match(line):
            im_optionalen_abschnitt = False
            # Überschrift selbst fliegt unten über _NOISE raus
        if len(line) < 12 or len(line) > 400:
            continue
        if _NOISE.match(line):
            continue
        if line.endswith(":"):          # Zwischenüberschrift
            continue
        # Überschrift in Versalien („DAS ERWARTET DICH“, „IHRE AUFGABEN“)
        buchstaben = [z for z in line if z.isalpha()]
        if buchstaben and sum(z.isupper() for z in buchstaben) / len(buchstaben) > 0.85:
            continue
        if _TITEL.search(line):         # Stellentitel
            continue
        if len(line.split()) <= 5 and _RECHTSFORM.search(line):   # Firmen-/Standortzeile
            continue
        if len(line.split()) < 3:       # Stichwortzeile ohne Aussage
            continue
        if im_neutralen_abschnitt:      # Benefits, Über uns, Bewerbungsweg
            continue
        out.append((line, im_optionalen_abschnitt, im_anforderungsteil))
    return out


# Begriffe, bei denen ein vorangestellter Wortteil die Bedeutung kippt. „Dokumentation“
# ist Projektdokumentation — „Transferpreisdokumentation“ ist Steuerrecht und hat damit
# nichts zu tun. Für diese Wörter gilt weiterhin die strenge Wortgrenze.
_KEIN_KOMPOSITUM = {
    "dokumentation", "entwicklung", "management", "beratung", "prozess", "planung",
    "steuerung", "betreuung", "verwaltung", "bewertung", "erfassung", "kalkulation",
    "abstimmung", "spezifikation",
}


def _strenges_muster(begriff: str) -> re.Pattern:
    """
    Wortgenaue Suche ohne vorangestellten Wortteil.

    Für Branchennamen, Regelwerke und Orte: „Ausbildung“ enthält „Bildung“, ist aber
    nicht die Bildungsbranche. Hier darf die Kompositum-Regel nicht greifen.
    """
    escaped = re.escape(begriff.strip()).replace(r"\ ", r"[\s\-]+")
    endung = r"[a-zäöüß]{0,3}" if len(begriff) >= 5 and begriff[-1].isalpha() else ""
    return re.compile(rf"(?<![\wäöüß]){escaped}{endung}(?![\wäöüß])", re.IGNORECASE)


def _alias_pattern(alias: str) -> re.Pattern:
    """
    Baut das Suchmuster für einen Begriff.

    Deutsch flektiert: „Datenmodell“ steht in Anzeigen als „Datenmodellen“, „Dashboard“
    als „Dashboards“, „Analyse“ als „Analysen“. Ein starres Wortende würde all das
    übersehen. Deshalb sind bei ausreichend langen Begriffen bis zu drei Buchstaben
    Endung erlaubt. Kurze Begriffe (SQL, ML, R, KI) bleiben streng, damit sie nicht
    versehentlich in anderen Wörtern auftauchen.
    """
    kern = alias.strip()
    escaped = re.escape(kern).replace(r"\ ", r"[\s\-]+")
    endung = r"[a-zäöüß]{0,3}" if len(kern) >= 5 and kern[-1].isalpha() else ""
    # Deutsche Komposita setzen den bekannten Begriff oft ans Ende:
    # „Erfolgskennzahlen“, „Vertriebsreporting“, „Fachkenntnisse“, „Fehleranalyse“.
    # Ab sieben Zeichen ist ein vorangestellter Wortteil erlaubt. Kurze Begriffe
    # (SQL, Excel, Python) bleiben streng, sonst träfe „SQL“ auch in „NoSQL“.
    erlaubt = len(kern) >= 7 and kern[0].isalpha() and kern not in _KEIN_KOMPOSITUM
    vorsilbe = r"(?:[a-zäöüß]{2,18}-?)?" if erlaubt else ""
    return re.compile(
        rf"(?<![\wäöüß]){vorsilbe}{escaped}{endung}(?![\wäöüß])", re.IGNORECASE
    )


_PATTERNS = {
    s["key"]: [(a, _alias_pattern(a)) for a in s["aliases"]] for s in SKILLS
}
_GAP_PATTERNS = {k: _alias_pattern(k) for k in NICHT_VORHANDEN}


# ----------------------------------------------------------------------------
# Ergebnisstrukturen
# ----------------------------------------------------------------------------

@dataclass
class Treffer:
    skill: dict
    fundstellen: list[str] = field(default_factory=list)
    begriffe: list[str] = field(default_factory=list)
    semantisch: bool = False
    pflicht: bool = True

    @property
    def gewicht(self) -> float:
        g = self.skill["staerke"] / 5.0
        if not self.pflicht:
            g *= 0.5
        # Ein semantischer Treffer ist eine Ähnlichkeit, kein Nachweis über ein
        # bekanntes Synonym. Er darf nicht so schwer wiegen wie ein wörtlicher —
        # sonst hebt eine Fehlzuordnung des Modells den Wert wie ein echter Beleg.
        if self.semantisch:
            g *= 0.7
        return g


@dataclass
class Luecke:
    begriff: str
    fundstelle: str
    pflicht: bool = True

    @property
    def gewicht(self) -> float:
        return 1.0 if self.pflicht else 0.4


@dataclass
class Standort:
    """Ort und Arbeitsmodell aus der Anzeige — getrennt ausgewiesen, nie im Score."""
    orte: list[str] = field(default_factory=list)
    modelle: list[str] = field(default_factory=list)
    passt: bool | None = True   # None = nicht beurteilbar
    begruendung: str = ""


@dataclass
class Sprachbedarf:
    sprache: str
    gefordert: str
    vorhanden: str
    erfuellt: bool
    fundstelle: str = ""
    zwingend: bool = False

    @property
    def gewicht(self) -> float:
        # Eine Sprachanforderung oberhalb des eigenen Niveaus ist normalerweise kein
        # K.-o.-Kriterium: Sie zählt schwächer als eine fehlende Kernkompetenz.
        # Schreibt die Anzeige das Niveau aber ausdrücklich als zwingend vor, ist es
        # eine formale Hürde wie ein gefordertes Studium — dann wiegt sie voll.
        if self.erfuellt:
            return 0.0
        return 2.5 if self.zwingend else 0.6


@dataclass
class Branche:
    name: str
    fundstelle: str = ""
    art: str = "branche"   # "branche", "belegt" oder "regelwerk"


@dataclass
class Ergebnis:
    score: int
    treffer: list[Treffer]
    luecken: list[Luecke]
    offene_zeilen: list[str]
    semantik_aktiv: bool
    hinweis: str = ""
    branchen: list[Branche] = field(default_factory=list)
    sprachen: list[Sprachbedarf] = field(default_factory=list)
    standort: Standort | None = None
    umgebung: list[Branche] = field(default_factory=list)
    pflicht_luecken: int = 0
    belastbar: bool = True


# ----------------------------------------------------------------------------
# Semantische Stufe
# ----------------------------------------------------------------------------

_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_embedder = None
_skill_vectors = None
_semantik_fehler = ""


def _skill_text(skill: dict) -> str:
    return f"{skill['label']}. {', '.join(skill['aliases'][:10])}. {skill['beleg']}"


def lade_semantik():
    """Lädt das Embedding-Modell einmalig. Gibt (ok, fehlermeldung) zurück."""
    global _embedder, _skill_vectors, _semantik_fehler
    if _embedder is not None:
        return True, ""
    if _semantik_fehler:
        return False, _semantik_fehler
    try:
        import numpy as np
        from fastembed import TextEmbedding

        _embedder = TextEmbedding(model_name=_MODEL_NAME)
        texte = [_skill_text(s) for s in SKILLS]
        vecs = np.array(list(_embedder.embed(texte)), dtype="float32")
        vecs /= (np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9)
        _skill_vectors = vecs
        return True, ""
    except Exception as exc:  # pragma: no cover - abhängig von der Laufzeitumgebung
        _embedder = None
        _semantik_fehler = f"{type(exc).__name__}: {exc}"
        return False, _semantik_fehler


def _semantische_treffer(
    zeilen: list[str], schwelle: float = 0.48, abstand: float = 0.04
):
    """Ordnet offenen Zeilen die nächstliegende Kompetenz zu.

    Zwei Bedingungen, nicht nur eine: Die Ähnlichkeit muss über der Schwelle liegen
    UND erkennbar über der zweitbesten Kompetenz. Liegen die beiden gleichauf, ist
    die Zuordnung Zufall — „Feature-Test“ landet sonst bei „A/B-Testing“, weil in
    beiden das Wort Test vorkommt.
    """
    import numpy as np

    if not zeilen or _embedder is None or _skill_vectors is None:
        return {}, zeilen

    qv = np.array(list(_embedder.embed(list(zeilen))), dtype="float32")
    qv /= (np.linalg.norm(qv, axis=1, keepdims=True) + 1e-9)
    sim = qv @ _skill_vectors.T

    zuordnung: dict[str, list[str]] = {}
    offen: list[str] = []
    for i, zeile in enumerate(zeilen):
        reihe = sim[i]
        j = int(reihe.argmax())
        bester = float(reihe[j])
        zweiter = float(np.partition(reihe, -2)[-2]) if reihe.size > 1 else 0.0
        if bester >= schwelle and (bester - zweiter) >= abstand:
            zuordnung.setdefault(SKILLS[j]["key"], []).append(zeile)
        else:
            offen.append(zeile)
    return zuordnung, offen


def _ohne_portal(text: str) -> str:
    """Rohtext ohne die Oberfläche des Jobportals.

    Für die Kompetenzsuche zählt der ganze Anzeigentext, auch kurze Zeilen und
    Überschriften — anders als bei der Anforderungszählung darf hier nichts
    wegfallen. Entfernt wird nur, was das Portal selbst beisteuert: LinkedIns
    „Mit KI Ihre Eignung ermitteln“ hat sonst die Kompetenz GenAI belegt.
    """
    behalten = []
    for zeile in text.splitlines():
        sauber = _entmarkiere(zeile)
        if sauber and _PORTAL.match(sauber):
            continue
        behalten.append(zeile)
    return "\n".join(behalten)


# ----------------------------------------------------------------------------
# Hauptfunktion
# ----------------------------------------------------------------------------

def analysiere(anzeige: str, semantik: bool = True) -> Ergebnis:
    markiert = split_requirements_markiert(anzeige)
    zeilen = [z for z, _, _ in markiert]
    optional_flags = [opt for _, opt, _ in markiert]
    anforderungs_flags = [anf for _, _, anf in markiert]
    volltext = _normalise(_ohne_portal(anzeige))

    def ist_pflicht(zeile: str, idx: int | None = None) -> bool:
        if idx is not None and 0 <= idx < len(optional_flags) and optional_flags[idx]:
            return False
        if _OPTIONAL_MARKER.search(zeile):
            return False
        return True

    # --- Stufe 1: lexikalisch ---
    # Eine Kompetenz zählt nur dann als Treffer, wenn sie in einer Zeile steht, die eine
    # Anforderung oder Aufgabe beschreibt. Nennt die Anzeige sie bloss als Umgebung des
    # Unternehmens („unser Team nutzt Python“), ist das keine Anforderung an die Person —
    # und darf das Ergebnis nicht nach oben ziehen. Dieselbe Trennung gilt weiter unten
    # für nicht vorhandene Technologien; sie muss in beide Richtungen gleich sein.
    umfeld_zeilen = {i for i, z in enumerate(zeilen) if _UMFELD.search(z)}

    treffer: dict[str, Treffer] = {}
    nur_umfeld: dict[str, str] = {}
    erfasste_zeilen: set[int] = set()

    for skill in SKILLS:
        gefunden_begriffe: list[str] = []
        gefunden_zeilen: list[str] = []
        umfeld_fundstelle = ""
        pflicht = False
        for alias, pattern in _PATTERNS[skill["key"]]:
            if not pattern.search(volltext):
                continue
            treffer_in_anforderung = False
            for idx, zeile in enumerate(zeilen):
                if not pattern.search(_normalise(zeile)):
                    continue
                if idx in umfeld_zeilen:
                    umfeld_fundstelle = umfeld_fundstelle or zeile
                    erfasste_zeilen.add(idx)
                    continue
                treffer_in_anforderung = True
                if zeile not in gefunden_zeilen:
                    gefunden_zeilen.append(zeile)
                erfasste_zeilen.add(idx)
                if ist_pflicht(zeile, idx):
                    pflicht = True
            # Steht der Begriff nur im Fliesstext ohne eigene Zeile, zählt er weiterhin.
            if treffer_in_anforderung or not umfeld_fundstelle:
                gefunden_begriffe.append(alias.strip())
        if gefunden_begriffe and (gefunden_zeilen or not umfeld_fundstelle):
            treffer[skill["key"]] = Treffer(
                skill=skill,
                fundstellen=gefunden_zeilen[:3],
                begriffe=sorted(set(gefunden_begriffe), key=len, reverse=True)[:4],
                pflicht=pflicht or not gefunden_zeilen,
            )
        elif umfeld_fundstelle:
            nur_umfeld[skill["label"]] = umfeld_fundstelle

    # --- Lücken: ausdrücklich nicht vorhandene Technologien ---
    # Eine Technologie wird nur dann zur Lücke, wenn die Anzeige sie von der Bewerberin
    # oder dem Bewerber verlangt. Wird sie bloss beschreibend genannt („unsere Daten
    # liegen in Azure“), ist sie Umgebungsinformation und gehört in den Kontext, nicht
    # in die Lückenliste.
    luecken: list[Luecke] = []
    umgebung: list[Branche] = []
    for schluessel, anzeigename in NICHT_VORHANDEN.items():
        pattern = _GAP_PATTERNS[schluessel]
        if not pattern.search(volltext):
            continue
        if any(l.begriff == anzeigename for l in luecken) or \
           any(u.name == anzeigename for u in umgebung):
            continue
        fundstelle, verlangt, pflicht = "", False, False
        for idx, zeile in enumerate(zeilen):
            if pattern.search(_normalise(zeile)):
                fundstelle = zeile
                im_teil = idx < len(anforderungs_flags) and anforderungs_flags[idx]
                verlangt = (
                    bool(_FORDERUNG.search(zeile))
                    or bool(_OPTIONAL_MARKER.search(zeile))
                    # Eine Technologie, die im Aufgaben- oder Profilteil steht, ist
                    # gefordert — auch ohne das Wort „Kenntnisse“. Sonst verschwindet
                    # genau das Werkzeug lautlos, um das sich die Stelle dreht.
                    or (im_teil and not _UMFELD.search(zeile))
                )
                pflicht = (
                    bool(_FORDERUNG.search(zeile)) or im_teil
                ) and ist_pflicht(zeile, idx)
                if verlangt:
                    erfasste_zeilen.add(idx)
                break
        # Steht die Technologie in einer Aufzählung von Alternativen und ist eine davon
        # belegt, ist nichts offen: „SPSS oder Python“ ist mit Python erfüllt.
        alternative_erfuellt = False
        if fundstelle and _ALTERNATIVE.search(fundstelle):
            norm_zeile = _normalise(fundstelle)
            alternative_erfuellt = any(
                p.search(norm_zeile) for key in treffer for _, p in _PATTERNS[key]
            )
        if alternative_erfuellt:
            umgebung.append(Branche(name=anzeigename, fundstelle=fundstelle, art="alternative"))
        elif verlangt:
            luecken.append(Luecke(begriff=anzeigename, fundstelle=fundstelle, pflicht=pflicht))
        else:
            umgebung.append(Branche(name=anzeigename, fundstelle=fundstelle, art="umgebung"))

    # Vorhandene Kompetenzen, die nur als Umgebung des Unternehmens genannt sind:
    # ebenfalls sichtbar machen, aber ausdrücklich nicht als erfüllte Anforderung.
    for label, fundstelle in nur_umfeld.items():
        if not any(u.name == label for u in umgebung):
            umgebung.append(Branche(name=label, fundstelle=fundstelle, art="umgebung_koennen"))

    # --- Lücken: geforderte Berufsjahre und Seniorität ---
    jahre_treffer = [int(m.group(1)) for m in _JAHRE.finditer(anzeige) if int(m.group(1)) <= 20]
    if jahre_treffer:
        gefordert = max(jahre_treffer)
        if gefordert * 12 > PRAXIS_MONATE + 6:
            fundstelle = ""
            for idx, zeile in enumerate(zeilen):
                if _JAHRE.search(zeile):
                    fundstelle = zeile
                    erfasste_zeilen.add(idx)
                    break
            luecken.append(
                Luecke(
                    begriff=f"Mehrjährige Berufserfahrung (gefordert: {gefordert} Jahre)",
                    fundstelle=fundstelle,
                    pflicht=gefordert >= 3,
                )
            )

    elif _JAHRE_WORT.search(anzeige):
        # Ohne Zahl lässt sich die Höhe nicht beziffern; „mehrjährig“ liegt aber
        # erkennbar über sieben Monaten Praxis und gehört offen ausgewiesen. Diese
        # Formulierung ist in deutschen Anzeigen häufiger als jede Jahreszahl.
        fundstelle = ""
        for idx, zeile in enumerate(zeilen):
            if _JAHRE_WORT.search(zeile):
                fundstelle = zeile
                erfasste_zeilen.add(idx)
                break
        luecken.append(
            Luecke(
                begriff="Mehrjährige Berufserfahrung (ohne Jahreszahl gefordert)",
                fundstelle=fundstelle,
                pflicht=True,
            )
        )

    studierenden_stelle = False
    studierenden_fundstelle = ""
    for m in _STUDIERENDEN_STELLE.finditer(anzeige):
        satz = _satz_um(anzeige, m.start(), m.end())
        if _ERFAHRUNGSQUELLE.search(satz):
            continue        # Aufzählung möglicher Erfahrungsquellen, keine Bedingung
        studierenden_stelle = True
        studierenden_fundstelle = satz.strip()[:200]
        break
    if studierenden_stelle:
        fundstelle = studierenden_fundstelle or next(
            (z for z in zeilen if _STUDIERENDEN_STELLE.search(z)), ""
        )
        luecken.append(
            Luecke(
                begriff="Laufendes Studium (Praktikum, Werkstudium oder duales Studium)",
                fundstelle=fundstelle,
                pflicht=True,
            )
        )

    kopf = "\n".join(anzeige.strip().splitlines()[:3])
    if _SENIOR.search(kopf) or _SENIOR.search(" ".join(zeilen[:6])):
        luecken.append(
            Luecke(
                begriff="Senior- bzw. Führungsebene",
                fundstelle=kopf.strip().splitlines()[0] if kopf.strip() else "",
                pflicht=True,
            )
        )

    # --- Generische Analysephrasen: branchenneutrale Tätigkeit erkennen ---
    # Bewusst auch für bereits erfasste Zeilen: „Auswertung von Daten aus dem CRM“
    # ist zugleich Kundenanalytik und explorative Analyse. Doppelt gezählt wird nichts,
    # weil die Treffer nach Kompetenz-Schlüssel abgelegt werden.
    for idx, zeile in enumerate(zeilen):
        if not _ANALYSE_PHRASE.search(zeile):
            continue
        skill = next(s for s in SKILLS if s["key"] == "eda")
        eintrag = treffer.get("eda")
        if eintrag is None:
            eintrag = Treffer(skill=skill, fundstellen=[], begriffe=[],
                              pflicht=ist_pflicht(zeile, idx))
            treffer["eda"] = eintrag
        if len(eintrag.fundstellen) < 3 and zeile not in eintrag.fundstellen:
            eintrag.fundstellen.append(zeile)
        erfasste_zeilen.add(idx)

    # --- Branchenkontext (wertneutral) ---
    branchen: list[Branche] = []
    gesehen: set[str] = set()

    # Zuerst: Branchen, in denen Erfahrung tatsächlich belegt ist. Das ist kein
    # Zugeständnis, sondern ein Pluspunkt und gehört zuerst genannt.
    for skill_key, anzeigename in BRANCHEN_SKILLS.items():
        if skill_key in treffer and anzeigename not in gesehen:
            branchen.append(
                Branche(name=anzeigename,
                        fundstelle=(treffer[skill_key].fundstellen or [""])[0],
                        art="belegt")
            )
            gesehen.add(anzeigename)

    for schluessel, anzeigename in FREMDE_BRANCHEN.items():
        if anzeigename in gesehen:
            continue
        pattern = _strenges_muster(schluessel)
        if not pattern.search(volltext):
            continue
        fundstelle = next((z for z in zeilen if pattern.search(_normalise(z))), "")
        branchen.append(Branche(name=anzeigename, fundstelle=fundstelle, art="branche"))
        gesehen.add(anzeigename)
    for schluessel, anzeigename in REGELWERKE.items():
        pattern = _strenges_muster(schluessel)
        if not pattern.search(volltext) or anzeigename in gesehen:
            continue
        fundstelle = ""
        gefordert = False
        for idx, zeile in enumerate(zeilen):
            if pattern.search(_normalise(zeile)):
                fundstelle = zeile
                gefordert = bool(_FORDERUNG.search(zeile)) and ist_pflicht(zeile, idx)
                break
        gesehen.add(anzeigename)
        if gefordert:
            # Ausdrücklich verlangtes Regelwerk ist eine echte Lücke, kein Kontext.
            luecken.append(Luecke(begriff=anzeigename, fundstelle=fundstelle, pflicht=True))
        else:
            branchen.append(Branche(name=anzeigename, fundstelle=fundstelle, art="regelwerk"))

    # Eine allgemein geforderte „Branchenerfahrung“ ohne erkennbare Branche: ebenfalls
    # ansprechen, damit die Liste oben nicht als abschliessend missverstanden wird.
    if not any(b.art in ("branche", "belegt") for b in branchen):
        for signal in BRANCHEN_SIGNAL:
            pattern = _strenges_muster(signal)
            if pattern.search(volltext):
                fundstelle = next((z for z in zeilen if pattern.search(_normalise(z))), "")
                branchen.append(
                    Branche(name="Branchenerfahrung", fundstelle=fundstelle, art="branche")
                )
                break

    # --- Sprachanforderungen ---
    def _niveau(roh: str) -> str:
        roh = roh.lower().strip()
        if roh[:2] in ("a1", "a2", "b1", "b2", "c1", "c2"):
            return roh[:2].upper()
        for wort, stufe in _NIVEAU_WORT.items():
            if roh.startswith(wort):
                return stufe
        return ""

    # sprache -> (niveau, fundstelle, zwingend gefordert)
    gefunden: dict[str, tuple[str, str, bool]] = {}

    # Zuerst Paare wie „Deutsch und Englisch verhandlungssicher“
    for m in _SPRACHE_PAAR.finditer(anzeige):
        stufe = _niveau(m.group(3))
        if not stufe:
            continue
        satz = _satz_um(anzeige, m.start(), m.end())
        zwingend = bool(_SPRACHE_ZWINGEND.search(satz))
        for s in (m.group(1).lower(), m.group(2).lower()):
            gefunden.setdefault(s, (stufe, m.group(0).strip(), zwingend))

    for name, pattern in _SPRACHE.items():
        if name in gefunden:
            continue
        m = pattern.search(anzeige)
        if m:
            stufe = _niveau(m.group(1))
            if stufe:
                satz = _satz_um(anzeige, m.start(), m.end())
                gefunden[name] = (stufe, m.group(0).strip(),
                                  bool(_SPRACHE_ZWINGEND.search(satz)))
                continue
        m = _SPRACHE_VORAN[name].search(anzeige)
        if m:
            # Das Niveau kann zur Sprache DAVOR gehören: In „Deutsch C1, Englisch“
            # beschreibt C1 das Deutsch, über Englisch sagt der Satz nichts.
            davor = anzeige[max(0, m.start() - 24):m.start()].lower()
            zwischentext = m.group(0)[len(m.group(1)):].lower()
            fremde_sprache = any(
                anderer in davor or anderer in zwischentext
                for anderer in SPRACHNAMEN if anderer != name
            )
            stufe = "" if fremde_sprache else _niveau(m.group(1))
            if stufe:
                satz = _satz_um(anzeige, m.start(), m.end())
                gefunden[name] = (stufe, m.group(0).strip(),
                                  bool(_SPRACHE_ZWINGEND.search(satz)))

    sprachen: list[Sprachbedarf] = []
    for name, (stufe, fundstelle, zwingend) in gefunden.items():
        eigen = EIGENE_SPRACHEN.get(name)
        if eigen is None:
            sprachen.append(
                Sprachbedarf(sprache=name.capitalize(), gefordert=stufe,
                             vorhanden="nicht vorhanden", erfuellt=False,
                             fundstelle=fundstelle, zwingend=zwingend)
            )
            continue
        erfuellt = NIVEAU_RANG.get(eigen.lower(), 0) >= NIVEAU_RANG.get(stufe.lower(), 0)
        sprachen.append(
            Sprachbedarf(sprache=name.capitalize(), gefordert=stufe, vorhanden=eigen,
                         erfuellt=erfuellt, fundstelle=fundstelle, zwingend=zwingend)
        )

    # --- Standort und Arbeitsmodell (wertneutral) ---
    orte_gefunden, modelle_gefunden = [], []
    for ort in sorted(ERREICHBARE_REGIONEN | FERNE_ORTE):
        if _strenges_muster(ort).search(volltext):
            orte_gefunden.append(ort)
    for schluessel, name in _MODELLE.items():
        if _strenges_muster(schluessel).search(volltext) and name not in modelle_gefunden:
            modelle_gefunden.append(name)

    nah = [o for o in orte_gefunden if o in ERREICHBARE_REGIONEN]
    fern = [o for o in orte_gefunden if o in FERNE_ORTE]
    remote_moeglich = any(m in ("Remote", "Homeoffice", "Mobiles Arbeiten") for m in modelle_gefunden)

    # „Pendelbereich“ heisst hier ausschliesslich: der Ort steht auf einer gepflegten
    # Liste von Orten in NRW, Rheinland-Pfalz und Hessen. Es wird KEINE Fahrzeit
    # berechnet. Steht ein Ort auf keiner der beiden Listen, lautet das Ergebnis
    # „unbekannt“ — nicht „passt“.
    REGEL = ("Grundlage ist eine Ortsliste für NRW, Rheinland-Pfalz und Hessen, "
             "keine berechnete Fahrzeit.")
    standort = None
    if orte_gefunden or modelle_gefunden:
        if nah:
            passt, grund = True, f"Ort auf der Liste erreichbarer Regionen. {REGEL}"
        elif fern and remote_moeglich:
            passt, grund = True, (
                f"Ort ausserhalb der Liste, aber remote oder hybrid möglich. {REGEL}"
            )
        elif fern:
            passt, grund = False, (
                f"Ort ausserhalb der Liste und ausschliesslich vor Ort. Ein Umzug ist "
                f"denkbar, sollte aber vorab besprochen werden. {REGEL}"
            )
        elif modelle_gefunden and not orte_gefunden:
            passt, grund = None, (
                "Die Anzeige nennt ein Arbeitsmodell, aber keinen für die Prüfung "
                f"erkennbaren Ort. Zur Erreichbarkeit lässt sich daher nichts sagen. {REGEL}"
            )
        else:
            passt, grund = None, (
                "Der genannte Ort steht auf keiner der hinterlegten Listen. Ob er "
                f"erreichbar ist, lässt sich hier nicht beurteilen. {REGEL}"
            )
        standort = Standort(
            orte=[o.title() for o in (nah + fern)],
            modelle=modelle_gefunden,
            passt=passt,
            begruendung=grund,
        )

    # --- Teilanforderungen: nicht erkannte Stücke erfasster Zeilen sichtbar halten ---
    teil_offen: list[str] = []
    teil_offen_set: set[str] = set()
    for idx in sorted(erfasste_zeilen):
        if idx >= len(zeilen):
            continue
        zeile = zeilen[idx]
        for teil in _TEILUNG.split(zeile):
            teil = teil.strip(" \t-–—:·")
            if len(teil) < 14 or len(teil.split()) < 3:
                continue
            norm = _normalise(teil)
            erkannt = any(
                p.search(norm) for key in treffer for _, p in _PATTERNS[key]
            ) or any(_GAP_PATTERNS[k].search(norm) for k in NICHT_VORHANDEN)
            # Sprachanforderungen werden im eigenen Abschnitt ausgewertet und dürfen
            # nicht zusätzlich als unklare Anforderung in den Nenner wandern.
            if any(p.search(teil) for p in _SPRACHE.values()):
                erkannt = True
            # Geforderte Berufsjahre stehen schon als eigene Lücke im Nenner.
            if jahre_treffer and _JAHRE.search(teil):
                erkannt = True
            if not erkannt and (_FORDERUNG.search(teil) or _ANFORDERUNG_FORM.search(teil)):
                teil_offen.append(teil)
                teil_offen_set.add(teil)

    # Zeilen, die bereits als Sprachanforderung ausgewertet wurden, dürfen nicht
    # zusätzlich als „unklare Anforderung“ in den Nenner wandern.
    for _, (_, fundstelle, _zwingend) in gefunden.items():
        for idx, zeile in enumerate(zeilen):
            if fundstelle and fundstelle[:30].lower() in zeile.lower():
                erfasste_zeilen.add(idx)

    # --- Stufe 2: semantisch für die restlichen Zeilen ---
    # Anzeige wie Bewertung: Selbstdarstellung, Umfeldsätze und Benefit-Aufzählungen
    # gehören nicht in die Liste offener Anforderungen — sie sind keine.
    def _ist_anforderung(z: str) -> bool:
        return not (
            _SELBSTDARSTELLUNG.match(z)
            or _UMFELD.search(z)
            or _BENEFIT_LISTE.search(z)
        )

    offene = [
        z for i, z in enumerate(zeilen)
        if i not in erfasste_zeilen and _ist_anforderung(z)
    ] + [z for z in teil_offen if _ist_anforderung(z)]
    semantik_aktiv = False
    hinweis = ""
    if semantik and offene:
        ok, fehler = lade_semantik()
        if ok:
            semantik_aktiv = True
            zuordnung, offene = _semantische_treffer(offene)
            for key, zugeordnete in zuordnung.items():
                skill = next(s for s in SKILLS if s["key"] == key)
                if key in treffer:
                    for z in zugeordnete:
                        if z not in treffer[key].fundstellen and len(treffer[key].fundstellen) < 3:
                            treffer[key].fundstellen.append(z)
                else:
                    treffer[key] = Treffer(
                        skill=skill,
                        fundstellen=zugeordnete[:2],
                        begriffe=[],
                        semantisch=True,
                        pflicht=any(ist_pflicht(z) for z in zugeordnete),
                    )
        else:
            hinweis = (
                "Der semantische Abgleich ist gerade nicht verfügbar — die Auswertung "
                "beruht allein auf der Synonymliste."
            )

    treffer_liste = sorted(
        treffer.values(), key=lambda t: (t.pflicht, t.skill["staerke"]), reverse=True
    )

    # --- Score ---
    # Der Nenner enthält ALLE erkannten Anforderungen der Anzeige, nicht nur die Lücken.
    # Sonst erreicht jede Anzeige ohne ausdrückliche Lücke automatisch den Höchstwert und
    # der Wert verliert jede Trennschärfe.
    #   Zähler  = belegte Anforderungen, gewichtet nach Belegstärke
    #   Nenner  = belegte + nicht belegte + nicht zuordenbare Anforderungen
    gewicht_treffer = sum(t.gewicht for t in treffer_liste)
    gewicht_luecken = sum(l.gewicht for l in luecken)
    gewicht_sprachen = sum(s.gewicht for s in sprachen)
    score_ohne_sprache = None

    # Nicht zuordenbare Zeilen zählen nur mit, wenn sie überhaupt nach einer
    # Anforderung aussehen — Fliesstext über das Unternehmen bleibt aussen vor.
    in_anforderungsteil = {
        z for z, flag in zip(zeilen, anforderungs_flags) if flag
    }
    unklare_anforderungen = [
        z for z in offene
        if (_FORDERUNG.search(z) or _ANFORDERUNG_FORM.search(z) or z in in_anforderungsteil)
        and not _SELBSTDARSTELLUNG.match(z)
        and not _UMFELD.search(z)
        and not _BENEFIT_LISTE.search(z)
    ]
    # Eine nicht zuordenbare Anforderung wiegt weniger als eine bestätigte Lücke — sie
    # könnte etwas sein, das die Synonymliste nur nicht kennt. Aber deutlich mehr als
    # bisher: Wer neun von elf Punkten nicht versteht, darf keine 85 % ausweisen.
    # Ein Reststück einer im Übrigen erfüllten Zeile wiegt halb so viel wie eine
    # komplett unverstandene Anforderung — es ist Detail, nicht eigener Punkt.
    gewicht_unklar = sum(
        0.35 if z in teil_offen_set else 0.7 for z in unklare_anforderungen
    )

    nenner = gewicht_treffer + gewicht_luecken + gewicht_sprachen + gewicht_unklar
    score = 0 if nenner == 0 else 100 * gewicht_treffer / nenner

    # Eine Sprachlücke darf das fachliche Ergebnis höchstens um 5 Punkte drücken.
    # Sie ist eine Frage der Einarbeitung, keine fehlende Fachkompetenz.
    if gewicht_sprachen and not any(sp.zwingend and not sp.erfuellt for sp in sprachen):
        nenner_ohne = gewicht_treffer + gewicht_luecken + gewicht_unklar
        score_ohne_sprache = 0 if nenner_ohne == 0 else 100 * gewicht_treffer / nenner_ohne
        score = max(score, score_ohne_sprache - 5)

    # Pflichtlücken werden NICHT über einen willkürlichen Deckel verrechnet. Eine fehlende
    # Muss-Anforderung wiegt im Nenner ohnehin am schwersten; ein zusätzlicher Deckel würde
    # eine im Übrigen starke Übereinstimmung unangemessen zerstören. Stattdessen wird die
    # Zahl der Pflichtlücken getrennt ausgewiesen und im Ergebnis deutlich genannt.
    pflicht_luecken = sum(1 for l in luecken if l.pflicht)

    # Obergrenze: Der Wert misst die fachliche Abdeckung, nicht die Gesamteignung.
    # Berufserfahrung, Team-Fit und Motivation entscheiden sich im Gespräch, nicht hier.
    score = max(0, min(95, round(score)))

    return Ergebnis(
        score=score,
        treffer=treffer_liste,
        luecken=luecken,
        offene_zeilen=offene[:8],
        semantik_aktiv=semantik_aktiv,
        hinweis=hinweis,
        branchen=branchen,
        sprachen=sprachen,
        standort=standort,
        umgebung=umgebung,
        pflicht_luecken=pflicht_luecken,
        # Eine Anzeige mit sehr wenig erkennbaren Anforderungen erlaubt keine belastbare
        # Aussage. Dann wird das offen gesagt, statt eine Zahl zu zeigen, die nach
        # schlechter Passung aussieht, obwohl nur der Text zu kurz war.
        belastbar=_belastbar(treffer_liste, luecken, zeilen, anzeige),
    )
