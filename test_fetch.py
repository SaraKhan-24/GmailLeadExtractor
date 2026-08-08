from src.auth import get_email_service
from src.gmail_reader import fetch_recent_emails

def main():
    service = get_email_service()


    #Try a real Gmail Search query - adjust to match something
    #actually in your inbox for a meaningful test

    emails=fetch_recent_emails(service,query="is:unread",max_results=5)

    for email in emails:
        print("="*60)
        print(f"From:   {email['sender']}")
        print(f"Subject:    {email['subject']}")
        print(f"Date:   {email['date']}")
        print(f"Body preview:   {email['body'][:200]}...")

if __name__=="__main__":
    main()
