import { request } from '../utils/api'
import type { 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  User
} from '@/types'

export const authAPI = {
  /**
   * 用户注册
   * @returns 直接返回 AuthResponse（包含 token 和用户信息）
   */
  register: (data: RegisterData): Promise<AuthResponse> => {
    return request.post('/auth/register', data)
  },

  /**
   * 用户登录
   * @returns 直接返回 AuthResponse（包含 token 和用户信息）
   */
  login: (credentials: LoginCredentials): Promise<AuthResponse> => {
    return request.post('/auth/login', credentials)
  },

  /**
   * 刷新Token
   * @returns 直接返回新的 AuthResponse
   */
  refreshToken: (refresh_token: string): Promise<AuthResponse> => {
    return request.post('/auth/refresh', { refresh_token })
  },

  /**
   * 获取当前用户信息
   * @returns 直接返回 User 对象
   */
  getCurrentUser: (): Promise<User> => {
    return request.get('/auth/me')
  },

  /**
   * 修改密码
   * @returns 直接返回消息对象
   */
  changePassword: (data: {
    current_password: string
    new_password: string
    confirm_password: string
  }): Promise<{ message: string }> => {
    return request.post('/auth/change-password', data)
  },

  /**
   * 注销登录
   * @returns 直接返回消息对象
   */
  logout: (): Promise<{ message: string }> => {
    return request.post('/auth/logout')
  }
}

export default authAPI
