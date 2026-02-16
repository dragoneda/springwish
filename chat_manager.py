#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import datetime
from database import get_db_connection

class ChatManager:
    def __init__(self):
        pass

    def save_chat(self, contact_id, content):
        """保存聊天记录"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chats (contact_id, content) VALUES (?, ?)', (contact_id, content))
        conn.commit()
        chat_id = cursor.lastrowid
        conn.close()
        return chat_id

    def get_chats_by_contact_id(self, contact_id):
        """获取联系人的聊天记录"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM chats WHERE contact_id = ? ORDER BY timestamp DESC', (contact_id,))
        chats = cursor.fetchall()
        conn.close()
        return chats

    def analyze_chats(self, chats):
        """分析聊天记录（提取关键词和重要事项）"""
        if not chats:
            return {
                'keywords': [],
                'important_matters': [],
                'recent_activities': []
            }

        keywords = []
        important_matters = []
        recent_activities = []

        keyword_patterns = [
            {'pattern': ['工作', '项目', '任务'], 'category': '工作'},
            {'pattern': ['健康', '身体', '生病'], 'category': '健康'},
            {'pattern': ['家庭', '孩子', '父母'], 'category': '家庭'},
            {'pattern': ['学习', '考试', '毕业'], 'category': '学习'},
            {'pattern': ['生日', '节日', '庆祝'], 'category': '节日'},
            {'pattern': ['帮助', '支持', '感谢'], 'category': '情感'},
            {'pattern': ['计划', '目标', '未来'], 'category': '规划'}
        ]

        for chat in chats:
            content = chat['content']
            # 提取关键词
            for pattern in keyword_patterns:
                for word in pattern['pattern']:
                    if word in content and word not in keywords:
                        keywords.append(word)

            # 提取重要事项
            if '重要' in content or '记得' in content or '务必' in content:
                important_matters.append(content)

            # 提取最近活动（一个月内）
            timestamp = datetime.datetime.fromisoformat(chat['timestamp'])
            one_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
            if timestamp > one_month_ago:
                recent_activities.append(content)

        return {
            'keywords': keywords,
            'important_matters': important_matters,
            'recent_activities': recent_activities
        }