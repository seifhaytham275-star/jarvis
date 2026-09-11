"""
Gmail + Google Drive access for JARVIS.

These functions are passed straight into Gemini's `tools=[...]` list.
The google-genai SDK reads each function's type hints and docstring to build
the tool schema automatically, and executes them itself when the model
decides it needs to check email or Drive (Automatic Function Calling).

ONE-TIME SETUP REQUIRED — see GOOGLE_SETUP.md for the full walkthrough:
  1. Create a Google Cloud project, enable the Gmail API and Drive API.
  2. Create an OAuth Client ID of type "Desktop app", download it as
     credentials.json, and place it next to this file.
  3. First run will open a browser tab asking you to sign in and approve
     access — after that, a token.json is saved locally and reused.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def is_google_connected() -> bool:
    """True if we already have a stored, usable Google token."""
    return os.path.exists(TOKEN_FILE)


def get_google_creds() -> Credentials:
    """Load stored credentials, refreshing or running the OAuth flow as needed.

    NOTE: on first use this opens a browser window for you to approve access —
    only call it from an explicit "Connect Google" action, not silently.
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "credentials.json not found. Follow GOOGLE_SETUP.md to create one."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds


def search_gmail(query: str, max_results: int = 5) -> str:
    """Search the user's Gmail inbox and return matching emails.

    Args:
        query: A Gmail search query, e.g. "from:boss subject:invoice" or
            "is:unread newer_than:3d". Plain keywords also work.
        max_results: Maximum number of emails to return (default 5).

    Returns:
        A text summary of each matching email: sender, subject, date, and a
        short snippet of the body.
    """
    creds = get_google_creds()
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    messages = results.get("messages", [])

    if not messages:
        return "No matching emails found."

    lines = []
    for m in messages:
        msg = service.users().messages().get(
            userId="me",
            id=m["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        snippet = msg.get("snippet", "")

        lines.append(
            f"From: {headers.get('From', '?')}\n"
            f"Subject: {headers.get('Subject', '(no subject)')}\n"
            f"Date: {headers.get('Date', '?')}\n"
            f"Preview: {snippet}"
        )

    return "\n\n---\n\n".join(lines)


def search_drive(query: str, max_results: int = 5) -> str:
    """Search the user's Google Drive by file name or content.

    Args:
        query: Keywords to search for in file names or file contents.
        max_results: Maximum number of files to return (default 5).

    Returns:
        A text list of matching files with their name, type, and a link.
        Use read_drive_file with the returned file ID to read a file's contents.
    """
    creds = get_google_creds()
    service = build("drive", "v3", credentials=creds)

    safe_query = query.replace("'", "\\'")
    results = service.files().list(
        q=f"fullText contains '{safe_query}' or name contains '{safe_query}'",
        pageSize=max_results,
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
    ).execute()

    files = results.get("files", [])

    if not files:
        return "No matching files found."

    lines = [
        f"{f['name']} | id: {f['id']} | type: {f['mimeType']} | link: {f['webViewLink']}"
        for f in files
    ]
    return "\n".join(lines)


def read_drive_file(file_id: str) -> str:
    """Read the text content of a Google Drive file (Google Docs, or plain text files).

    Args:
        file_id: The Drive file ID, as returned by search_drive.

    Returns:
        The file's text content (truncated if very large).
    """
    creds = get_google_creds()
    service = build("drive", "v3", credentials=creds)

    meta = service.files().get(fileId=file_id, fields="mimeType, name").execute()
    mime = meta["mimeType"]

    if mime == "application/vnd.google-apps.document":
        data = service.files().export(fileId=file_id, mimeType="text/plain").execute()
    else:
        data = service.files().get_media(fileId=file_id).execute()

    text = data.decode("utf-8", errors="ignore") if isinstance(data, bytes) else str(data)
    return text[:8000]
