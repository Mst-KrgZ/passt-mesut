"""
Kompetenzprofil Mesut Karagöz — belegbasierte Datengrundlage für das Matching.

Jede Kompetenz ist mit einem Nachweis verknüpft (Zertifikatsstunden und/oder Projekt).
Grundlage: claude/Skill_Evidence_Matrix_Mesut.md

Regel: Hier steht nur, was belegt ist. `NICHT_VORHANDEN` listet bewusst, was NICHT
behauptet wird — das Matching meldet diese Punkte offen als Lücke, statt sie zu
überspielen.
"""

PERSON = {
    "name": "Mesut Karagöz",
    "titel": "Data Analyst (IHK) | Business Intelligence | Data Scientist",
    "standort": "Neuwied, Rheinland-Pfalz",
    "regionen": ["NRW", "Rheinland-Pfalz", "Hessen"],
    "arbeitsmodell": ["Vor Ort", "Hybrid", "Remote"],
    "sprachen": {"Deutsch": "C1", "Türkisch": "Muttersprache", "Englisch": "B1"},
    "email": "mesutkrgz65@gmail.com",
    "portfolio": "https://mesutkaragoez.de",
    "github": "https://github.com/Mst-KrgZ",
    "linkedin": "https://www.linkedin.com/in/mesut-karagoz/",
}

GH = "https://github.com/Mst-KrgZ"

# Projekte, auf die sich die Nachweise beziehen
PROJEKTE = {
    "kfz": {
        "name": "Kfz Insurance Risk & Pure Premium Platform",
        "repo": f"{GH}/kfz-insurance-risk-platform",
        "demo": None,
        "kurz": "678.013 Policen · Poisson-/Gamma-GLM · Tweedie Pure Premium · PostgreSQL · FastAPI · Power BI",
    },
    "bankdq": {
        "name": "Banking Data Quality Monitoring",
        "repo": f"{GH}/banking-data-quality-monitoring",
        "demo": "https://banking-data-quality-monitoring-eaxfftumawvnsotzdp4zhd.streamlit.app/",
        "kurz": "17 Prüfregeln · 6 Qualitätsdimensionen · Precision/Recall gegen Ground Truth · CI mit pytest und ruff",
    },
    "superstore": {
        "name": "Superstore Profitabilitätsanalyse (IHK-Abschlussprojekt)",
        "repo": f"{GH}/superstore-profitability-analysis",
        "demo": None,
        "kurz": "Teamprojekt, Projektleitung · KNIME-ETL · Power-BI-Sternschema · Handlungsempfehlungen",
    },
    "churn": {
        "name": "Bank Customer Churn Prediction",
        "repo": f"{GH}/bank-churn-prediction-ml-system",
        "demo": "https://huggingface.co/spaces/mesut-karagoz/Bank-Churn-Prediction-ML-System",
        "kurz": "CatBoost · SMOTE · ROC-AUC 0,865 · FastAPI · Docker",
    },
    "chatbot": {
        "name": "Analytics Chatbot (RAG + SQL)",
        "repo": f"{GH}/amazon-analytics-chatbot",
        "demo": "https://amazon-analytics-chatbot-exwrkjj8deznlaytmjxndj.streamlit.app/",
        "kurz": "RAG-Pipeline · FAISS · Sentence Transformers · SQLite · Streamlit",
    },
    "forecast": {
        "name": "Revenue Forecasting Decision System",
        "repo": f"{GH}/amazon-revenue-forecasting-decision-system",
        "demo": "https://amazon-revenue-forecasting-decision-system-wdk7lpkyjp7xqhj3mry.streamlit.app/",
        "kurz": "SARIMA · Prophet · XGBoost · LSTM · Ensemble · Konfidenzintervalle",
    },
    "rfm": {
        "name": "RFM & CLV Customer Analytics",
        "repo": f"{GH}/RFM-CLV-Amazon-Analytics",
        "demo": "https://rfm-clv-amazon-analytics-8hzh8knruybc98ebuvkz8v.streamlit.app/",
        "kurz": "RFM-Segmentierung · Kohortenanalyse · CLV-Prognose · Streamlit",
    },
    "buybox": {
        "name": "Buy Box Prediction System",
        "repo": f"{GH}/amazon-buybox-prediction-system",
        "demo": "https://amazon-buybox-prediction-system-kpda7qdr6sdcvmf64gfvti.streamlit.app/",
        "kurz": "XGBoost · LightGBM · Ensemble · 70+ Features · Modellvergleich",
    },
    "cv": {
        "name": "Product Image Classifier",
        "repo": f"{GH}/amazon-computer-vision-classifier",
        "demo": None,
        "kurz": "MobileNetV2 · Transfer Learning · TensorFlow/Keras",
    },
    "sentiment": {
        "name": "Product Review Sentiment Analysis",
        "repo": f"{GH}/amazon-product-review-sentiment-analysis",
        "demo": "https://amazon-appuct-review-sentiment-analysis-jdrlrfa4eesoktbk2gwwgu.streamlit.app/",
        "kurz": "Stimmung, Beschwerdegrund und Belegphrase je Rezension · BERT · KeyBERT · 574 ausgewertete Rezensionen",
    },
    "crosssell": {
        "name": "Cross-Sell Recommendation System",
        "repo": f"{GH}/amazon-cross-sell-recommendation-system",
        "demo": "https://amazon-cross-sell-recommendation-system-tex9appawawubsi5dwkxsd.streamlit.app/",
        "kurz": "Apriori · Association Rules · Netzwerkvisualisierung",
    },
    "olist": {
        "name": "Olist E-Commerce Analytics",
        "repo": f"{GH}/olist-ecommerce-analysis",
        "demo": "https://olist-ecommerce-analysis-xtrytimgbgkgnqla2e5grv.streamlit.app/",
        "kurz": "Lieferperformance · Kundenzufriedenheit · Umsatzanalyse · Streamlit",
    },
    "stroke": {
        "name": "Stroke Risk Analytics Dashboard",
        "repo": f"{GH}/stroke-risk-analytics-dashboard",
        "demo": "https://stroke-risk-analytics-dashboard-dpstthrybrupoh7c9wdkkv.streamlit.app/",
        "kurz": "Hypothesengetrieben · Mann-Whitney-U · Chi-Quadrat · Stratifizierung",
    },
    "credit": {
        "name": "Credit Risk Analysis (MySQL)",
        "repo": f"{GH}/credit-risk-analysis-MySQL",
        "demo": None,
        "kurz": "MySQL-Regellogik mit CASE und Views · Risikosegmentierung · Power BI",
    },
    "marketing": {
        "name": "Marketing Campaign ML",
        "repo": f"{GH}/marketing-campaign-ml",
        "demo": None,
        "kurz": "Kundenanalyse · Clustering · Klassifikation · businessorientierte Bewertung",
    },
    "amazonbi": {
        "name": "Amazon Sales & Marketplace Analytics (Power BI)",
        "repo": f"{GH}/amazon-sales-analytics-powerbi-optimization-forecasting",
        "demo": None,
        "kurz": "Mehrseitige Power-BI-Dashboards · DAX · PPC-Optimierung · Funnel · Stock Planning",
    },
}

