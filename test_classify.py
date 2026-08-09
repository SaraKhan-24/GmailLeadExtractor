from src.auth import get_gmail_service
from src.gmail_reader import fetch_recent_emails
from src.ai_classifier import classify_email

def main():
    service=get_gmail_service()
    emails=fetch_recent_emails(service,query="newer_than:30d",max_results=5)

    for email in emails:
        result=classify_email(email["subject"],email["body"])
        print("="*60)
        print(f"Subject:{email['subject']}")
        if result:
            print(result.model_dump_json(indent=2))
        else:
            print("Classification failed for this email.")

if __name__=="__main__":
    main()
