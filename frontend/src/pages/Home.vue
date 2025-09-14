<template>
  <div class="page-container">
    <!-- 英雄区域 -->
    <div :style="{
      textAlign: 'center',
      padding: '60px 0',
      background: 'linear-gradient(135deg, #fff5f0 0%, #fff8f5 100%)',
      borderRadius: '16px',
      marginBottom: '48px',
    }">
      <a-typography-title 
        :level="1" 
        :style="{ 
          fontSize: '48px', 
          marginBottom: '16px',
          background: 'linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }"
      >
        欢迎来到我的生活
      </a-typography-title>
      <a-typography-paragraph :style="{ 
        fontSize: '18px', 
        color: '#666', 
        marginBottom: '32px',
        maxWidth: '600px',
        margin: '0 auto 32px',
      }">
        在这里分享我的日常生活照片和视频，记录每一个美好瞬间。
        你可以浏览免费内容，或成为VIP会员解锁更多精彩内容，还可以与我实时聊天交流。
      </a-typography-paragraph>
      <a-space size="large">
        <router-link to="/gallery">
          <a-button 
            type="primary" 
            size="large" 
            class="btn-primary"
            :icon="h(PictureOutlined)"
          >
            浏览照片视频
          </a-button>
        </router-link>
        <router-link to="/chat">
          <a-button 
            size="large" 
            :icon="h(MessageOutlined)"
          >
            开始聊天
          </a-button>
        </router-link>
      </a-space>
    </div>

    <!-- 数据统计 -->
    <a-row :gutter="[24, 24]" :style="{ marginBottom: '48px' }">
      <a-col 
        v-for="(stat, index) in stats" 
        :key="index"
        :xs="12" 
        :sm="6"
      >
        <a-card :style="{ textAlign: 'center', height: '120px' }">
          <div :style="{ 
            fontSize: '32px', 
            color: '#ff6b35', 
            marginBottom: '8px',
          }">
            <component :is="stat.icon" />
          </div>
          <div :style="{ 
            fontSize: '24px', 
            fontWeight: 'bold', 
            color: '#333',
            marginBottom: '4px',
          }">
            {{ stat.value }}
          </div>
          <div :style="{ fontSize: '14px', color: '#666' }">
            {{ stat.label }}
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 最新内容 -->
    <div :style="{ marginBottom: '48px' }">
      <div :style="{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '24px',
      }">
        <a-typography-title :level="2" :style="{ margin: 0 }">
          最新内容
        </a-typography-title>
        <router-link to="/gallery">
          <a-button type="link" :icon="h(RightOutlined)">
            查看全部
          </a-button>
        </router-link>
      </div>
      
      <a-row :gutter="[24, 24]">
        <a-col 
          v-for="item in latestContent" 
          :key="item.id"
          :xs="24" 
          :sm="12" 
          :lg="8"
        >
          <a-card 
            hoverable
            class="card-hover"
          >
            <template #cover>
              <div :style="{ position: 'relative' }">
                <img 
                  :alt="item.title" 
                  :src="item.thumbnail"
                  :style="{ height: '200px', objectFit: 'cover' }"
                />
                <div 
                  v-if="item.type === 'video'"
                  :style="{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    fontSize: '32px',
                    color: 'white',
                    textShadow: '0 2px 4px rgba(0,0,0,0.5)',
                  }"
                >
                  <PlayCircleOutlined />
                </div>
                <div 
                  v-if="item.isPaid"
                  :style="{
                    position: 'absolute',
                    top: '8px',
                    right: '8px',
                    background: '#ff6b35',
                    color: 'white',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                  }"
                >
                  ¥{{ item.price }}
                </div>
              </div>
            </template>
            
            <a-card-meta :title="item.title">
              <template #description>
                <div>
                  <a-typography-paragraph 
                    :ellipsis="{ rows: 2 }" 
                    :style="{ marginBottom: '8px', color: '#666' }"
                  >
                    {{ item.description }}
                  </a-typography-paragraph>
                  <div :style="{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '12px',
                    color: '#999',
                  }">
                    <span>{{ item.date }}</span>
                    <span :style="{ 
                      color: item.isPaid ? '#ff6b35' : '#52c41a',
                      fontWeight: 'bold',
                    }">
                      {{ item.isPaid ? `付费 ¥${item.price}` : '免费' }}
                    </span>
                  </div>
                </div>
              </template>
            </a-card-meta>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- VIP会员推广 -->
    <a-card :style="{
      background: 'linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%)',
      border: 'none',
      color: 'white',
      textAlign: 'center',
      padding: '24px',
    }">
      <CrownOutlined :style="{ fontSize: '48px', marginBottom: '16px' }" />
      <a-typography-title 
        :level="3" 
        :style="{ color: 'white', marginBottom: '16px' }"
      >
        成为VIP会员
      </a-typography-title>
      <a-typography-paragraph :style="{ 
        color: 'white', 
        fontSize: '16px', 
        marginBottom: '24px',
      }">
        解锁所有付费内容，享受无限制浏览体验，优先获得最新内容推送
      </a-typography-paragraph>
      <router-link to="/vip">
        <a-button 
          size="large" 
          :style="{ 
            background: 'white', 
            color: '#ff6b35',
            border: 'none',
            fontWeight: 'bold',
          }"
        >
          了解VIP特权
        </a-button>
      </router-link>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { h, ref } from 'vue'
import { 
  Row as ARow,
  Col as ACol,
  Card as ACard,
  Button as AButton,
  Typography,
  Space as ASpace,
} from 'ant-design-vue'
import { 
  PictureOutlined, 
  MessageOutlined, 
  CrownOutlined,
  RightOutlined,
  PlayCircleOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'

// 模拟最新内容数据
const latestContent = ref([
  {
    id: 1,
    type: 'image',
    title: '春日樱花',
    description: '在公园里拍摄的美丽樱花，春天的气息扑面而来...',
    thumbnail: 'https://via.placeholder.com/300x200?text=Spring+Cherry',
    isPaid: false,
    date: '2024-03-15',
  },
  {
    id: 2,
    type: 'video',
    title: '日落时分',
    description: '海边的黄昏，夕阳西下时的宁静时光...',
    thumbnail: 'https://via.placeholder.com/300x200?text=Sunset+Video',
    isPaid: true,
    price: 5,
    date: '2024-03-12',
  },
  {
    id: 3,
    type: 'image',
    title: '城市夜景',
    description: '繁华都市的夜晚，霓虹灯下的城市魅力...',
    thumbnail: 'https://via.placeholder.com/300x200?text=City+Night',
    isPaid: false,
    date: '2024-03-10',
  },
])

const stats = ref([
  { label: '总照片数', value: '1,234', icon: PictureOutlined },
  { label: '总视频数', value: '89', icon: PlayCircleOutlined },
  { label: '注册用户', value: '567', icon: UserOutlined },
  { label: '在线聊天', value: '活跃', icon: MessageOutlined },
])
</script>

<style scoped>
.page-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-hover {
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.btn-primary {
  background: linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ff8e53 0%, #ff6b35 100%);
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
}
</style>
