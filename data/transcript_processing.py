"""
Transcript processing module for EdFast application.
Handles transcript processing using Google's Gemini AI.
"""

import json
import streamlit as st
import google.generativeai as genai
from config.constants import GEMINI_API_KEY, GEMINI_MODEL_NAME


def initialize_gemini_api():
    """Initialize Gemini API with the configured API key."""
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        try:
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            return model
        except Exception as e:
            st.error(f"Error initializing Gemini API: {str(e)}")
            return None
    return None


def make_transcript_prompt():
    """Create a prompt for the Gemini model optimized for transcript extraction."""
    prompt_text = """
You are an expert in analyzing academic transcripts. I'm providing an image of a student transcript.
Extract all the information and structure it as a valid JSON following this template:

{
  "transcript": {
    "semesters": [
      {
        "term": "Fall 2021",
        "summary": {
          "credits_attempted": 17,
          "credits_earned": 14,
          "cgpa": 1.76,
          "sgpa": 1.76
        },
        "courses": [
          {
            "code": "CLI000",
            "name": "Introduction to Information and Communication Technology",
            "section": "BDS-1U",
            "credit_hours": 1,
            "grade": "B-",
            "points": 2.67,
            "type": "Core",
            "remarks": ""
          }
        ]
      }
    ]
  }
}

Important:
1. Include ALL semesters shown in the transcript.
2. For each semester, include a summary with credits attempted, credits earned, CGPA, and SGPA.
3. For each course, extract the course code, full name, section, credit hours, grade, points, type (Core/Elective), and any remarks.
4. Pay attention to courses that were retaken (often marked with R-1, R-2, etc. in remarks).
5. Format numbers as decimals (e.g., 3.67 not 3,67).
6. Ensure the JSON is properly formatted and valid.

Return ONLY the JSON object without any additional explanation.
"""
    return prompt_text


def extract_transcript_with_gemini(image):
    """Extract transcript data from an image using Gemini."""
    model = initialize_gemini_api()
    if model is None:
        st.error("Gemini API key is not set or invalid.")
        return None
    
    try:
        prompt = make_transcript_prompt()
        response = model.generate_content([prompt, image])
        extracted_text = response.text
        
        # Clean up the response to ensure it's valid JSON
        # Sometimes Gemini includes markdown code blocks
        if "```json" in extracted_text:
            extracted_text = extracted_text.split("```json")[1].split("```")[0].strip()
        elif "```" in extracted_text:
            extracted_text = extracted_text.split("```")[1].split("```")[0].strip()
            
        # Parse the JSON to validate it
        transcript_data = json.loads(extracted_text)
        return transcript_data
    except Exception as e:
        st.error(f"Error processing transcript with Gemini: {str(e)}")
        return None


