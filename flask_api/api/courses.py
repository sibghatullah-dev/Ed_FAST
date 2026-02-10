"""
Courses API Endpoints
Handles course catalog browsing and search
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

courses_bp = Blueprint('courses', __name__)

# Load courses data
COURSES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'courses.json'
)

def load_courses():
    """Load courses from JSON file"""
    try:
        with open(COURSES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        return None


@courses_bp.route('/', methods=['GET'])
def get_courses():
    """
    Get all courses
    
    Query Parameters:
        semester: Filter by semester number
        elective: Filter electives (true/false)
        limit: Number of courses (default: all)
        offset: Offset for pagination (default: 0)
    """
    try:
        courses_data = load_courses()
        
        if not courses_data:
            return jsonify({
                'success': False,
                'error': 'Courses data not available'
            }), 503
        
        # Get query parameters
        semester = request.args.get('semester')
        elective = request.args.get('elective')
        limit = request.args.get('limit')
        offset = int(request.args.get('offset', 0))
        
        # Extract all courses from semesters
        all_courses = []
        study_plan = courses_data.get('study_plan', {})
        for semester_key, semester_data in study_plan.items():
            if 'courses' in semester_data:
                for course in semester_data['courses']:
                    course_copy = course.copy()
                    course_copy['semester'] = semester_key.replace('semester_', '')
                    all_courses.append(course_copy)
        
        # Apply filters
        filtered_courses = all_courses
        
        if semester:
            filtered_courses = [c for c in filtered_courses if str(c.get('semester')) == str(semester)]
        
        if elective is not None:
            is_elective = elective.lower() == 'true'
            filtered_courses = [c for c in filtered_courses if c.get('elective', False) == is_elective]
        
        # Apply pagination
        if limit:
            limit = int(limit)
            filtered_courses = filtered_courses[offset:offset + limit]
        else:
            filtered_courses = filtered_courses[offset:]
        
        return jsonify({
            'success': True,
            'data': {
                'courses': filtered_courses,
                'count': len(filtered_courses),
                'total': len(all_courses)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get courses',
            'message': str(e)
        }), 500


@courses_bp.route('/<course_code>', methods=['GET'])
def get_course(course_code):
    """Get specific course by code"""
    try:
        courses_data = load_courses()
        
        if not courses_data:
            return jsonify({
                'success': False,
                'error': 'Courses data not available'
            }), 503
        
        # Search for course
        study_plan = courses_data.get('study_plan', {})
        for semester_key, semester_data in study_plan.items():
            if 'courses' in semester_data:
                for course in semester_data['courses']:
                    if course.get('code', '').upper() == course_code.upper():
                        course_copy = course.copy()
                        course_copy['semester'] = semester_key.replace('semester_', '')
                        return jsonify({
                            'success': True,
                            'data': course_copy
                        }), 200
        
        return jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get course',
            'message': str(e)
        }), 500


@courses_bp.route('/search', methods=['GET'])
def search_courses():
    """
    Search courses
    
    Query Parameters:
        q: Search query (searches in code, name, description)
        limit: Number of results (default: 20)
    """
    try:
        query = request.args.get('q', '').strip().lower()
        limit = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        courses_data = load_courses()
        
        if not courses_data:
            return jsonify({
                'success': False,
                'error': 'Courses data not available'
            }), 503
        
        # Search courses
        results = []
        study_plan = courses_data.get('study_plan', {})
        for semester_key, semester_data in study_plan.items():
            if 'courses' in semester_data:
                for course in semester_data['courses']:
                    # Search in code, name, and description
                    if (query in course.get('code', '').lower() or
                        query in course.get('name', '').lower() or
                        query in course.get('description', '').lower()):
                        
                        course_copy = course.copy()
                        course_copy['semester'] = semester_key.replace('semester_', '')
                        results.append(course_copy)
        
        # Limit results
        results = results[:limit]
        
        return jsonify({
            'success': True,
            'data': {
                'courses': results,
                'count': len(results),
                'query': query
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Search failed',
            'message': str(e)
        }), 500


@courses_bp.route('/electives', methods=['GET'])
def get_electives():
    """Get all elective courses"""
    try:
        courses_data = load_courses()
        
        if not courses_data:
            return jsonify({
                'success': False,
                'error': 'Courses data not available'
            }), 503
        
        # Extract elective courses
        electives = []
        study_plan = courses_data.get('study_plan', {})
        for semester_key, semester_data in study_plan.items():
            if 'courses' in semester_data:
                for course in semester_data['courses']:
                    if course.get('elective', False):
                        course_copy = course.copy()
                        course_copy['semester'] = semester_key.replace('semester_', '')
                        electives.append(course_copy)
        
        return jsonify({
            'success': True,
            'data': {
                'courses': electives,
                'count': len(electives)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get electives',
            'message': str(e)
        }), 500


@courses_bp.route('/semesters', methods=['GET'])
def get_semesters():
    """Get all semesters with course counts"""
    try:
        courses_data = load_courses()
        
        if not courses_data:
            return jsonify({
                'success': False,
                'error': 'Courses data not available'
            }), 503
        
        semesters = []
        study_plan = courses_data.get('study_plan', {})
        for semester_key, semester_data in study_plan.items():
            semesters.append({
                'semester': semester_key.replace('semester_', ''),
                'courses_count': len(semester_data.get('courses', [])),
                'key': semester_key
            })
        
        return jsonify({
            'success': True,
            'data': {
                'semesters': semesters,
                'count': len(semesters)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get semesters',
            'message': str(e)
        }), 500


@courses_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get course catalog statistics"""
    try:
        courses_data = load_courses()
        
        if not courses_data:
            return jsonify({
                'success': False,
                'error': 'Courses data not available'
            }), 503
        
        total_courses = 0
        electives = 0
        required = 0
        total_credits = 0
        
        study_plan = courses_data.get('study_plan', {})
        for semester_key, semester_data in study_plan.items():
            if 'courses' in semester_data:
                for course in semester_data['courses']:
                    total_courses += 1
                    if course.get('elective', False):
                        electives += 1
                    else:
                        required += 1
                    total_credits += course.get('credits', 0)
        
        return jsonify({
            'success': True,
            'data': {
                'total_courses': total_courses,
                'electives': electives,
                'required': required,
                'total_credits': total_credits,
                'semesters': len(courses_data)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get statistics',
            'message': str(e)
        }), 500


@courses_bp.route('/my-transcript', methods=['GET'])
@jwt_required()
def get_my_transcript_courses():
    """Get current user's transcript courses"""
    try:
        username = get_jwt_identity()
        
        # Get user's transcript data
        from auth.db_user_service import UserService
        transcript_data = UserService.get_user_transcript_data(username)
        
        if not transcript_data or 'transcript' not in transcript_data:
            return jsonify({
                'success': True,
                'data': {
                    'courses': [],
                    'count': 0,
                    'semesters': [],
                    'statistics': {
                        'total_courses': 0,
                        'total_credits': 0,
                        'cgpa': 0,
                        'semesters_completed': 0
                    }
                }
            }), 200
        
        # Extract courses from all semesters
        all_courses = []
        semesters = []
        total_credits = 0
        total_cgpa = 0
        semesters_count = 0
        
        transcript = transcript_data['transcript']
        semesters_data = transcript.get('semesters', [])
        
        for semester in semesters_data:
            semester_courses = semester.get('courses', [])
            semester_info = {
                'term': semester.get('term', ''),
                'summary': semester.get('summary', {}),
                'courses_count': len(semester_courses)
            }
            semesters.append(semester_info)
            
            for course in semester_courses:
                course_copy = course.copy()
                course_copy['semester'] = semester.get('term', '')
                all_courses.append(course_copy)
                total_credits += course.get('credit_hours', 0)
            
            # Get latest CGPA
            summary = semester.get('summary', {})
            if 'cgpa' in summary:
                total_cgpa = summary['cgpa']
                semesters_count += 1
        
        return jsonify({
            'success': True,
            'data': {
                'courses': all_courses,
                'count': len(all_courses),
                'semesters': semesters,
                'statistics': {
                    'total_courses': len(all_courses),
                    'total_credits': total_credits,
                    'cgpa': total_cgpa,
                    'semesters_completed': semesters_count
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get transcript courses',
            'message': str(e)
        }), 500


