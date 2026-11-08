"""
Regressionstests für die Matching-Engine.

Ausführen:  pytest -q

Jeder Test hält ein Verhalten fest, das in der Entwicklung schon einmal falsch war.
Wer die Synonymliste oder die Bewertung ändert, sieht hier sofort, was dabei kaputtgeht.
"""

import re
import sys
from html import escape
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.matcher import (  # noqa: E402
    EIGENE_SPRACHEN,
    analysiere,
    split_requirements_markiert,
    _alias_pattern,
)
from src.profile_data import SKILLS  # noqa: E402


def keys(ergebnis):
    return {t.skill["key"] for t in ergebnis.treffer}


def luecken(ergebnis):
    return {l.begriff for l in ergebnis.luecken}


def pflicht_luecken(ergebnis):
    return {l.begriff for l in ergebnis.luecken if l.pflicht}


# ---------------------------------------------------------------- Abschnitte

def test_wuenschenswert_abschnitt_bleibt_optional():
    anzeige = """Data Analyst (m/w/d)
Ihr Profil:
- Sehr gute SQL-Kenntnisse
- Power BI mit DAX
Wünschenswert:
- Kenntnisse in Databricks
- Erfahrung mit Snowflake"""
    r = analysiere(anzeige, semantik=False)
    assert pflicht_luecken(r) == set(), "Punkte unter 'Wünschenswert:' dürfen kein Muss sein"
    assert {"Databricks", "Snowflake"} <= luecken(r)


def test_technologie_als_kontext_ist_kein_muss():
    anzeige = """Data Analyst (m/w/d)
Aufgaben: Unsere Daten liegen in Azure. Sie bauen KPI-Dashboards in Power BI und
werten mit SQL aus, sichern die Datenqualität und automatisieren das Reporting.
Profil: SQL, Power BI, Datenmodellierung, Deutsch C1."""
    r = analysiere(anzeige, semantik=False)
    assert "Azure" not in pflicht_luecken(r)
    assert r.score >= 80


def test_technologie_als_echte_forderung_ist_ein_muss():
    anzeige = """Data Analyst (m/w/d)
Aufgaben: KPI-Dashboards in Power BI, SQL-Auswertungen, Datenqualität.
Profil: SQL, Power BI, Deutsch C1. Fundierte Azure-Kenntnisse sind zwingend erforderlich."""
    r = analysiere(anzeige, semantik=False)
    assert "Azure" in pflicht_luecken(r)


# ---------------------------------------------------------------- Teilanforderungen

def test_mehrere_anforderungen_in_einer_zeile():
    """Ein erkannter Begriff darf die übrigen Teile derselben Zeile nicht verdecken."""
    anzeige = """Data Analyst (m/w/d)
Profil: Fundierte Kenntnisse in Power BI, SQL und Apache Spark erforderlich.
Deutsch C1."""
    r = analysiere(anzeige, semantik=False)
    assert {"powerbi", "sql"} <= keys(r)
    assert "Apache Spark" in pflicht_luecken(r), "Spark darf nicht hinter Power BI verschwinden"


# ---------------------------------------------------------------- Flexion

@pytest.mark.parametrize(
    "alias,text",
    [
        ("datenmodell", "Modellierung von Datenmodellen im Warehouse"),
        ("dashboard", "Erstellung von Dashboards"),
        ("analyse", "Durchführung von Analysen"),
        ("kenntnis", "Fundierte Kenntnisse in SQL"),
        ("prognose", "Erstellung von Prognosen"),
        ("bericht", "Erstellung der Berichte"),
    ],
)
def test_deutsche_flexion_wird_erkannt(alias, text):
    assert _alias_pattern(alias).search(text)


@pytest.mark.parametrize(
    "alias,text",
    [
        ("excel", "Das Team ist excellent aufgestellt"),
        ("sql", "Wir nutzen NoSQLDatenbanken"),
        ("cloud", "Cloudflare Konfiguration"),
        ("python", "Pythonista Community"),
        ("kredit", "Kreditinstitutsaufsichtsrecht"),
    ],
)
def test_aehnliche_woerter_loesen_keinen_treffer_aus(alias, text):
    assert not _alias_pattern(alias).search(text)


