#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from database import init_database
from contact_relation import determine_relation
from chat_manager import ChatManager
from greeting_generator import GreetingGenerator
from user_interaction import UserInteraction
from database import get_db_connection

def main():
    ui = UserInteraction()
    chat_manager = ChatManager()
    generator = GreetingGenerator()

    try:
        ui.show_info('正在初始化拜年微信生成程序...')
        init_database()

        menu_options = [
            '查看联系人列表',
            '添加新联系人',
            '查看聊天记录',
            '添加聊天记录',
            '生成拜年微信',
            '退出程序'
        ]

        while True:
            choice = ui.show_menu(menu_options)

            if choice == 0:
                # 查看联系人列表
                show_contacts(ui)
            elif choice == 1:
                # 添加新联系人
                add_contact(ui)
            elif choice == 2:
                # 查看聊天记录
                show_chats(ui, chat_manager)
            elif choice == 3:
                # 添加聊天记录
                add_chat(ui, chat_manager)
            elif choice == 4:
                # 生成拜年微信
                generate_greeting(ui, chat_manager, generator)
            elif choice == 5:
                # 退出程序
                ui.show_success('程序已退出')
                break

    except Exception as e:
        ui.show_error(f'程序错误: {e}')
        import traceback
        print(traceback.format_exc())

def show_contacts(ui):
    """查看联系人列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    conn.close()

    ui.show_info(f'共有 {len(contacts)} 位联系人:')
    for i, contact in enumerate(contacts, 1):
        print(f'\n{i}. {contact["name"]}')
        print(f'   关系: {contact["relation"]}')
        print(f'   电话: {contact["phone"] or "未设置"}')
        print(f'   备注: {contact["notes"] or "无"}')

def add_contact(ui):
    """添加新联系人"""
    name = ui.get_input('请输入联系人姓名: ')
    if not name:
        ui.show_error('姓名不能为空')
        return

    phone = ui.get_input('请输入联系人电话: ')
    notes = ui.get_input('请输入联系人备注: ')

    contact = {'name': name, 'phone': phone, 'notes': notes}
    relation = determine_relation(contact)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO contacts (name, phone, relation, notes) VALUES (?, ?, ?, ?)',
                   (name, phone, relation, notes))
    conn.commit()
    conn.close()

    ui.show_success(f'联系人 "{name}" 已添加，关系: {relation}')

def show_chats(ui, chat_manager):
    """查看聊天记录"""
    name = ui.get_input('请输入联系人姓名: ')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM contacts WHERE name = ?', (name,))
    contact = cursor.fetchone()
    conn.close()

    if not contact:
        ui.show_error(f'未找到联系人 "{name}"')
        return

    chats = chat_manager.get_chats_by_contact_id(contact['id'])
    ui.show_info(f'联系人 "{name}" 的聊天记录 (共 {len(chats)} 条):')
    for i, chat in enumerate(chats, 1):
        time = chat['timestamp']
        print(f'\n{i}. [{time}] {chat["content"]}')

def add_chat(ui, chat_manager):
    """添加聊天记录"""
    name = ui.get_input('请输入联系人姓名: ')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM contacts WHERE name = ?', (name,))
    contact = cursor.fetchone()
    conn.close()

    if not contact:
        ui.show_error(f'未找到联系人 "{name}"')
        return

    content = ui.get_input('请输入聊天内容: ')
    if not content:
        ui.show_error('聊天内容不能为空')
        return

    chat_manager.save_chat(contact['id'], content)
    ui.show_success('聊天记录已添加')

def generate_greeting(ui, chat_manager, generator):
    """生成拜年微信"""
    name = ui.get_input('请输入联系人姓名: ')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE name = ?', (name,))
    contact = cursor.fetchone()
    conn.close()

    if not contact:
        ui.show_error(f'未找到联系人 "{name}"')
        return

    chats = chat_manager.get_chats_by_contact_id(contact['id'])

    greeting = None
    is_satisfied = False
    attempts = 0
    max_attempts = 5

    while not is_satisfied and attempts < max_attempts:
        greeting = generator.generate_greeting(contact, chats)
        is_satisfied = ui.show_greeting_and_get_feedback(greeting, contact['name'])
        attempts += 1

    if is_satisfied:
        ui.show_success('拜年微信已生成并保存')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO greetings (contact_id, content, status) VALUES (?, ?, ?)',
                       (contact['id'], greeting, 'approved'))
        conn.commit()
        conn.close()
    else:
        ui.show_error('已达到最大尝试次数，程序已停止')

if __name__ == '__main__':
    main()