# Passt Mesut?

**Stellenanzeige einfügen — die App prüft, wie weit das Profil von Mesut Karagöz die
Anforderungen abdeckt, und nennt zu jedem Treffer den Nachweis.**

Eine Anwendung für Recruiterinnen und Recruiter. Statt einer Liste von Schlagworten
beantwortet sie die Frage, die im Bewerbungsprozess tatsächlich gestellt wird:
*Passt dieser Mensch zu dieser Stelle — und woran lässt sich das festmachen?*

---

## Was die App macht

1. **Zerlegen** — Der eingefügte Anzeigentext wird in einzelne Anforderungen zerlegt.
   Überschriften, Standortangaben und Benefits werden dabei aussortiert.
2. **Lexikalischer Abgleich** — Eine gepflegte Synonymliste ordnet jeder Anforderung eine
   Kompetenz zu: „BI-Reporting“ → Power BI, „Aufbereitung von Massendaten“ → ETL.
   Jeder Treffer nennt den gefundenen Begriff, bleibt also überprüfbar.
3. **Semantischer Abgleich** — Was dabei offen bleibt, vergleicht ein mehrsprachiges
   Embedding-Modell nach Bedeutung statt nach Wortlaut.
4. **Nachweis** — Zu jeder erfüllten Anforderung erscheint der Beleg: Zertifikatsstunden
   und/oder ein öffentliches Projekt samt Code- und Demo-Link.
5. **Lücken** — Was nicht belegt ist, wird offen genannt. Auch geforderte Berufsjahre und
   Senior-Positionen werden geprüft und als Lücke ausgewiesen.

## Was der Wert sagt — und was nicht

Der Wert ist der **Anteil der belegten an allen erkannten Anforderungen**. Er sagt,
wie weit das dokumentierte Profil eine Anzeige abdeckt. Er sagt **nicht**, ob daraus
eine Einladung wird: darüber entscheiden Berufsjahre, Team und Gespräch.

Diese Grenze ist nicht geschätzt, sondern gemessen. Die App wurde gegen **221 echte
Stellenanzeigen** geprüft, deren Ausgang bekannt war. Ergebnis: Anzeigen mit und ohne
anschliessendes Gespräch überlappen sich im Messwert deutlich. Ein hoher Wert bedeutet
also gute fachliche Abdeckung — keine Prognose. Deshalb heisst die Beschriftung
„Abdeckung“ und nicht „Passung“, und deshalb liegt die Obergrenze bei **95 %**.

Ebenso bewusst meldet die App Lücken, statt sie zu überspielen. Eine Anwendung, die bei
jeder Anzeige „perfekte Übereinstimmung“ anzeigt, ist Werbung — keine Analyse.

| Beispielanzeige | Ergebnis |
| --- | --- |
| Data Analyst, Power BI und SQL, Reporting | 95 % — hohe fachliche Abdeckung |
| Data Analyst, Azure zwingend erforderlich | 78 % — eine Muss-Lücke, getrennt ausgewiesen |
| Senior Data Engineer, Spark, Databricks, 5 Jahre | 29 % — sechs Muss-Lücken |
| Consultant Konzernrechnungswesen, IFRS | kein Wert — fachfremd, zu wenig erkannt |

Die Werte in dieser Tabelle stammen aus der Testsuite und werden bei jeder Änderung
nachgerechnet.

### Wann die App keinen Wert ausgibt

Ein Prozentwert auf dünner Grundlage wäre irreführend. Die App verweigert ihn, wenn
weniger als fünf Anforderungen erkennbar sind — etwa bei einem Lebenslauf statt einer
Anzeige, bei einem Textfragment oder bei einer **englischsprachigen Anzeige**: die
Synonymliste ist deutsch und würde aus vereinzelten Technologienamen einen hohen Wert
auf winziger Basis bilden.

## Technik

