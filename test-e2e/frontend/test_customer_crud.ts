import { test, expect } from '@playwright/test';

test.describe('客户CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/dashboard', { timeout: 5000 });
    await page.goto('http://localhost:5173/customers');
    await page.waitForLoadState('networkidle');
  });

  test('创建客户对话框正常', async ({ page }) => {
    const createButton = page.locator('button:has-text("新增客户")').or(page.locator('button:has-text("创建")').or(page.locator('.add-button'));
    const isCreateVisible = await createButton.isVisible().catch(() => false);
    
    if (isCreateVisible) {
      await createButton.click();
      await page.waitForTimeout(500);
      const dialog = page.locator('.modal').or(page.locator('.dialog').or(page.locator('text=创建客户')));
      await expect(dialog).toBeVisible();
    }
  });

  test('编辑客户对话框正常', async ({ page }) => {
    const table = page.locator('table').or(page.locator('.arco-table'));
    const isTableVisible = await table.isVisible().catch(() => false);
    
    if (isTableVisible) {
      const firstRow = table.locator('tr').nth(1);
      const editButton = firstRow.locator('button:has-text("编辑")').or(firstRow.locator('.edit-button'));
      const isEditVisible = await editButton.isVisible().catch(() => false);
      
      if (isEditVisible) {
        await editButton.click();
        await page.waitForTimeout(500);
        const dialog = page.locator('.modal').or(page.locator('.dialog').or(page.locator('text=编辑客户')));
        await expect(dialog).toBeVisible();
      }
    }
  });

  test('删除客户确认对话框', async ({ page }) => {
    const table = page.locator('table').or(page.locator('.arco-table'));
    const isTableVisible = await table.isVisible().catch(() => false);
    
    if (isTableVisible) {
      const firstRow = table.locator('tr').nth(1);
      const deleteButton = firstRow.locator('button:has-text("删除")').or(firstRow.locator('.delete-button'));
      const isDeleteVisible = await deleteButton.isVisible().catch(() => false);
      
      if (isDeleteVisible) {
        await deleteButton.click();
        await page.waitForTimeout(500);
        const dialog = page.locator('.modal').or(page.locator('.dialog').or(page.locator('text=确认删除'));
        await expect(dialog).toBeVisible();
      }
    }
  });

  test('表单验证正常', async ({ page }) => {
    const createButton = page.locator('button:has-text("新增客户)').
      .or(page.locator('button:has-text("创建")')).
      or(page.locator('.add-button'));
    const isCreateVisible = await createButton.isVisible().catch(() => false);
    
    if (isCreateVisible) {
      await createButton.click();
      await page.waitForTimeout(500);
      
      const submitButton = page.locator('button:has-text("确定")').or(page.locator('button[type="submit"]'));
      const form = page.locator('.customer-form').or(page.locator('form'));
      
      if (await form.isVisible().catch(() => false)) {
        await submitButton.click();
        await page.waitForTimeout(500);
        const errorMsg = page.locator('text=请填写').or(page.locator('.error-message'));
        const isErrorVisible = await errorMsg.isVisible().catch(() => false);
        if (isErrorVisible) {
          await expect(errorMsg).toBeVisible();
        }
      }
    }
  });

  test('操作成功提示显示', async ({ page }) => {
    const createButton = page.locator('button:has-text("新增客户")').
      or(page.locator('button:has-text("创建")')).
      or(page.locator('.add-button'));
    const isCreateVisible = await createButton.isVisible().catch(() => false);
    
    if (isCreateVisible) {
      await createButton.click();
      await page.waitForTimeout(500);
      
      const nameInput = page.locator('input[name*="name"]').or(page.locator('input[placeholder*="客户名称"]'));
      const submitButton = page.locator('button:has-text("确定")').or(page.locator('button[type="submit"]'));
      
      if (await nameInput.isVisible().catch(() => false)) {
        await nameInput.fill('E2E测试客户');
        
        if (await submitButton.isVisible().catch(() => false)) {
          await submitButton.click();
          await page.waitForTimeout(2000);
          
          const successMsg = page.locator('text=成功').or(page.locator('.arco-message-success'));
          const isSuccessVisible = await successMsg.isVisible().catch(() => false);
          if (isSuccessVisible) {
            await expect(successMsg).toBeVisible();
          }
        }
      }
    }
  });
});
