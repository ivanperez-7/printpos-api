import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_credentials_path() -> Path:
    """Return the path to credentials.json.

    Priority:
    1. GMAIL_CREDENTIALS_PATH env var
    2. <project root>/credentials.json
    3. /etc/secrets/credentials.json (Render)
    """
    env = os.getenv('GMAIL_CREDENTIALS_PATH')
    if env:
        return Path(env)

    for candidate in [ROOT / 'credentials.json', Path('/etc/secrets/credentials.json')]:
        if candidate.exists():
            return candidate

    return ROOT / 'credentials.json'


def _resolve_token_path() -> Path:
    """Return a writable path for token.json.

    Priority:
    1. GMAIL_TOKEN_PATH env var
    2. <project root>/token.json
    """
    env = os.getenv('GMAIL_TOKEN_PATH')
    if env:
        return Path(env)

    return ROOT / 'token.json'


def _resolve_token_seed_path() -> Path | None:
    """Return the read-only seed path for token.json (Render secret files).

    Priority:
    1. GMAIL_TOKEN_SEED_PATH env var
    2. /etc/secrets/token.json
    """
    env = os.getenv('GMAIL_TOKEN_SEED_PATH')
    if env:
        return Path(env)

    p = Path('/etc/secrets/token.json')
    return p if p.exists() else None


def authenticate():
    creds = None
    credentials_path = _resolve_credentials_path()
    token_path = _resolve_token_path()

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    elif (seed := _resolve_token_seed_path()) is not None:
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_bytes(seed.read_bytes())
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())

    return creds
