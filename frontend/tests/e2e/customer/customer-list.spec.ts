import { test, expect } from '@playwright/test';

test.describe('客户管理 E2E 测试', () => {
  test.beforeEach(async ({ page }) => {
    // 先登录
    await page.context().clearCookies();
    await page.goto('/login');
    await page.locator('input[placeholder="请输入用户名"]').fill('admin');
    await page.locator('input[placeholder="请输入密码"]').fill('Admin@123');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
  });

  test('TC-CUSTOMER-001: 访问客户列表页面', async ({ page }) => {
    // 访问客户列表
    await page.goto('/customers');
    await expect(page).toHaveURL(/.*\/customers/, { timeout: 10000 });

    // 验证页面标题
    await expect(page.locator('h1, .page-title, .ant-page-header-heading-title')).toContainText('客户');
  });

  test('TC-CUSTOMER-002: 客户列表显示统计卡片', async ({ page }) => {
    await page.goto('/customers');

    // 验证列表容器存在
    const listContainer = page.locator('.customer-list, [class*="customer"], .ant-table');
    await expect(listContainer).toBeVisible({ timeout: 10000 });
  });

  test('TC-CUSTOMER-003: 访问批量导入页面', async ({ page }) => {
    await page.goto('/customers/import');
    await expect(page).toHaveURL(/.*\/customers\/import/, { timeout: 10000 });

    // 验证导入页面标题
    const title = page.locator('h1, .page-title, .ant-page-header-heading-title');
    await expect(title).toContainText('导入');
  });

  test('TC-CUSTOMER-004: 侧边栏菜单显示客户管理', async ({ page }) => {
    await page.goto('/dashboard');

    // 验证侧边栏客户管理菜单存在
    const customerMenu = page.locator('[class*="menu"]').filter({ hasText: '客户管理' });
    await expect(customerMenu).toBeVisible();
  });

  test('TC-CUSTOMER-005: 从侧边栏导航到客户列表', async ({ page }) => {
    await page.goto('/dashboard');

    // 点击客户管理菜单
    const customerMenu = page.locator('[class*="menu"]').filter({ hasText: '客户管理' });
    await customerMenu.click();

    // 验证跳转到客户列表
    await expect(page).toHaveURL(/.*\/customers/, { timeout: 10000 });
  });
});
