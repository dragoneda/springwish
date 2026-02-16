#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
from database import init_database, DB_PATH, get_db_connection
from contact_relation import determine_relation
from chat_manager import ChatManager
from greeting_generator import GreetingGenerator

def test():
    print('=== 拜年微信生成程序测试 ===\n')

    try:
        init_database()

        chat_manager = ChatManager()
        generator = GreetingGenerator()

        print('1. 关系判断测试:')
        test_contacts = [
            {'name': '张老师', 'notes': '我的数学老师'},
            {'name': '李经理', 'notes': '工作上的领导'},
            {'name': '王同事', 'notes': '公司的同事'},
            {'name': '刘同学', 'notes': '大学同学'},
            {'name': '陈朋友', 'notes': '好朋友'},
            {'name': '赵总', 'notes': '部门经理'}
        ]

        for contact in test_contacts:
            relation = determine_relation(contact)
            print(f'   {contact["name"]}: {relation}')

        print('\n2. 添加测试数据到数据库:')
        test_names = ['张老师', '李经理', '王同事', '陈朋友', '刘同学']
        test_relations = ['师生', '上下级', '同事', '朋友', '同学']

        conn = get_db_connection()
        cursor = conn.cursor()
        for i, (name, relation) in enumerate(zip(test_names, test_relations)):
            phone = f'1380013800{i}'
            notes = f'这是我的{relation}，关系很好'
            cursor.execute('INSERT OR IGNORE INTO contacts (name, phone, relation, notes) VALUES (?, ?, ?, ?)',
                          (name, phone, relation, notes))
        conn.commit()

        cursor.execute('SELECT * FROM contacts')
        contacts = cursor.fetchall()
        print(f'   数据库中有 {len(contacts)} 个联系人')

        test_chats = [
            [
                '张老师，我最近在学习Java，遇到了一些问题，您有时间能帮我解答吗？',
                '当然可以，有什么问题随时问我',
                '老师，您推荐的那本书我看完了，收获很大，谢谢！',
                '不客气，学习有什么困难就找我'
            ],
            [
                '李经理，项目进展顺利，预计下周能完成',
                '好的，辛苦大家了',
                '李经理，我们遇到了一个技术难题，需要您的支持',
                '我了解一下情况，明天给你们回复'
            ],
            [
                '王同事，今天的工作进度怎么样？',
                '进展不错，我们已经完成了大部分任务',
                '太好了，我们一起努力',
                '明天我们开个会总结一下'
            ],
            [
                '陈朋友，最近在忙什么？',
                '我在准备考试，压力很大',
                '加油，相信你一定能通过',
                '考完试我们一起出去放松一下'
            ],
            [
                '刘同学，好久不见，最近怎么样？',
                '我刚换了工作，现在在一家科技公司',
                '恭喜你，工作顺利！',
                '有空我们一起聚聚'
            ]
        ]

        for i, contact in enumerate(contacts):
            chats = test_chats[i]
            for content in chats:
                chat_manager.save_chat(contact['id'], content)
        print('   测试聊天记录添加成功')
        conn.close()

        print('\n3. 聊天记录分析测试:')
        for contact in contacts:
            chats = chat_manager.get_chats_by_contact_id(contact['id'])
            print(f'   {contact["name"]}: {len(chats)} 条聊天记录')

        print('\n4. 拜年微信生成测试:')
        for contact in contacts:
            chats = chat_manager.get_chats_by_contact_id(contact['id'])
            greeting = generator.generate_greeting(contact, chats)
            print(f'\n   === 为 {contact["name"]} 生成的拜年微信 ===')
            print(greeting)
            print('')

        print('=== 测试完成 ===')

    except Exception as e:
        print(f'\n❌ 测试过程中出现错误: {e}')
        import traceback
        print(traceback.format_exc())

if __name__ == '__main__':
    test()