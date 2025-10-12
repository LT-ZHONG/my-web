<template>
  <div class="work-card card-hover">
    <div class="work-image-wrapper" @click="handleClick">
      <n-image
        :src="getFullFileUrl(props.work.thumbnail_url || props.work.file_url)"
        :alt="props.work.title"
        :class="['work-image', !work.is_paid && !work.isVideo ? 'blur-image' : '']"
        object-fit="cover"
      />
      
      <!-- 视频播放按钮 -->
      <div v-if="work.isVideo && !work.is_paid" class="video-overlay">
        <div class="play-button" @click="handlePreview">
          <n-icon :component="Play" :size="24" />
        </div>
        <div class="video-preview-label">免费预览 10 秒</div>
      </div>
      
      <!-- 付费标签 -->
      <div class="work-badge premium-badge">
        {{ work.purchased ? '已购买' : '付费' }}
      </div>
      
      <!-- 模糊遮罩提示 -->
      <div v-if="!work.is_paid && !work.isVideo" class="blur-overlay">
        <div class="blur-message">
          点击购买查看高清作品
        </div>
      </div>
      
      <!-- 解锁按钮 -->
      <div v-if="!work.is_paid" class="unlock-overlay" @click="handleUnlock">
        <n-button type="error" size="large" class="unlock-button">
          <template #icon>
            <n-icon :component="LockClosed" />
          </template>
          {{ work.isVideo ? '解锁完整视频' : '立即解锁' }}
        </n-button>
      </div>
    </div>
    
    <div class="work-info">
      <h4 class="work-title">{{ work.title }}</h4>
      <p class="work-meta">{{ work.category || work.type }}</p>
      <div class="work-footer">
        <p class="work-price">
          <span v-if="work.price">¥{{ work.price }}</span>
          <span v-else>{{ work.cost }} 积分</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NImage, NButton, NIcon, useMessage } from 'naive-ui'
import { Play, LockClosed } from '@vicons/ionicons5'
import type { MediaItem } from '@/types'
import { getFullFileUrl } from '@/utils'

interface Work {
  id: number
  title: string
  category?: string
  type?: string
  description?: string
  url?: string
  imageUrl?: string
  isVideo?: boolean
  price?: number
  cost?: number
  salesCount?: number
  downloads?: number
  purchased?: boolean
  isPremium?: boolean
}

const props = defineProps<{
  work: MediaItem
}>()

const emit = defineEmits<{
  (e: 'unlock', work: Work): void
  (e: 'preview', work: Work): void
}>()

const message = useMessage()

const handleClick = () => {
  if (props.work.is_paid) {
    // 已购买，可以查看
    message.success('查看作品详情')
  }
}

const handlePreview = (e: Event) => {
  e.stopPropagation()
  emit('preview', props.work)
  message.info(`正在播放 "${props.work.title}" 的前10秒预览`)
}

const handleUnlock = (e: Event) => {
  e.stopPropagation()
  emit('unlock', props.work)
}
</script>

<style scoped>
.work-card {
  width: 320px;
  flex-shrink: 0;
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}

.work-card:hover {
  border-color: var(--color-neon-pink);
}

.work-image-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 4/5;
  overflow: hidden;
  background: var(--color-dark-700);
}

.work-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: filter 0.3s ease;
}

.video-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: rgba(0, 0, 0, 0.3);
  pointer-events: none;
}

.play-button {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(5, 217, 232, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-dark-900);
  cursor: pointer;
  pointer-events: auto;
  transition: all 0.3s ease;
}

.play-button:hover {
  background: var(--color-neon-blue);
  transform: scale(1.1);
}

.video-preview-label {
  background: rgba(10, 10, 10, 0.8);
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
}

.work-badge {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  z-index: 10;
}

.premium-badge {
  background: var(--color-neon-pink);
  color: white;
}

.blur-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(10, 10, 10, 0.9) 0%, transparent 50%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 24px;
  opacity: 0.9;
}

.blur-message {
  background: rgba(26, 26, 26, 0.9);
  backdrop-filter: blur(8px);
  color: white;
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.unlock-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(10, 10, 10, 0.6);
  backdrop-filter: blur(4px);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.work-card:hover .unlock-overlay {
  opacity: 1;
}

.unlock-button {
  transform: translateY(10px);
  transition: transform 0.3s ease;
}

.work-card:hover .unlock-button {
  transform: translateY(0);
}

.work-info {
  padding: 20px;
}

.work-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 8px 0;
}

.work-meta {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin: 0 0 12px 0;
}

.work-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.work-price {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-neon-pink);
  margin: 0;
}

.sales-count {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

@media (max-width: 768px) {
  .work-card {
    width: 100%;
  }
}
</style>

