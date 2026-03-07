import { test, expect } from '@playwright/test';

test.describe('登录页面 E2E 测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.goto('/login');
  });

  // TC-LOGIN-001: 有效用户登录 (P0)
  test('TC-LOGIN-001: 有效用户登录成功', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('admin');
    await page.locator('input[placeholder="请输入密码"]').fill('Admin@123');
    await page.locator('button[type="submit"]').click();
    
    // 验证跳转到仪表盘
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // 验证 localStorage 中有 token
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  // TC-LOGIN-002: 无效用户名登录失败 (P0)
  test('TC-LOGIN-002: 无效用户名登录失败', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('nonexistent_user');
    await page.locator('input[placeholder="请输入密码"]').fill('SomePassword123');
    await page.locator('button[type="submit"]').click();
    
    // 验证停留在登录页面
    await expect(page).toHaveURL(/.*\/login/, { timeout: 10000 });
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  // TC-LOGIN-003: 错误密码登录失败 (P0)
  test('TC-LOGIN-003: 错误密码登录失败', async ({ page }) => {
    await page.locator('input[placeholder="请输入用户名"]').fill('admin');
    await page.locator('input[placeholder="请输入密码"]').fill('WrongPassword');
    await page.locator('button[type="submit"]').click();
    
    // 验证停留在登录页面
    await expect(page).toHaveURL(/.*\/login/, { timeout: 10000 });
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });
});