# Stärke: 5 = sehr hoch, 4 = hoch, 3 = mittel-hoch, 2 = Grundlagen, 1 = nur auf Nachfrage
SKILLS = [
    # ---------------- Daten & Datenbanken ----------------
    {
        "key": "sql", "label": "SQL", "kategorie": "Daten & Datenbanken", "staerke": 5,
        "aliases": ["sql", "structured query language", "sql-kenntnisse", "sql abfragen", "abfragesprache",
                    "datenbankabfragen", "queries", "joins", "stored procedures", "views", "cte"],
        "beleg": "DataSmart-Modulzertifikat 288 UE · TechPro 138 Std.",
        "projekte": ["kfz", "credit", "bankdq"],
    },
    {
        "key": "postgresql", "label": "PostgreSQL", "kategorie": "Daten & Datenbanken", "staerke": 4,
        "aliases": ["postgresql", "postgres", "psql"],
        "beleg": "Analytics-Layer der Kfz-Plattform in PostgreSQL",
        "projekte": ["kfz"],
    },
    {
        "key": "mysql", "label": "MySQL", "kategorie": "Daten & Datenbanken", "staerke": 4,
        "aliases": ["mysql", "mariadb"],
        "beleg": "Regelbasierte Kreditrisikoanalyse mit CASE-Logik und Views",
        "projekte": ["credit"],
    },
    {
        "key": "datenmodellierung", "label": "Datenmodellierung", "kategorie": "Daten & Datenbanken", "staerke": 4,
        "aliases": ["datenmodellierung", "data modeling", "datenmodell", "sternschema", "star schema",
                    "dimensionale modellierung", "fakten", "dimensionen", "semantisches modell",
                    "data warehouse", "datawarehouse", "dwh", "data mart", "datenarchitektur",
                    "modellierung im data warehouse", "datenquellen"],
        "beleg": "Sternschema im Superstore-Projekt · analytisches Datenmodell in der Kfz-Plattform",
        "projekte": ["superstore", "kfz"],
    },
    {
        "key": "etl", "label": "ETL / Datenaufbereitung", "kategorie": "Daten & Datenbanken", "staerke": 4,
        "aliases": ["etl", "elt", "data engineering", "datenpipeline", "datenstrecke",
                    "datenaufbereitung", "datenintegration", "data preparation", "data wrangling",
                    "datenbereinigung", "data cleaning", "datentransformation", "data transformation", "datenpipeline", "data pipeline",
                    "ingestion", "datenaufbereitungsprozesse"],
        "beleg": "Ingestion-, Curated- und Feature-Schichten der Kfz-Plattform · KNIME-ETL im Superstore-Projekt",
        "projekte": ["kfz", "superstore", "bankdq"],
    },
    {
        "key": "datenqualitaet", "label": "Datenqualität & Data Governance", "kategorie": "Daten & Datenbanken", "staerke": 5,
        "aliases": ["datenqualität", "data quality", "datenqualitätsmanagement", "plausibilitätsprüfung",
                    "konsistenzprüfung", "vollständigkeitsprüfung", "data governance", "datenvalidierung",
                    "qualitätssicherung", "kontenabstimmung", "reconciliation", "datenbereinigung"],
        "beleg": "17 Prüfregeln über 6 Qualitätsdimensionen, messbar gegen dokumentierte Ground Truth",
        "projekte": ["bankdq", "kfz"],
    },
    {
        "key": "excel", "label": "Excel", "kategorie": "Daten & Datenbanken", "staerke": 4,
        "aliases": ["excel", "ms excel", "microsoft excel", "pivot", "pivottabellen", "tabellenkalkulation",
                    "power query", "google sheets", "spreadsheets"],
        "beleg": "Excel-Abschlussprojekt der Weiterbildung · Übergabeschichten in Superstore und Banking DQ",
        "projekte": ["superstore", "bankdq"],
    },

    # ---------------- Programmierung ----------------
    {
        "key": "python", "label": "Python", "kategorie": "Programmierung", "staerke": 5,
        "aliases": ["python", "python3", "pandas", "numpy", "scikit-learn", "sklearn", "skriptsprache",
                    "programmierkenntnisse", "jupyter", "notebooks"],
        "beleg": "DataSmart-Modulzertifikat 413 UE · TechPro 183 Std. · in allen Projekten eingesetzt",
        "projekte": ["kfz", "bankdq", "churn", "forecast"],
    },
    {
        "key": "git", "label": "Git / GitHub", "kategorie": "Programmierung", "staerke": 4,
        "aliases": ["git", "github", "gitlab", "versionskontrolle", "version control", "versionierung",
                    "pull request", "code review"],
        "beleg": "26 öffentliche Repositories · CI-Workflow im Banking-DQ-Projekt",
        "projekte": ["bankdq", "kfz"],
    },
    {
        "key": "testing", "label": "Testing & CI/CD", "kategorie": "Programmierung", "staerke": 3,
        "aliases": ["testing", "unit tests", "pytest", "ci/cd", "continuous integration", "github actions",
                    "automatisierte tests", "linting", "ruff", "code quality"],
        "beleg": "pytest-Suite, ruff und GitHub-Actions-Workflow im Banking-DQ-Projekt",
        "projekte": ["bankdq", "kfz"],
    },
    {
        "key": "r", "label": "R", "kategorie": "Programmierung", "staerke": 1,
        "aliases": [" r ", "r-programmierung", "rstudio", "tidyverse"],
        "beleg": "Kursmodul im Google Data Analytics Professional Certificate",
        "projekte": [],
    },
    {
        "key": "web", "label": "HTML / CSS / JavaScript", "kategorie": "Programmierung", "staerke": 3,
        "aliases": ["html", "css", "javascript", "frontend", "webentwicklung", "web development"],
        "beleg": "Udemy 26,5 Std. · Coursera · TechPro 54 Std. · eigene Portfolio-Website",
        "projekte": [],
    },

    # ---------------- Business Intelligence ----------------
    {
        "key": "powerbi", "label": "Power BI", "kategorie": "Business Intelligence", "staerke": 5,
        "aliases": ["power bi", "powerbi", "pbi", "power-bi", "dax", "power query", "microsoft power bi",
                    "berichtswesen power bi"],
        "beleg": "DataSmart-Modulzertifikat 200 UE · TechPro 90 Std. · mehrere mehrseitige Dashboards",
        "projekte": ["kfz", "superstore", "amazonbi", "credit"],
    },
    {
        "key": "tableau", "label": "Tableau", "kategorie": "Business Intelligence", "staerke": 4,
        "aliases": ["tableau", "tableau desktop", "tableau public"],
        "beleg": "Coursera UC Davis · TechPro 78 Std. · Tableau-Public-Profil",
        "projekte": [],
    },
    {
        "key": "dashboards", "label": "Dashboards & Visualisierung", "kategorie": "Business Intelligence", "staerke": 5,
        "aliases": ["dashboard", "dashboards", "visualisierung", "datenvisualisierung", "data visualization",
                    "visualisierungen", "reports", "berichte", "berichtswesen", "plotly", "charts", "grafiken"],
        "beleg": "Power-BI-, Tableau- und Streamlit-Dashboards in über zehn Projekten",
        "projekte": ["amazonbi", "bankdq", "rfm", "olist"],
    },
    {
        "key": "kpi", "label": "KPI-Definition & Reporting", "kategorie": "Business Intelligence", "staerke": 5,
        "aliases": ["kpi", "kpis", "kennzahlen", "kennzahlensystem", "reporting", "management reporting",
                    "monatsreporting", "regelreporting", "reportingprozesse", "kpi-logik", "steuerungskennzahlen",
                    "berichtserstellung"],
        "beleg": "KPI-Katalog und automatisierter Excel-Monatsreport im Banking-DQ-Projekt",
        "projekte": ["bankdq", "amazonbi", "superstore"],
    },
    {
        "key": "automatisierung", "label": "Reporting-Automatisierung", "kategorie": "Business Intelligence", "staerke": 4,
        "aliases": ["automatisierung", "automatisiertes reporting", "report automation", "prozessautomatisierung",
                    "automatisierte berichte", "openpyxl", "workflow automation"],
        "beleg": "Automatisierter Excel-Monatsreport (openpyxl) · Ein-Klick-Aktualisierung der Kfz-Pipeline",
        "projekte": ["bankdq", "kfz"],
    },
    {
        "key": "knime", "label": "KNIME", "kategorie": "Business Intelligence", "staerke": 3,
        "aliases": ["knime", "knime analytics platform", "low code", "no code", "low-code", "visuelle datenanalyse"],
        "beleg": "Bestandteil des IHK-Moduls · fachliche Begleitung des Teams im Superstore-Projekt",
        "projekte": ["superstore"],
    },

    # ---------------- Statistik & Analyse ----------------
    {
        "key": "statistik", "label": "Statistik & statistische Modellierung", "kategorie": "Statistik & Analyse", "staerke": 5,
        "aliases": ["statistik", "statistisch", "statistics", "statistische methoden",
                    "statistische analyse", "statistiksoftware", "empirisch", "hypothesentest",
                    "signifikanz", "regression", "regressionsanalyse", "regressionsmodell",
                    "multivariat", "multivariate analyse", "varianzanalyse", "faktorenanalyse",
                    "treiberanalyse", "glm", "verteilungen", "korrelation", "inferenz",
                    "wahrscheinlichkeitsrechnung", "mathematik", "stichprobe", "gewichtung"],
        "beleg": "Poisson-, Gamma- und Tweedie-GLM mit Deviance-, D²- und Gini-Bewertung · Physikstudium",
        "projekte": ["kfz", "stroke"],
    },
    {
        "key": "abtest", "label": "A/B-Testing & Effektstärke", "kategorie": "Statistik & Analyse", "staerke": 4,
        "aliases": ["a/b-test", "a/b testing", "ab-test", "experimentdesign", "testdesign", "effektstärke",
                    "effect size", "signifikanztest", "conversion-tests"],
        "beleg": "A/B-Tests und Effektstärkenanalyse im E-Commerce-Umfeld · Effect-Size-Seiten im Power-BI-Dashboard",
        "projekte": ["amazonbi"],
    },
    {
        "key": "eda", "label": "Explorative Datenanalyse", "kategorie": "Statistik & Analyse", "staerke": 5,
        "aliases": ["eda", "explorative datenanalyse", "exploratory data analysis", "datenanalyse",
                    "ad-hoc-analysen", "ad hoc analysen", "auswertungen", "datenauswertung", "analyse von daten"],
        "beleg": "EDA-Notebooks in nahezu allen Projekten · EDA-Module in beiden Weiterbildungen",
        "projekte": ["kfz", "olist", "stroke"],
    },
    {
        "key": "rootcause", "label": "Root-Cause- & Ursachenanalyse", "kategorie": "Statistik & Analyse", "staerke": 4,
        "aliases": ["root cause", "root-cause-analyse", "ursachenanalyse", "fehleranalyse", "problemanalyse",
                    "abweichungsanalyse", "diagnostik"],
        "beleg": "Root-Cause-Analysen für stornierte Bestellungen · Fehleranalyse-Seite im Banking-DQ-Dashboard",
        "projekte": ["bankdq", "amazonbi"],
    },
    {
        "key": "crm", "label": "Kundenanalytik & CRM-Daten", "kategorie": "Statistik & Analyse", "staerke": 4,
        "aliases": ["crm", "crm-system", "kundenmanagement", "kundendaten", "customer relationship",
                    "kundenanalyse", "kundenanalytik", "customer analytics", "kundenverhalten",
                    "customer insights", "kundenbindung", "churn", "abwanderung", "clv",
                    "customer lifetime value", "kundenwert", "bestandskunden", "salesforce-daten"],
        "beleg": "RFM- und CLV-Analyse auf 9.745 Kunden · Churn-Prognose mit CatBoost "
                 "(ROC-AUC 0,865) · Kohortenanalyse und Kundensegmentierung",
        "projekte": ["rfm", "churn"],
    },
    {
        "key": "segmentierung", "label": "Segmentierung & Clustering", "kategorie": "Statistik & Analyse", "staerke": 4,
        "aliases": ["segmentierung", "kundensegmentierung", "clustering", "k-means", "customer segmentation",
                    "risikosegmentierung", "zielgruppensegmentierung", "rfm"],
        "beleg": "RFM-Segmentierung · Risikosegmentierung über Tweedie-Score · Clustering im Marketing-Projekt",
        "projekte": ["rfm", "kfz", "marketing"],
    },

    # ---------------- Machine Learning ----------------
    {
        "key": "ml", "label": "Machine Learning", "kategorie": "Machine Learning", "staerke": 5,
        "aliases": ["machine learning", "maschinelles lernen", "ml", "predictive analytics",
                    "prognosemodelle", "klassifikation", "classification", "supervised learning",
                    "modellvergleich", "feature engineering", "scikit-learn", "xgboost", "lightgbm", "catboost",
                    "random forest", "gradient boosting"],
        "beleg": "TechPro 189 Std. · neun verglichene Algorithmen im Churn-Projekt · Ensembles im Buy-Box-Modell",
        "projekte": ["churn", "buybox", "kfz", "marketing"],
    },
    {
        "key": "forecasting", "label": "Zeitreihen & Forecasting", "kategorie": "Machine Learning", "staerke": 4,
        "aliases": ["forecasting", "zeitreihen", "zeitreihenanalyse", "time series", "prognose", "vorhersage",
                    "absatzprognose", "bedarfsprognose", "demand planning", "sarima", "arima", "prophet",
                    "saisonalität", "trendanalyse"],
        "beleg": "SARIMA, Prophet, XGBoost und LSTM im Vergleich, inklusive Konfidenzintervallen",
        "projekte": ["forecast", "amazonbi"],
    },
    {
        "key": "deeplearning", "label": "Deep Learning", "kategorie": "Machine Learning", "staerke": 4,
        "aliases": ["deep learning", "neuronale netze", "neural networks", "tensorflow", "keras", "pytorch",
                    "cnn", "lstm", "rnn", "transfer learning"],
        "beleg": "TechPro 111 Std. · MobileNetV2-Transfer-Learning · LSTM im Forecasting-Projekt",
        "projekte": ["cv", "forecast"],
    },
    {
        "key": "nlp", "label": "NLP & Textanalyse", "kategorie": "Machine Learning", "staerke": 4,
        "aliases": ["nlp", "natural language processing", "textanalyse", "text mining", "sentiment",
                    "sentimentanalyse", "bert", "transformer", "sprachverarbeitung", "embeddings"],
        "beleg": "TechPro 21 Std. · transformerbasierte Sentiment-Klassifikation · Embeddings im RAG-Chatbot",
        "projekte": ["sentiment", "chatbot"],
    },
    {
        "key": "genai", "label": "GenAI, LLM & RAG", "kategorie": "Machine Learning", "staerke": 4,
        "aliases": ["genai", "generative ai", "generative ki", "llm", "large language model", "rag",
                    "retrieval augmented generation", "prompt engineering", "ki-anwendungen", "chatbot",
                    "openai", "langchain", "vektordatenbank", "faiss", "ai agents", "ki-gestützt",
                    "ki-gestützte entwicklung", "github copilot", "copilot", "ai coding",
                    "ki-unterstützt", "künstliche intelligenz", "ki"],
        "beleg": "RAG-Pipeline mit FAISS und Sentence Transformers · AI-Literacy-Zertifikat · KI-gestützte Entwicklung",
        "projekte": ["chatbot"],
    },
    {
        "key": "computervision", "label": "Computer Vision", "kategorie": "Machine Learning", "staerke": 4,
        "aliases": ["computer vision", "bildverarbeitung", "bilderkennung", "image classification",
                    "bildklassifikation", "mobilenet", "opencv"],
        "beleg": "TechPro 45 Std. · Produktbild-Klassifikation mit MobileNetV2",
        "projekte": ["cv"],
    },
    {
        "key": "recommender", "label": "Empfehlungssysteme", "kategorie": "Machine Learning", "staerke": 3,
        "aliases": ["empfehlungssystem", "recommender", "recommendation", "warenkorbanalyse",
                    "market basket", "apriori", "association rules", "cross-selling"],
        "beleg": "Apriori-basiertes Cross-Sell-System mit Support-, Confidence- und Lift-Bewertung",
        "projekte": ["crosssell"],
    },

    # ---------------- Deployment & Tooling ----------------
    {
        "key": "streamlit", "label": "Streamlit", "kategorie": "Deployment & Tooling", "staerke": 5,
        "aliases": ["streamlit", "dash", "gradio", "datenapp", "data app", "web-app für analysen"],
        "beleg": "Neun öffentlich erreichbare Streamlit-Anwendungen",
        "projekte": ["bankdq", "rfm", "forecast", "olist"],
    },
    {
        "key": "fastapi", "label": "FastAPI / REST-Schnittstellen", "kategorie": "Deployment & Tooling", "staerke": 4,
        "aliases": ["fastapi", "rest api", "rest-api", "api", "apis", "schnittstellen", "api-entwicklung",
                    "webservice", "endpoint", "flask", "swagger", "openapi", "json"],
        "beleg": "FastAPI-Schnittstellen in der Kfz-Plattform und im Churn-System · DSP-Modulblock zu API-Schnittstellen",
        "projekte": ["kfz", "churn"],
    },
    {
        "key": "docker", "label": "Docker", "kategorie": "Deployment & Tooling", "staerke": 3,
        "aliases": ["docker", "container", "containerisierung", "docker-compose", "kubernetes-grundlagen"],
        "beleg": "Dockerfile und docker-compose im Churn-System · TechPro-Deployment-Modul",
        "projekte": ["churn"],
    },
    {
        "key": "aws", "label": "AWS (Grundlagen)", "kategorie": "Deployment & Tooling", "staerke": 2,
        "aliases": ["aws", "amazon web services", "s3", "rds", "sagemaker", "cloud", "cloud-dienste",
                    "cloud computing"],
        "beleg": "TechPro 15 Std.: Grundlagen, S3, RDS, SageMaker — Ausbildungsniveau, keine Produktionserfahrung",
        "projekte": [],
    },
    {
        "key": "webscraping", "label": "Web Scraping", "kategorie": "Deployment & Tooling", "staerke": 3,
        "aliases": ["web scraping", "webscraping", "crawling", "beautifulsoup", "scrapy", "datenbeschaffung"],
        "beleg": "TechPro 9 Std. · dreiwöchiger Vollzeitblock in der DataSmart-Weiterbildung",
        "projekte": [],
    },
    {
        "key": "jira", "label": "Agiles Arbeiten (Scrum, Jira)", "kategorie": "Deployment & Tooling", "staerke": 3,
        "aliases": ["jira", "scrum", "agil", "agile", "kanban", "sprints", "sdlc", "confluence",
                    "agiles projektmanagement"],
        "beleg": "TechPro SDLC- und Jira-Module · Sprint-Struktur in den Amazon-Analytics-Projekten",
        "projekte": ["amazonbi"],
    },

    # ---------------- Fachlich & persönlich ----------------
    {
        "key": "stakeholder", "label": "Stakeholder-Kommunikation", "kategorie": "Fachlich & persönlich", "staerke": 5,
        "aliases": ["stakeholder", "kommunikation", "präsentation", "präsentationsfähigkeit", "schnittstelle",
                    "fachbereiche", "fachabteilungen", "adressatengerecht", "verständlich aufbereiten",
                    "zusammenarbeit mit fachbereichen", "storytelling", "data storytelling", "beratung",
                    "handlungsempfehlungen", "entscheidungsvorlagen", "entscheidungsunterstützung",
                    "empfehlungen ableiten", "kommunikationsfähigkeit", "kommunikationsstärke", "abstimmung", "anforderungsabstimmung"],
        "beleg": "Über zehn Jahre Unterrichtserfahrung · Handlungsempfehlungen und Abschlusspräsentationen in jedem Projekt",
        "projekte": ["superstore", "bankdq"],
    },
    {
        "key": "studium", "label": "Akademischer Hintergrund", "kategorie": "Fachlich & persönlich", "staerke": 4,
        "aliases": ["studium", "hochschulabschluss", "akademischer abschluss", "bachelor", "master",
                    "abgeschlossenes studium", "naturwissenschaft", "naturwissenschaften", "physik",
                    "mathematik", "quantitativer schwerpunkt", "quantitativ", "vergleichbare qualifikation",
                    "vergleichbarer abschluss", "mint"],
        "beleg": "B.Sc. Physik (İstanbul Üniversitesi), von der KMK/ZAB als deutscher Hochschulabschluss "
                 "auf Bachelor-Ebene anerkannt · zusätzlich Data Analyst (IHK)",
        "projekte": [],
    },
    {
        "key": "analytik", "label": "Analytisches Denken & strukturierte Arbeitsweise",
        "kategorie": "Fachlich & persönlich", "staerke": 5,
        "aliases": ["analytisches denken", "analytisches denkvermögen", "analytische fähigkeiten",
                    "analytische denkweise", "analytisches arbeiten", "abstraktionsvermögen",
                    "strukturierte arbeitsweise", "strukturierte analyse", "strukturiertes vorgehen", "strukturierte vorgehensweise", "selbstständige arbeitsweise", "sorgfältig",
                    "selbstständig", "eigenverantwortlich", "gewissenhaft", "lernbereitschaft",
                    "problemlösungskompetenz", "problemlösung",
                    "lösungsorientiert", "sorgfalt", "genauigkeit", "zahlenaffinität", "zahlenverständnis",
                    "konzeptionelles denken", "eigenständige arbeitsweise", "detailgenauigkeit"],
        "beleg": "Physikstudium (B.Sc., als deutscher Bachelor anerkannt) · durchgängig dokumentierte, "
                 "reproduzierbare Projektarbeit mit offen ausgewiesenen Limitationen",
        "projekte": ["kfz", "stroke"],
    },
    {
        "key": "projektleitung", "label": "Projektleitung & Koordination", "kategorie": "Fachlich & persönlich", "staerke": 4,
        "aliases": ["projektleitung", "projektmanagement", "koordination", "teamleitung", "projektverantwortung",
                    "projektsteuerung", "führung", "teamführung", "projektverantwortlich"],
        "beleg": "Projektleitung im vierköpfigen IHK-Abschlussprojekt inklusive fachlicher Unterstützung des Teams",
        "projekte": ["superstore"],
    },
    {
        "key": "dokumentation", "label": "Dokumentation & Fachkonzepte", "kategorie": "Fachlich & persönlich", "staerke": 5,
        "aliases": ["dokumentation", "fachkonzept", "spezifikation", "anforderungsanalyse", "requirements",
                    "prozessdokumentation", "model card", "datenkatalog", "data dictionary"],
        "beleg": "14 Dokumente in der Kfz-Plattform: Model Card, Data Dictionary, Architektur, Wochenstatusberichte",
        "projekte": ["kfz", "bankdq"],
    },
    {
        "key": "banking", "label": "Banken- & Finanzdomäne", "kategorie": "Domänen", "staerke": 3,
        "aliases": ["bank", "banken", "bankenumfeld", "bankensektor", "kreditinstitut", "sparkasse",
                    "volksbank", "finanzdienstleistung", "kreditrisiko", "einlagen", "portfolio",
                    "finanzwesen", "finanzumfeld", "kredit", "risikomanagement", "meldewesen", "finanzsektor"],
        "beleg": "Banking Data Quality Monitoring (Regionalbank-Szenario) · Credit Risk Analysis · Churn-Prognose",
        "projekte": ["bankdq", "credit", "churn"],
    },
    {
        "key": "versicherung", "label": "Versicherungsdomäne", "kategorie": "Domänen", "staerke": 3,
        "aliases": ["versicherung", "versicherungen", "aktuariat", "schadenfrequenz", "schadenhöhe",
                    "pure premium", "underwriting", "tarifierung", "kfz-versicherung", "risikobewertung"],
        "beleg": "Kfz-Risikoplattform: Frequency-, Severity- und Tweedie-Modellierung auf 678.013 Policen",
        "projekte": ["kfz"],
    },
    {
        "key": "ecommerce", "label": "E-Commerce & Handel", "kategorie": "Domänen", "staerke": 4,
        "aliases": ["e-commerce", "ecommerce", "onlinehandel", "handel", "retail", "marktplatz", "amazon",
                    "warenwirtschaft", "einzelhandel", "pricing", "sortiment"],
        "beleg": "Praktische Tätigkeit im E-Commerce-Umfeld · über zehn Amazon-Analytics-Projekte",
        "projekte": ["rfm", "buybox", "amazonbi", "olist"],
    },
    # Sprachen werden bewusst NICHT als Kompetenz gezählt, sondern im eigenen Abschnitt
    # „Sprachanforderungen“ geführt. Sonst entsteht der unsinnige Fall, dass eine Anzeige
    # Englisch C1 verlangt und das Profil mit „Englisch B1“ als Treffer erscheint.
]

