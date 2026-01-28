import os.path
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
import re

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def fetch_glassdoor_emails(service):
    try:
        # Search for emails from Glassdoor
        query = "from:noreply@glassdoor.com"
        print(f"Searching for Glassdoor job emails...")
        results = service.users().messages().list(userId='me', q=query, maxResults=20).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found from noreply@glassdoor.com. Trying keyword search...')
            query = "Glassdoor"
            results = service.users().messages().list(userId='me', q=query, maxResults=20).execute()
            messages = results.get('messages', [])
            
        if not messages:
            print('No Glassdoor emails found.')
            return []

        print(f"Processing {len(messages)} emails...")
        job_data = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            
            date, subject, sender = "", "", ""
            for header in headers:
                if header['name'] == 'Date': date = header['value']
                if header['name'] == 'Subject': subject = header['value']
                if header['name'] == 'From': sender = header['value']

            # Extract body
            body = ""
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/html':
                        data = part['body'].get('data')
                        if data: body = base64.urlsafe_b64decode(data).decode()
            elif 'body' in payload:
                data = payload['body'].get('data')
                if data: body = base64.urlsafe_b64decode(data).decode()

            if body:
                soup = BeautifulSoup(body, 'html.parser')
                # Improved regex to handle partner links and different domains (.com, .co.in, etc.)
                links = soup.find_all('a', href=re.compile(r'glassdoor\..*(jobListing|job-listing)', re.IGNORECASE))
                
                for link in links:
                    job_link = link.get('href')
                    title = link.get_text().strip()
                    
                    if not title or title.lower() in ['apply now', 'view job', 'details', 'apply']:
                        parent = link.find_parent()
                        if parent: title = parent.get_text().strip().split('\n')[0]

                    company = "Unknown"
                    parent = link.find_parent()
                    if parent:
                        text = parent.get_text(separator='|')
                        parts = [p.strip() for p in text.split('|') if p.strip()]
                        if " at " in title:
                            title_parts = title.split(" at ")
                            title, company = title_parts[0].strip(), title_parts[1].strip()
                        elif len(parts) > 1:
                            for p in parts:
                                if p != title and len(p) < 50 and "Apply" not in p:
                                    company = p
                                    break

                    if job_link:
                        job_data.append({
                            'date': date,
                            'title': title,
                            'company': company,
                            'link': job_link
                        })

        # Deduplicate by link
        unique_jobs = {job['link']: job for job in job_data}.values()
        return list(unique_jobs)

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def main():
    service = get_gmail_service()
    jobs = fetch_glassdoor_emails(service)
    
    output_path = "detected_jobs.json"
    with open(output_path, "w") as f:
        json.dump(jobs, f, indent=4)
    
    print(f"Stored {len(jobs)} jobs in {output_path}")

if __name__ == "__main__":
    main()
