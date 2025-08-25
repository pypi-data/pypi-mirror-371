# -*- coding: utf-8 -*-
# charts.py
import math
import unicodedata
from datetime import datetime, timedelta
from .language import get_text, lang


def get_display_width(text):
    """精确计算显示宽度，考虑CJK字符"""
    if not text:
        return 0
    width = 0
    for char in str(text):
        # 检查字符是否为全角或宽字符
        eaw = unicodedata.east_asian_width(char)
        if eaw in ("F", "W"):  # Fullwidth, Wide
            width += 2
        elif eaw in ("H", "N", "Na"):  # Halfwidth, Narrow, Neutral
            width += 1
        else:  # 'A' (Ambiguous) 作为1处理
            width += 1
    return width


def pad_text(text, target_width, align="left"):
    """按指定宽度对齐文本"""
    if not text:
        text = ""
    current_width = get_display_width(text)

    if current_width >= target_width:
        return text[:target_width] if current_width > target_width else text

    padding = target_width - current_width

    if align == "center":
        left_pad = padding // 2
        right_pad = padding - left_pad
        return " " * left_pad + text + " " * right_pad
    elif align == "right":
        return " " * padding + text
    else:  # left
        return text + " " * padding


def truncate_text(text, max_width):
    """安全截断文本到指定宽度"""
    if not text:
        return ""

    current_width = 0
    result = ""

    for char in str(text):
        char_width = 2 if unicodedata.east_asian_width(char) in ("F", "W") else 1
        if current_width + char_width > max_width:
            break
        result += char
        current_width += char_width

    return result


def create_line_chart(data, title="", width=45, height=12):
    """Create fixed width ASCII line chart"""
    if not data or not any(data.values()):
        no_data_text = get_text("no_data")
        return [pad_text(f"{title}: {no_data_text}", width)]

    values = list(data.values())
    labels = list(data.keys())

    if not values:
        no_data_text = get_text("no_data")
        return [pad_text(f"{title}: {no_data_text}", width)]

    min_val, max_val = min(values), max(values)
    if min_val == max_val:
        max_val += 1

    chart = []

    # 标题行 - 精确控制宽度
    title_safe = truncate_text(title, width - 8)
    title_line = (
        f"┌─ {title_safe} "
        + "─" * (width - get_display_width(f"┌─ {title_safe} ") - 1)
        + "┐"
    )
    chart.append(title_line)

    # 图表主体
    plot_width = width - 2  # 为边框和Y轴数值留空间

    for y in range(height):
        y_val = (
            max_val - (max_val - min_val) * y / (height - 1) if height > 1 else max_val
        )

        # 绘制数据点
        line_content = ""
        for x in range(plot_width):
            if x < len(values):
                val = values[x]
                if max_val != min_val:
                    chart_y = int((max_val - val) / (max_val - min_val) * (height - 1))
                else:
                    chart_y = height // 2

                if chart_y == y:
                    line_content += "●"
                elif abs(chart_y - y) == 1:
                    line_content += "·"
                else:
                    line_content += " "
            else:
                line_content += " "

        # 确保内容宽度正确
        line_content = pad_text(line_content, plot_width)

        # 构建完整行，包括Y轴数值
        y_val_str = f"{y_val:.0f}"
        full_line = f"│{line_content}│ {y_val_str}"

        # 确保整行宽度正确
        full_line = pad_text(full_line, width + 5)
        chart.append(full_line)

    # 底部边框
    bottom_line = "└" + "─" * (width - 2) + "┘"
    chart.append(bottom_line)

    # X轴标签
    if labels and len(labels) <= 5:
        label_content = "  ".join(truncate_text(label, 8) for label in labels[:5])
        label_line = " " + pad_text(label_content, width - 2) + " "
        chart.append(label_line)

    return chart


