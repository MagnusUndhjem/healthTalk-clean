from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

client_secret = Path(__file__).parent / "client_secret.json"
token_path    = Path(__file__).parent / "token.json"

flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
creds = flow.run_local_server(port=0)        # åpner nettleser for Google‑login
token_path.write_text(creds.to_json(), encoding="utf‑8")
print("✅  token.json skrevet til", token_path.resolve())
