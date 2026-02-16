const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// 数据库文件路径
const DB_PATH = path.join(__dirname, 'data', 'wechat.db');

// 初始化数据库
function initDatabase() {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DB_PATH, (err) => {
      if (err) {
        console.error('数据库连接失败:', err);
        reject(err);
      } else {
        console.log('数据库连接成功');
        resolve(db);
      }
    });
  });
}

// 创建表结构
function createTables(db) {
  return new Promise((resolve, reject) => {
    // 联系人表
    const createContactsTable = `
      CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        relation TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `;

    // 聊天记录表
    const createChatsTable = `
      CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
      )
    `;

    // 拜年微信历史表
    const createGreetingsTable = `
      CREATE TABLE IF NOT EXISTS greetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER,
        content TEXT,
        status TEXT DEFAULT 'draft',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
      )
    `;

    // 串行执行表创建
    db.run(createContactsTable, (err) => {
      if (err) {
        console.error('创建 contacts 表失败:', err);
        reject(err);
      } else {
        db.run(createChatsTable, (err) => {
          if (err) {
            console.error('创建 chats 表失败:', err);
            reject(err);
          } else {
            db.run(createGreetingsTable, (err) => {
              if (err) {
                console.error('创建 greetings 表失败:', err);
                reject(err);
              } else {
                console.log('数据库表结构已创建或更新');
                resolve();
              }
            });
          }
        });
      }
    });
  });
}

// 导出数据库操作模块
module.exports = {
  initDatabase,
  createTables,
  DB_PATH
};