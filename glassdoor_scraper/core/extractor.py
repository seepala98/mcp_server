"""Data extraction functions for Glassdoor job listings."""

import re
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup

from ..utils.helpers import clean_text, extract_salary_range, parse_posting_date


class JobDataExtractor:
    """Extracts job data from Glassdoor HTML pages."""
    
    @staticmethod
    def extract_jobs_from_search_page(html: str) -> List[Dict[str, Any]]:
        """
        Extract job listings from a search results page.
        
        Args:
            html: HTML content of the search page
            
        Returns:
            List of job dictionaries with basic info
        """
        soup = BeautifulSoup(html, 'lxml')
        jobs = []
        
        # Try multiple selectors for job cards
        job_cards = (
            soup.find_all('li', {'data-test': 'jobListing'})
            or soup.find_all('div', {'data-test': 'jobListing'})
            or soup.find_all('li', class_=re.compile('jobListing'))
            or soup.select('.jobCard')
            or soup.select('[data-testid="job-listing"]')
        )
        
        for card in job_cards:
            try:
                job = JobDataExtractor._extract_job_card_data(card)
                if job.get('title') and job.get('company'):
                    jobs.append(job)
            except Exception as e:
                continue
        
        return jobs
    
    @staticmethod
    def _extract_job_card_data(card) -> Dict[str, Any]:
        """Extract data from a single job card element."""
        job = {}
        
        # Job title
        title_elem = (
            card.find('a', {'data-test': 'job-title'})
            or card.find('a', class_=re.compile('jobLink|jobTitle'))
            or card.find('a', href=re.compile('job-listing'))
        )
        if title_elem:
            job['title'] = clean_text(title_elem.get_text())
            job['job_url'] = title_elem.get('href', '')
            if job['job_url'] and not job['job_url'].startswith('http'):
                job['job_url'] = f"https://www.glassdoor.com{job['job_url']}"
        
        # Company name
        company_elem = (
            card.find('a', {'data-test': 'employer-name'})
            or card.find('span', {'data-test': 'employer-name'})
            or card.find('div', class_=re.compile('employerName|companyName'))
        )
        if company_elem:
            job['company'] = clean_text(company_elem.get_text())
        
        # Location
        location_elem = (
            card.find('span', {'data-test': 'job-location'})
            or card.find('span', class_=re.compile('location'))
        )
        if location_elem:
            job['location'] = clean_text(location_elem.get_text())
        
        # Salary
        salary_elem = (
            card.find('span', {'data-test': 'job-salary'})
            or card.find('span', class_=re.compile('salary'))
        )
        if salary_elem:
            job['salary'] = clean_text(salary_elem.get_text())
        else:
            # Try to extract from text
            card_text = card.get_text()
            salary = extract_salary_range(card_text)
            if salary:
                job['salary'] = salary
        
        # Posting date
        date_elem = (
            card.find('span', {'data-test': 'job-date'})
            or card.find('div', class_=re.compile('jobAge|date'))
        )
        if date_elem:
            date_text = clean_text(date_elem.get_text())
            job['posting_date_text'] = date_text
            job['posting_date'] = parse_posting_date(date_text)
        
        # Company rating
        rating_elem = card.find('span', class_=re.compile('rating'))
        if rating_elem:
            rating_text = rating_elem.get_text()
            try:
                job['company_rating'] = float(rating_text.strip())
            except ValueError:
                pass
        
        # Job ID
        job_id = card.get('data-jobid') or card.get('data-id')
        if job_id:
            job['id'] = job_id
        
        return job
    
    @staticmethod
    def extract_job_details(html: str) -> Dict[str, Any]:
        """
        Extract detailed job information from a job detail page.
        
        Args:
            html: HTML content of the job detail page
            
        Returns:
            Dictionary with detailed job information
        """
        soup = BeautifulSoup(html, 'lxml')
        details = {}
        
        # Job description
        desc_elem = (
            soup.find('div', {'data-test': 'job-description'})
            or soup.find('div', class_=re.compile('jobDescriptionContent|description'))
            or soup.find('div', id='JobDescriptionContainer')
        )
        if desc_elem:
            details['description'] = clean_text(desc_elem.get_text())
        
        # Requirements / Qualifications
        req_section = (
            soup.find('div', string=re.compile('Requirements|Qualifications', re.I))
            or soup.find('h3', string=re.compile('Requirements|Qualifications', re.I))
        )
        if req_section:
            req_parent = req_section.find_parent('div')
            if req_parent:
                # Get the next sibling or parent's next sibling
                req_content = req_parent.find_next_sibling()
                if req_content:
                    details['requirements'] = clean_text(req_content.get_text())
        
        # If no separate requirements found, try to extract from description
        if 'description' in details and 'requirements' not in details:
            # Look for common requirement indicators
            req_patterns = [
                r'(?:Requirements?|Qualifications?|What You Need|Must Have)[\s:]*(.+?)(?=\n\n|$)',
                r'(?:Basic Qualifications?)[\s:]*(.+?)(?=\n\n|Preferred|$)',
            ]
            for pattern in req_patterns:
                match = re.search(pattern, details['description'], re.IGNORECASE | re.DOTALL)
                if match:
                    details['requirements'] = clean_text(match.group(1))
                    break
        
        # Employment type
        emp_type_elem = (
            soup.find('span', {'data-test': 'employment-type'})
            or soup.find('span', string=re.compile('Full-time|Part-time|Contract|Internship', re.I))
        )
        if emp_type_elem:
            details['employment_type'] = clean_text(emp_type_elem.get_text())
        
        # Company size
        size_elem = soup.find('div', string=re.compile('Size'))
        if size_elem:
            size_value = size_elem.find_next_sibling()
            if size_value:
                details['company_size'] = clean_text(size_value.get_text())
        
        # Industry
        industry_elem = soup.find('div', string=re.compile('Industry'))
        if industry_elem:
            industry_value = industry_elem.find_next_sibling()
            if industry_value:
                details['industry'] = clean_text(industry_value.get_text())
        
        # Benefits
        benefits_section = soup.find('div', string=re.compile('Benefits?', re.I))
        if benefits_section:
            benefits_parent = benefits_section.find_parent('div')
            if benefits_parent:
                benefits_content = benefits_parent.find_next_sibling()
                if benefits_content:
                    details['benefits'] = clean_text(benefits_content.get_text())
        
        # Interview difficulty (if available)
        difficulty_elem = soup.find('div', class_=re.compile('interviewDifficulty'))
        if difficulty_elem:
            details['interview_difficulty'] = clean_text(difficulty_elem.get_text())
        
        return details
    
    @staticmethod
    def has_next_page(html: str) -> bool:
        """
        Check if there's a next page of results.
        
        Args:
            html: HTML content of the page
            
        Returns:
            True if next page exists, False otherwise
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Look for next button
        next_btn = (
            soup.find('button', {'data-test': 'pagination-next'})
            or soup.find('a', {'data-test': 'pagination-next'})
            or soup.find('a', class_=re.compile('next'))
        )
        
        if next_btn:
            # Check if disabled
            disabled = next_btn.get('disabled') or 'disabled' in next_btn.get('class', [])
            return not disabled
        
        return False
    
    @staticmethod
    def get_next_page_url(html: str) -> Optional[str]:
        """
        Get the URL for the next page of results.
        
        Args:
            html: HTML content of the page
            
        Returns:
            Next page URL or None
        """
        soup = BeautifulSoup(html, 'lxml')
        
        next_btn = (
            soup.find('button', {'data-test': 'pagination-next'})
            or soup.find('a', {'data-test': 'pagination-next'})
            or soup.find('a', class_=re.compile('next'))
        )
        
        if next_btn:
            href = next_btn.get('href')
            if href:
                if not href.startswith('http'):
                    href = f"https://www.glassdoor.com{href}"
                return href
        
        return None
    
    @staticmethod
    def extract_total_jobs(html: str) -> Optional[int]:
        """
        Extract the total number of jobs from search results.
        
        Args:
            html: HTML content of the page
            
        Returns:
            Total job count or None
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Look for job count text
        count_elem = (
            soup.find('div', {'data-test': 'job-count'})
            or soup.find('h1', class_=re.compile('jobCount'))
        )
        
        if count_elem:
            text = count_elem.get_text()
            # Extract number from text like "1,234 Jobs"
            match = re.search(r'([\d,]+)', text)
            if match:
                try:
                    return int(match.group(1).replace(',', ''))
                except ValueError:
                    pass
        
        return None