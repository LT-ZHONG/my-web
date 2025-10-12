import type { Component, CSSProperties } from 'vue'

// 用户相关类型
export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  nickname?: string
  bio?: string
  avatar_url?: string
  phone?: string
  is_active: boolean
  is_admin: boolean
  is_vip: boolean
  vip_expire_at?: string
  credits: number
  created_at: string
  updated_at?: string
}

export interface UserProfile {
  id: number
  username: string
  full_name?: string
  email: string
  avatar_url?: string
  bio?: string
  phone?: string
  is_vip: boolean
  vip_expire_at?: string
  created_at: string
}

export interface UserUpdateData {
  full_name?: string
  bio?: string
  phone?: string
  avatar_url?: string
}

export interface UserSettings {
  notifications: boolean
  emailUpdates: boolean
  privacy: 'public' | 'private'
  theme: 'light' | 'dark'
  language: 'zh-CN' | 'en-US'
}

// 认证相关类型
export interface LoginCredentials {
  username: string // 后端使用username字段
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  confirm_password: string
  full_name?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

// 媒体相关类型
export interface MediaItem {
  id: number
  title: string
  description?: string
  media_type: 'image' | 'video'
  file_url: string
  thumbnail_url?: string
  is_paid: boolean
  price?: number
  tags?: string
  status?: 'active' | 'hidden' | 'deleted'
  view_count: number
  like_count: number
  file_size: number
  duration?: number
  width?: number
  height?: number
  owner_id: number
  created_at: string
  updated_at?: string
  user?: UserProfile
}

export interface MediaUploadData {
  title: string
  description?: string
  is_paid: boolean
  price?: number
}

export interface MediaListParams {
  page?: number
  page_size?: number
  media_type?: 'image' | 'video'
  is_paid?: boolean
  search?: string
  tags?: string
  sort_by?: 'created_at' | 'views' | 'likes' | 'title'
  order?: 'asc' | 'desc'
}

export interface MediaUpdateData {
  title?: string
  description?: string
  tags?: string
  is_paid?: boolean
  price?: number
}

export interface MediaStats {
  total_media: number
  total_images: number
  total_videos: number
  total_views: number
  total_likes: number
  total_size: number
}

// 聊天相关类型
export interface ChatMessage {
  id: number
  content: string
  message_type: 'text' | 'image' | 'emoji' | 'system'
  room_id: number
  sender_id: number
  sender_username?: string
  sender_avatar?: string
  is_deleted: boolean
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface ChatRoom {
  id: number
  name: string
  description?: string
  is_active: boolean
  is_public: boolean
  max_users: number
  created_by: number
  created_at: string
  updated_at: string
}

export interface OnlineUser {
  user_id: number
  username: string
  nickname?: string
  avatar_url?: string
  connected_at?: string
  last_seen_at?: string
}

// 管理员信息
export interface AdminInfo {
  id: number
  username: string
  nickname?: string
  avatar_url?: string
}

// 用户信息（聊天列表）
export interface ChatUserInfo {
  id: number
  username: string
  nickname?: string
  avatar_url?: string
}

// 私聊房间响应
export interface PrivateRoomResponse {
  room_id: number
  room_name: string
  admin_info: AdminInfo
}

// 管理员聊天列表项
export interface AdminChatListItem {
  user_id: number
  username: string
  nickname?: string
  avatar_url?: string
  room_id: number
  last_message?: string
  last_message_time?: string
  unread_count: number
}

// 管理员开始聊天响应
export interface StartChatResponse {
  room_id: number
  user_info: ChatUserInfo
}

// WebSocket消息类型
export interface WSMessage {
  type: 'join_room' | 'leave_room' | 'send_message' | 'typing'
  data: any
}

export interface WSChatMessage {
  content: string
  message_type: 'text' | 'image' | 'emoji'
  room_id: number
}

export interface WSJoinRoom {
  room_id: number
  user: {
    username: string
    nickname?: string
    avatar_url?: string
  }
}

export interface WSTyping {
  room_id: number
  is_typing: boolean
}

// 兼容旧类型（为了不破坏现有代码）
export interface Message extends ChatMessage {
  senderId: number
  senderName?: string
  senderAvatar?: string
  timestamp: number
  isRead: boolean
}

// VIP相关类型
export interface VIPPlan {
  id: string
  name: string
  price: number
  originalPrice?: number
  duration: number // 天数
  features: string[]
  popular?: boolean
  color: string
}

export interface VIPSubscription {
  id: string
  planId: string
  userId: string
  startDate: string
  endDate: string
  status: 'active' | 'expired' | 'cancelled'
  autoRenew: boolean
}

// 支付相关类型
export interface PaymentOrder {
  id: string
  userId: string
  type: 'vip' | 'media' | 'credits'
  itemId: string
  amount: number
  currency: string
  status: 'pending' | 'paid' | 'failed' | 'refunded'
  paymentMethod: 'wechat' | 'alipay' | 'bank' | 'paypal' | 'usdt'
  createdAt: string
  paidAt?: string
}

export interface PaymentRequest {
  type: 'vip' | 'media' | 'credits'
  itemId: string
  amount: number
  paymentMethod: 'wechat' | 'alipay' | 'paypal' | 'usdt'
}

// 积分充值相关
export interface CreditRechargeRequest {
  amount: number  // 美元金额
  payment_method: 'paypal' | 'usdt'
}

export interface CreditRechargeResponse {
  order_id: number
  order_no: string
  amount: number
  credits: number  // 对应的积分数量
  payment_method: 'paypal' | 'usdt'
  payment_info: {
    payment_url?: string  // PayPal支付链接
    address?: string      // USDT地址
    qr_code?: string      // USDT二维码
    amount: number
    note: string
    network?: string      // USDT网络
  }
  message: string
}

export interface CreditTransaction {
  id: number
  user_id: number
  amount: number  // 积分变动(正数为增加,负数为减少)
  balance_before: number
  balance_after: number
  transaction_type: 'recharge' | 'consume' | 'refund' | 'admin'
  description?: string
  order_id?: number
  media_id?: number
  created_at: string
}

export interface CreditBalance {
  user_id: number
  username: string
  credits: number
}

// 媒体访问权限
export interface MediaAccessResponse {
  has_access: boolean
  is_paid: boolean
  price?: number
  required_credits?: number
  user_credits?: number
  has_enough_credits?: boolean
  reason: string
  file_url?: string
  message?: string
  credits_used?: number
  credits_remaining?: number
}

// 文件上传相关类型
export interface UploadProgress {
  percent: number
  status: 'uploading' | 'done' | 'error'
  response?: any
}

export interface FileInfo {
  uid: string
  name: string
  status: 'uploading' | 'done' | 'error'
  url?: string
  response?: any
  percent?: number
}

// 通知相关类型
export interface Notification {
  id: string
  userId: string
  type: 'system' | 'payment' | 'media' | 'chat'
  title: string
  content: string
  isRead: boolean
  createdAt: string
  data?: Record<string, any>
}

// 统计数据类型
export interface UserStats {
  totalViews: number
  totalLikes: number
  totalFavorites: number
  mediaCount: number
  joinDays: number
  vipDays: number
}

export interface AdminStats {
  totalUsers: number
  totalMedia: number
  totalRevenue: number
  activeUsers: number
  newUsersToday: number
  popularMedia: MediaItem[]
}

// 表单验证类型
export interface FormErrors {
  [key: string]: string | undefined
}

export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  pattern?: RegExp
  message: string
}

// WebSocket事件类型
export type SocketEvent = 
  | 'connect'
  | 'disconnect'
  | 'user-online'
  | 'user-offline'
  | 'new-message'
  | 'user-typing'
  | 'user-stop-typing'
  | 'message-read'

export interface SocketData {
  event: SocketEvent
  data: any
  timestamp: number
}

// 路由相关类型
export interface RouteConfig {
  path: string
  component: Component
  requireAuth?: boolean
  requireVIP?: boolean
  title?: string
}

// 主题配置类型
export interface ThemeConfig {
  colors: {
    primary: string
    secondary: string
    background: string
    text: string
    border: string
  }
  fonts: {
    family: string
    sizes: Record<string, string>
  }
  spacing: Record<string, string>
  breakpoints: Record<string, string>
}

// 应用配置类型
export interface AppConfig {
  api: {
    baseUrl: string
    timeout: number
  }
  upload: {
    maxSize: number
    allowedTypes: string[]
  }
  chat: {
    maxMessageLength: number
    historyLimit: number
  }
  media: {
    pageSize: number
    maxTags: number
  }
}

// 错误类型
export interface AppError {
  code: string
  message: string
  details?: any
  timestamp: number
}

// 本地存储键名类型
export type StorageKey = 
  | 'token'
  | 'refreshToken'
  | 'userPreferences'
  | 'theme'
  | 'language'

// 组件Props类型
export interface BaseComponentProps {
  class?: string | object
  style?: CSSProperties
  children?: Component | Component[]
}