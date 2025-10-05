<template>
  <div class="page-container">
    <div class="header-section">
      <a-typography-title :level="2">照片视频</a-typography-title>
      <a-button 
        type="primary" 
        @click="showUploadModal = true"
        v-if="authStore.isAdmin"
      >
        <template #icon>
          <plus-outlined />
        </template>
        上传内容
      </a-button>
    </div>
    
    <!-- 筛选器 -->
    <div class="filter-section">
      <a-row :gutter="16" align="middle">
        <a-col :xs="24" :sm="12" :md="8">
          <a-space>
            <a-select
              v-model:value="filters.media_type"
              :style="{ width: '120px' }"
              placeholder="类型"
              @change="handleFilterChange"
            >
              <a-select-option value="">全部类型</a-select-option>
              <a-select-option value="image">照片</a-select-option>
              <a-select-option value="video">视频</a-select-option>
            </a-select>
            
            <a-select
              v-model:value="filters.is_paid"
              :style="{ width: '120px' }"
              placeholder="价格"
              @change="handleFilterChange"
            >
              <a-select-option :value="undefined">全部价格</a-select-option>
              <a-select-option :value="false">免费</a-select-option>
              <a-select-option :value="true">付费</a-select-option>
            </a-select>
          </a-space>
        </a-col>
        
        <a-col :xs="24" :sm="12" :md="8">
          <a-input-search 
            v-model:value="filters.search"
            placeholder="搜索标题、标签..."
            @search="handleSearch"
          />
        </a-col>
        
        <a-col :xs="24" :sm="24" :md="8">
          <a-space>
            <span>排序:</span>
            <a-select
              v-model:value="filters.sort_by"
              :style="{ width: '120px' }"
              @change="handleFilterChange"
            >
              <a-select-option value="created_at">最新</a-select-option>
              <a-select-option value="views">最多观看</a-select-option>
              <a-select-option value="likes">最多点赞</a-select-option>
              <a-select-option value="title">标题</a-select-option>
            </a-select>
          </a-space>
        </a-col>
      </a-row>
    </div>

    <!-- 加载状态 -->
    <a-spin :spinning="mediaStore.loading" tip="加载中...">
      <!-- 媒体网格 -->
      <a-row :gutter="[16, 16]" v-if="mediaStore.mediaItems.length > 0">
        <a-col 
          v-for="item in mediaStore.mediaItems" 
          :key="item.id"
          :xs="12" 
          :sm="8" 
          :md="6" 
          :lg="4"
        >
          <div class="media-card">
            <a-card 
              hoverable
              :cover="renderMediaCover(item)"
              :actions="[
                h(EyeOutlined, { onClick: () => handleView(item) }),
                h(HeartOutlined, { 
                  style: { color: '#ff4d4f' },
                  onClick: () => handleLike(item) 
                }),
                h(DownloadOutlined, { onClick: () => handleDownload(item) })
              ]"
              @click="handlePreview(item)"
            >
              <a-card-meta>
                <template #title>
                  <div class="card-title">
                    {{ item.title }}
                    <a-tag v-if="item.is_paid" color="orange" size="small">
                      ¥{{ item.price }}
                    </a-tag>
                    <a-tag v-else color="green" size="small">
                      免费
                    </a-tag>
                  </div>
                </template>
                <template #description>
                  <div class="card-description">
                    <div class="stats">
                      <span><eye-outlined /> {{ formatNumber(item.view_count) }}</span>
                      <span><heart-outlined /> {{ formatNumber(item.like_count) }}</span>
                    </div>
                    <div class="file-info">
                      <span class="file-size">{{ formatFileSize(item.file_size) }}</span>
                      <span v-if="item.duration" class="duration">
                        {{ formatDuration(item.duration) }}
                      </span>
                    </div>
                  </div>
                </template>
              </a-card-meta>
            </a-card>
          </div>
        </a-col>
      </a-row>

      <!-- 空状态 -->
      <a-empty 
        v-else-if="!mediaStore.loading"
        description="暂无内容"
        :image="empty.PRESENTED_IMAGE_SIMPLE"
      />
    </a-spin>

    <!-- 分页 -->
    <div class="pagination-section" v-if="mediaStore.pagination.total > 0">
      <a-pagination 
        v-model:current="mediaStore.pagination.page"
        v-model:page-size="mediaStore.pagination.page_size"
        :total="mediaStore.pagination.total"
        :show-size-changer="false"
        :show-quick-jumper="true"
        :show-total="(total, range) => `${range[0]}-${range[1]} 共 ${total} 条`"
        @change="handlePageChange"
      />
    </div>

    <!-- 媒体预览模态框 -->
    <a-modal
      v-model:open="previewVisible"
      :title="currentPreview?.title"
      :width="800"
      :footer="null"
      center
    >
      <div v-if="currentPreview" class="preview-content">
        <div class="preview-media">
          <img 
            v-if="currentPreview.media_type === 'image'"
            :src="getFullFileUrl(currentPreview.file_url)"
            :alt="currentPreview.title"
            style="width: 100%; height: auto; max-height: 500px; object-fit: contain;"
            @error="(e: Event) => {
              console.error('[Gallery.preview] 预览图片加载失败:', getFullFileUrl(currentPreview?.file_url), e)
            }"
            @load="() => {
              console.log('[Gallery.preview] 预览图片加载成功:', getFullFileUrl(currentPreview?.file_url))
            }"
          />
          <video 
            v-else-if="currentPreview.media_type === 'video'"
            :src="getFullFileUrl(currentPreview.file_url)"
            controls
            style="width: 100%; height: auto; max-height: 500px;"
            @error="(e: Event) => {
              console.error('[Gallery.preview] 预览视频加载失败:', getFullFileUrl(currentPreview?.file_url), e)
            }"
            @loadeddata="() => {
              console.log('[Gallery.preview] 预览视频加载成功:', getFullFileUrl(currentPreview?.file_url))
            }"
          />
        </div>
        <div class="preview-info">
          <p v-if="currentPreview.description">{{ currentPreview.description }}</p>
          <a-space>
            <span>上传者: {{ currentPreview.user?.username || '未知' }}</span>
            <span>上传时间: {{ formatDate(currentPreview.created_at) }}</span>
          </a-space>
          <div class="preview-actions">
            <a-button @click="handleLike(currentPreview)">
              <template #icon>
                <heart-outlined />
              </template>
              点赞 ({{ currentPreview.like_count }})
            </a-button>
            <a-button @click="handleDownload(currentPreview)">
              <template #icon>
                <download-outlined />
              </template>
              下载
            </a-button>
          </div>
        </div>
      </div>
    </a-modal>

    <!-- 上传模态框 -->
    <MediaUpload 
      v-model:open="showUploadModal" 
      @uploaded="handleUploaded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted, watch } from 'vue'
