<template>
  <n-modal
    v-model:show="isOpen"
    preset="card"
    title="上传媒体文件"
    :style="{ width: '600px', maxWidth: '90vw' }"
    :loading="mediaStore.uploading"
  >
    <n-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-placement="top"
    >
      <!-- 基本信息 -->
      <n-form-item path="title" label="标题" required>
        <n-input 
          v-model:value="form.title" 
          placeholder="请输入媒体标题"
          :maxlength="100"
          show-count
        />
      </n-form-item>

      <!-- 文件上传 -->
      <n-upload
          :on-before-upload="beforeUpload"
          accept="image/*,video/*"
          :show-file-list="false"
          :directory="false"
          :multiple="false"
      >
        <n-button type="primary" ghost>
          <template #icon>
            <n-icon><cloud-upload-outline /></n-icon>
          </template>
          选择文件
        </n-button>
      </n-upload>

      <!-- 上传进度 -->
      <div v-if="mediaStore.uploading" class="upload-progress">
        <n-progress 
          type="line" 
          :percentage="mediaStore.uploadProgress" 
          :status="mediaStore.uploadProgress === 100 ? 'success' : 'default'"
          processing
        />
        <p class="progress-text">上传中... {{ mediaStore.uploadProgress }}%</p>
      </div>

      <n-form-item path="description" label="描述">
        <n-input 
          v-model:value="form.description" 
          type="textarea"
          placeholder="请输入描述信息（可选）"
          :rows="3"
          :maxlength="500"
          show-count
        />
      </n-form-item>

      <!-- 价格设置 -->
      <n-form-item path="is_paid" label="内容类型">
        <n-radio-group v-model:value="form.is_paid">
          <n-space>
            <n-radio :value="false">免费内容</n-radio>
            <n-radio :value="true">付费内容</n-radio>
          </n-space>
        </n-radio-group>
      </n-form-item>

      <n-form-item 
        v-if="form.is_paid" 
        path="price" 
        label="价格"
      >
        <n-input-number
          v-model:value="form.price"
          placeholder="请设置价格"
          :min="0.01"
          :max="999"
          :precision="2"
          style="width: 100%"
        >
          <template #prefix>¥</template>
        </n-input-number>
      </n-form-item>

      <!-- 文件预览 -->
      <div v-if="previewUrl" class="file-preview">
        <h4>文件预览:</h4>
        <div class="preview-content">
          <img 
            v-if="fileType === 'image'" 
            :src="previewUrl" 
            alt="预览"
            style="max-width: 100%; max-height: 200px; object-fit: contain;"
          />
          <video 
            v-else-if="fileType === 'video'"
            :src="previewUrl" 
            controls
            style="max-width: 100%; max-height: 200px;"
          />
        </div>
        <div class="file-info">
          <p>文件大小: {{ formatFileSize(fileSize) }}</p>
          <p v-if="fileType === 'video' && videoDuration">
            时长: {{ formatDuration(videoDuration) }}
          </p>
        </div>
      </div>
    </n-form>
    
    <template #footer>
      <n-space justify="end">
        <n-button @click="handleCancel">取消</n-button>
        <n-button 
          type="primary" 
          @click="handleSubmit"
          :loading="mediaStore.uploading"
        >
          上传
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import {
  NModal,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NUpload,
  NProgress,
  NRadioGroup,
  NRadio,
  NInputNumber,
  NSpace,
  NIcon,
  type UploadFileInfo,
} from 'naive-ui'
import { CloudUploadOutline } from '@vicons/ionicons5'
import { useMediaStore } from '@/stores'
import { formatFileSize, formatDuration, isImageFile, isVideoFile } from '@/utils'
import type { MediaUploadData, MediaItem } from '@/types'

interface Props {
  open: boolean
}

interface Emits {
  (e: 'update:open', open: boolean): void
  (e: 'uploaded', media: MediaItem): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const mediaStore = useMediaStore()
const message = useMessage()
const formRef = ref()

const isOpen = computed({
  get: () => props.open,
  set: (val) => emit('update:open', val)
})

// 表单数据
const form = reactive<MediaUploadData>({
  title: '',
  description: '',
  is_paid: false,
  price: undefined as number | undefined,
})

// 文件相关
const selectedFile = ref<File | null>(null)
const previewUrl = ref('')
const fileType = ref<'image' | 'video' | ''>('')
const fileSize = ref(0)
const videoDuration = ref(0)

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { max: 100, message: '标题长度不能超过100个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述长度不能超过500个字符', trigger: 'blur' }
  ]
}

// 文件上传前检查
const beforeUpload = (options: { file: UploadFileInfo }): boolean => {
  const file = options.file.file as File
  
  // 检查文件类型
  if (!isImageFile(file) && !isVideoFile(file)) {
    message.error('只支持图片和视频文件！')
    return false
  }

  // 检查文件大小 (50MB)
  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    message.error('文件大小不能超过50MB！')
    return false
  }

  // 设置选中的文件
  selectedFile.value = file
  fileSize.value = file.size
  
  // 设置文件类型
  if (isImageFile(file)) {
    fileType.value = 'image'
  } else if (isVideoFile(file)) {
    fileType.value = 'video'
  }

  // 生成预览URL
  previewUrl.value = URL.createObjectURL(file)

  // 如果是视频，获取时长
  if (fileType.value === 'video') {
    getVideoDuration(file)
  }

  // 自动设置标题（如果为空）
  if (!form.title) {
    form.title = file.name.split('.')[0]
  }

  return false // 阻止自动上传
}