# Was ausdrücklich NICHT behauptet wird. Taucht eines davon in der Anzeige auf,
# meldet die App es offen als Lücke.
NICHT_VORHANDEN = {
    "databricks": "Databricks", "snowflake": "Snowflake", "sap": "SAP", "sap bw": "SAP BW",
    "azure": "Azure", "microsoft fabric": "Microsoft Fabric", "fabric": "Microsoft Fabric",
    "spark": "Apache Spark", "pyspark": "PySpark", "hadoop": "Hadoop", "kafka": "Kafka",
    "airflow": "Apache Airflow", "dbt": "dbt", "kubernetes": "Kubernetes", "terraform": "Terraform",
    "qlik": "Qlik", "qliksense": "Qlik Sense", "looker": "Looker", "micated": "",
    "cognos": "IBM Cognos", "sas": "SAS", "spss": "SPSS", "matlab": "MATLAB",
    "salesforce": "Salesforce", "dynamics": "MS Dynamics", "google analytics": "Google Analytics",
    "google cloud": "Google Cloud", "gcp": "Google Cloud", "bigquery": "BigQuery",
    "scala": "Scala", "java": "Java", "c#": "C#", ".net": ".NET", "abap": "ABAP",
    "talend": "Talend", "informatica": "Informatica", "ssis": "SSIS", "ssas": "SSAS",
}
NICHT_VORHANDEN = {k: v for k, v in NICHT_VORHANDEN.items() if v}

