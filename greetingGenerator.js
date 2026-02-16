// 拜年微信生成模块
const { getTitleByRelation } = require('./contactRelation');

class GreetingGenerator {
  constructor() {
    // 不同关系的拜年模板
    this.templates = {
      '师生': [
        '{title}您好！值此龙年新春佳节之际，我想向您致以最诚挚的问候！感谢您一直以来对我的谆谆教导和关怀，您的言传身教让我受益匪浅。\n\n今年我们在{topic}方面有过很多交流，您的指导让我在{achievement}上取得了进步。新的一年里，我会继续努力学习，不辜负您的期望。\n\n祝您新年快乐，身体健康，工作顺利，阖家幸福！',
        '尊敬的{title}：\n\n龙年大吉！感谢您这一年来对我的关心和帮助。记得我们在{topic}上的深入交流，您的见解让我茅塞顿开。\n\n新的一年，希望能继续得到您的指导。祝您新春快乐，万事如意！'
      ],
      '同事': [
        '{name}您好！龙年吉祥！过去的一年里，我们在{project}项目上合作愉快，感谢您的支持和配合。\n\n记得我们一起攻克{difficulty}难关的日子，您的专业能力让我钦佩。新的一年，希望我们继续携手共进，取得更大的成绩。\n\n祝您新年快乐，工作顺利，身体健康！',
        '{name}：\n\n新年快乐！感谢这一年来的互帮互助。我们在{topic}上的交流让我收获良多。新的一年，愿我们的合作更加愉快！\n\n祝您龙年大吉，万事如意！'
      ],
      '上下级': [
        '{title}您好！龙年新春快乐！感谢您一直以来对我的信任和培养，您的领导和支持是我前进的动力。\n\n过去一年，在您的指导下，我在{work}方面取得了{progress}。新的一年，我会更加努力，为团队做出更大的贡献。\n\n祝您新年快乐，事业蒸蒸日上，阖家幸福！',
        '尊敬的{title}：\n\n值此新春佳节，祝您龙年大吉！感谢您这一年来的关怀和提携。我们在{topic}上的交流让我受益匪浅。\n\n新的一年，我会加倍努力工作，不辜负您的期望。祝您万事如意，身体健康！'
      ],
      '朋友': [
        '{name}！龙年快乐！好久不见，甚是想念！今年我们在{activity}玩得很开心，感谢有你这样的朋友。\n\n记得我们一起{experience}的时光，那是我今年最美好的回忆之一。新的一年，希望我们能常聚常聊，友谊长存！\n\n祝你新年快乐，万事顺遂，心想事成！',
        '{name}：\n\n新年快乐！感谢这一年来的陪伴和支持。我们在{topic}上的交流让我很开心。\n\n新的一年，愿我们的友谊地久天长！祝你龙年大吉，一切顺利！'
      ],
      '家人': [
        '{name}，龙年大吉！感谢您一直以来的付出和关爱，您的支持是我最坚强的后盾。\n\n过去一年，我们一起度过了{moment}，这些时光让我倍感温馨。新的一年，希望我们能有更多的时间在一起，共享天伦之乐。\n\n祝您新年快乐，身体健康，阖家幸福！',
        '{name}：\n\n新年快乐！感谢您的养育之恩。今年我们在{event}方面的交流让我更加了解您的想法。\n\n新的一年，我会更加孝顺您。祝您龙年吉祥，万事如意！'
      ],
      '同学': [
        '{name}，龙年快乐！毕业这么多年，我们的友谊依然如初。感谢你一直以来的陪伴。\n\n今年我们在{reunion}上见面，聊起{memory}，仿佛回到了学生时代。新的一年，希望我们能保持联系，常聚常新！\n\n祝你新年快乐，事业有成，阖家幸福！',
        '{name}：\n\n新年快乐！感谢同学情谊。我们在{topic}上的交流让我回忆起美好的校园时光。\n\n新的一年，愿我们的友谊地久天长！祝你龙年大吉，一切顺利！'
      ],
      '其他': [
        '{name}您好！龙年新春快乐！感谢这一年来的交流和支持。\n\n新的一年，希望我们能有更多的合作机会。祝您万事如意，身体健康！',
        '{name}：\n\n新年快乐！龙年大吉！感谢您的关注和支持。\n\n新的一年，祝您事业兴旺，阖家幸福！'
      ]
    };
  }

  // 根据关系和聊天记录生成拜年微信
  generateGreeting(contact, chats) {
    const { name, relation } = contact;
    const title = getTitleByRelation(relation, name);

    // 分析聊天记录
    const chatAnalysis = this.analyzeChats(chats);

    // 选择合适的模板
    const availableTemplates = this.templates[relation] || this.templates['其他'];
    const template = availableTemplates[Math.floor(Math.random() * availableTemplates.length)];

    // 填充模板变量
    let greeting = template
      .replace(/\{title\}/g, title)
      .replace(/\{name\}/g, name);

    // 填充聊天记录相关的变量
    if (chatAnalysis.importantMatters.length > 0) {
      greeting = greeting.replace(/\{topic\}/g, chatAnalysis.importantMatters[0].slice(0, 20) + '...');
      greeting = greeting.replace(/\{project\}/g, chatAnalysis.importantMatters[0].slice(0, 20) + '...');
      greeting = greeting.replace(/\{work\}/g, chatAnalysis.importantMatters[0].slice(0, 20) + '...');
      greeting = greeting.replace(/\{activity\}/g, chatAnalysis.importantMatters[0].slice(0, 20) + '...');
      greeting = greeting.replace(/\{memory\}/g, chatAnalysis.importantMatters[0].slice(0, 20) + '...');
    } else {
      greeting = greeting.replace(/\{topic\}/g, '工作和生活');
      greeting = greeting.replace(/\{project\}/g, '合作项目');
      greeting = greeting.replace(/\{work\}/g, '工作');
      greeting = greeting.replace(/\{activity\}/g, '活动');
      greeting = greeting.replace(/\{memory\}/g, '往事');
    }

    // 填充其他变量
    greeting = greeting.replace(/\{achievement\}/g, '工作中');
    greeting = greeting.replace(/\{difficulty\}/g, '技术');
    greeting = greeting.replace(/\{progress\}/g, '显著进步');
    greeting = greeting.replace(/\{experience\}/g, '旅行');
    greeting = greeting.replace(/\{moment\}/g, '节日');
    greeting = greeting.replace(/\{event\}/g, '家庭聚会');
    greeting = greeting.replace(/\{reunion\}/g, '同学聚会');

    return greeting;
  }

  // 分析聊天记录（复用 chatManager 的功能）
  analyzeChats(chats) {
    const keywords = [];
    const importantMatters = [];
    const recentActivities = [];

    // 简单的关键词提取
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
      KEYWORD_PATTERNS.forEach(({ pattern }) => {
        const matches = chat.content.match(pattern);
        if (matches) {
          matches.forEach(match => {
            if (!keywords.includes(match)) {
              keywords.push(match);
            }
          });
        }
      });

      if (chat.content.includes('重要') || chat.content.includes('记得') || chat.content.includes('务必')) {
        importantMatters.push(chat.content);
      }

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
}

module.exports = GreetingGenerator;