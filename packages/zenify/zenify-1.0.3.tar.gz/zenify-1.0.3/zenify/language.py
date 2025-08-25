# -*- coding: utf-8 -*-
# language.py

import os
import json
from typing import Dict, Any


class LanguageManager:
    """Multi-language support for Zenify"""

    def __init__(self):
        self.current_language = "zh"  # Default to Chinese
        self.supported_languages = ["zh", "en", "ja"]
        self.language_names = {"zh": "中文", "en": "English", "ja": "日本語"}
        self.translations = self._load_translations()

    def _load_translations(self) -> Dict[str, Dict[str, Any]]:
        """Load all translations"""
        return {
            "zh": {
                # Menu items
                "mode": "模式",
                "breathing_method": "呼吸法",
                "duration_min": "时长(分钟)",
                "view_stats": "查看统计",
                "detailed_analysis": "详细分析",
                "start_practice": "开始练习",
                "language": "语言",
                "graphics": "图形",
                # Modes
                "graphical_mode": "图形模式",
                "progress_bar_mode": "进度条模式",
                # Shapes
                "diamond": "钻石",
                "star": "星辰",
                "wave_flow": "流水",
                "tree": "大树",
                "crystal": "水晶",
                "infinity": "无限",
                "mandala": "曼陀罗",
                "labyrinth": "迷宫",
                "yin_yang": "阴阳",
                "spiral": "螺旋",
                "zen_circle": "禅圆",
                "unknown": "未知",
                # Breathing phases
                "inhale": "吸气",
                "hold": "屏息",
                "exhale": "呼气",
                "hold_post": "屏息",
                # Controls
                "controls_help": "[↑/↓] 选择, [←/→] 编辑, [Enter] 确定/开始, [Space] 快速开始, [q] 退出",
                "pause_continue": "[p] 暂停/继续",
                "return_menu": "[m] 返回菜单",
                "quit": "[q] 退出",
                "navigation": "[←/→] 切换图表  [Enter] 返回菜单",
                # Session
                "session_start": "=== 呼吸练习开始 ===",
                "session_controls": "控制键: [p]暂停/继续  [m]返回菜单  [q]退出并总结",
                "paused": "已暂停",
                "continue_practice": "按 [p] 继续练习",
                "interrupted": "练习被中断",
                "practice_complete": "练习结束",
                "resume": "继续练习...",
                "session_summary": "练习总结",
                "cycle_completed": "完成一轮",
                # Breathing guidance
                "breathe_in_slowly": "慢慢吸气...",
                "breathe_out_slowly": "缓缓呼气...",
                "hold_breath": "保持屏息...",
                # Stats
                "statistics": "练习统计",
                "detailed_stats": "详细统计分析",
                "session_duration": "本次练习时长",
                "breathing_cycles": "呼吸循环次数",
                "total_duration": "累计练习时长",
                "total_practice_time": "总练习时长",
                "total_sessions": "总练习次数",
                "average_duration": "平均每次时长",
                "most_used_mode": "最常用模式",
                "current_streak": "当前连续天数",
                "best_streak": "    最佳记录",
                "minutes": "分钟",
                "seconds": "秒",
                "hours": "小时",
                "days": "天",
                "times": "次",
                "na": "N/A",
                # Charts
                "monthly_duration": "月度练习时长",
                "time_distribution": "练习时段分布",
                "practice_calendar": "练习日历",
                "practice_heatmap": "练习热力图",
                "streak_progress": "连续记录",
                "no_data": "暂无数据",
                "no_enough_data": "暂无足够数据生成图表",
                "start_practice_to_view": "开始练习以查看统计分析",
                # Time periods
                "morning": "上午",
                "afternoon": "下午",
                "evening": "晚上",
                "night": "深夜",
                # Days of week
                "monday": "周一",
                "tuesday": "周二",
                "wednesday": "周三",
                "thursday": "周四",
                "friday": "周五",
                "saturday": "周六",
                "sunday": "周日",
                # Messages
                "app_exit": "Zenify 已退出。",
                "peaceful_day": "祝您有平静的一天。",
                "press_any_key": "按任意键退出",
                "press_any_key_menu": "按任意键返回菜单",
                "creating_new_record": "🎉 创造新记录！",
                "great_persistence": "💪 坚持得很好！",
                "forming_habit": "👍 养成好习惯！",
                "good_start": "🌱 好的开始！",
                "start_today": "🎯 今天开始练习吧！",
                # Progress indicators
                "10plus_minutes": "10+分钟",
                "5plus_minutes": "5+分钟",
                "under_5_minutes": "<5分钟",
                "no_practice": "未练习",
                # Presets
                "4-7-8_breathing": "4-7-8呼吸 (放松)",
                "box_breathing": "盒子呼吸 (专注)",
                "custom": "自定义",
                # Shape styles
                "diamond": "钻石图案",
                "star": "星辰图案",
                "wave_flow": "流水图案",
                "tree": "大树图案",
                "crystal": "水晶图案",
                "infinity": "无限图案",
                "mandala": "曼陀罗图案",
                "labyrinth": "迷宫图案",
                "yin_yang": "阴阳图案",
                "style": "样式",
            },
            "en": {
                # Menu items
                "mode": "Mode",
                "breathing_method": "Breathing Method",
                "duration_min": "Duration (min)",
                "view_stats": "View Stats",
                "detailed_analysis": "Detailed Analysis",
                "start_practice": "Start Practice",
                "language": "Language",
                "graphics": "Graphics",
                # Modes
                "graphical_mode": "Graphical Mode",
                "progress_bar_mode": "Progress Bar Mode",
                # Shapes
                "diamond": "Diamond",
                "star": "Star",
                "wave_flow": "Wave Flow",
                "tree": "Tree",
                "crystal": "Crystal",
                "infinity": "Infinity",
                "mandala": "Mandala",
                "labyrinth": "Labyrinth",
                "yin_yang": "Yin Yang",
                "spiral": "Spiral",
                "zen_circle": "Zen Circle",
                "unknown": "Unknown",
                # Breathing phases
                "inhale": "Inhale",
                "hold": "Hold",
                "exhale": "Exhale",
                "hold_post": "Hold",
                # Controls
                "controls_help": "[↑/↓] Select, [←/→] Edit, [Enter] Confirm/Start, [Space] Quick Start, [q] Quit",
                "pause_continue": "[p] Pause/Continue",
                "return_menu": "[m] Return to Menu",
                "quit": "[q] Quit",
                "navigation": "[←/→] Switch Charts  [Enter] Return to Menu",
                # Session
                "session_start": "=== Breathing Practice Started ===",
                "session_controls": "Controls: [p]Pause/Continue  [m]Return to Menu  [q]Quit & Summary",
                "paused": "Paused",
                "continue_practice": "Press [p] to Continue",
                "interrupted": "Practice Interrupted",
                "practice_complete": "Practice Complete",
                "resume": "Resuming practice...",
                "session_summary": "Session Summary",
                "cycle_completed": "Cycle Completed",
                # Breathing guidance
                "breathe_in_slowly": "Breathe in slowly...",
                "breathe_out_slowly": "Breathe out slowly...",
                "hold_breath": "Hold your breath...",
                # Stats
                "statistics": "Practice Statistics",
                "detailed_stats": "Detailed Statistical Analysis",
                "session_duration": "Session Duration",
                "breathing_cycles": "Breathing Cycles",
                "total_duration": "Total Practice Time",
                "total_practice_time": "Total Practice Duration",
                "total_sessions": "Total Sessions",
                "average_duration": "Average Duration",
                "most_used_mode": "Most Used Mode",
                "current_streak": "Current Streak",
                "best_streak": "   Best Record",
                "minutes": "minutes",
                "seconds": "seconds",
                "hours": "hours",
                "days": "days",
                "times": "times",
                "na": "N/A",
                # Charts
                "monthly_duration": "Monthly Practice Duration",
                "time_distribution": "Time Distribution",
                "practice_calendar": "Practice Calendar",
                "practice_heatmap": "Practice Heatmap",
                "streak_progress": "Streak Progress",
                "no_data": "No Data",
                "no_enough_data": "Not enough data to generate charts",
                "start_practice_to_view": "Start practicing to view statistical analysis",
                # Time periods
                "morning": "Morning",
                "afternoon": "Afternoon",
                "evening": "Evening",
                "night": "Night",
                # Days of week
                "monday": "Mon",
                "tuesday": "Tue",
                "wednesday": "Wed",
                "thursday": "Thu",
                "friday": "Fri",
                "saturday": "Sat",
                "sunday": "Sun",
                # Messages
                "app_exit": "Zenify has exited.",
                "peaceful_day": "Have a peaceful day.",
                "press_any_key": "Press any key to exit",
                "press_any_key_menu": "Press any key to return to menu",
                "creating_new_record": "🎉 New Record Created!",
                "great_persistence": "💪 Great Persistence!",
                "forming_habit": "👍 Forming Good Habits!",
                "good_start": "🌱 Good Start!",
                "start_today": "🎯 Start Practicing Today!",
                # Progress indicators
                "10plus_minutes": "10+ min",
                "5plus_minutes": "5+ min",
                "under_5_minutes": "<5 min",
                "no_practice": "No practice",
                # Presets
                "4-7-8_breathing": "4-7-8 Breathing (Relax)",
                "box_breathing": "Box Breathing (Focus)",
                "custom": "Custom",
                # Shape styles
                "diamond": "Diamond",
                "star": "Star",
                "wave_flow": "Wave Flow",
                "tree": "Tree",
                "crystal": "Crystal",
                "infinity": "Infinity",
                "mandala": "Mandala",
                "labyrinth": "Labyrinth",
                "yin_yang": "Yin Yang",
                "style": "Style",
            },
            "ja": {
                # Menu items
                "mode": "モード",
                "breathing_method": "呼吸法",
                "duration_min": "時間(分)",
                "view_stats": "統計を見る",
                "detailed_analysis": "詳細分析",
                "start_practice": "練習開始",
                "language": "言語",
                "graphics": "グラフィック",
                # Modes
                "graphical_mode": "グラフィカルモード",
                "progress_bar_mode": "プログレスバーモード",
                # Shapes
                "diamond": "ダイヤモンド",
                "star": "星",
                "wave_flow": "流れ",
                "tree": "木",
                "crystal": "クリスタル",
                "infinity": "無限",
                "mandala": "マンダラ",
                "labyrinth": "迷宮",
                "yin_yang": "陰陽",
                "spiral": "螺旋",
                "zen_circle": "禅円",
                "unknown": "不明",
                # Breathing phases
                "inhale": "吸気",
                "hold": "息止め",
                "exhale": "呼気",
                "hold_post": "息止め",
                # Controls
                "controls_help": "[↑/↓] 選択, [←/→] 編集, [Enter] 確定/開始, [Space] クイック開始, [q] 終了",
                "pause_continue": "[p] 一時停止/続行",
                "return_menu": "[m] メニューに戻る",
                "quit": "[q] 終了",
                "navigation": "[←/→] チャート切替  [Enter] メニューに戻る",
                # Session
                "session_start": "=== 呼吸練習開始 ===",
                "session_controls": "操作: [p]一時停止/続行  [m]メニューに戻る  [q]終了＆まとめ",
                "paused": "一時停止中",
                "continue_practice": "[p] を押して続行",
                "interrupted": "練習が中断されました",
                "practice_complete": "練習完了",
                "resume": "練習を再開します...",
                "session_summary": "セッション要約",
                "cycle_completed": "サイクル完了",
                # Breathing guidance
                "breathe_in_slowly": "ゆっくり息を吸って...",
                "breathe_out_slowly": "ゆっくり息を吐いて...",
                "hold_breath": "息を止めて...",
                # Stats
                "statistics": "練習統計",
                "detailed_stats": "詳細統計分析",
                "session_duration": "セッション時間",
                "breathing_cycles": "呼吸サイクル数",
                "total_duration": "総練習時間",
                "total_practice_time": "総練習時間",
                "total_sessions": "総セッション数",
                "average_duration": "平均時間",
                "most_used_mode": "最もよく使うモード",
                "current_streak": "現在の連続日数",
                "best_streak": "      最高記録",
                "minutes": "分",
                "seconds": "秒",
                "hours": "時間",
                "days": "日",
                "times": "回",
                "na": "N/A",
                # Charts
                "monthly_duration": "月間練習時間",
                "time_distribution": "時間分布",
                "practice_calendar": "練習カレンダー",
                "practice_heatmap": "練習ヒートマップ",
                "streak_progress": "連続記録",
                "no_data": "データなし",
                "no_enough_data": "チャートを生成するのに十分なデータがありません",
                "start_practice_to_view": "統計分析を見るには練習を開始してください",
                # Time periods
                "morning": "朝",
                "afternoon": "午後",
                "evening": "夕方",
                "night": "夜",
                # Days of week
                "monday": "月",
                "tuesday": "火",
                "wednesday": "水",
                "thursday": "木",
                "friday": "金",
                "saturday": "土",
                "sunday": "日",
                # Messages
                "app_exit": "Zenifyを終了しました。",
                "peaceful_day": "穏やかな一日をお過ごしください。",
                "press_any_key": "任意のキーを押して終了",
                "press_any_key_menu": "任意のキーを押してメニューに戻る",
                "creating_new_record": "🎉 新記録達成！",
                "great_persistence": "💪 素晴らしい継続力！",
                "forming_habit": "👍 良い習慣を築いています！",
                "good_start": "🌱 良いスタート！",
                "start_today": "🎯 今日から練習を始めましょう！",
                # Progress indicators
                "10plus_minutes": "10分以上",
                "5plus_minutes": "5分以上",
                "under_5_minutes": "5分未満",
                "no_practice": "未練習",
                # Presets
                "4-7-8_breathing": "4-7-8呼吸法 (リラックス)",
                "box_breathing": "ボックス呼吸法 (集中)",
                "custom": "カスタム",
                # Shape styles
                "diamond": "ダイヤモンド",
                "star": "星",
                "wave_flow": "流れ",
                "tree": "木",
                "crystal": "クリスタル",
                "infinity": "無限",
                "mandala": "マンダラ",
                "labyrinth": "迷宮",
                "yin_yang": "陰陽",
                "style": "スタイル",
            },
        }

    def set_language(self, lang_code: str):
        """Set current language"""
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            self.save_language_preference()

    def get_text(self, key: str, default: str = None) -> str:
        """Get translated text for current language"""
        if default is None:
            default = key

        return self.translations.get(self.current_language, {}).get(key, default)

    def get_language_name(self, lang_code: str = None) -> str:
        """Get language display name"""
        if lang_code is None:
            lang_code = self.current_language
        return self.language_names.get(lang_code, lang_code)

    def get_supported_languages(self) -> list:
        """Get list of supported language codes"""
        return self.supported_languages

    def get_language_options(self) -> list:
        """Get list of (code, name) tuples for language selection"""
        return [(code, self.language_names[code]) for code in self.supported_languages]

    def save_language_preference(self):
        """Save language preference to file"""
        try:
            with open("zenify_language.txt", "w") as f:
                f.write(self.current_language)
        except IOError:
            pass  # Fail silently

    def load_language_preference(self):
        """Load language preference from file"""
        try:
            if os.path.exists("zenify_language.txt"):
                with open("zenify_language.txt", "r") as f:
                    lang = f.read().strip()
                    if lang in self.supported_languages:
                        self.current_language = lang
        except IOError:
            pass  # Fail silently


# Global language manager instance
lang = LanguageManager()
lang.load_language_preference()


def get_text(key: str, default: str = None) -> str:
    """Convenience function to get translated text"""
    return lang.get_text(key, default)


def load_language_preference() -> str:
    """Load and return current language preference"""
    lang.load_language_preference()
    return lang.current_language


def save_language_preference(lang_code: str):
    """Save language preference"""
    lang.set_language(lang_code)


def get_language_strings(lang_code: str) -> Dict[str, str]:
    """Get all language strings for a specific language"""
    return lang.translations.get(lang_code, lang.translations["zh"])
