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

def fetch_job_description(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract main text
            # This is tricky because Glassdoor uses JS or has complex DOM
            # Attempting to find description div
            desc = soup.find('div', {'id': 'JobDescriptionContainer'})
            if not desc:
                desc = soup.find('div', {'class': 'jobDescriptionContent'})
            
            if desc:
                return desc.get_text().strip()
            return soup.get_text().strip()[:2000] # Fallback to first 2k chars
        return "Description Unavailable"
    except Exception as e:
        print(f"Error fetching job desc: {e}")
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
            model="gemini-2.0-flash-exp",
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
        
        # In a real scenario, we'd fetch the URL content
        # job_desc = fetch_job_description(job['link'])
        job_desc = "Full job description extraction requires advanced scraping/browser. Using Title/Company context."
        
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
