# Gmail MCP Server Setup Guide

This guide will help you set up the Gmail integration for sending calculation results via email.

## Prerequisites

- Google account with Gmail access
- OAuth 2.0 credentials from Google Cloud Console

## Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Give it a name (e.g., "MCP Gmail Agent")
   - Click "Create"
5. Download the credentials:
   - Click the download button (⬇️) next to your OAuth client
   - Save the file as `credentials.json` in your project directory

## Step 2: Install Required Packages

```bash
# Install Google API packages
uv pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Or using regular pip
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 3: Configure Email Settings

### Option A: Edit the file directly

Open `talk2mcp_with_gmail.py` and update line 19:

```python
RECIPIENT_EMAIL = "your.email@example.com"  # Replace with your actual email
```

### Option B: Use environment variables

Add to your `.env` file:

```
RECIPIENT_EMAIL=your.email@example.com
```

Then update `talk2mcp_with_gmail.py` to read from env:

```python
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "your.email@example.com")
```

## Step 4: Update Gmail Server Configuration

Open `gmail_mcp_server.py` and verify these paths (lines 23-24):

```python
CREDENTIALS_FILE = "credentials.json"  # Your OAuth credentials
TOKEN_FILE = "token.json"  # Where to store the access token (will be created automatically)
```

If your files are in a different location, update these paths accordingly.

## Step 5: First Run - OAuth Authorization

The first time you run the script, you'll need to authorize the application:

1. Run the script:
   ```bash
   python talk2mcp_with_gmail.py
   ```

2. A browser window will open asking you to sign in to Google

3. Select your Google account

4. Click "Allow" to grant the application permission to send emails on your behalf

5. The browser will show "The authentication flow has completed"

6. Close the browser and return to the terminal

7. A `token.json` file will be created automatically - this stores your authorization for future runs

## Step 6: Test the Integration

Run the complete workflow:

```bash
python talk2mcp_with_gmail.py
```

The agent will:
1. Calculate ASCII values for "INDIA"
2. Calculate the exponential sum
3. Open Paint and draw a rectangle with the result
4. Send an email with the final answer

## Troubleshooting

### "File not found: credentials.json"
- Make sure you downloaded the OAuth credentials from Google Cloud Console
- Check that the file is named exactly `credentials.json`
- Verify the path in `gmail_mcp_server.py`

### "Access blocked: Authorization Error"
- Your app needs to be verified by Google if you want to use it with external users
- For personal use, add your email as a test user in Google Cloud Console:
  - Go to "OAuth consent screen"
  - Add your email under "Test users"

### "Invalid grant: Token expired"
- Delete `token.json` and reauthorize the application
- The refresh token may have been revoked

### Email not sending
- Check the terminal output for detailed error messages
- Verify your Gmail account has no sending restrictions
- Make sure you're using the correct recipient email format

## File Structure

```
mcp_server/
├── mcp_server.py              # Math and Paint automation tools
├── gmail_mcp_server.py        # Gmail email sending tool (NEW)
├── talk2mcp.py                # Original agent (no email)
├── talk2mcp_with_gmail.py     # New agent with Gmail integration (NEW)
├── credentials.json           # OAuth credentials (you need to add this)
├── token.json                 # Auto-generated after first authorization
└── .env                       # Environment variables
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit** `credentials.json` or `token.json` to version control
2. Add them to `.gitignore`:
   ```
   credentials.json
   token.json
   ```
3. The `token.json` file contains your access token - keep it secure
4. Only grant the minimum required scopes (we only use `gmail.send`)
5. Regularly review authorized applications in your Google Account settings

## Reference

For more information about the Gmail API and MCP integration, see:
- [Gmail MCP Server by Jason Sum](https://medium.com/@jason.summer/create-a-gmail-agent-with-model-context-protocol-mcp-061059c07777)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Model Context Protocol](https://modelcontextprotocol.io/)
