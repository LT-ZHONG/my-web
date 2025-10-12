<template>
  <div class="message-item">
    <div class="message-header">
      <div class="user-info">
        <n-avatar :src="message.avatar" :size="48" />
        <div class="user-details">
          <h4 class="user-name">{{ message.name }}</h4>
          <p class="message-date">{{ message.date }}</p>
        </div>
      </div>
      <n-tag 
        :type="message.replied ? 'success' : 'default'"
        size="small"
      >
        {{ message.replied ? '已回复' : '待回复' }}
      </n-tag>
    </div>
    
    <p class="message-content">{{ message.content }}</p>
    
    <div v-if="message.replied && message.reply" class="message-reply">
      <p class="reply-label">
        <span class="reply-author">管理员回复：</span>
        <span class="reply-text">{{ message.reply }}</span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NAvatar, NTag } from 'naive-ui'

export interface Message {
  id: number
  name: string
  avatar: string
  date: string
  content: string
  replied: boolean
  reply?: string
}

const props = defineProps<{
  message: Message
}>()
</script>

<style scoped>
.message-item {
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.message-item:hover {
  border-color: var(--color-neon-pink);
  box-shadow: 0 4px 16px rgba(255, 42, 109, 0.2);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.user-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.message-date {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.message-content {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.message-reply {
  background: var(--color-dark-700);
  border-left: 4px solid var(--color-neon-blue);
  border-radius: 4px;
  padding: 12px 16px;
  margin-top: 12px;
}

.reply-label {
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.reply-author {
  color: var(--color-neon-blue);
  font-weight: 600;
  margin-right: 8px;
}

.reply-text {
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .message-item {
    padding: 16px;
  }
  
  .message-header {
    flex-direction: column;
    gap: 12px;
  }
}
</style>

