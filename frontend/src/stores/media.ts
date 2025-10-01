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

      // 过滤掉 undefined 和空字符串的参数
      const requestParams: any = {
        page: params?.page || pagination.value.page,
        page_size: params?.page_size || pagination.value.page_size,
      }
      
      if (params) {
        Object.keys(params).forEach(key => {
          const value = params[key as keyof MediaListParams]
          if (value !== undefined && value !== '' && key !== 'page' && key !== 'page_size') {
            requestParams[key] = value
          }
        })
      }

      console.log('[mediaStore.getMediaList] 请求参数:', requestParams)

      const response = await mediaAPI.getMediaList(requestParams)
      
      console.log('[mediaStore.getMediaList] 响应数据:', response)
      console.log('[mediaStore.getMediaList] 媒体列表:', response.media_list)
      console.log('[mediaStore.getMediaList] 媒体列表长度:', response.media_list?.length)
      console.log('[mediaStore.getMediaList] 总数:', response.total)
      
      // 注意：FastAPI的response_model直接返回模型数据，不需要访问.data
      mediaItems.value = response.media_list || []
      console.log('[mediaStore.getMediaList] 赋值后 mediaItems.value 长度:', mediaItems.value.length)
      
      // 打印每个媒体项的详细信息
      if (mediaItems.value.length > 0) {
        console.log('[mediaStore.getMediaList] 媒体项详细信息:')
        mediaItems.value.forEach((item, index) => {
          console.log(`  [${index}] ID: ${item.id}, 标题: ${item.title}`)
          console.log(`      file_url: ${item.file_url}`)
          console.log(`      thumbnail_url: ${item.thumbnail_url}`)
          console.log(`      media_type: ${item.media_type}`)
          console.log(`      status: ${item.status}`)
        })
      }
      
      pagination.value = {
        page: response.page,
        page_size: response.page_size,
        total: response.total,
        total_pages: response.total_pages,
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
      
      // FastAPI response_model 直接返回数据
      currentMedia.value = response

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

      console.log('[mediaStore.uploadMedia] 开始上传:', file.name, data)

      const response = await mediaAPI.uploadMedia(file, data, (progress) => {
        setUploadProgress(progress)
      })
      
      console.log('[mediaStore.uploadMedia] 上传响应:', response)
      console.log('[mediaStore.uploadMedia] 上传成功，媒体对象:', response.media)
      // 上传成功后不直接添加到列表，由页面刷新处理
      // mediaItems.value.unshift(response.media)

      return response
    } catch (err: any) {
      console.error('[mediaStore.uploadMedia] 上传失败:', err)
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
      
      // 更新本地状态
      const index = mediaItems.value.findIndex(item => item.id === id)
      if (index !== -1) {
        mediaItems.value[index] = response
      }
      
      if (currentMedia.value?.id === id) {
        currentMedia.value = response
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
      
      // 更新本地状态
      const mediaItem = mediaItems.value.find(item => item.id === id)
      if (mediaItem && response.like_count !== undefined) {
        mediaItem.like_count = response.like_count
      }

      if (currentMedia.value?.id === id && response.like_count !== undefined) {
        currentMedia.value.like_count = response.like_count
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
      
      mediaStats.value = response

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
