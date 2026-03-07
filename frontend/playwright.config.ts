import { defineConfig, devices } from '@playwright/test';

/**
 * 阅读文档配置：https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e',
  
  // 完全并行运行测试
  fullyParallel: true,
  
  // 每个文件的超时时间
  timeout: 30 * 1000,
  
  // 每个测试用例的超时时间
  expect: {
    timeout: 5000
  },
  
  // 失败后重试次数
  retries: 1,
  
  // 最大 worker 数
  workers: undefined,
  
  // 报告器
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],
  
  // 共享配置
  use: {
    // 基础 URL
    baseURL: 'http://localhost:5174',
    
    // 收集追踪信息
    trace: 'on-first-retry',
    
    // 浏览器截图
    screenshot: 'only-on-failure',
    
    // 录制视频
    video: 'retain-on-failure',
    
    // 浏览器上下文
    viewport: { width: 1280, height: 720 },
  },
  
  // 浏览器配置
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    
    // 可选：测试移动端
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
  ],
  
  // 运行开发服务器
  webServer: {
    command: 'npm run dev',
    port: 5174,
    reuseExistingServer: true,
  },
});
