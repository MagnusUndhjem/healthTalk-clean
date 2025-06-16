# pages/03_Manuell_Oppdatering.py
import streamlit as st
import subprocess, sys, os
from pathlib import Path

st.set_page_config(page_title="HealthTalk - Manuell Oppdatering")
st.title("⚙️ Manuell oppdatering av artikkeldatabasen")

st.warning(
    "**Advarsel:** Denne prosessen kan ta flere minutter å fullføre. "
    "Ikke lukk dette vinduet mens den kjører."
)

ROOT_DIR = Path(__file__).parent.parent          # 👉 peker på prosjektroten

if st.button("🚀 Start manuell skraping nå!"):
    with st.status("Starter skrapeprosessen …", expanded=True) as status:
        try:
            st.write("Kjører `run_daily_scrape.py` …")

            process = subprocess.run(
                [sys.executable, str(ROOT_DIR / "run_daily_scrape.py")],
                cwd=ROOT_DIR,                       # kjør fra prosjektroten
                env=os.environ.copy(),              # arver .env / API-key
                capture_output=True,
                text=True,
                check=True,
            )

            # 👉 Vis både stdout *og* stderr
            st.write("Prosesslogg:")
            st.code(process.stdout + process.stderr)   # <-- begge strømmer

            status.update(label="✅ Skraping fullført!", state="complete", expanded=False)
            st.success("Databasen er oppdatert! Gå til «Artikkelarkiv» for å se de siste funnene.")
            st.balloons()

        except subprocess.CalledProcessError as e:
            status.update(label="❌ Skraping feilet!", state="error", expanded=True)
            st.error("Det oppstod en feil under kjøringen av skriptet.")
            st.code(e.stdout + e.stderr)

        except FileNotFoundError:
            status.update(label="❌ Finner ikke skriptet!", state="error", expanded=True)
            st.error("Kunne ikke finne `run_daily_scrape.py` i rotmappen.")
