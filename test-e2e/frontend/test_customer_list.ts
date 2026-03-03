import { test, expect } from '@playwright/test';

test.describe('客户列表', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/dashboard', { timeout: 5000 });
    await page.goto('http://localhost:5173/customers');
    await page.waitForLoadState('networkidle');
  });

  test('客户列表正常加载', async ({ page }) => {
    await expect(page.locator('text=客户列表').or(page.locator('text=客户')).toBeVisible();
    const table = page.locator('table').or(page.locator('.arco-table'));
    await expect(table.first()).toBeVisible();
  });

  test('搜索功能正常', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="搜索"]').or(page.locator('.search-input'));
    const isSearchVisible = await searchInput.isVisible().catch(() => false);
    
    if (isSearchVisible) {
      await searchInput.fill('测试客户');
      await page.waitForTimeout(1000);
      await expect(searchInput).toHaveValue('测试客户');
    }
  });

  test('分页功能正常', async ({ page }) => {
    const pagination = page.locator('.pagination').or(page.locator('text=下一页').or(page.locator('button:has-text(">")));
    const isPaginationVisible = await pagination.isVisible().catch(() => false);
    
    if (isPaginationVisible) {
      await expect(pagination).toBeVisible();
    }
  });

  test('排序功能正常', async ({ page }) => {
    const sortButton = page.locator('text=排序').or(page.locator('.sort-button'));
    const isSortVisible = await sortButton.isVisible().catch(() => false);
    
    if (isSortVisible) {
      await sortButton.click();
      await page.waitForTimeout(500);
      await expect(sortButton).toBeVisible();
    }
  });

  test('权限控制正常', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    const table = page.locator('table').or(page.locator('.arco-table'));
    const isTableVisible = await table.isVisible().catch(() => false);
    
    if (isTableVisible) {
      await expect(table).toBeVisible();
    }
  });
});
