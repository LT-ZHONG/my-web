<template>
  <div class="chat-container">
    <div class="chat-header">
      <n-h2>
        <template v-if="!authStore.user?.is_admin">
          与管理员聊天
        </template>
        <template v-else>
          用户聊天管理
        </template>
      </n-h2>
      
      <div class="connection-status">
        <n-tag v-if="connected" type="success">
          <template #icon>
            <n-icon><checkmark-circle-outline /></n-icon>
          </template>
          已连接
        </n-tag>
        <n-tag v-else type="error">
          <template #icon>
            <n-icon><close-circle-outline /></n-icon>
          </template>
          未连接
        </n-tag>
        
        <n-spin v-if="reconnectAttempts > 0" size="small" style="margin-left: 8px" />
      </div>
    </div>

    <n-alert
      v-if="error"
      :title="error"
      type="error"
      closable
      @close="clearError"
      style="margin-bottom: 16px"
    />
    
    <!-- 普通用户聊天界面 -->
    <div v-if="!authStore.user?.is_admin" class="user-chat">
      <div v-if="adminInfo" class="admin-info">
        <n-avatar round size="large">
          {{ adminInfo.username?.charAt(0).toUpperCase() }}
        </n-avatar>
        <div class="admin-details">
          <h3>{{ adminInfo.nickname || adminInfo.username }}</h3>
          <p>管理员</p>
        </div>
      </div>
      
      <div class="chat-box">
        <div class="chat-messages" ref="messagesContainer">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <n-spin size="large" />
          </div>
          
          <!-- 消息列表 -->
          <div 
            v-for="msg in messages" 
            :key="msg.id"
            :class="['message', { 'own-message': isOwnMessage(msg) }]"
          >
            <div class="message-avatar" v-if="!isOwnMessage(msg)">
              <n-avatar 
                round
                size="small"
              >
                {{ (msg.sender_username || adminInfo?.username)?.charAt(0).toUpperCase() }}
              </n-avatar>
            </div>
            
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
              <div class="message-time">
                {{ formatTime(msg.created_at) }}
              </div>
            </div>
            
            <div class="message-avatar" v-if="isOwnMessage(msg)">
              <n-avatar 
                round
                size="small"
              >
                {{ authStore.user?.username?.charAt(0).toUpperCase() }}
              </n-avatar>
            </div>
          </div>
          
          <!-- 正在输入指示器 -->
          <div v-if="typingUsers.length > 0" class="typing-indicator">
            <n-avatar round size="small">
              {{ adminInfo?.username?.charAt(0).toUpperCase() }}
            </n-avatar>
            <span class="typing-text">正在输入...</span>
          </div>
        </div>
        
        <div class="chat-input">
          <n-input 
            v-model:value="newMessage"
            placeholder="输入消息..."
            :maxlength="1000"
            @keydown.enter="handleSendMessage"
            @input="handleTyping"
            @blur="handleStopTyping"
            :disabled="!connected"
          >
            <template #suffix>
              <n-button 
                type="primary" 
                @click="handleSendMessage"
                :disabled="!connected || !newMessage.trim()"
                :loading="sending"
                text
              >
                <template #icon>
                  <n-icon><send-outline /></n-icon>
                </template>
              </n-button>
            </template>
          </n-input>
        </div>
      </div>
    </div>

    <!-- 管理员聊天界面 -->
    <div v-else class="admin-chat">
      <n-grid :cols="24" :x-gap="16">
        <!-- 用户列表 -->
        <n-grid-item :span="24" :md="8">
          <n-card title="用户列表" size="small" class="user-list-card">
            <div class="user-list">
              <div 
                v-for="chat in adminChatList" 
                :key="chat.user_id"
                :class="['user-item', { 'active': currentChatUser?.user_id === chat.user_id }]"
                @click="switchToUser(chat)"
              >
                <n-avatar 
                  round
                  size="medium"
                >
                  {{ chat.username?.charAt(0).toUpperCase() }}
                </n-avatar>
                <div class="user-details">
                  <div class="user-name">{{ chat.nickname || chat.username }}</div>
                  <div class="last-message">{{ chat.last_message }}</div>
                </div>
                <div class="message-info">
                  <div class="message-time">{{ formatLastMessageTime(chat.last_message_time) }}</div>
                  <n-badge v-if="chat.unread_count > 0" :value="chat.unread_count" />
                </div>
              </div>
              
              <n-empty v-if="adminChatList.length === 0" 
                description="暂无聊天记录" 
              />
            </div>
          </n-card>
        </n-grid-item>
        
        <!-- 聊天区域 -->
        <n-grid-item :span="24" :md="16">
          <div v-if="currentChatUser" class="chat-box">
            <div class="chat-header-user">
              <n-avatar round size="large">
                {{ currentChatUser.username?.charAt(0).toUpperCase() }}
              </n-avatar>
              <div class="user-info">
                <h3>{{ currentChatUser.nickname || currentChatUser.username }}</h3>
                <p>{{ connected ? '在线' : '离线' }}</p>
              </div>
            </div>
            
            <div class="chat-messages" ref="messagesContainer">
              <!-- 加载状态 -->
              <div v-if="loading" class="loading-container">
                <n-spin size="large" />
              </div>
              
              <!-- 消息列表 -->
              <div 
                v-for="msg in messages" 
                :key="msg.id"
                :class="['message', { 'own-message': isOwnMessage(msg) }]"
              >
                <div class="message-avatar" v-if="!isOwnMessage(msg)">
                  <n-avatar 
                    round
                    size="small"
                  >
                    {{ (msg.sender_username || currentChatUser.username)?.charAt(0).toUpperCase() }}
                  </n-avatar>
                </div>
                
                <div class="message-content">
                  <div class="message-text">{{ msg.content }}</div>
                  <div class="message-time">
                    {{ formatTime(msg.created_at) }}
                  </div>
                </div>
                
                <div class="message-avatar" v-if="isOwnMessage(msg)">
                  <n-avatar 
                    round
                    size="small"
                  >
                    {{ authStore.user?.username?.charAt(0).toUpperCase() }}
                  </n-avatar>
                </div>
              </div>
              
              <!-- 正在输入指示器 -->
              <div v-if="typingUsers.length > 0" class="typing-indicator">
                <n-avatar round size="small">
                  {{ currentChatUser.username?.charAt(0).toUpperCase() }}
                </n-avatar>
                <span class="typing-text">正在输入...</span>
              </div>
            </div>
            
            <div class="chat-input">
              <n-input 
                v-model:value="newMessage"
                placeholder="输入消息..."
                :maxlength="1000"
                @keydown.enter="handleSendMessage"
                @input="handleTyping"
                @blur="handleStopTyping"
                :disabled="!connected"
              >
                <template #suffix>
                  <n-button 
                    type="primary" 
                    @click="handleSendMessage"
                    :disabled="!connected || !newMessage.trim()"
                    :loading="sending"
                    text
                  >
                    <template #icon>
                      <n-icon><send-outline /></n-icon>
                    </template>
                  </n-button>
                </template>
              </n-input>
            </div>
          </div>
          
          <div v-else class="no-chat-selected">
            <n-empty description="请选择要聊天的用户" />
          </div>
        </n-grid-item>
      </n-grid>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { 
  NInput,
  NButton, 
  NGrid,
  NGridItem,
  NCard,
  NAvatar,
  NBadge,
  NTag,
  NAlert,
  NEmpty,
  NSpin,
  NH2,
  NIcon,
  useMessage
} from 'naive-ui'
import { 
  SendOutline, 
  CheckmarkCircleOutline,
  CloseCircleOutline,
} from '@vicons/ionicons5'
import dayjs from 'dayjs'
import { useChatStore } from '@/stores'
import { useAuthStore } from '@/stores'
import type { ChatMessage, AdminInfo, AdminChatListItem, PrivateRoomResponse } from '@/types'