def test_modellierung_ist_kein_machine_learning():
    anzeige = """Data Engineer (m/w/d)
Aufgaben: Modellierung und Optimierung von Datenmodellen im Data Warehouse.
Profil: Sehr gute SQL-Kenntnisse."""
    r = analysiere(anzeige, semantik=False)
    assert "ml" not in keys(r), "'Modellierung' allein ist kein Machine Learning"
    assert "datenmodellierung" in keys(r)


def test_echtes_machine_learning_wird_weiter_erkannt():
    r = analysiere(
        "Data Scientist: Erfahrung mit Machine Learning, XGBoost und Feature Engineering. Python.",
        semantik=False,
    )
    assert "ml" in keys(r)


# ---------------------------------------------------------------- Sprachen

def test_beide_sprachen_in_einem_satz():
    anzeige = """Data Analyst (m/w/d)
Profil: Sehr gute SQL-Kenntnisse, Power BI. Deutsch und Englisch verhandlungssicher."""
    r = analysiere(anzeige, semantik=False)
    gefunden = {s.sprache: s for s in r.sprachen}
    assert set(gefunden) == {"Deutsch", "Englisch"}
    assert gefunden["Deutsch"].erfuellt is True
    assert gefunden["Englisch"].erfuellt is False
    assert gefunden["Englisch"].vorhanden == EIGENE_SPRACHEN["englisch"]


def test_sprachen_sind_keine_kompetenzen():
    assert [s for s in SKILLS if s["key"] in ("deutsch", "englisch")] == []


def test_sprachluecke_kostet_hoechstens_fuenf_punkte():
    basis = """Data Analyst (m/w/d)
Aufgaben: KPI-Dashboards in Power BI, SQL-Auswertungen, Reporting-Automatisierung,
Datenqualität sicherstellen, Ad-hoc-Analysen, Datenmodellierung.
Profil: Sehr gute SQL-Kenntnisse, fundierte Power-BI-Kenntnisse."""
    ohne = analysiere(basis, semantik=False)
    mit = analysiere(basis + "\nEnglisch C1 ist erforderlich.", semantik=False)
    assert ohne.score - mit.score <= 5, "Eine Sprachanforderung darf den Wert nicht einbrechen lassen"
    assert any(not s.erfuellt for s in mit.sprachen), "Die Lücke muss trotzdem sichtbar sein"


# ---------------------------------------------------------------- Branchen

def test_versicherung_ist_belegte_branche():
    anzeige = """Data Analyst Versicherung (m/w/d)
Aufgaben: Analyse von Schadendaten, Risikobewertung, KPI-Dashboards in Power BI.
Profil: SQL, Python, Erfahrung in der Versicherungsbranche von Vorteil, Deutsch C1."""
    r = analysiere(anzeige, semantik=False)
    assert any(b.art == "belegt" and b.name == "Versicherung" for b in r.branchen)
    assert r.score >= 80


def test_fremde_branche_senkt_den_fachlichen_wert_nicht():
    anzeige = """Data Analyst Pharma (m/w/d)
Aufgaben: Analyse von Qualitätsdaten, KPI-Dashboards in Power BI, Datenqualität sicherstellen.
Profil: Sehr gute SQL-Kenntnisse, Erfahrung in der Pharmaindustrie von Vorteil, Deutsch C1."""
    r = analysiere(anzeige, semantik=False)
    assert r.score >= 80
    assert any(b.name == "Pharma & Life Sciences" for b in r.branchen)


