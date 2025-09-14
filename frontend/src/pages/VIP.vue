<template>
  <div class="vip-container">
    <div class="vip-header">
      <a-typography-title :level="1" class="vip-title">
        <CrownOutlined />
        VIP会员特权
      </a-typography-title>
      <a-typography-paragraph class="vip-description">
        成为VIP会员，享受专属特权，解锁全部精彩内容
      </a-typography-paragraph>
    </div>

    <a-row :gutter="[24, 24]">
      <a-col 
        v-for="plan in vipPlans" 
        :key="plan.id"
        :xs="24" 
        :md="8"
      >
        <a-card 
          :class="['vip-card', { 'popular': plan.popular }]"
          :bordered="false"
        >
          <template #title>
            <div class="plan-header">
              <div class="plan-name">{{ plan.name }}</div>
              <div v-if="plan.popular" class="popular-badge">推荐</div>
            </div>
          </template>
          
          <div class="plan-price">
            <span class="price">¥{{ plan.price }}</span>
            <span v-if="plan.originalPrice" class="original-price">
              ¥{{ plan.originalPrice }}
            </span>
            <div class="price-unit">/ {{ plan.duration }}天</div>
          </div>

          <a-divider />

          <div class="plan-features">
            <div 
              v-for="feature in plan.features" 
              :key="feature"
              class="feature-item"
            >
              <CheckOutlined class="feature-icon" />
              {{ feature }}
            </div>
          </div>

          <a-button 
            type="primary"
            size="large"
            block
            :class="['plan-button', { 'popular-button': plan.popular }]"
            @click="handleSubscribe(plan)"
          >
            立即开通
          </a-button>
        </a-card>
      </a-col>
    </a-row>

    <!-- 会员特权说明 -->
    <a-card 
      title="会员特权详解" 
      :style="{ marginTop: '48px' }"
    >
      <a-row :gutter="[24, 24]">
        <a-col :xs="24" :md="12">
          <a-space direction="vertical" size="large">
            <div class="privilege-item">
              <EyeOutlined class="privilege-icon" />
              <div>
                <h4>无限制浏览</h4>
                <p>解锁所有付费内容，无限制浏览高质量照片和视频</p>
              </div>
            </div>
            <div class="privilege-item">
              <MessageOutlined class="privilege-icon" />
              <div>
                <h4>优先聊天</h4>
                <p>VIP用户消息优先显示，获得更快的回复速度</p>
              </div>
            </div>
          </a-space>
        </a-col>
        <a-col :xs="24" :md="12">
          <a-space direction="vertical" size="large">
            <div class="privilege-item">
              <GiftOutlined class="privilege-icon" />
              <div>
                <h4>专属内容</h4>
                <p>访问VIP专属内容区域，享受独家精彩内容</p>
              </div>
            </div>
            <div class="privilege-item">
              <DownloadOutlined class="privilege-icon" />
              <div>
                <h4>高清下载</h4>
                <p>支持下载高清原图，随时保存喜欢的内容</p>
              </div>
            </div>
          </a-space>
        </a-col>
      </a-row>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  Typography,
  Row as ARow,
  Col as ACol,
  Card as ACard,
  Button as AButton,
  Divider as ADivider,
  Space as ASpace,
} from 'ant-design-vue'
import {
  CrownOutlined,
  CheckOutlined,
  EyeOutlined,
  MessageOutlined,
  GiftOutlined,
  DownloadOutlined,
} from '@ant-design/icons-vue'
import type { VIPPlan } from '../types'

// VIP套餐数据
const vipPlans = ref<VIPPlan[]>([
  {
    id: '1',
    name: '体验会员',
    price: 29,
    duration: 30,
    features: [
      '解锁付费内容',
      '无限制浏览',
      '标准画质',
      '基础客服支持',
    ],
    color: '#52c41a',
  },
  {
    id: '2',
    name: '尊享会员',
    price: 88,
    originalPrice: 120,
    duration: 90,
    features: [
      '解锁所有内容',
      '高清画质',
      '优先聊天权限',
      '专属客服',
      '内容下载',
    ],
    popular: true,
    color: '#ff6b35',
  },
  {
    id: '3',
    name: '至尊会员',
    price: 268,
    originalPrice: 360,
    duration: 365,
    features: [
      '全部尊享会员权限',
      '超高清画质',
      '独家专属内容',
      '1对1专属服务',
      '优先新内容推送',
      '会员专属活动',
    ],
    color: '#722ed1',
  },
])

// 处理订阅
const handleSubscribe = (plan: VIPPlan) => {
  console.log('订阅套餐:', plan)
  // TODO: 实现支付逻辑
}
</script>

<style scoped>
.vip-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.vip-header {
  text-align: center;
  margin-bottom: 48px;
}

.vip-title {
  color: #ff6b35;
  margin-bottom: 16px;
}

.vip-description {
  font-size: 18px;
  color: #666;
  max-width: 600px;
  margin: 0 auto;
}

.vip-card {
  position: relative;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.vip-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.vip-card.popular {
  border: 2px solid #ff6b35;
  transform: scale(1.05);
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-name {
  font-size: 18px;
  font-weight: 600;
}

.popular-badge {
  background: #ff6b35;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.plan-price {
  text-align: center;
  margin: 24px 0;
}

.price {
  font-size: 36px;
  font-weight: bold;
  color: #ff6b35;
}

.original-price {
  font-size: 16px;
  color: #999;
  text-decoration: line-through;
  margin-left: 8px;
}

.price-unit {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.plan-features {
  margin: 24px 0;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.feature-icon {
  color: #52c41a;
  margin-right: 8px;
}

.plan-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.popular-button {
  background: linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%);
  border: none;
}

.privilege-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.privilege-icon {
  font-size: 24px;
  color: #ff6b35;
  margin-top: 4px;
}

.privilege-item h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.privilege-item p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}
</style>
