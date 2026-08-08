"""
auth.py
--------
Handles the full OAuth2 lifecycle for Google APIs:
1. First-time login (opens browser consent screen)
2. Token caching to disk (token.json)
3. Silent token refresh on expiry
4. Returns ready-to-use API service objects (Gmail + Sheets)

This is the ONLY file in the project that should touch raw
Google auth objects — every other module just imports the
functions below and gets a usable client.
"""

import os
import logging
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import gspread

from src.config import Config

logger = logging.getLogger(__name__)


def get_credentials() -> Credentials:
    """
    Retrieve valid Google API credentials, handling the full lifecycle:

    - If a cached token exists and is still valid -> use it.
    - If it's expired but has a refresh token -> refresh silently.
    - If no token exists at all -> run the interactive browser login
      (only happens once per machine, ever).

    Returns:
        google.oauth2.credentials.Credentials: authenticated credentials
        object usable by any Google API client.
    """
    Config.validate()
    creds = None
    token_path = Config.GOOGLE_TOKEN_PATH

    # Step 1: Try loading a previously saved token
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, Config.GMAIL_SCOPES)
        except Exception as e:
            logger.warning(f"Failed to load cached token from {token_path}: {e}")
            creds = None

    # Step 2: If no valid creds, either refresh or do a fresh login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Access token expired. Refreshing silently...")
                creds.refresh(Request())
            except RefreshError as e:
                logger.warning(f"Token refresh failed ({e}). Re-authenticating via browser...")
                creds = None

        if not creds or not creds.valid:
            logger.info("No valid token found. Launching browser for consent...")
            flow = InstalledAppFlow.from_client_secrets_file(
                Config.GOOGLE_CREDENTIALS_PATH, Config.GMAIL_SCOPES
            )
            # run_local_server spins up a temporary localhost server
            # to catch Google's OAuth redirect automatically.
            creds = flow.run_local_server(port=0)

        # Step 3: Persist the token to disk so we never have to
        # repeat the browser login again on this machine.
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())
        logger.info(f"Token saved to {token_path}")

    return creds


def get_gmail_service():
    """
    Build and return an authenticated Gmail API service object.

    Returns:
        googleapiclient.discovery.Resource: Gmail service client,
        used in Module 2 to fetch/parse emails.
    """
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


# Alias for backward compatibility / caller convenience
get_email_service = get_gmail_service


def get_sheets_client() -> gspread.Client:
    """
    Build and return an authenticated gspread client for Google Sheets.

    Returns:
        gspread.Client: used in Module 4 to write structured leads
        into a spreadsheet.
    """
    creds = get_credentials()
    return gspread.authorize(creds)