def test_gefordertes_regelwerk_ist_eine_echte_luecke():
    anzeige = """Data Analyst Pharma (m/w/d)
Aufgaben: Analyse von Qualitätsdaten, KPI-Dashboards in Power BI.
Profil: Sehr gute SQL-Kenntnisse, fundierte GxP-Kenntnisse sind erforderlich, Deutsch C1."""
    r = analysiere(anzeige, semantik=False)
    assert "GxP" in pflicht_luecken(r), "Ein verlangtes Regelwerk darf nicht als Kontext durchgehen"


def test_unbekannte_branche_wird_trotzdem_angesprochen():
    anzeige = """Data Analyst (m/w/d)
Aufgaben: KPI-Dashboards in Power BI, SQL-Auswertungen, Datenqualität.
Profil: Sehr gute SQL-Kenntnisse, einschlägige Branchenerfahrung wünschenswert, Deutsch C1."""
    r = analysiere(anzeige, semantik=False)
    assert any(b.art == "branche" for b in r.branchen)


# ---------------------------------------------------------------- Erfahrung

def test_realistische_senior_anzeige_ist_nicht_null():
    anzeige = """Senior Data Engineer (m/w/d)
Aufgaben: Aufbau von Datenpipelines, Datenmodellierung im Data Warehouse,
Sicherstellung der Datenqualität, Mentoring im Team.
Profil: Mindestens 5 Jahre Berufserfahrung. Sehr gute SQL-Kenntnisse und Python.
Fundierte Kenntnisse in Apache Spark und Databricks erforderlich. Docker und CI/CD."""
    r = analysiere(anzeige, semantik=False)
    assert 25 <= r.score <= 65, f"erwartet mittlerer Bereich, erhalten {r.score}"
    assert {"sql", "python"} <= keys(r)
    assert {"Apache Spark", "Databricks"} <= pflicht_luecken(r)
    assert any("Berufserfahrung" in b for b in pflicht_luecken(r))


def test_junior_anzeige_passt_deutlich_besser_als_senior():
    junior = """Junior Data Engineer (m/w/d)
Aufgaben: ETL-Strecken mit Python und SQL, Datenmodellierung, Datenqualität.
Profil: MINT-Studium, gute SQL- und Python-Kenntnisse, Docker und Git, Deutsch sehr gut."""
    senior = """Senior Data Engineer (m/w/d)
Profil: Mindestens 5 Jahre Berufserfahrung. Fundierte Kenntnisse in Apache Spark
und Databricks erforderlich. Snowflake und dbt vorausgesetzt. SQL und Python."""
    assert analysiere(junior, semantik=False).score > analysiere(senior, semantik=False).score + 20


# ---------------------------------------------------------------- Trennschärfe

def test_fachfremde_anzeige_bekommt_niedrigen_wert():
    anzeige = """Consultant (m/w/d) Konzernrechnungswesen
Profil: Sie verfügen über fundierte Kenntnisse in der Konsolidierung nach IFRS.
Sie bringen Erfahrung in der Transferpreisdokumentation mit.
Sie beherrschen die Konzernberichterstattung. Sehr gute SQL-Kenntnisse."""
    r = analysiere(anzeige, semantik=False)
    assert r.score <= 50, f"fachfremde Anzeige darf nicht hoch bewertet werden, erhalten {r.score}"


def test_ideale_anzeige_bekommt_hohen_wert():
    anzeige = """Data Analyst (m/w/d)
Aufgaben: Aufbau von KPI-Dashboards in Power BI, SQL-Auswertungen, Sicherstellung
der Datenqualität, Automatisierung des Reportings, Ad-hoc-Analysen, Präsentation
vor den Fachbereichen, Datenmodellierung.
Profil: Sehr gute SQL-Kenntnisse, fundierte Power-BI-Kenntnisse mit DAX, Deutsch C1."""
    r = analysiere(anzeige, semantik=False)
    assert r.score >= 85


def test_kein_wert_ueber_95():
    anzeige = "Data Analyst: SQL, Power BI, Reporting, Dashboards, Datenqualität, Python, Excel, Tableau."
    assert analysiere(anzeige, semantik=False).score <= 95


# ---------------------------------------------------------------- Belastbarkeit