// Store
const chatStore = useChatStore()
const authStore = useAuthStore()
const message = useMessage()

// 响应式状态
const newMessage = ref('')
const sending = ref(false)
const messagesContainer = ref<HTMLElement>()
const typingTimer = ref<NodeJS.Timeout>()
const adminInfo = ref<AdminInfo | null>(null)
const adminChatList = ref<AdminChatListItem[]>([])
const currentChatUser = ref<AdminChatListItem | null>(null)

// 使用 storeToRefs 保持响应式
const {
  messages,
  onlineUsers,
  connected,
  loading,
  error,
  reconnectAttempts,
  typing
} = storeToRefs(chatStore)

// Store 方法（不需要使用 storeToRefs）
const {
  clearError
} = chatStore

// 获取正在输入的用户信息
const typingUsers = computed(() => {
  return onlineUsers.value.filter(user => typing.value.includes(user.user_id))
})

// 判断是否为自己的消息
const isOwnMessage = (msg: ChatMessage) => {
  return msg.sender_id === authStore.user?.id
}

// 发送消息
const handleSendMessage = async () => {
  if (!newMessage.value.trim() || sending.value) return
  
  try {
    sending.value = true
    chatStore.sendMessage(newMessage.value.trim())
    newMessage.value = ''
    
    // 滚动到底部
    await nextTick(() => {
      scrollToBottom()
    })
  } catch (error) {
    message.error('发送消息失败')
  } finally {
    sending.value = false
  }
}

