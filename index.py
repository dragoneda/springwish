#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from database import init_database
from contact_relation import determine_relation
from chat_manager import ChatManager
from greeting_generator import GreetingGenerator
from user_interaction import UserInteraction
from database import get_db_connection
from wechatDBFinder import WeChatDBFinder

def main():
    ui = UserInteraction()
    chat_manager = ChatManager()
    generator = GreetingGenerator()

    try:
        ui.show_info('正在初始化拜年微信生成程序...')

        # 首先查找微信数据库
        finder = WeChatDBFinder()
        contact_db_paths = finder.find_contacts_db()
        if contact_db_paths:
            ui.show_success(f"找到 {len(contact_db_paths)} 个微信数据库文件")
            # 可以选择一个数据库进行读取
            db_path = contact_db_paths[0]
            if finder.verify_db(db_path):
                ui.show_success("数据库验证成功")
                # 尝试提取联系人信息
                contacts_data = finder.extract_contacts(db_path)
                if contacts_data:
                    ui.show_success(f"成功提取 {len(contacts_data['contacts'])} 位联系人信息")
                    # 打印所有联系人信息
                    print("\n=== 微信联系人列表 ===")
                    for i, contact in enumerate(contacts_data['contacts']):
                        contact_info = ""
                        if len(contacts_data['columns']) > 0:
                            # 查找姓名字段
                            name_idx = -1
                            notes_idx = -1
                            for j, col in enumerate(contacts_data['columns']):
                                col_lower = col.lower()
                                if 'nick' in col_lower or 'name' in col_lower:
                                    name_idx = j
                                elif 'remark' in col_lower or 'notes' in col_lower:
                                    notes_idx = j

                            name = str(contact[name_idx]) if name_idx != -1 and name_idx < len(contact) else str(contact[1]) if len(contact) > 1 else "未知"
                            notes = str(contact[notes_idx]) if notes_idx != -1 and notes_idx < len(contact) else ""

                            contact_info = f"{i+1}. {name}"
                            if notes and notes != name:
                                contact_info += f" ({notes})"

                        print(contact_info)
                    # 将联系人信息导入到本地数据库
                    import_contacts_from_wechat(contacts_data['contacts'])
            else:
                ui.show_error("数据库验证失败")
        else:
            ui.show_info("未找到微信数据库，使用本地数据库")

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

def import_contacts_from_wechat(wechat_contacts):
    """从微信数据库导入联系人到本地数据库"""
    if not wechat_contacts:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    added_count = 0
    for contact in wechat_contacts:
        # 提取联系人姓名和备注
        name = ''
        notes = ''
        try:
            # 这取决于微信数据库的字段结构，这里只是示例
            # 实际需要根据微信数据库的字段进行调整
            if len(contact) > 1:
                name = str(contact[1])
            if len(contact) > 2:
                notes = str(contact[2])

            if name:
                cursor.execute('SELECT id FROM contacts WHERE name = ?', (name,))
                existing_contact = cursor.fetchone()
                if not existing_contact:
                    # 自动判断关系
                    import_cont = {'name': name, 'notes': notes}
                    relation = determine_relation(import_cont)
                    cursor.execute('INSERT INTO contacts (name, phone, relation, notes) VALUES (?, ?, ?, ?)',
                                  (name, '', relation, notes))
                    added_count += 1
        except Exception as e:
            print(f"导入联系人 '{name}' 时出错: {e}")

    conn.commit()
    conn.close()

    if added_count > 0:
        print(f"成功导入 {added_count} 位联系人到本地数据库")

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