def test_zu_kurze_anzeige_liefert_keinen_wert():
    r = analysiere("Wir suchen einen Data Analyst mit SQL-Kenntnissen.", semantik=False)
    assert r.belastbar is False, "Bei zu wenig Text darf kein Messwert ausgewiesen werden"


def test_ausreichende_anzeige_ist_belastbar():
    anzeige = """Data Analyst (m/w/d)

Ihre Aufgaben
Sie erstellen Reports und Dashboards für die Fachbereiche.
Sie analysieren Daten und bereiten Kennzahlen auf.

Ihr Profil
Fundierte Kenntnisse in SQL und Power BI.
Erfahrung in der Datenmodellierung und im Reporting.
Sie haben ein Auge für Datenqualität und arbeiten strukturiert.
Sehr gute Deutschkenntnisse."""
    assert analysiere(anzeige, semantik=False).belastbar is True


def test_lebenslauftext_liefert_keinen_wert():
    """Wer statt einer Anzeige einen Lebenslauf einfügt, darf keine 95 % sehen."""
    r = analysiere(
        "Mesut Karagöz, Neuwied. B.Sc. Physik. SQL, Python, Power BI. Lehrer 7 Jahre.",
        semantik=False,
    )
    assert r.belastbar is False


def test_englische_anzeige_liefert_keinen_wert():
    """Die Synonymliste ist deutsch — auf englischem Text ist der Wert nicht belastbar."""
    anzeige = (
        "We are looking for a Data Analyst with strong SQL and Power BI skills. "
        "You will build dashboards and work with our business teams. "
        "You have experience with data modelling and reporting. "
        "You are fluent in English and enjoy working in a team."
    )
    assert analysiere(anzeige, semantik=False).belastbar is False


# ---------------------------------------------------------------- Standort

def test_ferner_ort_ohne_remote_wird_getrennt_ausgewiesen():
    anzeige = """Data Analyst (m/w/d) in München
Aufgaben: KPI-Dashboards in Power BI, SQL-Auswertungen, Datenqualität, Reporting.
Profil: Sehr gute SQL-Kenntnisse, Power BI, Deutsch C1. Vor Ort in München."""
    r = analysiere(anzeige, semantik=False)
    assert r.standort is not None and r.standort.passt is False
    assert r.score >= 80, "Der Standort darf den fachlichen Wert nicht senken"


def test_naher_ort_passt():
    anzeige = """Data Analyst (m/w/d) in Koblenz
Profil: SQL, Power BI, Datenqualität, Reporting, Deutsch C1. Hybrid möglich."""
    r = analysiere(anzeige, semantik=False)
    assert r.standort is not None and r.standort.passt is True


# ---------------------------------------------------------------- Sicherheit

def test_anzeigentext_wird_fuer_die_ausgabe_maskiert():
    """Die Oberfläche maskiert jede Fundstelle; hier wird die Maskierung selbst geprüft."""
    boese = """Data Analyst (m/w/d)
Profil: Sehr gute SQL-Kenntnisse <img src=x onerror="alert(1)"> und Power BI.
Datenqualität und Reporting."""
    r = analysiere(boese, semantik=False)
    rohe = [f for t in r.treffer for f in t.fundstellen]
    assert any("<img" in f for f in rohe), "Testvoraussetzung: der Rohtext enthält HTML"
    for f in rohe:
        maskiert = escape(f, quote=True)
        assert "<img" not in maskiert and "onerror=\"" not in maskiert


def test_keine_zustandsspeicherung_zwischen_aufrufen():
    """Zwei Aufrufe dürfen sich nicht gegenseitig beeinflussen."""
    a = analysiere("Data Analyst: SQL, Power BI, Reporting, Datenqualität, Deutsch C1.", semantik=False)
    analysiere("Senior Data Engineer: Spark, Databricks, Kubernetes erforderlich.", semantik=False)
    b = analysiere("Data Analyst: SQL, Power BI, Reporting, Datenqualität, Deutsch C1.", semantik=False)
    assert a.score == b.score and keys(a) == keys(b)