// 处理输入事件（输入指示器）
const handleTyping = () => {
  if (!connected) return
  
  // 发送正在输入状态
  chatStore.startTyping()
  
  // 清除之前的计时器
  if (typingTimer.value) {
    clearTimeout(typingTimer.value)
  }
  
  // 3秒后自动停止输入状态
  typingTimer.value = setTimeout(() => {
    chatStore.stopTyping()
  }, 3000)
}

// 停止输入
const handleStopTyping = () => {
  if (typingTimer.value) {
    clearTimeout(typingTimer.value)
  }
  chatStore.stopTyping()
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 格式化时间
const formatTime = (dateString: string) => {
  return dayjs(dateString).format('HH:mm')
}

// 格式化最后消息时间
const formatLastMessageTime = (dateString: string) => {
  const date = dayjs(dateString)
  const now = dayjs()
  
  if (date.isSame(now, 'day')) {
    return date.format('HH:mm')
  } else if (date.isSame(now.subtract(1, 'day'), 'day')) {
    return '昨天'
  } else {
    return date.format('MM-DD')
  }
}

// 切换到指定用户聊天
const switchToUser = async (chatUser: AdminChatListItem) => {
  try {
    currentChatUser.value = chatUser
    
    // 获取历史消息
    await chatStore.fetchMessages(chatUser.room_id)
    
    // 连接WebSocket
    const userData = {
      username: authStore.user?.username,
      nickname: authStore.user?.nickname || authStore.user?.full_name
    }
    
    chatStore.connect(authStore.token || '', chatUser.room_id, userData)
    
    // 滚动到底部
    await nextTick(() => {
      scrollToBottom()
    })
  } catch (error) {
    console.error('切换用户聊天失败:', error)
    message.error('连接聊天失败')
  }
}

// 初始化普通用户聊天
const initializeUserChat = async () => {
  try {
    // 获取私聊房间
    const roomData: PrivateRoomResponse = await chatStore.fetchPrivateRoom()

    if (!roomData) {
      console.error('[Chat Page] roomData 为空!')
      message.error('获取聊天房间失败：数据为空')
      return
    }
    
    if (!roomData.admin_info) {
      console.error('[Chat Page] roomData.admin_info 为空!', '完整数据:', roomData)
      message.error('获取管理员信息失败')
      return
    }
    
    adminInfo.value = roomData.admin_info
    
    // 获取历史消息
    await chatStore.fetchMessages(roomData.room_id)
    
    // 连接WebSocket
    const userData = {
      username: authStore.user?.username,
      nickname: authStore.user?.nickname || authStore.user?.full_name
    }
    console.log('[Chat Page] 开始连接 WebSocket, userData:', userData)
    
    chatStore.connect(authStore.token || '', roomData.room_id, userData)
    
    // 滚动到底部
    await nextTick(() => {
      scrollToBottom()
    })
  } catch (error) {
    console.error('[Chat Page] 初始化用户聊天失败:', error)
    console.error('[Chat Page] 错误堆栈:', error instanceof Error ? error.stack : '无堆栈信息')
    message.error('连接聊天服务失败')
  }
}

// 初始化管理员聊天
const initializeAdminChat = async () => {
  try {
    // 获取聊天列表
    adminChatList.value = await chatStore.fetchAdminChatList()
    
    // 如果有聊天记录，默认选择第一个
    if (adminChatList.value.length > 0) {
      await switchToUser(adminChatList.value[0])
    }
  } catch (error) {
    console.error('初始化管理员聊天失败:', error)
    message.error('获取聊天列表失败')
  }
}

// 初始化聊天
const initializeChat = async () => {
  if (!authStore.isAuthenticated) {
    message.error('请先登录')
    return
  }

  try {
    if (authStore.user?.is_admin) {
      await initializeAdminChat()
    } else {
      await initializeUserChat()
    }
  } catch (error) {
    console.error('初始化聊天失败:', error)
    message.error('初始化聊天失败')
  }
}

// 监听消息变化，自动滚动到底部
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

// 生命周期
onMounted(() => {
  initializeChat()
})

onUnmounted(() => {
  // 清理资源
  if (typingTimer.value) {
    clearTimeout(typingTimer.value)
  }
  chatStore.disconnect()
})
</script>

<style scoped>
.chat-container {
  min-height: 100vh;
  background: var(--color-dark-900);
  padding: 80px 24px 48px;
  max-width: 1400px;
  margin: 0 auto;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.chat-header :deep(h2) {
  font-family: 'Playfair Display', serif;
  color: var(--color-neon-blue);
  text-shadow: 0 0 20px rgba(5, 217, 232, 0.5);
  margin: 0;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 普通用户聊天样式 */
.user-chat {
  max-width: 900px;
  margin: 0 auto;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 16px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.admin-info:hover {
  border-color: var(--color-neon-blue);
  box-shadow: 0 8px 24px rgba(5, 217, 232, 0.2);
}

.admin-details h3 {
  margin: 0 0 4px;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.admin-details p {
  margin: 0;
  color: var(--color-neon-blue);
  font-size: 0.875rem;
}

/* 管理员聊天样式 */
.admin-chat {
  min-height: 700px;
}

.user-list-card {
  height: 100%;
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 16px;
}

.user-list-card :deep(.n-card) {
  background: var(--color-dark-800);
  border-color: var(--color-dark-600);
}

.user-list-card :deep(.n-card__content) {
  padding: 0;
  height: calc(100% - 57px);
  overflow: hidden;
}

.user-list {
  height: 100%;
  overflow-y: auto;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid var(--color-dark-600);
}

.user-item:hover {
  background: var(--color-dark-700);
  border-left: 3px solid var(--color-neon-blue);
}

.user-item.active {
  background: rgba(5, 217, 232, 0.1);
  border-left: 3px solid var(--color-neon-blue);
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 600;
  font-size: 0.9375rem;
  margin-bottom: 4px;
  color: var(--color-text-primary);
}

.last-message {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.message-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.message-time {
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
}

.chat-header-user {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-dark-600);
  background: var(--color-dark-800);
  border-radius: 16px 16px 0 0;
}

.user-info h3 {
  margin: 0 0 4px;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.user-info p {
  margin: 0;
  color: var(--color-neon-blue);
  font-size: 0.875rem;
}

.no-chat-selected {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 600px;
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 16px;
}

.chat-box {
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 16px;
  height: 600px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.chat-messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  scroll-behavior: smooth;
  background: var(--color-dark-900);
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
}

.message {
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.own-message {
  justify-content: flex-end;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  background: var(--color-dark-700);
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
  border: 1px solid var(--color-dark-600);
  color: var(--color-text-primary);
}

.own-message .message-content {
  background: linear-gradient(135deg, var(--color-neon-blue), var(--color-neon-purple));
  border-color: transparent;
  color: var(--color-dark-900);
  box-shadow: 0 4px 16px rgba(5, 217, 232, 0.3);
}

.message-sender {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
  font-weight: 500;
}

.own-message .message-sender {
  display: none;
}

.message-text {
  word-wrap: break-word;
  line-height: 1.6;
  margin-bottom: 4px;
}

.message-time {
  font-size: 0.6875rem;
  opacity: 0.7;
  text-align: right;
}

.own-message .message-time {
  color: rgba(0, 0, 0, 0.6);
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--color-dark-700);
  border: 1px solid var(--color-dark-600);
  border-radius: 16px;
  margin-bottom: 12px;
  animation: pulse 1.5s infinite;
}

.typing-text {
  font-size: 0.8125rem;
  color: var(--color-neon-blue);
  font-style: italic;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.chat-input {
  padding: 20px 24px;
  border-top: 1px solid var(--color-dark-600);
  background: var(--color-dark-800);
  border-radius: 0 0 16px 16px;
}

.chat-input :deep(.n-input) {
  background: var(--color-dark-700);
  border-color: var(--color-dark-600);
}

.chat-input :deep(.n-input__input-el) {
  color: var(--color-text-primary);
}

.chat-input :deep(.n-input:hover) {
  border-color: var(--color-neon-blue);
}

.chat-input :deep(.n-input.n-input--focus) {
  border-color: var(--color-neon-blue);
  box-shadow: 0 0 0 2px rgba(5, 217, 232, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    padding: 64px 16px 32px;
  }
  
  .chat-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 24px;
  }
  
  .user-chat .chat-box {
    height: 500px;
  }
  
  .admin-chat {
    min-height: auto;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .user-item {
    padding: 12px 16px;
  }
  
  .admin-info {
    padding: 16px 20px;
  }
}

/* 自定义滚动条 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: var(--color-dark-800);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: var(--color-dark-600);
  border-radius: 3px;
  transition: background 0.3s ease;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--color-neon-blue);
}

.user-list::-webkit-scrollbar {
  width: 6px;
}

.user-list::-webkit-scrollbar-track {
  background: var(--color-dark-800);
}

.user-list::-webkit-scrollbar-thumb {
  background: var(--color-dark-600);
  border-radius: 3px;
}

.user-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-neon-blue);
}
</style>
