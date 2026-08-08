from src.auth import get_gmail_service

def main():
    service = get_gmail_service()
    profile = service.users().getProfile(userId="me").execute()
    print(f"✅ Authenticated successfully as: {profile['emailAddress']}")

if __name__ == "__main__":
    main()