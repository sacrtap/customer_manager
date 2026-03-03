import { test, expect } from '@playwright/test';

test.describe('登录页面', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
  });

  test('页面正常加载', async ({ page }) => {
    await expect(page).toHaveTitle(/客户运营中台/);
    await expect(page.locator('.login-container')).toBeVisible();
    await expect(page.locator('input[placeholder*="用户名"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('表单验证 - 必填字段', async ({ page }) => {
    const loginButton = page.locator('button:has-text("登录")');
    await loginButton.click();
    
    await expect(page.locator('text=请输入用户名')).toBeVisible();
    await expect(page.locator('text=请输入密码')).toBeVisible();
  });

  test('登录成功跳转到Dashboard', async ({ page }) => {
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    
    const loginButton = page.locator('button:has-text("登录")');
    await loginButton.click();
    
    await page.waitForURL('**/dashboard', { timeout: 5000 });
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('登录失败显示错误提示', async ({ page }) => {
    await page.fill('input[placeholder*="用户名"]', 'wronguser');
    await page.fill('input[type="password"]', 'wrongpass');
    
    const loginButton = page.locator('button:has-text("登录")');
    await loginButton.click();
    
    await expect(page.locator('text=登录失败').or(page.locator('text=未授权')).or(page.locator('text=用户名或密码错误'))).toBeVisible();
  });
});
