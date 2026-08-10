"""
Entry point and orchestration layer for the AI-Powered Gmail Lead Extractor.
"""

import argparse
import logging
import sys

from src.config import Config
from src.auth import get_email_service,get_sheets_client
from src.gmail_reader import fetch_recent_emails
from src.ai_classifier import classify_email
from src.gmail_labeler import get_or_create_label, mark_as_processed
from src.sheets_exporter import (
    get_or_create_worksheet,get_or_create_spreadsheet,
    get_existing_message_ids,build_row,append_leads_batch,
)

def setup_logging (verbose:bool=False)->None:
    """
    Logging configuration, for the whole app
    """

    level=logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("pipeline.log"), 
        ],
    )

def parse_args() -> argparse.Namespace:
    """
    CLI arguments so the pipeline is configurable without editing code
    """

    parser=argparse.ArgumentParser(description="AI-Powered Gmail Lead Extractor")
    parser.add_argument(
        "--query-extra",default="newer_than:30d",
        help="Additional Gmail search filter appended to the unprocessed-email query.",

    )

    parser.add_argument(
        "--max-results", type=int, default=25,
        help="Max number of unprocessed emails to pull per run.",
    )

    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable debug-level logging."
    )

    return parser.parse_args()

def run_pipeline(query_extra: str, max_results: int) -> dict:
    """
    Execute one full pipeline run: Fetch, Classify, Export and Label
    """

    logger = logging.getLogger(__name__)
    stats={"fetched": 0, "leads_found": 0, "skipped": 0, "errors": 0}

    gmail=get_email_service()
    sheets_client=get_sheets_client()

    label_id=get_or_create_label(gmail,Config.GMAIL_PROCESSED_LABEL)
    query=f"-label:{Config.GMAIL_PROCESSED_LABEL} {query_extra}"
    emails=fetch_recent_emails(gmail,query=query,max_results=max_results)
    stats["fetched"]=len(emails)
    logger.info(f"Fetched {len(emails)} unprocessed emails for query: '{query}'")

    spreadsheet=get_or_create_spreadsheet(sheets_client,Config.GOOGLE_SHEET_NAME)
    worksheet=get_or_create_worksheet(spreadsheet)
    existing_ids=get_existing_message_ids(worksheet)

    new_rows=[]

    for email in emails:
        try:
            lead=classify_email(email["subject"],email["body"])

            if lead is None:
                stats["errors"] += 1
            elif lead.is_lead and email["id"] not in existing_ids:
                new_rows.append(build_row(email,lead))
                stats["leads_found"] += 1
            else:
                stats["skipped"] += 1
            
            mark_as_processed(gmail,email["id"],label_id)
        except Exception:
            logger.exception(f"Unexpected error processing email {email.get('id')}")
            stats["errors"] += 1
    append_leads_batch(worksheet,new_rows)
    return stats

def main()->None:
    args=parse_args()
    setup_logging(verbose=args.verbose)
    logger=logging.getLogger(__name__)
    try:
        Config.validate()
    except (ValueError, FileNotFoundError) as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    try:
        stats=run_pipeline(args.query_extra,args.max_results)
    except Exception:
        logger.exception("Pipeline run failed with an unhandled error.")
        sys.exit(1)
    logger.info(
        f"Run Complete | Fetched: {stats['fetched']} |"
        f"Leads found: {stats['leads_found']} |"
        f"Skipped: {stats['skipped']} | Errors: {stats['errors']}"
    )

if __name__=="__main__":
    main()