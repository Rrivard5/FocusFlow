import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import re
# Removed openpyxl - using pandas instead
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

# Enhanced CSS with color coding and 30-minute increments
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
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .app-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #6c5ce7;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
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
        margin-bottom: 0.75rem;
    }
    
    .class-schedule {
        background: rgba(108, 92, 231, 0.1);
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 3px solid #6c5ce7;
    }
    
    .class-schedule-item {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
        margin: 0.25rem 0;
    }
    
    .intramural-card {
        background: rgba(230, 126, 34, 0.1);
        border: 1px solid rgba(230, 126, 34, 0.3);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    
    .intramural-card h4 {
        color: #e67e22;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    
    .activity-item {
        background: rgba(230, 126, 34, 0.15);
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 3px solid #e67e22;
        color: #ffffff;
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
        gap: 1rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.8);
        background: rgba(255, 255, 255, 0.05);
        padding: 0.5rem 0.75rem;
        border-radius: 20px;
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
    
    /* Form styling */
    .stSelectbox label, .stTextInput label, .stSlider label, .stTimeInput label {
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
        .app-title {
            font-size: 1.6rem;
        }
        
        .main-container {
            margin: 0.25rem;
            padding: 1rem;
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

def parse_time_string(time_str):
    """Parse time string like '10:40-11:30am' or 'M,W,F 10:40-11:30am'"""
    if not time_str or str(time_str).lower() == 'n/a':
        return None
    
    # Remove days from the string if present
    time_part = time_str
    if any(day in time_str.upper() for day in ['M', 'T', 'W', 'R', 'F', 'S']):
        parts = time_str.split(' ')
        if len(parts) > 1:
            time_part = parts[1]
    
    # Extract time range
    time_match = re.search(r'(\d{1,2}:\d{2})-(\d{1,2}:\d{2})', time_part)
    if time_match:
        start_time = time_match.group(1)
        end_time = time_match.group(2)
        
        # Add AM/PM if not present
        if 'am' in time_part.lower() or 'pm' in time_part.lower():
            period = 'AM' if 'am' in time_part.lower() else 'PM'
            if ':' in start_time and 'M' not in start_time:
                start_time += f' {period}'
            if ':' in end_time and 'M' not in end_time:
                end_time += f' {period}'
        
        return start_time, end_time
    
    return None

def parse_days_string(schedule_str):
    """Parse days from string like 'M,W,F 10:40-11:30am'"""
    if not schedule_str or str(schedule_str).lower() == 'n/a':
        return []
    
    days_map = {
        'M': 'Monday',
        'T': 'Tuesday', 
        'W': 'Wednesday',
        'R': 'Thursday',
        'F': 'Friday',
        'S': 'Saturday',
        'U': 'Sunday'
    }
    
    days = []
    for abbr, full_name in days_map.items():
        if abbr in schedule_str.upper():
            days.append(full_name)
    
    return days

def parse_excel_course_file(file):
    """Parse the Excel file with the specified format using pandas"""
    try:
        # Read all sheets from the Excel file
        excel_data = pd.read_excel(file, sheet_name=None, header=None)
        courses = []
        
        # Process each sheet (each course)
        for sheet_name, df in excel_data.items():
            if sheet_name.startswith('Course'):
                course_data = {}
                assignments = []
                
                # Read course information (first 20 rows, first 2 columns)
                for index, row in df.iloc[:20, :2].iterrows():
                    if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                        field = str(row.iloc[0]).strip()
                        value = str(row.iloc[1]).strip()
                        
                        if 'Course title' in field:
                            course_data['name'] = value
                        elif 'Course Lecture Schedule' in field:
                            course_data['lecture_schedule'] = value
                        elif 'Lecture location' in field:
                            course_data['lecture_location'] = value
                        elif 'When in lab' in field:
                            course_data['lab_schedule'] = value
                        elif 'Where is lab' in field:
                            course_data['lab_location'] = value
                        elif 'When is recitation' in field:
                            course_data['recitation_schedule'] = value
                        elif 'Where is recitation' in field:
                            course_data['recitation_location'] = value
                        elif 'Suggested daily study time' in field:
                            course_data['daily_study_time'] = value
                
                # Generate course code from name if not provided
                if 'name' in course_data:
                    # Try to extract course code from name
                    code_match = re.search(r'([A-Z]{2,4})\s*(\d{3,4})', course_data['name'].upper())
                    if code_match:
                        course_data['code'] = f"{code_match.group(1)}{code_match.group(2)}"
                    else:
                        # Create code from name
                        name_parts = course_data['name'].split()
                        if len(name_parts) >= 2:
                            course_data['code'] = f"{name_parts[0][:3]}{name_parts[1][:3]}".upper()
                        else:
                            course_data['code'] = course_data['name'].replace(' ', '')[:6].upper()
                
                # Parse class schedules
                class_schedule = []
                
                # Lecture schedule
                if 'lecture_schedule' in course_data and course_data['lecture_schedule'].lower() != 'n/a':
                    days = parse_days_string(course_data['lecture_schedule'])
                    times = parse_time_string(course_data['lecture_schedule'])
                    if days and times:
                        class_schedule.append({
                            'days': days,
                            'start_time': times[0],
                            'end_time': times[1],
                            'type': 'Lecture',
                            'location': course_data.get('lecture_location', '')
                        })
                
                # Lab schedule
                if 'lab_schedule' in course_data and course_data['lab_schedule'].lower() != 'n/a':
                    days = parse_days_string(course_data['lab_schedule'])
                    times = parse_time_string(course_data['lab_schedule'])
                    if days and times:
                        class_schedule.append({
                            'days': days,
                            'start_time': times[0],
                            'end_time': times[1],
                            'type': 'Lab',
                            'location': course_data.get('lab_location', '')
                        })
                
                # Recitation schedule
                if 'recitation_schedule' in course_data and course_data['recitation_schedule'].lower() != 'n/a':
                    days = parse_days_string(course_data['recitation_schedule'])
                    times = parse_time_string(course_data['recitation_schedule'])
                    if days and times:
                        class_schedule.append({
                            'days': days,
                            'start_time': times[0],
                            'end_time': times[1],
                            'type': 'Recitation',
                            'location': course_data.get('recitation_location', '')
                        })
                
                course_data['class_schedule'] = class_schedule
                
                # Read assignments (look for rows with "Large Assignment" or "Exam" in rows 15-30)
                for index, row in df.iloc[14:30, :3].iterrows():
                    if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                        assignment_name = str(row.iloc[0]).strip()
                        assignment_type = str(row.iloc[1]).strip()
                        due_date = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
                        
                        if 'Large Assignment' in assignment_name or 'Exam' in assignment_type:
                            assignments.append({
                                'id': str(uuid.uuid4()),
                                'title': assignment_type,
                                'date': due_date,
                                'type': 'exam' if 'Exam' in assignment_type else 'assignment',
                                'course': course_data.get('code', 'UNKNOWN'),
                                'priority': 'high' if 'Exam' in assignment_type else 'medium'
                            })
                
                course_data['assignments'] = assignments
                courses.append(course_data)
        
        return courses
    
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return []

def generate_time_slots():
    """Generate 30-minute time slots"""
    time_slots = []
    for hour in range(6, 24):  # 6 AM to 11:30 PM
        for minute in [0, 30]:
            time_obj = time(hour, minute)
            if hour == 0:
                time_str = f"12:{minute:02d} AM"
            elif hour < 12:
                time_str = f"{hour}:{minute:02d} AM"
            elif hour == 12:
                time_str = f"12:{minute:02d} PM"
            else:
                time_str = f"{hour-12}:{minute:02d} PM"
            time_slots.append(time_str)
    return time_slots

def time_to_slot_index(time_str):
    """Convert time string to slot index"""
    time_slots = generate_time_slots()
    try:
        return time_slots.index(time_str)
    except ValueError:
        # Try to find closest match
        for i, slot in enumerate(time_slots):
            if time_str in slot:
                return i
        return 0

def generate_weekly_schedule(courses, intramurals, preferences):
    """Generate a structured weekly schedule with 30-minute increments"""
    schedule = {}
    time_slots = generate_time_slots()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Generate 4 weeks of schedule
    for week in range(4):
        weekly_schedule = {}
        
        for day in days:
            daily_schedule = {}
            is_weekend = day in ["Saturday", "Sunday"]
            
            # Initialize all slots as free
            for time_slot in time_slots:
                daily_schedule[time_slot] = {"activity": "Free Time", "type": "free"}
            
            # Add sleep schedule
            wake_time = preferences.get('wake_time', 8)
            bedtime = preferences.get('bedtime', 11)
            
            # Fill sleep times
            for time_slot in time_slots:
                hour = int(time_slot.split(':')[0])
                is_pm = 'PM' in time_slot
                is_am = 'AM' in time_slot
                
                if is_pm and hour != 12:
                    hour += 12
                elif is_am and hour == 12:
                    hour = 0
                
                # Sleep from bedtime to wake time
                if (bedtime >= 22 and hour >= bedtime) or (hour < wake_time):
                    daily_schedule[time_slot] = {"activity": "Sleep", "type": "sleep"}
            
            # Add class times from Excel data
            for course in courses:
                if 'class_schedule' in course:
                    for class_time in course['class_schedule']:
                        if day in class_time['days']:
                            start_time = class_time['start_time']
                            end_time = class_time['end_time']
                            class_type = class_time['type']
                            location = class_time.get('location', '')
                            
                            # Convert times and fill schedule
                            try:
                                # Parse start and end times
                                start_hour = int(start_time.split(':')[0])
                                start_min = int(start_time.split(':')[1].split()[0])
                                if 'PM' in start_time and start_hour != 12:
                                    start_hour += 12
                                elif 'AM' in start_time and start_hour == 12:
                                    start_hour = 0
                                
                                end_hour = int(end_time.split(':')[0])
                                end_min = int(end_time.split(':')[1].split()[0])
                                if 'PM' in end_time and end_hour != 12:
                                    end_hour += 12
                                elif 'AM' in end_time and end_hour == 12:
                                    end_hour = 0
                                
                                # Find corresponding time slots
                                for time_slot in time_slots:
                                    slot_hour = int(time_slot.split(':')[0])
                                    slot_min = int(time_slot.split(':')[1].split()[0])
                                    if 'PM' in time_slot and slot_hour != 12:
                                        slot_hour += 12
                                    elif 'AM' in time_slot and slot_hour == 12:
                                        slot_hour = 0
                                    
                                    slot_time = slot_hour * 60 + slot_min
                                    start_time_min = start_hour * 60 + start_min
                                    end_time_min = end_hour * 60 + end_min
                                    
                                    if start_time_min <= slot_time < end_time_min:
                                        activity_name = f"{course['code']} - {class_type}"
                                        if location:
                                            activity_name += f" ({location})"
                                        daily_schedule[time_slot] = {
                                            "activity": activity_name,
                                            "type": "class"
                                        }
                            except:
                                continue
            
            # Add intramural activities
            for intramural in intramurals:
                if intramural.get('scheduled') and day in intramural.get('days', []):
                    start_time = intramural.get('start_time', '5:00 PM')
                    duration = intramural.get('duration', 90)  # minutes
                    
                    try:
                        start_slot = time_to_slot_index(start_time)
                        slots_needed = duration // 30
                        
                        for i in range(start_slot, min(start_slot + slots_needed, len(time_slots))):
                            if i < len(time_slots):
                                daily_schedule[time_slots[i]] = {
                                    "activity": f"{intramural['name']} - {intramural['type']}",
                                    "type": "activity"
                                }
                    except:
                        continue
            
            # Add meals
            meal_times = {
                "8:00 AM": "Breakfast",
                "12:00 PM": "Lunch", 
                "6:00 PM": "Dinner"
            }
            
            for meal_time, meal_name in meal_times.items():
                if meal_time in daily_schedule:
                    daily_schedule[meal_time] = {"activity": meal_name, "type": "meal"}
            
            # Add study sessions based on course recommendations
            if not is_weekend:
                study_times = ["10:00 AM", "2:00 PM", "4:00 PM", "7:00 PM"]
            else:
                study_times = ["10:00 AM", "2:00 PM"]
            
            for study_time in study_times:
                if study_time in daily_schedule and daily_schedule[study_time]["type"] == "free":
                    if courses:
                        course = random.choice(courses)
                        study_types = ['Reading', 'Practice', 'Review', 'Homework']
                        study_type = random.choice(study_types)
                        daily_schedule[study_time] = {
                            "activity": f"{course['code']} - {study_type}",
                            "type": "study"
                        }
            
            # Add breaks
            break_times = ["10:30 AM", "3:30 PM"]
            for break_time in break_times:
                if break_time in daily_schedule and daily_schedule[break_time]["type"] == "free":
                    daily_schedule[break_time] = {"activity": "Break/Walk", "type": "break"}
            
            weekly_schedule[day] = daily_schedule
        
        schedule[f'week_{week}'] = weekly_schedule
    
    return schedule

def create_schedule_dataframe(weekly_schedule):
    """Create a pandas DataFrame for the schedule table"""
    time_slots = generate_time_slots()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Create the dataframe
    data = []
    for time_slot in time_slots:
        row = [time_slot]
        for day in days:
            slot_data = weekly_schedule.get(day, {}).get(time_slot, {"activity": "Free Time", "type": "free"})
            activity = slot_data["activity"]
            row.append(activity)
        data.append(row)
    
    df = pd.DataFrame(data, columns=["Time"] + days)
    return df

def style_schedule_dataframe(df, weekly_schedule):
    """Apply color coding to the schedule dataframe"""
    def color_cell(val):
        # Get the type from the weekly schedule
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            for time_slot in weekly_schedule.get(day, {}):
                slot_data = weekly_schedule[day][time_slot]
                if slot_data["activity"] == val:
                    activity_type = slot_data["type"]
                    if activity_type == "class":
                        return "background-color: #3742fa; color: white; font-weight: bold;"
                    elif activity_type == "study":
                        return "background-color: #5f27cd; color: white; font-weight: bold;"
                    elif activity_type == "meal":
                        return "background-color: #ff9f43; color: white; font-weight: bold;"
                    elif activity_type == "activity":
                        return "background-color: #e67e22; color: white; font-weight: bold;"
                    elif activity_type == "sleep":
                        return "background-color: #2f3542; color: white; font-weight: bold;"
                    elif activity_type == "break":
                        return "background-color: #ff6b6b; color: white; font-weight: bold;"
                    elif activity_type == "free":
                        return "background-color: #00d2d3; color: white; font-weight: bold;"
        return "background-color: #00d2d3; color: white; font-weight: bold;"  # Default to free time
    
    return df.style.applymap(color_cell, subset=df.columns[1:])

def generate_pdf_schedule(schedule_data, user_data):
    """Generate a PDF schedule with wellness reminders"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # Create custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6c5ce7')
    )
    
    wellness_style = ParagraphStyle(
        'Wellness',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.HexColor('#2f3542'),
        leftIndent=20
    )
    
    # Build the story
    story = []
    
    # Compact title
    story.append(Paragraph("🎯 FocusFlow Schedule", title_style))
    story.append(Spacer(1, 12))
    
    # Wellness reminder at the top
    story.append(Paragraph("📋 Important Reminders", styles['Heading2']))
    story.append(Paragraph("• <b>Sleep is crucial:</b> This schedule prioritizes 7-9 hours of sleep for optimal learning and memory consolidation.", wellness_style))
    story.append(Paragraph("• <b>Sample schedule:</b> This is one possible arrangement. Adjust times and activities based on your needs and preferences.", wellness_style))
    story.append(Paragraph("• <b>Flexibility matters:</b> Use 'buffer time' between classes for walking, transitions, or short breaks.", wellness_style))
    story.append(Paragraph("• <b>Balance is key:</b> Notice how study time is balanced with meals, exercise, and relaxation.", wellness_style))
    story.append(Spacer(1, 16))
    
    # Add schedule tables for each week
    for week_num in range(4):
        week_key = f'week_{week_num}'
        if week_key in schedule_data:
            # Week header
            story.append(Paragraph(f"Week {week_num + 1}", styles['Heading3']))
            story.append(Spacer(1, 8))
            
            # Create schedule table
            weekly_schedule = schedule_data[week_key]
            df = create_schedule_dataframe(weekly_schedule)
            
            # Convert to table data (show only key times to save space)
            key_times = ["7:00 AM", "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", 
                        "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM",
                        "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM", "11:00 PM"]
            
            table_data = []
            for _, row in df.iterrows():
                if row['Time'] in key_times:
                    table_data.append(list(row))
            
            # Create table
            table = Table(table_data, colWidths=[0.8*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.85*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c5ce7')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),
                ('FONTSIZE', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9ff')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e6ff')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9ff'), colors.HexColor('#ffffff')])
            ]))
            
            story.append(table)
            story.append(Spacer(1, 12))
            
            # Page break after each week except the last
            if week_num < 3:
                story.append(PageBreak())
    
    # Footer with color legend
    story.append(Spacer(1, 12))
    story.append(Paragraph("🎨 Color Guide", styles['Heading3']))
    story.append(Paragraph("Classes: Blue | Study: Purple | Meals: Orange | Activities: Brown | Sleep: Dark Gray | Breaks: Red | Free Time: Teal", wellness_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    # Simple title
    st.markdown('<h1 class="app-title">🎯 FocusFlow</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Step-by-step flow
    if st.session_state.step == 1:
        show_excel_upload()
    elif st.session_state.step == 2:
        show_preferences_step()
    elif st.session_state.step == 3:
        show_schedule_step()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_excel_upload():
    """Step 1: Excel file upload and processing"""
    st.markdown("""
    <div class="setup-card">
        <h2><span class="step-number">1</span>Upload Your Course Template</h2>
        <p>Upload the Excel file with your course information, class schedules, and assignments.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show current courses if any
    if st.session_state.courses:
        st.markdown("### 📚 Your Courses")
        for course in st.session_state.courses:
            st.markdown(f"""
            <div class="course-card">
                <div class="course-code">{course.get('code', 'Unknown')}</div>
                <div class="course-name">{course.get('name', 'Unknown Course')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show class schedule
            if 'class_schedule' in course and course['class_schedule']:
                st.markdown(f"**Class Schedule for {course.get('code', 'Unknown')}:**")
                for class_time in course['class_schedule']:
                    days_str = ", ".join(class_time['days'])
                    location = f" - {class_time['location']}" if class_time.get('location') else ""
                    st.markdown(f"""
                    <div class="class-schedule">
                        <div class="class-schedule-item">{class_time['type']}: {days_str}, {class_time['start_time']} - {class_time['end_time']}{location}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # File upload section
    st.markdown("### 📄 Upload Course Template")
    
    # Instructions
    st.info("""
    **Template Format Requirements:**
    - Excel file with separate tabs for each course (Course 1, Course 2, etc.)
    - Each tab should contain course information, class schedules, and assignment details
    - Use the format: Course title, lecture schedule, lab schedule, assignments, etc.
    """)
    
    uploaded_file = st.file_uploader(
        "Choose Excel file",
        type=['xlsx', 'xls'],
        help="Upload your course template Excel file"
    )
    
    if uploaded_file is not None:
        with st.spinner("🧠 Processing your course template..."):
            courses = parse_excel_course_file(uploaded_file)
            
            if courses:
                st.session_state.courses = courses
                
                # Create assignments list
                all_assignments = []
                for course in courses:
                    all_assignments.extend(course.get('assignments', []))
                st.session_state.assignments = all_assignments
                
                st.success(f"✅ Successfully loaded {len(courses)} courses with {len(all_assignments)} assignments!")
                st.rerun()
            else:
                st.error("❌ Could not read course data from the file. Please check the format.")
    
    # Progress and navigation
    st.markdown("""
    <div class="progress-bar">
        <div class="progress-fill" style="width: 33%"></div>
    </div>
    <p class="progress-text">Step 1 of 3 - Upload your course template to continue</p>
    """, unsafe_allow_html=True)
    
    if st.session_state.courses:
        if st.button("🚀 Continue to Preferences", type="primary"):
            st.session_state.step = 2
            st.rerun()
    else:
        st.info("👆 Upload your course template Excel file to continue")

def show_preferences_step():
    """Step 2: Preferences setup"""
    st.markdown("""
    <div class="setup-card">
        <h2><span class="step-number">2</span>Personalize Your Schedule</h2>
        <p>Set your preferences to create a balanced schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏰ Time Preferences")
        wake_time = st.slider("Wake up time", 6, 11, 8, format="%d:00 AM")
        
        # Bedtime with AM/PM
        bedtime_hour = st.slider("Bedtime hour", 9, 2, 11)
        if bedtime_hour >= 9:
            bedtime_display = f"{bedtime_hour}:00 PM"
        else:
            bedtime_display = f"{bedtime_hour}:00 AM"
        
        st.write(f"**Bedtime: {bedtime_display}**")
        
        st.markdown("### 📚 Study Preferences")
        study_intensity = st.selectbox(
            "Study intensity",
            ["🌿 Light (2-3 sessions/day)", "⚖️ Moderate (3-4 sessions/day)", "🔥 Intensive (4-5 sessions/day)"]
        )
    
    with col2:
        st.markdown("### 🏃 Intramural Activities")
        include_intramurals = st.checkbox("Include intramural/exercise time", value=False)
        
        if include_intramurals:
            st.markdown("**Add Your Activities:**")
            activity_name = st.text_input("Activity Name (e.g., Soccer, Basketball)", key="activity_name")
            activity_type = st.selectbox("Activity Type", ["Practice", "Game", "Workout", "Club Meeting"], key="activity_type")
            
            # Activity scheduling
            is_scheduled = st.checkbox("Has specific schedule?", value=False, key="is_scheduled")
            
            if is_scheduled:
                selected_days = st.multiselect(
                    "Select days",
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    key="selected_days"
                )
                activity_start_time = st.time_input("Start Time", value=time(17, 0), key="activity_start_time")
                activity_duration = st.slider("Duration (minutes)", 30, 180, 90, key="activity_duration")
                
                st.write(f"**Schedule: {', '.join(selected_days)} at {activity_start_time.strftime('%I:%M %p')} for {activity_duration} minutes**")
            
            if st.button("Add Activity", key="add_activity") and activity_name:
                intramural = {
                    'name': activity_name,
                    'type': activity_type,
                    'scheduled': is_scheduled,
                    'days': selected_days if is_scheduled else [],
                    'start_time': activity_start_time.strftime('%I:%M %p') if is_scheduled else None,
                    'duration': activity_duration if is_scheduled else 60
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
                    start_time = intramural.get('start_time', 'TBD')
                    duration = intramural.get('duration', 60)
                    schedule_info = f" - {days} at {start_time} ({duration} min)"
                
                st.markdown(f"""
                <div class="activity-item">
                    <strong>{intramural['name']}</strong> ({intramural['type']}){schedule_info}
                </div>
                """, unsafe_allow_html=True)
    
    # Wellness information
    st.markdown("""
    <div class="wellness-info">
        <h4>🌟 Wellness Focus (Automatically Included)</h4>
        <p><strong>Sleep:</strong> 7-9 hours prioritized for memory consolidation and focus</p>
        <p><strong>Meals:</strong> Regular eating times maintain energy and brain function</p>
        <p><strong>Free Time:</strong> Social time and relaxation prevent burnout</p>
        <p><strong>Balance:</strong> Sustainable schedule for long-term success</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Store preferences
    preferences = {
        'wake_time': wake_time,
        'bedtime': bedtime_hour,
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
        if st.button("← Back to Upload"):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button("🎨 Generate Schedule", type="primary"):
            with st.spinner("🎨 Creating your personalized schedule..."):
                schedule = generate_weekly_schedule(
                    st.session_state.courses,
                    st.session_state.intramurals,
                    preferences
                )
                st.session_state.final_schedule = schedule
                st.session_state.step = 3
                st.rerun()

def show_schedule_step():
    """Step 3: Schedule display with color-coded table"""
    st.markdown("""
    <div class="setup-card">
        <h2><span class="step-number">3</span>Your Color-Coded Schedule</h2>
        <p>30-minute increments with your actual class times and balanced wellness</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    courses_count = len(st.session_state.courses)
    assignments_count = len(st.session_state.get('assignments', []))
    intramurals_count = len(st.session_state.intramurals)
    
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
            <span class="stat-number">4</span>
            <div class="stat-label">Weeks</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Color legend
    st.markdown("""
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: #3742fa;"></div>
            <span>📚 Classes</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #5f27cd;"></div>
            <span>📖 Study</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #ff9f43;"></div>
            <span>🍽️ Meals</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #e67e22;"></div>
            <span>🏃 Activities</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #2f3542;"></div>
            <span>😴 Sleep</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #ff6b6b;"></div>
            <span>☕ Breaks</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #00d2d3;"></div>
            <span>🎉 Free Time</span>
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
        
        # Display current week
        week_key = f'week_{current_week}'
        if week_key in st.session_state.final_schedule:
            weekly_schedule = st.session_state.final_schedule[week_key]
            df = create_schedule_dataframe(weekly_schedule)
            styled_df = style_schedule_dataframe(df, weekly_schedule)
            
            # Display the schedule table
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                height=800
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
            help="Download your complete 4-week schedule with wellness reminders"
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
    
    ✅ **{courses_count} courses** with actual class times from your Excel template
    ✅ **{assignments_count} assignments** with deadline tracking
    ✅ **{intramurals_count} activities** scheduled with proper duration
    ✅ **30-minute increments** for precise time management
    ✅ **Color-coded activities** for easy visual scanning
    ✅ **Wellness-focused design** with sleep, meals, and balance prioritized
    
    📚 **Remember:** This is a sample schedule to get you started. Adjust times and activities to fit your specific needs!
    """)

if __name__ == "__main__":
    main()
