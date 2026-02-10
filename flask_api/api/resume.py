"""
Resume Builder API Endpoints
Handles resume creation, auto-fill, AI suggestions, and PDF generation
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth import get_user_resume_data, update_user_resume_data, get_user_description, UserService
from data.data_extraction import extract_info_from_description, extract_info_from_transcript
from data.transcript_processing import generate_resume_content
from resume.pdf_generator import generate_resume_pdf

resume_bp = Blueprint('resume', __name__)


@resume_bp.route('/', methods=['GET'])
@jwt_required()
def get_resume():
    """Get current user's resume data"""
    try:
        username = get_jwt_identity()
        resume_data = get_user_resume_data(username)
        
        # Convert backend format to frontend format
        frontend_data = {
            'personal_info': resume_data.get('personal_info', {}) if resume_data else {},
            'education': resume_data.get('education', []) if resume_data else [],
            'experience': resume_data.get('work_experience', []) if resume_data else [],
            'skills': resume_data.get('skills', []) if resume_data else [],
            'projects': resume_data.get('projects', []) if resume_data else [],
            'certifications': resume_data.get('certifications', []) if resume_data else [],
            'languages': resume_data.get('languages', []) if resume_data else [],
            'objective': resume_data.get('objective', '') if resume_data else '',
            'linkedin': resume_data.get('linkedin', '') if resume_data else '',
            'github': resume_data.get('github', '') if resume_data else '',
            'website': resume_data.get('website', '') if resume_data else ''
        }
        
        return jsonify({
            'success': True,
            'data': frontend_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get resume data',
            'message': str(e)
        }), 500


@resume_bp.route('/', methods=['PUT'])
@jwt_required()
def update_resume():
    """
    Update resume data
    
    Request Body:
    {
        "resume_data": {
            "personal_info": {...},
            "education": [...],
            "skills": [...],
            "experience": [...],
            "projects": [...],
            "certifications": [...],
            "languages": [...]
        }
    }
    """
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'resume_data' not in data:
            return jsonify({
                'success': False,
                'error': 'resume_data is required'
            }), 400
        
        # Convert frontend format to backend format
        frontend_data = data['resume_data']
        backend_data = {
            'personal_info': frontend_data.get('personal_info', {}),
            'education': frontend_data.get('education', []),
            'work_experience': frontend_data.get('experience', []),
            'skills': frontend_data.get('skills', []),
            'projects': frontend_data.get('projects', []),
            'certifications': frontend_data.get('certifications', []),
            'languages': frontend_data.get('languages', []),
            'objective': frontend_data.get('objective', ''),
            'linkedin': frontend_data.get('linkedin', ''),
            'github': frontend_data.get('github', ''),
            'website': frontend_data.get('website', '')
        }
        
        update_user_resume_data(username, backend_data)
        
        return jsonify({
            'success': True,
            'message': 'Resume updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update resume',
            'message': str(e)
        }), 500


@resume_bp.route('/autofill', methods=['POST'])
@jwt_required()
def autofill_resume():
    """Auto-fill resume from transcript and description"""
    try:
        username = get_jwt_identity()
        
        # Get transcript data
        transcript_data = None
        if UserService:
            from auth.db_user_service import UserService
            transcript_data = UserService.get_user_transcript_data(username)
        
        # Get user description
        user_description = get_user_description(username)
        
        if not transcript_data and not user_description:
            return jsonify({
                'success': False,
                'error': 'No transcript or description found. Please upload transcript and add description first.'
            }), 400
        
        # Extract information
        description_info = extract_info_from_description(user_description) if user_description else {}
        transcript_info = extract_info_from_transcript(transcript_data) if transcript_data else {}
        
        # Merge information
        resume_data = {
            'personal_info': {
                'name': transcript_data.get('student_name', '') if transcript_data else '',
                'email': '',
                'phone': '',
                'address': '',
                'linkedin': '',
                'github': '',
                'website': ''
            },
            'education': transcript_info.get('education', []),
            'skills': list(set(description_info.get('skills', []) + transcript_info.get('skills', []))),
            'work_experience': description_info.get('work_experience', []),
            'projects': description_info.get('projects', []),
            'certifications': description_info.get('certifications', []),
            'languages': description_info.get('languages', []),
            'objective': '',
            'linkedin': '',
            'github': '',
            'website': ''
        }
        
        # Update user resume data
        update_user_resume_data(username, resume_data)
        
        # Convert to frontend format
        frontend_data = {
            'personal_info': resume_data.get('personal_info', {}),
            'education': resume_data.get('education', []),
            'experience': resume_data.get('work_experience', []),
            'skills': resume_data.get('skills', []),
            'projects': resume_data.get('projects', []),
            'certifications': resume_data.get('certifications', []),
            'languages': resume_data.get('languages', []),
            'objective': resume_data.get('objective', ''),
            'linkedin': resume_data.get('linkedin', ''),
            'github': resume_data.get('github', ''),
            'website': resume_data.get('website', '')
        }
        
        return jsonify({
            'success': True,
            'message': 'Resume auto-filled successfully',
            'data': frontend_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to auto-fill resume',
            'message': str(e)
        }), 500


