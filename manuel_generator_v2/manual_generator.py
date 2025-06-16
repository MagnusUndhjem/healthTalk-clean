# streamlit/manual_generator.py
import os
import sys
import datetime as dt
import streamlit as st
from dotenv import load_dotenv

# slik at vi kan importere fra common/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generate_articles import (
    hent_artikkeltekst,
    generer_artikkel,
)
from google_docs import last_opp_til_google_docs
from utils import les_fil_innhold  # håndterer PDF/DOCX

load_dotenv()
HOVED_MAPPE_ID = "DIN_MAPPE_ID"  # ← legg inn Drive-mappe for artikler

st.set_page_config(page_title="HealthTalk - Manuell AI-artikkel")

st.title("📰 Manuell AI-artikkelgenerator")

# -----------------------------------------------------------------
#  INPUTTYPE
# -----------------------------------------------------------------
input_type = st.radio("Velg type input", ["Lim inn tekst", "Lim inn URL", "Last opp fil"])
råtekst, url = "", ""

if input_type == "Lim inn tekst":
    råtekst = st.text_area("Lim inn teksten her", height=300)

elif input_type == "Lim inn URL":
    st.info(
        "⚠️ Direkte uthenting fra URL kan feile hvis siden er uvanlig. "
        "Hvis du får tomt resultat, kopier heller teksten manuelt."
    )
    url = st.text_input("Lim inn URL")
    if url and st.button("Hent tekst fra URL"):
        with st.spinner("Henter tekst ..."):
            hentet = hent_artikkeltekst(url)
        if hentet:
            råtekst = hentet
            st.success("✅ Tekst hentet!")
            st.text_area("Råtekst fra URL", value=råtekst, height=300)
        else:
            st.error("❌ Klarte ikke hente tekst. Kopier inn manuelt.")

elif input_type == "Last opp fil":
    file = st.file_uploader("Last opp PDF eller DOCX", type=["pdf", "docx"])
    if file:
        with st.spinner("Leser fil ..."):
            råtekst = les_fil_innhold(file)
        st.success("✅ Fil lest.")
        st.text_area("Råtekst fra fil", value=råtekst, height=300)

# -----------------------------------------------------------------
#  TILLEGGSVALG
# -----------------------------------------------------------------
st.subheader("Tilleggsvalg (frivillig)")

publ_dato = st.date_input("Publiseringsdato", value=dt.date.today())
nøkkelord = st.text_input("Nøkkelord (kommaseparert, valgfritt)")
kategori   = st.text_input("Kategori (valgfritt)")

lengdevalg = st.radio(
    "Ønsket artikkellengde",
    [
        "Notis (2-4 setninger)",
        "Kort (~366 tegn)",
        "Middels (~700 tegn)",
        "Lang (>1000 tegn)",
    ],
)

# -----------------------------------------------------------------
#  GENERER
# -----------------------------------------------------------------
if råtekst:
    tittel = st.text_input("Tittel til Google-Docs (valgfritt)", value="AI-generert artikkel")

    if st.button("🧠 Generer artikkel og last opp til Google Docs"):
        with st.spinner("Genererer artikkel med AI ..."):
            artikkel = generer_artikkel(
                råtekst,
                url=url or "",
                kategori=kategori if kategori.strip() else "Ukjent",
                lengde=lengdevalg,
            )

            try:
                link = last_opp_til_google_docs(
                    tittel or "AI-generert artikkel",
                    artikkel,
                    mappe_id=HOVED_MAPPE_ID,
                    dato=publ_dato,
                    nøkkelord=nøkkelord,
                )
                st.success("✅ Lastet opp!")
                st.markdown(f"[📄 Åpne dokumentet]({link})")
            except Exception as e:
                st.error(f"❌ Feil ved opplasting: {e}")