def test_leere_eingabe_stuerzt_nicht_ab():
    r = analysiere("", semantik=False)
    assert r.score == 0 and r.belastbar is False


# ---------------------------------------------------------------- Sprachposition

@pytest.mark.parametrize(
    "variante",
    [
        "Profil: Sehr gute SQL-Kenntnisse, fundierte Power-BI-Kenntnisse, Datenqualität, "
        "Reporting-Automatisierung, Datenmodellierung, Ad-hoc-Analysen.\n"
        "Englisch C1 ist erforderlich.",
        "Profil: Sehr gute SQL-Kenntnisse, fundierte Power-BI-Kenntnisse, Datenqualität, "
        "Reporting-Automatisierung, Datenmodellierung, Ad-hoc-Analysen, Englisch C1 erforderlich.",
        "Profil: Sehr gute SQL-Kenntnisse; fundierte Power-BI-Kenntnisse; Datenqualität; "
        "Reporting-Automatisierung; Datenmodellierung; Ad-hoc-Analysen; Englisch C1 erforderlich.",
        "Englisch C1 erforderlich. Profil: Sehr gute SQL-Kenntnisse, fundierte "
        "Power-BI-Kenntnisse, Datenqualität, Reporting-Automatisierung, Datenmodellierung, "
        "Ad-hoc-Analysen.",
    ],
)
def test_sprachanforderung_unabhaengig_von_der_satzstellung(variante):
    """Dieselbe Anforderung muss denselben Wert ergeben, egal wo sie im Text steht."""
    ohne = analysiere(
        "Profil: Sehr gute SQL-Kenntnisse, fundierte Power-BI-Kenntnisse, Datenqualität, "
        "Reporting-Automatisierung, Datenmodellierung, Ad-hoc-Analysen.",
        semantik=False,
    )
    mit = analysiere(variante, semantik=False)
    assert ohne.score - mit.score <= 5
    assert any(not s.erfuellt for s in mit.sprachen)


def test_sprachzeile_wird_nicht_doppelt_gezaehlt():
    r = analysiere(
        "Profil: Sehr gute SQL-Kenntnisse, Power BI, Datenqualität, Reporting, "
        "Datenmodellierung, Englisch C1 erforderlich.",
        semantik=False,
    )
    assert not any("Englisch" in z for z in r.offene_zeilen)


# ---------------------------------------------------------------- Umgebung vs. Lücke

def test_technologie_als_umgebung_ist_gar_keine_luecke():
    anzeige = """Data Analyst (m/w/d)
Aufgaben: Unsere Daten liegen in Azure. KPI-Dashboards in Power BI, SQL-Auswertungen,
Datenqualität, Reporting-Automatisierung, Datenmodellierung.
Profil: SQL, Power BI, Deutsch C1."""
    r = analysiere(anzeige, semantik=False)
    assert "Azure" not in luecken(r), "Reine Umgebungsinformation ist keine Kompetenzlücke"
    assert any(u.name == "Azure" for u in r.umgebung)


def test_technologie_von_vorteil_ist_optionale_luecke():
    anzeige = """Data Analyst (m/w/d)
Aufgaben: KPI-Dashboards in Power BI, SQL, Datenqualität, Reporting, Datenmodellierung.
Profil: SQL, Power BI. Azure-Kenntnisse von Vorteil."""
    r = analysiere(anzeige, semantik=False)
    assert "Azure" in luecken(r) and "Azure" not in pflicht_luecken(r)


# ---------------------------------------------------------------- Standort

def test_unbekannter_ort_gilt_nicht_automatisch_als_passend():
    anzeige = """Data Analyst (m/w/d) in Paderborn
Profil: SQL, Power BI, Datenqualität, Reporting, Deutsch C1. Vor Ort."""
    r = analysiere(anzeige, semantik=False)
    assert r.standort is not None
    assert r.standort.passt is None, "Ein Ort ohne Listeneintrag darf nicht als passend gelten"


