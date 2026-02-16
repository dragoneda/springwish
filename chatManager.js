// 聊天记录管理模块
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { DB_PATH } = require('./database');

class ChatManager {
  constructor() {
    this.db = new sqlite3.Database(DB_PATH);
  }

  // 保存聊天记录
  async saveChat(contactId, content) {
    return new Promise((resolve, reject) => {
      const sql = `INSERT INTO chats (contact_id, content) VALUES (?, ?)`;
      this.db.run(sql, [contactId, content], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve(this.lastID);
        }
      });
    });
  }

  // 获取联系人的聊天记录
  async getChatsByContactId(contactId) {
    return new Promise((resolve, reject) => {
      const sql = `SELECT * FROM chats WHERE contact_id = ? ORDER BY timestamp DESC`;
      this.db.all(sql, [contactId], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // 分析聊天记录（提取关键词和重要事项）
  analyzeChats(chats) {
    if (!chats || chats.length === 0) {
      return {
        keywords: [],
        importantMatters: [],
        recentActivities: []
      };
    }

    // 简单的关键词提取（可以根据需要扩展）
    const keywords = [];
    const importantMatters = [];
    const recentActivities = [];

    // 关键词列表
    const KEYWORD_PATTERNS = [
      { pattern: /(工作|项目|任务)/g, category: '工作' },
      { pattern: /(健康|身体|生病)/g, category: '健康' },
      { pattern: /(家庭|孩子|父母)/g, category: '家庭' },
      { pattern: /(学习|考试|毕业)/g, category: '学习' },
      { pattern: /(生日|节日|庆祝)/g, category: '节日' },
      { pattern: /(帮助|支持|感谢)/g, category: '情感' },
      { pattern: /(计划|目标|未来)/g, category: '规划' }
    ];

    chats.forEach(chat => {
      // 查找关键词
      KEYWORD_PATTERNS.forEach(({ pattern, category }) => {
        const matches = chat.content.match(pattern);
        if (matches) {
          matches.forEach(match => {
            if (!keywords.includes(match)) {
              keywords.push(match);
            }
          });
        }
      });

      // 提取重要事项（包含特定关键词的消息）
      if (chat.content.includes('重要') || chat.content.includes('记得') || chat.content.includes('务必')) {
        importantMatters.push(chat.content);
      }

      // 最近的活动（比如最近一个月的消息）
      const oneMonthAgo = Date.now() - 30 * 24 * 60 * 60 * 1000;
      if (new Date(chat.timestamp).getTime() > oneMonthAgo) {
        recentActivities.push(chat.content);
      }
    });

    return {
      keywords,
      importantMatters,
      recentActivities
    };
  }

  // 关闭数据库连接
  close() {
    this.db.close();
  }
}

module.exports = ChatManager;