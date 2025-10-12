<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides" :locale="zhCN">
    <n-message-provider>
      <n-notification-provider>
        <n-layout class="app-layout">
          <Header />
          <n-layout-content class="app-content">
            <router-view />
          </n-layout-content>
          <Footer />
        </n-layout>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { 
  NConfigProvider, 
  NLayout, 
  NLayoutContent, 
  NMessageProvider,
  NNotificationProvider,
  darkTheme,
  zhCN
} from 'naive-ui'
import type { GlobalThemeOverrides } from 'naive-ui'
import Header from './components/Layout/Header.vue'
import Footer from './components/Layout/Footer.vue'
import { useAuthStore } from '@/stores'

const authStore = useAuthStore()

// 自定义暗黑主题配置
const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#05D9E8', // 霓虹蓝作为主色调
    primaryColorHover: '#05D9E8cc',
    primaryColorPressed: '#05D9E899',
    primaryColorSuppl: '#05D9E8',
    infoColor: '#05D9E8',
    successColor: '#4CAF50',
    warningColor: '#FFF300',
    errorColor: '#FF2A6D', // 霓虹粉作为错误/强调色
    textColorBase: '#E5E5E5',
    bodyColor: '#0A0A0A',
    cardColor: '#1A1A1A',
    borderColor: '#333333',
  },
  Layout: {
    color: '#121212',
    textColor: '#E5E5E5',
  },
  Card: {
    color: '#1A1A1A',
    textColor: '#E5E5E5',
    borderColor: '#333333',
  },
  Input: {
    color: '#222222',
    colorFocus: '#222222',
    textColor: '#E5E5E5',
    border: '1px solid #333333',
    borderHover: '1px solid #05D9E8',
    borderFocus: '1px solid #05D9E8',
  },
  Button: {
    textColorPrimary: '#0A0A0A',
    textColorHoverPrimary: '#0A0A0A',
    textColorPressedPrimary: '#0A0A0A',
    colorPrimary: '#05D9E8',
    colorHoverPrimary: '#05D9E8cc',
    colorPressedPrimary: '#05D9E899',
  },
}

// 应用初始化
onMounted(async () => {
  // 初始化认证状态（如果有token，尝试获取用户信息）
  try {
    await authStore.initAuth()
  } catch (error) {
    // 初始化失败也没关系，用户可以重新登录
    console.log('Auth initialization failed, user needs to login')
  }
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-dark-900);
}

.app-content {
  flex: 1;
  padding: 0;
}
</style>
