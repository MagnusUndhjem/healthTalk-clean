import json
import streamlit as st
from pathlib import Path
from datetime import date, timedelta

# --- 1. Sidekonfigurasjon ---
# Setter tittelen som vises i nettleserfanen og på selve siden.
st.set_page_config(page_title="HealthTalk - Artikkelarkiv")
st.title("🔎 Artikkelarkiv fra automatiske søk")
st.write("Her finner du de siste artiklene som er funnet av overvåkningsroboten.")

# --- 2. Innlasting av data ---
# Finner stien til databasen. Path(__file__).parent.parent er en robust måte
# å finne rotmappen på, uansett hvor prosjektet ligger.
PROSJEKT_ROT = Path(__file__).parent.parent
DATABASE_FIL = PROSJEKT_ROT / "artikkel_database.json" 

# Laster inn hele databasen og håndterer feil hvis filen er tom eller korrupt.
alle_funn = []
if DATABASE_FIL.exists():
    try:
        with open(DATABASE_FIL, 'r', encoding='utf-8') as f:
            alle_funn = json.load(f)
    except json.JSONDecodeError:
        st.error(f"Kunne ikke lese datafilen ({DATABASE_FIL.name}). Den kan være korrupt.")
else:
    st.warning(f"Fant ingen datafil ({DATABASE_FIL.name}). Kjør en skraping for å opprette den.")

# --- 3. Brukergrensesnitt og filtrering ---
if not alle_funn:
    st.info("Artikkeldatabasen er tom. Ingen artikler å vise ennå.")
else:
    st.success(f"Databasen inneholder totalt {len(alle_funn)} unike artikler.")
    st.write("---")

    # Lager et interaktivt filter slik at journalisten kan velge dager.
    today = date.today()
    dato_valg = {
        "I dag": today.isoformat(),
        "I går": (today - timedelta(days=1)).isoformat(),
        "For 2 dager siden": (today - timedelta(days=2)).isoformat(),
        "For 3 dager siden": (today - timedelta(days=3)).isoformat(),
    }
    
    # Multiselect-widget lar brukeren velge flere dager (perfekt for mandager).
    valgte_dager_navn = st.multiselect(
        "Vis artikler funnet på følgende dager:",
        options=list(dato_valg.keys()),
        default=["I dag", "I går"] # Standardvalg som er mest nyttig.
    )

    # Filtrer listen basert på brukerens valg.
    filtrerte_funn = []
    if valgte_dager_navn:
        valgte_dato_iso = [dato_valg[navn] for navn in valgte_dager_navn]
        filtrerte_funn = [
            artikkel for artikkel in alle_funn 
            if artikkel.get("funnet_dato") in valgte_dato_iso
        ]
    
    st.write("---")

    # --- 4. Visning av resultater ---
    if not filtrerte_funn:
        st.write("Ingen artikler funnet for de valgte dagene.")
    else:
        st.subheader(f"Viser {len(filtrerte_funn)} artikler")
        
        # Sorterer listen slik at de nyeste funnene vises øverst.
        filtrerte_funn.sort(key=lambda x: x.get("funnet_dato", ""), reverse=True)

        # Går gjennom og viser hver eneste filtrerte artikkel.
        for artikkel in filtrerte_funn:
            tittel = artikkel.get("tittel", "Mangler tittel")
            url = artikkel.get("url", "#") # '#' som fallback hvis URL mangler.
            kilde_dato = artikkel.get("dato", "ukjent") # Datoen fra selve artikkelen.
            funnet_dato = artikkel.get("funnet_dato", "ukjent")

            # Bruker st.markdown for å lage en pen, formatert og klikkbar visning.
            st.markdown(
                f"""
                #### {tittel}
                **Kilde-URL:** [Åpne originalartikkel]({url})  
                *Funnet av roboten: {funnet_dato} (Original dato: {kilde_dato})*
                """
            )
            st.write("---") # Skillelinje for lesbarhet.