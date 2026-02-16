#!/usr/bin/env node
// 主程序入口

const { initDatabase, createTables } = require('./database');
const { determineRelation, RELATION_TYPES } = require('./contactRelation');
const ChatManager = require('./chatManager');
const GreetingGenerator = require('./greetingGenerator');
const UserInteraction = require('./userInteraction');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = path.join(__dirname, 'data', 'wechat.db');

async function main() {
  const ui = new UserInteraction();
  const chatManager = new ChatManager();
  const generator = new GreetingGenerator();

  try {
    ui.showInfo('正在初始化拜年微信生成程序...');

    // 初始化数据库
    const db = await initDatabase();
    await createTables(db);

    // 显示菜单
    const menuOptions = [
      '查看联系人列表',
      '添加新联系人',
      '查看聊天记录',
      '添加聊天记录',
      '生成拜年微信',
      '退出程序'
    ];

    while (true) {
      const choice = await ui.showMenu(menuOptions);

      switch (choice) {
        case 0:
          // 查看联系人列表
          await showContacts(db, ui);
          break;
        case 1:
          // 添加新联系人
          await addContact(db, ui);
          break;
        case 2:
          // 查看聊天记录
          await showChats(db, ui, chatManager);
          break;
        case 3:
          // 添加聊天记录
          await addChat(db, ui, chatManager);
          break;
        case 4:
          // 生成拜年微信
          await generateGreeting(db, ui, chatManager, generator);
          break;
        case 5:
          // 退出程序
          ui.showSuccess('程序已退出');
          db.close();
          chatManager.close();
          ui.close();
          return;
      }
    }
  } catch (error) {
    ui.showError(`程序错误: ${error.message}`);
    console.error(error.stack);
    ui.close();
  }
}

// 查看联系人列表
async function showContacts(db, ui) {
  return new Promise((resolve, reject) => {
    const sql = 'SELECT * FROM contacts';
    db.all(sql, (err, rows) => {
      if (err) {
        ui.showError(`查询失败: ${err.message}`);
        reject(err);
      } else {
        ui.showInfo(`共有 ${rows.length} 位联系人:`);
        rows.forEach((contact, index) => {
          console.log(`\n${index + 1}. ${contact.name}`);
          console.log(`   关系: ${contact.relation}`);
          console.log(`   电话: ${contact.phone || '未设置'}`);
          console.log(`   备注: ${contact.notes || '无'}`);
        });
        resolve();
      }
    });
  });
}

// 添加新联系人
async function addContact(db, ui) {
  return new Promise((resolve, reject) => {
    ui.getInput('请输入联系人姓名: ').then(async (name) => {
      const phone = await ui.getInput('请输入联系人电话: ');
      const notes = await ui.getInput('请输入联系人备注: ');

      // 自动判断关系
      const contact = { name, phone, notes };
      const relation = determineRelation(contact);

      const sql = 'INSERT INTO contacts (name, phone, relation, notes) VALUES (?, ?, ?, ?)';
      db.run(sql, [name, phone, relation, notes], function(err) {
        if (err) {
          ui.showError(`添加失败: ${err.message}`);
          reject(err);
        } else {
          ui.showSuccess(`联系人 "${name}" 已添加，关系: ${relation}`);
          resolve(this.lastID);
        }
      });
    });
  });
}

// 查看聊天记录
async function showChats(db, ui, chatManager) {
  return new Promise((resolve, reject) => {
    ui.getInput('请输入联系人姓名: ').then(async (name) => {
      const sql = 'SELECT id FROM contacts WHERE name = ?';
      db.get(sql, [name], async (err, row) => {
        if (err) {
          ui.showError(`查询失败: ${err.message}`);
          reject(err);
        } else if (!row) {
          ui.showError(`未找到联系人 "${name}"`);
          resolve();
        } else {
          const chats = await chatManager.getChatsByContactId(row.id);
          ui.showInfo(`联系人 "${name}" 的聊天记录 (共 ${chats.length} 条):`);
          chats.forEach((chat, index) => {
            const time = new Date(chat.timestamp).toLocaleString();
            console.log(`\n${index + 1}. [${time}] ${chat.content}`);
          });
          resolve();
        }
      });
    });
  });
}

// 添加聊天记录
async function addChat(db, ui, chatManager) {
  return new Promise((resolve, reject) => {
    ui.getInput('请输入联系人姓名: ').then(async (name) => {
      const sql = 'SELECT id FROM contacts WHERE name = ?';
      db.get(sql, [name], async (err, row) => {
        if (err) {
          ui.showError(`查询失败: ${err.message}`);
          reject(err);
        } else if (!row) {
          ui.showError(`未找到联系人 "${name}"`);
          resolve();
        } else {
          const content = await ui.getInput('请输入聊天内容: ');
          const chatId = await chatManager.saveChat(row.id, content);
          ui.showSuccess('聊天记录已添加');
          resolve(chatId);
        }
      });
    });
  });
}

// 生成拜年微信
async function generateGreeting(db, ui, chatManager, generator) {
  return new Promise((resolve, reject) => {
    ui.getInput('请输入联系人姓名: ').then(async (name) => {
      const sql = 'SELECT * FROM contacts WHERE name = ?';
      db.get(sql, [name], async (err, contact) => {
        if (err) {
          ui.showError(`查询失败: ${err.message}`);
          reject(err);
        } else if (!contact) {
          ui.showError(`未找到联系人 "${name}"`);
          resolve();
        } else {
          // 获取聊天记录
          const chats = await chatManager.getChatsByContactId(contact.id);

          // 生成拜年微信
          let greeting;
          let isSatisfied = false;
          let attempts = 0;
          const maxAttempts = 5;

          while (!isSatisfied && attempts < maxAttempts) {
            greeting = generator.generateGreeting(contact, chats);
            isSatisfied = await ui.showGreetingAndGetFeedback(greeting, contact.name);
            attempts++;
          }

          if (isSatisfied) {
            ui.showSuccess('拜年微信已生成并保存');
            // 保存到数据库
            const sql = 'INSERT INTO greetings (contact_id, content, status) VALUES (?, ?, ?)';
            db.run(sql, [contact.id, greeting, 'approved']);
          } else {
            ui.showError('已达到最大尝试次数，程序已停止');
          }
          resolve();
        }
      });
    });
  });
}

// 启动程序
main();