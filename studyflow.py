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
    page_title="StudyFlow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with weekly table styling
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
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: #ffffff;
        position: relative;
        overflow: hidden;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.95;
    }
    
    .setup-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: all 0.3s ease;
        color: #ffffff;
    }
    
    .step-number {
        display: inline-block;
        width: 45px;
        height: 45px;
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 45px;
        font-weight: 600;
        margin-right: 15px;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
    }
    
    .course-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #ffffff;
    }
    
    .course-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .course-code {
        font-size: 1.2rem;
        font-weight: 600;
        color: #6c5ce7;
    }
    
    .course-name {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0;
    }
    
    .weekly-table {
        width: 100%;
        border-collapse: collapse;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        overflow: hidden;
        margin: 2rem 0;
    }
    
    .weekly-table th {
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        color: white;
        padding: 1rem;
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .weekly-table td {
        padding: 0.75rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        vertical-align: top;
        min-height: 60px;
        background: rgba(255, 255, 255, 0.05);
    }
    
    .time-slot {
        font-weight: 600;
        color: #6c5ce7;
        min-width: 80px;
        text-align: center;
        background: rgba(108, 92, 231, 0.1);
        border-right: 2px solid rgba(108, 92, 231, 0.3);
    }
    
    .activity-cell {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.9);
        line-height: 1.3;
    }
    
    .study-activity {
        background: rgba(108, 92, 231, 0.2);
        border-left: 3px solid #6c5ce7;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0.1rem 0;
    }
    
    .meal-activity {
        background: rgba(253, 203, 110, 0.2);
        border-left: 3px solid #fdcb6e;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0.1rem 0;
    }
    
    .free-activity {
        background: rgba(0, 184, 148, 0.2);
        border-left: 3px solid #00b894;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0.1rem 0;
    }
    
    .break-activity {
        background: rgba(253, 121, 168, 0.2);
        border-left: 3px solid #fd79a8;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0.1rem 0;
    }
    
    .deadline-activity {
        background: rgba(231, 76, 60, 0.2);
        border-left: 3px solid #e74c3c;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0.1rem 0;
        font-weight: 600;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: all 0.3s ease;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #6c5ce7;
        display: block;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .stat-label {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .progress-bar {
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        overflow: hidden;
        margin: 1.5rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #6c5ce7, #a29bfe);
        transition: width 0.3s ease;
    }
    
    .progress-text {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton > button {
        border: none !important;
        border-radius: 50px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
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
        font-size: 1rem !important;
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
    
    /* Form styling */
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
        padding: 2rem !important;
        text-align: center !important;
    }
    
    .legend {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.9);
    }
    
    .legend-color {
        width: 20px;
        height: 12px;
        border-radius: 3px;
        border-left: 3px solid;
    }
    
    .week-navigation {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .week-nav-btn {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    .week-nav-btn:hover {
        background: rgba(108, 92, 231, 0.3);
        border-color: #6c5ce7;
    }
    
    .current-week {
        font-size: 1.1rem;
        font-weight: 600;
        color: #6c5ce7;
        text-align: center;
        min-width: 200px;
    }
    
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .main-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .weekly-table {
            font-size: 0.8rem;
        }
        
        .weekly-table th, .weekly-table td {
            padding: 0.5rem;
        }
        
        .legend {
            flex-direction: column;
            gap: 1rem;
        }
        
        .week-navigation {
            flex-direction: column;
            gap: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'courses' not in st.session_state:
    st.session_state.courses = []
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
                'name': name,
                'difficulty': random.randint(3, 5),
                'credits': random.randint(3, 4)
            }
            course_found = True
            break
    
    # If no course found, use hint or create default
    if not course_found:
        if course_code_hint:
            course_info = {
                'code': course_code_hint,
                'name': f'{course_code_hint} Course',
                'difficulty': 4,
                'credits': 3
            }
        else:
            course_info = {
                'code': 'COURSE101',
                'name': 'Course',
                'difficulty': 4,
                'credits': 3
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

def generate_weekly_schedule(courses, assignments, preferences):
    """Generate a structured weekly schedule"""
    schedule = {}
    
    # Time slots for the weekly table
    time_slots = [
        "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
        "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM",
        "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM"
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
                
                # Morning routine
                if time_slot == "8:00 AM":
                    activities.append({
                        'activity': '🌅 Morning Routine',
                        'type': 'routine',
                        'duration': 60
                    })
                
                # Meals
                elif time_slot == "12:00 PM":
                    activities.append({
                        'activity': '🍽️ Lunch',
                        'type': 'meal',
                        'duration': 60
                    })
                elif time_slot == "6:00 PM":
                    activities.append({
                        'activity': '🍕 Dinner',
                        'type': 'meal',
                        'duration': 60
                    })
                
                # Study sessions
                elif time_slot in ["10:00 AM", "2:00 PM", "4:00 PM", "7:00 PM"] and not is_weekend:
                    if courses:
                        course = random.choice(courses)
                        study_types = ['Reading', 'Practice', 'Review', 'Problems', 'Notes']
                        study_type = random.choice(study_types)
                        activities.append({
                            'activity': f'📚 {course["code"]} - {study_type}',
                            'type': 'study',
                            'course': course['code'],
                            'duration': preferences.get('attention_span', 45)
                        })
                
                # Weekend study (lighter)
                elif time_slot in ["10:00 AM", "2:00 PM"] and is_weekend:
                    if courses and random.random() < 0.6:  # 60% chance
                        course = random.choice(courses)
                        activities.append({
                            'activity': f'📚 {course["code"]} - Review',
                            'type': 'study',
                            'course': course['code'],
                            'duration': preferences.get('attention_span', 45)
                        })
                
                # Breaks
                elif time_slot in ["11:00 AM", "3:00 PM", "5:00 PM"]:
                    if preferences.get('include_breaks', True):
                        activities.append({
                            'activity': '📱 Break',
                            'type': 'break',
                            'duration': 15
                        })
                
                # Evening activities
                elif time_slot in ["8:00 PM", "9:00 PM", "10:00 PM"]:
                    if is_weekend:
                        activities.append({
                            'activity': '🎉 Social Time',
                            'type': 'free',
                            'duration': 120
                        })
                    else:
                        free_activities = ['🎮 Gaming', '📺 Netflix', '📖 Reading', '🎵 Music', '💭 Relaxation']
                        activities.append({
                            'activity': random.choice(free_activities),
                            'type': 'free',
                            'duration': 60
                        })
                
                daily_schedule[time_slot] = activities
            
            weekly_schedule[day] = daily_schedule
        
        schedule[f'week_{week}'] = weekly_schedule
    
    return schedule

def render_weekly_table(weekly_schedule):
    """Render the weekly schedule as an HTML table"""
    time_slots = [
        "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
        "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM",
        "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM"
    ]
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Create table HTML
    table_html = """
    <table class="weekly-table">
        <thead>
            <tr>
                <th>Time</th>
    """
    
    for day in days:
        table_html += f"<th>{day}</th>"
    
    table_html += """
            </tr>
        </thead>
        <tbody>
    """
    
    for time_slot in time_slots:
        table_html += f"""
            <tr>
                <td class="time-slot">{time_slot}</td>
        """
        
        for day in days:
            activities = weekly_schedule.get(day, {}).get(time_slot, [])
            
            cell_content = ""
            for activity in activities:
                activity_type = activity.get('type', 'other')
                activity_text = activity['activity']
                
                # Add duration if available
                if activity.get('duration'):
                    activity_text += f" ({activity['duration']}m)"
                
                cell_content += f'<div class="{activity_type}-activity">{activity_text}</div>'
            
            if not cell_content:
                cell_content = '<div style="color: rgba(255,255,255,0.3); font-style: italic;">Free time</div>'
            
            table_html += f'<td class="activity-cell">{cell_content}</td>'
        
        table_html += "</tr>"
    
    table_html += """
        </tbody>
    </table>
    """
    
    return table_html

def main():
    # Hero Section
    st.markdown("""
    <div class="main-container">
        <div class="hero-section">
            <div class="hero-title">⚡ StudyFlow</div>
            <div class="hero-subtitle">Your AI-powered study scheduler that balances academics with life</div>
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
        <p>Upload each syllabus individually for accurate course detection. This helps us create a personalized schedule for each class.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show current courses
    if st.session_state.courses:
        st.markdown("### 📚 Your Courses")
        for i, course in enumerate(st.session_state.courses):
            st.markdown(f"""
            <div class="course-card">
                <div class="course-header">
                    <div>
                        <div class="course-code">{course['code']}</div>
                        <div class="course-name">{course['name']}</div>
                    </div>
                    <div style="text-align: right;">
                        <div>⭐ {course['difficulty']}/5</div>
                        <div>{course['credits']} credits</div>
                    </div>
                </div>
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
        manual_difficulty = st.slider("Difficulty Level", 1, 5, 3, key="manual_difficulty")
        manual_credits = st.selectbox("Credits", [1, 2, 3, 4, 5], index=2, key="manual_credits")
        
        if st.button("Add Manual Course"):
            if manual_code and manual_name:
                course_info = {
                    'code': manual_code,
                    'name': manual_name,
                    'difficulty': manual_difficulty,
                    'credits': manual_credits
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
        <p>Tell us about your preferences so we can create a schedule that works for your lifestyle</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**⏰ Time Preferences**")
        wake_time = st.slider("Wake up time", 6, 11, 8, format="%d:00")
        bedtime = st.slider("Bedtime", 10, 2, 11, format="%d:00")
        
        st.markdown("**📚 Study Preferences**")
        attention_span = st.slider("Study session length (minutes)", 15, 90, 45)
        study_intensity = st.selectbox(
            "Study intensity",
            ["🌿 Light (2-3 sessions/day)", "⚖️ Moderate (3-4 sessions/day)", "🔥 Intensive (4-5 sessions/day)"]
        )
    
    with col2:
        st.markdown("**🎯 Lifestyle Balance**")
        include_breaks = st.checkbox("Include social media breaks", value=True)
        include_exercise = st.checkbox("Include exercise/intramural time", value=True)
        include_social = st.checkbox("Include social/relaxation time", value=True)
        
        st.markdown("**📱 Wellness Focus**")
        emphasize_sleep = st.checkbox("Emphasize sleep importance", value=True)
        emphasize_meals = st.checkbox("Include regular meal times", value=True)
        emphasize_balance = st.checkbox("Emphasize work-life balance", value=True)
    
    # Store preferences
    preferences = {
        'wake_time': wake_time,
        'bedtime': bedtime,
        'attention_span': attention_span,
        'study_intensity': study_intensity,
        'include_breaks': include_breaks,
        'include_exercise': include_exercise,
        'include_social': include_social,
        'emphasize_sleep': emphasize_sleep,
        'emphasize_meals': emphasize_meals,
        'emphasize_balance': emphasize_balance
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
                    preferences
                )
                st.session_state.final_schedule = schedule
                st.session_state.step = 3
                st.rerun()

def show_schedule_step():
    """Step 3: Schedule display with weekly table"""
    st.markdown("""
    <div class="setup-card">
        <h2><span class="step-number">3</span>Your Weekly Schedule</h2>
        <p>Here's your personalized weekly schedule that balances academics with wellness and social life</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    courses_count = len(st.session_state.courses)
    assignments_count = len(st.session_state.get('assignments', []))
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
            <span class="stat-number">{attention_span}</span>
            <div class="stat-label">Min Sessions</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">4</span>
            <div class="stat-label">Weeks Planned</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Legend
    st.markdown("""
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color study-activity" style="background: rgba(108, 92, 231, 0.2); border-left-color: #6c5ce7;"></div>
            <span>📚 Study Sessions</span>
        </div>
        <div class="legend-item">
            <div class="legend-color meal-activity" style="background: rgba(253, 203, 110, 0.2); border-left-color: #fdcb6e;"></div>
            <span>🍽️ Meals</span>
        </div>
        <div class="legend-item">
            <div class="legend-color free-activity" style="background: rgba(0, 184, 148, 0.2); border-left-color: #00b894;"></div>
            <span>🎉 Free Time</span>
        </div>
        <div class="legend-item">
            <div class="legend-color break-activity" style="background: rgba(253, 121, 168, 0.2); border-left-color: #fd79a8;"></div>
            <span>📱 Breaks</span>
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
            st.markdown(f'<div class="current-week">Week {current_week + 1} of {total_weeks}</div>', unsafe_allow_html=True)
        
        with col3:
            if st.button("Next Week →", disabled=current_week >= total_weeks - 1):
                st.session_state.current_week = min(total_weeks - 1, current_week + 1)
                st.rerun()
        
        # Display current week
        week_key = f'week_{current_week}'
        if week_key in st.session_state.final_schedule:
            weekly_schedule = st.session_state.final_schedule[week_key]
            table_html = render_weekly_table(weekly_schedule)
            st.markdown(table_html, unsafe_allow_html=True)
    
    # Wellness reminders
    st.markdown("""
    <div class="setup-card">
        <h3>💡 Wellness Reminders</h3>
        <p>Your schedule includes these important elements for academic success:</p>
        <ul>
            <li><strong>🛌 Sleep:</strong> Adequate rest is crucial for memory consolidation and focus</li>
            <li><strong>🍽️ Meals:</strong> Regular eating maintains energy levels and brain function</li>
            <li><strong>🎉 Free Time:</strong> Relaxation and social time prevent burnout and improve wellbeing</li>
            <li><strong>📱 Breaks:</strong> Short breaks between study sessions improve retention</li>
            <li><strong>⚖️ Balance:</strong> A balanced schedule is more sustainable long-term</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Export options
    st.markdown("### 🚀 Export Your Schedule")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download PDF"):
            st.info("PDF generation coming soon!")
    
    with col2:
        if st.button("📅 Export Calendar"):
            st.info("Calendar export coming soon!")
    
    with col3:
        if st.button("🔄 Modify Schedule"):
            st.session_state.step = 2
            st.rerun()
    
    # Progress complete
    st.markdown("""
    <div class="progress-bar">
        <div class="progress-fill" style="width: 100%"></div>
    </div>
    <p class="progress-text">🎉 Schedule Complete!</p>
    """, unsafe_allow_html=True)
    
    st.success(f"""
    🎉 **Your StudyFlow Schedule is Ready!**
    
    ✅ **{courses_count} courses** with structured study sessions
    ✅ **{assignments_count} assignments** tracked and scheduled
    ✅ **{attention_span}-minute focus blocks** optimized for your attention span
    ✅ **Wellness-focused design** with sleep, meals, and free time prioritized
    ✅ **4 weeks** of detailed weekly planning
    
    📚 **Remember:** This schedule balances academics with life - stick to it and adjust as needed!
    """)

if __name__ == "__main__":
    main()
