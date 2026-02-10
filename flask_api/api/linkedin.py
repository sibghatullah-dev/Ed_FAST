"""
LinkedIn API Endpoints for EdFast Platform
Provides job scraping and post scraping functionality via REST API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin.job_scraper import LinkedInJobScraper
from linkedin.post_scraper import LinkedInPostScraper
from linkedin.models import LinkedInJob, LinkedInPost, LinkedInScrapingSession

# Create blueprint
linkedin_bp = Blueprint('linkedin', __name__)

# Global scraper instances (in production, use proper session management)
job_scraper = LinkedInJobScraper()
post_scraper = None  # Will be initialized when needed

@linkedin_bp.route('/jobs/search', methods=['POST'])
@jwt_required()
def search_jobs():
    """
    Search for LinkedIn jobs with specified criteria.
    
    Request Body:
    {
        "search_term": "software engineer",
        "location": "San Francisco, CA",
        "results_wanted": 20,
        "hours_old": 24,
        "job_type": "fulltime",
        "is_remote": false,
        "linkedin_fetch_description": true
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Extract parameters with defaults
        search_term = data.get('search_term', 'software engineer')
        location = data.get('location', 'San Francisco, CA')
        results_wanted = min(data.get('results_wanted', 20), 100)  # Limit to 100
        hours_old = data.get('hours_old')
        job_type = data.get('job_type')
        is_remote = data.get('is_remote', False)
        linkedin_fetch_description = data.get('linkedin_fetch_description', True)
        
        # Validate job_type
        if job_type and job_type not in ['fulltime', 'parttime', 'internship', 'contract']:
            return jsonify({
                'success': False,
                'error': 'Invalid job_type. Must be one of: fulltime, parttime, internship, contract'
            }), 400
        
        # Create session
        session_id = str(uuid.uuid4())
        session = LinkedInScrapingSession(
            session_id=session_id,
            session_type="job_scraping",
            search_params=data,
            results_count=0,
            started_at=datetime.now().isoformat(),
            status="running"
        )
        
        # Scrape jobs
        jobs_df = job_scraper.scrape_jobs(
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            job_type=job_type,
            is_remote=is_remote,
            linkedin_fetch_description=linkedin_fetch_description
        )
        
        if jobs_df is not None and len(jobs_df) > 0:
            # Format jobs for API response
            jobs_list = job_scraper.format_jobs_for_api(jobs_df)
            stats = job_scraper.get_job_statistics(jobs_df)
            
            # Update session
            session.results_count = len(jobs_list)
            session.completed_at = datetime.now().isoformat()
            session.status = "completed"
            
            return jsonify({
                'success': True,
                'message': f'Successfully scraped {len(jobs_list)} jobs',
                'session_id': session_id,
                'data': {
                    'jobs': jobs_list,
                    'statistics': stats,
                    'search_params': data
                }
            }), 200
        else:
            # Update session
            session.completed_at = datetime.now().isoformat()
            session.status = "completed"
            session.error_message = "No jobs found"
            
            return jsonify({
                'success': True,
                'message': 'No jobs found with the specified criteria',
                'session_id': session_id,
                'data': {
                    'jobs': [],
                    'statistics': {},
                    'search_params': data
                }
            }), 200
            
    except ImportError as e:
        return jsonify({
            'success': False,
            'error': 'LinkedIn job scraping not available',
            'message': str(e)
        }), 503
    except Exception as e:
        current_app.logger.error(f"LinkedIn job search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@linkedin_bp.route('/posts/scrape', methods=['POST'])
@jwt_required()
def scrape_posts():
    """
    Scrape LinkedIn posts from a profile or company page.
    
    Request Body:
    {
        "profile_url": "https://www.linkedin.com/company/example/posts/",
        "max_posts": 50,
        "headless": false
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        profile_url = data.get('profile_url')
        if not profile_url:
            return jsonify({
                'success': False,
                'error': 'profile_url is required'
            }), 400
        
        max_posts = min(data.get('max_posts', 50), 200)  # Limit to 200
        headless = data.get('headless', False)
        
        # Initialize post scraper
        global post_scraper
        post_scraper = LinkedInPostScraper(headless=headless)
        
        if not post_scraper.setup_chrome():
            return jsonify({
                'success': False,
                'error': 'Failed to setup Chrome WebDriver'
            }), 500
        
        # Create session
        session_id = str(uuid.uuid4())
        session = LinkedInScrapingSession(
            session_id=session_id,
            session_type="post_scraping",
            search_params=data,
            results_count=0,
            started_at=datetime.now().isoformat(),
            status="running"
        )
        
        # Login to LinkedIn
        if not post_scraper.login_to_linkedin():
            post_scraper.close()
            return jsonify({
                'success': False,
                'error': 'Failed to login to LinkedIn'
            }), 401
        
        # Scrape posts
        posts_data = post_scraper.scrape_posts_from_profile(profile_url, max_posts)
        
        # Close scraper
        post_scraper.close()
        
        if posts_data:
            # Update session
            session.results_count = len(posts_data)
            session.completed_at = datetime.now().isoformat()
            session.status = "completed"
            
            return jsonify({
                'success': True,
                'message': f'Successfully scraped {len(posts_data)} posts',
                'session_id': session_id,
                'data': {
                    'posts': posts_data,
                    'profile_url': profile_url,
                    'scraped_at': datetime.now().isoformat()
                }
            }), 200
        else:
            # Update session
            session.completed_at = datetime.now().isoformat()
            session.status = "completed"
            session.error_message = "No posts found"
            
            return jsonify({
                'success': True,
                'message': 'No posts found on the specified profile',
                'session_id': session_id,
                'data': {
                    'posts': [],
                    'profile_url': profile_url
                }
            }), 200
            
    except ImportError as e:
        return jsonify({
            'success': False,
            'error': 'LinkedIn post scraping not available',
            'message': str(e)
        }), 503
    except Exception as e:
        current_app.logger.error(f"LinkedIn post scraping error: {str(e)}")
        if post_scraper:
            post_scraper.close()
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@linkedin_bp.route('/jobs/statistics', methods=['GET'])
@jwt_required()
def get_job_statistics():
    """Get statistics about available job scraping functionality."""
    try:
        stats = {
            'job_scraper_available': job_scraper.scraper_available,
            'post_scraper_available': LinkedInPostScraper().selenium_available,
            'supported_job_types': ['fulltime', 'parttime', 'internship', 'contract'],
            'max_results_per_search': 100,
            'max_posts_per_scrape': 200
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"LinkedIn statistics error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@linkedin_bp.route('/health', methods=['GET'])
def linkedin_health():
    """Health check for LinkedIn scraping functionality."""
    try:
        health_status = {
            'job_scraper': job_scraper.scraper_available,
            'post_scraper': LinkedInPostScraper().selenium_available,
            'status': 'healthy' if (job_scraper.scraper_available or LinkedInPostScraper().selenium_available) else 'degraded'
        }
        
        return jsonify({
            'success': True,
            'data': health_status
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Health check failed',
            'message': str(e)
        }), 500

@linkedin_bp.route('/jobs/sample', methods=['GET'])
@jwt_required()
def get_sample_jobs():
    """Get sample job data structure for frontend development."""
    sample_job = {
        'title': 'Software Engineer',
        'company': 'Example Company',
        'location': 'San Francisco, CA',
        'description': 'We are looking for a talented software engineer...',
        'url': 'https://www.linkedin.com/jobs/view/1234567890',
        'posted_date': '2024-01-15',
        'job_type': 'fulltime',
        'is_remote': True,
        'min_salary': 80000,
        'max_salary': 120000,
        'currency': 'USD',
        'company_url': 'https://www.example.com',
        'company_industry': 'Technology',
        'company_num_employees': '1001-5000',
        'company_revenue': '$10M - $50M',
        'emails': ['hr@example.com'],
        'scraped_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': {
            'sample_job': sample_job,
            'description': 'This is a sample job data structure for frontend development'
        }
    }), 200

@linkedin_bp.route('/posts/sample', methods=['GET'])
@jwt_required()
def get_sample_posts():
    """Get sample post data structure for frontend development."""
    sample_post = {
        'post_url': 'https://www.linkedin.com/posts/example-1234567890',
        'content': 'This is a sample LinkedIn post content...',
        'type': 'Original',
        'like_count': '25',
        'comment_count': '5',
        'repost_count': '3',
        'img_url': 'https://example.com/image.jpg',
        'image_drive_link': 'https://drive.google.com/uc?id=example',
        'post_date': '2 days ago',
        'profile_url': 'https://www.linkedin.com/company/example',
        'scraped_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': {
            'sample_post': sample_post,
            'description': 'This is a sample post data structure for frontend development'
        }
    }), 200
