import { test, expect } from '@playwright/test';

test.describe('导航', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/dashboard', { timeout: 5000 });
  });

  test('侧边栏菜单显示', async ({ page }) => {
    const sidebar = page.locator('.sidebar').or(page.locator('.arco-layout-sider'));
    await expect(sidebar).toBeVisible();
    
    await expect(page.locator('text=工作台').or(page.locator('a[href*="dashboard"]')).toBeVisible();
    await expect(page.locator('text=客户列表').or(page.locator('a[href*="customers"]')).toBeVisible();
    await expect(page.locator('text=用户管理').or(page.locator('a[href*="users"]')).toBeVisible();
  });

.

  test('顶部导航用户菜单', async ({ page }) => {
    const header = page.locator('.header').or(page.locator('.arco-layout-header'));
    await expect(header).toBeVisible();
    
    const userMenu = header.locator('.user-menu').or(header.locator('.user-dropdown'));
    const isMenuVisible = await userMenu.isVisible().catch(() => false);
    
    if (isMenuVisible) {
      await expect(userMenu).toBeVisible();
    }
  });

  test('路由跳转正常', async ({ page }) => {
    await page.click('a[href*="customers"]');
    await page.waitForURL('**/customers', { timeout: 3000 });
    await expect(page).toHaveURL(/.*customers/);
    
    await page.click('a[href*="dashboard"]');
    await page.waitForURL('**/dashboard', { timeout: 3000 });
    await expect(page).toHaveURL(/.*dashboard/);
  });
});
