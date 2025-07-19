import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import re
from io import BytesIO
import json
import uuid
import random
from collections import defaultdict
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Page config
st.set_page_config(
    page_title="FocusFlow",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS
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
</style>
""", unsafe_allow_html=True)

# Initialize session state with proper defaults
def init_session_state():
    defaults = {
        'step': 1,
        'courses': [],
        'intramurals': [],
        'current_week': 0,
        'user_data': {},
        'schedule_ready': False,
        'final_schedule': None,
        'file_processed': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def generate_time_slots():
    """Generate 30-minute time slots"""
    time_slots = []
    for hour in range(6, 24):  # 6 AM to 11:30 PM
        for minute in [0, 30]:
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

def parse_excel_course_file(file):
    """Simple Excel parser"""
    try:
        excel_data = pd.read_excel(file, sheet_name=None, header=None, nrows=20)
        courses = []
        
        for sheet_name, df in excel_data.items():
            if sheet_name.startswith('Course') and len(courses) < 5:
                course_data = {'assignments': []}
                
                for index in range(min(15, df.shape[0])):
                    try:
                        if index < df.shape[0] and df.shape[1] >= 2:
                            field_val = df.iloc[index, 0]
                            value_val = df.iloc[index, 1]
                            
                            if pd.notna(field_val) and pd.notna(value_val):
                                field = str(field_val).strip()
                                value = str(value_val).strip()
                                
                                if 'Course title' in field:
                                    course_data['name'] = value
                                    # Generate simple code
                                    course_data['code'] = value.upper().replace(' ', '')[:6]
                                elif 'Course Lecture Schedule' in field:
                                    course_data['lecture_schedule'] = value
                                elif 'When in lab' in field:
                                    course_data['lab_schedule'] = value
                    except:
                        continue
                
                if 'name' in course_data:
                    course_data['class_schedule'] = []
                    courses.append(course_data)
        
        return courses
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return []

def show_step_1():
    """Step 1: Course upload"""
    st.markdown("### 📚 Step 1: Course Information")
    
    if not st.session_state.courses:
        uploaded_file = st.file_uploader("Upload Excel course file", type=['xlsx', 'xls'])
        
        if uploaded_file is not None:
            courses = parse_excel_course_file(uploaded_file)
            if courses:
                st.session_state.courses = courses
                st.success(f"✅ Loaded {len(courses)} courses!")
                st.rerun()
        
        if st.button("Add Manual Course"):
            st.session_state.courses.append({
                'name': 'Sample Course',
                'code': 'SAMPLE',
                'class_schedule': []
            })
            st.rerun()
    else:
        st.success(f"📚 {len(st.session_state.courses)} courses loaded")
        for course in st.session_state.courses:
            st.write(f"• {course.get('code', 'Unknown')} - {course.get('name', 'Unknown Course')}")
        
        if st.button("🚀 Continue to Preferences"):
            st.session_state.step = 2
            st.rerun()

def show_step_2():
    """Step 2: Preferences"""
    st.markdown("### ⚙️ Step 2: Your Preferences")
    
    wake_time = st.slider("Wake up time", 6, 11, 8, format="%d:00 AM")
    bedtime_hour = st.slider("Bedtime hour", 9, 2, 10)
    
    preferences = {
        'wake_time': wake_time,
        'bedtime': bedtime_hour
    }
    
    st.session_state.user_data = preferences
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("🎨 Generate Schedule"):
            # Simple schedule generation
            st.session_state.final_schedule = {"Monday": {}, "Tuesday": {}}  # Simplified
            st.session_state.step = 3
            st.rerun()

def show_step_3():
    """Step 3: Schedule display"""
    st.markdown("### 📅 Your Schedule")
    
    if st.session_state.final_schedule:
        st.success("✅ Schedule generated!")
        st.write("Schedule data:", st.session_state.final_schedule)
    
    if st.button("🏠 Start Over"):
        # Clear session state
        for key in ['courses', 'final_schedule', 'user_data']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.step = 1
        st.rerun()

def main():
    # Initialize session state first
    init_session_state()
    
    # Title
    st.markdown('<h1 class="app-title">🎯 FocusFlow</h1>', unsafe_allow_html=True)
    
    # Main container
    with st.container():
        # Step routing
        if st.session_state.step == 1:
            show_step_1()
        elif st.session_state.step == 2:
            show_step_2()
        elif st.session_state.step == 3:
            show_step_3()
        else:
            st.session_state.step = 1
            st.rerun()

if __name__ == "__main__":
    main()
