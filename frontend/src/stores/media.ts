import { defineStore } from 'pinia'
import { ref } from 'vue'
import { mediaAPI } from '../services/media'
import { handleApiError } from '../utils/api'
import type { MediaItem, MediaUploadData, MediaListParams, MediaUpdateData, MediaStats } from '../types'

export const useMediaStore = defineStore('media', () => {
  // 状态
  const mediaItems = ref<MediaItem[]>([])
  const currentMedia = ref<MediaItem | null>(null)
  const mediaStats = ref<MediaStats>({
    total_media: 0,
    total_images: 0,
    total_videos: 0,
    total_views: 0,
    total_likes: 0,
    total_size: 0,
  })
  const pagination = ref({
    page: 1,
    page_size: 12,
    total: 0,
    total_pages: 0,
  })
  const loading = ref(false)
  const uploading = ref(false)
  const uploadProgress = ref(0)
  const error = ref<string | null>(null)

  // 操作方法
  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const setUploading = (isUploading: boolean) => {
    uploading.value = isUploading
  }

  const setUploadProgress = (progress: number) => {
    uploadProgress.value = progress
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const clearError = () => {
    error.value = null
  }

  // 获取媒体列表
  const getMediaList = async (params?: MediaListParams) => {
    try {
      setLoading(true)
      clearError()

      const requestParams = {
        page: params?.page || pagination.value.page,
        page_size: params?.page_size || pagination.value.page_size,
        ...params
      }

      const response = await mediaAPI.getMediaList(requestParams)
      
      if (response.data) {
        mediaItems.value = response.data.media
        pagination.value = {
          page: response.data.page,
          page_size: response.data.page_size,
          total: response.data.total,
          total_pages: response.data.total_pages,
        }
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

  // 获取媒体详情
  const getMediaById = async (id: number) => {
    try {
      setLoading(true)
      clearError()

      const response = await mediaAPI.getMediaById(id)
      
      if (response.data) {
        currentMedia.value = response.data
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

  // 上传媒体
  const uploadMedia = async (file: File, data: MediaUploadData) => {
    try {
      setUploading(true)
      setUploadProgress(0)
      clearError()

      const response = await mediaAPI.uploadMedia(file, data, (progress) => {
        setUploadProgress(progress)
      })
      
      if (response.data) {
        // 添加到媒体列表开头
        mediaItems.value.unshift(response.data)
      }

      return response
    } catch (err: any) {
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  // 更新媒体信息
  const updateMedia = async (id: number, data: MediaUpdateData) => {
    try {
      setLoading(true)
      clearError()

      const response = await mediaAPI.updateMedia(id, data)
      
      if (response.data) {
        // 更新本地状态
        const index = mediaItems.value.findIndex(item => item.id === id)
        if (index !== -1) {
          mediaItems.value[index] = response.data
        }
        
        if (currentMedia.value?.id === id) {
          currentMedia.value = response.data
        }
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

  // 删除媒体
  const deleteMedia = async (id: number) => {
    try {
      setLoading(true)
      clearError()

      const response = await mediaAPI.deleteMedia(id)
      
      // 从列表中移除
      const index = mediaItems.value.findIndex(item => item.id === id)
      if (index !== -1) {
        mediaItems.value.splice(index, 1)
      }
      
      // 如果是当前媒体，清空
      if (currentMedia.value?.id === id) {
        currentMedia.value = null
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

  // 点赞/取消点赞媒体
  const toggleLike = async (id: number) => {
    try {
      const response = await mediaAPI.toggleLike(id)
      
      if (response.data) {
        // 更新本地状态
        const mediaItem = mediaItems.value.find(item => item.id === id)
        if (mediaItem) {
          mediaItem.likes = response.data.likes
        }

        if (currentMedia.value?.id === id) {
          currentMedia.value.likes = response.data.likes
        }
      }

      return response
    } catch (err: any) {
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }

  // 下载媒体
  const downloadMedia = async (id: number, filename?: string) => {
    try {
      await mediaAPI.downloadMedia(id, filename)
    } catch (err: any) {
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }

  // 获取媒体统计
  const getMediaStats = async () => {
    try {
      setLoading(true)
      clearError()

      const response = await mediaAPI.getMediaStats()
      
      if (response.data) {
        mediaStats.value = response.data
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

  // 清空媒体列表
  const clearMediaItems = () => {
    mediaItems.value = []
    currentMedia.value = null
    pagination.value = {
      page: 1,
      page_size: 12,
      total: 0,
      total_pages: 0,
    }
  }

  return {
    // 状态
    mediaItems,
    currentMedia,
    mediaStats,
    pagination,
    loading,
    uploading,
    uploadProgress,
    error,
    // 方法
    setLoading,
    setUploading,
    setUploadProgress,
    setError,
    clearError,
    getMediaList,
    getMediaById,
    uploadMedia,
    updateMedia,
    deleteMedia,
    toggleLike,
    downloadMedia,
    getMediaStats,
    clearMediaItems,
  }
})
