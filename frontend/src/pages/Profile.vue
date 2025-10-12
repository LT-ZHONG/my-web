<template>
  <div class="profile-page">
    <!-- 页头 -->
    <section class="profile-header">
      <h1 class="page-title text-neon-purple">个人资料</h1>
      <p class="page-subtitle">管理您的账户信息</p>
    </section>
    
    <!-- 用户卡片 -->
    <div class="user-card">
      <div class="user-avatar">
        <div class="avatar-circle">
          {{ profile?.username?.charAt(0).toUpperCase() }}
        </div>
        <n-tag v-if="profile?.is_vip" class="vip-badge" type="warning">
          <template #icon>
            <n-icon><star-outline /></n-icon>
          </template>
          VIP
        </n-tag>
      </div>
      
      <div class="user-info">
        <h2 class="username">@{{ profile?.username }}</h2>
        <p class="email">{{ profile?.email }}</p>
      </div>
    </div>
    
    <!-- 统计数据 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <n-icon size="32" :color="profile?.is_vip ? 'var(--color-neon-pink)' : '#666'">
            <star-outline v-if="profile?.is_vip" />
            <person-outline v-else />
          </n-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">会员状态</div>
          <div class="stat-value">{{ profile?.is_vip ? 'VIP用户' : '普通用户' }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <n-icon size="32" color="var(--color-neon-blue)">
            <wallet-outline />
          </n-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">积分余额</div>
          <div class="stat-value">{{ profile?.credits || 0 }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <n-icon size="32" color="var(--color-neon-purple)">
            <calendar-outline />
          </n-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">注册时间</div>
          <div class="stat-value small">{{ formatDate(profile?.created_at) }}</div>
        </div>
      </div>
      
      <div v-if="profile?.is_vip && profile?.vip_expire_at" class="stat-card">
        <div class="stat-icon">
          <n-icon size="32" color="var(--color-neon-pink)">
            <time-outline />
          </n-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">VIP到期</div>
          <div class="stat-value small">{{ formatDate(profile.vip_expire_at) }}</div>
        </div>
      </div>
    </div>
    
    <!-- 编辑表单 -->
    <div class="form-card">
      <h3 class="form-title">编辑资料</h3>
      <n-form 
        ref="formRef"
        :model="form" 
        :rules="rules"
        label-placement="top"
        @submit.prevent="handleSubmit"
      >
        <n-form-item path="bio" label="个人简介">
          <n-input 
            v-model:value="form.bio" 
            type="textarea"
            :rows="4"
            placeholder="介绍一下自己..."
            :maxlength="500"
            show-count
            class="dark-input"
          />
        </n-form-item>
        
        <n-form-item>
          <n-space>
            <n-button 
              class="save-btn"
              attr-type="submit"
              :loading="userStore.loading"
            >
              保存更改
            </n-button>
            <n-button class="reset-btn" @click="resetForm">重置</n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useMessage } from 'naive-ui'
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NSpace,
  NTag,
  NIcon,
} from 'naive-ui'
import { 
  StarOutline,
  PersonOutline,
  TimeOutline,
  WalletOutline,
  CalendarOutline,
} from '@vicons/ionicons5'
import { useAuthStore } from '@/stores'
import { useUserStore } from '@/stores'
import { formatDate } from '@/utils'
import type { UserUpdateData } from '@/types'

const authStore = useAuthStore()
const userStore = useUserStore()
const message = useMessage()
const formRef = ref()

// 用户资料信息 - 使用计算属性以保持响应式
const profile = computed(() => authStore.user || userStore.profile)

// 表单数据
const form = reactive({
  username: '',
  email: '',
  bio: '',
})

// 表单验证规则
const rules = {
  bio: [
    { max: 500, message: '个人简介不能超过500个字符', trigger: 'blur' }
  ]
}

// 初始化表单数据
const initForm = () => {
  if (profile.value) {
    form.username = profile.value.username
    form.email = profile.value.email
    form.bio = profile.value.bio || ''
  }
}

