"""
Finding/Creating the target spreadsheet, ensuring headers exist,
and writing new leads in efficient batches.
"""

import logging
import gspread
from src.ai_classifier import LeadData

logger=logging.getLogger(__name__)

#Constant Column Order
SHEET_HEADERS= [
    "message_id","date","sender_email","subject",
    "name","budget","priority","summary",
]

def get_or_create_spreadsheet(client:gspread.Client,sheet_name:str)->gspread.Spreadsheet:
    """
    Open/Create the target spreadsheet, will be authenticated using user's own
    OAuth credentials, spreadsheet will be owned by the same Google account.
    """

    try:
        return client.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        logger.info(f"Spreadsheet '{sheet_name}' not found. Creating it...")
        return client.create(sheet_name)

def get_or_create_worksheet(spreadsheet:gspread.Spreadsheet, worksheet_name:str="Leads")->gspread.Worksheet:
    """
    Return/create the target worksheet/tab
    Writing the header row if its new.
    """

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name,rows=1000,cols=len(SHEET_HEADERS))
        worksheet.append_row(SHEET_HEADERS)
        logger.info(f"Created worksheet '{worksheet_name}' with headers.")
        return worksheet
    #Incase worksheet was created manually, it might be empty
    if not worksheet.row_values(1):
        worksheet.append_row(SHEET_HEADERS)
    
    return worksheet

def get_existing_message_ids(worksheet: gspread.Worksheet)->set[str]:
    """
    This is a defensive second layer of dedup on top of Gmail labels- incase a label
    ever gets manually removed or a run get interrupted mid-batch
    """
    #First Column= message_id
    return set(worksheet.col_values(1)[1:])

def build_row(email_metadata:dict,lead:LeadData)->list:
    """
    Converting the email and its classified data to a single row in the exact order
    defined by SHEET_HEADERS
    """

    return[
        email_metadata["id"],
        email_metadata["date"],
        email_metadata["sender"],
        email_metadata["subject"],
        lead.name or "",
        lead.budget or "",
        lead.priority,
        lead.summary,

    ]

def append_leads_batch(worksheet:gspread.Worksheet,rows:list[list])->None:
    """
    Writing multiple lead rows in a single API call.
    Keeping us comfortably inside Sheets '60-writes/min-per-user quota
    """
    if not rows:
        logger.info("No new leads to write - skipping Sheets write.")
        return
    
    worksheet.append_rows(rows,value_input_option="USER_ENTERED")
    logger.info(f"Wrote {len(rows)} new lead row(s) to the sheet.")
    
