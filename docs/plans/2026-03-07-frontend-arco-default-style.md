# Frontend Arco Design 默认样式重构实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将前端页面从自定义样式（渐变背景、自定义圆角、阴影等）重构为使用 Arco Design 默认主题及样式

**Architecture:** 采用渐进式重构策略，先修改核心样式文件和组件，再逐个修复视图组件，最后统一验证

**Tech Stack:** Vue 3 + TypeScript + Arco Design + SCSS + Vite + Playwright

---

## 任务清单

### Task 1: 创建重构分支

**Step 1: 创建 Git 分支**

```bash
cd frontend && git checkout -b refactor/arco-default-style
```

**Step 2: 验证分支创建成功**

```bash
git branch --show-current
```
Expected: `refactor/arco-default-style`

**Step 3: 提交分支创建**

```bash
git add -A && git commit -m "chore: create refactor branch for arco default style" --allow-empty
```

---

### Task 2: 重构 variables.scss

**Files:**
- Modify: `frontend/src/styles/variables.scss`

**Step 1: 读取当前文件内容**

```bash
cat frontend/src/styles/variables.scss
```

**Step 2: 重写文件，移除自定义变量**

保留颜色变量，移除所有渐变、圆角、阴影变量：

```scss
// 主题颜色 - 保留用于 JS 逻辑引用
$primary-color: #165DFF;
$primary-dark: #0E42D2;
$success-color: #00B42A;
$warning-color: #FF7D00;
$danger-color: #F53F3F;

// 注意：其他样式请使用 Arco Design CSS 变量
// 如：var(--color-primary), var(--border-radius-medium), var(--color-bg-1)
```

**Step 3: 验证文件修改**

```bash
cat frontend/src/styles/variables.scss
```

**Step 4: 提交修改**

```bash
cd frontend && git add src/styles/variables.scss && git commit -m "refactor(styles): remove custom gradient and shadow variables"
```

---

### Task 3: 重构 StatCard.vue 组件

**Files:**
- Modify: `frontend/src/components/StatCard.vue`

**Step 1: 读取当前文件**

```bash
cat frontend/src/components/StatCard.vue
```

**Step 2: 修改 style 部分**

移除 `@import` 和渐变变量，使用 Arco CSS 变量：

```scss
<style scoped lang="scss">
.stat-card {
  background: var(--color-bg-1);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-medium);
  padding: 24px;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-icon.blue {
  background: var(--color-primary-light-1);
  color: var(--color-primary);
}

.stat-icon.green {
  background: var(--color-success-light-1);
  color: var(--color-success);
}

.stat-icon.orange {
  background: var(--color-warning-light-1);
  color: var(--color-warning);
}

.stat-icon.red {
  background: var(--color-danger-light-1);
  color: var(--color-danger);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-1);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-3);
}
</style>
```

**Step 3: 提交修改**

```bash
cd frontend && git add src/components/StatCard.vue && git commit -m "refactor(components): use arco css variables in StatCard"
```

---

### Task 4: 重构 MainLayout.vue

**Files:**
- Modify: `frontend/src/layouts/MainLayout.vue`

**Step 1: 移除侧边栏渐变背景**

修改 `.layout-sider` 样式：
```scss
.layout-sider {
  background: var(--color-bg-1);
  border-right: 1px solid var(--color-border);
  
  .sidebar-header {
    height: 64px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    border-bottom: 1px solid var(--color-border);
  }
  
  .sidebar-logo {
    width: 40px;
    height: 40px;
    background: var(--color-primary-light-1);
    border-radius: var(--border-radius-medium);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-primary);
    font-size: 18px;
    font-weight: bold;
    margin-right: 12px;
    flex-shrink: 0;
  }
  
  .sidebar-title {
    color: var(--color-text-1);
    font-size: 18px;
    font-weight: 600;
  }
}
```

**Step 2: 移除菜单深度样式覆盖**

移除所有 `:deep(.arco-menu-*)` 样式，让菜单使用 Arco 默认样式

**Step 3: 移除用户信息区域渐变**

