# -*- coding: utf-8 -*-
# history.py
import os
import csv
from datetime import datetime, timedelta

STATS_FILE = "zenify_log.csv"
FIELDNAMES = [
    "timestamp", "start_time", "end_time", "mode", "preset", "shape_type", 
    "duration_sec", "cycles", "completion_rate", "interruptions", 
    "pause_count", "time_of_day", "day_of_week", "quality_score"
]

def get_time_of_day(dt):
    """Determine time of day category"""
    hour = dt.hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"  
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

def get_day_of_week_name(dt):
    """Get day of week name in Chinese"""
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return days[dt.weekday()]

def calculate_completion_rate(actual_duration, planned_duration):
    """Calculate how much of the planned session was completed"""
    if planned_duration <= 0:
        return 0
    return min(1.0, actual_duration / planned_duration)

def add_session(session_data):
    """Appends a new session record to the CSV log."""
    is_new_file = not os.path.exists(STATS_FILE)
    try:
        with open(STATS_FILE, "a", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if is_new_file:
                writer.writeheader()
            writer.writerow(session_data)
    except IOError:
        pass # Fail silently

def _standardize_data_field(field_value, field_type):
    """Standardize multilingual field values to English keys"""
    if not field_value:
        return field_value
        
    # Mode standardization
    if field_type == 'mode':
        mode_map = {
            "图形模式": "graphical_mode",
            "グラフィカルモード": "graphical_mode", 
            "Graphical Mode": "graphical_mode",
            "进度条模式": "progress_bar_mode",
            "プログレスバーモード": "progress_bar_mode",
            "Progress Bar Mode": "progress_bar_mode"
        }
        return mode_map.get(field_value, field_value)
    
    # Preset standardization  
    elif field_type == 'preset':
        preset_map = {
            "4-7-8呼吸 (放松)": "4-7-8 Breathing (Relaxation)",
            "4-7-8呼吸法 (リラックス)": "4-7-8 Breathing (Relaxation)", 
            "盒子呼吸 (专注)": "Box Breathing (Focus)",
            "ボックス呼吸 (集中)": "Box Breathing (Focus)",
            "自定义": "Custom",
            "カスタム": "Custom"
        }
        return preset_map.get(field_value, field_value)
    
    # Shape type standardization
    elif field_type == 'shape_type':
        shape_map = {
            "莲花": "lotus",
            "蓮花": "lotus", 
            "ロータス": "lotus",
            "曼陀罗": "mandala",
            "マンダラ": "mandala",
            "太阳": "sun", 
            "太陽": "sun",
            "サン": "sun",
            "心形": "heart",
            "ハート": "heart", 
            "花朵": "flower",
            "フラワー": "flower",
            "禅圆": "zen_circle",
            "禅円": "zen_circle",
            "ゼンサークル": "zen_circle",
            "未知": "unknown",
            "不明": "unknown",
            "未知数": "unknown"
        }
        return shape_map.get(field_value, field_value)
    
    # Day of week standardization
    elif field_type == 'day_of_week':
        dow_map = {
            "周一": "monday", "周二": "tuesday", "周三": "wednesday", 
            "周四": "thursday", "周五": "friday", "周六": "saturday", "周日": "sunday",
            "月": "monday", "火": "tuesday", "水": "wednesday", 
            "木": "thursday", "金": "friday", "土": "saturday", "日": "sunday",
            "Monday": "monday", "Tuesday": "tuesday", "Wednesday": "wednesday",
            "Thursday": "thursday", "Friday": "friday", "Saturday": "saturday", "Sunday": "sunday"
        }
        return dow_map.get(field_value, field_value)
    
    return field_value

def get_stats():
    """Reads the log and computes rich statistics."""
    if not os.path.exists(STATS_FILE):
        return _get_empty_stats()

    sessions = []
    try:
        with open(STATS_FILE, "r") as f:
            lines = f.readlines()
            if not lines:
                return _get_empty_stats()
            
            # Check if file has proper CSV header
            first_line = lines[0].strip()
            if 'timestamp' not in first_line.lower():
                # File is corrupted, recreate with proper header
                _recreate_csv_file()
                return _get_empty_stats()
            
            # Read with CSV reader
            f.seek(0)
            reader = csv.DictReader(f)
            for row in reader:
                # Skip rows without required fields
                if 'timestamp' in row and row['timestamp']:
                    # Standardize all multilingual fields
                    standardized_row = dict(row)
                    standardized_row['mode'] = _standardize_data_field(row.get('mode', ''), 'mode')
                    standardized_row['preset'] = _standardize_data_field(row.get('preset', ''), 'preset')
                    standardized_row['shape_type'] = _standardize_data_field(row.get('shape_type', ''), 'shape_type')
                    standardized_row['day_of_week'] = _standardize_data_field(row.get('day_of_week', ''), 'day_of_week')
                    sessions.append(standardized_row)
    except (IOError, csv.Error):
        # If CSV is corrupted, recreate it
        _recreate_csv_file()
        return _get_empty_stats()

    if not sessions: 
        return _get_empty_stats()

    # Basic stats
    total_duration = sum(int(s.get('duration_sec', 0)) for s in sessions)
    total_sessions = len(sessions)
    avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
    
    # Mode preferences (now standardized)
    modes = [s.get('mode', '') for s in sessions if s.get('mode')]
    
    if modes:
        most_common_mode_key = max(set(modes), key=modes.count)
        # Convert back to localized text for display
        from .language import get_text
        if most_common_mode_key == "graphical_mode":
            mode_preference = get_text("graphical_mode")
        elif most_common_mode_key == "progress_bar_mode": 
            mode_preference = get_text("progress_bar_mode")
        else:
            mode_preference = most_common_mode_key
    else:
        mode_preference = "N/A"
    
    # Shape preferences (now standardized)
    shapes = [s.get('shape_type', '') for s in sessions if s.get('shape_type')]
    if shapes:
        most_common_shape_key = max(set(shapes), key=shapes.count)
        # Convert back to localized text for display
        from .language import get_text
        shape_display_map = {
            "diamond": get_text("diamond"),
            "star": get_text("star"),
            "wave_flow": get_text("wave_flow"),
            "tree": get_text("tree"),
            "crystal": get_text("crystal"),
            "infinity": get_text("infinity"),
            "mandala": get_text("mandala"),
            "labyrinth": get_text("labyrinth"),
            "yin_yang": get_text("yin_yang"),
            "spiral": get_text("spiral"),
            "zen_circle": get_text("zen_circle"),
            # Legacy shapes for existing data
            "lotus": get_text("lotus", "Lotus"),
            "sun": get_text("sun", "Sun"),
            "heart": get_text("heart", "Heart"),
            "flower": get_text("flower", "Flower"),
            "geometric": get_text("geometric", "Geometric"),
            "wave": get_text("wave", "Wave"),
            "matrix": get_text("matrix", "Matrix"),
            "braille": get_text("braille", "Braille"),
            "unknown": get_text("unknown")
        }
        shape_preference = shape_display_map.get(most_common_shape_key, most_common_shape_key)
    else:
        shape_preference = "N/A"

    # Time analysis (already standardized)
    time_periods = [s.get('time_of_day', '') for s in sessions if s.get('time_of_day')]
    time_preference = max(set(time_periods), key=time_periods.count) if time_periods else "N/A"
    
    # Weekly analysis
    weekly_data = {}
    for period in ["morning", "afternoon", "evening", "night"]:
        weekly_data[period] = time_periods.count(period)
    
    # Completion rate analysis
    completion_rates = [float(s.get('completion_rate', 1.0)) for s in sessions if s.get('completion_rate')]
    avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 1.0
    
    # Quality analysis
    quality_scores = [float(s.get('quality_score', 0)) for s in sessions if s.get('quality_score') and float(s['quality_score']) > 0]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

    # Streak calculation
    dates = sorted(list(set(datetime.fromisoformat(s['timestamp']).date() for s in sessions)), reverse=True)
    streak = _calculate_streak(dates)
    
    # Recent trends (last 7 days)
    recent_sessions = _get_recent_sessions(sessions, days=7)
    recent_avg_duration = sum(int(s.get('duration_sec', 0)) for s in recent_sessions) / len(recent_sessions) if recent_sessions else 0
    
    # Monthly data for charting
    monthly_data = _get_monthly_data(sessions)
    daily_data = _get_daily_data(sessions, days=30)

    return {
        "total_duration": total_duration,
        "total_sessions": total_sessions,
        "avg_duration": avg_duration,
        "mode_preference": mode_preference,
        "shape_preference": shape_preference,
        "time_preference": time_preference,
        "streak": streak,
        "avg_completion_rate": avg_completion_rate,
        "avg_quality": avg_quality,
        "recent_avg_duration": recent_avg_duration,
        "time_distribution": weekly_data,
        "monthly_data": monthly_data,
        "daily_data": daily_data,
        "total_cycles": sum(int(s.get('cycles', 0)) for s in sessions),
        "best_streak": _get_best_streak(sessions),
        "most_productive_day": _get_most_productive_day(sessions)
    }

def _recreate_csv_file():
    """Recreate CSV file with proper header when corrupted"""
    try:
        # Create new file with proper header
        headers = ['timestamp', 'start_time', 'end_time', 'mode', 'preset', 'shape_type', 
                  'duration_sec', 'cycles', 'completion_rate', 'interruptions', 'pause_count', 
                  'time_of_day', 'day_of_week', 'quality_score']
        
        with open(STATS_FILE, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
        print(f"CSV file recreated: {STATS_FILE}")
    except IOError as e:
        print(f"Failed to recreate CSV file: {e}")

def _get_empty_stats():
    """Return empty stats structure"""
    return {
        "total_duration": 0, "total_sessions": 0, "avg_duration": 0, 
        "mode_preference": "N/A", "shape_preference": "N/A", "time_preference": "N/A", 
        "streak": 0, "avg_completion_rate": 0, "avg_quality": 0, "recent_avg_duration": 0,
        "time_distribution": {"morning": 0, "afternoon": 0, "evening": 0, "night": 0},
        "monthly_data": {}, "daily_data": {}, "total_cycles": 0,
        "best_streak": 0, "most_productive_day": "N/A"
    }

def _calculate_streak(dates):
    """Calculate current streak"""
    streak = 0
    if dates:
        today = datetime.now().date()
        if (today - dates[0]).days <= 1:
            streak = 1
            for i in range(len(dates) - 1):
                if (dates[i] - dates[i+1]).days == 1:
                    streak += 1
                else:
                    break
    return streak

def _get_recent_sessions(sessions, days=7):
    """Get sessions from recent days"""
    cutoff = datetime.now() - timedelta(days=days)
    return [s for s in sessions if datetime.fromisoformat(s['timestamp']) >= cutoff]

def _get_monthly_data(sessions):
    """Get monthly aggregated data"""
    monthly = {}
    for session in sessions:
        date = datetime.fromisoformat(session['timestamp'])
        month_key = f"{date.year}-{date.month:02d}"
        if month_key not in monthly:
            monthly[month_key] = {"duration": 0, "sessions": 0}
        monthly[month_key]["duration"] += int(session.get('duration_sec', 0))
        monthly[month_key]["sessions"] += 1
    return monthly

def _get_daily_data(sessions, days=30):
    """Get daily data for recent days"""
    daily = {}
    cutoff = datetime.now() - timedelta(days=days)
    for session in sessions:
        date = datetime.fromisoformat(session['timestamp'])
        if date >= cutoff:
            day_key = date.strftime("%Y-%m-%d")
            if day_key not in daily:
                daily[day_key] = {"duration": 0, "sessions": 0}
            daily[day_key]["duration"] += int(session.get('duration_sec', 0))
            daily[day_key]["sessions"] += 1
    return daily

def _get_best_streak(sessions):
    """Calculate the best streak ever achieved"""
    if not sessions:
        return 0
    dates = sorted(list(set(datetime.fromisoformat(s['timestamp']).date() for s in sessions)))
    if not dates:
        return 0
        
    best_streak = 1
    current_streak = 1
    
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        else:
            current_streak = 1
    
    return best_streak

def _get_most_productive_day(sessions):
    """Find the most productive day of the week"""
    if not sessions:
        return "N/A"
    
    # Use standardized day keys for calculation
    day_totals = {}
    for session in sessions:
        # Use the standardized day_of_week from session data
        day_key = session.get('day_of_week', '')
        if day_key and day_key in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            if day_key not in day_totals:
                day_totals[day_key] = 0
            day_totals[day_key] += int(session.get('duration_sec', 0))
    
    if not day_totals:
        return "N/A"
    
    # Find most productive day key, then convert to localized display
    most_productive_key = max(day_totals, key=day_totals.get)
    from .language import get_text
    day_display_map = {
        "monday": get_text("monday"),
        "tuesday": get_text("tuesday"),
        "wednesday": get_text("wednesday"),
        "thursday": get_text("thursday"),
        "friday": get_text("friday"),
        "saturday": get_text("saturday"),
        "sunday": get_text("sunday")
    }
    return day_display_map.get(most_productive_key, most_productive_key)
