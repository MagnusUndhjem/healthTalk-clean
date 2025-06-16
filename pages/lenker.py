import streamlit as st
from pathlib import Path

# Definer stien til sources.txt
PROSJEKT_ROT = Path(__file__).parent.parent
SOURCES_FILE = PROSJEKT_ROT / "sources.txt"

st.set_page_config(page_title="HealthTalk - Administrer Kilder")
st.title("⚙️ Administrer Overvåkningskilder")
st.write("Her kan du legge til eller fjerne nettadresser i `sources.txt` som roboten skal sjekke.")

# --- Funksjoner for å lese og skrive til fil ---

def last_inn_kilder_fra_fil():
    """Laster inn alle kilder fra sources.txt"""
    if not SOURCES_FILE.exists():
        return []
    with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
        # Vi bruker set for å automatisk håndtere duplikater, og sorterer for pen visning
        return sorted(list(set([line.strip() for line in f if line.strip() and not line.startswith('#')])))

def lagre_kilder_til_fil(kilder):
    """Skriver en liste med kilder til sources.txt, og overskriver den gamle filen."""
    with open(SOURCES_FILE, 'w', encoding='utf-8') as f:
        for kilde in sorted(kilder):
            f.write(f"{kilde}\n")

# --- Streamlit-grensesnitt ---

# Last inn nåværende kilder
kilder = last_inn_kilder_fra_fil()

st.subheader("Nåværende kilder i `sources.txt`")
# Viser alle kildene i en boks som ikke kan redigeres
st.text_area("Kilder:", value="\n".join(kilder), height=250, disabled=True)

st.write("---")

# --- Seksjon for å legge til ny kilde ---
st.subheader("➕ Legg til en ny kilde")
ny_kilde = st.text_input("Lim inn full URL her (f.eks. https://www.vg.no):", key="ny_kilde_input")

if st.button("Lagre ny kilde"):
    if ny_kilde and ny_kilde.strip():
        # Sjekk om kilden allerede eksisterer for å unngå duplikater
        if ny_kilde.strip() not in kilder:
            kilder.append(ny_kilde.strip())
            lagre_kilder_til_fil(kilder)
            st.success(f"✅ La til '{ny_kilde.strip()}' i sources.txt!")
            st.rerun() # Laster siden på nytt for å vise den oppdaterte listen
        else:
            st.warning("Denne kilden finnes allerede i listen.")
    else:
        st.error("Du må skrive inn en URL.")

st.write("---")

# --- Seksjon for å fjerne kilder ---
st.subheader("❌ Fjern en eller flere kilder")
kilder_a_fjerne = st.multiselect(
    "Velg kildene du vil fjerne:",
    options=kilder
)

if st.button("Fjern valgte kilder", type="primary"):
    if kilder_a_fjerne:
        # Lager en ny liste som er lik den gamle, minus de som skal fjernes
        oppdaterte_kilder = [k for k in kilder if k not in kilder_a_fjerne]
        lagre_kilder_til_fil(oppdaterte_kilder)
        st.success("Kildene ble fjernet!")
        st.rerun() # Laster siden på nytt
    else:
        st.warning("Du må velge minst én kilde for å fjerne.")