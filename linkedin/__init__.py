"""
LinkedIn Integration Module for EdFast
Provides job scraping and post scraping functionality
"""

from .job_scraper import LinkedInJobScraper
from .post_scraper import LinkedInPostScraper
from .models import LinkedInJob, LinkedInPost

__all__ = ['LinkedInJobScraper', 'LinkedInPostScraper', 'LinkedInJob', 'LinkedInPost']
