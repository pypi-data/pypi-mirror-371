# -*- coding: utf-8 -*-
# ui.py
import curses
import time
import sys
import select
from . import config
from datetime import datetime
from .shapes import (
    create_diamond_shape,
    create_star_shape,
    create_wave_flow_shape,
    create_tree_shape,
    create_crystal_shape,
    create_infinity_shape,
    create_mandala_shape,
    create_labyrinth_shape,
    create_yin_yang_shape,
    create_spiral_pattern,
    create_zen_circle_shape,
)
from .easing import ease_in_out
from .charts import (
    create_line_chart,
    create_bar_chart,
    create_calendar_view,
    create_pie_chart,
    create_weekly_heatmap,
    create_progress_chart,
)
from .language import lang, get_text


# --- Color Management ---
class ColorManager:
    def __init__(self):
        self.pairs, self.next_pair, self.has_256 = (
            {},
            1,
            curses.has_colors() and curses.COLORS >= 256,
        )
        if self.has_256:
            try:
                curses.use_default_colors()
            except:
                pass

    def get(self, fg, bg=-1):
        if not self.has_256:
            return 1
        if (fg, bg) in self.pairs:
            return self.pairs[(fg, bg)]
        if self.next_pair >= curses.COLOR_PAIRS - 1:
            return 1
        curses.init_pair(self.next_pair, fg, bg)
        self.pairs[(fg, bg)] = self.next_pair
        self.next_pair += 1
        return self.next_pair - 1


# --- Drawing Helpers ---
def _draw_text(stdscr, y, x, text, pair, bold=False):
    h, w = stdscr.getmaxyx()
    if y < 0 or y >= h or x >= w:
        return
    if x < 0:
        text = text[-x:]
        x = 0
    if (x + len(text)) > w:
        text = text[: w - x - 1]
    attr = curses.color_pair(pair)
    if bold:
        attr |= curses.A_BOLD
    stdscr.addstr(y, x, text, attr)


# --- Non-blocking Input for Progress Bar ---
def check_for_input():
    """Improved non-blocking input detection"""
    try:
        if sys.platform == "win32":
            import msvcrt

            if msvcrt.kbhit():
                return msvcrt.getch().decode("utf-8", "ignore")
        else:
            # Use select with small timeout to make it more reliable
            ready, _, _ = select.select([sys.stdin], [], [], 0.01)
            if ready:
                char = sys.stdin.read(1)
                return char
    except (UnicodeDecodeError, OSError, IOError):
        pass
    return None


