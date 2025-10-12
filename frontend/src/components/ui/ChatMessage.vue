<template>
  <div :class="['chat-message', isMe ? 'chat-message-me' : 'chat-message-other']">
    <n-avatar
      v-if="!isMe"
      :src="avatar"
      :size="40"
      class="message-avatar"
    />
    
    <div class="message-content">
      <div :class="['message-bubble', isMe ? 'bubble-me' : 'bubble-other']">
        <p class="message-text">{{ content }}</p>
      </div>
      <p class="message-time">{{ time }}</p>
    </div>
    
    <n-avatar
      v-if="isMe"
      :src="avatar"
      :size="40"
      class="message-avatar"
    />
  </div>
</template>

<script setup lang="ts">
import { NAvatar } from 'naive-ui'

const props = defineProps<{
  isMe: boolean
  avatar: string
  content: string
  time: string
}>()
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: flex-start;
}

.chat-message-me {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-message-me .message-content {
  align-items: flex-end;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  word-wrap: break-word;
  word-break: break-word;
}

.bubble-me {
  background: var(--color-neon-blue);
  color: var(--color-dark-900);
  border-radius: 12px;
  border-top-right-radius: 4px;
}

.bubble-other {
  background: var(--color-dark-700);
  color: var(--color-text-primary);
  border: 1px solid var(--color-dark-600);
  border-radius: 12px;
  border-top-left-radius: 4px;
}

.message-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.message-time {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin: 0;
  padding: 0 4px;
}

@media (max-width: 768px) {
  .message-content {
    max-width: 80%;
  }
}
</style>

