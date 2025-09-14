<template>
  <a-layout-header 
    :style="{
      background: '#ffffff',
      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
      padding: '0 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 1000,
    }"
  >
    <!-- Logo和品牌名 -->
    <div :style="{ display: 'flex', alignItems: 'center' }">
      <router-link 
        to="/" 
        :style="{ display: 'flex', alignItems: 'center', textDecoration: 'none' }"
      >
        <div :style="{
          width: 40,
          height: 40,
          background: 'linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%)',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginRight: '12px',
          color: 'white',
          fontSize: '18px',
          fontWeight: 'bold',
        }">
          📸
        </div>
        <span :style="{
          fontSize: '20px',
          fontWeight: 600,
          background: 'linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }">
          我的生活
        </span>
      </router-link>
    </div>

    <!-- 桌面端导航菜单 -->
    <div class="hidden-mobile">
      <a-menu
        mode="horizontal"
        :selected-keys="[route.path]"
        :items="navItems"
        :style="{
          border: 'none',
          background: 'transparent',
          minWidth: '400px',
        }"
      />
    </div>

    <!-- 用户区域 -->
    <div :style="{ display: 'flex', alignItems: 'center', gap: '12px' }">
      <!-- 已登录状态 -->
      <a-dropdown 
        v-if="authStore.isAuthenticated"
        placement="bottomRight"
        :trigger="['click']"
      >
        <a-space :style="{ cursor: 'pointer' }">
          <a-avatar 
            :src="authStore.user?.avatar_url" 
            :icon="h(UserOutlined)"
          />
          <span 
            class="hidden-mobile" 
            :style="{ color: '#333' }"
          >
            {{ authStore.user?.nickname || authStore.user?.full_name || authStore.user?.username }}
          </span>
        </a-space>
        <template #overlay>
          <a-menu @click="handleUserMenuClick">
            <a-menu-item key="profile">
              <UserOutlined />
              个人资料
            </a-menu-item>
            <a-menu-item key="settings">
              <SettingOutlined />
              设置
            </a-menu-item>
            <a-menu-divider />
            <a-menu-item key="logout">
              <LogoutOutlined />
              退出登录
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>

      <!-- 未登录状态 -->
      <a-space v-else>
        <a-button 
          type="default" 
          :icon="h(LoginOutlined)"
          @click="router.push('/login')"
        >
          登录
        </a-button>
        <a-button 
          type="primary" 
          class="btn-primary"
          @click="router.push('/register')"
        >
          注册
        </a-button>
      </a-space>

      <!-- 移动端菜单按钮 -->
      <a-button 
        type="text" 
        :icon="h(MenuOutlined)"
        class="visible-mobile"
        @click="toggleMobileMenu"
      />
    </div>

    <!-- 移动端下拉菜单 -->
    <div 
      v-show="mobileMenuVisible"
      :style="{
        position: 'absolute',
        top: '100%',
        left: 0,
        right: 0,
        background: '#ffffff',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        zIndex: 999,
      }"
    >
      <a-menu
        mode="vertical"
        :selected-keys="[route.path]"
        :items="navItems"
        :style="{ border: 'none' }"
        @click="mobileMenuVisible = false"
      />
    </div>
  </a-layout-header>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  Layout as ALayout,
  Menu as AMenu,
  Button as AButton,
  Avatar as AAvatar,
  Dropdown as ADropdown,
  Space as ASpace,
} from 'ant-design-vue'
import {
  HomeOutlined,
  PictureOutlined,
  MessageOutlined,
  CrownOutlined,
  UserOutlined,
  LoginOutlined,
  LogoutOutlined,
  SettingOutlined,
  MenuOutlined,
} from '@ant-design/icons-vue'
import type { MenuProps } from 'ant-design-vue'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 响应式状态
const mobileMenuVisible = ref(false)

// 导航菜单项
const navItems = computed<MenuProps['items']>(() => [
  {
    key: '/',
    icon: h(HomeOutlined),
    label: h('router-link', { to: '/' }, '首页'),
  },
  {
    key: '/gallery',
    icon: h(PictureOutlined),
    label: h('router-link', { to: '/gallery' }, '照片视频'),
  },
  {
    key: '/chat',
    icon: h(MessageOutlined),
    label: h('router-link', { to: '/chat' }, '聊天'),
  },
  {
    key: '/vip',
    icon: h(CrownOutlined),
    label: h('router-link', { to: '/vip' }, 'VIP会员'),
  },
])

// 切换移动端菜单
const toggleMobileMenu = () => {
  mobileMenuVisible.value = !mobileMenuVisible.value
}

// 处理用户菜单点击
const handleUserMenuClick = ({ key }: { key: string }) => {
  switch (key) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      // TODO: 实现设置页面
      console.log('打开设置页面')
      break
    case 'logout':
      authStore.logout()
      router.push('/')
      break
  }
}
</script>

<style scoped>
.hidden-mobile {
  display: block;
}

.visible-mobile {
  display: none;
}

@media (max-width: 768px) {
  .hidden-mobile {
    display: none;
  }
  
  .visible-mobile {
    display: inline-flex;
  }
}

.btn-primary {
  background: linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ff8e53 0%, #ff6b35 100%);
}
</style>
