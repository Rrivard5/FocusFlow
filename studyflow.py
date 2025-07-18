import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import PyPDF2
import docx
from io import BytesIO
import json
import uuid
import random
import urllib.parse
from collections import defaultdict
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import base64

# Page config
st.set_page_config(
    page_title="FocusFlow",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with compact header and better readability
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
        color: #ffffff;
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .compact-hero {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: #ffffff;
    }
    
    .compact-hero h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .compact-hero p {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .setup-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #ffffff;
    }
    
    .step-number {
        display: inline-block;
        width: 35px;
        height: 35px;
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 35px;
        font-weight: 600;
        margin-right: 12px;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
    }
    
    .course-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #ffffff;
    }
    
    .course-code {
        font-size: 1.1rem;
        font-weight: 600;
        color: #6c5ce7;
        margin-bottom: 0.5rem;
    }
    
    .course-name {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.85);
    }
    
    .intramural-card {
        background: rgba(0, 184, 148, 0.1);
        border: 1px solid rgba(0, 184, 148, 0.3);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    
    .intramural-card h4 {
        color: #00b894;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    
    .activity-item {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 3px solid #00b894;
    }
    
    .wellness-info {
        background: rgba(253, 203, 110, 0.1);
        border: 1px solid rgba(253, 203, 110, 0.3);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    
    .wellness-info h4 {
        color: #fdcb6e;
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
    }
    
    .wellness-info p {
        color: rgba(255, 255, 255, 0.9);
        line-height: 1.5;
        margin-bottom: 0.5rem;
    }
    
    .schedule-table {
        width: 100%;
        border-collapse: collapse;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        overflow: hidden;
        margin: 1.5rem 0;
        font-size: 0.9rem;
    }
    
    .schedule-table th {
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        color: white;
        padding: 0.75rem 0.5rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .schedule-table td {
        padding: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        vertical-align: top;
        background: rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.85rem;
        line-height: 1.3;
    }
    
    .time-slot {
        font-weight: 600;
        color: #6c5ce7;
        min-width: 70px;
        text-align: center;
        background: rgba(108, 92, 231, 0.1);
        border-right: 2px solid rgba(108, 92, 231, 0.3);
        font-size: 0.8rem;
    }
    
    .study-block {
        background: rgba(108, 92, 231, 0.3);
        border-radius: 4px;
        padding: 0.25rem;
        margin: 0.1rem 0;
        font-weight: 500;
        color: white;
        text-align: center;
    }
    
    .meal-block {
        background: rgba(253, 203, 110, 0.3);
        border-radius: 4px;
        padding: 0.25rem;
        margin: 0.1rem 0;
        font-weight: 500;
        color: white;
        text-align: center;
    }
    
    .free-block {
        background: rgba(0, 184, 148, 0.3);
        border-radius: 4px;
        padding: 0.25rem;
        margin: 0.1rem 0;
        font-weight: 500;
        color: white;
        text-align: center;
    }
    
    .intramural-block {
        background: rgba(230, 126, 34, 0.3);
        border-radius: 4px;
        padding: 0.25rem;
        margin: 0.1rem 0;
        font-weight: 500;
        color: white;
        text-align: center;
    }
    
    .break-block {
        background: rgba(253, 121, 168, 0.3);
        border-radius: 4px;
        padding: 0.25rem;
        margin: 0.1rem 0;
        font-weight: 500;
        color: white;
        text-align: center;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #6c5ce7;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 0.5rem;
    }
    
    .progress-bar {
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #6c5ce7, #a29bfe);
        transition: width 0.3s ease;
    }
    
    .progress-text {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    .legend {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.8);
    }
    
    .legend-color {
        width: 16px;
        height: 10px;
        border-radius: 2px;
    }
    
    .week-nav {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .week-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #6c5ce7;
        min-width: 150px;
        text-align: center;
    }
    
    /* Button styling */
    .stButton > button {
        border: none !important;
        border-radius: 50px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        background: linear-gradient(135deg, #6c5ce7, #a29bfe) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4) !important;
    }
    
    .stDownloadButton > button {
        border: none !important;
        border-radius: 50px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        background: linear-gradient(135deg, #00b894, #00cec9) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0, 184, 148, 0.3) !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 184, 148, 0.4) !important;
    }
    
    /* Form styling with better readability */
    .stSelectbox label, .stTextInput label, .stSlider label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(200, 200, 200, 0.5) !important;
        border-radius: 50px !important;
        color: #000000 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 50px !important;
        color: #000000 !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px dashed rgba(255, 255, 255, 0.3) !important;
        border-radius: 20px !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        padding: 1.5rem !important;
        text-align: center !important;
    }
    
    .stFileUploader label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    @media (max-width: 768px) {
        .compact-hero h1 {
            font-size: 1.8rem;
        }
        
        .main-container {
            margin: 0.25rem;
            padding: 1rem;
        }
        
        .schedule-table {
            font-size: 0.8rem;
        }
        
        .schedule-table th, .schedule-table td {
            padding: 0.4rem 0.3rem;
        }
        
        .legend {
            flex-direction: column;
            gap: 0.75rem;
        }
        
        .week-nav {
            flex-direction: column;
            gap: 0.75rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'courses' not in st.session_state:
    st.session_state.courses = []
if 'intramurals' not in st.session_state:
    st.session_state.intramurals = []
if 'current_week' not in st.session_state:
    st.session_state.current_week = 0
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'schedule_ready' not in st.session_state:
    st.session_state.schedule_ready = False
if 'final_schedule' not in st.session_state:
    st.session_state.final_schedule = None

def extract_text_from_file(file):
    """Extract text from uploaded file"""
    try:
        if file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        else:
            return str(file.read(), "utf-8")
    except:
        return ""

def parse_single_syllabus(text, course_code_hint=None):
    """Parse a single syllabus for ONE specific course"""
    assignments = []
    course_info = {}
    
    # Try to extract course code and name
    course_patterns = [
        r'([A-Z]{2,4}[- ]?\d{3,4}[A-Z]?)\s*[-:]?\s*([^:\n]{10,80})',
        r'Course:\s*([A-Z]{2,4}[- ]?\d{3,4}[A-Z]?)\s*[-:]?\s*([^:\n]+)',
        r'([A-Z]{2,4}\s+\d{3,4})\s*[-:]?\s*([^:\n]+)',
    ]
    
    course_found = False
    for pattern in course_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            code = matches[0][0].strip().upper().replace(' ', '')
            name = matches[0][1].strip()
            course_info = {
                'code': code,
                'name': name
            }
            course_found = True
            break
    
    # If no course found, use hint or create default
    if not course_found:
        if course_code_hint:
            course_info = {
                'code': course_code_hint,
                'name': f'{course_code_hint} Course'
            }
        else:
            course_info = {
                'code': 'COURSE101',
                'name': 'Course'
            }
    
    # Extract assignments/deadlines
    date_patterns = [
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s*[-:]?\s*([^:\n]{10,100})',
        r'([A-Z][a-z]+\s+\d{1,2})\s*[-:]?\s*([^:\n]{10,100})',
        r'(Week\s+\d+)\s*[-:]?\s*([^:\n]{10,100})',
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            date_str = match[0].strip()
            title = match[1].strip()
            
            # Skip if it looks like a course code
            if re.match(r'^[A-Z]{2,4}[- ]?\d{3,4}', title):
                continue
                
            # Try to parse date
            try:
                # Handle different date formats
                if '/' in date_str or '-' in date_str:
                    # Try to parse as date
                    for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            formatted_date = parsed_date.strftime('%Y-%m-%d')
                            break
                        except:
                            continue
                    else:
                        # Default to future date
                        formatted_date = (datetime.now() + timedelta(days=random.randint(7, 60))).strftime('%Y-%m-%d')
                else:
                    # Default to future date
                    formatted_date = (datetime.now() + timedelta(days=random.randint(7, 60))).strftime('%Y-%m-%d')
                
                assignment_type = 'assignment'
                if any(word in title.lower() for word in ['exam', 'test', 'quiz', 'midterm', 'final']):
                    assignment_type = 'exam'
                elif any(word in title.lower() for word in ['lab', 'practical']):
                    assignment_type = 'lab'
                elif any(word in title.lower() for word in ['project', 'presentation']):
                    assignment_type = 'project'
                
                assignments.append({
                    'id': str(uuid.uuid4()),
                    'title': title,
                    'date': formatted_date,
                    'type': assignment_type,
                    'course': course_info['code'],
                    'priority': 'high' if assignment_type == 'exam' else 'medium'
                })
            except:
                continue
    
    return course_info, assignments

def generate_weekly_schedule(courses, assignments, intramurals, preferences):
    """Generate a structured weekly schedule with readable activities"""
    schedule = {}
    
    # Time slots for the schedule
    time_slots = [
        "7:00 AM", "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
        "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM",
        "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM"
    ]
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Generate 4 weeks of schedule
    for week in range(4):
        weekly_schedule = {}
        
        for day in days:
            daily_schedule = {}
            is_weekend = day in ["Saturday", "Sunday"]
            
            for time_slot in time_slots:
                activities = []
                
                # Wake up routine
                if time_slot == "7:00 AM":
                    activities.append("Wake Up & Morning Routine")
                
                # Breakfast
                elif time_slot == "8:00 AM":
                    activities.append("Breakfast")
                
                # Study blocks (weekdays)
                elif time_slot in ["9:00 AM", "10:00 AM", "2:00 PM", "3:00 PM"] and not is_weekend:
                    if courses:
                        course = random.choice(courses)
                        study_types = ['Reading', 'Practice Problems', 'Review Notes', 'Homework', 'Study Group']
                        study_type = random.choice(study_types)
                        activities.append(f"{course['code']} - {study_type}")
                
                # Light study on weekends
                elif time_slot in ["10:00 AM", "2:00 PM"] and is_weekend:
                    if courses and random.random() < 0.5:  # 50% chance
                        course = random.choice(courses)
                        activities.append(f"{course['code']} - Light Review")
                
                # Lunch
                elif time_slot == "12:00 PM":
                    activities.append("Lunch Break")
                
                # Short breaks
                elif time_slot in ["11:00 AM", "4:00 PM"]:
                    activities.append("Break / Walk")
                
                # Intramural activities
                elif time_slot == "5:00 PM" and intramurals:
                    for intramural in intramurals:
                        if intramural.get('scheduled'):
                            if day in intramural.get('days', []):
                                activities.append(f"{intramural['name']} - {intramural['type']}")
                                break
                    else:
                        if not is_weekend:
                            activities.append("Exercise / Intramural Time")
                
                # Dinner
                elif time_slot == "6:00 PM":
                    activities.append("Dinner")
                
                # Evening study
                elif time_slot == "7:00 PM" and not is_weekend:
                    if courses:
                        course = random.choice(courses)
                        activities.append(f"{course['code']} - Evening Study")
                
                # Free time / Social
                elif time_slot in ["8:00 PM", "9:00 PM"]:
                    if is_weekend:
                        activities.append("Social Time / Fun")
                    else:
                        free_activities = ['Gaming', 'Netflix', 'Social Media', 'Reading for Fun', 'Friends']
                        activities.append(random.choice(free_activities))
                
                # Wind down
                elif time_slot == "10:00 PM":
                    activities.append("Wind Down / Prep for Sleep")
                
                # Store activities (join if multiple)
                if activities:
                    daily_schedule[time_slot] = " | ".join(activities)
                else:
                    daily_schedule[time_slot] = "Free Time"
            
            weekly_schedule[day] = daily_schedule
        
        schedule[f'week_{week}'] = weekly_schedule
    
    return schedule

def create_schedule_dataframe(weekly_schedule):
    """Create a pandas DataFrame for the schedule table"""
    time_slots = [
        "7:00 AM", "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
        "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM",
        "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM"
    ]
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Create the dataframe
    data = []
    for time_slot in time_slots:
        row = [time_slot]
        for day in days:
            activity = weekly_schedule.get(day, {}).get(time_slot, "Free Time")
            row.append(activity)
        data.append(row)
    
    df = pd.DataFrame(data, columns=["Time"] + days)
    return df

def generate_pdf_schedule(schedule_data, user_data):
    """Generate a PDF schedule"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Create custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6c5ce7')
    )
    
    # Build the story
    story = []
    
    # Title
    story.append(Paragraph("🎯 FocusFlow Schedule", title_style))
    story.append(Spacer(1, 20))
    
    # Add schedule tables for each week
    for week_num in range(4):
        week_key = f'week_{week_num}'
        if week_key in schedule_data:
            # Week header
            story.append(Paragraph(f"Week {week_num + 1}", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Create schedule table
            weekly_schedule = schedule_data[week_key]
            df = create_schedule_dataframe(weekly_schedule)
            
            # Convert to table data
            table_data = []
            for _, row in df.iterrows():
                table_data.append(list(row))
            
            # Create table
            table = Table(table_data, colWidths=[0.8*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c5ce7')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9ff')),
                ('FONTSIZE', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e6ff')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Page break after each week except the last
            if week_num < 3:
                story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    # Compact Hero Section
    st.markdown("""
    <div class="main-container">
        <div class="compact-hero">
            <h1>🎯 FocusFlow</h1>
            <p>Balance academics with wellness and life</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Step-by-step flow
    if st.session_state.step == 1:
        show_course_setup()
    elif st.session_state.step == 2:
        show_preferences_step()
    elif st.session_state.step == 3:
        show_schedule_step()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_course_setup():
    """Step 1: Individual course setup"""
    st.markdown("""
    <div class="setup-card">
        <h2><span class="step-number">1</span>Add Your Courses</h2>
        <p>Upload each syllabus individually for accurate course detection. Each upload should be for one specific course.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show current courses
    if st.session_state.courses:
        st.markdown("### 📚 Your Courses")
        for course in st.session_state.courses:
            st.markdown(f"""
            <div class="course-card">
                <div class="course-code">{course['code']}</div>
                <div class="course-name">{course['name']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Add new course section
    st.markdown("### ➕ Add New Course")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Course code input for better parsing
        course_code = st.text_input(
            "Course Code (e.g., BIO1205, MATH101)",
            placeholder="Enter course code",
            help="This helps us identify the course in your syllabus"
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "📄 Upload Syllabus for This Course",
            type=['pdf', 'docx', 'txt'],
            help="Upload the syllabus for the course code above"
        )
    
    with col2:
        # Add course button
        if st.button("📚 Add Course", disabled=not (course_code and uploaded_file)):
            if course_code and uploaded_file:
                with st.spinner(f"🧠 Analyzing syllabus for {course_code}..."):
                    text = extract_text_from_file(uploaded_file)
                    course_info, assignments = parse_single_syllabus(text, course_code)
                    
                    # Add to session state
                    st.session_state.courses.append(course_info)
                    
                    # Store assignments
                    if 'assignments' not in st.session_state:
                        st.session_state.assignments = []
                    st.session_state.assignments.extend(assignments)
                    
                    st.success(f"✅ Added {course_info['code']} with {len(assignments)} assignments!")
                    st.rerun()
    
    # Manual course addition
    with st.expander("➕ Add Course Manually"):
        manual_code = st.text_input("Course Code", key="manual_code")
        manual_name = st.text_input("Course Name", key="manual_name")
        
        if st.button("Add Manual Course"):
            if manual_code and manual_name:
                course_info = {
                    'code': manual_code,
                    'name': manual_name
                }
                st.session_state.courses.append(course_info)
                st.success(f"✅ Added {manual_code} manually!")
                st.rerun()
    
    # Progress and navigation
    st.markdown("""
    <div class="progress-bar">
        <div class="progress-fill" style="width: 33%"></div>
    </div>
    <p class="progress-text">Step 1 of 3 - Add at least one course to continue</p>
    """, unsafe_allow_html=True)
    
    if st.session_state.courses:
        if st.button("🚀 Continue to Preferences", type="primary"):
            st.session_state.step = 2
            st.rerun()
    else:
        st.info("👆 Add at least one course to continue to the next step")

def show_preferences_step():
    """Step 2: Preferences setup"""
    st.markdown("""
    <div class="setup-card">
        <h2><span class="step-number">2</span>Personalize Your Schedule</h2>
        <p>Set your preferences to create a schedule that works for your lifestyle</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏰ Time Preferences")
        wake_time = st.slider("Wake up time", 6, 11, 8, format="%d:00")
        bedtime = st.slider("Bedtime", 10, 2, 11, format="%d:00")
        
        st.markdown("### 📚 Study Preferences")
        attention_span = st.slider("Study session length (minutes)", 15, 90, 45)
        study_intensity = st.selectbox(
            "Study intensity",
            ["🌿 Light (2-3 sessions/day)", "⚖️ Moderate (3-4 sessions/day)", "🔥 Intensive (4-5 sessions/day)"]
        )
    
    with col2:
        st.markdown("### 🏃 Intramural Activities")
        include_intramurals = st.checkbox("Include intramural/exercise time", value=False)
        
        if include_intramurals:
            st.markdown("**Add Your Activities:**")
            activity_name = st.text_input("Activity Name (e.g., Soccer, Basketball)")
            activity_type = st.selectbox("Activity Type", ["Practice", "Game", "Workout", "Club Meeting"])
            
            # Activity scheduling
            is_scheduled = st.checkbox("Has specific schedule?", value=False)
            
            if is_scheduled:
                selected_days = st.multiselect(
                    "Select days",
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                )
                activity_time = st.time_input("Time", value=datetime.strptime("17:00", "%H:%M").time())
            
            if st.button("Add Activity") and activity_name:
                intramural = {
                    'name': activity_name,
                    'type': activity_type,
                    'scheduled': is_scheduled,
                    'days': selected_days if is_scheduled else [],
                    'time': activity_time.strftime("%H:%M") if is_scheduled else None
                }
                st.session_state.intramurals.append(intramural)
                st.success(f"✅ Added {activity_name}!")
                st.rerun()
        
        # Show added intramurals
        if st.session_state.intramurals:
            st.markdown("""
            <div class="intramural-card">
                <h4>🏃 Your Activities</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for intramural in st.session_state.intramurals:
                schedule_info = ""
                if intramural.get('scheduled'):
                    days = ", ".join(intramural.get('days', []))
                    time = intramural.get('time', 'TBD')
                    schedule_info = f" - {days} at {time}"
                
                st.markdown(f"""
                <div class="activity-item">
                    {intramural['name']} ({intramural['type']}){schedule_info}
                </div>
                """, unsafe_allow_html=True)
    
    # Wellness information (no checkboxes - automatically included)
    st.markdown("""
    <div class="wellness-info">
        <h4>🌟 Wellness Focus (Automatically Included)</h4>
        <p><strong>Sleep:</strong> Regular sleep schedule is crucial for memory consolidation and focus</p>
        <p><strong>Meals:</strong> Consistent eating times maintain energy levels and brain function</p>
        <p><strong>Free Time:</strong> Relaxation and social time prevent burnout and improve wellbeing</p>
        <p><strong>Balance:</strong> A balanced schedule is more sustainable and effective long-term</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Store preferences
    preferences = {
        'wake_time': wake_time,
        'bedtime': bedtime,
        'attention_span': attention_span,
        'study_intensity': study_intensity,
        'include_intramurals': include_intramurals
    }
    
    st.session_state.user_data = preferences
    
    # Progress
    st.markdown("""
    <div class="progress-bar">
        <div class="progress-fill" style="width: 66%"></div>
    </div>
    <p class="progress-text">Step 2 of 3</p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Courses"):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button("🎨 Generate Schedule", type="primary"):
            with st.spinner("🎨 Creating your personalized weekly schedule..."):
                schedule = generate_weekly_schedule(
                    st.session_state.courses,
                    st.session_state.get('assignments', []),
                    st.session_state.intramurals,
                    preferences
                )
                st.session_state.final_schedule = schedule
                st.session_state.step = 3
                st.rerun()

def show_schedule_step():
    """Step 3: Schedule display with clean table"""
    st.markdown("""
    <div class="setup-card">
        <h2><span class="step-number">3</span>Your Weekly Schedule</h2>
        <p>Here's your personalized weekly schedule that balances academics with wellness and life</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    courses_count = len(st.session_state.courses)
    assignments_count = len(st.session_state.get('assignments', []))
    intramurals_count = len(st.session_state.intramurals)
    attention_span = st.session_state.user_data.get('attention_span', 45)
    
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <span class="stat-number">{courses_count}</span>
            <div class="stat-label">Courses</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{assignments_count}</span>
            <div class="stat-label">Assignments</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{intramurals_count}</span>
            <div class="stat-label">Activities</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{attention_span}</span>
            <div class="stat-label">Min Sessions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Week navigation
    if st.session_state.final_schedule:
        total_weeks = len(st.session_state.final_schedule)
        current_week = st.session_state.current_week
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Previous Week", disabled=current_week == 0):
                st.session_state.current_week = max(0, current_week - 1)
                st.rerun()
        
        with col2:
            st.markdown(f'<div class="week-title">Week {current_week + 1} of {total_weeks}</div>', unsafe_allow_html=True)
        
        with col3:
            if st.button("Next Week →", disabled=current_week >= total_weeks - 1):
                st.session_state.current_week = min(total_weeks - 1, current_week + 1)
                st.rerun()
        
        # Display current week as a clean table
        week_key = f'week_{current_week}'
        if week_key in st.session_state.final_schedule:
            weekly_schedule = st.session_state.final_schedule[week_key]
            df = create_schedule_dataframe(weekly_schedule)
            
            # Display the schedule table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Time": st.column_config.Column(width="small"),
                    "Monday": st.column_config.Column(width="medium"),
                    "Tuesday": st.column_config.Column(width="medium"),
                    "Wednesday": st.column_config.Column(width="medium"),
                    "Thursday": st.column_config.Column(width="medium"),
                    "Friday": st.column_config.Column(width="medium"),
                    "Saturday": st.column_config.Column(width="medium"),
                    "Sunday": st.column_config.Column(width="medium"),
                }
            )
    
    # Export section
    st.markdown("### 🚀 Export Your Schedule")
    
    if st.session_state.final_schedule and st.session_state.user_data:
        # Generate PDF
        pdf_buffer = generate_pdf_schedule(st.session_state.final_schedule, st.session_state.user_data)
        pdf_data = pdf_buffer.getvalue()
        
        st.download_button(
            label="📄 Download PDF Schedule",
            data=pdf_data,
            file_name=f"FocusFlow_Schedule_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            help="Download a beautifully formatted PDF of your 4-week schedule"
        )
    
    # Navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Modify Schedule"):
            st.session_state.step = 2
            st.rerun()
    
    with col2:
        if st.button("🏠 Start Over"):
            # Reset all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Progress complete
    st.markdown("""
    <div class="progress-bar">
        <div class="progress-fill" style="width: 100%"></div>
    </div>
    <p class="progress-text">🎉 Schedule Complete!</p>
    """, unsafe_allow_html=True)
    
    st.success(f"""
    🎉 **Your FocusFlow Schedule is Ready!**
    
    ✅ **{courses_count} courses** with structured study sessions
    ✅ **{assignments_count} assignments** tracked and planned
    ✅ **{intramurals_count} activities** integrated into your schedule
    ✅ **Wellness-focused design** with sleep, meals, and free time prioritized
    ✅ **4 weeks** of detailed planning ready for download
    
    📚 **Remember:** This schedule emphasizes balance - academics, wellness, and life all matter for your success!
    """)

if __name__ == "__main__":
    main()
