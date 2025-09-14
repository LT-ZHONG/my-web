import { request } from '../utils/api'
import type { 
  MediaItem, 
  MediaUploadData, 
  MediaListParams, 
  MediaUpdateData,
  MediaStats,
  ApiResponse 
} from '@/types'

export const mediaAPI = {
  /**
   * 获取媒体列表
   */
  getMediaList: (params?: MediaListParams): Promise<ApiResponse<{
    media: MediaItem[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }>> => {
    return request.get('/media/', { params })
  },

  /**
   * 获取媒体详情
   */
  getMediaById: (mediaId: number): Promise<ApiResponse<MediaItem>> => {
    return request.get(`/media/${mediaId}`)
  },

  /**
   * 上传媒体文件
   */
  uploadMedia: (
    file: File, 
    data: MediaUploadData, 
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<MediaItem>> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', data.title)
    
    if (data.description) {
      formData.append('description', data.description)
    }
    if (data.tags) {
      formData.append('tags', data.tags)
    }
    formData.append('is_paid', data.is_paid.toString())
    if (data.price !== undefined) {
      formData.append('price', data.price.toString())
    }

    return request.upload('/media/upload', formData, onProgress)
  },

  /**
   * 更新媒体信息
   */
  updateMedia: (mediaId: number, data: MediaUpdateData): Promise<ApiResponse<MediaItem>> => {
    return request.put(`/media/${mediaId}`, data)
  },

  /**
   * 删除媒体
   */
  deleteMedia: (mediaId: number): Promise<ApiResponse<void>> => {
    return request.delete(`/media/${mediaId}`)
  },

  /**
   * 点赞/取消点赞媒体
   */
  toggleLike: (mediaId: number): Promise<ApiResponse<{ liked: boolean; likes: number }>> => {
    return request.post(`/media/${mediaId}/like`)
  },

  /**
   * 下载媒体文件
   */
  downloadMedia: (mediaId: number, filename?: string): Promise<void> => {
    return request.download(`/media/${mediaId}/download`, filename)
  },

  /**
   * 获取媒体统计信息
   */
  getMediaStats: (): Promise<ApiResponse<MediaStats>> => {
    return request.get('/media/stats/overview')
  },

  /**
   * 获取分类列表
   */
  getCategories: (): Promise<ApiResponse<Array<{
    id: number
    name: string
    description?: string
    media_count: number
  }>>> => {
    return request.get('/media/categories/')
  },

  /**
   * 创建分类（管理员）
   */
  createCategory: (data: {
    name: string
    description?: string
  }): Promise<ApiResponse<{
    id: number
    name: string
    description?: string
  }>> => {
    return request.post('/media/categories/', data)
  },

  /**
   * 更新分类（管理员）
   */
  updateCategory: (categoryId: number, data: {
    name?: string
    description?: string
  }): Promise<ApiResponse<{
    id: number
    name: string
    description?: string
  }>> => {
    return request.put(`/media/categories/${categoryId}`, data)
  },

  /**
   * 删除分类（管理员）
   */
  deleteCategory: (categoryId: number): Promise<ApiResponse<void>> => {
    return request.delete(`/media/categories/${categoryId}`)
  }
}

export default mediaAPI
