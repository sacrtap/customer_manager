<template>
  <div class="login-container">
    <div class="login-wrapper">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div>
          <div class="brand-header">
            <div class="brand-logo">
              <div class="logo-icon">
                <icon-user-group />
              </div>
              <span class="brand-name">客户运营中台</span>
            </div>
            <h1 class="brand-title">数据驱动的<br>客户运营管理</h1>
            <p class="brand-subtitle">
              告别 Excel 分散管理，实现客户健康度自动监控<br>
              结算单自动生成，运营效率提升 70%
            </p>
          </div>

          <div class="brand-stats">
            <div class="stat-card">
              <div class="stat-number">1,320</div>
              <div class="stat-label">客户总数</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">82.5%</div>
              <div class="stat-label">活跃客户率</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">2h</div>
              <div class="stat-label">结算生成时间</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">99.9%</div>
              <div class="stat-label">数据准确率</div>
            </div>
          </div>
        </div>

        <div class="brand-footer">
          © 2026 客户运营中台系统 v1.0 | 企业内部管理系统
        </div>
      </div>

      <!-- 右侧登录区域 -->
      <div class="login-section">
        <div class="login-header">
          <h2 class="login-title">欢迎回来</h2>
          <p class="login-subtitle">请登录您的账户以继续</p>
        </div>

        <div class="login-form">
          <a-form
            ref="formRef"
            :model="form"
            :rules="rules"
            layout="vertical"
            @submit="handleLogin"
          >
            <a-form-item field="username">
              <template #label>
                <span class="form-label">用户名</span>
              </template>
              <a-input
                v-model="form.username"
                placeholder="请输入用户名"
                class="login-input"
                size="large"
              >
                <template #prefix>
                  <icon-user />
                </template>
              </a-input>
            </a-form-item>

            <a-form-item field="password">
              <template #label>
                <span class="form-label">密码</span>
              </template>
              <a-input-password
                v-model="form.password"
                placeholder="请输入密码"
                class="login-input"
                size="large"
              >
                <template #prefix>
                  <icon-lock />
                </template>
              </a-input-password>
            </a-form-item>

            <div class="form-options">
              <a-checkbox v-model="form.remember">记住我</a-checkbox>
              <span class="forgot-link">忘记密码？</span>
            </div>

            <a-button
              type="primary"
              class="login-btn"
              size="large"
              html-type="submit"
              :loading="loading"
              long
            >
              登 录
            </a-button>
          </a-form>

          <div class="divider">
            <span>快捷入口</span>
          </div>

          <div class="login-tips">
            <p>测试账号</p>
            <div class="role-tags">
              <a-tag color="arcoblue" @click="fillTestAccount('admin', 'admin123')">
                admin / admin123
              </a-tag>
              <a-tag color="green" @click="fillTestAccount('manager', 'manager123')">
                manager / manager123
              </a-tag>
              <a-tag color="orange" @click="fillTestAccount('specialist', 'specialist123')">
                specialist / specialist123
              </a-tag>
              <a-tag color="purple" @click="fillTestAccount('sales', 'sales123')">
                sales / sales123
              </a-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const loading = ref(false)

const rules = {
  username: [{ required: true, message: '请输入用户名' }],
  password: [{ required: true, message: '请输入密码' }]
}

const fillTestAccount = (username: string, password: string) => {
  form.username = username
  form.password = password
}

const handleLogin = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  loading.value = true

  try {
    await userStore.login({
      username: form.username,
      password: form.password
    })
    Message.success('登录成功')
    router.push('/dashboard')
  } catch (error) {
    Message.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-container {
  display: flex;
  min-height: 100vh;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

.login-wrapper {
  display: flex;
  width: 100%;
  max-width: 1200px;
  min-height: 640px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 左侧品牌区域 */
.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #165DFF 0%, #0E42D2 100%);
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: #ffffff;
  position: relative;
  overflow: hidden;
}

.brand-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.brand-header {
  position: relative;
  z-index: 1;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 40px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.brand-name {
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 20px;
}

.brand-subtitle {
  font-size: 16px;
  opacity: 0.9;
  line-height: 1.6;
}

.brand-stats {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 60px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  opacity: 0.8;
}

.brand-footer {
  position: relative;
  z-index: 1;
  font-size: 13px;
  opacity: 0.7;
  margin-top: 40px;
}

/* 右侧登录区域 */
.login-section {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-header {
  margin-bottom: 40px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: #86909c;
}

.login-form {
  max-width: 400px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #1d2129;
  margin-bottom: 8px;
}

.login-input {
  width: 100%;

  :deep(.arco-input-wrapper) {
    height: 44px;
    border-radius: 8px;
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.forgot-link {
  font-size: 14px;
  color: #165dff;
  cursor: pointer;

  &:hover {
    color: #4080ff;
  }
}

.login-btn {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  background: #165DFF;
  border: none;

  &:hover {
    background: #0E42D2;
  }
}

.divider {
  display: flex;
  align-items: center;
  margin: 32px 0;
  color: #86909c;
  font-size: 14px;

  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #e5e6eb;
  }

  span {
    padding: 0 16px;
  }
}

.login-tips {
  text-align: center;
  margin-top: 24px;

  p {
    font-size: 13px;
    color: #86909c;
    margin-bottom: 8px;
  }
}

.role-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;

  .arco-tag {
    cursor: pointer;
    transition: transform 0.2s;

    &:hover {
      transform: translateY(-2px);
    }
  }
}

/* 响应式 */
@media (max-width: 992px) {
  .login-wrapper {
    flex-direction: column;
    max-width: 480px;
  }

  .brand-section {
    padding: 40px 30px;
    min-height: 300px;
  }

  .brand-title {
    font-size: 28px;
  }

  .login-section {
    padding: 40px 30px;
  }
}

@media (max-width: 576px) {
  .brand-stats {
    grid-template-columns: 1fr;
  }

  .brand-section,
  .login-section {
    padding: 30px 20px;
  }
}
</style>
