
from PyPDF2 import PdfReader
import docx

def les_fil_innhold(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        tekst = ""
        for page in reader.pages:
            tekst += page.extract_text() + "\n"
        return tekst
    elif uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        tekst = "\n".join([para.text for para in doc.paragraphs])
        return tekst
    else:
        return ""