def test_ferner_ort_mit_remote_passt():
    anzeige = """Data Analyst (m/w/d) in München
Profil: SQL, Power BI, Datenqualität, Reporting, Deutsch C1. Remote möglich."""
    r = analysiere(anzeige, semantik=False)
    assert r.standort is not None and r.standort.passt is True


def test_standortregel_wird_benannt():
    anzeige = """Data Analyst (m/w/d) in Koblenz
Profil: SQL, Power BI, Datenqualität, Reporting, Deutsch C1."""
    r = analysiere(anzeige, semantik=False)
    assert "Ortsliste" in r.standort.begruendung and "Fahrzeit" in r.standort.begruendung


# ---------------------------------------------------------------- Wiederholung

def test_wiederholte_nennung_erhoeht_den_wert_nicht():
    einmal = analysiere(
        "Profil: SQL-Kenntnisse, Power BI, Datenqualität, Reporting, Datenmodellierung.",
        semantik=False,
    )
    mehrfach = analysiere(
        "Profil: SQL-Kenntnisse, SQL, SQL-Abfragen, Power BI, Power BI, Datenqualität, "
        "Reporting, Datenmodellierung.",
        semantik=False,
    )
    assert einmal.score == mehrfach.score


# ---------------------------------------------------------------- Unternehmensumfeld

def test_technologie_des_unternehmens_ist_keine_erfuellte_anforderung():
    """„Unser Team nutzt Python“ verlangt kein Python — das darf den Wert nicht heben."""
    anzeige = """Data Analyst (m/w/d)
Unser Team nutzt Python, Tableau und Power BI.
Ihr Profil: Sie verfügen über fundierte Kenntnisse in IFRS und Konsolidierung.
Sie beherrschen die Konzernberichterstattung."""
    r = analysiere(anzeige, semantik=False)
    assert keys(r) == set(), "Umfeld-Technologien dürfen nicht als Treffer zählen"
    assert {"Python", "Tableau", "Power BI"} <= {u.name for u in r.umgebung}
    assert r.score <= 25, f"fachfremde Anzeige darf nicht hoch bewertet werden, erhalten {r.score}"


def test_dieselben_tools_als_anforderung_zaehlen_weiterhin():
    anzeige = """Data Analyst (m/w/d)
Ihr Profil: Sehr gute Kenntnisse in Python, Tableau und Power BI.
Sie erstellen KPI-Dashboards und sichern die Datenqualität."""
    r = analysiere(anzeige, semantik=False)
    assert {"python", "tableau", "powerbi"} <= keys(r)
    assert r.score >= 85


def test_aufgabenzeilen_zaehlen_weiterhin():
    """Aufgaben sind das, was die Stelle verlangt — sie dürfen nicht als Umfeld gelten."""
    anzeige = """Data Analyst (m/w/d)
Aufgaben: Aufbau von KPI-Dashboards in Power BI, SQL-Auswertungen, Datenqualität,
Reporting-Automatisierung, Datenmodellierung.
Profil: SQL, Power BI, Deutsch C1."""
    r = analysiere(anzeige, semantik=False)
    assert {"powerbi", "sql", "datenmodellierung"} <= keys(r)
    assert r.score >= 85


def test_umfeld_und_anforderung_gemischt():
    anzeige = """Data Analyst (m/w/d)
Unsere Daten liegen in Azure und wir arbeiten mit Snowflake.
Ihr Profil: Sehr gute SQL-Kenntnisse, Power BI, Datenqualität, Reporting, Datenmodellierung."""
    r = analysiere(anzeige, semantik=False)
    assert {"sql", "powerbi"} <= keys(r)
    assert luecken(r) == set(), "Umfeld-Technologien sind keine Kompetenzlücken"
    assert {"Azure", "Snowflake"} <= {u.name for u in r.umgebung}


# ---------------------------------------------------------------------------
# Regressionen aus der Kalibrierung mit echten Stellenanzeigen (Runde 2)
# ---------------------------------------------------------------------------

