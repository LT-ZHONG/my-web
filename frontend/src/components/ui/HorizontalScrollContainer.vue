<template>
  <div class="horizontal-scroll-wrapper">
    <div ref="scrollContainer" class="scroll-container scrollbar-hide">
      <div class="scroll-content">
        <slot />
      </div>
    </div>
    
    <n-button 
      v-if="showControls"
      class="scroll-btn scroll-btn-left"
      circle
      quaternary
      size="small"
      @click="scroll(-300)"
    >
      <template #icon>
        <n-icon :component="ChevronBackOutline" />
      </template>
    </n-button>
    
    <n-button 
      v-if="showControls"
      class="scroll-btn scroll-btn-right"
      circle
      quaternary
      size="small"
      @click="scroll(300)"
    >
      <template #icon>
        <n-icon :component="ChevronForwardOutline" />
      </template>
    </n-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NIcon } from 'naive-ui'
import { ChevronBackOutline, ChevronForwardOutline } from '@vicons/ionicons5'

// Props
const props = defineProps<{
  showControls?: boolean
}>()

// 获取滚动容器
const scrollContainer = ref<HTMLDivElement | null>(null)

// 滚动函数
const scroll = (amount: number) => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollBy({
      left: amount,
      behavior: 'smooth'
    })
  }
}
</script>

<style scoped>
.horizontal-scroll-wrapper {
  position: relative;
  width: 100%;
}

.scroll-container {
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 16px;
}

.scroll-content {
  display: flex;
  gap: 24px;
  width: max-content;
}

.scroll-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  background: rgba(26, 26, 26, 0.9);
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  z-index: 10;
}

.scroll-btn:hover {
  background: rgba(5, 217, 232, 0.2);
  color: var(--color-neon-blue);
  transform: translateY(-50%) scale(1.1);
}

.scroll-btn-left {
  left: -10px;
}

.scroll-btn-right {
  right: -10px;
}

@media (max-width: 768px) {
  .scroll-btn {
    display: none;
  }
  
  .scroll-content {
    gap: 16px;
  }
}
</style>

