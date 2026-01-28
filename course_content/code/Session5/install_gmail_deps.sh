#!/bin/bash
# Install Gmail MCP Server Dependencies

echo "Installing Gmail integration dependencies..."
echo ""

# Using uv (recommended)
if command -v uv &> /dev/null; then
    echo "Using uv to install packages..."
    uv pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
    echo "✓ Dependencies installed with uv"
else
    echo "uv not found, using pip..."
    pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
    echo "✓ Dependencies installed with pip"
fi

echo ""
echo "Next steps:"
echo "1. Get OAuth credentials from Google Cloud Console"
echo "2. Save as credentials.json in this directory"
echo "3. Update RECIPIENT_EMAIL in talk2mcp_with_gmail.py"
echo "4. Run: python talk2mcp_with_gmail.py"
echo ""
echo "See GMAIL_SETUP.md for detailed instructions."
