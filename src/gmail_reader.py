import base64
import logging
from typing import Optional
# pyrefly: ignore [missing-import]
from googleapiclient.errors import HttpError

logger=logging.getLogger(__name__)

def list_message_ids(service, query: str="", max_results: int =10) -> list[str]:
    try:
         response=service.users().messages().list(
            userId="me", q=query, maxResults=max_results
         ).execute()
         messages= response.get("messages",[])
         return [msg["id"] for msg in messages]
    except HttpError as error:
        logger.error(f"Gmail API error while listing messages: {error}")
        return []

def _get_header(headers:list[dict],name:str)->str:
    """Pull a single header value(e.g. 'From', 'Subject') by name."""
    for header in headers:
        if header.get("name","").lower()==name.lower():
            return header.get("value","")
    return ""

def _decode_body(data:str)->str:
    """Decode Gmail's base64url-encoded body data into readable text."""
    padded=data+"="*(-len(data)%4) #Fix missing padding
    return base64.urlsafe_b64decode(padded).decode("utf-8",errors="ignore")

def _extract_body(payload: dict)->str:
    """Recursively walk the MIME 'parts' tree to find the best available body text. 
    Prefers text/plain; falls back to a stripped text/html"""

    #Case 1: No Nested Parts, This is text/plain or text/html, Extract directly
    if "parts" not in payload:
        body_data=payload.get("body",{}).get("data")
        return _decode_body(body_data) if body_data else ""
    
    #Case 2: Nested Parts - Search for the plain text first
    plain_text=""

    html_text=""

    for part in payload["parts"]:
        mime_type=part.get("mimeType","")
        if mime_type=="text/plain":
            body_data=part.get("body",{}).get("data")
            if body_data:
                plain_text=_decode_body(body_data)
        elif mime_type=="text/html":
            body_data=part.get("body",{}).get("data")
            if body_data:
                html_text=_decode_body(body_data)
        elif "parts" in part:
            #Recurse into nested multipart structures
            nested=_extract_body(part)
            if nested:
                plain_text=plain_text or nested
    if plain_text:
        return plain_text
    if html_text:
        return _strip_html_tags(html_text)

    return ""

def _strip_html_tags(html:str)-> str:
    """HTML-to-Text fallback for emails that provide only HTML body."""
    import re
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)          # strip remaining tags
    text = re.sub(r"\s+", " ", text).strip()       # collapse whitespace
    return text

def get_parsed_email(service,message_id:str)-> Optional[dict]:
    """Fetch a single email by ID and return it as a clean dictionary.
    Args: service: Authenticated Gmail API service object
    message_id: Gmail message ID (from list_message_ids)
    
    Returns:
    A Dict with keys: id, thread_id, sender, subject, date, body
    
    Returns Dict | None (None if the API call fails so callers can skip bad messages without
                        crashing the whole batch)"""
    try:
        msg=service.users().messages().get(
            userId="me", id=message_id, format="full"
        ).execute()
    except HttpError as error:
        logger.error(f"Failed to fetch message {message_id} : {error}")
        return None
    
    payload=msg.get("payload",{})
    headers=payload.get("headers",[])

    return {
        "id":msg.get("id"),
        "thread_id":msg.get("threadId"),
        "sender": _get_header(headers,"From"),
        "subject": _get_header(headers,"Subject"),
        "date": _get_header(headers,"Date"),
        "body":_extract_body(payload),
    }

def fetch_recent_emails(service, query: str = "", max_results: int = 10) -> list[dict]:
    """
    High-level convenience function: search + fetch + parse in one call.
    This is the main function that other modules (main.py and the AI Classifier)
    will import and use.

    Returns: list[dict]:parsed emails, skipping any that failed to fetch
    """      
    message_ids=list_message_ids(service,query=query,max_results=max_results)
    logger.info(f"Found {len(message_ids)} messages matching query: '{query}'")
    emails = []
    for msg_id in message_ids:
        parsed=get_parsed_email(service,msg_id)
        if parsed:
            emails.append(parsed)
    return emails