"""
config.py
----------
Centralized configuration loader.
Keeps all environment-dependent values in ONE place so nothing
is hardcoded across the codebase — a core clean-code principle.
"""

import os
from dotenv import load_dotenv

# Load variables from .env into the process environment
load_dotenv()


class Config:
    """Holds all runtime configuration pulled from environment variables."""

    GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    GOOGLE_TOKEN_PATH: str = os.getenv("GOOGLE_TOKEN_PATH", "token.json")

    # Scopes are stored as a comma-separated string in .env,
    # so we split them into the list format Google's SDK expects.
    GMAIL_SCOPES: list[str] = os.getenv("GMAIL_SCOPES", "").split(",")

    GEMINI_API_KEY:str=os.getenv("GEMINI_API_KEY","")
    GEMINI_MODEL_NAME:str=os.getenv("GEMINI_MODEL_NAME","gemini-flash-latest")



    @classmethod
    def validate(cls) -> None:
        """
        Fail loudly and early if required config is missing.
        Better to crash at startup with a clear message than
        halfway through processing a client's inbox.
        """
        if not cls.GMAIL_SCOPES or cls.GMAIL_SCOPES == [""]:
            raise ValueError("GMAIL_SCOPES is not set in .env")
        if not os.path.exists(cls.GOOGLE_CREDENTIALS_PATH):
            raise FileNotFoundError(
                f"credentials.json not found at '{cls.GOOGLE_CREDENTIALS_PATH}'. "
                "Download it from Google Cloud Console → Auth Platform → Clients."
            )
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in .env")
            