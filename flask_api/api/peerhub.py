"""
PeerHub API Endpoints
Handles posts, comments, votes, and community features
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from peerhub import PeerHubService
from auth import UserService

peerhub_bp = Blueprint('peerhub', __name__)


def get_user_id_from_username(username):
    """Get user ID from username"""
    if UserService:
        user = UserService.get_user_by_username(username)
        return user.id if user else None
    return username


@peerhub_bp.route('/posts', methods=['GET'])
def get_posts():
    """
    Get posts with optional filters
    
    Query Parameters:
        limit: Number of posts (default: 50)
        offset: Offset for pagination (default: 0)
        tag: Filter by tag
        author: Filter by author username
        course_code: Filter by course code
        sort_by: Sort option (created_at, score, comments)
    """
    try:
        service = PeerHubService()
        
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        tag = request.args.get('tag')
        author_username = request.args.get('author')
        course_code = request.args.get('course_code')
        sort_by = request.args.get('sort_by', 'created_at')
        
        # Get author ID if username provided
        author_id = None
        if author_username:
            author_id = get_user_id_from_username(author_username)
        
        posts = service.get_posts(
            limit=limit,
            offset=offset,
            tag=tag,
            author_id=author_id,
            course_code=course_code,
            sort_by=sort_by
        )
        
        posts_data = []
        for post in posts:
            # Get author information
            author = service.get_user(post.author_id)
            author_name = author.name if author else "Unknown User"
            author_username = author.username if author else "unknown"
            
            post_data = post.to_dict() if hasattr(post, 'to_dict') else {
                'post_id': post.id if hasattr(post, 'id') else post.post_id,
                'title': post.title,
                'content': post.content,
                'author_id': post.author_id,
                'author_name': author_name,
                'author_username': author_username,
                'tags': post.tags,
                'file_link': post.file_link,
                'course_code': post.course_code,
                'course_name': post.course_name,
                'semester': post.semester,
                'upvotes': post.upvotes,
                'downvotes': post.downvotes,
                'score': post.score if hasattr(post, 'score') else (post.upvotes - post.downvotes),
                'comments_count': post.comments_count,
                'is_pinned': post.is_pinned,
                'created_at': post.created_at.isoformat() if hasattr(post.created_at, 'isoformat') else post.created_at,
                'updated_at': post.updated_at.isoformat() if hasattr(post.updated_at, 'isoformat') else post.updated_at
            }
            posts_data.append(post_data)
        
        return jsonify({
            'success': True,
            'data': {
                'posts': posts_data,
                'count': len(posts_data)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get posts',
            'message': str(e)
        }), 500


@peerhub_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """
    Create a new post
    
    Request Body:
    {
        "title": "Post title",
        "content": "Post content",
        "tags": ["tag1", "tag2"],
        "file_link": "optional file link",
        "course_code": "optional course code",
        "course_name": "optional course name",
        "semester": optional semester number
    }
    """
    try:
        username = get_jwt_identity()
        author_id = get_user_id_from_username(username)
        
        if not author_id:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Title and content are required'
            }), 400
        
        service = PeerHubService()
        post = service.create_post(
            title=data['title'],
            content=data['content'],
            author_id=author_id,
            tags=data.get('tags', []),
            file_link=data.get('file_link', ''),
            course_code=data.get('course_code'),
            course_name=data.get('course_name'),
            semester=data.get('semester')
        )
        
        if post:
            post_data = post.to_dict() if hasattr(post, 'to_dict') else {
                'post_id': post.id if hasattr(post, 'id') else post.post_id,
                'title': post.title,
                'content': post.content,
                'author_id': post.author_id,
                'tags': post.tags,
                'created_at': post.created_at.isoformat() if hasattr(post.created_at, 'isoformat') else post.created_at
            }
            
            return jsonify({
                'success': True,
                'message': 'Post created successfully',
                'data': post_data
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create post'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to create post',
            'message': str(e)
        }), 500


@peerhub_bp.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """Get a single post by ID"""
    try:
        service = PeerHubService()
        post = service.get_post(post_id)
        
        if not post:
            return jsonify({
                'success': False,
                'error': 'Post not found'
            }), 404
        
        # Get author information
        author = service.get_user(post.author_id)
        author_name = author.name if author else "Unknown User"
        author_username = author.username if author else "unknown"
        
        # Get comments for the post
        comments = service.get_comments(post_id)
        comments_data = []
        for c in comments:
            comment_author = service.get_user(c.author_id)
            comment_author_name = comment_author.name if comment_author else "Unknown User"
            comment_author_username = comment_author.username if comment_author else "unknown"
            
            comment_data = {
                'comment_id': c.id if hasattr(c, 'id') else c.comment_id,
                'post_id': c.post_id,
                'content': c.content,
                'author_id': c.author_id,
                'author_name': comment_author_name,
                'author_username': comment_author_username,
                'parent_id': c.parent_id,
                'upvotes': c.upvotes,
                'downvotes': c.downvotes,
                'score': c.score if hasattr(c, 'score') else (c.upvotes - c.downvotes),
                'created_at': c.created_at.isoformat() if hasattr(c.created_at, 'isoformat') else c.created_at
            }
            comments_data.append(comment_data)
        
        post_data = post.to_dict() if hasattr(post, 'to_dict') else {
            'post_id': post.id if hasattr(post, 'id') else post.post_id,
            'title': post.title,
            'content': post.content,
            'author_id': post.author_id,
            'author_name': author_name,
            'author_username': author_username,
            'tags': post.tags,
            'file_link': post.file_link,
            'course_code': post.course_code,
            'course_name': post.course_name,
            'upvotes': post.upvotes,
            'downvotes': post.downvotes,
            'score': post.score if hasattr(post, 'score') else (post.upvotes - post.downvotes),
            'comments_count': post.comments_count,
            'comments': comments_data,
            'created_at': post.created_at.isoformat() if hasattr(post.created_at, 'isoformat') else post.created_at
        }
        
        return jsonify({
            'success': True,
            'data': post_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get post',
            'message': str(e)
        }), 500


@peerhub_bp.route('/posts/<post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """
    Update a post
    
    Request Body:
    {
        "title": "Updated title",
        "content": "Updated content",
        "tags": ["tag1", "tag2"]
    }
    """
    try:
        username = get_jwt_identity()
        author_id = get_user_id_from_username(username)
        
        service = PeerHubService()
        post = service.get_post(post_id)
        
        if not post:
            return jsonify({
                'success': False,
                'error': 'Post not found'
            }), 404
        
        # Check if user is the author
        if post.author_id != author_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        data = request.get_json()
        
        if 'title' in data:
            post.title = data['title']
        if 'content' in data:
            post.content = data['content']
        if 'tags' in data:
            post.tags = data['tags']
        
        success = service.update_post(post)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Post updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update post'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update post',
            'message': str(e)
        }), 500


@peerhub_bp.route('/posts/<post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """Delete a post"""
    try:
        username = get_jwt_identity()
        author_id = get_user_id_from_username(username)
        
        service = PeerHubService()
        success = service.delete_post(post_id, author_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Post deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete post or unauthorized'
            }), 403
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete post',
            'message': str(e)
        }), 500


@peerhub_bp.route('/posts/<post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """Get comments for a post"""
    try:
        service = PeerHubService()
        comments = service.get_comments(post_id)
        
        comments_data = []
        for c in comments:
            # Get author information
            author = service.get_user(c.author_id)
            author_name = author.name if author else "Unknown User"
            author_username = author.username if author else "unknown"
            
            comment_data = c.to_dict() if hasattr(c, 'to_dict') else {
                'comment_id': c.id if hasattr(c, 'id') else c.comment_id,
                'post_id': c.post_id,
                'content': c.content,
                'author_id': c.author_id,
                'author_name': author_name,
                'author_username': author_username,
                'parent_id': c.parent_id,
                'upvotes': c.upvotes,
                'downvotes': c.downvotes,
                'score': c.score if hasattr(c, 'score') else (c.upvotes - c.downvotes),
                'created_at': c.created_at.isoformat() if hasattr(c.created_at, 'isoformat') else c.created_at
            }
            comments_data.append(comment_data)
        
        return jsonify({
            'success': True,
            'data': {
                'comments': comments_data,
                'count': len(comments_data)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get comments',
            'message': str(e)
        }), 500


@peerhub_bp.route('/posts/<post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    """
    Create a comment on a post
    
    Request Body:
    {
        "content": "Comment content",
        "parent_id": "optional parent comment ID for replies"
    }
    """
    try:
        username = get_jwt_identity()
        author_id = get_user_id_from_username(username)
        
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        service = PeerHubService()
        comment = service.create_comment(
            post_id=post_id,
            content=data['content'],
            author_id=author_id,
            parent_id=data.get('parent_id')
        )
        
        if comment:
            return jsonify({
                'success': True,
                'message': 'Comment created successfully',
                'data': {
                    'comment_id': comment.id if hasattr(comment, 'id') else comment.comment_id,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat() if hasattr(comment.created_at, 'isoformat') else comment.created_at
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create comment'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to create comment',
            'message': str(e)
        }), 500


@peerhub_bp.route('/posts/<post_id>/vote', methods=['POST'])
@jwt_required()
def vote_post(post_id):
    """
    Vote on a post
    
    Request Body:
    {
        "vote_type": "upvote" or "downvote"
    }
    """
    try:
        username = get_jwt_identity()
        user_id = get_user_id_from_username(username)
        
        data = request.get_json()
        
        if not data or 'vote_type' not in data:
            return jsonify({
                'success': False,
                'error': 'vote_type is required'
            }), 400
        
        vote_type = data['vote_type']
        if vote_type not in ['upvote', 'downvote']:
            return jsonify({
                'success': False,
                'error': 'Invalid vote_type. Must be "upvote" or "downvote"'
            }), 400
        
        service = PeerHubService()
        success = service.vote(user_id, 'post', post_id, vote_type)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'{vote_type.capitalize()} recorded successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to record vote'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to vote',
            'message': str(e)
        }), 500


@peerhub_bp.route('/search', methods=['GET'])
def search_posts():
    """
    Search posts
    
    Query Parameters:
        query: Search query
        limit: Number of results (default: 20)
    """
    try:
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        service = PeerHubService()
        posts = service.search_posts(query, limit=limit)
        
        posts_data = []
        for p in posts:
            # Get author information
            author = service.get_user(p.author_id)
            author_name = author.name if author else "Unknown User"
            author_username = author.username if author else "unknown"
            
            post_data = p.to_dict() if hasattr(p, 'to_dict') else {
                'post_id': p.id if hasattr(p, 'id') else p.post_id,
                'title': p.title,
                'content': p.content[:200] + '...' if len(p.content) > 200 else p.content,
                'author_id': p.author_id,
                'author_name': author_name,
                'author_username': author_username,
                'tags': p.tags,
                'score': p.score if hasattr(p, 'score') else (p.upvotes - p.downvotes),
                'created_at': p.created_at.isoformat() if hasattr(p.created_at, 'isoformat') else p.created_at
            }
            posts_data.append(post_data)
        
        return jsonify({
            'success': True,
            'data': {
                'posts': posts_data,
                'count': len(posts_data),
                'query': query
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Search failed',
            'message': str(e)
        }), 500


@peerhub_bp.route('/trending', methods=['GET'])
def get_trending():
    """
    Get trending posts
    
    Query Parameters:
        limit: Number of posts (default: 10)
        days: Number of days to consider (default: 7)
    """
    try:
        limit = int(request.args.get('limit', 10))
        days = int(request.args.get('days', 7))
        
        service = PeerHubService()
        posts = service.get_trending_posts(limit=limit, days=days)
        
        posts_data = []
        for p in posts:
            # Get author information
            author = service.get_user(p.author_id)
            author_name = author.name if author else "Unknown User"
            author_username = author.username if author else "unknown"
            
            post_data = p.to_dict() if hasattr(p, 'to_dict') else {
                'post_id': p.id if hasattr(p, 'id') else p.post_id,
                'title': p.title,
                'content': p.content[:200] + '...' if len(p.content) > 200 else p.content,
                'author_id': p.author_id,
                'author_name': author_name,
                'author_username': author_username,
                'tags': p.tags,
                'score': p.score if hasattr(p, 'score') else (p.upvotes - p.downvotes),
                'comments_count': p.comments_count,
                'created_at': p.created_at.isoformat() if hasattr(p.created_at, 'isoformat') else p.created_at
            }
            posts_data.append(post_data)
        
        return jsonify({
            'success': True,
            'data': {
                'posts': posts_data,
                'count': len(posts_data)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get trending posts',
            'message': str(e)
        }), 500


@peerhub_bp.route('/tags', methods=['GET'])
def get_tags():
    """
    Get popular tags
    
    Query Parameters:
        limit: Number of tags (default: 20)
    """
    try:
        limit = int(request.args.get('limit', 20))
        
        service = PeerHubService()
        tags = service.get_popular_tags(limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'tags': tags,
                'count': len(tags)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get tags',
            'message': str(e)
        }), 500


@peerhub_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    try:
        service = PeerHubService()
        stats = service.get_platform_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get statistics',
            'message': str(e)
        }), 500


@peerhub_bp.route('/courses', methods=['GET'])
def get_courses():
    """Get available courses with post counts"""
    try:
        service = PeerHubService()
        courses = service.get_available_courses()
        
        return jsonify({
            'success': True,
            'data': {
                'courses': courses,
                'count': len(courses)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get courses',
            'message': str(e)
        }), 500


@peerhub_bp.route('/courses/<course_code>', methods=['GET'])
def get_course_posts(course_code):
    """Get posts for a specific course"""
    try:
        service = PeerHubService()
        posts = service.get_posts_by_course(course_code)
        
        posts_data = []
        for p in posts:
            # Get author information
            author = service.get_user(p.author_id)
            author_name = author.name if author else "Unknown User"
            author_username = author.username if author else "unknown"
            
            post_data = p.to_dict() if hasattr(p, 'to_dict') else {
                'post_id': p.id if hasattr(p, 'id') else p.post_id,
                'title': p.title,
                'content': p.content,
                'author_id': p.author_id,
                'author_name': author_name,
                'author_username': author_username,
                'tags': p.tags,
                'file_link': p.file_link,
                'course_code': p.course_code,
                'course_name': p.course_name,
                'semester': p.semester,
                'upvotes': p.upvotes,
                'downvotes': p.downvotes,
                'score': p.score if hasattr(p, 'score') else (p.upvotes - p.downvotes),
                'comments_count': p.comments_count,
                'is_pinned': p.is_pinned,
                'created_at': p.created_at.isoformat() if hasattr(p.created_at, 'isoformat') else p.created_at,
                'updated_at': p.updated_at.isoformat() if hasattr(p.updated_at, 'isoformat') else p.updated_at
            }
            posts_data.append(post_data)
        
        return jsonify({
            'success': True,
            'data': {
                'posts': posts_data,
                'count': len(posts_data),
                'course_code': course_code
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get course posts',
            'message': str(e)
        }), 500


@peerhub_bp.route('/courses/<course_code>/stats', methods=['GET'])
def get_course_stats(course_code):
    """Get statistics for a specific course"""
    try:
        service = PeerHubService()
        stats = service.get_course_stats(course_code)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get course statistics',
            'message': str(e)
        }), 500