def generate_resume_content(transcript_data, user_description, existing_resume_data):
    """Generate comprehensive resume content using transcript and description."""
    from data.data_extraction import extract_info_from_transcript, extract_info_from_description
    
    # Check if we're in a Streamlit context
    try:
        import streamlit as st
        in_streamlit = True
    except:
        in_streamlit = False
    
    def show_message(msg_type, message):
        """Helper function to show messages in appropriate context."""
        if in_streamlit:
            try:
                if msg_type == "info":
                    st.info(message)
                elif msg_type == "success":
                    st.success(message)
                elif msg_type == "warning":
                    st.warning(message)
                elif msg_type == "error":
                    st.error(message)
            except:
                print(f"{msg_type.upper()}: {message}")
        else:
            print(f"{msg_type.upper()}: {message}")
    
    model = initialize_gemini_api()
    if model is None:
        show_message("error", "❌ Gemini AI API not available. Please check API configuration.")
        return None
    
    try:
        show_message("info", "📊 Extracting information from your data...")
        
        # Extract information from transcript
        transcript_info = extract_info_from_transcript(transcript_data) if transcript_data else {}
        if transcript_data:
            show_message("success", f"✅ Extracted {len(transcript_info.get('skills', []))} skills from transcript")
        
        # Extract information from description
        description_info = extract_info_from_description(user_description) if user_description else {}
        if user_description:
            show_message("success", f"✅ Extracted {len(description_info.get('skills', []))} skills from description")
        
        # Check if we have any data to work with
        if not transcript_info and not description_info:
            show_message("warning", "⚠️ No transcript or description data available - generating basic suggestions")
            return {
                "objective": "Motivated computer science student seeking opportunities to apply technical knowledge and contribute to innovative projects.",
                "skills": ["Programming", "Problem Solving", "Teamwork"],
                "projects": [],
                "achievements": [],
                "course_highlights": []
            }
        
        # Combine information
        combined_info = {
            'skills': list(set(transcript_info.get('skills', []) + description_info.get('skills', []))),
            'education': transcript_info.get('education', []),
            'projects': description_info.get('projects', []),
            'certifications': description_info.get('certifications', []),
            'languages': description_info.get('languages', []),
            'work_experience': description_info.get('work_experience', []),
            'achievements': transcript_info.get('achievements', [])
        }
        
        show_message("info", f"🔗 Combined {len(combined_info['skills'])} total skills for AI analysis")
        
        # Create a prompt for generating resume content
        prompt = f"""
        You are a professional resume writer. I need you to enhance the following resume content based on the student's transcript and description.

        Current Resume Data:
        {json.dumps(existing_resume_data, indent=2)}

        Extracted Information:
        {json.dumps(combined_info, indent=2)}

        Please enhance the following sections:
        1. Career Objective: Create a compelling objective based on the student's academic performance and skills
        2. Skills: Organize and enhance the skills list, adding any relevant technical skills based on coursework
        3. Projects: Suggest project ideas based on the student's coursework and interests
        4. Achievements: Highlight academic achievements and notable grades
        5. Course Highlights: List the most relevant and high-performing courses

        Format your response as a valid JSON with these sections:
        {{
            "objective": "enhanced career objective",
            "skills": ["enhanced skills list"],
            "projects": [
                {{
                    "title": "project title",
                    "description": "project description",
                    "technologies": ["relevant technologies"]
                }}
            ],
            "achievements": ["list of achievements"],
            "course_highlights": [
                {{
                    "course": "course name",
                    "grade": "grade received",
                    "relevance": "why this course is important"
                }}
            ]
        }}

        Return ONLY the JSON object without any explanation.
        """
        
        show_message("info", "🤖 Sending request to AI...")
        response = model.generate_content(prompt)
        response_text = response.text
        
        show_message("success", "✅ AI response received, processing...")
        
        # Clean up the response to ensure it's valid JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Parse the JSON to validate it
        resume_suggestions = json.loads(response_text)
        
        # Validate the structure
        if not isinstance(resume_suggestions, dict):
            raise ValueError("Response is not a dictionary")
        
        # Ensure all required fields exist
        if 'objective' not in resume_suggestions:
            resume_suggestions['objective'] = "Motivated student seeking opportunities to apply knowledge and skills."
        
        if 'skills' not in resume_suggestions:
            resume_suggestions['skills'] = combined_info.get('skills', [])
        
        if 'projects' not in resume_suggestions:
            resume_suggestions['projects'] = []
            
        if 'achievements' not in resume_suggestions:
            resume_suggestions['achievements'] = combined_info.get('achievements', [])
            
        if 'course_highlights' not in resume_suggestions:
            resume_suggestions['course_highlights'] = []
        
        show_message("success", "✅ AI suggestions processed successfully!")
        return resume_suggestions
        
    except json.JSONDecodeError as e:
        show_message("error", f"❌ JSON parsing error: {str(e)}")
        show_message("error", "The AI response was not in valid JSON format. Providing fallback suggestions.")
        # Return a fallback response
        fallback_info = combined_info if 'combined_info' in locals() else {}
        return {
            "objective": "Motivated computer science student seeking opportunities to apply technical knowledge and contribute to innovative projects.",
            "skills": fallback_info.get('skills', ["Programming", "Problem Solving"]),
            "projects": fallback_info.get('projects', []),
            "achievements": fallback_info.get('achievements', []),
            "course_highlights": []
        }
    except Exception as e:
        show_message("error", f"❌ Error generating resume content: {str(e)}")
        # Return a fallback response with any available data
        fallback_skills = []
        fallback_achievements = []
        
        if transcript_data or user_description:
            transcript_info = extract_info_from_transcript(transcript_data) if transcript_data else {}
            description_info = extract_info_from_description(user_description) if user_description else {}
            fallback_skills = list(set(transcript_info.get('skills', []) + description_info.get('skills', [])))
            fallback_achievements = transcript_info.get('achievements', [])
        
        return {
            "objective": "Motivated student seeking opportunities to apply knowledge and skills in a professional environment.",
            "skills": fallback_skills if fallback_skills else ["Programming", "Problem Solving", "Teamwork"],
            "projects": [],
            "achievements": fallback_achievements,
            "course_highlights": []
        } 