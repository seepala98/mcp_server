import json
import os
import re
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Setup Gemini for evaluation (Stage 3 & 4 reasoning)
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def load_resume():
    with open("resume_text.txt", "r") as f:
        return f.read()

import random
import time
from typing import Optional

# Rotating user agents to mimic different browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.2; rv:121.0) Gecko/20100101 Firefox/121.0"
]

# Proxy configuration (optional, uncomment if using proxies)
# PROXIES = [
#     "http://proxy1:port",
#     "http://proxy2:port",
#     "http://proxy3:port"
# ]

def fetch_job_description(url, retries=3, delay=2):
    """
    Fetch job description from Glassdoor with anti-bot protections.
    
    Args:
        url: Job listing URL
        retries: Number of retry attempts
        delay: Initial delay between retries (exponential backoff)
    
    Returns:
        Job description text or "Description Unavailable"
    """
    for attempt in range(retries):
        try:
            # Random user agent to mimic different browsers
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0"
            }
            
            # Optional proxy rotation
            # proxies = {"http": random.choice(PROXIES), "https": random.choice(PROXIES)} if PROXIES else None
            
            response = requests.get(
                url, 
                headers=headers,
                # proxies=proxies,
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try different selectors for job description
                desc = None
                
                # Common Glassdoor job description selectors
                selectors = [
                    {'id': 'JobDescriptionContainer'},
                    {'class': 'jobDescriptionContent'},
                    {'class': 'job-description'},
                    {'class': 'jobDescription'},
                    {'data-test': 'job-description'},
                    {'class': 'description'},
                    {'class': 'job-details'}
                ]
                
                for selector in selectors:
                    if 'id' in selector:
                        desc = soup.find('div', {'id': selector['id']})
                    else:
                        desc = soup.find('div', {'class': selector['class']})
                    if desc:
                        break
                
                if desc:
                    # Clean up the text
                    text = desc.get_text().strip()
                    # Remove extra newlines and whitespace
                    text = re.sub(r'\s+', ' ', text)
                    return text
                
                # Fallback to first 3000 characters of page text if no description found
                fallback_text = soup.get_text().strip()[:3000]
                return re.sub(r'\s+', ' ', fallback_text)
                
            elif response.status_code == 429:
                # Too many requests - exponential backoff
                wait_time = delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited (429), waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                continue
                
            elif response.status_code in [500, 502, 503, 504]:
                # Server errors - retry
                wait_time = delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Server error ({response.status_code}), waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                continue
                
            else:
                print(f"Unexpected status code: {response.status_code} for URL: {url}")
                return "Description Unavailable"
                
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1} for URL: {url}")
            if attempt < retries - 1:
                wait_time = delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
                
        except requests.exceptions.ConnectionError:
            print(f"Connection error on attempt {attempt + 1} for URL: {url}")
            if attempt < retries - 1:
                wait_time = delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
                
        except Exception as e:
            print(f"Error fetching job desc (attempt {attempt + 1}): {e}")
            if attempt < retries - 1:
                wait_time = delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
    
    # All attempts failed
    print(f"Failed to fetch job description after {retries} attempts for URL: {url}")
    return "Description Unavailable"

def evaluate_job(resume_text, job_title, company, job_description):
    prompt = f"""
    OBJECTIVE: Evaluate the match between the resume and the job description.
    
    RESUME:
    {resume_text}
    
    JOB:
    Title: {job_title}
    Company: {company}
    Description: {job_description}
    
    STAGES OF REASONING:
    1. EXTRACT: Skills, Tools, YOE from Job Description.
    2. NORMALIZE: Parse resume into structured Skills, Tools, YOE per skill.
    3. MATCH: 
       - Skill Match % = % of required skills found in resume.
       - Experience Match % = alignment of years and seniority.
       - Responsibility Alignment % = similarity in domain/tasks.
    4. FORMULA: Final Match % = 0.5 * Skill Match + 0.3 * Experience Match + 0.2 * Responsibility Alignment.
    
    OUTPUT FORMAT (JSON):
    {{
        "matching_keywords": [],
        "missing_keywords": [],
        "match_percentage": float,
        "experience_gaps": [],
        "recommendation_notes": "",
        "trimmed_description": "First 200 chars..."
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
            }
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error evaluating job: {e}")
        return {
            "matching_keywords": [],
            "missing_keywords": [],
            "match_percentage": 0,
            "experience_gaps": ["Error in evaluation"],
            "recommendation_notes": str(e),
            "trimmed_description": job_description[:200]
        }

def main():
    resume_text = load_resume()
    if not os.path.exists("detected_jobs.json"):
        print("No jobs detected yet. Run fetch_emails.py first.")
        return

    with open("detected_jobs.json", "r") as f:
        jobs = json.load(f)

    print(f"Processing {len(jobs)} jobs...")
    
    results = []
    for job in jobs:
        print(f"Evaluating: {job['title']} at {job['company']}...")
        
        # Fetch the actual job description from the Glassdoor URL
        job_desc = fetch_job_description(job['link'])
        
        # Add random delay between requests to avoid rate limiting
        time.sleep(random.uniform(2, 5))
        
        evaluation = evaluate_job(resume_text, job['title'], job['company'], job_desc)
        
        results.append({
            "Date": job['date'],
            "Job Title": job['title'],
            "Company": job['company'],
            "Job Link": job['link'],
            "Job Description (trimmed)": evaluation.get("trimmed_description", job_desc[:200]),
            "Matching Keywords": ", ".join(evaluation.get("matching_keywords", [])),
            "Missing Keywords": ", ".join(evaluation.get("missing_keywords", [])),
            "Match Percentage": evaluation.get("match_percentage", 0),
            "Experience Gaps": ", ".join(evaluation.get("experience_gaps", [])),
            "Recommendation Notes": evaluation.get("recommendation_notes", "")
        })

    # Sort and filter
    results = [r for r in results if r["Match Percentage"] >= 50]
    results.sort(key=lambda x: x["Match Percentage"], reverse=True)

    if results:
        date_str = datetime.now().strftime("%Y-%m-%d")
        csv_file = f"Job_Matches_{date_str}.csv"
        keys = results[0].keys()
        with open(csv_file, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        print(f"Saved {len(results)} matches to {csv_file}")
    else:
        print("No jobs matched the 50% threshold.")

if __name__ == "__main__":
    main()
