from src.auth import get_gmail_service,get_sheets_client
from src.gmail_reader import fetch_recent_emails
from src.ai_classifier import classify_email
from src.gmail_labeler import get_or_create_label,mark_as_processed
from src.sheets_exporter import (
    get_or_create_spreadsheet,get_or_create_worksheet,get_existing_message_ids,
    build_row,append_leads_batch,
)
from src.config import Config

def main():
    gmail=get_gmail_service()
    sheets_client=get_sheets_client()


    #The Query excludes anything already labeled from a prior run

    label_id=get_or_create_label(gmail,Config.GMAIL_PROCESSED_LABEL)
    emails=fetch_recent_emails(
        gmail,query=f"-label:{Config.GMAIL_PROCESSED_LABEL} newer_than:30d", max_results=10
    )

    print(f"Found {len(emails)} unprocessed emails.")

    spreadsheet=get_or_create_spreadsheet(sheets_client,Config.GOOGLE_SHEET_NAME)
    worksheet=get_or_create_worksheet(spreadsheet)
    existing_ids=get_existing_message_ids(worksheet)

    new_rows=[]

    for email in emails:
        lead=classify_email(email["subject"],email["body"])

        if lead and lead.is_lead and email["id"] not in existing_ids:
            new_rows.append(build_row(email,lead))
            print(f"Lead found: {email['subject']}")
        else:
            print(f"Skipped(not a lead or already logged):{email['subject']}")

        mark_as_processed(gmail,email["id"],label_id)

    append_leads_batch(worksheet,new_rows)
    print(f"\nDone. {len(new_rows)} new lead(s) written to '{Config.GOOGLE_SHEET_NAME}'.")


if __name__=="__main__":
    main()
