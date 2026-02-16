#!/usr/bin/env node
// 测试程序

const { initDatabase, createTables } = require('./database');
const { determineRelation, RELATION_TYPES } = require('./contactRelation');
const ChatManager = require('./chatManager');
const GreetingGenerator = require('./greetingGenerator');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = path.join(__dirname, 'data', 'wechat.db');

async function test() {
  console.log('=== 拜年微信生成程序测试 ===\n');

  try {
    // 初始化数据库
    const db = await initDatabase();
    await createTables(db);

    const chatManager = new ChatManager();
    const generator = new GreetingGenerator();

    // 测试1: 关系判断
    console.log('1. 关系判断测试:');
    const testContacts = [
      { name: '张老师', notes: '我的数学老师' },
      { name: '李经理', notes: '工作上的领导' },
      { name: '王同事', notes: '公司的同事' },
      { name: '刘同学', notes: '大学同学' },
      { name: '陈朋友', notes: '好朋友' },
      { name: '赵总', notes: '部门经理' }
    ];

    testContacts.forEach(contact => {
      const relation = determineRelation(contact);
      console.log(`   ${contact.name}: ${relation}`);
    });

    // 测试2: 添加测试数据到数据库
    console.log('\n2. 添加测试数据到数据库:');

    // 添加测试联系人
    const testNames = ['张老师', '李经理', '王同事', '陈朋友', '刘同学'];
    const testRelations = ['师生', '上下级', '同事', '朋友', '同学'];

    for (let i = 0; i < testNames.length; i++) {
      const name = testNames[i];
      const relation = testRelations[i];
      const phone = `1380013800${i}`;
      const notes = `这是我的${relation}，关系很好`;

      await new Promise((resolve, reject) => {
        const sql = 'INSERT OR IGNORE INTO contacts (name, phone, relation, notes) VALUES (?, ?, ?, ?)';
        db.run(sql, [name, phone, relation, notes], function(err) {
          if (err) {
            console.error(err);
            reject(err);
          } else {
            resolve();
          }
        });
      });
    }
    console.log('   测试联系人添加成功');

    // 获取联系人ID
    const contacts = [];
    await new Promise((resolve, reject) => {
      const sql = 'SELECT * FROM contacts';
      db.all(sql, (err, rows) => {
        if (err) {
          console.error(err);
          reject(err);
        } else {
          contacts.push(...rows);
          console.log(`   数据库中有 ${rows.length} 个联系人`);
          resolve();
        }
      });
    });

    // 为每个联系人添加一些测试聊天记录
    const testChats = [
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
    ];

    for (let i = 0; i < contacts.length; i++) {
      const contact = contacts[i];
      const chats = testChats[i];

      for (const content of chats) {
        await chatManager.saveChat(contact.id, content);
      }
    }

    console.log('   测试聊天记录添加成功');

    // 测试3: 聊天记录分析
    console.log('\n3. 聊天记录分析测试:');
    for (const contact of contacts) {
      const chats = await chatManager.getChatsByContactId(contact.id);
      console.log(`   ${contact.name}: ${chats.length} 条聊天记录`);
    }

    // 测试4: 生成拜年微信
    console.log('\n4. 拜年微信生成测试:');
    for (const contact of contacts) {
      const chats = await chatManager.getChatsByContactId(contact.id);
      const greeting = generator.generateGreeting(contact, chats);
      console.log(`\n   === 为 ${contact.name} 生成的拜年微信 ===`);
      console.log(greeting);
      console.log('');
    }

    // 测试结果
    console.log('=== 测试完成 ===');

    // 关闭连接
    db.close();
    chatManager.close();

  } catch (error) {
    console.error('\n❌ 测试过程中出现错误:', error.message);
    console.error(error.stack);
  }
}

// 运行测试
test();