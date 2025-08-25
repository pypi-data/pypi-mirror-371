# -*- coding: utf-8 -*-
# main.py
import curses
import sys
from datetime import datetime, timedelta
from .ui import run_settings_menu, run_animation_loop, run_progressbar_mode, show_summary_screen, show_stats_screen, show_detailed_stats_screen
from .history import get_stats, add_session, get_time_of_day, get_day_of_week_name, calculate_completion_rate
from .language import get_text

def _standardize_preset_name(preset_name):
    """Standardize preset names to English"""
    if not preset_name:
        return "Custom"
    
    preset_map = {
        "4-7-8呼吸 (放松)": "4-7-8 Breathing (Relaxation)",
        "4-7-8呼吸法 (リラックス)": "4-7-8 Breathing (Relaxation)", 
        "盒子呼吸 (专注)": "Box Breathing (Focus)",
        "ボックス呼吸 (集中)": "Box Breathing (Focus)",
        "自定义": "Custom",
        "カスタム": "Custom",
        "Test": "Custom"  # Test entries become Custom
    }
    return preset_map.get(preset_name, preset_name)

def _get_standardized_weekday(dt):
    """Get standardized English weekday name"""
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    return weekdays[dt.weekday()]

def start_meditation_with_params(params, lang):
    """Start meditation with CLI parameters"""
    from . import shapes
    
    # Create settings from CLI parameters
    settings = {}
    
    # Set mode
    if params.get('mode') == 'guided':
        settings['mode'] = lang.get('graphical_mode', 'Graphical Mode')
    elif params.get('mode') == 'progress':
        settings['mode'] = lang.get('progress_bar_mode', 'Progress Bar Mode')
    else:
        # Default to guided mode
        settings['mode'] = lang.get('graphical_mode', 'Graphical Mode')
    
    # Set shape function
    shape_map = {
        'lotus': shapes.create_lotus_shape,
        'mandala': shapes.create_mandala_shape, 
        'sun': shapes.create_sun_shape,
        'heart': shapes.create_heart_shape,
        'flower': shapes.create_flower_shape,
        'zen_circle': shapes.create_zen_circle_shape
    }
    
    if params.get('shape'):
        settings['shape_func'] = shape_map.get(params['shape'], shapes.create_lotus_shape)
    else:
        settings['shape_func'] = shapes.create_lotus_shape
    
    # Set breathing preset
    preset_map = {
        '4-7-8': ('4-7-8', 4, 7, 8, '4-7-8 Breathing (Relaxation)'),
        'box': ('Box', 4, 4, 4, 'Box Breathing (Focus)'),
        'equal': ('Equal', 4, 0, 4, 'Equal Breathing'),
        'custom': ('Custom', 4, 0, 4, 'Custom')
    }
    
    if params.get('preset'):
        preset_data = preset_map.get(params['preset'], preset_map['4-7-8'])
        settings['preset_name'] = preset_data[4]
        settings['in_count'] = preset_data[1]
        settings['hold_count'] = preset_data[2] 
        settings['out_count'] = preset_data[3]
    else:
        # Default to 4-7-8
        preset_data = preset_map['4-7-8']
        settings['preset_name'] = preset_data[4]
        settings['in_count'] = preset_data[1]
        settings['hold_count'] = preset_data[2]
        settings['out_count'] = preset_data[3]
    
    # Set duration
    if params.get('duration'):
        settings['duration_sec'] = params['duration'] * 60
    else:
        settings['duration_sec'] = 300  # Default 5 minutes
    
    # Start meditation
    result = None
    mode = settings.pop("mode")
    
    if mode == lang.get('graphical_mode', 'Graphical Mode'):
        mode_key = "graphical_mode"
        result = curses.wrapper(run_animation_loop, settings)
    elif mode == lang.get('progress_bar_mode', 'Progress Bar Mode'):
        mode_key = "progress_bar_mode"
        result = run_progressbar_mode(settings)
    else:
        mode_key = "unknown_mode"
    
    # Save session data
    if result and result.get("duration", 0) > 0:
        now = datetime.now()
        start_time = now - timedelta(seconds=result["duration"])
        planned_duration = settings.get("duration_sec", 300)
        
        shape_names = {
            "create_lotus_shape": "lotus",
            "create_mandala_shape": "mandala", 
            "create_sun_shape": "sun",
            "create_heart_shape": "heart",
            "create_flower_shape": "flower",
            "create_zen_circle_shape": "zen_circle"
        }
        shape_func = settings.get("shape_func")
        shape_name = shape_names.get(shape_func.__name__ if shape_func else "", "unknown")
        
        session_data = {
            "timestamp": now.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": now.isoformat(),
            "mode": mode_key,
            "preset": _standardize_preset_name(settings.get("preset_name", "Unknown")),
            "shape_type": shape_name,
            "duration_sec": result.get("duration", 0),
            "cycles": result.get("cycles", 0),
            "completion_rate": calculate_completion_rate(result.get("duration", 0), planned_duration),
            "interruptions": result.get("interruptions", 0),
            "pause_count": result.get("pause_count", 0),
            "time_of_day": get_time_of_day(now),
            "day_of_week": _get_standardized_weekday(now),
            "quality_score": 0
        }
        add_session(session_data)
        
        # Show summary
        full_stats = get_stats()
        summary_stats = {**full_stats, **session_data}
        
        if mode == lang.get('graphical_mode', 'Graphical Mode'):
            curses.wrapper(show_summary_screen, summary_stats)
        else:
            session_min = result["duration"] // 60
            total_hr = full_stats["total_duration"] // 3600
            total_min_rem = (full_stats["total_duration"] % 3600) // 60
            print(f"\n\n--- {lang.get('session_summary', 'Session Summary')} ---")
            print(f"  {lang.get('session_duration', 'Duration')}: {session_min} {lang.get('minutes', 'minutes')}")
            print(f"  {lang.get('cycles', 'Cycles')}: {result['cycles']}")
            print(f"  {lang.get('total_duration', 'Total Duration')}: {total_hr} {lang.get('hours', 'hours')} {total_min_rem} {lang.get('minutes', 'minutes')}")


