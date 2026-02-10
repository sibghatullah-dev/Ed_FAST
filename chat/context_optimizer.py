"""
Context optimizer module for EdFast application.
Handles optimization of context for LLM queries to avoid token limits.
"""

from config.constants import MAX_CONTEXT_LENGTH, MAX_COURSES_DISPLAY, MAX_RECENT_COURSES


def create_optimized_context(transcript_data, user_description, user_input):
    """Create an optimized context that focuses on relevant information for the user's question."""
    context_parts = []
    
    # Analyze the user input to determine what information is most relevant
    user_input_lower = user_input.lower()
    
    # Always include comprehensive academic summary
    if transcript_data and 'transcript' in transcript_data:
        semesters = transcript_data['transcript']['semesters']
        latest_semester = semesters[-1]
        current_cgpa = latest_semester['summary']['cgpa']
        total_courses = sum(len(sem['courses']) for sem in semesters)
        total_credits = sum(sem['summary']['credits_earned'] for sem in semesters)
        
        context_parts.append(f"Academic Summary: {len(semesters)} semesters completed, {total_courses} courses, {total_credits} credits earned, Current CGPA: {current_cgpa}")
        
        # Include detailed semester-by-semester breakdown
        context_parts.append("\nSemester-by-Semester Breakdown:")
        for i, semester in enumerate(semesters, 1):
            semester_info = f"Semester {i}: {len(semester['courses'])} courses, {semester['summary']['credits_earned']} credits, CGPA: {semester['summary']['cgpa']}"
            context_parts.append(semester_info)
            
            # Include all courses with grades for each semester
            for course in semester['courses']:
                course_info = f"  - {course['code']}: {course['name']} (Grade: {course['grade']}, Credits: {course.get('credits', 'N/A')})"
                context_parts.append(course_info)
    
    # Include specific course information if question is about courses/grades
    if any(keyword in user_input_lower for keyword in ['course', 'grade', 'subject', 'class', 'performance', 'cgpa', 'gpa', 'ai', 'elective', 'prerequisite']):
        if transcript_data and 'transcript' in transcript_data:
            # Include all completed courses with grades
            completed_courses = []
            for semester in transcript_data['transcript']['semesters']:
                for course in semester['courses']:
                    completed_courses.append(f"{course['code']}: {course['name']} (Grade: {course['grade']})")
            
            if completed_courses:
                context_parts.append("\nCompleted Courses with Grades:")
                context_parts.extend(completed_courses)
    
    # Include user description if relevant
    if user_description and any(keyword in user_input_lower for keyword in ['skill', 'project', 'experience', 'work', 'internship']):
        # Truncate description if too long
        desc_summary = user_description[:MAX_CONTEXT_LENGTH] + "..." if len(user_description) > MAX_CONTEXT_LENGTH else user_description
        context_parts.append(f"\nAdditional Background: {desc_summary}")
    
    return "\n".join(context_parts)


