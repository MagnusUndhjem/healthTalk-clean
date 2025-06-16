
import requests
from bs4 import BeautifulSoup
import openai
from docx import Document
from dotenv import load_dotenv
import os
from generate_prompt import generate_prompt, generate_fallback_prompt
from config import OPENAI_API_KEY

load_dotenv()
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def hent_artikkeltekst(url):
    try:
        res = requests.get(url, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        # eks: EMA‑selector
        content_div = soup.select("div.ema-node-content-wrapper div.item")
        tekst = "\n\n".join(div.get_text(strip=True) for div in content_div)
        return tekst if tekst.strip() else None
    except Exception:
        return None

def generer_artikkel(råtekst, url, kategori="Legemidler", lengde="Middels"):
    # hvis råtekst mangler → lag fallback‑prompt
    if not råtekst:
        try:
            html = requests.get(url, timeout=15).text[:12000]  # maks 12 k tegn
        except Exception:
            html = ""
        prompt = generate_fallback_prompt(html, url, kategori, lengde)
    else:
        prompt = generate_prompt(råtekst, url, kategori, lengde)

    max_tok = 850
    if "366" in lengde: max_tok = 450
    elif "Lang" in lengde: max_tok = 1400

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Du er en erfaren helsejournalist for HealthTalk.no"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=max_tok,
    )
    return completion.choices[0].message.content

def lagre_som_docx(tekst, filnavn):
    doc = Document()
    for avsnitt in tekst.split("\n"):
        if avsnitt.strip():
            doc.add_paragraph(avsnitt)
    doc.save(filnavn)
