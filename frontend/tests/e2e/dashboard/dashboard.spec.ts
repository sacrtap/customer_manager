import { test, expect } from '@playwright/test';

test.describe('Dashboard 页面 E2E 测试', () => {
  test('TC-DASH-001: 访问 Dashboard 页面成功', async ({ page }) => {
    // 先登录
    await page.context().clearCookies();
    await page.goto('/login');
    await page.locator('input[placeholder="请输入用户名"]').fill('admin');
    await page.locator('input[placeholder="请输入密码"]').fill('Admin@123');
    await page.locator('button[type="submit"]').click();
    
    // 等待跳转到 Dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
  });

  test('TC-DASH-002: 欢迎横幅显示正确用户信息', async ({ page }) => {
    // 先登录
    await page.context().clearCookies();
    await page.goto('/login');
    await page.locator('input[placeholder="请输入用户名"]').fill('admin');
    await page.locator('input[placeholder="请输入密码"]').fill('Admin@123');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // 验证欢迎横幅
    const welcomeBanner = page.locator('.welcome-banner');
    await expect(welcomeBanner).toBeVisible({ timeout: 10000 });
    await expect(welcomeBanner.locator('h2')).toContainText('系统管理员');
  });

  test('TC-DASH-003: 欢迎横幅统计显示正确', async ({ page }) => {
    // 先登录
    await page.context().clearCookies();
    await page.goto('/login');
    await page.locator('input[placeholder="请输入用户名"]').fill('admin');
    await page.locator('input[placeholder="请输入密码"]').fill('Admin@123');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // 验证欢迎横幅统计
    const welcomeBanner = page.locator('.welcome-banner');
    await expect(welcomeBanner).toBeVisible({ timeout: 10000 });
    await expect(welcomeBanner).toContainText('客户总数');
    await expect(welcomeBanner).toContainText('活跃率');
  });

  test('TC-DASH-004: 统计卡片显示正确', async ({ page }) => {
    // 先登录
    await page.context().clearCookies();
    await page.goto('/login');
    await page.locator('input[placeholder="请输入用户名"]').fill('admin');
    await page.locator('input[placeholder="请输入密码"]').fill('Admin@123');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // 验证统计卡片
    await expect(page.locator('.stat-card').nth(0)).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.stat-card').nth(0)).toContainText('总客户数');
    await expect(page.locator('.stat-card').nth(1)).toContainText('活跃客户');
    await expect(page.locator('.stat-card').nth(2)).toContainText('风险客户');
    await expect(page.locator('.stat-card').nth(3)).toContainText('僵尸客户');
  });

  test('TC-DASH-005: 图表时间按钮文案正确', async ({ page }) => {
    // 先登录
    await page.context().clearCookies();
    await page.goto('/login');
    await page.locator('input[placeholder="请输入用户名"]').fill('admin');
    await page.locator('input[placeholder="请输入密码"]').fill('Admin@123');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // 验证图表卡片存在
    const chartCard = page.locator('.chart-card').first();
    await expect(chartCard).toBeVisible({ timeout: 10000 });
    
    // 验证卡片标题
    await expect(chartCard.locator('.chart-title')).toContainText('健康度趋势');
  });
});
