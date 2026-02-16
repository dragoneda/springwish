// 联系人关系判断模块

// 关系类型定义
const RELATION_TYPES = {
  TEACHER: '师生',
  COLLEAGUE: '同事',
  SUPERIOR: '上下级',
  FRIEND: '朋友',
  FAMILY: '家人',
  CLASSMATE: '同学',
  OTHER: '其他'
};

// 根据联系人信息判断关系
function determineRelation(contact) {
  const { name, notes, relation } = contact;

  // 如果已经有明确的关系标签，直接返回
  if (relation) {
    return relation;
  }

  // 根据备注信息判断关系
  const lowerNotes = (notes || '').toLowerCase();

  if (lowerNotes.includes('老师') || lowerNotes.includes('导师')) {
    return RELATION_TYPES.TEACHER;
  }

  if (lowerNotes.includes('同事') || lowerNotes.includes('工作')) {
    return RELATION_TYPES.COLLEAGUE;
  }

  if (lowerNotes.includes('领导') || lowerNotes.includes('上司') || lowerNotes.includes('下属')) {
    return RELATION_TYPES.SUPERIOR;
  }

  if (lowerNotes.includes('朋友') || lowerNotes.includes('好友')) {
    return RELATION_TYPES.FRIEND;
  }

  if (lowerNotes.includes('家人') || lowerNotes.includes('父母') || lowerNotes.includes('兄弟姐妹') ||
      lowerNotes.includes('配偶') || lowerNotes.includes('子女')) {
    return RELATION_TYPES.FAMILY;
  }

  if (lowerNotes.includes('同学') || lowerNotes.includes('校友')) {
    return RELATION_TYPES.CLASSMATE;
  }

  return RELATION_TYPES.OTHER;
}

// 获取关系对应的称谓
function getTitleByRelation(relation, name) {
  switch (relation) {
    case RELATION_TYPES.TEACHER:
      return name.includes('老师') ? name : name + '老师';
    case RELATION_TYPES.SUPERIOR:
      return name.includes('总') || name.includes('经理') ? name : name + '总';
    case RELATION_TYPES.FAMILY:
      return name; // 家人通常直接称呼名字或昵称
    case RELATION_TYPES.CLASSMATE:
    case RELATION_TYPES.FRIEND:
    case RELATION_TYPES.COLLEAGUE:
    case RELATION_TYPES.OTHER:
    default:
      return name;
  }
}

module.exports = {
  RELATION_TYPES,
  determineRelation,
  getTitleByRelation
};