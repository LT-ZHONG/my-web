<template>
  <div class="work-card card-hover" @click="handleClick">
    <div class="work-image-wrapper">
      <n-image
          :src="getFullFileUrl(props.work.thumbnail_url || props.work.file_url)"
          :alt="props.work.title"
          class="work-image"
          object-fit="cover"
          fallback-src="/images/placeholder.jpg"
      />
      <div class="work-badge free-badge">
        免费
      </div>
    </div>
    
    <div class="work-info">
      <h4 class="work-title">{{ work.title }}</h4>
      <p v-if="work.description" class="work-description line-clamp-2">
        {{ work.description }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NImage } from 'naive-ui'
import type { MediaItem } from '@/types'
import { getFullFileUrl } from '@/utils'

const props = defineProps<{
  work: MediaItem
}>()

const emit = defineEmits<{
  (e: 'click', work: MediaItem): void
}>()

const handleClick = () => {
  emit('click', props.work)
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
  border-color: var(--color-neon-blue);
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
}

.free-badge {
  background: var(--color-neon-blue);
  color: var(--color-dark-900);
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

.work-description {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 768px) {
  .work-card {
    width: 100%;
  }
}
</style>
