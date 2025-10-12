<template>
  <div class="gallery-page">
    <!-- 页头 -->
    <section class="gallery-header">
      <h1 class="page-title text-neon-blue">作品展示</h1>
      <p class="page-subtitle">探索摄影作品集</p>
      <n-button 
        v-if="authStore.isAdmin"
        class="upload-btn"
        @click="showUploadModal = true"
      >
        <template #icon>
          <n-icon><add-outline /></n-icon>
        </template>
        上传内容
      </n-button>
    </section>
    
    <!-- 分类过滤 -->
    <section class="filter-section">
      <div class="filter-tabs">
        <button 
          class="filter-tab"
          :class="{ active: !filters.media_type }"
          @click="handleFilterTab('')"
        >
          全部作品
        </button>
        <button 
          class="filter-tab"
          :class="{ active: filters.media_type === 'image' }"
          @click="handleFilterTab('image')"
        >
          照片
        </button>
        <button 
          class="filter-tab"
          :class="{ active: filters.media_type === 'video' }"
          @click="handleFilterTab('video')"
        >
          视频
        </button>
      </div>
      
      <div class="filter-controls">
        <div class="search-box">
          <n-input 
            v-model:value="filters.search"
            placeholder="搜索标题、标签..."
            clearable
            @keydown.enter="handleSearch"
          >
            <template #prefix>
              <n-icon><search-outline /></n-icon>
            </template>
          </n-input>
        </div>
      </div>
    </section>

    <!-- 加载状态 -->
    <n-spin v-if="mediaStore.loading" size="large" class="loading-spinner" />
    
    <div v-else-if="mediaStore.mediaItems.length > 0">
      <!-- 免费作品区 -->
      <section v-if="freeItems.length > 0" class="works-section">
        <h2 class="section-title">
          <span class="title-bar"></span>
          免费浏览
        </h2>
        <horizontal-scroll-container>
          <free-work-card 
            v-for="item in freeItems" 
            :key="item.id"
            :work="item"
            @click="handlePreview(item)"
          />
        </horizontal-scroll-container>
      </section>
      
      <!-- 付费作品区 -->
      <section v-if="paidItems.length > 0" class="works-section">
        <h2 class="section-title">
          <span class="title-bar premium"></span>
          Premium 精选作品
        </h2>
        <horizontal-scroll-container>
          <premium-work-card 
            v-for="item in paidItems" 
            :key="item.id"
            :work="item"
            @unlock="handlePreview(item)"
            @preview="handlePreview(item)"
          />
        </horizontal-scroll-container>
      </section>
    </div>
    
    <!-- 空状态 -->
    <div v-else class="empty-state">
      <n-icon size="80" color="#333">
        <images-outline />
      </n-icon>
      <p>暂无作品</p>
    </div>
    
    <!-- 分页 -->
    <div class="pagination-section" v-if="mediaStore.pagination.total > 0">
      <n-pagination 
        v-model:page="mediaStore.pagination.page"
        v-model:page-size="mediaStore.pagination.page_size"
        :page-count="Math.ceil(mediaStore.pagination.total / mediaStore.pagination.page_size)"
        show-quick-jumper
        @update:page="handlePageChange"
      />
    </div>

    <!-- 媒体预览模态框 -->
    <n-modal
      v-model:show="previewVisible"
      preset="card"
      :title="currentPreview?.title"
      :style="{ width: '800px', maxWidth: '90vw' }"
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
          <n-p v-if="currentPreview.description">{{ currentPreview.description }}</n-p>
          <n-space>
            <span>上传者: {{ currentPreview.user?.username || '未知' }}</span>
            <span>上传时间: {{ formatDate(currentPreview.created_at) }}</span>
          </n-space>
          <div class="preview-actions">
            <n-button @click="handleLike(currentPreview)">
              <template #icon>
                <n-icon><heart-outline /></n-icon>
              </template>
              点赞 ({{ currentPreview.like_count }})
            </n-button>
          </div>
        </div>
      </div>
    </n-modal>

    <!-- 上传模态框 -->
    <MediaUpload 
      v-model:open="showUploadModal" 
      @uploaded="handleUploaded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted, watch, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { 
  NPagination,
  NButton,
  NSpin,
  NModal,
  NSpace,
  NInput,
  NP,
  NIcon,
} from 'naive-ui'
import { 
  AddOutline,
  EyeOutline,
  HeartOutline,
  SearchOutline,
  ImagesOutline,
} from '@vicons/ionicons5'
import { useMediaStore } from '@/stores'
import { useAuthStore } from '@/stores'
import { formatNumber, formatFileSize, formatDuration, formatDate, getFullFileUrl } from '@/utils'
import type { MediaItem, MediaListParams } from '@/types'
import MediaUpload from '../components/MediaUpload.vue'
import HorizontalScrollContainer from '../components/ui/HorizontalScrollContainer.vue'
import FreeWorkCard from '../components/cards/FreeWorkCard.vue'
import PremiumWorkCard from '../components/cards/PremiumWorkCard.vue'

