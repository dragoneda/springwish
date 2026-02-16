#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 关系类型定义
RELATION_TYPES = {
    'TEACHER': '师生',
    'COLLEAGUE': '同事',
    'SUPERIOR': '上下级',
    'FRIEND': '朋友',
    'FAMILY': '家人',
    'CLASSMATE': '同学',
    'OTHER': '其他'
}

def determine_relation(contact):
    """根据联系人信息判断关系"""
    name = contact.get('name', '')
    notes = contact.get('notes', '').lower()
    relation = contact.get('relation', '')

    if relation:
        return relation

    if '老师' in notes or '导师' in notes:
        return RELATION_TYPES['TEACHER']
    if '同事' in notes or '工作' in notes:
        return RELATION_TYPES['COLLEAGUE']
    if '领导' in notes or '上司' in notes or '下属' in notes:
        return RELATION_TYPES['SUPERIOR']
    if '朋友' in notes or '好友' in notes:
        return RELATION_TYPES['FRIEND']
    if '家人' in notes or '父母' in notes or '子女' in notes or '兄弟姐妹' in notes or '配偶' in notes:
        return RELATION_TYPES['FAMILY']
    if '同学' in notes or '校友' in notes:
        return RELATION_TYPES['CLASSMATE']

    return RELATION_TYPES['OTHER']

def get_title_by_relation(relation, name):
    """根据关系获取称谓"""
    if relation == RELATION_TYPES['TEACHER']:
        return name + '老师' if '老师' not in name else name
    if relation == RELATION_TYPES['SUPERIOR']:
        return name + '总' if '总' not in name and '经理' not in name else name
    if relation == RELATION_TYPES['FAMILY']:
        return name
    return name