import { test, expect } from '@playwright/test';

test.describe('Dashboard 页面 E2E 测试', () => {
  // 测试用户配置
  const testUsers = {
    admin: { username: 'admin', password: 'Admin@123', realName: '系统管理员', role: '系统管理员' },
    manager: { username: 'manager', password: 'Manager@123', realName: '运营经理', role: '运营经理' },
    specialist: { username: 'specialist', password: 'Specialist@123', realName: '运营专员', role: '运营专员' },
    sales: { username: 'sales', password: 'Sales@123', realName: '销售人员', role: '销售人员' },
  };

  // 登录辅助函数
  async function login(page: any, username: string, password: string) {
    await page.context().clearCookies();
    await page.goto('/login');
    await page.locator('input[placeholder="请输入用户名"]').fill(username);
    await page.locator('input[placeholder="请输入密码"]').fill(password);
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.locator('.arco-message-success')).toBeVisible({ timeout: 5000 });
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 5000 });
  }

  test.describe('基础功能测试', () => {
    test.beforeEach(async ({ page }) => {
      await login(page, 'admin', 'Admin@123');
    });

    // TC-DASH-001: 访问 Dashboard 页面成功
    test('TC-DASH-001: 访问 Dashboard 页面成功', async ({ page }) => {
      await expect(page).toHaveURL(/.*\/dashboard/);
      await expect(page.locator('.welcome-banner')).toBeVisible({ timeout: 5000 });
    });

    // TC-DASH-002: 欢迎横幅显示正确用户信息
    test('TC-DASH-002: 欢迎横幅显示正确用户信息', async ({ page }) => {
      const welcomeBanner = page.locator('.welcome-banner');
      await expect(welcomeBanner).toBeVisible();
      await expect(welcomeBanner.locator('.welcome-title')).toContainText('系统管理员');
    });

    // TC-DASH-003: 统计卡片显示正确
    test('TC-DASH-003: 统计卡片显示正确', async ({ page }) => {
      await expect(page.locator('.stat-card').nth(0)).toBeVisible();
      await expect(page.locator('.stat-card').nth(0)).toContainText('客户总数');
      await expect(page.locator('.stat-card').nth(1)).toContainText('活跃客户');
      await expect(page.locator('.stat-card').nth(2)).toContainText('风险客户');
      await expect(page.locator('.stat-card').nth(3)).toContainText('僵尸客户');
    });
  });

  test.describe('图表渲染测试', () => {
    test.beforeEach(async ({ page }) => {
      await login(page, 'admin', 'Admin@123');
    });

    // TC-DASH-101: 健康度趋势图表渲染
    test('TC-DASH-101: 健康度趋势图表渲染', async ({ page }) => {
      await expect(page.locator('.chart-card').nth(0)).toBeVisible({ timeout: 5000 });
      await expect(page.locator('.chart-card').nth(0)).toContainText('客户健康度趋势');
    });

    // TC-DASH-102: 客户价值分布图表渲染
    test('TC-DASH-102: 客户价值分布图表渲染', async ({ page }) => {
      await expect(page.locator('.chart-card').nth(1)).toBeVisible({ timeout: 5000 });
      await expect(page.locator('.chart-card').nth(1)).toContainText('客户价值分布');
    });
  });

  test.describe('风险客户表格测试', () => {
    test.beforeEach(async ({ page }) => {
      await login(page, 'admin', 'Admin@123');
    });

    // TC-DASH-201: 风险客户表格显示
    test('TC-DASH-201: 风险客户表格显示', async ({ page }) => {
      const tableCard = page.locator('.table-card').nth(0);
      await expect(tableCard).toBeVisible({ timeout: 5000 });
      await expect(tableCard).toContainText('风险客户预警');
    });

    // TC-DASH-202: 风险客户表格列显示
    test('TC-DASH-202: 风险客户表格列显示', async ({ page }) => {
      await expect(page.getByRole('columnheader', { name: '客户名称', exact: true })).toBeVisible({ timeout: 5000 });
      await expect(page.getByRole('columnheader', { name: '等级', exact: true })).toBeVisible();
      await expect(page.getByRole('columnheader', { name: '未使用天数', exact: true })).toBeVisible();
      await expect(page.getByRole('columnheader', { name: '风险等级', exact: true })).toBeVisible();
    });
  });

  test.describe('权限控制测试', () => {
    test('TC-DASH-301 (Admin): 访问 Dashboard 成功', async ({ page }) => {
      await login(page, 'admin', 'Admin@123');
      
      // 验证 Dashboard 正常加载
      await expect(page.locator('.welcome-banner')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('.stats-grid')).toBeVisible();
    });

    test('TC-DASH-302 (Sales): 访问 Dashboard 成功', async ({ page }) => {
      await login(page, 'sales', 'Sales@123');
      
      // 验证 Dashboard 正常加载
      await expect(page.locator('.welcome-banner')).toBeVisible({ timeout: 5000 });
    });
  });
});
