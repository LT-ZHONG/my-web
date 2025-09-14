import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage, OnlineUser, ChatRoom, WSMessage, WSChatMessage, WSJoinRoom } from '../types'
import { api } from '../utils/api'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const messages = ref<ChatMessage[]>([])
  const onlineUsers = ref<OnlineUser[]>([])
  const chatRooms = ref<ChatRoom[]>([])
  const currentRoom = ref<number>(1) // 默认房间ID
  const websocket = ref<WebSocket | null>(null)
  const connected = ref(false)
  const typing = ref<number[]>([]) // 正在输入的用户ID
  const loading = ref(false)
  const error = ref<string | null>(null)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5

  // 操作方法
  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const clearError = () => {
    error.value = null
  }

  // 获取WebSocket URL
  const getWebSocketUrl = (token: string, roomId: number) => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_API_BASE_URL?.replace(/^https?:\/\//, '') || 'localhost:8000'
    return `${wsProtocol}//${host}/api/v1/chat/ws?token=${encodeURIComponent(token)}&room_id=${roomId}`
  }

  // 连接WebSocket
  const connect = (token: string, roomId: number = 1, userData?: any) => {
    if (websocket.value && connected.value) {
      return
    }

    try {
      const wsUrl = getWebSocketUrl(token, roomId)
      websocket.value = new WebSocket(wsUrl)

      websocket.value.onopen = () => {
        connected.value = true
        reconnectAttempts.value = 0
        clearError()
        console.log('WebSocket连接成功')

        // 加入房间
        const joinMessage: WSMessage = {
          type: 'join_room',
          data: {
            room_id: roomId,
            user: userData || {}
          }
        }
        sendWebSocketMessage(joinMessage)
      }

      websocket.value.onclose = () => {
        connected.value = false
        console.log('WebSocket连接关闭')
        
        // 自动重连
        if (reconnectAttempts.value < maxReconnectAttempts) {
          setTimeout(() => {
            reconnectAttempts.value++
            console.log(`尝试重连 ${reconnectAttempts.value}/${maxReconnectAttempts}`)
            connect(token, roomId, userData)
          }, 3000 * reconnectAttempts.value)
        } else {
          setError('连接已断开，请刷新页面重试')
        }
      }

      websocket.value.onerror = (event) => {
        console.error('WebSocket错误:', event)
        setError('连接失败')
      }

      websocket.value.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          handleWebSocketMessage(message)
        } catch (error) {
          console.error('解析消息失败:', error)
        }
      }

      currentRoom.value = roomId
    } catch (error) {
      console.error('创建WebSocket连接失败:', error)
      setError('连接失败')
    }
  }

  // 处理WebSocket消息
  const handleWebSocketMessage = (message: any) => {
    switch (message.type) {
      case 'new_message':
        const newMessage: ChatMessage = message.data
        messages.value.push(newMessage)
        break

      case 'user_online':
        const onlineUser: OnlineUser = message.data
        const existingUser = onlineUsers.value.find(u => u.user_id === onlineUser.user_id)
        if (existingUser) {
          Object.assign(existingUser, onlineUser)
        } else {
          onlineUsers.value.push(onlineUser)
        }
        break

      case 'user_offline':
        const userId = message.data.user_id
        const index = onlineUsers.value.findIndex(u => u.user_id === userId)
        if (index > -1) {
          onlineUsers.value.splice(index, 1)
        }
        break

      case 'user_typing':
        const typingUserId = message.data.user_id
        if (!typing.value.includes(typingUserId)) {
          typing.value.push(typingUserId)
        }
        break

      case 'user_stop_typing':
        const stopTypingUserId = message.data.user_id
        const typingIndex = typing.value.indexOf(stopTypingUserId)
        if (typingIndex > -1) {
          typing.value.splice(typingIndex, 1)
        }
        break

      case 'online_users':
        onlineUsers.value = message.data.users || []
        break

      case 'error':
        setError(message.data.message || '服务器错误')
        break

      default:
        console.log('未处理的消息类型:', message.type)
    }
  }

  // 发送WebSocket消息
  const sendWebSocketMessage = (message: WSMessage) => {
    if (websocket.value && connected.value) {
      websocket.value.send(JSON.stringify(message))
    } else {
      setError('连接已断开')
    }
  }

  // 断开连接
  const disconnect = () => {
    if (websocket.value) {
      websocket.value.close()
      websocket.value = null
      connected.value = false
    }
    onlineUsers.value = []
    typing.value = []
  }

  // 发送消息
  const sendMessage = (content: string, messageType: 'text' | 'image' | 'emoji' = 'text') => {
    if (!websocket.value || !connected.value) {
      setError('连接已断开')
      return
    }

    const message: WSMessage = {
      type: 'send_message',
      data: {
        content,
        message_type: messageType,
        room_id: currentRoom.value
      }
    }

    sendWebSocketMessage(message)
  }

  // 加入房间
  const joinRoom = (roomId: number, userData?: any) => {
    if (!websocket.value || !connected.value) {
      setError('连接已断开')
      return
    }

    const message: WSMessage = {
      type: 'join_room',
      data: {
        room_id: roomId,
        user: userData || {}
      }
    }

    sendWebSocketMessage(message)
    currentRoom.value = roomId
  }

  // 离开房间
  const leaveRoom = (roomId: number) => {
    if (!websocket.value || !connected.value) {
      return
    }

    const message: WSMessage = {
      type: 'leave_room',
      data: {
        room_id: roomId
      }
    }

    sendWebSocketMessage(message)
  }

  // 开始输入
  const startTyping = () => {
    if (!websocket.value || !connected.value) {
      return
    }

    const message: WSMessage = {
      type: 'typing',
      data: {
        room_id: currentRoom.value,
        is_typing: true
      }
    }

    sendWebSocketMessage(message)
  }

  // 停止输入
  const stopTyping = () => {
    if (!websocket.value || !connected.value) {
      return
    }

    const message: WSMessage = {
      type: 'typing',
      data: {
        room_id: currentRoom.value,
        is_typing: false
      }
    }

    sendWebSocketMessage(message)
  }

  // 获取历史消息
  const fetchMessages = async (roomId: number = 1, page = 1, pageSize = 50, beforeId?: number) => {
    try {
      setLoading(true)
      clearError()

      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString()
      })
      
      if (beforeId) {
        params.append('before_id', beforeId.toString())
      }

      const response = await api.get(`/chat/rooms/${roomId}/messages?${params}`)
      
      if (page === 1) {
        messages.value = response.data
      } else {
        messages.value.unshift(...response.data)
      }

      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '获取消息失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 获取私聊房间（普通用户）
  const fetchPrivateRoom = async () => {
    try {
      setLoading(true)
      clearError()

      const response = await api.get('/chat/private-room')
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '获取私聊房间失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 获取管理员聊天列表
  const fetchAdminChatList = async () => {
    try {
      setLoading(true)
      clearError()

      const response = await api.get('/chat/admin/chat-list')
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '获取聊天列表失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 管理员开始与用户聊天
  const startChatWithUser = async (userId: number) => {
    try {
      setLoading(true)
      clearError()

      const response = await api.post(`/chat/admin/start-chat/${userId}`)
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '开始聊天失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 获取在线用户
  const fetchOnlineUsers = async (roomId: number) => {
    try {
      const response = await api.get(`/chat/rooms/${roomId}/online-users`)
      onlineUsers.value = response.data
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '获取在线用户失败')
      throw err
    }
  }

  // 清空消息
  const clearMessages = () => {
    messages.value = []
  }

  // 清空所有状态
  const reset = () => {
    disconnect()
    clearMessages()
    chatRooms.value = []
    onlineUsers.value = []
    typing.value = []
    currentRoom.value = 1
    clearError()
  }

  return {
    // 状态
    messages,
    onlineUsers,
    chatRooms,
    currentRoom,
    websocket,
    connected,
    typing,
    loading,
    error,
    reconnectAttempts,
    // 方法
    setLoading,
    setError,
    clearError,
    connect,
    disconnect,
    sendMessage,
    joinRoom,
    leaveRoom,
    startTyping,
    stopTyping,
    fetchMessages,
    fetchPrivateRoom,
    fetchAdminChatList,
    startChatWithUser,
    fetchOnlineUsers,
    clearMessages,
    reset,
    sendWebSocketMessage,
    handleWebSocketMessage,
  }
})
