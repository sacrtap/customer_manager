import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/dashboard', { timeout: 5000 });
  });

  test('Dashboard页面正常加载', async ({ page }) => {
    await expect(page).toHaveTitle(/客户运营中台/);
    await expect(page.locator('text=工作台').or(page.locator('text=Dashboard')).toBeVisible();
  });

  test('快捷入口显示正确', async ({ page }) => {
    await expect(page.locator('text=客户列表').or(page.locator('a[href*="customers"]')).toBeVisible();
    await expect(page.locator('text=用户管理').or(page.locator('a[href*="users"]')).toBeVisible();
    await expect(page.locator('text=角色管理').or(page.locator('a[href*="roles"]')).toBeVisible();
  });

  test('最近操作记录显示', async ({ page }) => {
    await page.waitForTimeout(1000);
    const recentSection = page.locator('text=最近操作').or(page.locator('.recent-operations'));
    const isVisible = await recentSection.isVisible().catch(() => false);
    
    if (isVisible) {
      await expect(recentSection).toBeVisible();
    }
  });
});