```scss
.user-avatar-sidebar {
  width: 40px;
  height: 40px;
  background: var(--color-primary-light-1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  font-size: 16px;
  font-weight: 600;
}
```

**Step 4: 提交修改**

```bash
cd frontend && git add src/layouts/MainLayout.vue && git commit -m "refactor(layout): use arco default light theme for sidebar"
```

---

### Task 5: 重构 Dashboard.vue

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`

**Step 1: 移除 variables 引用**

删除 `@import "@/styles/variables.scss"`

**Step 2: 修改欢迎横幅样式**

```scss
.welcome-banner {
  background: var(--color-primary-light-1);
  border-radius: var(--border-radius-medium);
  padding: 32px;
  color: var(--color-primary);
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

**Step 3: 修改统计卡片图标样式**

移除渐变背景，使用 `var(--color-*-light-1)`

**Step 4: 提交修改**

```bash
cd frontend && git add src/views/Dashboard.vue && git commit -m "refactor(views): use arco variables in Dashboard"
```

---

### Task 6: 重构 health/Dashboard.vue

**Files:**
- Modify: `frontend/src/views/health/Dashboard.vue`

**Step 1: 移除 variables 引用和 mixin**

删除 `@import "@/styles/variables.scss"` 和 `@include chart-card`

**Step 2: 修改欢迎横幅样式**

使用 Arco CSS 变量

**Step 3: 提交修改**

```bash
cd frontend && git add src/views/health/Dashboard.vue && git commit -m "refactor(views): use arco variables in health dashboard"
```

---

### Task 7: 重构 LoginView.vue

**Files:**
- Modify: `frontend/src/views/LoginView.vue`

**Step 1: 移除所有渐变背景**

- `.login-container` 背景改为 `var(--color-fill-2)`
- `.brand-section` 背景改为 `var(--color-primary-light-1)`
- 移除 `@keyframes pulse` 动画

**Step 2: 简化品牌区域样式**

使用纯色背景，移除装饰性元素

**Step 3: 提交修改**

```bash
cd frontend && git add src/views/LoginView.vue && git commit -m "refactor(views): simplify login page with arco theme"
```

---

### Task 8: 验证构建

**Step 1: 安装依赖（如需要）**

```bash
cd frontend && npm install
```

**Step 2: 运行类型检查**

```bash
npm run build
```

Expected: 无编译错误

**Step 3: 启动开发服务器**

```bash
npm run dev
```

**Step 4: 手动验证视觉效果**

在浏览器中检查：
- [ ] 侧边栏为浅色主题
- [ ] 统计卡片图标为纯色背景
- [ ] 登录页样式正确
- [ ] Dashboard 页面样式正确

**Step 5: 提交验证**

```bash
git add -A && git commit -m "chore: verify build succeeds" --allow-empty
```

---

### Task 9: 运行 E2E 测试

**Step 1: 安装 Playwright（如需要）**

```bash
cd frontend && npx playwright install chromium
```

**Step 2: 运行完整测试套件**

```bash
npx playwright test
```

**Step 3: 如有失败，逐个修复**

**Step 4: 提交测试结果**

```bash
git add -A && git commit -m "test(e2e): all tests pass after style refactor" --allow-empty
```

---

### Task 10: 合并代码

**Step 1: 切换回主分支**

```bash
git checkout main
```

**Step 2: 合并重构分支**

```bash
git merge --no-ff refactor/arco-default-style -m "Merge pull request #1 - Frontend Arco default style refactor

- Removed custom gradient backgrounds
- Removed variables.scss custom variables
- Using Arco Design CSS variables throughout
- Sidebar now uses light theme
- All E2E tests passing"
```

**Step 3: 推送远程（可选）**

```bash
git push origin main
```

---

## 验收标准

- [ ] 所有文件不再引用 `variables.scss` 中的渐变变量
- [ ] 侧边栏使用 Arco 默认浅色主题
- [ ] 无 `linear-gradient` 自定义样式
- [ ] 开发服务器无 CSS 编译错误
- [ ] E2E 测试全部通过
- [ ] 视觉效果符合 Arco Design 默认风格

---

## 回滚方案

```bash
git checkout main
git branch -D refactor/arco-default-style
```