import { message, Empty } from 'ant-design-vue'
import { 
  Typography,
  Space as ASpace,
  Select as ASelect,
  Input as AInput,
  Row as ARow,
  Col as ACol,
  Card as ACard,
  Pagination as APagination,
  Button as AButton,
  Tag as ATag,
  Spin as ASpin,
  Modal as AModal,
} from 'ant-design-vue'
import { 
  PlusOutlined,
  EyeOutlined,
  HeartOutlined,
  DownloadOutlined,
} from '@ant-design/icons-vue'
import { useMediaStore } from '../stores/media'
import { useAuthStore } from '../stores/auth'
import { formatNumber, formatFileSize, formatDuration, formatDate, getFullFileUrl } from '../utils'
import type { MediaItem, MediaListParams } from '../types'
import MediaUpload from '../components/MediaUpload.vue'

const mediaStore = useMediaStore()
const authStore = useAuthStore()
const empty = Empty

// 响应式状态
const filters = reactive<MediaListParams>({
  page: 1,
  page_size: 12,
  media_type: undefined,
  is_paid: undefined,
  search: undefined,
  sort_by: 'created_at',
  order: 'desc',
})

// 预览相关
const previewVisible = ref(false)
const currentPreview = ref<MediaItem | null>(null)
const showUploadModal = ref(false)

