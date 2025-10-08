<template>
  <div class="chat-container">
    <div class="chat-header">
      <a-typography-title :level="2">
        <template v-if="!authStore.user?.is_admin">
          与管理员聊天
        </template>
        <template v-else>
          用户聊天管理
        </template>
      </a-typography-title>
      
      <div class="connection-status">
        <a-tag v-if="connected" color="success">
          <template #icon><CheckCircleOutlined /></template>
          已连接
        </a-tag>
        <a-tag v-else color="error">
          <template #icon><CloseCircleOutlined /></template>
          未连接
        </a-tag>
        
        <a-tooltip v-if="reconnectAttempts > 0" title="正在重连...">
          <a-spin size="small" style="margin-left: 8px" />
        </a-tooltip>
      </div>
    </div>

    <a-alert
      v-if="error"
      :message="error"
      type="error"
      show-icon
      closable
      @close="clearError"
      style="margin-bottom: 16px"
    />
    
    <!-- 普通用户聊天界面 -->
    <div v-if="!authStore.user?.is_admin" class="user-chat">
      <div v-if="adminInfo" class="admin-info">
        <a-avatar size="large">
          {{ adminInfo.username?.charAt(0).toUpperCase() }}
        </a-avatar>
        <div class="admin-details">
          <h3>{{ adminInfo.nickname || adminInfo.username }}</h3>
          <p>管理员</p>
        </div>
      </div>
      
      <div class="chat-box">
        <div class="chat-messages" ref="messagesContainer">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <a-spin size="large" />
          </div>
          
          <!-- 消息列表 -->
          <div 
            v-for="msg in messages" 
            :key="msg.id"
            :class="['message', { 'own-message': isOwnMessage(msg) }]"
          >
            <div class="message-avatar" v-if="!isOwnMessage(msg)">
              <a-avatar 
                :alt="msg.sender_username"
                size="small"
              >
                {{ (msg.sender_username || adminInfo?.username)?.charAt(0).toUpperCase() }}
              </a-avatar>
            </div>
            
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
              <div class="message-time">
                {{ formatTime(msg.created_at) }}
              </div>
            </div>
            
            <div class="message-avatar" v-if="isOwnMessage(msg)">
              <a-avatar 
                :alt="authStore.user?.username"
                size="small"
              >
                {{ authStore.user?.username?.charAt(0).toUpperCase() }}
              </a-avatar>
            </div>
          </div>
          
          <!-- 正在输入指示器 -->
          <div v-if="typingUsers.length > 0" class="typing-indicator">
            <a-avatar size="small">
              {{ adminInfo?.username?.charAt(0).toUpperCase() }}
            </a-avatar>
            <span class="typing-text">正在输入...</span>
          </div>
        </div>
        
        <div class="chat-input">
          <a-input 
            v-model:value="newMessage"
            placeholder="输入消息..."
            :maxlength="1000"
            @press-enter="handleSendMessage"
            @input="handleTyping"
            @blur="handleStopTyping"
            :disabled="!connected"
          >
            <template #suffix>
              <a-button 
                type="primary" 
                :icon="h(SendOutlined)"
                @click="handleSendMessage"
                :disabled="!connected || !newMessage.trim()"
                :loading="sending"
              />
            </template>
          </a-input>
        </div>
      </div>
    </div>

    <!-- 管理员聊天界面 -->
    <div v-else class="admin-chat">
      <a-row :gutter="16">
        <!-- 用户列表 -->
        <a-col :xs="24" :md="8">
          <a-card title="用户列表" size="small" class="user-list-card">
            <div class="user-list">
              <div 
                v-for="chat in adminChatList" 
                :key="chat.user_id"
                :class="['user-item', { 'active': currentChatUser?.user_id === chat.user_id }]"
                @click="switchToUser(chat)"
              >
                <a-avatar 
                  :alt="chat.username"
                  size="default"
                >
                  {{ chat.username?.charAt(0).toUpperCase() }}
                </a-avatar>
                <div class="user-details">
                  <div class="user-name">{{ chat.nickname || chat.username }}</div>
                  <div class="last-message">{{ chat.last_message }}</div>
                </div>
                <div class="message-info">
                  <div class="message-time">{{ formatLastMessageTime(chat.last_message_time) }}</div>
                  <a-badge v-if="chat.unread_count > 0" :count="chat.unread_count" />
                </div>
              </div>
              
              <a-empty v-if="adminChatList.length === 0" 
                image="simple" 
                description="暂无聊天记录" 
              />
            </div>
          </a-card>
        </a-col>
        
        <!-- 聊天区域 -->
        <a-col :xs="24" :md="16">
          <div v-if="currentChatUser" class="chat-box">
            <div class="chat-header-user">
              <a-avatar size="large">
                {{ currentChatUser.username?.charAt(0).toUpperCase() }}
              </a-avatar>
              <div class="user-info">
                <h3>{{ currentChatUser.nickname || currentChatUser.username }}</h3>
                <p>{{ connected ? '在线' : '离线' }}</p>
              </div>
            </div>
            
            <div class="chat-messages" ref="messagesContainer">
              <!-- 加载状态 -->
              <div v-if="loading" class="loading-container">
                <a-spin size="large" />
              </div>
              
              <!-- 消息列表 -->
              <div 
                v-for="msg in messages" 
                :key="msg.id"
                :class="['message', { 'own-message': isOwnMessage(msg) }]"
              >
                <div class="message-avatar" v-if="!isOwnMessage(msg)">
                  <a-avatar 
                    :alt="msg.sender_username"
                    size="small"
                  >
                    {{ (msg.sender_username || currentChatUser.username)?.charAt(0).toUpperCase() }}
                  </a-avatar>
                </div>
                
                <div class="message-content">
                  <div class="message-text">{{ msg.content }}</div>
                  <div class="message-time">
                    {{ formatTime(msg.created_at) }}
                  </div>
                </div>
                
                <div class="message-avatar" v-if="isOwnMessage(msg)">
                  <a-avatar 
                    :alt="authStore.user?.username"
                    size="small"
                  >
                    {{ authStore.user?.username?.charAt(0).toUpperCase() }}
                  </a-avatar>
                </div>
              </div>
              
              <!-- 正在输入指示器 -->
              <div v-if="typingUsers.length > 0" class="typing-indicator">
                <a-avatar size="small">
                  {{ currentChatUser.username?.charAt(0).toUpperCase() }}
                </a-avatar>
                <span class="typing-text">正在输入...</span>
              </div>
            </div>
            
            <div class="chat-input">
              <a-input 
                v-model:value="newMessage"
                placeholder="输入消息..."
                :maxlength="1000"
                @press-enter="handleSendMessage"
                @input="handleTyping"
                @blur="handleStopTyping"
                :disabled="!connected"
              >
                <template #suffix>
                  <a-button 
                    type="primary" 
                    :icon="h(SendOutlined)"
                    @click="handleSendMessage"
                    :disabled="!connected || !newMessage.trim()"
                    :loading="sending"
                  />
                </template>
              </a-input>
            </div>
          </div>
          
          <div v-else class="no-chat-selected">
            <a-empty description="请选择要聊天的用户" />
          </div>
        </a-col>
      </a-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { 
  Input as AInput,
  Button as AButton, 
  Row as ARow,
  Col as ACol,
  Card as ACard,
  Avatar as AAvatar,
  Badge as ABadge,
  Tag as ATag,
  Alert as AAlert,
  Empty as AEmpty,
  Spin as ASpin,
  Tooltip as ATooltip,
  message
} from 'ant-design-vue'
import { 
  SendOutlined, 
  CheckCircleOutlined,
  CloseCircleOutlined 
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import { useChatStore } from '@/stores'
import { useAuthStore } from '@/stores'
import type { ChatMessage, AdminInfo, AdminChatListItem, PrivateRoomResponse } from '@/types'

// Store
const chatStore = useChatStore()
const authStore = useAuthStore()

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
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 普通用户聊天样式 */
.user-chat {
  max-width: 800px;
  margin: 0 auto;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

.admin-details h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.admin-details p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* 管理员聊天样式 */
.admin-chat {
  height: 700px;
}

.user-list-card {
  height: 100%;
}

.user-list-card :deep(.ant-card-body) {
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
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f0f0f0;
}

.user-item:hover {
  background-color: #f5f5f5;
}

.user-item.active {
  background-color: #e6f7ff;
  border-color: #91d5ff;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 500;
  font-size: 14px;
  margin-bottom: 4px;
}

.last-message {
  font-size: 12px;
  color: #999;
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
  font-size: 11px;
  color: #999;
}

.chat-header-user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
  background: #fafafa;
}

.user-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.user-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.no-chat-selected {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-box {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 600px;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
}

.message {
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.message.own-message {
  justify-content: flex-end;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  background: #f5f5f5;
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
}

.own-message .message-content {
  background: linear-gradient(135deg, #ff6b35, #ff8e53);
  color: white;
}

.message-sender {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
  font-weight: 500;
}

.own-message .message-sender {
  display: none;
}

.message-text {
  word-wrap: break-word;
  line-height: 1.4;
  margin-bottom: 4px;
}

.message-time {
  font-size: 11px;
  opacity: 0.6;
  text-align: right;
}

.own-message .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f0f0f0;
  border-radius: 12px;
  margin-bottom: 12px;
  animation: pulse 1.5s infinite;
}

.typing-text {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #e8e8e8;
  background: #fafafa;
  border-radius: 0 0 12px 12px;
}

.online-users-card {
  height: 600px;
  overflow: hidden;
}

.online-users-card :deep(.ant-card-body) {
  padding: 12px;
  height: calc(100% - 57px);
  overflow-y: auto;
}

.online-users-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.online-user-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.online-user-item:hover {
  background-color: #f5f5f5;
}

.user-name {
  flex: 1;
  font-size: 14px;
  color: #333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    padding: 12px;
  }
  
  .chat-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .user-chat .chat-box {
    height: 500px;
  }
  
  .admin-chat {
    height: auto;
  }
  
  .admin-chat .ant-row {
    flex-direction: column;
  }
  
  .admin-chat .ant-col {
    width: 100% !important;
    margin-bottom: 16px;
  }
  
  .user-list-card {
    height: 300px;
  }
  
  .admin-chat .chat-box {
    height: 400px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .user-item {
    padding: 8px 12px;
  }
  
  .admin-info {
    padding: 12px 16px;
  }
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.online-users-list::-webkit-scrollbar {
  width: 4px;
}

.online-users-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.online-users-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}
</style>
