<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h2>注册</h2>
        <p>创建您的账户</p>
      </div>

      <n-form
        ref="formRef"
        :model="form"
        :rules="rules"
        @submit.prevent="handleRegister"
        size="large"
      >
        <n-form-item path="email" label="邮箱">
          <n-input 
            v-model:value="form.email"
            placeholder="请输入邮箱地址"
          >
            <template #prefix>
              <n-icon><mail-outline /></n-icon>
            </template>
          </n-input>
        </n-form-item>

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

        <n-form-item path="full_name" label="姓名">
          <n-input 
            v-model:value="form.full_name"
            placeholder="请输入姓名（可选）"
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

        <n-form-item path="confirm_password" label="确认密码">
          <n-input 
            v-model:value="form.confirm_password"
            type="password"
            show-password-on="click"
            placeholder="请再次输入密码"
          >
            <template #prefix>
              <n-icon><lock-closed-outline /></n-icon>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item>
          <n-checkbox v-model:checked="form.agree">
            我已阅读并同意
            <a href="#" class="terms-link">服务条款</a>
            和
            <a href="#" class="terms-link">隐私政策</a>
          </n-checkbox>
        </n-form-item>

        <n-form-item>
          <n-button 
            type="primary" 
            attr-type="submit"
            :loading="authStore.loading"
            block
            class="register-btn"
            :disabled="!form.agree"
          >
            注册
          </n-button>
        </n-form-item>

        <n-form-item>
          <div class="login-link">
            已有账户？
            <router-link to="/login">立即登录</router-link>
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
import { MailOutline, LockClosedOutline, PersonOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()
const formRef = ref()

// 表单数据
const form = reactive({
  email: '',
  username: '',
  full_name: '',
  password: '',
  confirm_password: '',
  agree: false,
})

// 自定义验证规则 - 确认密码
const validateConfirmPassword = (_rule: any, value: string) => {
  if (!value) {
    return new Error('请确认密码')
  }
  if (value !== form.password) {
    return new Error('两次输入的密码不一致')
  }
  return true
}

// 表单验证规则
const rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'input'] },
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' },
  ],
  full_name: [
    { max: 50, message: '姓名长度不能超过50个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: ['blur', 'input'] },
  ],
}

// 处理注册
const handleRegister = async () => {
  try {
    await formRef.value?.validate()
    
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
    if (error?.errorFields) {
      // 表单验证错误
      return
    }
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
  background: var(--color-dark-900);
  padding: 20px;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.1'/%3E%3C/svg%3E");
}

.register-box {
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

.register-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--color-neon-pink), var(--color-neon-purple), var(--color-neon-blue));
}

.register-header {
  text-align: center;
  margin-bottom: 40px;
}

.register-header h2 {
  font-family: 'Playfair Display', serif;
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--color-neon-pink);
  margin: 0 0 12px 0;
  text-shadow: 0 0 20px rgba(255, 42, 109, 0.5);
}

.register-header p {
  color: var(--color-text-secondary);
  margin: 0;
  font-size: 1rem;
}

.register-box :deep(.n-form-item-label) {
  color: var(--color-text-primary);
  font-weight: 500;
}

.register-box :deep(.n-input) {
  background: var(--color-dark-700);
  border-color: var(--color-dark-600);
  transition: all 0.3s ease;
}

.register-box :deep(.n-input__input-el) {
  color: var(--color-text-primary);
}

.register-box :deep(.n-input:hover) {
  border-color: var(--color-neon-pink);
}

.register-box :deep(.n-input.n-input--focus) {
  border-color: var(--color-neon-pink);
  box-shadow: 0 0 0 2px rgba(255, 42, 109, 0.2);
}

.register-box :deep(.n-input__prefix) {
  color: var(--color-neon-pink);
}

.register-box :deep(.n-checkbox) {
  color: var(--color-text-primary);
}

.terms-link {
  color: var(--color-neon-purple);
  text-decoration: none;
  transition: all 0.3s ease;
}

.terms-link:hover {
  color: var(--color-neon-blue);
  text-shadow: 0 0 10px rgba(5, 217, 232, 0.5);
}

.register-btn {
  background: linear-gradient(135deg, var(--color-neon-pink), var(--color-neon-purple));
  border: none;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  transition: all 0.3s ease;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 42, 109, 0.4);
}

.register-btn:active:not(:disabled) {
  transform: translateY(0);
}

.register-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  color: var(--color-text-secondary);
  width: 100%;
}

.login-link a {
  color: var(--color-neon-blue);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.login-link a:hover {
  color: var(--color-neon-purple);
  text-shadow: 0 0 10px rgba(211, 0, 197, 0.5);
}

@media (max-width: 480px) {
  .register-box {
    padding: 32px 24px;
  }
  
  .register-header h2 {
    font-size: 1.875rem;
  }
}
</style>
