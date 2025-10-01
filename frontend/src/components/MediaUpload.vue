<template>
  <a-modal
    :open="open"
    title="上传媒体文件"
    :width="600"
    :confirm-loading="mediaStore.uploading"
    @ok="handleSubmit"
    @cancel="handleCancel"
  >
    <a-form
      :model="form"
      :rules="rules"
      layout="vertical"
      ref="formRef"
    >
      <!-- 文件上传 -->
      <a-form-item label="选择文件">
        <a-upload-dragger
          v-model:file-list="fileList"
          name="file"
          :multiple="false"
          :before-upload="beforeUpload"
          @remove="handleRemove"
          accept="image/*,video/*"
        >
          <p class="ant-upload-drag-icon">
            <inbox-outlined />
          </p>
          <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p class="ant-upload-hint">
            支持图片和视频文件，单个文件大小不超过50MB
          </p>
        </a-upload-dragger>
      </a-form-item>

      <!-- 上传进度 -->
      <div v-if="mediaStore.uploading" class="upload-progress">
        <a-progress 
          :percent="mediaStore.uploadProgress" 
          :status="mediaStore.uploadProgress === 100 ? 'success' : 'active'"
        />
        <p class="progress-text">上传中... {{ mediaStore.uploadProgress }}%</p>
      </div>

      <!-- 基本信息 -->
      <a-form-item label="标题" name="title" required>
        <a-input 
          v-model:value="form.title" 
          placeholder="请输入媒体标题"
          :max-length="100"
          show-count
          id="form_item_title"
        />
      </a-form-item>

      <a-form-item label="描述" name="description">
        <a-textarea 
          v-model:value="form.description" 
          placeholder="请输入描述信息（可选）"
          :rows="3"
          :max-length="500"
          show-count
          id="form_item_description"
        />
      </a-form-item>

      <a-form-item label="标签" name="tags">
        <a-input 
          v-model:value="form.tags" 
          placeholder="请输入标签，用逗号分隔（可选）"
          :max-length="200"
          id="form_item_tags"
        />
      </a-form-item>

      <!-- 价格设置 -->
      <a-form-item label="内容类型" name="is_paid">
        <a-radio-group v-model:value="form.is_paid" id="form_item_is_paid">
          <a-radio :value="false">免费内容</a-radio>
          <a-radio :value="true">付费内容</a-radio>
        </a-radio-group>
      </a-form-item>

      <a-form-item 
        v-if="form.is_paid" 
        label="价格" 
        name="price"
        :rules="priceRules"
      >
        <a-input-number
          v-model:value="form.price"
          placeholder="请设置价格"
          :min="0.01"
          :max="999"
          :precision="2"
          style="width: 100%"
          id="form_item_price"
        >
          <template #addonBefore>¥</template>
        </a-input-number>
      </a-form-item>

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
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  Modal as AModal,
  Form as AForm,
  Input as AInput,
  Button as AButton,
  Upload as AUpload,
  Progress as AProgress,
  Radio as ARadio,
  InputNumber as AInputNumber,
} from 'ant-design-vue'
import { InboxOutlined } from '@ant-design/icons-vue'
import { useMediaStore } from '@/stores'
import { formatFileSize, formatDuration, isImageFile, isVideoFile } from '@/utils'
import type { MediaUploadData, MediaItem } from '@/types'
import type { UploadFile } from 'ant-design-vue'

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
const formRef = ref()

// 表单数据
const form = reactive<MediaUploadData>({
  title: '',
  description: '',
  tags: '',
  is_paid: false,
  price: undefined,
})

// 文件相关
const fileList = ref<UploadFile[]>([])
const selectedFile = ref<File | null>(null)
const previewUrl = ref('')
const fileType = ref<'image' | 'video' | ''>('')
const fileSize = ref(0)
const videoDuration = ref(0)

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入标题' },
    { max: 100, message: '标题长度不能超过100个字符' }
  ],
  description: [
    { max: 500, message: '描述长度不能超过500个字符' }
  ],
  tags: [
    { max: 200, message: '标签长度不能超过200个字符' }
  ]
}

const priceRules = computed(() => {
  if (form.is_paid) {
    return [
      { required: true, message: '付费内容必须设置价格' },
      { type: 'number', min: 0.01, message: '价格必须大于0' }
    ]
  }
  return []
})

// 文件上传前检查
const beforeUpload = (file: File) => {
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
}

// 提交表单
const handleSubmit = async () => {
  if (!selectedFile.value) {
    message.error('请选择要上传的文件')
    return
  }

  try {
    // 表单验证
    await formRef.value.validate()
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
  form.tags = ''
  form.is_paid = false
  form.price = undefined

  // 清理文件
  fileList.value = []
  handleRemove()

  // 重置表单验证
  formRef.value?.resetFields()

  emit('update:open', false)
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
.upload-progress {
  margin: 16px 0;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 6px;
}

.progress-text {
  text-align: center;
  margin: 8px 0 0 0;
  color: #666;
  font-size: 14px;
}

.file-preview {
  margin-top: 16px;
  padding: 16px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  background: #fafafa;
}

.file-preview h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.preview-content {
  text-align: center;
  margin-bottom: 12px;
}

.file-info {
  font-size: 12px;
  color: #666;
}

.file-info p {
  margin: 4px 0;
}

.ant-upload-drag {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  background: #fafafa;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.ant-upload-drag:hover {
  border-color: #40a9ff;
}

.ant-upload-drag-icon {
  font-size: 48px;
  color: #40a9ff;
}

.ant-upload-text {
  font-size: 16px;
  color: #666;
  margin: 0 0 4px 0;
}

.ant-upload-hint {
  font-size: 14px;
  color: #999;
  margin: 0;
}
</style>
