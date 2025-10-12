<template>
  <n-button
    v-if="showBackToTop"
    class="back-to-top-btn"
    circle
    type="primary"
    size="large"
    @click="scrollToTop"
  >
    <template #icon>
      <n-icon :component="ChevronUp" />
    </template>
  </n-button>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { NButton, NIcon } from 'naive-ui'
import { ChevronUp } from '@vicons/ionicons5'

// 显示状态
const showBackToTop = ref(false)

// 监听滚动事件
const handleScroll = () => {
  showBackToTop.value = window.scrollY > 500
}

// 挂载和卸载时处理事件监听
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// 滚动到顶部
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}
</script>

<style scoped>
.back-to-top-btn {
  position: fixed;
  bottom: 32px;
  right: 32px;
  width: 48px;
  height: 48px;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(5, 217, 232, 0.4);
  transition: all 0.3s ease;
}

.back-to-top-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(5, 217, 232, 0.6);
}

@media (max-width: 768px) {
  .back-to-top-btn {
    bottom: 20px;
    right: 20px;
    width: 44px;
    height: 44px;
  }
}
</style>

