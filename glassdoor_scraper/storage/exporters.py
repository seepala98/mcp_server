"""Data export utilities for scraped job data."""

import csv
import json
import os
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from ..utils.helpers import sanitize_filename


class DataExporter:
    """Handles exporting scraped job data to various formats."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the data exporter.
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_csv(self, jobs: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Export job data to CSV format.
        
        Args:
            jobs: List of job dictionaries
            filename: Output filename (optional)
            
        Returns:
            Path to the exported file
        """
        if not jobs:
            print("No jobs to export")
            return ""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"glassdoor_jobs_{timestamp}.csv"
        
        filename = sanitize_filename(filename)
        filepath = self.output_dir / filename
        
        # Get all unique fieldnames from all jobs
        fieldnames = set()
        for job in jobs:
            fieldnames.update(job.keys())
        
        # Define preferred order for common fields
        preferred_order = [
            "id", "title", "company", "location", "salary", "job_type",
            "description", "requirements", "company_rating", "company_size",
            "industry", "posting_date", "job_url", "company_url",
            "scraped_at"
        ]
        
        # Sort fieldnames with preferred order first
        ordered_fieldnames = []
        for field in preferred_order:
            if field in fieldnames:
                ordered_fieldnames.append(field)
                fieldnames.discard(field)
        
        # Add remaining fields alphabetically
        ordered_fieldnames.extend(sorted(fieldnames))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ordered_fieldnames)
            writer.writeheader()
            writer.writerows(jobs)
        
        print(f"Exported {len(jobs)} jobs to {filepath}")
        return str(filepath)
    
    def export_to_json(self, jobs: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Export job data to JSON format.
        
        Args:
            jobs: List of job dictionaries
            filename: Output filename (optional)
            
        Returns:
            Path to the exported file
        """
        if not jobs:
            print("No jobs to export")
            return ""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"glassdoor_jobs_{timestamp}.json"
        
        filename = sanitize_filename(filename)
        filepath = self.output_dir / filename
        
        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_jobs": len(jobs),
                "source": "Glassdoor"
            },
            "jobs": jobs
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(jobs)} jobs to {filepath}")
        return str(filepath)
    
    def export(self, jobs: List[Dict[str, Any]], format_type: str = "both", 
               filename_base: str = None) -> List[str]:
        """
        Export job data to specified format(s).
        
        Args:
            jobs: List of job dictionaries
            format_type: Export format - "csv", "json", or "both"
            filename_base: Base filename without extension (optional)
            
        Returns:
            List of exported file paths
        """
        if not jobs:
            print("No jobs to export")
            return []
        
        if filename_base is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_base = f"glassdoor_jobs_{timestamp}"
        
        exported_files = []
        
        if format_type in ("csv", "both"):
            csv_path = self.export_to_csv(jobs, f"{filename_base}.csv")
            if csv_path:
                exported_files.append(csv_path)
        
        if format_type in ("json", "both"):
            json_path = self.export_to_json(jobs, f"{filename_base}.json")
            if json_path:
                exported_files.append(json_path)
        
        return exported_files
    
    def append_to_csv(self, job: Dict[str, Any], filepath: str) -> None:
        """
        Append a single job to an existing CSV file.
        
        Args:
            job: Job dictionary to append
            filepath: Path to the CSV file
        """
        filepath = Path(filepath)
        file_exists = filepath.exists()
        
        with open(filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=job.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(job)
    
    def load_from_json(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load job data from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            List of job dictionaries
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and "jobs" in data:
            return data["jobs"]
        elif isinstance(data, list):
            return data
        else:
            return []
    
    def load_from_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load job data from a CSV file.
        
        Args:
            filepath: Path to the CSV file
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                jobs.append(dict(row))
        return jobs