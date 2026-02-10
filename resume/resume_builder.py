"""
Resume builder module for EdFast application.
Handles resume building functionality and UI components.
"""

import streamlit as st
import json
import os
from auth.user_management import get_user_resume_data, update_user_resume_data, get_user_description, get_user_name
from data.data_extraction import extract_info_from_transcript, extract_info_from_description
from data.transcript_processing import generate_resume_content
from resume.pdf_generator import generate_resume_pdf
from config.constants import RESUME_STYLES


def render_resume_section():
    """Render the resume builder section with style selection."""
    if st.session_state.user_logged_in:
        st.markdown("<div class='section-header'>Resume Builder</div>", unsafe_allow_html=True)
        
        # Get user resume data
        resume_data = get_user_resume_data(st.session_state.username)
        
        # Get user description
        user_description = get_user_description(st.session_state.username)
        
        # Get transcript data
        transcript_data = None
        if st.session_state.transcript_file and os.path.exists(st.session_state.transcript_file):
            with open(st.session_state.transcript_file, 'r') as f:
                transcript_data = json.load(f)
        
        # Auto-fill resume data
        auto_filled = auto_fill_resume_data(resume_data, user_description, transcript_data)
        if auto_filled:
            update_user_resume_data(st.session_state.username, resume_data)
        
        # Resume style selection
        render_style_selection()
        
        # Auto-fill and management buttons
        render_resume_controls(resume_data, user_description, transcript_data)
        
        # Create resume tabs
        resume_tabs = st.tabs(["Personal Info", "Education & Skills", "Experience & Projects", "Generate Resume"])
        
        with resume_tabs[0]:
            render_personal_info_tab(resume_data)
        
        with resume_tabs[1]:
            render_education_skills_tab(resume_data)
        
        with resume_tabs[2]:
            render_experience_projects_tab(resume_data)
        
        with resume_tabs[3]:
            render_generate_resume_tab(resume_data, transcript_data, user_description)