// 重置表单
const resetForm = () => {
  initForm()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    const updateData: UserUpdateData = {
      bio: form.bio || undefined,
    }

    await userStore.updateProfile(updateData)
    message.success('个人资料更新成功！')
    
    // 更新本地显示
    if (userStore.profile) {
      // 同时更新auth store中的用户信息
      authStore.updateUser(userStore.profile)
    }
  } catch (error: any) {
    if (error?.errorFields) {
      // 表单验证错误
      return
    }
    console.error('Profile update failed:', error)
  }
}

// 加载个人资料
const loadProfile = async () => {
  try {
    await userStore.getProfile()
    if (userStore.profile) {
      initForm()
    }
  } catch (error) {
    console.error('Failed to load profile:', error)
    // 如果获取个人资料失败但authStore有用户数据，使用authStore的数据
    if (authStore.user) {
      initForm()
    }
  }
}

// 组件挂载时加载数据
onMounted(() => {
  // 优先使用authStore的用户数据
  if (authStore.user) {
    initForm()
  } else if (!profile.value) {
    loadProfile()
  } else {
    initForm()
  }
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: var(--color-dark-900);
  padding: 80px 24px 48px;
}

/* 页头 */
.profile-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: bold;
  margin: 0 0 16px;
  text-shadow: 
    0 0 20px rgba(211, 0, 197, 0.5),
    0 0 40px rgba(211, 0, 197, 0.3);
}

.text-neon-purple {
  color: var(--color-neon-purple);
}

.page-subtitle {
  font-size: 1.125rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* 用户卡片 */
.user-card {
  max-width: 800px;
  margin: 0 auto 48px;
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 16px;
  padding: 32px;
  display: flex;
  align-items: center;
  gap: 32px;
  transition: all 0.3s ease;
}

.user-card:hover {
  border-color: var(--color-neon-purple);
  box-shadow: 0 8px 32px rgba(211, 0, 197, 0.2);
}

.user-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-neon-purple), var(--color-neon-pink));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: bold;
  color: white;
  box-shadow: 0 8px 24px rgba(211, 0, 197, 0.3);
}

.vip-badge {
  position: absolute;
  bottom: -8px;
  right: -8px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border: none;
  box-shadow: 0 4px 16px rgba(255, 215, 0, 0.4);
}

.user-info {
  flex: 1;
}

.username {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 8px;
}

.email {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* 统计数据网格 */
.stats-grid {
  max-width: 1200px;
  margin: 0 auto 48px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.stat-card {
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: var(--color-neon-blue);
  box-shadow: 0 8px 24px rgba(5, 217, 232, 0.2);
}

.stat-icon {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-value.small {
  font-size: 1.125rem;
}

/* 表单卡片 */
.form-card {
  max-width: 800px;
  margin: 0 auto;
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 16px;
  padding: 32px;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 24px;
}

.form-card :deep(.n-form-item-label) {
  color: var(--color-text-primary);
}

.form-card :deep(.n-input) {
  background: var(--color-dark-700);
  border-color: var(--color-dark-600);
}

.form-card :deep(.n-input__input-el),
.form-card :deep(.n-input__textarea-el) {
  color: var(--color-text-primary);
}

.form-card :deep(.n-input:hover) {
  border-color: var(--color-neon-purple);
}

.form-card :deep(.n-input.n-input--focus) {
  border-color: var(--color-neon-purple);
  box-shadow: 0 0 0 2px rgba(211, 0, 197, 0.2);
}

.save-btn {
  background: linear-gradient(135deg, var(--color-neon-purple), var(--color-neon-pink));
  border: none;
  color: white;
  font-weight: 600;
  padding: 12px 32px;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(211, 0, 197, 0.4);
}

.reset-btn {
  background: transparent;
  border: 1px solid var(--color-dark-600);
  color: var(--color-text-secondary);
  padding: 12px 32px;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.reset-btn:hover {
  border-color: var(--color-neon-blue);
  color: var(--color-neon-blue);
}

/* 响应式 */
@media (max-width: 768px) {
  .profile-page {
    padding: 64px 16px 32px;
  }
  
  .user-card {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .form-card {
    padding: 24px;
  }
}
</style>
