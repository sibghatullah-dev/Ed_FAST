"""
PDF Generator module for EdFast application.
Handles ATS-friendly resume PDF generation with multiple style options.
"""

from config.constants import RESUME_STYLES


def generate_resume_pdf(resume_data, output_file, style="professional"):
    """Generate a PDF resume with the specified style."""
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        # Get style configuration
        style_config = RESUME_STYLES.get(style, RESUME_STYLES["professional"])
        primary_color = colors.HexColor(style_config["color"])
        base_font_size = style_config["font_size"]
        
        # ATS-friendly document setup with standard margins
        doc = SimpleDocTemplate(
            output_file, 
            pagesize=LETTER,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        styles = getSampleStyleSheet()
        
        # Style-specific adjustments
        if style == "professional":
            header_size = base_font_size + 3
            section_size = base_font_size + 1
            name_color = colors.black
            section_color = primary_color
        elif style == "modern":
            header_size = base_font_size + 4
            section_size = base_font_size + 2
            name_color = primary_color
            section_color = primary_color
        else:  # creative
            header_size = base_font_size + 5
            section_size = base_font_size + 2
            name_color = primary_color
            section_color = colors.black
        
        # Dynamic styles based on selected template
        styles.add(ParagraphStyle(
            name='Name', 
            fontName='Helvetica-Bold', 
            fontSize=header_size, 
            leading=header_size + 4,
            alignment=1 if style == "modern" else 0,  # Center for modern style
            spaceAfter=8 if style == "creative" else 6,
            textColor=name_color
        ))
        
        styles.add(ParagraphStyle(
            name='ContactInfo', 
            fontName='Helvetica', 
            fontSize=base_font_size - 1, 
            leading=base_font_size + 1,
            alignment=1 if style == "modern" else 0,  # Center for modern style
            spaceAfter=4
        ))
        
        styles.add(ParagraphStyle(
            name='SectionTitle', 
            fontName='Helvetica-Bold', 
            fontSize=section_size, 
            leading=section_size + 2,
            spaceAfter=6,
            spaceBefore=12 if style == "creative" else 8,
            textColor=section_color,
            borderWidth=1 if style == "creative" else 0,
            borderColor=primary_color if style == "creative" else colors.white,
            borderPadding=2 if style == "creative" else 0
        ))
        
        styles.add(ParagraphStyle(
            name='SubHeading', 
            fontName='Helvetica-Bold', 
            fontSize=base_font_size,
            leading=base_font_size + 2,
            textColor=primary_color if style == "modern" else colors.black
        ))
        
        # Elements to add to the PDF
        elements = []
        
        # Name - Style-specific formatting
        name_text = resume_data.get('name', 'Full Name')
        if style == "creative":
            name_text = name_text.upper()
        
        elements.append(Paragraph(name_text, styles['Name']))
        
        # Contact info formatting based on style
        contact_parts = []
        if resume_data.get('email'):
            contact_parts.append(f"📧 {resume_data['email']}" if style == "creative" else f"Email: {resume_data['email']}")
        if resume_data.get('phone'):
            contact_parts.append(f"📱 {resume_data['phone']}" if style == "creative" else f"Phone: {resume_data['phone']}")
        if resume_data.get('address'):
            contact_parts.append(f"📍 {resume_data['address']}" if style == "creative" else f"Location: {resume_data['address']}")
        
        if contact_parts:
            separator = " • " if style == "modern" else " | "
            elements.append(Paragraph(separator.join(contact_parts), styles['ContactInfo']))
        
        # Professional links
        links_parts = []
        if resume_data.get('linkedin'):
            links_parts.append(f"LinkedIn: {resume_data['linkedin']}")
        if resume_data.get('github'):
            links_parts.append(f"GitHub: {resume_data['github']}")
        if resume_data.get('website'):
            links_parts.append(f"Portfolio: {resume_data['website']}")
        
        if links_parts:
            separator = " • " if style == "modern" else " | "
            elements.append(Paragraph(separator.join(links_parts), styles['ContactInfo']))
        
        # Spacing based on style
        if style == "creative":
            elements.append(Spacer(1, 0.3*inch))
        elif style == "modern":
            elements.append(Spacer(1, 0.25*inch))
        else:
            elements.append(Spacer(1, 0.2*inch))
        
        # Section headers with style-specific formatting
        def add_section_header(title):
            if style == "creative":
                title = f"● {title.upper()}"
            elif style == "modern":
                title = f"▎{title}"
            elements.append(Paragraph(title, styles['SectionTitle']))
        
        # Professional Summary/Objective
        if resume_data.get('objective'):
            add_section_header('PROFESSIONAL SUMMARY')
            elements.append(Paragraph(resume_data['objective'], styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Skills section with style-specific formatting
        if resume_data.get('skills'):
            add_section_header('SKILLS')
            if style == "creative":
                # Group skills for creative style
                skills_text = ' • '.join(resume_data['skills'])
            elif style == "modern":
                # Bullet points for modern style
                skills_text = '<br/>'.join([f"• {skill}" for skill in resume_data['skills']])
            else:
                # Simple comma-separated for professional
                skills_text = ', '.join(resume_data['skills'])
            
            elements.append(Paragraph(skills_text, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Education section
        if resume_data.get('education'):
            add_section_header('EDUCATION')
            for edu in resume_data['education']:
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                location = edu.get('location', '')
                graduation_date = edu.get('graduation_date', '')
                gpa = edu.get('gpa', '')
                
                if style == "modern":
                    edu_text = f"<b>{degree}</b><br/>{institution}"
                    if location:
                        edu_text += f" • {location}"
                else:
                    edu_text = f"<b>{degree}</b>"
                    if institution:
                        edu_text += f", {institution}"
                    if location:
                        edu_text += f", {location}"
                
                elements.append(Paragraph(edu_text, styles['SubHeading']))
                
                details = []
                if graduation_date:
                    details.append(f"Graduation: {graduation_date}")
                if gpa:
                    details.append(f"GPA: {gpa}")
                
                if details:
                    separator = " • " if style == "modern" else " | "
                    elements.append(Paragraph(separator.join(details), styles['Normal']))
                
                elements.append(Spacer(1, 0.1*inch))
        
        # Work Experience section
        if resume_data.get('work_experience'):
            add_section_header('PROFESSIONAL EXPERIENCE')
            for exp in resume_data['work_experience']:
                position = exp.get('position', '')
                company = exp.get('company', '')
                location = exp.get('location', '')
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', 'Present')
                description = exp.get('description', '')
                
                if style == "modern":
                    exp_text = f"<b>{position}</b><br/>{company}"
                    if location:
                        exp_text += f" • {location}"
                else:
                    exp_text = f"<b>{position}</b>"
                    if company:
                        exp_text += f", {company}"
                    if location:
                        exp_text += f", {location}"
                
                elements.append(Paragraph(exp_text, styles['SubHeading']))
                
                if start_date:
                    date_range = f"{start_date} - {end_date if end_date else 'Present'}"
                    elements.append(Paragraph(date_range, styles['Normal']))
                
                if description:
                    elements.append(Spacer(1, 0.05*inch))
                    elements.append(Paragraph(description, styles['Normal']))
                
                elements.append(Spacer(1, 0.1*inch))
        
        # Projects section
        if resume_data.get('projects'):
            add_section_header('PROJECTS')
            for project in resume_data['projects']:
                title = project.get('title', '')
                description = project.get('description', '')
                technologies = project.get('technologies', [])
                link = project.get('link', '')
                
                elements.append(Paragraph(f"<b>{title}</b>", styles['SubHeading']))
                
                if description:
                    elements.append(Paragraph(description, styles['Normal']))
                
                if technologies:
                    tech_text = f"Technologies: {', '.join(technologies)}"
                    if style == "creative":
                        tech_text = f"🔧 {', '.join(technologies)}"
                    elements.append(Paragraph(tech_text, styles['Normal']))
                
                if link:
                    elements.append(Paragraph(f"Link: {link}", styles['Normal']))
                
                elements.append(Spacer(1, 0.1*inch))
        
        # Certifications
        if resume_data.get('certifications'):
            add_section_header('CERTIFICATIONS')
            for cert in resume_data['certifications']:
                name = cert.get('name', '')
                issuer = cert.get('issuer', '')
                date = cert.get('date', '')
                
                cert_text = f"{name}"
                if issuer:
                    cert_text += f", {issuer}"
                if date:
                    cert_text += f", {date}"
                
                if style == "creative":
                    cert_text = f"🏆 {cert_text}"
                
                elements.append(Paragraph(cert_text, styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
        
        # Languages
        if resume_data.get('languages'):
            add_section_header('LANGUAGES')
            lang_items = []
            for lang in resume_data['languages']:
                language = lang.get('language', '')
                proficiency = lang.get('proficiency', '')
                
                if language:
                    lang_text = language
                    if proficiency:
                        lang_text += f" ({proficiency})"
                    lang_items.append(lang_text)
            
            if lang_items:
                if style == "creative":
                    lang_text = '🌐 ' + ', '.join(lang_items)
                else:
                    lang_text = ', '.join(lang_items)
                elements.append(Paragraph(lang_text, styles['Normal']))
        
        # Build the PDF
        doc.build(elements)
        return True
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return False 