// 渲染媒体封面
const renderMediaCover = (item: MediaItem) => {
  const coverPath = item.thumbnail_url || item.file_url
  const coverUrl = getFullFileUrl(coverPath)
  
  console.log('[Gallery.renderMediaCover] 媒体项:', {
    id: item.id,
    title: item.title,
    media_type: item.media_type,
    file_url: item.file_url,
    thumbnail_url: item.thumbnail_url,
    coverPath: coverPath,
    coverUrl: coverUrl
  })
  
  if (item.media_type === 'video') {
    return h('div', {
      style: {
        position: 'relative',
        height: '200px',
        background: `url(${coverUrl}) center/cover`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }
    }, [
      h('div', {
        style: {
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.3)'
        }
      }),
      h('div', {
        style: {
          color: 'white',
          fontSize: '24px',
          zIndex: 1
        }
      }, '▶')
    ])
  }
  
  return h('img', {
    alt: item.title,
    src: coverUrl,
    style: { height: '200px', width: '100%', objectFit: 'cover' },
    onError: (e: Event) => {
      console.error('[Gallery.renderMediaCover] 图片加载失败:', coverUrl, e)
    },
    onLoad: () => {
      console.log('[Gallery.renderMediaCover] 图片加载成功:', coverUrl)
    }
  })
}

// 处理搜索
const handleSearch = () => {
  filters.page = 1
  loadMediaList()
}

// 处理筛选条件变化
const handleFilterChange = () => {
  filters.page = 1
  loadMediaList()
}

// 处理分页变化
const handlePageChange = (page: number) => {
  filters.page = page
  loadMediaList()
}

// 加载媒体列表
const loadMediaList = async () => {
  try {
    console.log('[Gallery.loadMediaList] 开始加载，筛选条件:', filters)
    await mediaStore.getMediaList(filters)
    console.log('[Gallery.loadMediaList] 加载完成，mediaItems数量:', mediaStore.mediaItems.length)
  } catch (error) {
    console.error('[Gallery.loadMediaList] Failed to load media list:', error)
  }
}

// 处理查看
const handleView = (item: MediaItem) => {
  // 这里可以增加观看次数等逻辑
  console.log('View item:', item.id)
}

// 处理点赞
const handleLike = async (item: MediaItem) => {
  if (!authStore.isAuthenticated) {
    message.warning('请先登录')
    return
  }
  
  try {
    await mediaStore.toggleLike(item.id)
    message.success('操作成功')
  } catch (error) {
    console.error('Like failed:', error)
  }
}

// 处理下载
const handleDownload = async (item: MediaItem) => {
  if (!authStore.isAuthenticated) {
    message.warning('请先登录')
    return
  }
  
  if (item.is_paid && !authStore.isVip) {
    message.warning('付费内容需要VIP权限')
    return
  }
  
  try {
    await mediaStore.downloadMedia(item.id, item.title)
    message.success('下载开始')
  } catch (error) {
    console.error('Download failed:', error)
  }
}

// 处理预览
const handlePreview = (item: MediaItem) => {
  console.log('[Gallery.handlePreview] 预览媒体项:', {
    id: item.id,
    title: item.title,
    media_type: item.media_type,
    file_url: item.file_url,
    thumbnail_url: item.thumbnail_url,
    is_paid: item.is_paid,
    isVip: authStore.isVip
  })
  
  if (item.is_paid && !authStore.isVip) {
    message.warning('付费内容需要VIP权限查看')
    return
  }
  
  currentPreview.value = item
  previewVisible.value = true
}

// 处理上传完成
const handleUploaded = (newMedia: MediaItem) => {
  console.log('[Gallery] 收到上传完成事件:', newMedia)
  message.success('上传成功！')
  showUploadModal.value = false
  // 重新加载列表
  console.log('[Gallery] 重新加载媒体列表')
  loadMediaList()
}

// 监听分页变化
watch(() => mediaStore.pagination.page, (newPage) => {
  if (newPage !== filters.page) {
    filters.page = newPage
  }
})

// 组件挂载时获取数据
onMounted(() => {
  loadMediaList()
})
</script>

<style scoped>
.page-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.filter-section {
  background: #fafafa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.media-card {
  height: 100%;
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  line-height: 1.4;
}

.card-description {
  font-size: 12px;
  color: #666;
}

.stats {
  display: flex;
  gap: 12px;
  margin-bottom: 4px;
}

.stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.file-info {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #999;
}

.pagination-section {
  margin-top: 32px;
  text-align: center;
}

.preview-content {
  text-align: center;
}

.preview-media {
  margin-bottom: 16px;
}

.preview-info {
  text-align: left;
}

.preview-info p {
  margin-bottom: 12px;
  color: #666;
}

.preview-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .header-section {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .filter-section .ant-row {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