# --- Settings Menu ---
def run_settings_menu(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    cm = ColorManager()

    # Dynamic shape names based on current language - beautiful new designs
    shape_functions = [
        create_diamond_shape,
        create_star_shape,
        create_wave_flow_shape,
        create_tree_shape,
        create_crystal_shape,
        create_infinity_shape,
        create_mandala_shape,
        create_labyrinth_shape,
        create_yin_yang_shape,
        create_spiral_pattern,
        create_zen_circle_shape,
    ]
    shape_keys = [
        "diamond",
        "star",
        "wave_flow",
        "tree",
        "crystal",
        "infinity",
        "mandala",
        "labyrinth",
        "yin_yang",
        "spiral",
        "zen_circle",
    ]

    # Dynamic preset names
    preset_keys = ["4-7-8_breathing", "box_breathing", "custom"]

    # Dynamic mode names
    mode_keys = ["graphical_mode", "progress_bar_mode"]

    # Language options
    language_options = lang.get_language_options()

    settings = {
        "shape_idx": 0,
        "duration_min": 5,
        "preset_idx": 0,
        "mode_idx": 0,
        "lang_idx": next(
            (
                i
                for i, (code, _) in enumerate(language_options)
                if code == lang.current_language
            ),
            0,
        ),
    }
    edit_mode = None  # Track which item is being edited
    edit_values = {}  # Store temporary values during editing
    blink_counter = 0  # For blinking effect
    custom_times = list(config.PRESETS["自定义"])
    temp_custom_times = None  # Temporary custom times during editing
    selection = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        blink_counter = (blink_counter + 1) % 10  # Blink cycle

        # Get current language-specific values
        shapes = [
            (get_text(key), func) for key, func in zip(shape_keys, shape_functions)
        ]
        presets = [get_text(key) for key in preset_keys]
        modes = [get_text(key) for key in mode_keys]

        # Dynamic menu items based on language
        menu_items_base = [
            get_text("mode"),
            get_text("breathing_method"),
            get_text("duration_min"),
            get_text("view_stats"),
            get_text("detailed_analysis"),
            get_text("language"),
            get_text("start_practice"),
        ]

        _draw_text(
            stdscr,
            h // 2 - 8,
            w // 2 - 5,
            f"Zenify {get_text('settings', '设置')}",
            cm.get(config.MORANDI_WHITE),
            bold=True,
        )
        is_custom = preset_keys[settings["preset_idx"]] == "custom"
        is_graphical = mode_keys[settings["mode_idx"]] == "graphical_mode"
        menu_items = (
            menu_items_base[:2]
            + ([get_text("graphics")] if is_graphical else [])
            + menu_items_base[2:]
        )

        if is_custom:
            duration_idx = menu_items.index(get_text("duration_min"))
            menu_items.insert(duration_idx, f"  - {get_text('exhale')}")
            menu_items.insert(duration_idx, f"  - {get_text('hold')}")
            menu_items.insert(duration_idx, f"  - {get_text('inhale')}")
        for i, item in enumerate(menu_items):
            y = h // 2 - 5 + i * 2
            selector = "» " if i == selection else "  "

            # Enhanced blinking effect for edit mode
            if edit_mode == item:
                if blink_counter < 3:  # More obvious blinking
                    item_color = config.MORANDI_PINK_LIGHT
                    selector = "✏️ " if i == selection else "  "  # Edit indicator
                elif blink_counter < 6:
                    item_color = config.MORANDI_WHITE
                    selector = "✏️ " if i == selection else "  "
                else:
                    item_color = config.MORANDI_PINK_LIGHT
                    selector = "✏️ " if i == selection else "  "
            else:
                item_color = config.MORANDI_WHITE

            _draw_text(stdscr, y, w // 2 - 18, f"{selector}{item}", cm.get(item_color))
            value_text = ""

            # Show current or temporary values
            if item == get_text("mode"):
                idx = edit_values.get("mode_idx", settings["mode_idx"])
                value_text = f"< {modes[idx]} >"
            elif item == get_text("breathing_method"):
                idx = edit_values.get("preset_idx", settings["preset_idx"])
                value_text = f"< {presets[idx]} >"
            elif item == get_text("graphics"):
                idx = edit_values.get("shape_idx", settings["shape_idx"])
                value_text = f"< {shapes[idx][0]} >"
            elif item == get_text("duration_min"):
                val = edit_values.get("duration_min", settings["duration_min"])
                value_text = f"< {val} >"
            elif item == get_text("language"):
                idx = edit_values.get("lang_idx", settings["lang_idx"])
                value_text = f"< {language_options[idx][1]} >"
            elif is_custom:
                times_to_show = (
                    temp_custom_times if temp_custom_times is not None else custom_times
                )
                if item == f"  - {get_text('inhale')}":
                    value_text = f"< {times_to_show[0][1]}s >"
                elif item == f"  - {get_text('hold')}":
                    value_text = f"< {times_to_show[1][1]}s >"
                elif item == f"  - {get_text('exhale')}":
                    value_text = f"< {times_to_show[2][1]}s >"

            # Enhanced blinking value in edit mode
            if edit_mode == item:
                if blink_counter < 3:
                    value_color = config.MORANDI_WHITE
                    value_text = (
                        f"[{value_text[1:-1]}]"
                        if value_text.startswith("<")
                        else value_text
                    )
                elif blink_counter < 6:
                    value_color = config.MORANDI_PINK_LIGHT
                    value_text = (
                        f"<{value_text[1:-1]}>"
                        if value_text.startswith("[")
                        else value_text
                    )
                else:
                    value_color = config.MORANDI_WHITE
                    value_text = (
                        f"[{value_text[1:-1]}]"
                        if value_text.startswith("<")
                        else value_text
                    )
            else:
                value_color = config.MORANDI_PINK_LIGHT
            _draw_text(stdscr, y, w // 2 + 5, value_text, cm.get(value_color))

        _draw_text(
            stdscr,
            h - 2,
            w // 2 - 36,
            get_text("controls_help"),
            cm.get(config.MORANDI_GREY),
        )
        stdscr.refresh()
        key = stdscr.getch()

        # Handle Enter key
        if key in [curses.KEY_ENTER, 10]:
            current_item = menu_items[selection]
            if edit_mode == current_item:
                # Confirm changes and exit edit mode
                for key_name, value in edit_values.items():
                    settings[key_name] = value
                if temp_custom_times is not None:
                    custom_times[:] = temp_custom_times
                    temp_custom_times = None
                edit_mode = None
                edit_values.clear()

                # Apply language change if needed
                if current_item == get_text("language"):
                    lang.set_language(language_options[settings["lang_idx"]][0])

            elif current_item == get_text("view_stats"):
                return {"action": "show_stats"}
            elif current_item == get_text("detailed_analysis"):
                return {"action": "show_detailed_stats"}
            elif current_item == get_text("start_practice"):
                # Start practice
                preset_name = presets[settings["preset_idx"]]
                preset_key = preset_keys[settings["preset_idx"]]

                # Get correct preset phases
                if preset_key == "custom":
                    times = custom_times
                elif preset_key == "4-7-8_breathing":
                    times = config.PRESETS["4-7-8呼吸 (放松)"]
                elif preset_key == "box_breathing":
                    times = config.PRESETS["盒子呼吸 (专注)"]
                else:
                    times = custom_times  # fallback

                return {
                    "mode": modes[settings["mode_idx"]],
                    "shape_func": shapes[settings["shape_idx"]][1],
                    "duration_sec": settings["duration_min"] * 60,
                    "phases": times,
                    "preset_name": preset_name,
                }
        # Handle Space key for quick start
        elif key == 32:
            # Quick start regardless of selection
            preset_name = presets[settings["preset_idx"]]
            preset_key = preset_keys[settings["preset_idx"]]

            if preset_key == "custom":
                times = custom_times
            elif preset_key == "4-7-8_breathing":
                times = config.PRESETS["4-7-8呼吸 (放松)"]
            elif preset_key == "box_breathing":
                times = config.PRESETS["盒子呼吸 (专注)"]
            else:
                times = custom_times

            return {
                "mode": modes[settings["mode_idx"]],
                "shape_func": shapes[settings["shape_idx"]][1],
                "duration_sec": settings["duration_min"] * 60,
                "phases": times,
                "preset_name": preset_name,
            }
        elif key == ord("q"):
            return None
        elif key == 27:  # ESC key - cancel edit mode
            if edit_mode:
                edit_mode = None
                edit_values.clear()
                temp_custom_times = None
        if key == curses.KEY_UP:
            if edit_mode is None:
                selection = (selection - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            if edit_mode is None:
                selection = (selection + 1) % len(menu_items)
        elif key == curses.KEY_LEFT or key == curses.KEY_RIGHT:
            item_name = menu_items[selection]

            # Check if this is an editable item
            editable_items = [
                get_text("mode"),
                get_text("breathing_method"),
                get_text("graphics"),
                get_text("duration_min"),
                get_text("language"),
            ]
            if is_custom:
                editable_items.extend(
                    [
                        f"  - {get_text('inhale')}",
                        f"  - {get_text('hold')}",
                        f"  - {get_text('exhale')}",
                    ]
                )

            if item_name in editable_items:
                # Enter edit mode (will cause blinking)
                if edit_mode != item_name:
                    edit_mode = item_name
                    # Initialize temporary values with current values
                    edit_values.clear()
                    edit_values.update(settings)
                    if is_custom:
                        temp_custom_times = [t[:] for t in custom_times]  # Deep copy

                # Apply temporary changes (preview only)
                direction = -1 if key == curses.KEY_LEFT else 1

                if item_name == get_text("mode"):
                    edit_values["mode_idx"] = (
                        edit_values["mode_idx"] + direction
                    ) % len(modes)
                elif item_name == get_text("breathing_method"):
                    edit_values["preset_idx"] = (
                        edit_values["preset_idx"] + direction
                    ) % len(presets)
                elif item_name == get_text("graphics"):
                    edit_values["shape_idx"] = (
                        edit_values["shape_idx"] + direction
                    ) % len(shapes)
                elif item_name == get_text("duration_min"):
                    if direction == -1:
                        edit_values["duration_min"] = max(
                            1, edit_values["duration_min"] - 1
                        )
                    else:
                        edit_values["duration_min"] += 1
                elif item_name == get_text("language"):
                    edit_values["lang_idx"] = (
                        edit_values["lang_idx"] + direction
                    ) % len(language_options)
                elif is_custom and item_name.startswith("  -"):
                    time_indices = {
                        f"  - {get_text('inhale')}": 0,
                        f"  - {get_text('hold')}": 1,
                        f"  - {get_text('exhale')}": 2,
                    }
                    if item_name in time_indices:
                        time_idx = time_indices[item_name]
                        if not temp_custom_times:
                            temp_custom_times = [
                                t[:] for t in custom_times
                            ]  # Deep copy

                        if direction == -1:
                            temp_custom_times[time_idx] = (
                                temp_custom_times[time_idx][0],
                                max(1, temp_custom_times[time_idx][1] - 1),
                            )
                        else:
                            temp_custom_times[time_idx] = (
                                temp_custom_times[time_idx][0],
                                temp_custom_times[time_idx][1] + 1,
                            )


# --- Progress Bar Mode (COMPLETELY REWRITTEN) ---
def run_progressbar_mode(settings):
    """Improved progress bar mode with reliable pause and menu functions"""
    shape_func, duration_sec, phases, preset_name = settings.values()

    # Initialize session variables
    start_time = time.time()
    pause_start_time = 0
    total_pause_time = 0
    paused = False
    pause_count = 0
    interruptions = 0
    total_cycles = 0

    # Set terminal to raw mode for better input handling
    import tty, termios

    old_settings = None
    try:
        if sys.stdin.isatty():
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
    except (ImportError, OSError):
        # Windows or system doesn't support termios
        pass

    # Clean simple header
    print(f"\n=== {get_text('session_start')} ===")
    print(f"\n{get_text('session_controls')}")
    print("-" * 50)

    try:
        session_end_time = start_time + duration_sec

        while time.time() < session_end_time and not paused:
            for phase_name, phase_duration in phases:
                if time.time() >= session_end_time:
                    break

                phase_start_time = time.time()
                phase_end_time = min(
                    phase_start_time + phase_duration, session_end_time
                )

                while time.time() < phase_end_time:
                    # Check for input more frequently
                    for _ in range(3):  # Check 3 times per frame
                        char = check_for_input()
                        if char:
                            char = char.lower()

                            if char in ["q", "\x1b"]:  # q or Escape
                                raise KeyboardInterrupt
                            elif char == "m":  # Return to menu
                                return {
                                    "status": "menu",
                                    "duration": int(time.time() - start_time),
                                    "cycles": total_cycles,
                                    "pause_count": pause_count,
                                    "interruptions": interruptions,
                                }
                            elif char == "p":  # Pause/Resume
                                if paused:
                                    # Resume
                                    total_pause_time += time.time() - pause_start_time
                                    paused = False
                                    session_end_time += (
                                        time.time() - pause_start_time
                                    )  # Extend session
                                    phase_end_time += (
                                        time.time() - pause_start_time
                                    )  # Extend phase
                                    print(
                                        f"\r{'':60}\r继续练习...               ",
                                        end="\r",
                                    )
                                    sys.stdout.flush()
                                    time.sleep(
                                        0.5
                                    )  # Brief pause to show resume message
                                else:
                                    # Pause
                                    paused = True
                                    pause_start_time = time.time()
                                    pause_count += 1
                                break  # Exit input check loop

                    if paused:
                        pause_msg = (
                            f"⏸️ {get_text('paused')} - [p] 继续 [m] 菜单 [q] 退出"
                        )
                        print(f"\r{pause_msg}", end="\r")
                        sys.stdout.flush()
                        time.sleep(0.1)
                        continue

                    # Calculate and display progress
                    current_time = time.time()
                    if current_time >= phase_end_time:
                        break

                    progress = (current_time - phase_start_time) / (
                        phase_end_time - phase_start_time
                    )
                    progress = min(1.0, max(0.0, progress))

                    # Professional phase display
                    phase_info = {
                        "inhale": {
                            "icon": "🫁",
                            "name": get_text("inhale"),
                            "guide": get_text("breathe_in_slowly"),
                        },
                        "hold": {
                            "icon": "⏱️",
                            "name": get_text("hold"),
                            "guide": get_text("hold_breath"),
                        },
                        "exhale": {
                            "icon": "💨",
                            "name": get_text("exhale"),
                            "guide": get_text("breathe_out_slowly"),
                        },
                        "hold_post": {
                            "icon": "⏱️",
                            "name": get_text("hold_post"),
                            "guide": get_text("hold_breath"),
                        },
                    }

                    info = phase_info.get(
                        phase_name, {"icon": "⚡", "name": phase_name, "guide": ""}
                    )

                    # Professional progress bar
                    bar_width = 50
                    filled_len = int(bar_width * progress)
                    bar = "█" * filled_len + "░" * (bar_width - filled_len)

                    # Time and percentage
                    remaining = max(0, int(phase_end_time - current_time))
                    percentage = int(progress * 100)

                    # Format: [ICON] PHASE_NAME |████████░░░░░░░| 85% (3s) - Guidance text
                    phase_name_padded = f"{info['name']:<8}"  # Pad to 8 characters
                    percentage_str = f"{percentage:3d}%"
                    time_str = f"({remaining:2d}s)"

                    line = f"\r{info['icon']} {phase_name_padded} |{bar}| {percentage_str} {time_str} - {info['guide']}"
                    print(line.ljust(80), end="")
                    sys.stdout.flush()

                    time.sleep(1 / config.FPS)

                # Complete phase
                if not paused and time.time() >= phase_end_time:
                    info = phase_info.get(
                        phase_name, {"icon": "⚡", "name": phase_name, "guide": ""}
                    )
                    completed_bar = "█" * bar_width
                    phase_name_padded = f"{info['name']:<8}"
                    completion_line = f"\r{info['icon']} {phase_name_padded} |{completed_bar}| 100% ✓   - {info['guide']}"
                    print(completion_line.ljust(80))
                    time.sleep(0.3)  # Brief pause between phases

                if time.time() >= session_end_time:
                    break

            if time.time() < session_end_time and not paused:
                total_cycles += 1
                print(f"\n--- {get_text('cycle_completed')} ---")

    except KeyboardInterrupt:
        interruptions += 1
        print(f"\n\n{get_text('interrupted')}")

    finally:
        # Restore terminal settings
        if old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except:
                pass

    # Calculate final duration
    final_time = time.time()
    if paused:
        total_pause_time += final_time - pause_start_time

    duration_completed = int(final_time - start_time - total_pause_time)

    return {
        "status": "completed",
        "duration": duration_completed,
        "cycles": total_cycles,
        "pause_count": pause_count,
        "interruptions": interruptions,
    }


# --- Graphical Animation Loop ---
def _get_color(p, s, e):
    return int(s + (e - s) * p)


def run_animation_loop(stdscr, settings):
    """Enhanced graphical animation with pause and interruption tracking"""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1000 // config.FPS)
    cm = ColorManager()
    shape_func, duration_sec, phases, preset_name = settings.values()
    total_frames = int(duration_sec * config.FPS)
    phase_frames = [(p[0], int(p[1] * config.FPS)) for p in phases]
    cycle_frames = sum(p[1] for p in phase_frames)

    # Enhanced tracking variables
    frame, paused = 0, False
    start_time = time.time()
    pause_count = 0
    interruptions = 0
    total_pause_time = 0
    pause_start_time = 0

    while frame < total_frames:
        key = stdscr.getch()

        if key == ord("q"):
            interruptions += 1
            break
        elif key == ord("m"):
            return {
                "status": "menu",
                "duration": int(time.time() - start_time - total_pause_time),
                "cycles": int(frame / cycle_frames) if cycle_frames > 0 else 0,
                "pause_count": pause_count,
                "interruptions": interruptions,
            }
        elif key == ord("p"):
            if paused:
                # Resume
                total_pause_time += time.time() - pause_start_time
                paused = False
            else:
                # Pause
                paused = True
                pause_start_time = time.time()
                pause_count += 1

        if paused:
            h, w = stdscr.getmaxyx()
            pause_text = f"⏸️ {get_text('paused')}"
            continue_text = get_text("continue_practice")
            _draw_text(
                stdscr,
                h // 2,
                w // 2 - len(pause_text) // 2,
                pause_text,
                cm.get(config.MORANDI_WHITE),
                bold=True,
            )
            _draw_text(
                stdscr,
                h // 2 + 2,
                w // 2 - len(continue_text) // 2,
                continue_text,
                cm.get(config.MORANDI_GREY),
            )
            stdscr.refresh()
            continue

        # Animation logic
        frame_in_cycle = frame % cycle_frames
        accumulated_frames = 0

        for phase_name, duration_in_frames in phase_frames:
            if frame_in_cycle < accumulated_frames + duration_in_frames:
                progress = (frame_in_cycle - accumulated_frames) / duration_in_frames
                e_p = ease_in_out(progress)
                start_color, end_color = config.COLOR_MAP[phase_name]
                color = _get_color(e_p, start_color, end_color)

                if phase_name == "inhale":
                    radius = (
                        config.MIN_RADIUS
                        + (config.MAX_RADIUS - config.MIN_RADIUS) * e_p
                    )
                elif phase_name == "exhale":
                    radius = (
                        config.MAX_RADIUS
                        - (config.MAX_RADIUS - config.MIN_RADIUS) * e_p
                    )
                elif phase_name == "hold":
                    radius = config.MAX_RADIUS
                else:
                    radius = config.MIN_RADIUS
                break
            accumulated_frames += duration_in_frames

        # Draw animation
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        shape = shape_func(radius)
        shape_lines = shape
        shape_h, shape_w = len(shape_lines), len(shape_lines[0]) if shape_lines else 0
        start_y, start_x = h // 2 - shape_h // 2 - 3, w // 2 - shape_w // 2
        pair = cm.get(color)

        for i, line in enumerate(shape_lines):
            if 0 <= start_y + i < h and 0 <= start_x < w:
                stdscr.addstr(
                    start_y + i,
                    start_x,
                    line[: w - start_x - 1],
                    curses.color_pair(pair),
                )

        # Phase display
        phase_display_names = {
            "inhale": get_text("inhale"),
            "hold": get_text("hold"),
            "exhale": get_text("exhale"),
            "hold_post": get_text("hold_post"),
        }
        phase_text = phase_display_names.get(phase_name, phase_name)
        _draw_text(
            stdscr, h // 2 + 8, w // 2 - len(phase_text) // 2, phase_text, cm.get(color)
        )

        # Progress bar
        progress_bar_width = 20
        filled_len = int(progress_bar_width * frame / total_frames)
        bar = "█" * filled_len + "-" * (progress_bar_width - filled_len)
        _draw_text(
            stdscr,
            h // 2 + 12,
            w // 2 - progress_bar_width // 2 - 1,
            f"[{bar}]",
            cm.get(config.MORANDI_GREY),
        )

        # Controls
        controls_text = f"{get_text('pause_continue')}  {get_text('return_menu')}  {get_text('quit')}"
        _draw_text(
            stdscr,
            h - 2,
            w // 2 - len(controls_text) // 2,
            controls_text,
            cm.get(config.MORANDI_GREY),
        )

        stdscr.refresh()
        frame += 1

    duration_completed = time.time() - start_time - total_pause_time
    return {
        "status": "completed",
        "duration": int(duration_completed),
        "cycles": int(frame / cycle_frames) if cycle_frames > 0 else 0,
        "pause_count": pause_count,
        "interruptions": interruptions,
    }


# --- Summary & Stats Screens ---
def show_summary_screen(stdscr, stats):
    curses.curs_set(0)
    stdscr.nodelay(False)
    cm = ColorManager()
    h, w = stdscr.getmaxyx()
    session_min = stats.get("duration_sec", 0) // 60
    total_hr = stats.get("total_duration", 0) // 3600
    total_min_rem = (stats.get("total_duration", 0) % 3600) // 60
    cycles = stats.get("cycles", 0)
    stdscr.clear()
    _draw_text(
        stdscr,
        h // 2 - 4,
        w // 2 - 4,
        "练习结束",
        cm.get(config.MORANDI_WHITE),
        bold=True,
    )
    _draw_text(
        stdscr,
        h // 2 - 2,
        w // 2 - 12,
        f"本次练习时长: {session_min} 分钟",
        cm.get(config.MORANDI_WHITE),
    )
    _draw_text(
        stdscr,
        h // 2 - 1,
        w // 2 - 12,
        f"呼吸循环次数: {cycles} 次",
        cm.get(config.MORANDI_WHITE),
    )
    _draw_text(
        stdscr,
        h // 2 + 1,
        w // 2 - 12,
        f"累计练习时长: {total_hr} 小时 {total_min_rem} 分钟",
        cm.get(config.MORANDI_PINK_LIGHT),
    )
    _draw_text(stdscr, h - 2, w // 2 - 10, "按任意键退出", cm.get(config.MORANDI_GREY))
    stdscr.refresh()
    stdscr.getch()


def show_stats_screen(stdscr, stats):
    curses.curs_set(0)
    stdscr.nodelay(False)
    cm = ColorManager()
    h, w = stdscr.getmaxyx()
    stdscr.clear()

    # Multilingual title and labels
    title = get_text("statistics")
    _draw_text(
        stdscr,
        h // 2 - 6,
        w // 2 - len(title) // 2,
        title,
        cm.get(config.MORANDI_WHITE),
        bold=True,
    )

    total_min = stats["total_duration"] // 60
    total_sec_rem = stats["total_duration"] % 60
    avg_sec = stats["avg_duration"] if stats["avg_duration"] > 0 else 0

    # Multilingual stat lines
    stat_lines = [
        f"{get_text('total_practice_time')}: {total_min} {get_text('minutes')} {total_sec_rem} {get_text('seconds')}",
        f"{get_text('total_sessions')}: {stats['total_sessions']} {get_text('times')}",
        f"{get_text('average_duration')}: {avg_sec:.1f} {get_text('seconds')}",
        f"{get_text('most_used_mode')}: {stats['mode_preference']}",
        f"{get_text('current_streak')}: {stats['streak']} {get_text('days')}",
    ]

    # Better formatting with proper alignment
    max_label_width = max(len(line.split(":")[0]) for line in stat_lines)

    for i, line in enumerate(stat_lines):
        label, value = line.split(":", 1)
        formatted_line = f"{label:<{max_label_width}}: {value.strip()}"
        _draw_text(
            stdscr,
            h // 2 - 3 + i * 2,
            w // 2 - len(formatted_line) // 2,
            formatted_line,
            cm.get(config.MORANDI_WHITE),
        )

    exit_text = get_text("press_any_key_menu")
    _draw_text(
        stdscr,
        h - 2,
        w // 2 - len(exit_text) // 2,
        exit_text,
        cm.get(config.MORANDI_GREY),
    )
    stdscr.refresh()
    stdscr.getch()


def show_detailed_stats_screen(stdscr, stats):
    """Show detailed statistics with charts"""
    curses.curs_set(0)
    stdscr.nodelay(False)
    cm = ColorManager()
    current_chart = 0
    charts_data = []

    # Prepare multilingual chart data
    if stats["monthly_data"]:
        monthly_duration = {
            k: v["duration"] // 60 for k, v in stats["monthly_data"].items()
        }
        title = get_text("monthly_duration")
        chart_title = f"{title} ({get_text('minutes')})"
        charts_data.append((title, create_line_chart(monthly_duration, chart_title)))

    if stats["time_distribution"]:
        time_dist = {}
        time_labels = {
            "morning": get_text("morning"),
            "afternoon": get_text("afternoon"),
            "evening": get_text("evening"),
            "night": get_text("night"),
        }
        for k, v in stats["time_distribution"].items():
            if v > 0:
                time_dist[time_labels.get(k, k)] = v
        if time_dist:
            title = get_text("time_distribution")
            charts_data.append((title, create_pie_chart(time_dist, title)))

    if stats["daily_data"]:
        title = get_text("practice_calendar")
        charts_data.append((title, create_calendar_view(stats["daily_data"], title)))

    # Weekly data for heatmap - use real daily data if available
    if stats.get("daily_data"):
        # Use actual daily practice data
        daily_sums = {}
        for date_str, day_data in stats["daily_data"].items():
            # Convert date to weekday
            try:
                date_obj = datetime.fromisoformat(date_str).date()
                weekday_num = date_obj.weekday()  # 0=Monday, 6=Sunday

                current_lang = lang.current_language
                if current_lang == "zh":
                    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
                elif current_lang == "ja":
                    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
                else:
                    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

                weekday_name = weekdays[weekday_num]
                if weekday_name not in daily_sums:
                    daily_sums[weekday_name] = 0
                daily_sums[weekday_name] += day_data.get("duration", 0)
            except (ValueError, KeyError):
                continue

        if daily_sums:
            title = get_text("practice_heatmap")
            charts_data.append((title, create_weekly_heatmap(daily_sums, title)))
    elif stats["time_distribution"]:
        # Fallback: create minimal realistic data for demonstration
        current_lang = lang.current_language
        if current_lang == "zh":
            sample_data = {
                "一": 0,
                "二": 0,
                "三": 0,
                "四": 0,
                "五": 300,
                "六": 0,
                "日": 600,
            }
        elif current_lang == "ja":
            sample_data = {
                "月": 0,
                "火": 0,
                "水": 0,
                "木": 0,
                "金": 300,
                "土": 0,
                "日": 600,
            }
        else:
            sample_data = {
                "Mon": 0,
                "Tue": 0,
                "Wed": 0,
                "Thu": 0,
                "Fri": 300,
                "Sat": 0,
                "Sun": 600,
            }

        title = get_text("practice_heatmap")
        charts_data.append((title, create_weekly_heatmap(sample_data, title)))

    # Progress chart
    title = get_text("streak_progress")
    progress_chart = create_progress_chart(stats["streak"], stats["best_streak"], title)
    charts_data.append((title, progress_chart))

    if not charts_data:
        no_data_title = get_text("no_data")
        no_data_content = [
            get_text("no_enough_data"),
            get_text("start_practice_to_view"),
        ]
        charts_data.append((no_data_title, no_data_content))

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Multilingual title
        base_title = get_text("detailed_stats")
        title = f"{base_title} ({current_chart + 1}/{len(charts_data)})"
        _draw_text(
            stdscr,
            1,
            w // 2 - len(title) // 2,
            title,
            cm.get(config.MORANDI_WHITE),
            bold=True,
        )

        # Current chart
        chart_title, chart_lines = charts_data[current_chart]
        _draw_text(
            stdscr,
            3,
            w // 2 - len(chart_title) // 2,
            chart_title,
            cm.get(config.MORANDI_PINK_LIGHT),
        )

        # Draw chart
        start_y = 5
        for i, line in enumerate(chart_lines):
            if start_y + i < h - 3:
                _draw_text(
                    stdscr, start_y + i, 2, line[: w - 4], cm.get(config.MORANDI_WHITE)
                )

        # Multilingual navigation help
        nav_text = get_text("navigation")
        _draw_text(
            stdscr,
            h - 2,
            w // 2 - len(nav_text) // 2,
            nav_text,
            cm.get(config.MORANDI_GREY),
        )

        stdscr.refresh()
        key = stdscr.getch()

        if key in [curses.KEY_ENTER, 10, ord("q")]:
            break
        elif key == curses.KEY_LEFT and len(charts_data) > 1:
            current_chart = (current_chart - 1) % len(charts_data)
        elif key == curses.KEY_RIGHT and len(charts_data) > 1:
            current_chart = (current_chart + 1) % len(charts_data)
