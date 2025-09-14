<template>
  <a-layout class="app-layout">
    <Header />
    <a-layout-content class="app-content">
      <router-view />
    </a-layout-content>
    <Footer />
  </a-layout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { Layout as ALayout } from 'ant-design-vue'
import Header from './components/Layout/Header.vue'
import Footer from './components/Layout/Footer.vue'
import { useAuthStore } from '@/stores'

const authStore = useAuthStore()

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
}

.app-content {
  padding: 0;
}
</style>
