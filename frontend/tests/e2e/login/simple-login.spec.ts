import { test, expect } from '@playwright/test';

test.describe('简单登录测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
  });

  test('TC-LOGIN-001: 访问登录页面', async ({ page }) => {
    await page.goto('/login');
    
    // 截图调试
    await page.screenshot({ path: 'test-screenshot-1.png' });
    
    // 检查页面标题
    await expect(page).toHaveTitle(/客户管理系统/);
    
    // 检查登录框存在
    const loginBox = page.locator('.login-container').first();
    await expect(loginBox).toBeVisible();
    
    console.log('登录页面加载成功');
  });

  test('TC-LOGIN-002: 基本登录流程', async ({ page }) => {
    await page.goto('/login');
    
    // 截图
    await page.screenshot({ path: 'test-screenshot-2.png' });
    
    // 查找输入框
    const usernameInput = page.locator('input[type="text"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    
    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    
    // 输入凭证
    await usernameInput.fill('specialist');
    await passwordInput.fill('Specialist@123');
    
    // 点击登录
    await page.locator('button[type="submit"]').click();
    
    // 等待并截图
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-screenshot-3.png' });
    
    // 检查是否登录成功
    const token = await page.evaluate(() => localStorage.getItem('token'));
    console.log('Token:', token ? '存在' : '不存在');
    
    expect(token).toBeTruthy();
  });
});
