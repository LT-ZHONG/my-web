<template>
  <header 
    :class="['site-header', { 'header-scrolled': isScrolled }]"
  >
    <div class="header-container">
      <!-- Logo和品牌名 -->
      <router-link to="/" class="brand-logo">
        <span class="brand-text text-neon-blue animate-glow">LUMINOUS</span>
      </router-link>

      <!-- 桌面端导航菜单 -->
      <nav class="desktop-nav hidden-mobile">
        <router-link
          v-for="item in navItems"
          :key="item.key"
          :to="item.key"
          class="nav-link"
          :class="{ 'nav-link-active': route.path === item.key }"
        >
          {{ item.label }}
        </router-link>
      </nav>

      <!-- 用户区域 -->
      <div class="user-section">
        <!-- 已登录状态 -->
        <n-dropdown 
          v-if="authStore.isAuthenticated"
          placement="bottom-end"
          trigger="click"
          :options="userMenuOptions"
          @select="handleUserMenuSelect"
        >
          <div class="user-info">
            <n-avatar 
              round 
              :size="36"
              class="user-avatar"
              :style="{ background: 'var(--color-neon-blue)', color: 'var(--color-dark-900)' }"
            >
              {{ authStore.user?.username?.charAt(0).toUpperCase() }}
            </n-avatar>
            <span class="user-name hidden-mobile">
              {{ authStore.user?.nickname || authStore.user?.full_name || authStore.user?.username }}
            </span>
          </div>
        </n-dropdown>

        <!-- 未登录状态 -->
        <n-space v-else :size="12">
          <n-button 
            quaternary
            @click="router.push('/login')"
            class="btn-login"
          >
            <template #icon>
              <n-icon><LogInOutline /></n-icon>
            </template>
            <span class="hidden-mobile">登录</span>
          </n-button>
          <n-button 
            type="primary" 
            @click="router.push('/register')"
            class="btn-register"
          >
            注册
          </n-button>
        </n-space>

        <!-- 移动端菜单按钮 -->
        <n-button 
          quaternary
          circle
          class="visible-mobile mobile-menu-btn"
          @click="toggleMobileMenu"
        >
          <template #icon>
            <n-icon :component="mobileMenuVisible ? Close : Menu" />
          </template>
        </n-button>
      </div>
    </div>

    <!-- 移动端下拉菜单 -->
    <div 
      class="mobile-menu"
      :class="{ 'mobile-menu-open': mobileMenuVisible }"
    >
      <div class="mobile-menu-items">
        <router-link
          v-for="item in navItems"
          :key="item.key"
          :to="item.key"
          class="mobile-nav-link"
          @click="closeMobileMenu"
        >
          {{ item.label }}
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, h, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  NButton,
  NAvatar,
  NDropdown,
  NSpace,
  NIcon,
  type MenuOption,
} from 'naive-ui'
import {
  PersonOutline,
  LogInOutline,
  LogOutOutline,
  SettingsOutline,
  Menu,
  Close,
} from '@vicons/ionicons5'
import { useAuthStore } from '@/stores'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 响应式状态
const mobileMenuVisible = ref(false)
const isScrolled = ref(false)

// 渲染图标的辅助函数
const renderIcon = (icon: any) => {
  return () => h(NIcon, null, { default: () => h(icon) })
}

// 导航菜单项
const navItems = [
  { key: '/', label: '首页' },
  { key: '/gallery', label: '作品' },
  { key: '/profile', label: '关于' },
  { key: '/chat', label: '联系' },
  { key: '/recharge', label: '购买作品' },
]

// 用户菜单选项
const userMenuOptions = computed<MenuOption[]>(() => [
  {
    key: 'profile',
    icon: renderIcon(PersonOutline),
    label: '个人资料',
  },
  {
    key: 'settings',
    icon: renderIcon(SettingsOutline),
    label: '设置',
  },
  {
    type: 'divider',
    key: 'd1',
  },
  {
    key: 'logout',
    icon: renderIcon(LogOutOutline),
    label: '退出登录',
  },
])

// 监听滚动事件
const handleScroll = () => {
  isScrolled.value = window.scrollY > 100
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// 切换移动端菜单
const toggleMobileMenu = () => {
  mobileMenuVisible.value = !mobileMenuVisible.value
}

// 关闭移动端菜单
const closeMobileMenu = () => {
  mobileMenuVisible.value = false
}

// 处理用户菜单选择
const handleUserMenuSelect = (key: string) => {
  switch (key) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
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
.site-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: transparent;
  transition: all 0.3s ease;
}

.header-scrolled {
  background: rgba(18, 18, 18, 0.95);
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-logo {
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-text {
  font-family: var(--font-serif);
  font-size: 28px;
  font-weight: 900;
  letter-spacing: 1px;
}

.desktop-nav {
  display: flex;
  gap: 32px;
  align-items: center;
}

.nav-link {
  color: var(--color-text-primary);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  padding: 8px 4px;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--color-neon-blue);
  transition: width 0.3s ease;
}

.nav-link:hover {
  color: var(--color-neon-blue);
}

.nav-link:hover::after,
.nav-link-active::after {
  width: 100%;
}

.nav-link-active {
  color: var(--color-neon-blue);
}

.user-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 24px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(5, 217, 232, 0.1);
}

.user-name {
  color: var(--color-text-primary);
  font-size: 14px;
  font-weight: 500;
}

.btn-login {
  color: var(--color-text-primary);
}

.btn-login:hover {
  color: var(--color-neon-blue);
}

.btn-register {
  background: var(--color-neon-blue);
  color: var(--color-dark-900);
  font-weight: 600;
}

.mobile-menu-btn {
  color: var(--color-text-primary);
}

.mobile-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(18, 18, 18, 0.98);
  backdrop-filter: blur(12px);
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.mobile-menu-open {
  max-height: 400px;
  border-bottom: 1px solid var(--color-dark-600);
}

.mobile-menu-items {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mobile-nav-link {
  color: var(--color-text-primary);
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-dark-600);
  transition: all 0.3s ease;
}

.mobile-nav-link:hover {
  color: var(--color-neon-blue);
  padding-left: 8px;
}

.hidden-mobile {
  display: flex;
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
  
  .brand-text {
    font-size: 24px;
  }
  
  .header-container {
    padding: 12px 16px;
  }
}
</style>
