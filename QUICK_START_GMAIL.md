# Quick Start: Gmail Integration

## Files Created

1. **`gmail_mcp_server.py`** - New MCP server that handles email sending
2. **`talk2mcp_with_gmail.py`** - Updated agent that uses both math/paint AND Gmail tools
3. **`GMAIL_SETUP.md`** - Detailed setup instructions
4. **`.gitignore`** - Updated to protect sensitive OAuth files

## Quick Setup (3 Steps)

### 1. Get OAuth Credentials
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Enable Gmail API
- Create OAuth 2.0 Desktop App credentials
- Download as `credentials.json` and place in project directory

### 2. Install Dependencies
```bash
uv pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Update Configuration
Edit `talk2mcp_with_gmail.py` line 19:
```python
RECIPIENT_EMAIL = "your.email@example.com"  # Change this to your email
```

## Usage

### Run with Gmail Integration
```bash
python talk2mcp_with_gmail.py
```

First run will open browser for OAuth authorization. Subsequent runs will use saved token.

### Run without Gmail (Original)
```bash
python talk2mcp.py
```

## What It Does

The agent will:
1. ✅ Calculate ASCII values for "INDIA" → `[73, 78, 68, 73, 65]`
2. ✅ Calculate exponential sum → large number like `1.23e56`
3. ✅ Open Paint and draw rectangle
4. ✅ Add text to Paint with result
5. ✅ **NEW:** Send email with final answer to configured recipient

## Email Format

**Subject:** `Calculation Result` or `INDIA ASCII Sum Result`

**Body:**
```
The exponential sum is: 1.23456789e+56

Details:
- Input: INDIA
- ASCII values: [73, 78, 68, 73, 65]
- Final result: 1.23456789e+56
```

## Architecture

```
talk2mcp_with_gmail.py (Agent/Orchestrator)
        |
        +-- Connects to --> mcp_server.py (Math & Paint Tools)
        |                   - strings_to_chars_to_int
        |                   - int_list_to_exponential_sum
        |                   - open_paint_and_select_rectangle
        |                   - draw_rectangle
        |                   - add_text_in_paint
        |
        +-- Connects to --> gmail_mcp_server.py (Email Tool)
                            - send_email
```

## Key Differences from Original

| Feature | `talk2mcp.py` | `talk2mcp_with_gmail.py` |
|---------|---------------|---------------------------|
| MCP Servers | 1 (Calculator) | 2 (Calculator + Gmail) |
| Email Sending | ❌ No | ✅ Yes |
| OAuth Setup | Not needed | Required |
| Max Iterations | 10 | 12 (to allow email step) |
| Final Output | Paint only | Paint + Email |

## Troubleshooting

### OAuth Issues
```bash
# Delete token and reauthorize
rm token.json
python talk2mcp_with_gmail.py
```

### See Only Gmail Tools
```bash
# Test Gmail server independently
python gmail_mcp_server.py dev
```

### See Original Tools Only
```bash
# Test calculator server independently
python mcp_server.py dev
```

## Security Checklist

- [ ] `credentials.json` is in project directory
- [ ] `credentials.json` is NOT committed to git
- [ ] `token.json` is NOT committed to git
- [ ] `.gitignore` includes both OAuth files
- [ ] Test user added in Google Cloud Console (if needed)
- [ ] Correct recipient email configured

## Next Steps

1. Follow detailed setup in `GMAIL_SETUP.md`
2. Test with: `python talk2mcp_with_gmail.py`
3. Check your email inbox for the result!

## Reference

Based on: https://medium.com/@jason.summer/create-a-gmail-agent-with-model-context-protocol-mcp-061059c07777