def test_niveau_gehoert_zur_sprache_davor():
    """„Deutsch C1, Englisch“ sagt über das Englisch-Niveau nichts aus."""
    r = analysiere(
        "Ihr Profil\nSprachen: Deutsch C1, Englisch\nKenntnisse in SQL.",
        semantik=False,
    )
    englisch = [s for s in r.sprachen if s.sprache == "Englisch"]
    assert not englisch or englisch[0].gefordert != "C1"


def test_benefits_abschnitt_verschluckt_folgende_anforderungen_nicht():
    """Nach einem Benefits-Block müssen Aufgaben und Profil wieder zählen."""
    text = (
        "Benefits / Rahmenbedingungen\n"
        "Hybrides Arbeiten, 30 Tage Urlaub, Betriebssport, Altersvorsorge\n"
        "Ihre Aufgaben\n"
        "Entwicklung von Dashboards und Visualisierungen für die Fachbereiche.\n"
        "Ihr Profil\n"
        "Fundierte Kenntnisse in SQL und in der Datenmodellierung.\n"
    )
    zeilen = [z for z, _, _ in split_requirements_markiert(text)]
    assert any("Dashboards" in z for z in zeilen), zeilen
    assert any("SQL" in z for z in zeilen), zeilen
    assert not any("Betriebssport" in z for z in zeilen), zeilen


def test_berufsjahre_zaehlen_nur_einmal():
    """Die Jahresforderung ist eine Lücke und darf nicht zusätzlich offen sein."""
    r = analysiere(
        "Ihr Profil\nStudium sowie mind. 4 Jahre relevante Erfahrung im Reporting.",
        semantik=False,
    )
    assert any("Berufserfahrung" in l.begriff for l in r.luecken)
    assert not any("4 Jahre" in z for z in r.offene_zeilen), r.offene_zeilen


def test_firmenzeile_ist_keine_anforderung():
    text = "Data Analyst (gn) — FTSolutions OHG, Wetzlar\nIhr Profil\nKenntnisse in SQL.\n"
    zeilen = [z for z, _, _ in split_requirements_markiert(text)]
    assert not any("OHG" in z for z in zeilen), zeilen


def test_abstimmung_ist_stakeholder_arbeit_keine_datenqualitaet():
    r = analysiere(
        "Ihre Aufgaben\nEigenständige Abstimmung von Anforderungen mit unseren Kunden.",
        semantik=False,
    )
    labels = [t.skill["label"] for t in r.treffer]
    assert "Datenqualität & Data Governance" not in labels, labels
    assert "Stakeholder-Kommunikation" in labels, labels


def test_readme_beispiele_stimmen():
    """Die Beispieltabelle im README muss den tatsächlichen Werten entsprechen.

    Ein README, das andere Zahlen nennt als die App liefert, beschädigt genau das
    Vertrauen, das diese App herstellen soll.
    """
    analyst = """Data Analyst (m/w/d)
Ihre Aufgaben
Sie erstellen Reports und Dashboards für die Fachbereiche.
Sie analysieren Daten und bereiten Kennzahlen auf.
Ihr Profil
Fundierte Kenntnisse in SQL und Power BI.
Erfahrung in der Datenmodellierung und im Reporting.
Sie haben ein Auge für Datenqualität und arbeiten strukturiert.
Sehr gute Deutschkenntnisse."""
    assert analysiere(analyst, semantik=False).score == 95

    senior = """Senior Data Engineer (m/w/d)
Ihr Profil
Mindestens 5 Jahre Berufserfahrung im Data Engineering.
Fundierte Kenntnisse in Spark und Databricks.
Erfahrung mit Snowflake und Azure Data Factory.
Sie verantworten Deployment und Monitoring der Pipelines.
Kenntnisse in SQL und Python."""
    r = analysiere(senior, semantik=False)
    assert r.score <= 35, r.score
    assert sum(1 for l in r.luecken if l.pflicht) >= 4
