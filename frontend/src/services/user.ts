import { request } from '../utils/api'
import type { 
  UserProfile, 
  UserUpdateData, 
  User
} from '@/types'

// 用户列表响应类型
export interface UserListResponse {
  users: User[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const userAPI = {
  /**
   * 获取个人信息
   * @returns 直接返回 UserProfile 对象
   */
  getProfile: (): Promise<UserProfile> => {
    return request.get('/users/me')
  },

  /**
   * 更新个人信息
   * @returns 直接返回更新后的 UserProfile 对象
   */
  updateProfile: (data: UserUpdateData): Promise<UserProfile> => {
    return request.put('/users/me', data)
  },

  /**
   * 获取用户信息（根据用户ID）
   * @returns 直接返回 UserProfile 对象
   */
  getUserById: (userId: number): Promise<UserProfile> => {
    return request.get(`/users/${userId}`)
  },

  /**
   * 获取用户列表（管理员功能）
   * @returns 直接返回用户列表响应对象
   */
  getUserList: (params?: {
    page?: number
    page_size?: number
    search?: string
    is_active?: boolean
    is_vip?: boolean
  }): Promise<UserListResponse> => {
    return request.get('/users/', { params })
  },

}

export default userAPI
