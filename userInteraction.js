// 用户交互模块
const readline = require('readline');

class UserInteraction {
  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  // 显示拜年微信并征求用户意见
  async showGreetingAndGetFeedback(greeting, contactName) {
    console.log(`\n=== 为 ${contactName} 生成的拜年微信 ===\n`);
    console.log(greeting);
    console.log('\n========================================\n');

    return new Promise((resolve) => {
      this.rl.question('您是否满意这条拜年微信？(y/n): ', (answer) => {
        const normalizedAnswer = answer.trim().toLowerCase();
        resolve(normalizedAnswer === 'y' || normalizedAnswer === 'yes');
      });
    });
  }

  // 显示提示信息
  showInfo(message) {
    console.log(`\nℹ️  ${message}`);
  }

  // 显示成功信息
  showSuccess(message) {
    console.log(`\n✅ ${message}`);
  }

  // 显示错误信息
  showError(message) {
    console.log(`\n❌ ${message}`);
  }

  // 显示菜单
  showMenu(options) {
    console.log('\n请选择操作：');
    options.forEach((option, index) => {
      console.log(`${index + 1}. ${option}`);
    });

    return new Promise((resolve) => {
      this.rl.question('请输入选项编号：', (answer) => {
        const choice = parseInt(answer.trim());
        if (choice >= 1 && choice <= options.length) {
          resolve(choice - 1);
        } else {
          console.log('无效的选项，请重新输入');
          resolve(this.showMenu(options));
        }
      });
    });
  }

  // 获取用户输入
  getInput(prompt) {
    return new Promise((resolve) => {
      this.rl.question(prompt, (answer) => {
        resolve(answer.trim());
      });
    });
  }

  // 关闭交互界面
  close() {
    this.rl.close();
  }
}

module.exports = UserInteraction;