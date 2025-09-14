import { request } from '../utils/api'
import type { 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  User,
  ApiResponse 
} from '@/types'

export const authAPI = {
  /**
   * 用户注册
   */
  register: (data: RegisterData): Promise<ApiResponse<AuthResponse>> => {
    return request.post('/auth/register', data)
  },

  /**
   * 用户登录
   */
  login: (credentials: LoginCredentials): Promise<ApiResponse<AuthResponse>> => {
    return request.post('/auth/login', credentials)
  },

  /**
   * 刷新Token
   */
  refreshToken: (refresh_token: string): Promise<ApiResponse<{ access_token: string; refresh_token?: string }>> => {
    return request.post('/auth/refresh', { refresh_token })
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser: (): Promise<ApiResponse<User>> => {
    return request.get('/auth/me')
  },

  /**
   * 修改密码
   */
  changePassword: (data: {
    current_password: string
    new_password: string
    confirm_password: string
  }): Promise<ApiResponse<void>> => {
    return request.post('/auth/change-password', data)
  },

  /**
   * 注销登录（如果后端有此接口）
   */
  logout: (): Promise<ApiResponse<void>> => {
    return request.post('/auth/logout')
  }
}

export default authAPI