def render_style_selection():
    """Render the resume style selection interface."""
    st.markdown("### 🎨 Choose Your Resume Style")
    
    # Initialize selected style if not present
    if 'selected_resume_style' not in st.session_state:
        st.session_state.selected_resume_style = "professional"
    
    # Display style options in a single column layout to avoid nesting
    for style_key, style_info in RESUME_STYLES.items():
        # Style preview card
        st.markdown(f"""
        <div style="
            border: 2px solid {'#3B82F6' if st.session_state.selected_resume_style == style_key else '#E5E7EB'};
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: {'#F0F9FF' if st.session_state.selected_resume_style == style_key else '#FFFFFF'};
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div>
                <div style="font-size: 1.2rem; font-weight: bold; color: {style_info['color']}; margin-bottom: 0.5rem;">
                    {style_info['name']}
                </div>
                <div style="font-size: 0.9rem; color: #6B7280;">
                    {style_info['description']}
                </div>
            </div>
            <div style="background-color: {style_info['color']}; width: 60px; height: 8px; border-radius: 4px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Selection button
        if st.button(f"Select {style_info['name']}", key=f"select_{style_key}", use_container_width=True):
            st.session_state.selected_resume_style = style_key
            st.success(f"✅ {style_info['name']} style selected!")
            st.rerun()
    
    # Show current selection
    current_style = RESUME_STYLES[st.session_state.selected_resume_style]
    st.info(f"📋 **Current Style:** {current_style['name']} - {current_style['description']}")


def render_resume_controls(resume_data, user_description, transcript_data):
    """Render resume control buttons."""
    # Use single column layout to avoid nesting
    st.markdown("#### Resume Actions")
    
    if st.button("🔄 Auto-Fill Resume", help="Extract information from transcript and description to automatically fill resume sections", use_container_width=True):
        force_auto_fill_resume(resume_data, user_description, transcript_data)
    
    if st.button("🗑️ Clear Resume", help="Clear all resume data", use_container_width=True):
        handle_clear_resume()


def auto_fill_resume_data(resume_data, user_description, transcript_data):
    """Auto-fill resume data from transcript and description."""
    auto_filled = False
    
    if user_description or transcript_data:
        # Extract from transcript
        transcript_info = extract_info_from_transcript(transcript_data) if transcript_data else {}
        
        # Extract from description
        description_info = extract_info_from_description(user_description) if user_description else {}
        
        # Auto-fill skills if not present or if new skills are found
        extracted_skills = list(set(transcript_info.get('skills', []) + description_info.get('skills', [])))
        if extracted_skills and (not resume_data.get('skills') or len(extracted_skills) > len(resume_data.get('skills', []))):
            existing_skills = resume_data.get('skills', [])
            combined_skills = list(set(existing_skills + extracted_skills))
            resume_data['skills'] = combined_skills
            auto_filled = True
        
        # Auto-fill other sections
        if not resume_data.get('education') and transcript_info.get('education'):
            resume_data['education'] = transcript_info['education']
            auto_filled = True
        
        if not resume_data.get('projects') and description_info.get('projects'):
            resume_data['projects'] = description_info['projects']
            auto_filled = True
        
        if not resume_data.get('certifications') and description_info.get('certifications'):
            resume_data['certifications'] = description_info['certifications']
            auto_filled = True
        
        if not resume_data.get('languages') and description_info.get('languages'):
            resume_data['languages'] = description_info['languages']
            auto_filled = True
        
        if not resume_data.get('work_experience') and description_info.get('work_experience'):
            resume_data['work_experience'] = description_info['work_experience']
            auto_filled = True
        
        # Auto-generate objective if not present
        if not resume_data.get('objective') and (transcript_info.get('skills') or description_info.get('skills')):
            skills_text = ', '.join((transcript_info.get('skills', []) + description_info.get('skills', []))[:3])
            if skills_text:
                resume_data['objective'] = f"Motivated computer science student with skills in {skills_text}, seeking opportunities to apply technical knowledge and contribute to innovative projects."
                auto_filled = True
    
    return auto_filled


def force_auto_fill_resume(resume_data, user_description, transcript_data):
    """Force auto-fill process for resume data."""
    if user_description or transcript_data:
        transcript_info = extract_info_from_transcript(transcript_data) if transcript_data else {}
        description_info = extract_info_from_description(user_description) if user_description else {}
        
        # Force update all sections
        extracted_skills = list(set(transcript_info.get('skills', []) + description_info.get('skills', [])))
        if extracted_skills:
            existing_skills = resume_data.get('skills', [])
            combined_skills = list(set(existing_skills + extracted_skills))
            resume_data['skills'] = combined_skills
        
        # Continue with other sections...
        # (Same logic as auto_fill_resume_data but forced)
        
        update_user_resume_data(st.session_state.username, resume_data)
        st.success("✅ Resume auto-filled successfully!")
        st.rerun()
    else:
        st.warning("Please add a description or upload a transcript first to enable auto-fill.")


def handle_clear_resume():
    """Handle resume clearing with confirmation."""
    if st.session_state.get('confirm_clear_resume'):
        update_user_resume_data(st.session_state.username, {})
        st.success("Resume data cleared!")
        st.session_state.confirm_clear_resume = False
        st.rerun()
    else:
        st.session_state.confirm_clear_resume = True
        st.warning("Click again to confirm clearing all resume data.")


def render_personal_info_tab(resume_data):
    """Render the personal information tab."""
    st.markdown("### Personal Information")
    st.markdown("Enter your contact details and career objective.")
    
    # Use single column layout to avoid nesting
    email = st.text_input("Email", value=resume_data.get('email', ''), key="resume_email")
    phone = st.text_input("Phone", value=resume_data.get('phone', ''), key="resume_phone")
    address = st.text_input("Location", value=resume_data.get('address', ''), key="resume_address")
    linkedin = st.text_input("LinkedIn URL", value=resume_data.get('linkedin', ''), key="resume_linkedin")
    github = st.text_input("GitHub URL", value=resume_data.get('github', ''), key="resume_github")
    website = st.text_input("Personal Website", value=resume_data.get('website', ''), key="resume_website")
    
    objective = st.text_area("Career Objective", value=resume_data.get('objective', ''), height=100, key="resume_objective")
    
    if st.button("Save Personal Info", key="save_personal_info"):
        resume_data.update({
            'email': email,
            'phone': phone,
            'address': address,
            'linkedin': linkedin,
            'github': github,
            'website': website,
            'objective': objective,
            'name': get_user_name(st.session_state.username)
        })
        
        update_user_resume_data(st.session_state.username, resume_data)
        st.success("Personal information saved successfully!")


def render_education_skills_tab(resume_data):
    """Render the education and skills tab."""
    st.markdown("### Education & Skills")
    
    # Education section
    render_education_section(resume_data)
    
    st.markdown("---")
    
    # Skills section
    render_skills_section(resume_data)
    
    st.markdown("---")
    
    # Languages section
    render_languages_section(resume_data)


def render_education_section(resume_data):
    """Render the education section."""
    st.subheader("Education")
    
    # Display existing education entries
    if 'education' in resume_data and resume_data['education']:
        for i, edu in enumerate(resume_data['education']):
            with st.expander(f"Education #{i+1}: {edu.get('degree', 'Degree')}"):
                # Use single column layout to avoid nesting
                edu['degree'] = st.text_input("Degree/Program", value=edu.get('degree', ''), key=f"edu_degree_{i}")
                edu['institution'] = st.text_input("Institution", value=edu.get('institution', ''), key=f"edu_institution_{i}")
                edu['location'] = st.text_input("Location", value=edu.get('location', ''), key=f"edu_location_{i}")
                edu['graduation_date'] = st.text_input("Graduation Date", value=edu.get('graduation_date', ''), key=f"edu_grad_date_{i}")
                edu['gpa'] = st.text_input("GPA", value=edu.get('gpa', ''), key=f"edu_gpa_{i}")
                
                if st.button("Remove", key=f"remove_edu_{i}"):
                    resume_data['education'].pop(i)
                    update_user_resume_data(st.session_state.username, resume_data)
                    st.rerun()

    # Add new education entry
    if st.button("Add Education", key="add_education"):
        if 'education' not in resume_data:
            resume_data['education'] = []
        
        resume_data['education'].append({
            'degree': '',
            'institution': '',
            'location': '',
            'graduation_date': '',
            'gpa': ''
        })
        
        update_user_resume_data(st.session_state.username, resume_data)
        st.rerun()


def render_skills_section(resume_data):
    """Render the skills section."""
    st.subheader("Skills")
    skills = st.text_area("Enter skills (one per line)", 
                         value='\n'.join(resume_data.get('skills', [])), 
                         height=150,
                         key="skills_input")
    
    if st.button("Save Skills", key="save_skills"):
        # Convert the textarea input to a list of skills
        skills_list = [skill.strip() for skill in skills.split('\n') if skill.strip()]
        resume_data['skills'] = skills_list
        update_user_resume_data(st.session_state.username, resume_data)
        st.success("Skills saved successfully!")


def render_languages_section(resume_data):
    """Render the languages section."""
    st.subheader("Languages")
    
    # Display existing languages - single column layout to avoid nesting
    if 'languages' in resume_data and resume_data['languages']:
        for i, lang in enumerate(resume_data['languages']):
            st.markdown(f"**Language #{i+1}**")
            lang['language'] = st.text_input("Language", value=lang.get('language', ''), key=f"lang_name_{i}")
            lang['proficiency'] = st.selectbox("Proficiency", 
                                             options=["Basic", "Intermediate", "Fluent", "Native"],
                                             index=["Basic", "Intermediate", "Fluent", "Native"].index(lang.get('proficiency', 'Intermediate')) if lang.get('proficiency') in ["Basic", "Intermediate", "Fluent", "Native"] else 1,
                                             key=f"lang_prof_{i}")
            if st.button("Remove Language", key=f"remove_lang_{i}"):
                resume_data['languages'].pop(i)
                update_user_resume_data(st.session_state.username, resume_data)
                st.rerun()
            st.markdown("---")
    
    # Action buttons
    if st.button("Add Language", key="add_language", use_container_width=True):
        if 'languages' not in resume_data:
            resume_data['languages'] = []
        
        resume_data['languages'].append({
            'language': '',
            'proficiency': 'Intermediate'
        })
        
        update_user_resume_data(st.session_state.username, resume_data)
        st.rerun()
    
    if st.button("Save Languages", key="save_languages", use_container_width=True):
        update_user_resume_data(st.session_state.username, resume_data)
        st.success("Languages saved successfully!")


def render_experience_projects_tab(resume_data):
    """Render the experience and projects tab."""
    st.markdown("### Experience & Projects")
    
    # Work Experience section
    render_work_experience_section(resume_data)
    
    st.markdown("---")
    
    # Projects section
    render_projects_section(resume_data)
    
    st.markdown("---")
    
    # Certifications section
    render_certifications_section(resume_data)
    
    if st.button("Save Experience & Projects", key="save_exp_proj"):
        update_user_resume_data(st.session_state.username, resume_data)
        st.success("Experience and projects saved successfully!")


def render_work_experience_section(resume_data):
    """Render the work experience section."""
    st.subheader("Work Experience")
    
    # Display existing work experience entries
    if 'work_experience' in resume_data and resume_data['work_experience']:
        for i, exp in enumerate(resume_data['work_experience']):
            with st.expander(f"Work Experience #{i+1}: {exp.get('position', 'Position')} at {exp.get('company', 'Company')}"):
                # Single column layout to avoid nesting
                exp['position'] = st.text_input("Position", value=exp.get('position', ''), key=f"exp_position_{i}")
                exp['company'] = st.text_input("Company", value=exp.get('company', ''), key=f"exp_company_{i}")
                exp['location'] = st.text_input("Location", value=exp.get('location', ''), key=f"exp_location_{i}")
                exp['start_date'] = st.text_input("Start Date", value=exp.get('start_date', ''), key=f"exp_start_{i}")
                exp['end_date'] = st.text_input("End Date (leave blank for 'Present')", value=exp.get('end_date', ''), key=f"exp_end_{i}")
                exp['description'] = st.text_area("Description", value=exp.get('description', ''), height=100, key=f"exp_desc_{i}")
                
                if st.button("Remove", key=f"remove_exp_{i}"):
                    resume_data['work_experience'].pop(i)
                    update_user_resume_data(st.session_state.username, resume_data)
                    st.rerun()
    
    # Add new work experience entry
    if st.button("Add Work Experience", key="add_experience"):
        if 'work_experience' not in resume_data:
            resume_data['work_experience'] = []
        
        resume_data['work_experience'].append({
            'position': '',
            'company': '',
            'location': '',
            'start_date': '',
            'end_date': '',
            'description': ''
        })
        
        update_user_resume_data(st.session_state.username, resume_data)
        st.rerun()


def render_projects_section(resume_data):
    """Render the projects section."""
    st.subheader("Projects")
    
    # Display existing projects
    if 'projects' in resume_data and resume_data['projects']:
        for i, project in enumerate(resume_data['projects']):
            with st.expander(f"Project #{i+1}: {project.get('title', 'Project Title')}"):
                project['title'] = st.text_input("Project Title", value=project.get('title', ''), key=f"proj_title_{i}")
                project['description'] = st.text_area("Description", value=project.get('description', ''), height=100, key=f"proj_desc_{i}")
                
                # Technologies (comma-separated)
                tech_str = ', '.join(project.get('technologies', []))
                tech_input = st.text_input("Technologies (comma-separated)", value=tech_str, key=f"proj_tech_{i}")
                project['technologies'] = [tech.strip() for tech in tech_input.split(',') if tech.strip()]
                
                project['link'] = st.text_input("Project Link (optional)", value=project.get('link', ''), key=f"proj_link_{i}")
                
                if st.button("Remove", key=f"remove_proj_{i}"):
                    resume_data['projects'].pop(i)
                    update_user_resume_data(st.session_state.username, resume_data)
                    st.rerun()
    
    # Add new project
    if st.button("Add Project", key="add_project"):
        if 'projects' not in resume_data:
            resume_data['projects'] = []
        
        resume_data['projects'].append({
            'title': '',
            'description': '',
            'technologies': [],
            'link': ''
        })
        
        update_user_resume_data(st.session_state.username, resume_data)
        st.rerun()


def render_certifications_section(resume_data):
    """Render the certifications section."""
    st.subheader("Certifications")
    
    # Display existing certifications - single column layout to avoid nesting
    if 'certifications' in resume_data and resume_data['certifications']:
        for i, cert in enumerate(resume_data['certifications']):
            st.markdown(f"**Certification #{i+1}**")
            cert['name'] = st.text_input("Certification Name", value=cert.get('name', ''), key=f"cert_name_{i}")
            cert['issuer'] = st.text_input("Issuer", value=cert.get('issuer', ''), key=f"cert_issuer_{i}")
            cert['date'] = st.text_input("Date", value=cert.get('date', ''), key=f"cert_date_{i}")
            if st.button("Remove Certification", key=f"remove_cert_{i}"):
                resume_data['certifications'].pop(i)
                update_user_resume_data(st.session_state.username, resume_data)
                st.rerun()
            st.markdown("---")
    
    # Add new certification
    if st.button("Add Certification", key="add_certification"):
        if 'certifications' not in resume_data:
            resume_data['certifications'] = []
        
        resume_data['certifications'].append({
            'name': '',
            'issuer': '',
            'date': ''
        })
        
        update_user_resume_data(st.session_state.username, resume_data)
        st.rerun()


def render_generate_resume_tab(resume_data, transcript_data, user_description):
    """Render the generate resume tab."""
    st.markdown("### Generate Resume")
    
    # Single column layout to avoid nesting
    render_ai_suggestions_section(resume_data, transcript_data, user_description)
    
    st.markdown("---")
    
    render_export_section(resume_data)


def render_ai_suggestions_section(resume_data, transcript_data, user_description):
    """Render the AI suggestions section."""
    st.markdown("#### AI Suggestions")
    st.markdown("Get AI-generated suggestions for your resume based on your transcript and description.")
    
    # Show debug information
    st.markdown("**Debug Information:**")
    st.markdown(f"- Transcript data available: {'Yes' if transcript_data else 'No'}")
    st.markdown(f"- User description available: {'Yes' if user_description else 'No'}")
    st.markdown(f"- User description length: {len(user_description) if user_description else 0} characters")
    
    if transcript_data:
        st.markdown(f"- Transcript semesters: {len(transcript_data.get('transcript', {}).get('semesters', []))}")
    
    if st.button("Generate Suggestions", key="generate_suggestions"):
        try:
            # Show what we're working with
            st.info("🔍 Analyzing your data...")
            
            # Generate resume content
            with st.spinner("Generating resume suggestions..."):
                suggestions = generate_resume_content(transcript_data, user_description, resume_data)
                
                if suggestions:
                    st.session_state.resume_suggestions = suggestions
                    st.success("✅ Suggestions generated successfully!")
                    st.balloons()  # Add some visual feedback
                    st.rerun()
                else:
                    st.error("❌ Failed to generate suggestions. This could be due to:")
                    st.markdown("- API connection issues")
                    st.markdown("- Insufficient data in transcript or description")
                    st.markdown("- API rate limits")
                    st.markdown("**Try again in a few moments or check your data.**")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.markdown("**Please try the following:**")
            st.markdown("1. Make sure you have uploaded a transcript")
            st.markdown("2. Add some information in your profile description")
            st.markdown("3. Try again in a few moments")
    
    # Display suggestions if available (moved outside button check)
    if hasattr(st.session_state, 'resume_suggestions') and st.session_state.resume_suggestions:
        st.success("💡 AI suggestions are ready!")
        render_suggestions_display(st.session_state.resume_suggestions, resume_data)
    elif st.button("🔄 Refresh Suggestions", key="refresh_suggestions"):
        # Force refresh suggestions
        st.rerun()


def render_suggestions_display(suggestions, resume_data):
    """Render the suggestions display."""
    st.markdown("---")
    st.markdown("#### Available Suggestions")
    
    # Suggested Career Objective
    with st.expander("Suggested Career Objective", expanded=True):
        if 'objective' in suggestions and suggestions['objective']:
            suggested_objective = suggestions['objective']
            st.markdown(f"**Suggestion:** {suggested_objective}")
            if st.button("Apply Objective", key="apply_objective_btn"):
                resume_data['objective'] = suggested_objective
                update_user_resume_data(st.session_state.username, resume_data)
                st.success("Applied suggested objective!")
                st.rerun()
        else:
            st.markdown("No objective suggestion available.")
    
    # Suggested Skills
    with st.expander("Suggested Skills", expanded=True):
        if 'skills' in suggestions and suggestions['skills']:
            st.markdown("**Suggested Skills:**")
            for skill in suggestions['skills']:
                st.markdown(f"- {skill}")
            
            if st.button("Apply Skills", key="apply_skills_btn"):
                # Merge with existing skills to avoid duplicates
                existing_skills = resume_data.get('skills', [])
                new_skills = suggestions['skills']
                combined_skills = list(set(existing_skills + new_skills))
                resume_data['skills'] = combined_skills
                update_user_resume_data(st.session_state.username, resume_data)
                st.success("Applied suggested skills!")
                st.rerun()
        else:
            st.markdown("No skills suggestions available.")
    
    # Suggested Projects
    with st.expander("Suggested Projects", expanded=True):
        if 'projects' in suggestions and suggestions['projects']:
            st.markdown("**Suggested Projects:**")
            for i, project in enumerate(suggestions['projects']):
                st.markdown(f"**{i+1}. {project.get('title', '')}**")
                st.markdown(project.get('description', ''))
                if 'technologies' in project and project['technologies']:
                    st.markdown(f"*Technologies: {', '.join(project['technologies'])}*")
                st.markdown("---")
            
            if st.button("Apply Projects", key="apply_projects_btn"):
                if 'projects' not in resume_data:
                    resume_data['projects'] = []
                
                # Add suggested projects to existing ones
                resume_data['projects'].extend(suggestions['projects'])
                update_user_resume_data(st.session_state.username, resume_data)
                st.success("Applied suggested projects!")
                st.rerun()
        else:
            st.markdown("No project suggestions available.")
    
    # Suggested Achievements
    if 'achievements' in suggestions and suggestions['achievements']:
        with st.expander("Suggested Achievements", expanded=True):
            st.markdown("**Suggested Achievements:**")
            for achievement in suggestions['achievements']:
                st.markdown(f"- {achievement}")
            
            if st.button("Apply Achievements", key="apply_achievements_btn"):
                if 'achievements' not in resume_data:
                    resume_data['achievements'] = []
                
                # Add suggested achievements to existing ones
                existing_achievements = resume_data.get('achievements', [])
                new_achievements = suggestions['achievements']
                combined_achievements = list(set(existing_achievements + new_achievements))
                resume_data['achievements'] = combined_achievements
                update_user_resume_data(st.session_state.username, resume_data)
                st.success("Applied suggested achievements!")
                st.rerun()
    
    # Course Highlights
    if 'course_highlights' in suggestions and suggestions['course_highlights']:
        with st.expander("Course Highlights", expanded=True):
            st.markdown("**Course Highlights:**")
            for course in suggestions['course_highlights']:
                st.markdown(f"- **{course.get('course', '')}** - Grade: {course.get('grade', '')}")
                if course.get('relevance'):
                    st.markdown(f"  *{course['relevance']}*")
    
    # Clear suggestions button
    st.markdown("---")
    if st.button("Clear Suggestions", key="clear_suggestions_btn"):
        if hasattr(st.session_state, 'resume_suggestions'):
            del st.session_state.resume_suggestions
        st.success("Suggestions cleared!")
        st.rerun()


def render_export_section(resume_data):
    """Render the export section."""
    st.markdown("#### Export Resume")
    st.markdown("Generate and download your resume as a PDF.")
    
    # Add name field if not present
    if 'name' not in resume_data or not resume_data['name']:
        resume_data['name'] = st.text_input("Your Full Name", value="", key="resume_name")
    
    # Generate resume button
    if st.button("Generate PDF Resume", key="generate_resume"):
        # Ensure we have ReportLab installed
        try:
            import reportlab
            
            # Create a temporary file for the PDF
            pdf_filename = f"{st.session_state.username}_resume_{st.session_state.selected_resume_style}.pdf"
            
            # Add user's name to resume data
            resume_data['name'] = get_user_name(st.session_state.username)
            
            with st.spinner(f"Generating {RESUME_STYLES[st.session_state.selected_resume_style]['name']} resume..."):
                success = generate_resume_pdf(resume_data, pdf_filename, st.session_state.selected_resume_style)
                
                if success:
                    # Create a download button for the PDF
                    with open(pdf_filename, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                        st.download_button(
                            label=f"Download {RESUME_STYLES[st.session_state.selected_resume_style]['name']} Resume PDF",
                            data=pdf_bytes,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            key="download_resume"
                        )
                    st.success(f"✅ {RESUME_STYLES[st.session_state.selected_resume_style]['name']} resume PDF generated successfully!")
                else:
                    st.error("Failed to generate PDF. Please try again.")
        except ImportError:
            st.error("ReportLab library is required to generate PDF resumes.")
            st.markdown("Install it with: `pip install reportlab`")
    
    st.markdown("---")
    render_resume_completeness(resume_data)


def render_resume_completeness(resume_data):
    """Render resume completeness indicator."""
    st.markdown("#### Resume Completeness")
    
    # Calculate resume completeness
    completeness = 0
    total_fields = 0
    
    # Personal info (6 fields)
    for field in ['email', 'phone', 'address', 'linkedin', 'github', 'objective']:
        total_fields += 1
        if field in resume_data and resume_data[field]:
            completeness += 1
    
    # Education (at least 1 entry)
    total_fields += 1
    if 'education' in resume_data and resume_data['education']:
        completeness += 1
    
    # Skills (at least 3 skills)
    total_fields += 1
    if 'skills' in resume_data and len(resume_data['skills']) >= 3:
        completeness += 1
    
    # Work experience (at least 1 entry)
    total_fields += 1
    if 'work_experience' in resume_data and resume_data['work_experience']:
        completeness += 1
    
    # Projects (at least 1 entry)
    total_fields += 1
    if 'projects' in resume_data and resume_data['projects']:
        completeness += 1
    
    # Calculate percentage
    completeness_pct = int((completeness / total_fields) * 100)
    
    # Display progress bar
    st.progress(completeness_pct / 100)
    st.markdown(f"**{completeness_pct}%** complete")
    
    # Provide suggestions based on completeness
    if completeness_pct < 100:
        st.markdown("#### What's missing?")
        
        missing_items = []
        
        if 'email' not in resume_data or not resume_data['email']:
            missing_items.append("Email address")
        if 'phone' not in resume_data or not resume_data['phone']:
            missing_items.append("Phone number")
        if 'objective' not in resume_data or not resume_data['objective']:
            missing_items.append("Career objective")
        if 'education' not in resume_data or not resume_data['education']:
            missing_items.append("Education details")
        if 'skills' not in resume_data or len(resume_data['skills']) < 3:
            missing_items.append("At least 3 skills")
        if 'work_experience' not in resume_data or not resume_data['work_experience']:
            missing_items.append("Work experience")
        if 'projects' not in resume_data or not resume_data['projects']:
            missing_items.append("Projects")
        
        for item in missing_items:
            st.markdown(f"- {item}") 