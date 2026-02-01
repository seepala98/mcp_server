# Glassdoor Job Scraper

A robust, standalone Glassdoor job scraper with anti-bot protection, proxy rotation, and human-like behavior simulation.

## Features

- 🔍 **Advanced Search**: Search by keyword, location, job type, remote options, and date posted
- 🛡️ **Anti-Bot Protection**: Stealth browser with fingerprint randomization and automation detection evasion
- 🔄 **Proxy Rotation**: Automatic proxy rotation to avoid IP bans
- ⏱️ **Human-Like Delays**: Randomized delays between actions to mimic human behavior
- 📊 **Rich Data Extraction**: Job title, company, salary, description, requirements, company info, and more
- 📁 **Multiple Export Formats**: Export to CSV, JSON, or both
- 🖥️ **CLI Interface**: Easy-to-use command-line interface with progress indicators
- 🔧 **Configurable**: Extensive configuration options for delays, retries, and more

## Installation

### Prerequisites

- Python 3.8+
- Playwright browsers

### Setup

1. Clone or download the scraper:
```bash
cd glassdoor_scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

### Command Line

```bash
# Search for software engineer jobs in Toronto
python -m glassdoor_scraper "Software Engineer" --location "Toronto, ON"

# Search for remote data science jobs
python -m glassdoor_scraper "Data Scientist" --remote

# Search with multiple filters
python -m glassdoor_scraper "Product Manager" \
    --location "New York" \
    --job-type fulltime \
    --max-jobs 100 \
    --days-ago 7 \
    --format csv

# Search with salary filter
python -m glassdoor_scraper "Python Developer" \
    --min-salary 80000 \
    --max-salary 120000

# Run with visible browser (for debugging)
python -m glassdoor_scraper "Software Engineer" --no-headless

# Use proxies for additional protection
python -m glassdoor_scraper "Software Engineer" --use-proxies
```

### Python API

```python
from glassdoor_scraper import GlassdoorScraper, ScraperConfig

# Simple usage
from glassdoor_scraper import scrape_jobs

jobs = scrape_jobs(
    keyword="Software Engineer",
    location="Toronto, ON",
    max_jobs=50,
    headless=True
)

# Advanced usage with configuration
config = ScraperConfig(
    headless=True,
    max_jobs=100,
    min_delay=3.0,
    max_delay=8.0,
    use_proxies=True,
    proxy_list=["http://proxy1:8080", "http://proxy2:8080"],
)

with GlassdoorScraper(config) as scraper:
    jobs = scraper.search(
        keyword="Data Scientist",
        location="Remote",
        job_type="fulltime",
        days_ago=7,
    )
    
    # Export results
    scraper.export(format_type="both")
    
    # Access job data
    for job in scraper.get_jobs():
        print(f"{job['title']} at {job['company']}")
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SCRAPER_HEADLESS` | Run browser in headless mode | `true` |
| `SCRAPER_BROWSER` | Browser type (chromium, firefox, webkit) | `chromium` |
| `USE_PROXIES` | Enable proxy rotation | `false` |
| `MAX_JOBS` | Maximum jobs to scrape | `100` |
| `MAX_PAGES` | Maximum pages to scrape | `10` |
| `MIN_DELAY` | Minimum delay between requests (seconds) | `3.0` |
| `MAX_DELAY` | Maximum delay between requests (seconds) | `8.0` |
| `OUTPUT_DIR` | Output directory for exports | `output` |

### Command Line Options

| Option | Description |
|--------|-------------|
| `keyword` | Job title or keywords (required) |
| `--location`, `-l` | Job location |
| `--job-type`, `-t` | Job type: fulltime, parttime, contract, internship |
| `--remote`, `-r` | Filter for remote jobs |
| `--days-ago`, `-d` | Jobs posted within N days |
| `--max-jobs`, `-n` | Maximum jobs to scrape |
| `--max-pages` | Maximum pages to scrape |
| `--min-salary` | Minimum salary filter |
| `--max-salary` | Maximum salary filter |
| `--format`, `-f` | Export format: csv, json, both |
| `--output`, `-o` | Output directory |
| `--headless` | Run in headless mode |
| `--no-headless` | Show browser window |
| `--use-proxies` | Enable proxy rotation |
| `--delay-min` | Minimum delay between requests |
| `--delay-max` | Maximum delay between requests |

## Anti-Bot Measures

The scraper implements several anti-detection techniques:

1. **Stealth Browser**: Uses Playwright with custom stealth scripts to evade automation detection
2. **User-Agent Rotation**: Rotates between different browser user agents
3. **Viewport Randomization**: Randomizes browser viewport size
4. **Fingerprint Randomization**: Randomizes WebGL, Canvas, and Font fingerprints
5. **Human-Like Delays**: Random delays between actions (3-8 seconds by default)
6. **Mouse Movement Simulation**: Simulates realistic mouse movements
7. **Scroll Behavior**: Realistic scrolling patterns
8. **Proxy Rotation**: Optional proxy rotation to distribute requests

## Data Extracted

### Basic Information
- Job Title
- Company Name
- Location
- Job URL
- Posting Date

### Detailed Information
- Full Job Description
- Job Requirements/Qualifications
- Salary Range
- Employment Type
- Company Rating
- Company Size
- Industry
- Benefits

## Output Format

### CSV Export
```csv
id,title,company,location,salary,job_type,description,requirements,company_rating,posting_date,job_url,scraped_at
12345,Software Engineer,Tech Corp,San Francisco CA,$100k-$150k,Full-time,Job description...,Requirements...,4.5,2024-01-15,https://...,2024-01-28T10:30:00
```

### JSON Export
```json
{
  "metadata": {
    "exported_at": "2024-01-28T10:30:00",
    "total_jobs": 50,
    "source": "Glassdoor"
  },
  "jobs": [
    {
      "id": "12345",
      "title": "Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "salary": "$100k-$150k",
      "job_type": "Full-time",
      "description": "...",
      "requirements": "...",
      "company_rating": 4.5,
      "posting_date": "2024-01-15",
      "job_url": "https://...",
      "scraped_at": "2024-01-28T10:30:00"
    }
  ]
}
```

## Rate Limiting & Ethics

⚠️ **Important Notice**:

- This tool is for educational and personal use only
- Respect Glassdoor's Terms of Service
- Do not scrape at high volumes or frequencies
- Use reasonable delays between requests (default: 3-8 seconds)
- Consider using this tool responsibly and ethically

## Troubleshooting

### CAPTCHA Detection
If you encounter CAPTCHA:
- Increase delays between requests
- Use proxies
- Run with `--no-headless` to solve manually
- Wait before trying again

### Access Blocked
If your IP is blocked:
- Enable proxy rotation with `--use-proxies`
- Wait several hours before retrying
- Use a VPN

### No Jobs Found
- Check your search parameters
- Try different keywords or locations
- Glassdoor may have updated their HTML structure

### Browser Issues
```bash
# Reinstall Playwright browsers
playwright install --force chromium
```

## Limitations

- Glassdoor's HTML structure may change, requiring selector updates
- Some job details may not be available for all listings
- Salary information is not always present
- Large-scale scraping may trigger anti-bot measures despite precautions
- Job location IDs may require manual lookup for some locations

## License

This project is for educational purposes. Please use responsibly and in accordance with Glassdoor's Terms of Service.

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All tests pass
- Documentation is updated
- Anti-bot measures are maintained

## Disclaimer

This tool is provided as-is without any warranties. Users are responsible for complying with applicable laws and website terms of service. The authors are not responsible for any misuse or consequences arising from the use of this tool.