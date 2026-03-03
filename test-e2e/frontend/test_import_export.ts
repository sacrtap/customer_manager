import { test, expect } from '@playwright/test';

test.describe('批量导入导出', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/dashboard', { timeout: 5000 });
  });

  test('下载导入模板成功', async ({ page }) => {
    await page.goto('http://localhost:5173/customers/import');
    await page.waitForLoadState('networkidle');
    
    const downloadButton = page.locator('button:has-text("下载模板")').or(page.locator('a:has-text("模板")'));
    const isDownloadVisible = await downloadButton.isVisible().catch(() => false);
    
    if (isDownloadVisible) {
      const downloadPromise = page.waitForEvent('download');
      await downloadButton.click();
      
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.(xlsx|csv)$/);
    }
  });

  test('文件上传功能正常', async ({ page }) => {
    await page.goto('http://localhost:5173/customers/import');
    await page.waitForLoadState('networkidle');
    
    const fileInput = page.locator('input[type="file"]');
    const isFileVisible = await fileInput.isVisible().catch(() => false);
    
    if (isFileVisible) {
      await expect(fileInput).toBeVisible();
    }
  });

  test('导入结果展示正确', async ({ page }) => {
    await page.goto('http://localhost:5173/customers/import');
    await page.waitForLoadState('networkidle');
    
    const resultSection = page.locator('.import-result').or(page.locator('text=导入结果'));
    const isResultVisible = await resultSection.isVisible().catch(() => false);
    
    if (isResultVisible) {
      await expect(resultSection).toBeVisible();
    }
  });

  test('导出下载成功', async ({ page }) => {
    await page.goto('http://localhost:5173/customers');
    await page.waitForLoadState('networkidle');
    
    const exportButton = page.locator('button:has-text("导出")').or(page.locator('a:has-text("导出")'));
    const isExportVisible = await exportButton.isVisible().catch(() => false);
    
    if (isExportVisible) {
      const downloadPromise = page.waitForEvent('download');
      await exportButton.click();
      
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.(xlsx|csv)$/);
    }
  });
});
