#!/usr/bin/env python3
"""
CLI entry point for Zenify meditation app
"""

import argparse
import sys
import os

# Import main modules
from . import main
from . import history
from . import language


def create_parser():
    """Create argument parser for CLI"""
    parser = argparse.ArgumentParser(
        prog='zen',
        description='A beautiful terminal meditation app with multi-language support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zen                          # Start interactive menu
  zen -m guided               # Start guided breathing mode
  zen -m progress             # Start progress bar mode  
  zen -s lotus                # Start with lotus shape
  zen -p 4-7-8                # Start with 4-7-8 breathing preset
  zen -d 10                   # Set duration to 10 minutes
  zen --stats                 # Show meditation statistics
  zen --lang zh               # Set language to Chinese
  zen --lang en               # Set language to English
  zen --lang ja               # Set language to Japanese

Available shapes: lotus, mandala, sun, heart, flower, zen_circle
Available presets: 4-7-8, box, equal, custom
        """
    )
    
    # Mode options
    parser.add_argument('-m', '--mode', 
                       choices=['guided', 'progress'],
                       help='Meditation mode (guided or progress)')
    
    # Shape options
    parser.add_argument('-s', '--shape',
                       choices=['lotus', 'mandala', 'sun', 'heart', 'flower', 'zen_circle'],
                       help='Shape for guided mode')
    
    # Breathing preset
    parser.add_argument('-p', '--preset',
                       choices=['4-7-8', 'box', 'equal', 'custom'],
                       help='Breathing pattern preset')
    
    # Duration
    parser.add_argument('-d', '--duration', type=int,
                       help='Meditation duration in minutes')
    
    # Statistics
    parser.add_argument('--stats', action='store_true',
                       help='Show meditation statistics and exit')
    
    # Language
    parser.add_argument('--lang', '--language',
                       choices=['zh', 'en', 'ja'],
                       help='Set interface language (zh=Chinese, en=English, ja=Japanese)')
    
    # Version
    parser.add_argument('--version', action='version', version='zenify 1.0.0')
    
    return parser


def show_stats():
    """Show meditation statistics"""
    try:
        # Load language
        lang_code = language.load_language_preference()
        lang_dict = language.get_language_strings(lang_code)
        
        # Get stats from history module  
        stats = history.get_stats()
        
        # Display basic statistics
        total_sessions = stats.get("total_sessions", 0)
        total_duration = stats.get("total_duration", 0)
        total_minutes = total_duration // 60
        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60
        
        avg_duration = stats.get("average_duration", 0) // 60
        current_streak = stats.get("current_streak", 0)
        best_streak = stats.get("best_streak", 0)
        
        print("\n=== Zenify Meditation Statistics ===")
        print(f"Total Sessions: {total_sessions}")
        print(f"Total Time: {total_hours}h {remaining_minutes}m")
        print(f"Average Session: {avg_duration} minutes")
        print(f"Current Streak: {current_streak} days")
        print(f"Best Streak: {best_streak} days")
        
        if total_sessions > 0:
            print(f"\nCompletion Rate: {stats.get('completion_rate', 0):.1f}%")
            print(f"Most Active Time: {stats.get('most_active_time_of_day', 'N/A')}")
            print(f"Favorite Mode: {stats.get('most_used_mode', 'N/A')}")
        
    except Exception as e:
        print(f"Error showing statistics: {e}")
        sys.exit(1)


def set_language(lang_code):
    """Set and save language preference"""
    try:
        language.save_language_preference(lang_code)
        lang = language.get_language_strings(lang_code)
        lang_names = {"zh": "中文", "en": "English", "ja": "日本語"}
        print(f"Language set to: {lang_names.get(lang_code, lang_code)}")
    except Exception as e:
        print(f"Error setting language: {e}")
        sys.exit(1)


def start_meditation(args):
    """Start meditation with CLI parameters"""
    try:
        # Set language if specified
        if args.lang:
            set_language(args.lang)
        
        # Load current language
        lang_code = language.load_language_preference()
        lang = language.get_language_strings(lang_code)
        
        # Prepare session parameters
        session_params = {}
        
        if args.mode:
            session_params['mode'] = args.mode
            
        if args.shape:
            session_params['shape'] = args.shape
            
        if args.preset:
            session_params['preset'] = args.preset
            
        if args.duration:
            session_params['duration'] = args.duration
        
        # Start meditation with parameters
        from . import main as main_module
        main_module.start_meditation_with_params(session_params, lang)
        
    except KeyboardInterrupt:
        print(f"\n{lang.get('meditation_interrupted', 'Meditation interrupted')}")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting meditation: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = create_parser()
    
    # If no arguments provided, start interactive mode
    if len(sys.argv) == 1:
        try:
            from . import main as main_module
            main_module.main()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
        return
    
    args = parser.parse_args()
    
    # Handle specific commands
    if args.stats:
        show_stats()
        return
    
    if args.lang and not any([args.mode, args.shape, args.preset, args.duration]):
        # Just setting language
        set_language(args.lang)
        return
    
    # Start meditation with parameters
    start_meditation(args)


if __name__ == '__main__':
    main()