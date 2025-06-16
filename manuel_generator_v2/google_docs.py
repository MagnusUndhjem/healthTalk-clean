# google_docs.py
import os
from pathlib import Path
from datetime import date
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

HERE = Path(__file__).parent
TOKEN_FILE = HERE / "token.json"
CLIENT_SECRET = HERE / "client_secret.json"


def _get_credentials() -> Credentials:
    """Hent gyldige Google-credentials, eller åpne nettleser-flow første gang."""
    if TOKEN_FILE.exists():
        return Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not CLIENT_SECRET.exists():
        raise FileNotFoundError(
            "client_secret.json mangler. Plasser den i samme mappe som google_docs.py"
        )

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def _get_or_create_month_folder(drive, parent_folder_id: str, dato: date) -> str:
    """Returner undermappe-ID for YYYY-MM – opprett den hvis den ikke finnes."""
    ym = dato.strftime("%Y-%m")  # f.eks. "2025-05"

    query = (
        f"mimeType='application/vnd.google-apps.folder' "
        f"and name='{ym}' and '{parent_folder_id}' in parents and trashed=false"
    )
    resp = drive.files().list(q=query, fields="files(id, name)").execute()
    if resp["files"]:
        return resp["files"][0]["id"]

    meta = {
        "name": ym,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id],
    }
    folder_id = drive.files().create(body=meta, fields="id").execute()["id"]
    return folder_id


def last_opp_til_google_docs(
    tittel: str,
    innhold: str,
    mappe_id: str,
    dato: date,
    nøkkelord: str = "",
) -> str:
    """
    Opprett Google-dokument med innhold og legg det i undermappe YYYY-MM under mappe_id.
    Returnerer delbar lenke.
    """
    creds = _get_credentials()

    drive = build("drive", "v3", credentials=creds)
    docs = build("docs", "v1", credentials=creds)

    # 1) Sørg for korrekt månedsmappe
    month_folder_id = _get_or_create_month_folder(drive, mappe_id, dato)

    # 2) Lag dokumentet
    doc_meta = {"title": tittel}
    doc = docs.documents().create(body=doc_meta).execute()
    doc_id = doc["documentId"]

    # 3) Flytt dokumentet til månedsmappe
    drive.files().update(
        fileId=doc_id,
        addParents=month_folder_id,
        removeParents="root",
        fields="id, parents",
    ).execute()

    # 4) Skriv innhold
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": innhold,
                    }
                }
            ]
        },
    ).execute()

    # 5) Lagre nøkkelord som description (valgfritt)
    if nøkkelord.strip():
        drive.files().update(
            fileId=doc_id,
            body={"description": nøkkelord},
        ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"
