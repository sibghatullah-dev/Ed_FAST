"""
Data extraction module for EdFast application.
Handles extraction of structured information from user descriptions and transcript data.
"""

import streamlit as st
from config.constants import DEFAULT_DEGREE, DEFAULT_INSTITUTION, DEFAULT_LOCATION, DEFAULT_GRADUATION


def extract_info_from_description(description):
    """Extract structured information from user's description."""
    if not description:
        return {}
    
    info = {
        'skills': [],
        'projects': [],
        'certifications': [],
        'languages': [],
        'work_experience': []
    }
    
    # Split description into lines
    lines = description.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for section headers
        lower_line = line.lower()
        if 'skills' in lower_line or 'technical skills' in lower_line:
            current_section = 'skills'
            continue
        elif 'projects' in lower_line or 'project' in lower_line:
            current_section = 'projects'
            continue
        elif 'certifications' in lower_line or 'certificates' in lower_line:
            current_section = 'certifications'
            continue
        elif 'languages' in lower_line:
            current_section = 'languages'
            continue
        elif 'experience' in lower_line or 'work' in lower_line:
            current_section = 'work_experience'
            continue
            
        # Process content based on current section
        if current_section == 'skills':
            # Split skills by common delimiters
            skills = [s.strip() for s in line.replace(',', ';').split(';') if s.strip()]
            info['skills'].extend(skills)
            
        elif current_section == 'projects':
            # Try to extract project information
            if ':' in line:
                title, desc = line.split(':', 1)
                info['projects'].append({
                    'title': title.strip(),
                    'description': desc.strip(),
                    'technologies': []
                })
            else:
                info['projects'].append({
                    'title': line,
                    'description': '',
                    'technologies': []
                })
                
        elif current_section == 'certifications':
            # Try to extract certification information
            if ':' in line:
                name, issuer = line.split(':', 1)
                info['certifications'].append({
                    'name': name.strip(),
                    'issuer': issuer.strip(),
                    'date': ''
                })
            else:
                info['certifications'].append({
                    'name': line,
                    'issuer': '',
                    'date': ''
                })
                
        elif current_section == 'languages':
            # Try to extract language and proficiency
            if '(' in line and ')' in line:
                lang, prof = line.split('(', 1)
                prof = prof.rstrip(')')
                info['languages'].append({
                    'language': lang.strip(),
                    'proficiency': prof.strip()
                })
            else:
                info['languages'].append({
                    'language': line,
                    'proficiency': 'Intermediate'
                })
                
        elif current_section == 'work_experience':
            # Try to extract work experience information
            if ':' in line:
                role, company = line.split(':', 1)
                info['work_experience'].append({
                    'position': role.strip(),
                    'company': company.strip(),
                    'location': '',
                    'start_date': '',
                    'end_date': '',
                    'description': ''
                })
    
    return info


def extract_info_from_transcript(transcript_data):
    """Extract structured information from transcript data."""
    if not transcript_data or 'transcript' not in transcript_data:
        return {}
    
    info = {
        'skills': set(),
        'education': [],
        'courses': [],
        'achievements': []
    }
    
    try:
        # Extract education information
        if 'transcript' in transcript_data and 'semesters' in transcript_data['transcript']:
            semesters = transcript_data['transcript']['semesters']
            
            # Get the latest semester for current CGPA
            latest_semester = semesters[-1]
            current_cgpa = latest_semester['summary']['cgpa']
            
            # Calculate total credits and courses
            total_credits = sum(sem['summary']['credits_earned'] for sem in semesters)
            total_courses = sum(len(sem['courses']) for sem in semesters)
            
            # Extract course information and skills
            for semester in semesters:
                for course in semester['courses']:
                    # Add course to courses list
                    course_info = {
                        'code': course['code'],
                        'name': course['name'],
                        'grade': course['grade'],
                        'credits': course['credit_hours'],
                        'type': course['type']
                    }
                    info['courses'].append(course_info)
                    
                    # Extract potential skills from course names
                    course_name = course['name'].lower()
                    if 'programming' in course_name or 'software' in course_name:
                        info['skills'].add('Programming')
                    if 'database' in course_name:
                        info['skills'].add('Database Management')
                    if 'network' in course_name:
                        info['skills'].add('Networking')
                    if 'algorithm' in course_name:
                        info['skills'].add('Algorithms')
                    if 'data structure' in course_name:
                        info['skills'].add('Data Structures')
                    if 'artificial intelligence' in course_name or 'ai' in course_name:
                        info['skills'].add('Artificial Intelligence')
                    if 'machine learning' in course_name:
                        info['skills'].add('Machine Learning')
                    if 'web' in course_name:
                        info['skills'].add('Web Development')
                    if 'security' in course_name:
                        info['skills'].add('Cybersecurity')
                    if 'cloud' in course_name:
                        info['skills'].add('Cloud Computing')
                    
                    # Add achievements for good grades
                    if course['grade'].startswith('A'):
                        info['achievements'].append(f"Received grade A in {course['name']}")
            
            # Add education summary
            info['education'].append({
                'degree': DEFAULT_DEGREE,
                'institution': DEFAULT_INSTITUTION,
                'location': DEFAULT_LOCATION,
                'graduation_date': DEFAULT_GRADUATION,
                'gpa': f"{current_cgpa:.2f}",
                'achievements': [
                    f"Completed {total_courses} courses with {total_credits} credit hours",
                    f"Maintained CGPA of {current_cgpa:.2f}"
                ]
            })
    
    except Exception as e:
        st.error(f"Error extracting information from transcript: {str(e)}")
    
    # Convert skills set to list
    info['skills'] = list(info['skills'])
    return info 