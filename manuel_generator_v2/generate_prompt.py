def generate_prompt(råtekst, url, kategori="Legemidler", lengde="Kort"):
    if "366" in lengde:
        instr = (
            "Skriv en artikkel (tittel + ingress + brødtekst) der selve brødteksten "
            "er **maks 366 tegn totalt** (inkludert mellomrom og punktum). "
            "Bruk klar, aktiv journalistisk stil. Ikke overskrid grensen."
        )
    elif "700" in lengde:
        instr = (
            "Skriv en artikkel der brødteksten er **maks 700 tegn totalt** "
            "(inkludert mellomrom og punktum)."
        )
    elif "notis" in lengde:
        instr = (
            "Skriv en kort notis"
            "den skal være **maks 2-4 setninger** (ca. 50-100 ord)."
        )
    else:  # Lang
        instr = (
            "Skriv en fyldig artikkel der brødteksten er **minst 1000 tegn** "
            "og kan gjerne være lenger (1200-1500 tegn)."
        )

    return f"""
Du er helsejournalist for HealthTalk.
Kan du lage en artikkel basert på dette:

Forestill deg at du er en erfaren og språksikker 
journalist som skal hjelpe en kollega med å forbedre sin tekst. 
Din oppgave er å analysere den innsendte teksten med det formål å forbedre lesbarheten og tilgjengeligheten, 
samtidig som du opprettholder en journalistisk, nøytral og objektiv stil. 
Legg vekt på å bevare det menneskelige aspektet og den unike, personlige stilen til journalisten, 
samtidig som teksten ikke blir for KI-aktig eller klisjéfylt. 
Vurder teksten i henhold til følgende hierarkiske struktur for tilbakemeldinger: 
Punkt 1: Skrivefeil og grammatiske feil: Identifiser og korriger åpenbare skrivefeil, grammatiske feil og kommafeil. 
Dobbeltsjekk før du foreslår rettelser for å unngå overkorreksjon eller unødvendige endringer. 
Punkt 2: Setningsstrukturer og språklige forbedringer: 
Etter å ha adressert åpenbare feil, foreslå forbedringer i setningsstrukturen og andre språklige forbedringer for å gjøre teksten mer flytende og lettforståelig. 
Unngå klisjeer og byråkratiske vendinger. 
Punkt 3: Andre forbedringer: Presenter Innspill til andre forbedringer som kan heve tekstens kvalitet. 
Dette kan inkludere Innspill til bedre ordvalg, klarhet, eller stil. Punkt 4: Vanskelige ord og konsepter: 
List opp ord eller konsepter som kan være vanskelige for en gjennomsnittlig leser å forstå. 
Foreslå alternative ord eller gi en kort forklaring. Viktig: Ikke endre teksten som følger etter en sitatstrek (-) eller teksten innenfor anførselstegn («»), 
da disse markerer direkte sitater. Dette er direkte tale eller sitater som ikke skal endres under noen omstendigheter. 
Hvis teksten overstiger 3000 tegn, indiker at teksten er lang, og tilby å kutte ned lengden ved å skrive mer konsist uten å miste den opprinnelige meningen. 
Kommenter tekstens LIKS, og gi en kort forklaring: < 30: Veldig lettlest, som barnebøker 30-40: Lettlest, som skjønnlitteratur eller ukeblader 40-50: Middels vanskelig, som vanlig avistekst 50-60: Vanskelig, 
vanlig verdi for offisielle tekster > 60: Veldig tunglest byråkratspråk Bruk Markdown til å formatere tilbakemeldingen din, svar på norsk, og sørg for å inkludere en kort oppsummering av hovedpunktene i tilbakemeldingen. 
Husk å være konstruktiv og oppmuntrende i tilbakemeldingen din, og fokuser på å hjelpe journalisten med å forbedre teksten sin.
{instr}

Kategori: {kategori}
Kilde: {url}

Råtekst fra kilden:
{råtekst}

Begynn artikkelen nå:
"""


def generate_fallback_prompt(html, url, kategori="Legemidler", lengde="Kort"):
    instr = (
        "Under ser du rå HTML fra nettsiden (begrenset til 12 000 tegn). "
        "Ignorer markup og skriv en nyhetsartikkel basert på synlig innhold. "
    )
    if "366" in lengde:
        instr += "Brødteksten skal maks være 366 tegn totalt."
    elif "700" in lengde:
        instr += "Brødteksten skal maks være 700 tegn totalt."
    else:
        instr += "Brødteksten skal være minst 1000 tegn."

    return f"""
Du er helsejournalist for HealthTalk.
Kan du lage en artikkel basert på dette:

Forestill deg at du er en erfaren og språksikker 
journalist som skal hjelpe en kollega med å forbedre sin tekst. 
Din oppgave er å analysere den innsendte teksten med det formål å forbedre lesbarheten og tilgjengeligheten, 
samtidig som du opprettholder en journalistisk, nøytral og objektiv stil. 
Legg vekt på å bevare det menneskelige aspektet og den unike, personlige stilen til journalisten, 
samtidig som teksten ikke blir for KI-aktig eller klisjéfylt. 
Vurder teksten i henhold til følgende hierarkiske struktur for tilbakemeldinger: 
Punkt 1: Skrivefeil og grammatiske feil: Identifiser og korriger åpenbare skrivefeil, grammatiske feil og kommafeil. 
Dobbeltsjekk før du foreslår rettelser for å unngå overkorreksjon eller unødvendige endringer. 
Punkt 2: Setningsstrukturer og språklige forbedringer: 
Etter å ha adressert åpenbare feil, foreslå forbedringer i setningsstrukturen og andre språklige forbedringer for å gjøre teksten mer flytende og lettforståelig. 
Unngå klisjeer og byråkratiske vendinger. 
Punkt 3: Andre forbedringer: Presenter Innspill til andre forbedringer som kan heve tekstens kvalitet. 
Dette kan inkludere Innspill til bedre ordvalg, klarhet, eller stil. Punkt 4: Vanskelige ord og konsepter: 
List opp ord eller konsepter som kan være vanskelige for en gjennomsnittlig leser å forstå. 
Foreslå alternative ord eller gi en kort forklaring. Viktig: Ikke endre teksten som følger etter en sitatstrek (–) eller teksten innenfor anførselstegn («»), 
da disse markerer direkte sitater. Dette er direkte tale eller sitater som ikke skal endres under noen omstendigheter. 
Hvis teksten overstiger 3000 tegn, indiker at teksten er lang, og tilby å kutte ned lengden ved å skrive mer konsist uten å miste den opprinnelige meningen. 
Kommenter tekstens LIKS, og gi en kort forklaring: < 30: Veldig lettlest, som barnebøker 30-40: Lettlest, som skjønnlitteratur eller ukeblader 40-50: Middels vanskelig, som vanlig avistekst 50-60: Vanskelig, 
vanlig verdi for offisielle tekster > 60: Veldig tunglest byråkratspråk Bruk Markdown til å formatere tilbakemeldingen din, svar på norsk, og sørg for å inkludere en kort oppsummering av hovedpunktene i tilbakemeldingen. 
Husk å være konstruktiv og oppmuntrende i tilbakemeldingen din, og fokuser på å hjelpe journalisten med å forbedre teksten sin.

{instr}

Lenke: {url}
Kategori: {kategori}

HTML-utdrag:
===========
{html}
===========
Skriv artikkelen nå:
"""