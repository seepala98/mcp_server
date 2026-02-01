#!/usr/bin/env python3
"""Command-line interface for Glassdoor Job Scraper."""

import os
import sys
import argparse
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich import box

from .core import GlassdoorScraper, scrape_jobs
from .config import ScraperConfig
from .exceptions import ScraperException


console = Console()


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Glassdoor Job Scraper - Scrape job listings from Glassdoor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for software engineer jobs in Toronto
  python -m glassdoor_scraper "Software Engineer" --location "Toronto, ON"
  
  # Search for remote data science jobs
  python -m glassdoor_scraper "Data Scientist" --remote
  
  # Search with filters and export to specific file
  python -m glassdoor_scraper "Product Manager" --location "New York" --max-jobs 100 --format csv
  
  # Search with salary filter
  python -m glassdoor_scraper "Python Developer" --min-salary 80000 --max-salary 120000
        """
    )
    
    # Required arguments
    parser.add_argument(
        "keyword",
        help="Job title or keywords to search for"
    )
    
    # Optional arguments
    parser.add_argument(
        "--location", "-l",
        default="",
        help="Job location (city, state, or country)"
    )
    
    parser.add_argument(
        "--job-type", "-t",
        choices=["fulltime", "parttime", "contract", "internship"],
        help="Filter by job type"
    )
    
    parser.add_argument(
        "--remote", "-r",
        action="store_true",
        help="Filter for remote jobs only"
    )
    
    parser.add_argument(
        "--days-ago", "-d",
        type=int,
        default=0,
        help="Only show jobs posted within this many days"
    )
    
    parser.add_argument(
        "--max-jobs", "-n",
        type=int,
        default=50,
        help="Maximum number of jobs to scrape (default: 50)"
    )
    
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Maximum number of pages to scrape (default: 10)"
    )
    
    parser.add_argument(
        "--min-salary",
        type=int,
        default=0,
        help="Minimum salary filter"
    )
    
    parser.add_argument(
        "--max-salary",
        type=int,
        default=0,
        help="Maximum salary filter"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["csv", "json", "both"],
        default="both",
        help="Export format (default: both)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory (default: output)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )
    
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser with GUI visible"
    )
    
    parser.add_argument(
        "--use-proxies",
        action="store_true",
        help="Enable proxy rotation"
    )
    
    parser.add_argument(
        "--delay-min",
        type=float,
        default=3.0,
        help="Minimum delay between requests in seconds (default: 3)"
    )
    
    parser.add_argument(
        "--delay-max",
        type=float,
        default=8.0,
        help="Maximum delay between requests in seconds (default: 8)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def print_banner():
    """Print the application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           Glassdoor Job Scraper v1.0.0                        ║
    ║           Robust job scraping with anti-bot protection        ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="blue", box=box.DOUBLE))


def print_results(jobs: list):
    """Print job results in a table."""
    if not jobs:
        console.print("[yellow]No jobs found.[/yellow]")
        return
    
    table = Table(
        title=f"Scraped {len(jobs)} Jobs",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="cyan", min_width=30)
    table.add_column("Company", style="green", min_width=20)
    table.add_column("Location", style="yellow", min_width=15)
    table.add_column("Salary", style="blue", min_width=15)
    
    for i, job in enumerate(jobs[:20], 1):  # Show first 20
        table.add_row(
            str(i),
            job.get("title", "N/A")[:50],
            job.get("company", "N/A")[:30],
            job.get("location", "N/A")[:20],
            job.get("salary", "N/A")[:20]
        )
    
    if len(jobs) > 20:
        table.add_row(
            "...",
            f"[dim]and {len(jobs) - 20} more...[/dim]",
            "",
            "",
            ""
        )
    
    console.print(table)


def main():
    """Main entry point."""
    print_banner()
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle headless flag
    headless = not args.no_headless if args.no_headless else args.headless
    
    # Create configuration
    config = ScraperConfig(
        headless=headless,
        max_jobs=args.max_jobs,
        max_pages=args.max_pages,
        min_delay=args.delay_min,
        max_delay=args.delay_max,
        use_proxies=args.use_proxies,
        output_dir=args.output,
    )
    
    # Print search parameters
    console.print("\n[bold]Search Parameters:[/bold]")
    console.print(f"  Keyword: [cyan]{args.keyword}[/cyan]")
    console.print(f"  Location: [cyan]{args.location or 'Any'}[/cyan]")
    console.print(f"  Job Type: [cyan]{args.job_type or 'Any'}[/cyan]")
    console.print(f"  Remote: [cyan]{'Yes' if args.remote else 'No'}[/cyan]")
    console.print(f"  Max Jobs: [cyan]{args.max_jobs}[/cyan]")
    console.print(f"  Headless: [cyan]{'Yes' if headless else 'No'}[/cyan]")
    console.print()
    
    try:
        # Initialize scraper with progress display
        with console.status("[bold green]Initializing browser...") as status:
            scraper = GlassdoorScraper(config)
            scraper.start()
        
        console.print("[green]✓[/green] Browser started successfully\n")
        
        # Perform search
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Scraping jobs...", total=None)
            
            def update_progress(current, total):
                progress.update(task, description=f"[cyan]Scraped {current}/{total} jobs...")
            
            jobs = scraper.search(
                keyword=args.keyword,
                location=args.location,
                job_type=args.job_type or "",
                remote=args.remote,
                days_ago=args.days_ago,
                min_salary=args.min_salary,
                max_salary=args.max_salary,
                progress_callback=update_progress,
            )
        
        # Print results
        console.print()
        print_results(jobs)
        
        # Export results
        if jobs:
            exported_files = scraper.export(format_type=args.format)
            console.print(f"\n[green]✓[/green] Exported to:")
            for file_path in exported_files:
                console.print(f"   [dim]{file_path}[/dim]")
        
        # Cleanup
        scraper.stop()
        console.print("\n[green]✓[/green] Scraping complete!")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Scraping interrupted by user[/yellow]")
        sys.exit(0)
    
    except ScraperException as e:
        console.print(f"\n[red]✗ Scraper error: {e}[/red]")
        sys.exit(1)
    
    except Exception as e:
        console.print(f"\n[red]✗ Unexpected error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()