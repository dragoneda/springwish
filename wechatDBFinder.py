#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import sys

class WeChatDBFinder:
    """微信数据库查找器"""

    def __init__(self):
        self.platform = platform.system()
        self.wechat_db_paths = self.get_wechat_db_paths()

    def get_wechat_db_paths(self):
        """根据操作系统获取微信数据库可能的路径"""
        paths = []
        user_home = os.path.expanduser('~')

        if self.platform == 'Windows':
            # Windows 平台微信数据库路径
            wechat_dir = os.path.join(user_home, 'Documents', 'WeChat Files')
            if os.path.exists(wechat_dir):
                for wechat_id in os.listdir(wechat_dir):
                    msg_dir = os.path.join(wechat_dir, wechat_id, 'Msg')
                    if os.path.exists(msg_dir):
                        for msg_file in os.listdir(msg_dir):
                            if msg_file.endswith('.db'):
                                paths.append(os.path.join(msg_dir, msg_file))
        elif self.platform == 'Darwin':  # macOS
            # macOS 平台微信数据库路径
            library_dir = os.path.join(user_home, 'Library', 'Containers', 'com.tencent.xinWeChat', 'Data', 'Library', 'Application Support', 'com.tencent.xinWeChat')
            if os.path.exists(library_dir):
                for version in os.listdir(library_dir):
                    version_dir = os.path.join(library_dir, version)
                    if os.path.isdir(version_dir):
                        for wechat_id in os.listdir(version_dir):
                            message_dir = os.path.join(version_dir, wechat_id, 'Message')
                            if os.path.exists(message_dir):
                                for msg_file in os.listdir(message_dir):
                                    if msg_file.endswith('.db'):
                                        paths.append(os.path.join(message_dir, msg_file))
        elif self.platform == 'Linux':
            # Linux 平台微信数据库路径
            wechat_dir = os.path.join(user_home, '.wine', 'drive_c', 'users', os.path.basename(user_home), 'Documents', 'WeChat Files')
            if os.path.exists(wechat_dir):
                for wechat_id in os.listdir(wechat_dir):
                    msg_dir = os.path.join(wechat_dir, wechat_id, 'Msg')
                    if os.path.exists(msg_dir):
                        for msg_file in os.listdir(msg_dir):
                            if msg_file.endswith('.db'):
                                paths.append(os.path.join(msg_dir, msg_file))
        else:
            print(f"未支持的操作系统: {self.platform}")

        return paths

    def find_contacts_db(self):
        """查找联系人数据库"""
        print("正在查找微信联系人数据库...")
        contact_db_paths = []
        for db_path in self.wechat_db_paths:
            if 'MSG' in os.path.basename(db_path) or 'Contact' in os.path.basename(db_path) or 'EnMicroMsg' in os.path.basename(db_path):
                contact_db_paths.append(db_path)

        if contact_db_paths:
            print(f"找到 {len(contact_db_paths)} 个可能的微信数据库:")
            for i, db_path in enumerate(contact_db_paths, 1):
                print(f"{i}. {db_path}")
            return contact_db_paths
        else:
            print("未找到微信联系人数据库")
            return None

    def verify_db(self, db_path):
        """验证数据库文件是否为微信数据库"""
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 尝试查询常见的微信表
            common_tables = ['contact', 'user', 'chat', 'message', 'rcontact']
            tables = []
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            for row in cursor.fetchall():
                table_name = row[0]
                for common_name in common_tables:
                    if common_name.lower() in table_name.lower():
                        tables.append(table_name)

            conn.close()
            return len(tables) > 0
        except Exception as e:
            print(f"验证数据库失败: {e}")
            return False

    def extract_contacts(self, db_path):
        """从微信数据库中提取联系人信息（针对微信电脑版 MSG.db 优化）"""
        print(f"正在从数据库中提取联系人信息: {db_path}")

        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 查找联系人表（微信电脑版通常使用 rcontact 表）
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            contact_table = None
            for row in cursor.fetchall():
                table_name = row[0]
                if 'rcontact' in table_name.lower():
                    contact_table = table_name
                    break

            if not contact_table:
                print("未找到 rcontact 表")
                conn.close()
                return None

            print(f"联系人表: {contact_table}")

            # 读取联系人表字段
            cursor.execute(f"PRAGMA table_info({contact_table})")
            columns = [column[1] for column in cursor.fetchall()]

            print("联系人表字段:")
            for i, column in enumerate(columns, 1):
                print(f"{i}. {column}")

            # 查询所有联系人记录
            cursor.execute(f"SELECT * FROM {contact_table}")
            contacts = cursor.fetchall()
            print(f"\n查询到 {len(contacts)} 位联系人:")

            extracted_contacts = []

            for i, contact in enumerate(contacts, 1):
                # 分析微信电脑版 rcontact 表字段
                name = ""
                alias = ""
                remark = ""

                try:
                    # 根据微信电脑版数据库字段结构提取信息
                    if "NickName" in columns:
                        name_idx = columns.index("NickName")
                        if name_idx < len(contact):
                            name = str(contact[name_idx])
                    if "Alias" in columns:
                        alias_idx = columns.index("Alias")
                        if alias_idx < len(contact):
                            alias = str(contact[alias_idx])
                    if "Remark" in columns:
                        remark_idx = columns.index("Remark")
                        if remark_idx < len(contact):
                            remark = str(contact[remark_idx])

                    # 确定显示名称
                    display_name = remark if remark else name if name else alias if alias else "未知"

                    # 输出信息
                    contact_info = f"{i}. {display_name}"
                    if (name or alias) and remark and name != remark and alias != remark:
                        contact_info += f" ({name or alias})"

                    print(contact_info)

                    extracted_contacts.append({
                        "nickname": name,
                        "alias": alias,
                        "remark": remark,
                        "display_name": display_name
                    })
                except Exception as e:
                    print(f"分析联系人 {i} 时出错: {e}")

            conn.close()

            return {
                'table_name': contact_table,
                'columns': columns,
                'contacts': extracted_contacts
            }

        except Exception as e:
            print(f"提取联系人信息失败: {e}")
            return None

    def find_chat_records(self, db_path):
        """从微信数据库中提取聊天记录"""
        print(f"正在从数据库中提取聊天记录: {db_path}")

        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 查找聊天记录相关的表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            chat_tables = []
            for row in cursor.fetchall():
                table_name = row[0]
                if 'message' in table_name.lower() or 'msg' in table_name.lower() or 'chat' in table_name.lower():
                    chat_tables.append(table_name)

            if not chat_tables:
                print("未找到聊天记录相关的表")
                conn.close()
                return None

            print(f"找到 {len(chat_tables)} 个聊天记录相关的表:")
            for i, table_name in enumerate(chat_tables, 1):
                print(f"{i}. {table_name}")

            # 读取第一个表的信息
            first_table = chat_tables[0]
            cursor.execute(f"PRAGMA table_info({first_table})")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"\n表 '{first_table}' 的字段:")
            for i, column in enumerate(columns, 1):
                print(f"{i}. {column}")

            # 尝试查询聊天记录数据
            cursor.execute(f"SELECT * FROM {first_table} LIMIT 10")
            records = cursor.fetchall()
            print(f"\n查询到 {len(records)} 条聊天记录:")
            for i, record in enumerate(records, 1):
                print(f"{i}. {record}")

            conn.close()

            return {
                'tables': chat_tables,
                'first_table': first_table,
                'columns': columns,
                'records': records
            }

        except Exception as e:
            print(f"提取聊天记录失败: {e}")
            return None


def test_wechat_db_finder():
    finder = WeChatDBFinder()
    contact_db_paths = finder.find_contacts_db()

    if contact_db_paths:
        # 选择第一个数据库进行验证和读取
        db_path = contact_db_paths[0]

        # 验证数据库
        if finder.verify_db(db_path):
            print("\n数据库验证成功")
        else:
            print("\n数据库验证失败")
            return

        # 提取联系人信息
        print("\n=== 提取联系人信息 ===")
        contacts_data = finder.extract_contacts(db_path)
        if contacts_data:
            print("联系人信息提取成功")
        else:
            print("联系人信息提取失败")

        # 提取聊天记录
        print("\n=== 提取聊天记录 ===")
        chat_records = finder.find_chat_records(db_path)
        if chat_records:
            print("聊天记录提取成功")
        else:
            print("聊天记录提取失败")

    else:
        print("未找到微信数据库")


if __name__ == '__main__':
    test_wechat_db_finder()