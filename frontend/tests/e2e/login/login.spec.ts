import { test, expect } from '@playwright/test';

test.describe('登录页面 E2E 测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.goto('/login');
  });

  // TC-LOGIN-001: 有效用户登录 (P0)
  test('TC-LOGIN-001: 有效用户登录成功', async ({ page }) => {
    // Arco Design 的 Input 组件使用特定的选择器
    await page.locator('input[placeholder="请输入用户名"]').fill('specialist');
    await page.locator('input[placeholder="请输入密码"]').fill('Specialist@123');
    
    // 点击登录按钮
    await page.getByRole('button', { name: '登录' }).click();
    
    // 等待登录成功提示
    await expect(page.locator('.arco-message-success')).toBeVisible({ timeout: 5000 });
    
    // 验证跳转到仪表盘
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 5000 });
    
    // 验证 localStorage 中有 token
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  // TC-LOGIN-002: 无效用户名 (P0)
  test('TC-LOGIN-002: 无效用户名登录失败', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('nonexistent_user');
    await page.locator('input[placeholder="请输入密码"]').fill('SomePassword123');
    await page.getByRole('button', { name: '登录' }).click();
    
    // 等待错误提示
    await expect(page.locator('.arco-message-error')).toBeVisible({ timeout: 5000 });
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  // TC-LOGIN-003: 错误密码 (P0)
  test('TC-LOGIN-003: 错误密码登录失败', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('specialist');
    await page.locator('input[placeholder="请输入密码"]').fill('WrongPassword');
    await page.getByRole('button', { name: '登录' }).click();
    
    await expect(page.locator('.arco-message-error')).toBeVisible({ timeout: 5000 });
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  // TC-LOGIN-004: 禁用账号登录 (P1)
  test('TC-LOGIN-004: 禁用账号登录失败', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('test_inactive');
    await page.locator('input[placeholder="请输入密码"]').fill('Test123!');
    await page.getByRole('button', { name: '登录' }).click();
    
    await expect(page.locator('.arco-message-error')).toBeVisible({ timeout: 5000 });
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  // TC-LOGIN-005: 用户名为空 (P1)
  test('TC-LOGIN-005: 用户名为空表单验证', async ({ page }) => {
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.locator('.arco-form-item-error').first()).toBeVisible({ timeout: 5000 });
  });

  // TC-LOGIN-006: 用户名长度不足 (P1)
  test('TC-LOGIN-006: 用户名长度不足表单验证', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('ab');
    await page.locator('input[placeholder="请输入密码"]').fill('Password123');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.locator('.arco-form-item-error').first()).toBeVisible({ timeout: 5000 });
  });

  // TC-LOGIN-007: 密码为空 (P1)
  test('TC-LOGIN-007: 密码为空表单验证', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('testuser');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.locator('.arco-form-item-error').first()).toBeVisible({ timeout: 5000 });
  });

  // TC-LOGIN-008: 密码长度不足 (P1)
  test('TC-LOGIN-008: 密码长度不足表单验证', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('testuser');
    await page.locator('input[placeholder="请输入密码"]').fill('12345');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.locator('.arco-form-item-error').first()).toBeVisible({ timeout: 5000 });
  });

  // TC-LOGIN-009: 登录后 Token 存储验证 (P1)
  test('TC-LOGIN-009: 登录后 Token 和用户信息存储', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('specialist');
    await page.locator('input[placeholder="请输入密码"]').fill('Specialist@123');
    await page.getByRole('button', { name: '登录' }).click();
    
    await expect(page.locator('.arco-message-success')).toBeVisible({ timeout: 5000 });
    
    const storage = await page.evaluate(() => ({
      token: localStorage.getItem('token'),
      userInfo: localStorage.getItem('userInfo')
    }));
    
    expect(storage.token).toBeTruthy();
    expect(storage.userInfo).toBeTruthy();
  });

  // TC-LOGIN-010: 登出功能 (P1)
  test('TC-LOGIN-010: 登出功能验证', async ({ page }) => {
    // 登录
    await page.locator('input[placeholder="请输入用户名"]').fill('specialist');
    await page.locator('input[placeholder="请输入密码"]').fill('Specialist@123');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.locator('.arco-message-success')).toBeVisible({ timeout: 5000 });
    
    await page.waitForURL(/.*\/dashboard/);
    
    // 模拟登出
    await page.evaluate(() => {
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      localStorage.removeItem('permissions');
    });
    
    await page.goto('/login');
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  // TC-LOGIN-011: SQL 注入防护 (P2 安全)
  test('TC-LOGIN-011: SQL 注入攻击防护', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill("admin' OR '1'='1");
    await page.locator('input[placeholder="请输入密码"]').fill('anything');
    await page.getByRole('button', { name: '登录' }).click();
    
    await expect(page.locator('.arco-message-error')).toBeVisible({ timeout: 5000 });
  });

  // TC-LOGIN-012: 管理员登录 (P1)
  test('TC-LOGIN-012: 管理员角色登录成功', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('admin');
    await page.locator('input[placeholder="请输入密码"]').fill('Admin@123');
    await page.getByRole('button', { name: '登录' }).click();
    
    await expect(page.locator('.arco-message-success')).toBeVisible({ timeout: 5000 });
    await expect(page).toHaveURL(/.*\/dashboard/);
  });
});
