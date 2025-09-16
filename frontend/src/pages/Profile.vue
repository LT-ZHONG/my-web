<template>
  <div class="profile-container">
    <a-typography-title :level="2">个人资料</a-typography-title>
    
    <a-row :gutter="24">
      <a-col :span="24">
        <a-card title="基本信息">
          <div class="user-info-header">
            <h3>@{{ profile?.username }}</h3>
            <a-tag v-if="profile?.is_vip" color="gold">
              <template #icon>
                <crown-outlined />
              </template>
              VIP用户
            </a-tag>
          </div>
          <a-divider />
          <a-form 
            :model="form" 
            :rules="rules"
            layout="vertical"
            @finish="handleSubmit"
          >
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="用户名" name="username">
                  <a-input v-model:value="form.username" disabled />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="邮箱" name="email">
                  <a-input v-model:value="form.email" disabled />
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-form-item label="姓名" name="full_name">
              <a-input v-model:value="form.full_name" placeholder="请输入姓名" />
            </a-form-item>
            
            <a-form-item label="手机号" name="phone">
              <a-input v-model:value="form.phone" placeholder="请输入手机号" />
            </a-form-item>
            
            <a-form-item label="个人简介" name="bio">
              <a-textarea 
                v-model:value="form.bio" 
                :rows="4"
                placeholder="介绍一下自己..."
                :max-length="500"
                show-count
              />
            </a-form-item>
            
            <a-form-item>
              <a-space>
                <a-button 
                  type="primary" 
                  html-type="submit"
                  :loading="userStore.loading"
                >
                  保存更改
                </a-button>
                <a-button @click="resetForm">重置</a-button>
              </a-space>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
    </a-row>

    <!-- VIP状态卡片 -->
    <a-row :gutter="24" style="margin-top: 24px">
      <a-col :span="24">
        <a-card title="账户状态">
          <a-row :gutter="16">
            <a-col :span="8">
              <a-statistic 
                title="注册时间" 
                :value="formatDate(profile?.created_at)" 
              />
            </a-col>
            <a-col :span="8">
              <a-statistic 
                title="VIP状态" 
                :value="profile?.is_vip ? 'VIP用户' : '普通用户'"
                :value-style="{ color: profile?.is_vip ? '#f5a623' : '#666' }"
              />
            </a-col>
            <a-col :span="8" v-if="profile?.is_vip && profile?.vip_expire_at">
              <a-statistic 
                title="VIP到期" 
                :value="formatDate(profile.vip_expire_at)"
                :value-style="{ color: '#f5a623' }"
              />
            </a-col>
          </a-row>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, h, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  Typography,
  Row as ARow,
  Col as ACol,
  Card as ACard,
  Button as AButton,
  Form as AForm,
  Input as AInput,
  Space as ASpace,
  Tag as ATag,
  Statistic as AStatistic,
  Divider as ADivider,
} from 'ant-design-vue'
import { 
  CrownOutlined 
} from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { formatDate, validatePhone } from '../utils'
import type { UserUpdateData } from '../types'

const authStore = useAuthStore()
const userStore = useUserStore()

// 用户资料信息 - 使用计算属性以保持响应式
const profile = computed(() => authStore.user || userStore.profile)

// 表单数据
const form = reactive({
  username: '',
  email: '',
  full_name: '',
  phone: '',
  bio: '',
})

// 表单验证规则
const rules = {
  full_name: [
    { max: 50, message: '姓名长度不能超过50个字符' }
  ],
  phone: [
    { 
      validator: (_rule: any, value: string) => {
        if (value && !validatePhone(value)) {
          return Promise.reject('请输入正确的手机号格式')
        }
        return Promise.resolve()
      }
    }
  ],
  bio: [
    { max: 500, message: '个人简介不能超过500个字符' }
  ]
}

// 初始化表单数据
const initForm = () => {
  if (profile.value) {
    form.username = profile.value.username
    form.email = profile.value.email
    form.full_name = profile.value.full_name || ''
    form.phone = profile.value.phone || ''
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
    const updateData: UserUpdateData = {
      full_name: form.full_name || undefined,
      phone: form.phone || undefined,
      bio: form.bio || undefined,
    }

    await userStore.updateProfile(updateData)
    message.success('个人资料更新成功！')
    
    // 更新本地显示
    if (userStore.profile) {
      profile.value = userStore.profile
      // 同时更新auth store中的用户信息
      authStore.updateUser(userStore.profile)
    }
  } catch (error) {
    console.error('Profile update failed:', error)
  }
}

// 加载个人资料
const loadProfile = async () => {
  try {
    await userStore.getProfile()
    if (userStore.profile) {
      profile.value = userStore.profile
      initForm()
    }
  } catch (error) {
    console.error('Failed to load profile:', error)
    // 如果获取个人资料失败但authStore有用户数据，使用authStore的数据
    if (authStore.user) {
      profile.value = authStore.user
      initForm()
    }
  }
}

// 组件挂载时加载数据
onMounted(() => {
  // 优先使用authStore的用户数据
  if (authStore.user) {
    profile.value = authStore.user
    initForm()
  } else if (!profile.value) {
    loadProfile()
  } else {
    initForm()
  }
})
</script>

<style scoped>
.profile-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.user-info-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.user-info-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.ant-statistic :deep(.ant-statistic-title) {
  font-size: 14px;
  color: #666;
}

.ant-statistic :deep(.ant-statistic-content) {
  font-size: 16px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .profile-container {
    padding: 16px;
  }
}
</style>