// 获取视频时长
const getVideoDuration = (file: File) => {
  const video = document.createElement('video')
  video.preload = 'metadata'
  
  video.onloadedmetadata = () => {
    videoDuration.value = video.duration
    URL.revokeObjectURL(video.src)
  }
  
  video.src = URL.createObjectURL(file)
}

// 移除文件
const handleRemove = () => {
  selectedFile.value = null
  previewUrl.value = ''
  fileType.value = ''
  fileSize.value = 0
  videoDuration.value = 0
  
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  
  return true
}

// 提交表单
const handleSubmit = async () => {
  if (!selectedFile.value) {
    message.error('请选择要上传的文件')
    return
  }

  try {
    // 表单验证
    await formRef.value?.validate()
  } catch (validationError) {
    // 表单验证失败，直接返回
    console.error('Form validation failed:', validationError)
    return
  }

  try {
    // 上传文件
    console.log('[MediaUpload] 调用上传接口')
    const response = await mediaStore.uploadMedia(selectedFile.value, form)
    
    console.log('[MediaUpload] 上传接口返回:', response)
    console.log('[MediaUpload] 媒体数据:', response.media)
    
    message.success('媒体文件上传成功！')
    // 传递媒体对象给父组件
    emit('uploaded', response.media)
    handleCancel()
  } catch (error) {
    // 上传失败
    console.error('[MediaUpload] Upload failed:', error)
    message.error('媒体文件上传失败，请重试！')
  }
}

// 取消上传
const handleCancel = () => {
  // 重置表单
  form.title = ''
  form.description = ''
  form.is_paid = false
  form.price = undefined

  // 清理文件
  handleRemove()

  // 重置表单验证
  formRef.value?.restoreValidation()

  isOpen.value = false
}

// 监听付费状态变化
watch(() => form.is_paid, (isPaid) => {
  if (!isPaid) {
    form.price = undefined
  }
})

// 组件卸载时清理URL
const cleanup = () => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
}

// 监听open变化，关闭时清理
watch(() => props.open, (open) => {
  if (!open) {
    cleanup()
  }
})
</script>

<style scoped>
:deep(.n-modal) {
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
}

:deep(.n-card__header) {
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-dark-600);
}

:deep(.n-form-item-label) {
  color: var(--color-text-primary);
  font-weight: 500;
}

:deep(.n-input) {
  background: var(--color-dark-700);
  border-color: var(--color-dark-600);
}

:deep(.n-input__input-el),
:deep(.n-input__textarea-el) {
  color: var(--color-text-primary);
}

:deep(.n-input:hover) {
  border-color: var(--color-neon-blue);
}

:deep(.n-input.n-input--focus) {
  border-color: var(--color-neon-blue);
  box-shadow: 0 0 0 2px rgba(5, 217, 232, 0.2);
}

:deep(.n-input-number) {
  background: var(--color-dark-700);
  border-color: var(--color-dark-600);
}

:deep(.n-input-number__input) {
  color: var(--color-text-primary);
}

:deep(.n-input-number:hover) {
  border-color: var(--color-neon-blue);
}

:deep(.n-input-number.n-input-number--focus) {
  border-color: var(--color-neon-blue);
  box-shadow: 0 0 0 2px rgba(5, 217, 232, 0.2);
}

:deep(.n-radio) {
  color: var(--color-text-primary);
}

:deep(.n-upload-dragger:hover) {
  border-color: var(--color-neon-blue);
  background: var(--color-dark-600);
}

:deep(.upload-icon-container .n-icon) {
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.n-upload-dragger .n-text) {
  color: var(--color-text-primary);
  display: block;
  margin-bottom: 8px;
}

:deep(.n-upload-dragger .n-p) {
  color: var(--color-text-secondary);
  display: block;
}

.upload-progress {
  margin: 16px 0;
  padding: 20px;
  background: var(--color-dark-700);
  border: 1px solid var(--color-dark-600);
  border-radius: 12px;
}

.upload-progress :deep(.n-progress-graph-line-fill) {
  background: linear-gradient(90deg, var(--color-neon-blue), var(--color-neon-purple));
}

.progress-text {
  text-align: center;
  margin: 12px 0 0 0;
  color: var(--color-neon-blue);
  font-size: 0.875rem;
  font-weight: 500;
}

.file-preview {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid var(--color-dark-600);
  border-radius: 12px;
  background: var(--color-dark-700);
  transition: all 0.3s ease;
}

.file-preview:hover {
  border-color: var(--color-neon-blue);
  box-shadow: 0 4px 16px rgba(5, 217, 232, 0.2);
}

.file-preview h4 {
  margin: 0 0 16px 0;
  color: var(--color-neon-blue);
  font-weight: 600;
  font-size: 1rem;
}

.preview-content {
  text-align: center;
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-dark-900);
  padding: 12px;
}

.preview-content img,
.preview-content video {
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.file-info {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.file-info p {
  margin: 6px 0;
  padding: 6px 12px;
  background: var(--color-dark-600);
  border-radius: 6px;
  display: inline-block;
}

:deep(.n-card__footer) {
  border-top: 1px solid var(--color-dark-600);
}
</style>