def create_bar_chart(data, title="", width=50, height=12):
    """Create ASCII bar chart"""
    if not data:
        no_data_text = get_text("no_data")
        return [pad_text(f"{title}: {no_data_text}", width)]

    items = list(data.items())
    if not items:
        no_data_text = get_text("no_data")
        return [pad_text(f"{title}: {no_data_text}", width)]

    max_val = max(items, key=lambda x: x[1])[1] if items else 1
    if max_val == 0:
        max_val = 1

    chart = []
    title_truncated = truncate_text(title, width - 6)
    title_width = get_display_width(title_truncated)
    border = "─" * (width - title_width - 4)
    chart.append(f"┌─ {title_truncated} ─{border}┐")

    # Calculate bar width considering label display width
    total_label_width = sum(min(get_display_width(label), 8) + 1 for label, _ in items)
    bar_width = max(1, (width - 20) // len(items))

    for y in range(height, 0, -1):
        line = "│"
        threshold = (y / height) * max_val

        for label, value in items:
            if value >= threshold:
                line += "█" * bar_width
            else:
                line += " " * bar_width
            line += " "

        line = pad_text(line, width - 10)
        line += f"│ {threshold:.0f}"
        chart.append(line)

    # Bottom line
    chart.append("└" + "─" * (width - 2) + "┘")

    # Labels
    label_line = " "
    for label, value in items:
        short_label = truncate_text(label, bar_width * 2)
        padded_label = pad_text(short_label, bar_width)
        label_line += padded_label + " "
    chart.append(pad_text(label_line, width))

    return chart


def create_calendar_view(daily_data, title="", weeks=4):
    """Create ASCII calendar view with fixed alignment"""
    today = datetime.now().date()
    start_date = today - timedelta(days=weeks * 7 - 1)

    chart = []
    target_width = 25  # 固定宽度

    # 标题行
    title_safe = truncate_text(title, target_width - 8)
    title_line = (
        f"┌─ {title_safe} "
        + "─" * (target_width - get_display_width(f"┌─ {title_safe} ") - 1)
        + "┐"
    )
    chart.append(title_line)

    # 星期标题
    current_lang = lang.current_language
    if current_lang == "zh":
        weekday_chars = ["一", "二", "三", "四", "五", "六", "日"]
    elif current_lang == "ja":
        weekday_chars = ["月", "火", "水", "木", "金", "土", "日"]
    else:
        weekday_chars = ["M", "T", "W", "T", "F", "S", "S"]

    # 构建标题行 - 更均匀分布
    header_content = " ".join(weekday_chars)
    header_padded = pad_text(header_content, target_width - 2, "center")
    header_line = f"│{header_padded}│"
    chart.append(header_line)

    # 分隔线
    separator = "├" + "─" * (target_width - 2) + "┤"
    chart.append(separator)

    # 对齐到周一
    current_date = start_date
    while current_date.weekday() != 0:
        current_date -= timedelta(days=1)

    # 绘制周行 - 更好的点分布
    for week in range(weeks):
        symbols = []
        for day in range(7):
            date_str = current_date.strftime("%Y-%m-%d")

            if date_str in daily_data:
                duration = daily_data[date_str].get("duration", 0)
                if duration >= 600:  # 10+ minutes
                    symbol = "●"
                elif duration >= 300:  # 5+ minutes
                    symbol = "◐"
                elif duration > 0:
                    symbol = "○"
                else:
                    symbol = "·"
            elif current_date <= today:
                symbol = "·"
            else:
                symbol = " "

            symbols.append(symbol)
            current_date += timedelta(days=1)

        # 构建周内容 - 根据语言调整点的间距
        current_lang = lang.current_language
        if current_lang in ["zh", "ja"]:
            # 中文和日文的星期名称是2字符宽，需要更宽的间距
            week_content = "  ".join(symbols)  # 双空格间距
        else:
            # 英文的星期名称是1字符宽
            week_content = " ".join(symbols)  # 单空格间距

        week_padded = pad_text(week_content, target_width - 2, "center")
        week_line = f"│{week_padded}│"
        chart.append(week_line)

    # 底部边框
    bottom_line = "└" + "─" * (target_width - 2) + "┘"
    chart.append(bottom_line)

    # 图例 - 允许稍微超出宽度
    legend_text = f"● {get_text('10plus_minutes')} ◐ {get_text('5plus_minutes')}"
    legend_text2 = f"○ {get_text('under_5_minutes')} · {get_text('no_practice')}"

    chart.append(pad_text(legend_text, target_width, "center"))
    chart.append(pad_text(legend_text2, target_width, "center"))

    return chart


def create_pie_chart(data, title="", width=35):
    """Create simplified horizontal bar chart for time distribution"""
    if not data or not any(data.values()):
        no_data_text = get_text("no_data")
        return [pad_text(f"{title}: {no_data_text}", width)]

    total = sum(data.values())
    if total <= 0:
        no_data_text = get_text("no_data")
        return [pad_text(f"{title}: {no_data_text}", width)]

    chart = []

    # 标题行
    title_safe = truncate_text(title, width - 8)
    title_line = (
        f"┌─ {title_safe} "
        + "─" * (width - get_display_width(f"┌─ {title_safe} ") - 1)
        + "┐"
    )
    chart.append(title_line)

    # 符号
    symbols = ["█", "▓", "▒", "░", "▪", "▫", "●", "○"]

    # 为每个数据项创建水平条
    for i, (label, value) in enumerate(data.items()):
        if value > 0:
            percentage = (value / total) * 100
            bar_length = max(1, int((percentage / 100) * 20))  # 最大20字符的条

            symbol = symbols[i % len(symbols)]
            bar = symbol * bar_length + "░" * (20 - bar_length)

            # 格式化显示
            label_safe = truncate_text(label, 8)
            percent_str = f"{percentage:.1f}%"

            # 构建行内容
            content = f"{symbol} {label_safe}: {percent_str}"
            content_padded = pad_text(content, width - 2)
            line = f"│{content_padded}│"
            chart.append(line)

    # 底部边框
    bottom_line = "└" + "─" * (width - 2) + "┘"
    chart.append(bottom_line)

    return chart


def create_weekly_heatmap(weekly_data, title=""):
    """Create weekly practice heatmap with fixed alignment"""
    current_lang = lang.current_language

    # 获取星期标签
    if current_lang == "zh":
        days = ["一", "二", "三", "四", "五", "六", "日"]
        unit = "分"
    elif current_lang == "ja":
        days = ["月", "火", "水", "木", "金", "土", "日"]
        unit = "分"
    else:  # English
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        unit = "m"

    if not weekly_data:
        weekly_data = {day: 0 for day in days}

    chart = []
    target_width = 32  # 固定宽度

    # 标题行
    # title_safe = truncate_text(title, target_width - 8)
    title_safe = title
    title_line = (
        f"┌─ {title_safe} "
        + "─" * (target_width - get_display_width(f"┌─ {title_safe} ") - 1)
        + "┐"
    )
    chart.append(title_line)

    # 计算最大时长（分钟）
    max_duration_sec = max(weekly_data.values()) if weekly_data.values() else 60
    max_duration_min = max(1, max_duration_sec // 60)

    # 为每天创建行
    for day in days:
        duration_sec = weekly_data.get(day, 0)
        duration_min = duration_sec // 60

        # 强度计算
        intensity = duration_min / max_duration_min if max_duration_min > 0 else 0

        # 进度条（固定8字符宽度）
        if intensity >= 0.8:
            bar = "████████"
        elif intensity >= 0.6:
            bar = "██████▓▓"
        elif intensity >= 0.4:
            bar = "████▓▓▓▓"
        elif intensity >= 0.2:
            bar = "██▓▓▓▓▓▓"
        elif intensity > 0:
            bar = "▓▓▓▓░░░░"
        else:
            bar = "░░░░░░░░"

        # 构建行内容 - 精确控制宽度
        day_part = f"{day}:"  # 星期标签
        bar_part = bar  # 进度条
        value_part = f"{duration_min:2d}{unit}"  # 数值

        # 计算实际显示宽度
        day_width = get_display_width(day_part)
        bar_width = 8  # 进度条固定宽度
        value_width = get_display_width(value_part)

        # 总内容宽度
        content_width = day_width + 1 + bar_width + 1 + value_width  # +1为空格
        padding_needed = target_width - 2 - content_width  # -2为边框

        if padding_needed > 0:
            content = f"{day_part} {bar_part}{' ' * padding_needed} {value_part}"
        else:
            content = f"{day_part} {bar_part} {value_part}"

        # 确保内容不超出边界
        content = truncate_text(content, target_width - 2)
        content = pad_text(content, target_width - 2)

        line = f"│{content}│"
        chart.append(line)

    # 底部边框
    bottom_line = "└" + "─" * (target_width - 2) + "┘"
    chart.append(bottom_line)

    return chart


def create_progress_chart(current_streak, best_streak, title=""):
    """Create progress visualization for streaks with fixed alignment"""
    chart = []
    target_width = 40

    # 标题行
    title_safe = truncate_text(title, target_width - 8)
    title_line = (
        f"┌─ {title_safe} "
        + "─" * (target_width - get_display_width(f"┌─ {title_safe} ") - 1)
        + "┐"
    )
    chart.append(title_line)

    # 计算进度条参数
    max_display = max(best_streak, current_streak, 10)  # 至少10作为最大值
    bar_length = 15  # 固定进度条长度

    current_blocks = (
        int((current_streak / max_display) * bar_length) if max_display > 0 else 0
    )
    best_blocks = (
        int((best_streak / max_display) * bar_length) if max_display > 0 else 0
    )

    # 获取本地化文本
    current_label = get_text("current_streak")
    best_label = get_text("best_streak")
    days_text = get_text("days")

    # 当前连续天数行
    current_bar = "█" * current_blocks + "░" * (bar_length - current_blocks)
    current_value = f"{current_streak}{days_text}"

    # 计算宽度分布
    label_width = get_display_width(current_label)
    value_width = get_display_width(current_value)
    separator_width = 2  # ": "

    # 计算填充
    total_fixed_width = (
        label_width + separator_width + bar_length + 1 + value_width
    )  # +1 for space
    padding_needed = max(0, target_width - 2 - total_fixed_width)  # -2 for borders

    current_content = (
        f"{current_label}: {current_bar}{' ' * padding_needed} {current_value}"
    )
    current_content = truncate_text(current_content, target_width - 2)
    current_content = pad_text(current_content, target_width - 2)
    current_line = f"│{current_content}│"
    chart.append(current_line)

    # 最佳连续天数行
    best_bar = "█" * best_blocks + "░" * (bar_length - best_blocks)
    best_value = f"{best_streak}{days_text}"

    best_content = f"{best_label}: {best_bar}{' ' * padding_needed} {best_value}"
    best_content = truncate_text(best_content, target_width - 2)
    best_content = pad_text(best_content, target_width - 2)
    best_line = f"│{best_content}│"
    chart.append(best_line)

    # 底部边框
    bottom_line = "└" + "─" * (target_width - 2) + "┘"
    chart.append(bottom_line)

    # 激励消息
    if current_streak >= best_streak and current_streak > 0:
        message = get_text("creating_new_record")
    elif current_streak >= 7:
        message = get_text("great_persistence")
    elif current_streak >= 3:
        message = get_text("forming_habit")
    elif current_streak >= 1:
        message = get_text("good_start")
    else:
        message = get_text("start_today")

    message_line = pad_text(message, target_width, "center")
    chart.append(message_line)

    return chart
