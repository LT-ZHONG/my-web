<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>登录</h2>
        <p>欢迎回到我的生活</p>
      </div>

      <n-form
        ref="formRef"
        :model="form"
        :rules="rules"
        @submit.prevent="handleLogin"
        size="large"
      >
        <n-form-item path="username" label="用户名">
          <n-input 
            v-model:value="form.username"
            placeholder="请输入用户名"
          >
            <template #prefix>
              <n-icon><person-outline /></n-icon>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item path="password" label="密码">
          <n-input 
            v-model:value="form.password"
            type="password"
            show-password-on="click"
            placeholder="请输入密码"
          >
            <template #prefix>
              <n-icon><lock-closed-outline /></n-icon>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item>
          <div class="login-options">
            <n-checkbox v-model:checked="form.remember">
              记住我
            </n-checkbox>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>
        </n-form-item>

        <n-form-item>
          <n-button 
            type="primary" 
            attr-type="submit"
            :loading="authStore.loading"
            block
            class="login-btn"
          >
            登录
          </n-button>
        </n-form-item>

        <n-form-item>
          <div class="register-link">
            还没有账户？
            <router-link to="/register">立即注册</router-link>
          </div>
        </n-form-item>
      </n-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  NForm,
  NFormItem,
  NInput,
  NButton,
  NCheckbox,
  NIcon,
} from 'naive-ui'
import { PersonOutline, LockClosedOutline } from '@vicons/ionicons5'
import { useAuthStore } from '@/stores'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()
const formRef = ref()

// 表单数据
const form = reactive({
  username: '',
  password: '',
  remember: false,
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' },
  ],
}

// 处理登录
const handleLogin = async () => {
  try {
    await formRef.value?.validate()
    
    await authStore.login({
      username: form.username,
      password: form.password,
    })
    
    message.success('登录成功！')
    router.push('/')
  } catch (error: any) {
    if (error?.errorFields) {
      // 表单验证错误
      return
    }
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
  background: var(--color-dark-900);
  padding: 20px;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.1'/%3E%3C/svg%3E");
}

.login-box {
  width: 100%;
  max-width: 450px;
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  padding: 48px 40px;
  border-radius: 24px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
  position: relative;
  overflow: hidden;
}

.login-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--color-neon-blue), var(--color-neon-purple), var(--color-neon-pink));
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h2 {
  font-family: 'Playfair Display', serif;
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--color-neon-blue);
  margin: 0 0 12px 0;
  text-shadow: 0 0 20px rgba(5, 217, 232, 0.5);
}

.login-header p {
  color: var(--color-text-secondary);
  margin: 0;
  font-size: 1rem;
}

.login-box :deep(.n-form-item-label) {
  color: var(--color-text-primary);
  font-weight: 500;
}

.login-box :deep(.n-input) {
  background: var(--color-dark-700);
  border-color: var(--color-dark-600);
  transition: all 0.3s ease;
}

.login-box :deep(.n-input__input-el) {
  color: var(--color-text-primary);
}

.login-box :deep(.n-input:hover) {
  border-color: var(--color-neon-blue);
}

.login-box :deep(.n-input.n-input--focus) {
  border-color: var(--color-neon-blue);
  box-shadow: 0 0 0 2px rgba(5, 217, 232, 0.2);
}

.login-box :deep(.n-input__prefix) {
  color: var(--color-neon-blue);
}

.login-box :deep(.n-checkbox) {
  color: var(--color-text-primary);
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.forgot-link {
  color: var(--color-neon-purple);
  text-decoration: none;
  transition: all 0.3s ease;
}

.forgot-link:hover {
  color: var(--color-neon-pink);
  text-shadow: 0 0 10px rgba(255, 42, 109, 0.5);
}

.login-btn {
  background: linear-gradient(135deg, var(--color-neon-blue), var(--color-neon-purple));
  border: none;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-dark-900);
  transition: all 0.3s ease;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(5, 217, 232, 0.4);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
}

.register-link {
  text-align: center;
  color: var(--color-text-secondary);
  width: 100%;
}

.register-link a {
  color: var(--color-neon-pink);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.register-link a:hover {
  color: var(--color-neon-purple);
  text-shadow: 0 0 10px rgba(211, 0, 197, 0.5);
}

@media (max-width: 480px) {
  .login-box {
    padding: 32px 24px;
  }
  
  .login-header h2 {
    font-size: 1.875rem;
  }
}
</style>
