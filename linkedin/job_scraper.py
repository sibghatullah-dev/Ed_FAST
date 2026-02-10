"""
LinkedIn Job Scraper using JobSpy
Integrated version for EdFast platform
"""

import csv
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
import pandas as pd

try:
    from jobspy import scrape_jobs
except ImportError:
    print("Warning: jobspy not installed. LinkedIn job scraping will not be available.")
    scrape_jobs = None

class LinkedInJobScraper:
    """
    LinkedIn Job Scraper using JobSpy library.
    Integrated with EdFast platform for job search functionality.
    """
    
    def __init__(self):
        self.scraper_available = scrape_jobs is not None
        if not self.scraper_available:
            print("⚠️ JobSpy not available. Install with: pip install python-jobspy")
    
    def scrape_jobs(
        self,
        search_term: str = "software engineer",
        location: str = "San Francisco, CA",
        results_wanted: int = 20,
        hours_old: Optional[int] = None,
        job_type: Optional[str] = None,
        is_remote: bool = False,
        linkedin_fetch_description: bool = True,
        output_file: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Scrape LinkedIn jobs using JobSpy library.
        
        Args:
            search_term (str): Job search term (e.g., "software engineer", "data scientist")
            location (str): Location to search for jobs (e.g., "New York, NY", "Remote")
            results_wanted (int): Number of job results to retrieve
            hours_old (int): Filter jobs by hours since posted (optional)
            job_type (str): Job type filter - "fulltime", "parttime", "internship", "contract" (optional)
            is_remote (bool): Filter for remote jobs only
            linkedin_fetch_description (bool): Fetch full job descriptions (slower but more detailed)
            output_file (str): Output CSV file path (optional)
        
        Returns:
            pandas.DataFrame: DataFrame containing scraped job data
        """
        
        if not self.scraper_available:
            raise ImportError("JobSpy library not available. Please install with: pip install python-jobspy")
        
        print(f"🔍 Searching LinkedIn for: '{search_term}' in '{location}'")
        print(f"📊 Requesting {results_wanted} job results...")
        
        try:
            # Scrape jobs from LinkedIn only
            jobs = scrape_jobs(
                site_name=["linkedin"],  # Only LinkedIn
                search_term=search_term,
                location=location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                job_type=job_type,
                is_remote=is_remote,
                linkedin_fetch_description=linkedin_fetch_description,
                verbose=2  # Show detailed logs
            )
            
            print(f"✅ Found {len(jobs)} LinkedIn jobs!")
            
            if len(jobs) > 0:
                # Display basic info about found jobs
                print("\n📋 Job Summary:")
                print(f"   • Total jobs found: {len(jobs)}")
                print(f"   • Companies: {jobs['company'].nunique()}")
                print(f"   • Locations: {jobs['location'].nunique()}")
                
                # Show first few jobs
                print("\n🎯 Sample Jobs:")
                for i, job in jobs.head(3).iterrows():
                    print(f"   {i+1}. {job['title']} at {job['company']} - {job['location']}")
                
                # Save to CSV if output file specified
                if output_file:
                    jobs.to_csv(
                        output_file, 
                        quoting=csv.QUOTE_NONNUMERIC, 
                        escapechar="\\", 
                        index=False
                    )
                    print(f"\n💾 Jobs saved to: {output_file}")
                
                return jobs
            else:
                print("❌ No jobs found. Try adjusting your search parameters.")
                return None
                
        except Exception as e:
            print(f"❌ Error occurred while scraping: {str(e)}")
            print("💡 Tips:")
            print("   • LinkedIn has rate limits - try reducing results_wanted")
            print("   • Consider using proxies if you get blocked")
            print("   • Try different search terms or locations")
            return None
    
    def get_job_statistics(self, jobs_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get statistics from scraped jobs data.
        
        Args:
            jobs_df (pd.DataFrame): DataFrame containing job data
            
        Returns:
            Dict[str, Any]: Statistics about the jobs
        """
        if jobs_df is None or len(jobs_df) == 0:
            return {}
        
        # Convert numpy types to native Python types for JSON serialization
        stats = {
            'total_jobs': int(len(jobs_df)),
            'unique_companies': int(jobs_df['company'].nunique()) if 'company' in jobs_df.columns else 0,
            'unique_locations': int(jobs_df['location'].nunique()) if 'location' in jobs_df.columns else 0,
            'remote_jobs': int(jobs_df['is_remote'].sum()) if 'is_remote' in jobs_df.columns else 0,
            'fulltime_jobs': int((jobs_df['job_type'] == 'fulltime').sum()) if 'job_type' in jobs_df.columns else 0,
            'avg_min_salary': float(jobs_df['min_amount'].mean()) if 'min_amount' in jobs_df.columns and not jobs_df['min_amount'].isna().all() else 0.0,
            'avg_max_salary': float(jobs_df['max_amount'].mean()) if 'max_amount' in jobs_df.columns and not jobs_df['max_amount'].isna().all() else 0.0,
        }
        
        return stats
    
    def format_jobs_for_api(self, jobs_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Format jobs data for API response.
        
        Args:
            jobs_df (pd.DataFrame): DataFrame containing job data
            
        Returns:
            List[Dict[str, Any]]: Formatted job data for API
        """
        if jobs_df is None or len(jobs_df) == 0:
            return []
        
        jobs_list = []
        for _, job in jobs_df.iterrows():
            # Convert numpy types to native Python types for JSON serialization
            job_data = {
                'title': str(job.get('title', '')) if pd.notna(job.get('title')) else '',
                'company': str(job.get('company', '')) if pd.notna(job.get('company')) else '',
                'location': str(job.get('location', '')) if pd.notna(job.get('location')) else '',
                'description': str(job.get('description', '')) if pd.notna(job.get('description')) else '',
                'url': str(job.get('job_url', '')) if pd.notna(job.get('job_url')) else '',
                'posted_date': str(job.get('date_posted', '')) if pd.notna(job.get('date_posted')) else '',
                'job_type': str(job.get('job_type', '')) if pd.notna(job.get('job_type')) else '',
                'is_remote': bool(job.get('is_remote', False)) if pd.notna(job.get('is_remote')) else False,
                'min_salary': int(job.get('min_amount', 0)) if pd.notna(job.get('min_amount')) else 0,
                'max_salary': int(job.get('max_amount', 0)) if pd.notna(job.get('max_amount')) else 0,
                'currency': str(job.get('currency', 'USD')) if pd.notna(job.get('currency')) else 'USD',
                'emails': list(job.get('emails', [])) if pd.notna(job.get('emails')) else [],
                'company_url': str(job.get('company_url', '')) if pd.notna(job.get('company_url')) else '',
                'company_industry': str(job.get('company_industry', '')) if pd.notna(job.get('company_industry')) else '',
                'company_num_employees': str(job.get('company_num_employees', '')) if pd.notna(job.get('company_num_employees')) else '',
                'company_revenue': str(job.get('company_revenue', '')) if pd.notna(job.get('company_revenue')) else '',
                'scraped_at': datetime.now().isoformat()
            }
            jobs_list.append(job_data)
        
        return jobs_list