const mediaStore = useMediaStore()
const authStore = useAuthStore()
const message = useMessage()

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

// 计算属性：分离免费和付费作品
const freeItems = computed(() => {
  return mediaStore.mediaItems.filter(item => !item.is_paid)
})

const paidItems = computed(() => {
  return mediaStore.mediaItems.filter(item => item.is_paid)
})

// 处理分类标签切换
const handleFilterTab = (type: string) => {
  filters.media_type = type || undefined
  filters.page = 1
  loadMediaList()
}

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
    return () => h('div', {
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
  
  return () => h('img', {
    alt: item.title,
    src: coverUrl,
    style: { height: '200px', width: '100%', objectFit: 'cover' },
    onError: (e: Event) => {
      console.error('[Gallery.renderMediaCover] 图片加载失败:', coverUrl, e)
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
.gallery-page {
  min-height: 100vh;
  background: var(--color-dark-900);
  padding: 80px 24px 48px;
}

/* 页头 */
.gallery-header {
  text-align: center;
  margin-bottom: 48px;
  position: relative;
}

.page-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: bold;
  margin: 0 0 16px;
  text-shadow: 
    0 0 20px rgba(5, 217, 232, 0.5),
    0 0 40px rgba(5, 217, 232, 0.3);
}

.text-neon-blue {
  color: var(--color-neon-blue);
}

.page-subtitle {
  font-size: 1.125rem;
  color: var(--color-text-secondary);
  margin: 0 0 24px;
}

.upload-btn {
  background: linear-gradient(135deg, var(--color-neon-blue), var(--color-neon-purple));
  border: none;
  color: var(--color-dark-900);
  font-weight: 600;
  padding: 12px 32px;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.upload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(5, 217, 232, 0.4);
}

/* 分类过滤 */
.filter-section {
  margin-bottom: 48px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-tabs {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 12px 32px;
  border-radius: 50px;
  background: var(--color-dark-700);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-dark-600);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-tab:hover {
  background: var(--color-dark-600);
  border-color: var(--color-neon-blue);
}

.filter-tab.active {
  background: var(--color-neon-blue);
  color: var(--color-dark-900);
  border-color: var(--color-neon-blue);
  box-shadow: 0 4px 16px rgba(5, 217, 232, 0.3);
}

.filter-controls {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.search-box {
  max-width: 400px;
  width: 100%;
}

.search-box :deep(.n-input) {
  background: var(--color-dark-700);
  border-color: var(--color-dark-600);
}

.search-box :deep(.n-input__input-el) {
  color: var(--color-text-primary);
}

.search-box :deep(.n-input:hover) {
  border-color: var(--color-neon-blue);
}

.search-box :deep(.n-input.n-input--focus) {
  border-color: var(--color-neon-blue);
  box-shadow: 0 0 0 2px rgba(5, 217, 232, 0.2);
}

/* 作品区域 */
.works-section {
  margin-bottom: 64px;
}

.section-title {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  color: var(--color-text-primary);
}

.title-bar {
  display: inline-block;
  width: 4px;
  height: 32px;
  background: var(--color-neon-blue);
  margin-right: 16px;
  border-radius: 2px;
}

.title-bar.premium {
  background: var(--color-neon-pink);
}

/* 加载和空状态 */
.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.empty-state {
  text-align: center;
  padding: 80px 24px;
  color: var(--color-text-secondary);
}

.empty-state p {
  margin-top: 16px;
  font-size: 1.125rem;
}

/* 分页 */
.pagination-section {
  margin-top: 64px;
  display: flex;
  justify-content: center;
}

.pagination-section :deep(.n-pagination) {
  gap: 8px;
}

.pagination-section :deep(.n-pagination-item) {
  background: var(--color-dark-700);
  border-color: var(--color-dark-600);
  color: var(--color-text-primary);
}

.pagination-section :deep(.n-pagination-item:hover) {
  border-color: var(--color-neon-blue);
}

.pagination-section :deep(.n-pagination-item--active) {
  background: var(--color-neon-blue);
  border-color: var(--color-neon-blue);
  color: var(--color-dark-900);
}

/* 预览模态框 */
.preview-content {
  text-align: center;
}

.preview-media {
  margin-bottom: 24px;
  background: var(--color-dark-800);
  border-radius: 12px;
  overflow: hidden;
}

.preview-info {
  text-align: left;
  color: var(--color-text-secondary);
}

.preview-info p {
  margin-bottom: 16px;
  line-height: 1.6;
}

.preview-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .gallery-page {
    padding: 64px 16px 32px;
  }
  
  .gallery-header {
    margin-bottom: 32px;
  }
  
  .filter-section {
    margin-bottom: 32px;
  }
  
  .works-section {
    margin-bottom: 48px;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .pagination-section {
    margin-top: 48px;
  }
}
</style>