def main():
    """Main entry point for the Zenify application."""
    while True:
        try:
            settings = curses.wrapper(run_settings_menu)

            if not settings: # User quit from menu
                print(get_text("app_exit"))
                break

            # Handle stats screen request
            if settings.get("action") == "show_stats":
                stats = get_stats()
                curses.wrapper(show_stats_screen, stats)
                continue # Loop back to menu
            elif settings.get("action") == "show_detailed_stats":
                stats = get_stats()
                curses.wrapper(show_detailed_stats_screen, stats)
                continue # Loop back to menu

            mode = settings.pop("mode")
            result = None

            # Standardize mode names for consistent data storage
            if mode == get_text("graphical_mode"):
                mode_key = "graphical_mode"
                result = curses.wrapper(run_animation_loop, settings)
            elif mode == get_text("progress_bar_mode"):
                mode_key = "progress_bar_mode"
                result = run_progressbar_mode(settings)
            else:
                mode_key = "unknown_mode"

            # --- Unified Summary Logic ---
            if result and result.get("duration", 0) > 0:
                now = datetime.now()
                start_time = now - timedelta(seconds=result["duration"])
                planned_duration = settings.get("duration_sec", 300)  # Default to 5 minutes
                
                # Get shape name from function (standardized English keys)
                shape_names = {"create_diamond_shape": "diamond", "create_star_shape": "star", 
                              "create_wave_flow_shape": "wave_flow", "create_tree_shape": "tree",
                              "create_crystal_shape": "crystal", "create_infinity_shape": "infinity",
                              "create_mandala_shape": "mandala", "create_labyrinth_shape": "labyrinth",
                              "create_yin_yang_shape": "yin_yang", "create_spiral_pattern": "spiral",
                              "create_zen_circle_shape": "zen_circle", "create_lotus_shape": "lotus",
                              "create_sun_shape": "sun", "create_heart_shape": "heart", 
                              "create_flower_shape": "flower"}
                shape_func = settings.get("shape_func")
                shape_name = shape_names.get(shape_func.__name__ if shape_func else "", "unknown")
                
                session_data = {
                    "timestamp": now.isoformat(),
                    "start_time": start_time.isoformat(),
                    "end_time": now.isoformat(),
                    "mode": mode_key,  # Use standardized key instead of localized text
                    "preset": _standardize_preset_name(settings.get("preset_name", "Unknown")),
                    "shape_type": shape_name,
                    "duration_sec": result.get("duration", 0),
                    "cycles": result.get("cycles", 0),
                    "completion_rate": calculate_completion_rate(result.get("duration", 0), planned_duration),
                    "interruptions": result.get("interruptions", 0),
                    "pause_count": result.get("pause_count", 0),
                    "time_of_day": get_time_of_day(now),
                    "day_of_week": _get_standardized_weekday(now),
                    "quality_score": 0  # Could be enhanced with user input later
                }
                add_session(session_data)
                
                # Get fresh stats for the summary screen
                full_stats = get_stats()
                summary_stats = {**full_stats, **session_data}  # session_data should override, not be overwritten

                if mode == get_text("graphical_mode"):
                    curses.wrapper(show_summary_screen, summary_stats)
                else:
                    session_min = result["duration"] // 60
                    total_hr = full_stats["total_duration"] // 3600
                    total_min_rem = (full_stats["total_duration"] % 3600) // 60
                    print("\n\n--- 练习总结 ---")
                    print(f"  本次练习时长: {session_min} 分钟")
                    print(f"  呼吸循环次数: {result['cycles']} 次")
                    print(f"  累计练习时长: {total_hr} 小时 {total_min_rem} 分钟")
            
            if result and result.get("status") == "menu":
                continue # Loop back to menu
            else:
                print(f"\n{get_text('app_exit')} {get_text('peaceful_day')}")
                break # Exit program

        except curses.error as e:
            print(f"{get_text('error', '发生错误')}: {e}"); break
        except KeyboardInterrupt:
            print(f"\n{get_text('app_exit')}"); break
        except Exception as e:
            print(f"An unexpected error occurred: {e}"); break

if __name__ == '__main__':
    main()