def get_relevant_course_info(courses_data, user_input):
    """Extract relevant course information based on user query."""
    if not courses_data:
        return ""
    
    user_input_lower = user_input.lower()
    
    # Check if user is asking about courses
    if any(keyword in user_input_lower for keyword in ['course', 'subject', 'class', 'prerequisite', 'elective', 'semester', 'program', 'curriculum', 'ai', 'cs', 'elective']):
        course_info_parts = []
        
        # Add program information
        if 'program' in courses_data:
            course_info_parts.append(f"Program: {courses_data['program']}")
        if 'university' in courses_data:
            course_info_parts.append(f"University: {courses_data['university']}")
        
        # Check if asking about specific semester
        semester_keywords = ['semester 1', 'semester 2', 'semester 3', 'semester 4', 
                           'semester 5', 'semester 6', 'semester 7', 'semester 8',
                           'first semester', 'second semester', 'third semester', 'fourth semester',
                           'fifth semester', 'sixth semester', 'seventh semester', 'eighth semester']
        
        specific_semester = None
        for keyword in semester_keywords:
            if keyword in user_input_lower:
                if 'first' in keyword or '1' in keyword:
                    specific_semester = 'semester_1'
                elif 'second' in keyword or '2' in keyword:
                    specific_semester = 'semester_2'
                elif 'third' in keyword or '3' in keyword:
                    specific_semester = 'semester_3'
                elif 'fourth' in keyword or '4' in keyword:
                    specific_semester = 'semester_4'
                elif 'fifth' in keyword or '5' in keyword:
                    specific_semester = 'semester_5'
                elif 'sixth' in keyword or '6' in keyword:
                    specific_semester = 'semester_6'
                elif 'seventh' in keyword or '7' in keyword:
                    specific_semester = 'semester_7'
                elif 'eighth' in keyword or '8' in keyword:
                    specific_semester = 'semester_8'
                break
        
        # Handle AI/CS elective queries specifically
        if 'ai' in user_input_lower or 'artificial intelligence' in user_input_lower:
            course_info_parts.append("\nAI-Related Courses in BS Computer Science Program:")
            if 'study_plan' in courses_data:
                for semester_key, semester_data in courses_data['study_plan'].items():
                    semester_name = semester_key.replace('_', ' ').title()
                    ai_courses = []
                    for course in semester_data['courses']:
                        if 'ai' in course['code'].lower() or 'artificial intelligence' in course['name'].lower():
                            ai_courses.append(f"    • {course['code']}: {course['name']} ({course['credits']} credits)")
                            if course['prerequisite'] != 'None':
                                ai_courses.append(f"      Prerequisite: {course['prerequisite']}")
                    if ai_courses:
                        course_info_parts.append(f"  {semester_name}:")
                        course_info_parts.extend(ai_courses)
        
        # Handle CS elective queries
        elif 'elective' in user_input_lower or 'cs elective' in user_input_lower:
            course_info_parts.append("\nCS Electives Available in BS Computer Science Program:")
            if 'study_plan' in courses_data:
                for semester_key, semester_data in courses_data['study_plan'].items():
                    semester_name = semester_key.replace('_', ' ').title()
                    elective_courses = []
                    for course in semester_data['courses']:
                        if 'elective' in course['name'].lower() and 'cs' in course['code'].lower():
                            elective_courses.append(f"    • {course['code']}: {course['name']} ({course['credits']} credits)")
                            if course['prerequisite'] != 'None':
                                elective_courses.append(f"      Prerequisite: {course['prerequisite']}")
                    if elective_courses:
                        course_info_parts.append(f"  {semester_name}:")
                        course_info_parts.extend(elective_courses)
        
        # If asking about specific semester, provide detailed info
        elif specific_semester and 'study_plan' in courses_data and specific_semester in courses_data['study_plan']:
            semester_data = courses_data['study_plan'][specific_semester]
            course_info_parts.append(f"\n{specific_semester.replace('_', ' ').title()}:")
            course_info_parts.append(f"Total Credits: {semester_data['total_credits']}")
            course_info_parts.append("Courses:")
            for course in semester_data['courses']:
                course_info_parts.append(f"  • {course['code']}: {course['name']} ({course['credits']} credits)")
                if course['prerequisite'] != 'None':
                    course_info_parts.append(f"    Prerequisite: {course['prerequisite']}")
        else:
            # Provide overview of all semesters
            if 'study_plan' in courses_data:
                course_info_parts.append("\nComplete Study Plan:")
                for semester_key, semester_data in courses_data['study_plan'].items():
                    semester_name = semester_key.replace('_', ' ').title()
                    course_info_parts.append(f"\n{semester_name} ({semester_data['total_credits']} credits):")
                    for course in semester_data['courses'][:3]:  # Show first 3 courses per semester
                        course_info_parts.append(f"  • {course['code']}: {course['name']}")
                    if len(semester_data['courses']) > 3:
                        course_info_parts.append(f"  ... and {len(semester_data['courses']) - 3} more courses")
        
        return "\n".join(course_info_parts)
    
    return ""


def create_optimized_prompt(optimized_context, course_info, user_input):
    """Create an optimized prompt for the LLM."""
    prompt = f"""You are an experienced and friendly academic advisor for the BS Computer Science program at FAST-NU. Your goal is to have natural, conversational interactions with students while providing accurate, personalized guidance.

STUDENT'S ACADEMIC RECORD:
{optimized_context}

PROGRAM INFORMATION:
{course_info}

STUDENT'S QUESTION: {user_input}

RESPONSE GUIDELINES:
- Respond naturally as if you're having a real conversation with the student
- Use a warm, supportive, and professional tone
- Address the student's specific question directly
- Provide information that's relevant to their actual situation based on their transcript
- Use casual language where appropriate, but maintain professionalism
- Feel free to use conversational phrases like "I see that...", "Based on your transcript...", "It looks like..."
- Structure your response naturally - don't force bullet points unless they genuinely help
- Be concise but informative - answer what was asked without over-explaining
- If you notice something important about their academic record, mention it naturally
- Include specific course codes, names, and requirements only when directly relevant to the question
- If you need to make recommendations, explain your reasoning in a conversational way
- Adapt your level of detail to the question - simple questions get simple answers

IMPORTANT: 
- Only use information from the student's actual transcript and course data provided above
- Don't make assumptions about information that isn't provided
- If you don't have enough information to answer fully, say so naturally
- Keep your responses focused and avoid unnecessary formality or structured formats unless the question specifically asks for organization
- Your responses should sound like they're coming from a helpful advisor, not an automated system

Now, please respond to the student's question in a natural, conversational way."""
    
    return prompt 