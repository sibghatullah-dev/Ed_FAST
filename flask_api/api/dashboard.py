"""
Dashboard API Endpoints
Handles dashboard statistics and user activity data
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth import get_user_name, get_user_description, get_user_transcript, get_user_resume_data
from database.db_config import get_session
from database.models import User, Post, Comment, Vote

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for the current user"""
    try:
        username = get_jwt_identity()
        session = get_session()
        
        # Get user data
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get user's posts count
        user_posts_count = session.query(Post).filter(Post.author_id == user.id).count()
        
        # Get user's comments count
        user_comments_count = session.query(Comment).filter(Comment.author_id == user.id).count()
        
        # Get user's votes count
        user_votes_count = session.query(Vote).filter(Vote.user_id == user.id).count()
        
        # Get total activities (posts + comments + votes)
        total_activities = user_posts_count + user_comments_count + user_votes_count
        
        # Get courses count from transcript data
        courses_count = 0
        try:
            from auth.db_user_service import UserService
            transcript_data = UserService.get_user_transcript_data(username)
            if transcript_data and 'transcript' in transcript_data:
                # Count courses from all semesters
                total_courses = 0
                semesters = transcript_data['transcript'].get('semesters', [])
                for semester in semesters:
                    courses = semester.get('courses', [])
                    total_courses += len(courses)
                courses_count = total_courses
        except Exception as e:
            print(f"Error getting courses count: {e}")
            pass
        
        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_posts = session.query(Post).filter(
            Post.author_id == user.id,
            Post.created_at >= week_ago
        ).count()
        
        recent_comments = session.query(Comment).filter(
            Comment.author_id == user.id,
            Comment.created_at >= week_ago
        ).count()
        
        recent_activities = recent_posts + recent_comments
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': {
                'posts': user_posts_count,
                'comments': user_comments_count,
                'votes': user_votes_count,
                'activities': total_activities,
                'courses': courses_count,
                'recent_activities': recent_activities,
                'has_transcript': bool(get_user_transcript(username)),
                'has_resume': bool(get_user_resume_data(username))
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get dashboard stats',
            'message': str(e)
        }), 500


@dashboard_bp.route('/activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    """Get recent activity for the current user"""
    try:
        username = get_jwt_identity()
        session = get_session()
        
        # Get user first
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get recent posts by user
        recent_posts = session.query(Post).filter(
            Post.author_id == user.id
        ).order_by(Post.created_at.desc()).limit(3).all()
        
        # Get recent comments by user
        recent_comments = session.query(Comment).filter(
            Comment.author_id == user.id
        ).order_by(Comment.created_at.desc()).limit(3).all()
        
        # Combine and sort activities
        activities = []
        
        for post in recent_posts:
            activities.append({
                'type': 'post',
                'title': f'Posted: {post.title}',
                'description': f'New post in {post.course_code or "General"}',
                'created_at': post.created_at,
                'id': post.id
            })
        
        for comment in recent_comments:
            activities.append({
                'type': 'comment',
                'title': f'Commented on: {comment.post.title if comment.post else "Unknown Post"}',
                'description': f'Added a comment',
                'created_at': comment.created_at,
                'id': comment.id
            })
        
        # Sort by creation date
        activities.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Take only the 5 most recent
        activities = activities[:5]
        
        # Format timestamps
        for activity in activities:
            activity['time_ago'] = get_time_ago(activity['created_at'])
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': {
                'activities': activities
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get recent activity',
            'message': str(e)
        }), 500


def get_time_ago(created_at):
    """Get human-readable time ago string"""
    now = datetime.utcnow()
    diff = now - created_at
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"
