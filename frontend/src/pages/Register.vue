<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h2>注册</h2>
        <p>创建您的账户</p>
      </div>

      <a-form
        :model="form"
        :rules="rules"
        @finish="handleRegister"
        layout="vertical"
      >
        <a-form-item label="邮箱" name="email">
          <a-input 
            v-model:value="form.email"
            size="large"
            placeholder="请输入邮箱地址"
            :prefix="h(MailOutlined)"
          />
        </a-form-item>

        <a-form-item label="用户名" name="username">
          <a-input 
            v-model:value="form.username"
            size="large"
            placeholder="请输入用户名"
            :prefix="h(UserOutlined)"
          />
        </a-form-item>

        <a-form-item label="姓名" name="full_name">
          <a-input 
            v-model:value="form.full_name"
            size="large"
            placeholder="请输入姓名（可选）"
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

        <a-form-item label="确认密码" name="confirm_password">
          <a-input-password 
            v-model:value="form.confirm_password"
            size="large"
            placeholder="请再次输入密码"
            :prefix="h(LockOutlined)"
          />
        </a-form-item>

        <a-form-item>
          <a-checkbox v-model:checked="form.agree">
            我已阅读并同意
            <a href="#" class="terms-link">服务条款</a>
            和
            <a href="#" class="terms-link">隐私政策</a>
          </a-checkbox>
        </a-form-item>

        <a-form-item>
          <a-button 
            type="primary" 
            html-type="submit"
            size="large"
            :loading="authStore.loading"
            block
            class="register-btn"
            :disabled="!form.agree"
          >
            注册
          </a-button>
        </a-form-item>

        <a-form-item>
          <div class="login-link">
            已有账户？
            <router-link to="/login">立即登录</router-link>
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
import { MailOutlined, LockOutlined, UserOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const form = reactive({
  email: '',
  username: '',
  full_name: '',
  password: '',
  confirm_password: '',
  agree: false,
})

// 表单验证规则
const rules = {
  email: [
    { required: true, message: '请输入邮箱地址' },
    { type: 'email', message: '请输入正确的邮箱格式' },
  ],
  username: [
    { required: true, message: '请输入用户名' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线' },
  ],
  full_name: [
    { max: 50, message: '姓名长度不能超过50个字符' },
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码至少6个字符' },
  ],
  confirm_password: [
    { required: true, message: '请确认密码' },
    {
      validator: (_rule: any, value: string) => {
        if (value !== form.password) {
          return Promise.reject('两次输入的密码不一致')
        }
        return Promise.resolve()
      },
    },
  ],
}

// 处理注册
const handleRegister = async () => {
  try {
    await authStore.register({
      email: form.email,
      username: form.username,
      password: form.password,
      confirm_password: form.confirm_password,
      full_name: form.full_name || undefined,
    })
    
    message.success('注册成功！请登录')
    router.push('/login')
  } catch (error: any) {
    message.error(error.message || '注册失败')
    console.error('Register error:', error)
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff5f0 0%, #fff8f5 100%);
  padding: 20px;
}

.register-box {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.register-header p {
  color: #666;
  margin: 0;
}

.terms-link {
  color: #ff6b35;
  text-decoration: none;
}

.terms-link:hover {
  text-decoration: underline;
}

.register-btn {
  background: linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%);
  border: none;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.register-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #ff8e53 0%, #ff6b35 100%);
}

.login-link {
  text-align: center;
  color: #666;
}

.login-link a {
  color: #ff6b35;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
