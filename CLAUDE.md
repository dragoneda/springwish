### 任务生命周期

1. **领取任务**：原子操作，从 `data/dev-tasks.json` 获取任务
2. **创建工作区**：
   - git worktree add -b task/xxx ../voice-notes-worktrees/task-xxx
   - 创建隔离的 `data/` 目录（实验数据库）
   - Symlink 共享文件：dev-tasks.json, api-key.json ( PROGRESS.md 禁止 symlink)
   - Symlink `node_modules/` 加速启动
   - 分配专属端口
3. **实现功能**：Claude Code 在隔离环境中工作
4. **提交代码**：`git commit` 在任务分支
5. **Merge + 测试**：
   - `git fetch origin && git merge origin/main`
   - `npm test`
6. **自动合并到 main**：
   - `git fetch origin main`
   - `git rebase origin/main`, 如果失败，按照下面的 "冲突处理" 来 resolve rebase conflict
   - 如果成功，则 `git merge main task-xxx && git push origin main`, 并且 继续执行下一步
   - 如果这一步有任何失败，则退回步骤 5
7. **标记完成**：更新 `dev-tasks.json`（必须在清理之前，防止进程被杀时任务状态丢失）
8. **清理**：
   - `git worktree remove` + 删除本地分支
   - 删除远程 task 分支
   - 重启 dev server
9. **经验沉淀**：在 PROGRESS.md 记录经验教训（可选，如果被杀也不影响任务状态）