@resume_bp.route('/suggestions', methods=['POST'])
@jwt_required()
def get_suggestions():
    """
    Get AI-powered resume suggestions
    
    Request Body:
    {
        "section": "optional section name" (skills, experience, etc.)
    }
    """
    try:
        username = get_jwt_identity()
        
        # Get transcript data
        transcript_data = None
        if UserService:
            from auth.db_user_service import UserService
            transcript_data = UserService.get_user_transcript_data(username)
        
        # Get user description
        user_description = get_user_description(username)
        
        # Get current resume data
        resume_data = get_user_resume_data(username)
        
        # Generate suggestions using Gemini AI
        suggestions = generate_resume_content(
            transcript_data,
            user_description,
            resume_data
        )
        
        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to generate suggestions',
            'message': str(e)
        }), 500


@resume_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_pdf():
    """
    Generate PDF resume
    
    Request Body:
    {
        "style": "professional" | "modern" | "creative" (default: professional)
    }
    """
    try:
        username = get_jwt_identity()
        data = request.get_json() or {}
        
        style = data.get('style', 'professional')
        
        if style not in ['professional', 'modern', 'creative']:
            return jsonify({
                'success': False,
                'error': 'Invalid style. Must be: professional, modern, or creative'
            }), 400
        
        # Get resume data
        resume_data = get_user_resume_data(username)
        
        if not resume_data or not resume_data.get('personal_info'):
            return jsonify({
                'success': False,
                'error': 'Resume data is incomplete. Please fill in your information first.'
            }), 400
        
        # Convert backend format to PDF generator format
        # Convert education data
        education_data = []
        for edu in resume_data.get('education', []):
            education_data.append({
                'degree': edu.get('degree', ''),
                'institution': edu.get('institution', ''),
                'location': '',  # Not used in frontend
                'graduation_date': edu.get('year', ''),  # Map year to graduation_date
                'gpa': edu.get('gpa', '')
            })
        
        # Convert work experience data
        work_experience_data = []
        for exp in resume_data.get('work_experience', []):
            work_experience_data.append({
                'position': exp.get('title', ''),  # Map title to position
                'company': exp.get('company', ''),
                'location': '',  # Not used in frontend
                'start_date': exp.get('duration', '').split(' - ')[0] if exp.get('duration') else '',  # Extract start date
                'end_date': exp.get('duration', '').split(' - ')[1] if exp.get('duration') and ' - ' in exp.get('duration') else 'Present',
                'description': exp.get('description', '')
            })
        
        # Convert projects data
        projects_data = []
        for proj in resume_data.get('projects', []):
            projects_data.append({
                'title': proj.get('name', ''),  # Map name to title
                'description': proj.get('description', ''),
                'technologies': proj.get('technologies', '').split(',') if proj.get('technologies') else [],
                'link': ''  # Not used in frontend
            })
        
        pdf_data = {
            'name': resume_data.get('personal_info', {}).get('name', ''),
            'email': resume_data.get('personal_info', {}).get('email', ''),
            'phone': resume_data.get('personal_info', {}).get('phone', ''),
            'address': resume_data.get('personal_info', {}).get('address', ''),
            'linkedin': resume_data.get('linkedin', ''),
            'github': resume_data.get('github', ''),
            'website': resume_data.get('website', ''),
            'objective': resume_data.get('objective', ''),
            'skills': resume_data.get('skills', []),
            'education': education_data,
            'work_experience': work_experience_data,
            'projects': projects_data,
            'certifications': resume_data.get('certifications', []),
            'languages': resume_data.get('languages', [])
        }
        
        # Generate PDF
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'resumes')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{username}_resume_{style}.pdf")
        
        generate_resume_pdf(pdf_data, output_file, style=style)
        
        # Send file
        return send_file(
            output_file,
            as_attachment=True,
            download_name=f"{resume_data['personal_info'].get('name', username)}_resume.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to generate PDF',
            'message': str(e)
        }), 500


@resume_bp.route('/completeness', methods=['GET'])
@jwt_required()
def check_completeness():
    """Check resume completeness"""
    try:
        username = get_jwt_identity()
        resume_data = get_user_resume_data(username)
        
        if not resume_data:
            return jsonify({
                'success': True,
                'data': {
                    'completeness': 0,
                    'missing_sections': ['all']
                }
            }), 200
        
        # Calculate completeness
        total_sections = 7  # personal_info, education, skills, experience, projects, certifications, languages
        completed_sections = 0
        missing_sections = []
        
        if resume_data.get('personal_info') and resume_data['personal_info'].get('name'):
            completed_sections += 1
        else:
            missing_sections.append('personal_info')
        
        if resume_data.get('education') and len(resume_data['education']) > 0:
            completed_sections += 1
        else:
            missing_sections.append('education')
        
        if resume_data.get('skills'):
            completed_sections += 1
        else:
            missing_sections.append('skills')
        
        if resume_data.get('experience') and len(resume_data['experience']) > 0:
            completed_sections += 1
        else:
            missing_sections.append('experience')
        
        if resume_data.get('projects') and len(resume_data['projects']) > 0:
            completed_sections += 1
        else:
            missing_sections.append('projects')
        
        if resume_data.get('certifications') and len(resume_data['certifications']) > 0:
            completed_sections += 1
        else:
            missing_sections.append('certifications')
        
        if resume_data.get('languages') and len(resume_data['languages']) > 0:
            completed_sections += 1
        else:
            missing_sections.append('languages')
        
        completeness = int((completed_sections / total_sections) * 100)
        
        return jsonify({
            'success': True,
            'data': {
                'completeness': completeness,
                'completed_sections': completed_sections,
                'total_sections': total_sections,
                'missing_sections': missing_sections
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to check completeness',
            'message': str(e)
        }), 500




