import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import {authAPI} from '../services/auth'
import {handleApiError, tokenManager} from '../utils/api'
import type {LoginCredentials, RegisterData, User} from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const token = computed(() => tokenManager.getToken())
  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  const isVip = computed(() => {
    if (!user.value?.is_vip) return false
    if (!user.value.vip_expire_at) return true
    return new Date(user.value.vip_expire_at) > new Date()
  })

  // 操作方法
  const clearError = () => {
    error.value = null
  }

  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const setUser = (userData: User | null) => {
    user.value = userData
  }

  // 登录操作
  const login = async (credentials: LoginCredentials) => {
    try {
      setLoading(true)
      clearError()

      const authResponse = await authAPI.login(credentials)
      
      // 保存token
      tokenManager.setToken(authResponse.access_token)
      if (authResponse.refresh_token) {
        tokenManager.setRefreshToken(authResponse.refresh_token)
      }
      
      // 保存用户信息
      setUser(authResponse.user)

      return authResponse
    } catch (err: any) {
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // 注册操作
  const register = async (userData: RegisterData) => {
    try {
      setLoading(true)
      clearError()

      return await authAPI.register(userData)
    } catch (err: any) {
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // 获取当前用户信息
  const getCurrentUser = async () => {
    try {
      setLoading(true)
      clearError()

      // 后端直接返回 User 对象，不包装
      const user = await authAPI.getCurrentUser()
      setUser(user)

      return user
    } catch (err: any) {
      // Token可能无效，清除本地存储
      await logout()
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // 修改密码
  const changePassword = async (passwordData: {
    current_password: string
    new_password: string
    confirm_password: string
  }) => {
    try {
      setLoading(true)
      clearError()

      return await authAPI.changePassword(passwordData)
    } catch (err: any) {
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // 登出操作
  const logout = async () => {
    try {
      // 尝试调用后端登出接口（如果有的话）
      await authAPI.logout()
    } catch (err) {
      // 即使后端登出失败也要清除本地数据
      console.warn('Backend logout failed:', err)
    } finally {
      // 清除本地数据
      setUser(null)
      tokenManager.clearTokens()
      clearError()
    }
  }

  // 更新用户信息
  const updateUser = (userData: Partial<User>) => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
    }
  }

  // 初始化时获取用户信息（如果有token）
  const initAuth = async () => {
    const token = tokenManager.getToken()
    if (token) {
      try {
        await getCurrentUser()
      } catch (err) {
        // Token无效，清除本地存储
        await logout()
      }
    }
  }

  return {
    // 状态
    user,
    loading,
    error,
    // 计算属性
    token,
    isAuthenticated,
    isAdmin,
    isVip,
    // 方法
    clearError,
    setLoading,
    setError,
    setUser,
    login,
    register,
    getCurrentUser,
    changePassword,
    logout,
    updateUser,
    initAuth,
  }
})
