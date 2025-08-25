# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

- **Start application**: `python main.py`
- **Dependencies**: Standard Python libraries (curses, math, csv, datetime, unicodedata)

## Architecture Overview

**Enhanced Core Flow**: main.py → ui.py → shapes.py/language.py/charts.py/history.py
- `main.py`: Entry point with enhanced session tracking and multilingual support
- `ui.py`: Complete UI system with advanced menu, animations, and multi-language support
- `language.py`: Comprehensive i18n system supporting Chinese, English, and Japanese
- `shapes.py`: Beautiful ASCII art generators with proper aspect ratio correction
- `charts.py`: Advanced data visualization with CJK character width handling
- `history.py`: Rich statistical analysis and session tracking
- `easing.py`: Smooth animation transitions
- `config.py`: Central configuration hub

## Key Features

**🎨 Visual Enhancements**:
- 6 beautiful meditation shapes: Lotus, Mandala, Sun, Heart, Flower, Zen Circle
- Proper terminal aspect ratio correction (0.5 ratio for character width)
- Smooth color transitions with Morandi palette
- Advanced ASCII art with mathematical precision

**🌐 Multi-Language Support**:
- Full i18n system with Chinese (中文), English, Japanese (日本語)
- Persistent language preferences saved to `zenify_language.txt`
- CJK character width aware text formatting and chart alignment
- Dynamic UI translation with proper text width calculations

**📊 Advanced Analytics**:
- Comprehensive session tracking with 14+ data fields
- Beautiful ASCII charts: line charts, bar charts, calendar views, heatmaps
- Time-based analysis (morning/afternoon/evening/night patterns)
- Streak tracking and motivational messages
- Monthly and daily trend visualization

**🎮 Enhanced UX**:
- Improved progress bar mode with reliable pause/resume functionality
- Better input handling with cross-platform terminal raw mode
- Real-time breathing guidance with emoji indicators
- Detailed session summaries with completion rates and quality metrics

## Technical Implementation

**Character Width Handling**:
- `get_display_width()`: Calculates proper width for CJK characters
- `pad_text()` and `truncate_text()`: Smart text formatting functions
- All charts and tables use proper character width alignment

**Session Data Model**:
```
Fields: timestamp, start_time, end_time, mode, preset, shape_type, 
        duration_sec, cycles, completion_rate, interruptions, 
        pause_count, time_of_day, day_of_week, quality_score
```

**Shape Generation**:
- Mathematical precision with proper aspect ratio (0.5 factor)
- Smooth radius transitions for breathing animation
- Clean, meditation-focused designs avoiding overwhelming patterns

**Input System**:
- Cross-platform raw terminal input for progress bar mode
- Reliable pause/resume functionality with time tracking
- Menu navigation with language-aware text handling

## Development Notes

**Testing Considerations**:
- Test all three languages thoroughly
- Verify chart alignment with CJK characters
- Ensure pause/resume works reliably in both modes
- Check session data persistence and statistics accuracy

**Performance**:
- Optimized shape generation with mathematical formulas
- Efficient character width calculations
- Minimal dependencies (no external packages required)

**Maintainability**:
- Clean separation of concerns across modules
- Comprehensive error handling for file operations
- Graceful fallbacks for terminal capability limitations