# ---------------------------------------------------------------------------
# Branchenkontext
#
# Belegte Branchenerfahrung: Versicherung, Bankwesen, E-Commerce/Handel.
# Für alle anderen Branchen gilt: keine direkte Erfahrung, aber die eingesetzten
# Methoden sind branchenunabhängig. Das wird offen gesagt statt verschwiegen —
# und fliesst bewusst NICHT in den Wert ein, weder positiv noch negativ.
# ---------------------------------------------------------------------------

BELEGTE_BRANCHEN = ["Versicherung", "Bankwesen", "E-Commerce und Handel"]

# Kompetenz-Keys, deren Treffer eine belegte Branchenerfahrung anzeigen
BRANCHEN_SKILLS = {
    "versicherung": "Versicherung",
    "banking": "Bankwesen",
    "ecommerce": "E-Commerce und Handel",
}

FREMDE_BRANCHEN = {
    "pharma": "Pharma & Life Sciences",
    "pharmaindustrie": "Pharma & Life Sciences",
    "life science": "Pharma & Life Sciences",
    "biotech": "Pharma & Life Sciences",
    "automotive": "Automobilindustrie",
    "automobil": "Automobilindustrie",
    "automobilindustrie": "Automobilindustrie",
    "fahrzeugbau": "Automobilindustrie",
    "energiewirtschaft": "Energiewirtschaft",
    "energieversorger": "Energiewirtschaft",
    "netzbetreiber": "Energiewirtschaft",
    "stadtwerke": "Energiewirtschaft",
    "logistik": "Logistik & Supply Chain",
    "supply chain": "Logistik & Supply Chain",
    "spedition": "Logistik & Supply Chain",
    "gesundheitswesen": "Gesundheitswesen",
    "klinik": "Gesundheitswesen",
    "krankenhaus": "Gesundheitswesen",
    "krankenkasse": "Gesundheitswesen",
    "maschinenbau": "Industrie & Produktion",
    "produktion": "Industrie & Produktion",
    "fertigung": "Industrie & Produktion",
    "werksleitung": "Industrie & Produktion",
    "telekommunikation": "Telekommunikation",
    "öffentlicher dienst": "Öffentlicher Sektor",
    "behörde": "Öffentlicher Sektor",
    "kommunal": "Öffentlicher Sektor",
    "immobilien": "Immobilienwirtschaft",
    "tourismus": "Tourismus",
    "medien": "Medien",
    "bildung": "Bildung",
    "chemie": "Chemie",
    "lebensmittel": "Lebensmittelindustrie",
    "luftfahrt": "Luftfahrt",
    "bauwesen": "Bauwesen",
    "baugewerbe": "Bauwesen",
    "agrar": "Agrarwirtschaft",
    "landwirtschaft": "Agrarwirtschaft",
    "textil": "Textilindustrie",
    "mobilität": "Mobilität & Verkehr",
    "verkehr": "Mobilität & Verkehr",
    "bahn": "Mobilität & Verkehr",
    "sport": "Sport",
    "consulting": "Beratung",
    "unternehmensberatung": "Beratung",
    "wirtschaftsprüfung": "Wirtschaftsprüfung",
    "steuerberatung": "Steuerberatung",
    "personaldienstleistung": "Personaldienstleistung",
    "non-profit": "Non-Profit",
    "verband": "Verbände",
}

