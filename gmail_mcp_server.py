# gmail_mcp_server.py - Simplified Gmail MCP Server for sending emails

import os
import sys
import asyncio
import base64
import logging
from email.message import EmailMessage
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("Gmail")

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Configuration - Update these paths to your OAuth files
CREDENTIALS_FILE = "credentials.json"  # Path to your OAuth credentials file
TOKEN_FILE = "token.json"  # Where to store the access token

class GmailService:
    """Simplified Gmail service for sending emails"""
    
    def __init__(self, creds_file: str, token_file: str):
        self.creds_file = creds_file
        self.token_file = token_file
        self.service = None
        self.user_email = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gmail API service"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            logger.info(f"Loading token from {self.token_file}")
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired token")
                creds.refresh(Request())
            else:
                logger.info(f"Getting new token using {self.creds_file}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
                logger.info(f"Token saved to {self.token_file}")
        
        # Build the service
        self.service = build('gmail', 'v1', credentials=creds)
        
        # Get user email
        profile = self.service.users().getProfile(userId='me').execute()
        self.user_email = profile.get('emailAddress', '')
        logger.info(f"Gmail service initialized for {self.user_email}")
    
    def send_email(self, recipient: str, subject: str, body: str) -> dict:
        """Send an email"""
        try:
            message = EmailMessage()
            message.set_content(body)
            message['To'] = recipient
            message['From'] = self.user_email
            message['Subject'] = subject
            
            # Encode the message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            
            # Send the message
            send_result = self.service.users().messages().send(
                userId="me", 
                body=create_message
            ).execute()
            
            logger.info(f"Email sent successfully. Message ID: {send_result['id']}")
            return {
                "status": "success",
                "message_id": send_result['id'],
                "from": self.user_email,
                "to": recipient
            }
        
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return {
                "status": "error",
                "error": str(error)
            }
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# Initialize Gmail service
gmail_service = None

def init_gmail_service():
    """Initialize the Gmail service"""
    global gmail_service
    if gmail_service is None:
        try:
            gmail_service = GmailService(CREDENTIALS_FILE, TOKEN_FILE)
            print(f"✓ Gmail service initialized for: {gmail_service.user_email}")
        except Exception as e:
            print(f"✗ Failed to initialize Gmail service: {e}")
            raise

# ------------------------------------------------
# MCP TOOLS
# ------------------------------------------------

@mcp.tool()
async def send_email(recipient: str, subject: str, body: str) -> dict:
    """Send an email with the calculation results.
    
    Args:
        recipient: Email address to send to (e.g., user@example.com)
        subject: Email subject line
        body: Email body content (the final answer)
    
    Example: send_email|user@example.com|Calculation Result|The final answer is 42
    """
    print("\n" + "="*60)
    print(f"SEND_EMAIL CALLED")
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    print("="*60)
    
    try:
        if gmail_service is None:
            init_gmail_service()
        
        result = gmail_service.send_email(recipient, subject, body)
        
        if result["status"] == "success":
            response_text = (
                f"✓ Email sent successfully!\n"
                f"From: {result['from']}\n"
                f"To: {result['to']}\n"
                f"Message ID: {result['message_id']}"
            )
            print(f"\n[SUCCESS] {response_text}")
        else:
            response_text = f"✗ Failed to send email: {result['error']}"
            print(f"\n[ERROR] {response_text}")
        
        print("="*60 + "\n")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=response_text
                )
            ]
        }
    
    except Exception as e:
        error_msg = f"Error sending email: {str(e)}"
        print(f"\n[ERROR] {error_msg}")
        print("="*60 + "\n")
        import traceback
        traceback.print_exc()
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=error_msg
                )
            ]
        }

# ------------------------------------------------
# MAIN
# ------------------------------------------------

if __name__ == "__main__":
    print("="*60)
    print("GMAIL MCP SERVER STARTING...")
    print("="*60)
    
    # Initialize Gmail service on startup
    try:
        init_gmail_service()
    except Exception as e:
        print(f"Warning: Gmail service not initialized: {e}")
        print("Will attempt to initialize when first email is sent.")
    
    # Run the MCP server
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio")
