"""
After a lead is extracted and exported we tag the source email so future runs skip 
it automatically
"""

import logging
from googleapiclient.errors import HttpError

logger=logging.getLogger(__name__)

def get_or_create_label(service,label_name:str)->str:
    """
    Return gmail label ID, creating the lavel if it doesnt exist already.
    """

    try: 
        existing = service.users().labels().list(userId="me").execute()
        for label in existing.get("labels",[]):
            if label["name"] == label_name:
                return label["id"]
        
        logger.info(f"Label '{label_name}' not found.Creating it...")

        new_label=service.users().labels().create(
            userId="me",
            body={
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            },
        ).execute()
        return new_label["id"]
    
    except HttpError as error:
        logger.error(f"Failed to get/create label '{label_name}':{error}")
        raise

def mark_as_processed(service, message_id:str, label_id:str) -> bool:
    """
    Apply the label to a message so it is skipped next time.
    """

    try:
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds":[label_id]},

        ).execute()
        return True
    except HttpError as error:
        logger.error(f"Failed to label message {message_id}: {error}")
        return False
        