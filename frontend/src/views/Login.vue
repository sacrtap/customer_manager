<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>客户运营中台</h1>
        <p>内部运营中台客户信息管理与运营系统</p>
      </div>

      <Form ref="formRef" :model="form" layout="vertical">
        <FormItem field="username" :rules="usernameRules" label="用户名">
          <Input v-model="form.username" placeholder="请输入用户名" size="large" />
        </FormItem>

        <FormItem field="password" :rules="passwordRules" label="密码">
          <InputPassword v-model="form.password" placeholder="请输入密码" size="large" />
        </FormItem>

        <FormItem>
          <Button
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            long
            @click="handleLogin"
          >
            登录
          </Button>
        </FormItem>
      </Form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Message, Form, FormItem, Input, InputPassword, Button } from '@arco-design/web-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref()

const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)

const usernameRules = [
  { required: true, message: '请输入用户名' },
  { minLength: 3, message: '用户名至少 3 个字符' }
]

const passwordRules = [
  { required: true, message: '请输入密码' },
  { minLength: 6, message: '密码至少 6 个字符' }
]

const handleLogin = async () => {
  try {
    const error = await formRef.value?.validate()
    if (error) return

    loading.value = true

    await userStore.login(form.username, form.password)

    Message.success('登录成功')

    const redirect = route.query.redirect as string
    router.push(redirect || '/dashboard')
  } catch (error: any) {
    Message.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

  .login-box {
    width: 400px;
    padding: 40px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);

    .login-header {
      text-align: center;
      margin-bottom: 40px;

      h1 {
        font-size: 28px;
        color: #1f2937;
        margin-bottom: 8px;
      }

      p {
        color: #86909c;
        font-size: 14px;
      }
    }
  }
}
</style>
