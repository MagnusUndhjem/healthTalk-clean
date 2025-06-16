import streamlit as st
import openai
import os
from dotenv import load_dotenv

# --- KONFIGURASJON OG OPPSETT ---

st.set_page_config(page_title="Bildegenerator for Artikler", layout="wide")
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = openai.OpenAI(api_key=api_key)
else:
    client = None

# --- FUNKSJONER FOR AI-KALL ---

def create_visual_prompt_from_text(article_text: str, style: str, adjustments: dict) -> str | None:
    """
    Bygger en dynamisk bildeprompt basert på input og valgte justeringer.
    """
    
    # **NYTT: Velger en helt annen system-prompt hvis minimalistisk modus er valgt.**
    if adjustments.get('is_minimalist'):
        system_prompt = f"""
        You are a minimalist concept artist creating an iconic, symbolic image. Your task is to:
        1. Read the article and identify the SINGLE most important, symbolic object (e.g., a pill, a specific molecule, a syringe, a white blood cell, a microchip).
        2. Create a detailed prompt for a clean, minimalist studio shot of ONLY this object.

        The image style should be: **{style}**.
        - The object must be isolated and the main focus.
        - Describe a clean, simple, and often neutral background.
        - Specify professional studio lighting (e.g., "soft studio lighting," "dramatic side-lighting").
        - The prompt MUST NOT describe a complex scene with multiple elements or people.
        """
    else:
        # Standard system-prompt for fulle scener
        system_prompt = f"""
        You are an expert photo editor for a prestigious news agency. Create a prompt for an image with a **{style}** style, that looks authentic and grounded in reality.
        - Describe a clear, specific scene with a focus on realism.
        - Specify lighting, composition, and mood.
        - AVOID: Generic AI-clichés and sterile scenes.
        """

    # Bygg en liste med tilleggsinstruksjoner
    directives = []
    if adjustments.get('is_background') and not adjustments.get('is_minimalist'):
        directives.append("- The image MUST NOT contain any people or faces. It is a background shot.")
        directives.append("- Compose the shot with intentional negative space for post-production.")
    
    if adjustments.get('use_bokeh'):
        directives.append("- Use a shallow depth of field to create a soft, aesthetically pleasing blurry background (photographic bokeh).")
        
    # Legg til justeringene i prompten
    if directives:
        system_prompt += "\n\n**Additional Directives:**\n" + "\n".join(directives)

    system_prompt += "\n\nYour final output must be ONLY the detailed prompt in ENGLISH, nothing else."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Article text:\n\n{article_text}"}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Feil under analyse av tekst: {e}")
        return None

def generate_images(prompt: str, num_images: int) -> list[str] | None:
    # Denne funksjonen er uendret
    image_urls = []
    try:
        progress_text = "Genererer bilder... (Dette kan ta litt tid)"
        progress_bar = st.progress(0, text=progress_text)
        
        for i in range(num_images):
            response = client.images.generate(
                model="dall-e-3", prompt=prompt, n=1,
                size="1792x1024", quality="hd", response_format="url"
            )
            image_urls.append(response.data[0].url)
            progress_bar.progress((i + 1) / num_images, text=progress_text)
        
        progress_bar.empty()
        return image_urls
    except openai.APIError as e:
        st.error(f"En feil oppstod hos OpenAI: {e}")
        return None
    except Exception as e:
        st.error(f"En uventet feil oppstod: {e}")
        return None

# --- STREAMLIT BRUKERGRENSESNITT ---

st.title("🎨 Bildegenerator for Artikler")
st.markdown("Lim inn en artikkeltekst, velg stil og justeringer, og få forslag til bilder fra DALL-E 3.")

if not client:
    st.error("🔴 **FEIL:** `OPENAI_API_KEY` er ikke satt.")
    st.stop()

article_text = st.text_area(
    "**Trinn 1: Lim inn artikkelteksten her**", height=250,
    placeholder="Lim inn teksten fra en nyhetsartikkel..."
)

st.divider()

st.subheader("Trinn 2: Velg bildestil")
col1, col2 = st.columns(2)
with col1:
    image_style = st.selectbox(
        "**Stil**", ("Fotorealistisk", "Dokumentarisk/Reportasje", "Cinematic", "Nøytral/Corporate"),
        help="Bestemmer den visuelle tonen i bildet."
    )
with col2:
    num_images = st.number_input(
        "**Antall bilder**", min_value=1, max_value=4, value=2, step=1
    )

st.divider()

st.subheader("Trinn 3: Juster komposisjon (valgfritt)")
# **UI for justeringer, inkludert det nye valget**
col_a, col_b, col_c = st.columns(3)
with col_a:
    adj_is_minimalist = st.checkbox("Minimalistisk / Ikonisk bilde", value=False, help="Fokuserer på ett enkelt, symbolsk objekt mot en ren bakgrunn. Overstyrer 'Bakgrunnsbilde'.")
with col_b:
    # Deaktiverer "bakgrunnsbilde" hvis minimalistisk er valgt, da de er motstridende
    adj_is_background = st.checkbox("Lag bakgrunnsbilde (ingen personer)", value=False, help="Lager en scene uten mennesker.", disabled=adj_is_minimalist)
with col_c:
    adj_use_bokeh = st.checkbox("Bruk uskarp bakgrunn (bokeh)", value=False, help="Skaper en profesjonell, fotografisk effekt.")

st.divider()

generate_button = st.button("🚀 **Trinn 4: Generer Bilder**", type="primary", use_container_width=True)

if generate_button:
    if not article_text.strip():
        st.warning("Vennligst lim inn en tekst i tekstfeltet over.")
    else:
        adjustments = {
            "is_minimalist": adj_is_minimalist,
            "is_background": adj_is_background,
            "use_bokeh": adj_use_bokeh
        }
        
        with st.spinner("🤖 Analyserer teksten og bygger en skreddersydd bildebeskrivelse..."):
            visual_prompt = create_visual_prompt_from_text(article_text, image_style, adjustments)
        
        if visual_prompt:
            st.info(f"**Bildeprompt sendt til DALL-E 3:**\n\n> *{visual_prompt}*")
            
            with st.spinner("🎨 DALL-E 3 maler bildene dine..."):
                image_urls = generate_images(visual_prompt, num_images)

            if image_urls:
                st.success("🎉 Bildene er klare! Høyreklikk på et bilde for å lagre det.")
                
                cols = st.columns(num_images)
                for i, url in enumerate(image_urls):
                    with cols[i]:
                        st.image(url, caption=f"Forslag {i+1}", use_container_width=True)