| Baustein | Umsetzung |
| --- | --- |
| Oberfläche | Streamlit, deutschsprachig, dunkles Thema |
| Lexikalischer Abgleich | Synonymliste über alle belegten Kompetenzen, Wortgrenzen-Regex |
| Semantischer Abgleich | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` via `fastembed` (ONNX, 0,22 GB, ohne PyTorch) |
| Messuhr | handgeschriebenes Inline-SVG, keine Diagrammbibliothek |
| Datengrundlage | `src/profile_data.py` — jede Kompetenz mit Beleg und Projektverweis |

Der semantische Abgleich ist optional: Lässt sich das Modell nicht laden, arbeitet die
App mit der Synonymliste weiter und weist im Interface darauf hin.

## Lokal starten

```bash
git clone https://github.com/Mst-KrgZ/passt-mesut.git
cd passt-mesut
pip install -r requirements.txt
streamlit run app.py
```

Beim ersten Start mit aktiviertem semantischem Abgleich wird das Embedding-Modell
geladen (einmalig, ca. 0,22 GB).

## Deployment auf Streamlit Community Cloud

1. Repository auf GitHub anlegen und den Inhalt dieses Ordners pushen.
2. Auf [share.streamlit.io](https://share.streamlit.io) → **New app** → Repository und
   `app.py` als Hauptdatei auswählen.
3. Nach dem Deploy die URL in den LinkedIn-Beitrag, den Lebenslauf und die
   Portfolio-Website eintragen.

> **Hinweis zum Ruhezustand:** Apps auf der Community Cloud gehen nach rund zwölf Stunden
> ohne Aufrufe schlafen und müssen von Besuchern per Klick geweckt werden. Vor jeder
> Bewerbungs- oder Beitragswelle den Link einmal selbst öffnen.

## Projektstruktur

```
passt-mesut/
├── app.py                 Streamlit-Oberfläche
├── requirements.txt
├── .streamlit/config.toml dunkles Farbschema
├── src/
│   ├── profile_data.py    belegbasiertes Kompetenzprofil
│   ├── matcher.py         lexikalischer und semantischer Abgleich, Bewertung
│   ├── gauge.py           SVG-Messuhr
│   ├── render.py          Maskierung aller Texte aus der Anzeige
│   └── analytics.py       anonyme Nutzungszählung
└── tests/                 68 Regressionstests
```

## Datenschutz

Der eingefügte Anzeigentext wird nur für die Dauer des Aufrufs im Arbeitsspeicher des
Servers verarbeitet. Er wird **nicht** zwischengespeichert (kein `st.cache_data`), nicht
protokolliert, nicht in eine Datenbank geschrieben und an keinen externen Dienst
gesendet. Der semantische Abgleich läuft lokal über ein ONNX-Modell; beim ersten Start
wird nur das Modell selbst geladen, niemals Text aus der Anzeige.

Jeder Text, der aus der Anzeige stammt und in der Oberfläche erscheint, läuft vorher
durch `src/render.py`. Nicht zugeordnete Zeilen werden als reiner Text ausgegeben, nicht
als Markdown oder HTML.

### Nutzungszählung

Die Seitenleiste enthält einen passwortgeschützten Bereich mit anonymen Zählungen:
geöffnete Sitzungen, begonnene Eingaben, gestartete Prüfungen, abgeschlossene
Auswertungen, Sitzungen ohne Prüfung, Sitzungen mit Eingabe aber ohne Prüfung,
Sitzungen ohne semantische Stufe und Fehler — je für heute, 7 und 30 Tage.

Jede Zahl ist eine Zahl von **Sitzungen**, nicht von Personen und nicht von
Einzelauswertungen: Jedes Ereignis zählt höchstens einmal pro Sitzung. Wer in derselben
Sitzung eine zweite Anzeige prüft, erscheint weiterhin als eine Sitzung.

Gespeichert werden ausschliesslich **Datum, Ereignisname und Anzahl**. Kein
Anzeigentext, keine Namen, keine E-Mail-Adressen, keine IP-Adressen, keine Browserdaten.
Die Zahlen stehen für Sitzungen, nicht für Personen.

**Einrichtung.** In den Streamlit-Secrets:

```toml
ADMIN_PASSWORT = "..."          # schaltet den Bereich frei
SUPABASE_URL   = "https://..."  # optional, für dauerhafte Zahlen
SUPABASE_KEY   = "..."          # optional
```

Ohne `SUPABASE_*` zählt die App nur im Arbeitsspeicher des laufenden Prozesses. Auf
Streamlit Community Cloud ist das **nicht dauerhaft**: Nach einem Ruhezustand oder einem
neuen Deploy beginnen die Zahlen wieder bei null. Die Oberfläche weist darauf hin. Für
dauerhafte Zahlen genügt eine Tabelle:

```sql
create table passt_mesut_events (
  id bigserial primary key,
  tag date not null,
  ereignis text not null
);
create index on passt_mesut_events (tag, ereignis);
```

Je Ereignis wird genau eine Zeile angehängt; summiert wird erst beim Lesen. Ein Zähler,
der erst gelesen und dann erhöht wird, würde bei zwei gleichzeitigen Aufrufen eine
Zählung verlieren.

Secrets gehören nie in den Quellcode; `.streamlit/secrets.toml` ist in `.gitignore`.

---

**Mesut Karagöz** — Data Analyst (IHK) | Business Intelligence | Data Scientist
Neuwied, Rheinland-Pfalz · [Portfolio](https://mesutkaragoez.de) ·
[GitHub](https://github.com/Mst-KrgZ) · [LinkedIn](https://www.linkedin.com/in/mesut-karagoz/)

---

## Tests

```bash
pip install pytest
pytest -q
```

**68 Tests** in `tests/`:

| Datei | Prüft |
| --- | --- |
| `test_matching.py` | Abschnittslogik, deutsche Flexion, Teilanforderungen, Sprachniveaus und ihre Satzstellung, Unternehmensumfeld gegen Anforderung, Branchenkontext, Erfahrung und Seniorität, Standort, Trennschärfe, Belastbarkeit |
| `test_render.py` | Maskierung genau der Funktion, die die App benutzt — inklusive einer echten Fundstelle aus der Analyse |
| `test_analytics.py` | dass im Bericht kein Anzeigentext landet, nur Datum und Ereignis gespeichert werden und die Zählung ohne Lesen-Ändern-Schreiben auskommt |

## Bekannte Grenzen

- **Der semantische Abgleich ist nicht Ende zu Ende getestet.** Die Entwicklungsumgebung
  hatte keinen Netzzugang zum Modell-Download. Alle Zahlen oben stammen aus der
  lexikalischen Stufe. Schlägt der Modellstart fehl, arbeitet die App mit dieser Stufe
  weiter und sagt es im Interface.
- **Die Synonymliste ist gepflegt, aber endlich.** Ungewöhnlich formulierte Anforderungen
  landen unter „Nicht eindeutig zugeordnet“ und senken dort den Wert, statt ihn zu schönen.
- **Der Wert ist eine Orientierung, keine Prognose.** Formel und Gewichte stehen in der
  Seitenleiste; die Obergrenze von 95 % ist bewusst gesetzt. Gegen 221 echte Anzeigen
  geprüft: Abdeckung und Gesprächseinladung korrelieren nur schwach.
- **Englischsprachige Anzeigen werden abgelehnt**, nicht geschätzt. Das Wörterbuch ist
  deutsch; ein Wert auf englischem Text wäre eine Zahl ohne Grundlage.
- **Berufsjahre** werden aus Zahlenangaben gelesen. „Langjährige Erfahrung“ ohne Zahl
  wird nicht erkannt.
- **Standort** beruht auf einer Ortsliste, nicht auf einer Fahrzeitberechnung. Orte
  ausserhalb beider Listen werden als „nicht beurteilbar“ ausgewiesen, nicht als passend.
- **Nutzungszahlen sind ohne Supabase-Konfiguration flüchtig** (siehe Datenschutz) und
  zählen Sitzungen, nicht Personen oder einzelne Auswertungen.
- **Die Erkennung von Unternehmensumfeld gegenüber Anforderung** beruht auf
  Formulierungsmustern („unser Team nutzt …“). Ungewöhnlich formulierte Sätze können
  weiterhin falsch einsortiert werden; im Zweifel landet eine Technologie unter
  „Technologien im Unternehmensumfeld“ und zählt dann gar nicht — also eher zu
  vorsichtig als zu grosszügig.