# Allgemeine Formulierungen, die auf eine geforderte Branchenerfahrung hindeuten,
# auch wenn die Branche selbst nicht in der Liste oben steht.
BRANCHEN_SIGNAL = [
    "branchenerfahrung", "branchenkenntnis", "erfahrung in der branche",
    "kenntnisse der branche", "einschlägige branchenerfahrung", "branchenwissen",
]

# Branchenspezifische Regelwerke und Normen: nicht vorhanden, aber erlernbar.
# Erscheinen im Branchenkontext, nicht als Kompetenzlücke.
REGELWERKE = {
    "gxp": "GxP", "gmp": "GMP", "fda": "FDA-Anforderungen", "iso 13485": "ISO 13485",
    "edifact": "EDIFACT", "marisk": "MaRisk", "bait": "BAIT", "basel": "Basel-Rahmenwerk",
    "solvency": "Solvency II", "ifrs": "IFRS", "hgb": "HGB", "gobd": "GoBD",
    "iatf": "IATF 16949", "iso 9001": "ISO 9001", "reach": "REACH",
}

TRANSFER_SATZ = (
    "Keine direkte Branchenerfahrung — die eingesetzten Methoden sind jedoch "
    "branchenunabhängig und in drei verschiedenen Branchen nachgewiesen: "
    "Versicherung (Risikomodellierung auf 678.013 Policen), Bankwesen "
    "(Datenqualität und Managementreporting) und E-Commerce (Umsatz-, "
    "Profitabilitäts- und Kundenanalysen). Ein Portfolio, das denselben "
    "Werkzeugkasten in drei Domänen zeigt, ist der Beleg dafür, dass eine "
    "vierte kein Hindernis ist."
)

SKILL_BY_KEY = {s["key"]: s for s in SKILLS}
