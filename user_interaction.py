#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class UserInteraction:
    def __init__(self):
        pass

    def show_greeting_and_get_feedback(self, greeting, contact_name):
        """显示拜年微信并征求用户意见"""
        print(f"\n=== 为 {contact_name} 生成的拜年微信 ===\n")
        print(greeting)
        print("\n" + "="*40 + "\n")

        while True:
            answer = input('您是否满意这条拜年微信？(y/n): ').strip().lower()
            if answer in ['y', 'yes']:
                return True
            elif answer in ['n', 'no']:
                return False
            else:
                print("无效的选项，请输入 y 或 n")

    def show_info(self, message):
        """显示提示信息"""
        print(f"\nℹ️  {message}")

    def show_success(self, message):
        """显示成功信息"""
        print(f"\n✅ {message}")

    def show_error(self, message):
        """显示错误信息"""
        print(f"\n❌ {message}")

    def show_menu(self, options):
        """显示菜单"""
        print('\n请选择操作：')
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        while True:
            answer = input('请输入选项编号：').strip()
            if answer.isdigit():
                choice = int(answer) - 1
                if 0 <= choice < len(options):
                    return choice
            print('无效的选项，请重新输入')

    def get_input(self, prompt):
        """获取用户输入"""
        return input(prompt).strip()