<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>登录</h2>
        <p>欢迎回到我的生活</p>
      </div>

      <a-form
        :model="form"
        :rules="rules"
        @finish="handleLogin"
        layout="vertical"
      >
        <a-form-item label="用户名" name="username">
          <a-input 
            v-model:value="form.username"
            size="large"
            placeholder="请输入用户名"
            :prefix="h(UserOutlined)"
          />
        </a-form-item>

        <a-form-item label="密码" name="password">
          <a-input-password 
            v-model:value="form.password"
            size="large"
            placeholder="请输入密码"
            :prefix="h(LockOutlined)"
          />
        </a-form-item>

        <a-form-item>
          <div class="login-options">
            <a-checkbox v-model:checked="form.remember">
              记住我
            </a-checkbox>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>
        </a-form-item>

        <a-form-item>
          <a-button 
            type="primary" 
            html-type="submit"
            size="large"
            :loading="authStore.loading"
            block
            class="login-btn"
          >
            登录
          </a-button>
        </a-form-item>

        <a-form-item>
          <div class="register-link">
            还没有账户？
            <router-link to="/register">立即注册</router-link>
          </div>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, h } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  Form as AForm,
  Input as AInput,
  Button as AButton,
  Checkbox as ACheckbox,
} from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const form = reactive({
  username: '',
  password: '',
  remember: false,
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符' },
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码至少6个字符' },
  ],
}

// 处理登录
const handleLogin = async () => {
  try {
    await authStore.login({
      username: form.username,
      password: form.password,
    })
    
    message.success('登录成功！')
    router.push('/')
  } catch (error: any) {
    message.error(error.message || '登录失败')
    console.error('Login error:', error)
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff5f0 0%, #fff8f5 100%);
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.login-header p {
  color: #666;
  margin: 0;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-link {
  color: #ff6b35;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.login-btn {
  background: linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%);
  border: none;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.login-btn:hover {
  background: linear-gradient(135deg, #ff8e53 0%, #ff6b35 100%);
}

.register-link {
  text-align: center;
  color: #666;
}

.register-link a {
  color: #ff6b35;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-box {
    padding: 24px;
  }
}
</style>
