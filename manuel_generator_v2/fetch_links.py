from datetime import date, timedelta
from typing import List, Union
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from firecrawl import FirecrawlApp

# 1) API-nøkkel fra .env
load_dotenv()                 # .env må ha FIRECRAWL_API_KEY=fc-xxxx
app = FirecrawlApp()          # nøkkelen plukkes automatisk

# 2) Kildeliste
with open("sources.txt") as f:
    sources = [ln.strip() for ln in f if ln.strip()]

# 3) Dato­filter
today = date(2025, 6, 15)
dates = {today.isoformat(),
         (today - timedelta(days=1)).isoformat(),
         (today - timedelta(days=2)).isoformat()}

# 4) Pydantic-schema
class Article(BaseModel):
    title: str
    url: str = Field(description="Canonical article link")
    published: str = Field(description="Publication date YYYY-MM-DD")

class ArticlePage(BaseModel):
    articles: List[Article]

schema = ArticlePage.model_json_schema()

prompt = (
    "Return an object called 'articles'. "
    f"Include every news article on this page whose publication date is "
    f"exactly one of these ISO dates: {', '.join(sorted(dates))}. "
    "For each article return: title, canonical URL (url), published."
)

# 5) Kall /extract  (én posisjonell parameter = URL-listen)
resp = app.extract(
    sources,
    prompt=prompt,
    schema=schema,
)

# 6) Hent data på tvers av SDK-versjoner
if hasattr(resp, "data"):            # nye SDK 2.7+ ➜ ExtractResponse
    raw = resp.data
else:                                # eldre SDK 2.6- ➜ dict
    raw = resp.get("data", resp)

pages = raw if isinstance(raw, list) else [raw]

links = [
    art["url"]
    for page in pages
    for art in page.get("articles", [])
    if art["published"] in dates
]

print(f"\nFant {len(links)} artikler fra 13.–15. juni 2025:\n")
print("\n".join(links))
