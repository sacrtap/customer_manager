<template>
  <div class="login-container">
    <div class="login-card">
      <h1>客户运营中台</h1>
      <a-form @submit="handleLogin">
        <a-form-item label="用户名">
          <a-input v-model="username" />
        </a-form-item>
        <a-form-item label="密码">
          <a-input-password v-model="password" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit">登录</a-button>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const username = ref('')
const password = ref('')

const handleLogin = () => {
  console.log('Login:', username.value, password.value)
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 400px;
}
</style>
