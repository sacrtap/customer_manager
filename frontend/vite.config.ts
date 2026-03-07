import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  css: {
    preprocessorOptions: {
      less: {
        modifyVars: {
          // Arco Design 主题色定制 - 极致蓝
          'arcoblue-6': '#165DFF',
          'primary-6': '#165DFF',
          // 其他主题色阶（可选，如需微调可取消注释）
          // 'primary-1': '#E8F3FF', // 最浅色 - 背景
          // 'primary-2': '#BFD8FF', // 次浅色 - 悬停背景
          // 'primary-3': '#8FBFFF', // 浅色
          // 'primary-4': '#64A3FF', // 中浅色
          // 'primary-5': '#4080FF', // Hover 状态
          // 'primary-6': '#165DFF', // 主色 - 按钮、链接
          // 'primary-7': '#0E42D2', // Active 状态
        },
        javascriptEnabled: true,
      }
    }
  },
  plugins: [
    vue({
      script: {
        defineModel: true,
        propsDestructure: true
      },
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('arco-')
        }
      }
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
