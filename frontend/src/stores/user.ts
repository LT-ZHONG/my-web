import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userAPI } from '../services/user'
import { handleApiError } from '../utils/api'
import type { User, UserProfile, UserUpdateData, UserSettings, UserStats } from '@/types'

export const useUserStore = defineStore('user', () => {
  // 状态
  const profile = ref<UserProfile | null>(null)
  const users = ref<User[]>([])
  const userSettings = ref<UserSettings>({
    notifications: true,
    emailUpdates: true,
    privacy: 'public',
    theme: 'light',
    language: 'zh-CN',
  })
  const userStats = ref<UserStats>({
    totalViews: 0,
    totalLikes: 0,
    totalFavorites: 0,
    mediaCount: 0,
    joinDays: 0,
    vipDays: 0,
  })
  const loading = ref(false)
  const error = ref<string | null>(null)

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

  // 获取个人资料
  const getProfile = async () => {
    try {
      setLoading(true)
      clearError()

      const response = await userAPI.getProfile()
      if (response.data) {
        profile.value = response.data
      }
      return response
    } catch (err: any) {
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // 更新个人资料
  const updateProfile = async (data: UserUpdateData) => {
    try {
      setLoading(true)
      clearError()

      const response = await userAPI.updateProfile(data)
      if (response.data) {
        profile.value = response.data
      }
      return response
    } catch (err: any) {
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // 获取用户列表（管理员功能）
  const getUserList = async (params?: {
    page?: number
    page_size?: number
    search?: string
    is_active?: boolean
    is_vip?: boolean
  }) => {
    try {
      setLoading(true)
      clearError()

      const response = await userAPI.getUserList(params)
      if (response.data) {
        users.value = response.data.users
      }
      return response
    } catch (err: any) {
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }


  // 更新用户设置（本地存储）
  const updateUserSettings = (settings: Partial<UserSettings>) => {
    userSettings.value = { ...userSettings.value, ...settings }
    // 保存到本地存储
    localStorage.setItem('userSettings', JSON.stringify(userSettings.value))
  }

  // 从本地存储加载用户设置
  const loadUserSettings = () => {
    try {
      const saved = localStorage.getItem('userSettings')
      if (saved) {
        userSettings.value = { ...userSettings.value, ...JSON.parse(saved) }
      }
    } catch (err) {
      console.warn('Failed to load user settings:', err)
    }
  }

  // 初始化
  loadUserSettings()

  return {
    // 状态
    profile,
    users,
    userSettings,
    userStats,
    loading,
    error,
    // 方法
    setLoading,
    setError,
    clearError,
    getProfile,
    updateProfile,
    getUserList,
    updateUserSettings,
    loadUserSettings,
  }
})
