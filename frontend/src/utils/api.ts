import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { storage } from './index'

// API配置
const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
}

// 创建axios实例
export const apiClient: AxiosInstance = axios.create(API_CONFIG)

// Token管理
const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export const tokenManager = {
  getToken: (): string | null => storage.get(TOKEN_KEY),
  setToken: (token: string): void => storage.set(TOKEN_KEY, token),
  getRefreshToken: (): string | null => storage.get(REFRESH_TOKEN_KEY),
  setRefreshToken: (token: string): void => storage.set(REFRESH_TOKEN_KEY, token),
  clearTokens: (): void => {
    storage.remove(TOKEN_KEY)
    storage.remove(REFRESH_TOKEN_KEY)
  }
}

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = tokenManager.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Token过期，尝试刷新
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = tokenManager.getRefreshToken()
        if (refreshToken) {
          const response = await axios.post(
            `${API_CONFIG.baseURL}/auth/refresh`,
            { refresh_token: refreshToken }
          )
          
          const { access_token, refresh_token } = response.data
          tokenManager.setToken(access_token)
          
          if (refresh_token) {
            tokenManager.setRefreshToken(refresh_token)
          }
          
          // 重新发送原请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // 刷新失败，清除tokens并跳转到登录页
        tokenManager.clearTokens()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// 通用API请求方法
export const request = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.get<T>(url, config).then(res => res.data),
    
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.post<T>(url, data, config).then(res => res.data),
    
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.put<T>(url, data, config).then(res => res.data),
    
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.delete<T>(url, config).then(res => res.data),
    
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.patch<T>(url, data, config).then(res => res.data),

  // 文件上传
  upload: <T = any>(url: string, formData: FormData, onProgress?: (progress: number) => void): Promise<T> =>
    apiClient.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    }).then(res => res.data),

  // 下载文件
  download: (url: string, filename?: string): Promise<void> =>
    apiClient.get(url, {
      responseType: 'blob'
    }).then(response => {
      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    })
}

// 错误处理
export const handleApiError = (error: any): string => {
  if (error.response) {
    // 服务器响应错误
    const { status, data } = error.response
    
    // 优先使用后端返回的具体错误信息
    const backendMessage = data?.detail || data?.message
    
    switch (status) {
      case 400:
        return backendMessage || '请求参数错误'
      case 401:
        // 对于401错误，优先使用后端返回的具体错误信息
        // 这样可以区分"用户名密码错误"和"登录已过期"等不同情况
        return backendMessage || '认证失败，请重新登录'
      case 403:
        return backendMessage || '没有权限访问此资源'
      case 404:
        return backendMessage || '请求的资源不存在'
      case 409:
        return backendMessage || '资源冲突'
      case 422:
        return backendMessage || '数据验证失败'
      case 429:
        return backendMessage || '请求过于频繁，请稍后再试'
      case 500:
        return backendMessage || '服务器内部错误'
      default:
        return backendMessage || `请求失败 (${status})`
    }
  } else if (error.request) {
    // 网络错误
    return '网络连接失败，请检查网络设置'
  } else {
    // 其他错误
    return error.message || '未知错误'
  }
}

// 别名导出，方便使用
export const api = request

export default apiClient
