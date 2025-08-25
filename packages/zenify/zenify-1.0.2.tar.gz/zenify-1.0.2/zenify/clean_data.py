#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data cleaning utility for Zenify meditation app
清理异常数据的工具
"""

import csv
import shutil
from datetime import datetime

def clean_zenify_data():
    """清理zenify_log.csv中的异常数据"""
    input_file = "zenify_log.csv"
    backup_file = "zenify_log_backup.csv"
    
    # 备份原文件
    try:
        shutil.copy(input_file, backup_file)
        print(f"已备份原数据到: {backup_file}")
    except FileNotFoundError:
        print(f"文件 {input_file} 不存在")
        return
    
    cleaned_rows = []
    removed_count = 0
    total_removed_duration = 0
    
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            duration = int(row.get('duration_sec', 0))
            
            # 移除超过10分钟(600秒)的异常记录
            if duration > 600:
                print(f"移除异常记录: {duration}秒 ({duration//60}分钟) - {row['timestamp']}")
                removed_count += 1
                total_removed_duration += duration
            else:
                cleaned_rows.append(row)
    
    # 写入清理后的数据
    with open(input_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)
    
    print(f"\n清理完成:")
    print(f"  移除记录数: {removed_count}")
    print(f"  移除总时长: {total_removed_duration}秒 ({total_removed_duration//60}分钟)")
    print(f"  保留记录数: {len(cleaned_rows)}")
    
    # 计算清理后的总时长
    new_total_duration = sum(int(row.get('duration_sec', 0)) for row in cleaned_rows)
    print(f"  新的总时长: {new_total_duration}秒 ({new_total_duration//60}分钟 {new_total_duration%60}秒)")
    print(f"  新的总时长: {new_total_duration//3600}小时 {(new_total_duration%3600)//60}分钟")

if __name__ == "__main__":
    clean_zenify_data()