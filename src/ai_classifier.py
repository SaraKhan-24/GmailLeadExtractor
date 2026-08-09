import logging
from typing import Optional,Literal
from google import genai
from google.genai import types
from pydantic  import BaseModel, Field, ValidationError
from src.config import Config

logger=logging.getLogger(__name__)

#One client instance will be reused accross every classification call
_client=genai.Client(api_key=Config.GEMINI_API_KEY)

class LeadData(BaseModel):
    """
    This is the exact scheme that is enforced by the Gemini API at 
    generation time.
    """
    is_lead:bool = Field(
        description="True if this email is a genuine sales inquiry or"
                    "business opportunity. False for newsletters, receipts,"
                    "spam, or personal correspondence."
    )
    name: Optional[str]=Field(
        default=None, description="Sender's full name, if mentioned or inferable."
    )
    email: Optional[str]=Field(
        default=None, description="Sender's contact email address."
    )
    budget: Optional[str]=Field(
        default=None, description="Any budget or price figure mentioned, as written "
                                "(e.g. '$5,000','2000 USD'). Null if not mentioned."
    )
    priority: Literal["High","Medium", "Low"]=Field(
        description="Urgency/value of this lead. High=clear budget + "
        "urgent timeline. Medium = interested but vague. "
        "Low = casual inquiry or unclear intent."
    )
    summary: str = Field(
        description="One-sentence plain-English summary of what the sender wants."
    )

"""
The system instruction controls the model's behavior accross every call.
"""
_SYSTEM_INSTRUCTION="""
You are a strict data-extraction engine for a sales team's inbox.
Given the raw text of an email, extract lead information according to the schema.

Rules:
-If the email is clearly not a business inquiry (newsletter, receipt, spam,
    automated notification), set is_lead to false and leave other fields as 
    best-effort or null- donot fabricate data.
- Never invent a budget or name that isnt stated or strongly implied.
- Priority should reflect the genuine urgency signals in the text (deadlines,
    explicit budget, "ASAP" language) - not just a guess.
- Keep the summary factual under 20 words.
"""

def classify_email(subject:str, body:str, max_retries: int=2) -> Optional[LeadData]:
    """
    Send a single email's content to Gemini and return structured lead data.
    """
    #Gemini has token limits and long emails add cost for no extra signal-
    #most lead intent is clear in the first 2000 characters.

    truncated_body=body[:2000]
    prompt=f"Subject: {subject}\n\nBody:\n{truncated_body}"

    for attempt in range (1, max_retries+1):
        try:
            response=_client.models.generate_content(
                model=Config.GEMINI_MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=_SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=LeadData,
                    temperature=0, #Deterministic extraction (no creative writing)
                ),
            )
            return LeadData.model_validate_json(response.text)
        except ValidationError as e:
            logger.warning(f"Schema validation failed on attempt {attempt}:{e}")
        except Exception as e:
            logger.warning(f"Gemini API call failed on attempt {attempt}:{e}")
    logger.error(f"Classification failed after {max_retries} attempts for subject: '{subject}'")
    return None