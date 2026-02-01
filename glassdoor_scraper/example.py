#!/usr/bin/env python3
"""
Example usage of the Glassdoor Job Scraper.

This file demonstrates various ways to use the scraper.
"""

from glassdoor_scraper import GlassdoorScraper, ScraperConfig, scrape_jobs


def example_basic_usage():
    """Basic usage with default settings."""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Simple one-liner
    jobs = scrape_jobs(
        keyword="Software Engineer",
        location="Toronto, ON",
        max_jobs=10,
        headless=True
    )
    
    print(f"Found {len(jobs)} jobs")
    for job in jobs[:3]:
        print(f"  - {job['title']} at {job['company']}")


def example_advanced_usage():
    """Advanced usage with custom configuration."""
    print("\n" + "=" * 60)
    print("Example 2: Advanced Usage with Configuration")
    print("=" * 60)
    
    # Create custom configuration
    config = ScraperConfig(
        headless=True,
        max_jobs=20,
        min_delay=4.0,  # Slower to avoid detection
        max_delay=10.0,
        use_proxies=False,  # Set to True if you have proxies
        output_dir="my_job_search",
    )
    
    with GlassdoorScraper(config) as scraper:
        # Search with multiple filters
        jobs = scraper.search(
            keyword="Data Scientist",
            location="Remote",
            job_type="fulltime",
            days_ago=7,
        )
        
        # Export to both CSV and JSON
        exported_files = scraper.export(format_type="both")
        
        print(f"Found {len(jobs)} jobs")
        print(f"Exported to: {exported_files}")


def example_with_progress():
    """Example with progress tracking."""
    print("\n" + "=" * 60)
    print("Example 3: With Progress Callback")
    print("=" * 60)
    
    def progress_callback(current, total):
        percent = (current / total) * 100
        print(f"\rProgress: {current}/{total} ({percent:.1f}%)", end="", flush=True)
    
    config = ScraperConfig(max_jobs=15)
    
    with GlassdoorScraper(config) as scraper:
        jobs = scraper.search(
            keyword="Product Manager",
            location="New York, NY",
            progress_callback=progress_callback,
        )
    
    print(f"\n\nTotal jobs: {len(jobs)}")


def example_salary_filter():
    """Example with salary filtering."""
    print("\n" + "=" * 60)
    print("Example 4: With Salary Filter")
    print("=" * 60)
    
    with GlassdoorScraper() as scraper:
        jobs = scraper.search(
            keyword="Python Developer",
            location="San Francisco, CA",
            min_salary=100000,
            max_salary=200000,
            max_jobs=10,
        )
        
        print(f"Found {len(jobs)} jobs matching salary criteria")
        for job in jobs:
            salary = job.get('salary', 'Not specified')
            print(f"  - {job['title']} at {job['company']}: {salary}")


def example_multiple_searches():
    """Example running multiple searches."""
    print("\n" + "=" * 60)
    print("Example 5: Multiple Searches")
    print("=" * 60)
    
    searches = [
        {"keyword": "Frontend Developer", "location": "Austin, TX"},
        {"keyword": "Backend Developer", "location": "Austin, TX"},
        {"keyword": "Full Stack Developer", "location": "Austin, TX"},
    ]
    
    config = ScraperConfig(max_jobs=5)
    
    with GlassdoorScraper(config) as scraper:
        all_jobs = []
        
        for search in searches:
            print(f"\nSearching: {search['keyword']}")
            jobs = scraper.search(**search)
            all_jobs.extend(jobs)
            scraper.clear_jobs()  # Clear for next search
        
        # Combine all jobs
        scraper.jobs = all_jobs
        scraper.export(format_type="csv", filename="combined_search")
        
        print(f"\nTotal jobs from all searches: {len(all_jobs)}")


def example_custom_proxy():
    """Example with custom proxy configuration."""
    print("\n" + "=" * 60)
    print("Example 6: With Custom Proxies")
    print("=" * 60)
    
    # Configure with custom proxies
    config = ScraperConfig(
        use_proxies=True,
        proxy_list=[
            # Add your proxies here
            # "http://user:pass@proxy1:8080",
            # "http://proxy2:8080",
        ],
        max_jobs=5,
    )
    
    if not config.proxy_list:
        print("Note: Add your proxy URLs to the proxy_list to test this example")
        return
    
    with GlassdoorScraper(config) as scraper:
        jobs = scraper.search(
            keyword="DevOps Engineer",
            location="Remote",
        )
        print(f"Found {len(jobs)} jobs using proxies")


def example_inspect_job_details():
    """Example showing how to inspect detailed job information."""
    print("\n" + "=" * 60)
    print("Example 7: Inspect Job Details")
    print("=" * 60)
    
    with GlassdoorScraper(ScraperConfig(max_jobs=3)) as scraper:
        jobs = scraper.search(
            keyword="Machine Learning Engineer",
            location="Boston, MA",
        )
        
        for i, job in enumerate(jobs, 1):
            print(f"\n--- Job {i} ---")
            print(f"Title: {job.get('title', 'N/A')}")
            print(f"Company: {job.get('company', 'N/A')}")
            print(f"Location: {job.get('location', 'N/A')}")
            print(f"Salary: {job.get('salary', 'Not specified')}")
            print(f"Type: {job.get('employment_type', 'Not specified')}")
            print(f"Rating: {job.get('company_rating', 'N/A')}")
            print(f"Description: {job.get('description', 'N/A')[:200]}...")


if __name__ == "__main__":
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  Glassdoor Job Scraper - Usage Examples".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    
    # Run examples
    try:
        example_basic_usage()
        # Uncomment the examples you want to run:
        # example_advanced_usage()
        # example_with_progress()
        # example_salary_filter()
        # example_multiple_searches()
        # example_custom_proxy()
        # example_inspect_job_details()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)