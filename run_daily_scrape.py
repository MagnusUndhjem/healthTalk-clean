# fetch_articles_extract.py
import os
import json
import logging
from pathlib import Path
from datetime import date, timedelta
from urllib.parse import urljoin
import traceback

from dotenv import load_dotenv
import dateparser
from pydantic import BaseModel, Field
from firecrawl import FirecrawlApp

# ---------- konfig ---------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

PROSJEKT_ROT   = Path(__file__).parent
SOURCES_FILE   = PROSJEKT_ROT / "sources.txt"
SEEN_URLS_FILE = PROSJEKT_ROT / "seen_urls.json"
DATABASE_FILE  = PROSJEKT_ROT / "artikkel_database.json"

SOURCE_CONFIG = {
    "legemiddelverket.no": {"css_selector": ".PageContent_pageContent__3313R"},
    "dmp.no":              {"css_selector": "main#main-content"}
}

# ---------- schema for extract ---------- #
class Article(BaseModel):
    title: str
    url: str = Field(description="Canonical link to the article")
    published: str | None = Field(
        default=None,
        description="Publication date in ISO-8601 (YYYY-MM-DD) if available"
    )

class ArticleList(BaseModel):
    articles: list[Article]

SCHEMA = ArticleList.model_json_schema()

# ---------- Firecrawl-oppsett ---------- #
fc = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

def extract_with_firecrawl(url: str, css_selector: str | None = None) -> list[dict]:
    """
    Kjører /extract på én URL og returnerer listen av artikler (dicts).
    """
    # Bygg prompt dynamisk
    prompt_parts = [
        "Return an object with key 'articles'.",
        "For every news article on this page include:",
        "title, canonical URL (url), and published date in ISO format if you can find it.",
    ]
    if css_selector:
        prompt_parts.append(
            f"Only look inside the HTML element that matches the CSS selector '{css_selector}'."
        )
    prompt = " ".join(prompt_parts)

    resp = fc.extract(
        urls=[url],
        prompt=prompt,
        schema=SCHEMA,
    )

    # v2.7+: ExtractResponse har .data; eldre SDK gir dict – håndter begge
    raw = resp.data if hasattr(resp, "data") else resp.get("data", {})

    return raw.get("articles", [])

# ---------- hjelpe-funksjoner ---------- #
def last_inn_kilder() -> list[str]:
    if not SOURCES_FILE.exists():
        logging.error(f"{SOURCES_FILE} mangler.")
        return []
    return [l.strip() for l in SOURCES_FILE.read_text().splitlines() if l.strip()]

def last_inn_database() -> list[dict]:
    if DATABASE_FILE.exists():
        try:
            return json.loads(DATABASE_FILE.read_text())
        except json.JSONDecodeError:
            logging.warning("Kunne ikke lese artikkel-JSON – starter tom.")
    return []

def last_inn_sette_urls() -> set[str]:
    if SEEN_URLS_FILE.exists():
        try:
            return set(json.loads(SEEN_URLS_FILE.read_text()))
        except json.JSONDecodeError:
            logging.warning("Kunne ikke lese seen_urls – starter tom.")
    return set()

def lagre_data(db: list[dict], seen: set[str]):
    DATABASE_FILE.write_text(json.dumps(db, ensure_ascii=False, indent=2))
    SEEN_URLS_FILE.write_text(json.dumps(list(seen), indent=2))
    logging.info(f"Lagret {len(db)} artikler og {len(seen)} sett-URL-er.")

def er_nylig_artikkel(dato_str: str | None) -> bool:
    if not dato_str:
        return False
    try:
        parsed = dateparser.parse(dato_str, languages=["nb", "en"])
    except ValueError:
        return False
    if not parsed:
        return False
    return parsed.date() >= (date.today() - timedelta(days=3))

# ---------- hoved-løp ---------- #
def main():
    if not FIRECRAWL_API_KEY:
        logging.error("FIRECRAWL_API_KEY mangler i .env – avslutter.")
        return

    kilder       = last_inn_kilder()
    database     = last_inn_database()
    sette_urls   = last_inn_sette_urls()
    funn_total   = 0
    i_dag_iso    = date.today().isoformat()

    logging.info(f"Starter. DB={len(database)} artikler, "
                 f"{len(sette_urls)} tidligere URL-er.")

    for url in kilder:
        logging.info(f"--- Kilde: {url}")
        domain = url.split("//")[-1].split("/")[0]
        css    = SOURCE_CONFIG.get(domain, {}).get("css_selector")

        try:
            artikler = extract_with_firecrawl(url, css)
            if not artikler:
                logging.info("  (Ingen artikler funnet)")
                continue

            for art in artikler:
                art_url = art.get("url")
                if not art_url:
                    continue
                if not art_url.startswith("http"):
                    art_url = urljoin(url, art_url)
                    art["url"] = art_url

                if art_url in sette_urls:
                    continue

                if er_nylig_artikkel(art.get("published")):
                    # 🔄   Endrer feltnavn til de norsk-språklige som Streamlit-appen forventer
                    art["tittel"]       = art.pop("title", "Mangler tittel")
                    art["dato"]         = art.pop("published", None)
                    art["funnet_dato"]  = i_dag_iso          # beholder det gamle navnet

                    database.append(art)
                    funn_total += 1
                    logging.info(f"  ✅ Ny artikkel: {art['tittel']}")

                else:
                    logging.info(f"  -> Gammel artikkel ({art.get('published')})")

                sette_urls.add(art_url)

        except Exception as e:
            logging.error(f"Feil på {url}: {e}")
            logging.error(traceback.format_exc())

    logging.info("--- Ferdig ---")
    database.sort(key=lambda x: x.get("found_date", ""), reverse=True)
    lagre_data(database, sette_urls)
    logging.info(f"Totalt nye artikler denne kjøringen: {funn_total}")

if __name__ == "__main__":
    main()
