import { request } from '../utils/api'
import type { 
  UserProfile, 
  UserUpdateData, 
  User,
  ApiResponse 
} from '@/types'

export const userAPI = {
  /**
   * 获取个人信息
   */
  getProfile: (): Promise<ApiResponse<UserProfile>> => {
    return request.get('/users/me')
  },

  /**
   * 更新个人信息
   */
  updateProfile: (data: UserUpdateData): Promise<ApiResponse<UserProfile>> => {
    return request.put('/users/me', data)
  },

  /**
   * 获取用户信息（根据用户ID）
   */
  getUserById: (userId: number): Promise<ApiResponse<UserProfile>> => {
    return request.get(`/users/${userId}`)
  },

  /**
   * 获取用户列表（管理员功能）
   */
  getUserList: (params?: {
    page?: number
    page_size?: number
    search?: string
    is_active?: boolean
    is_vip?: boolean
  }): Promise<ApiResponse<{
    users: User[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }>> => {
    return request.get('/users/', { params })
  },

}

export default userAPI
