<template>
  <div class="home-page">
    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="hero-background">
        <n-image 
          src="https://picsum.photos/id/1015/1920/1080" 
          alt="背景图" 
          class="hero-bg-image"
          object-fit="cover"
        />
        <div class="hero-overlay"></div>
      </div>
      
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="title-line">捕捉光影</span>
          <span class="title-line text-neon-pink text-shadow-neon-pink">定格瞬间</span>
        </h1>
        <p class="hero-subtitle">
          用镜头讲述故事，每一张照片都是时光的切片，情感的容器
        </p>
        <div class="hero-actions">
          <n-button 
            type="primary"
            size="large"
            @click="router.push('/gallery')"
            class="hero-btn hero-btn-primary"
          >
            <template #icon>
              <n-icon :component="ImagesOutline" />
            </template>
            浏览作品
          </n-button>
          <n-button 
            quaternary
            size="large"
            @click="router.push('/profile')"
            class="hero-btn hero-btn-secondary"
          >
            了解更多
          </n-button>
        </div>
      </div>
      
      <div class="scroll-indicator">
        <router-link to="#content" class="scroll-link">
          <n-icon :component="ChevronDown" :size="36" />
        </router-link>
      </div>
    </section>

    <!-- 主要内容 -->
    <div id="content" class="content-container">
      <!-- 数据统计 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div 
            v-for="(stat, index) in stats" 
            :key="index"
            class="stat-card"
          >
            <h3 class="stat-value text-neon-blue">{{ stat.value }}</h3>
            <p class="stat-label">{{ stat.label }}</p>
          </div>
        </div>
      </section>

      <!-- 最新作品 -->
      <section class="works-section">
        <div class="section-header">
          <h2 class="section-title">
            <span class="text-neon-blue text-shadow-neon-blue">最新作品</span>
          </h2>
          <p class="section-subtitle">
            探索最近上传的精彩内容，从城市夜景到自然风光
          </p>
        </div>
        
        <horizontal-scroll-container :show-controls="true">
          <free-work-card
            v-for="work in freeWorks"
            :key="work.id"
            :work="work"
            @click="handleWorkClick"
          />
        </horizontal-scroll-container>
      </section>

      <!-- Premium 作品 -->
      <section class="works-section">
        <div class="section-header">
          <h2 class="section-title">
            <span class="text-neon-pink text-shadow-neon-pink">Premium 精选</span>
          </h2>
          <p class="section-subtitle">
            限量版高清作品，支持商业与个人使用
          </p>
        </div>
        
        <horizontal-scroll-container :show-controls="true">
          <premium-work-card
            v-for="work in premiumWorks"
            :key="work.id"
            :work="work"
            @unlock="handleUnlock"
            @preview="handlePreview"
          />
        </horizontal-scroll-container>
      </section>

      <!-- CTA 区域 -->
      <section class="cta-section">
        <div class="cta-card">
          <div class="cta-icon">
            <n-icon :component="Star" :size="64" />
          </div>
          <h3 class="cta-title">购买作品套餐</h3>
          <p class="cta-desc">
            解锁所有付费内容，享受无限制浏览体验，获得高清下载权限
          </p>
          <n-button 
            type="error"
            size="large"
            @click="router.push('/recharge')"
            class="cta-button"
          >
            查看套餐
          </n-button>
        </div>
      </section>
    </div>

    <!-- 返回顶部 -->
    <back-to-top />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NIcon, NImage, useMessage } from 'naive-ui'
import { 
  ImagesOutline, 
  ChevronDown,
  Star,
} from '@vicons/ionicons5'
import HorizontalScrollContainer from '@/components/ui/HorizontalScrollContainer.vue'
import FreeWorkCard from '@/components/cards/FreeWorkCard.vue'
import PremiumWorkCard from '@/components/cards/PremiumWorkCard.vue'
import BackToTop from '@/components/ui/BackToTop.vue'

const router = useRouter()
const message = useMessage()

// 统计数据
const stats = ref([
  { label: '摄影经验', value: '10+年' },
  { label: '游历国家', value: '30+' },
  { label: '展览展出', value: '150+' },
  { label: '作品拍摄', value: '5000+' },
])

// 免费作品数据
const freeWorks = ref([
  {
    id: 1,
    title: '山间迷雾',
    category: '自然风光',
    year: 2023,
    description: '清晨的山谷被薄雾笼罩，宛如仙境。',
    imageUrl: 'https://picsum.photos/id/1016/800/1000',
  },
  {
    id: 2,
    title: '沉思',
    category: '人文肖像',
    year: 2023,
    description: '城市角落的沉思者，现代生活中的片刻宁静。',
    imageUrl: 'https://picsum.photos/id/1025/800/1000',
  },
  {
    id: 3,
    title: '几何之美',
    category: '城市夜景',
    year: 2023,
    description: '现代建筑的几何线条与光影交错。',
    imageUrl: 'https://picsum.photos/id/1031/800/1000',
  },
  {
    id: 4,
    title: '森林秘境',
    category: '自然风光',
    year: 2023,
    description: '阳光穿过茂密的树林，形成斑驳的光影。',
    imageUrl: 'https://picsum.photos/id/1039/800/1000',
  },
])

// 付费作品数据
const premiumWorks = ref([
  {
    id: 101,
    title: '北极光舞',
    category: '自然风光 · 限量版',
    description: '冰岛夜空下舞动的北极光。',
    imageUrl: 'https://picsum.photos/id/1019/800/1000',
    price: 199,
    salesCount: 24,
  },
  {
    id: 102,
    title: '城市脉动',
    category: '延时摄影 · 4K',
    description: '记录城市从日出到日落的光影变化。',
    imageUrl: 'https://picsum.photos/id/1042/800/1000',
    isVideo: true,
    price: 299,
    salesCount: 18,
  },
  {
    id: 103,
    title: '银河漫游',
    category: '星空摄影 · 限量版',
    description: '新西兰特卡波湖上空的璀璨银河。',
    imageUrl: 'https://picsum.photos/id/1047/800/1000',
    price: 249,
    salesCount: 31,
  },
])

// 作品点击处理
const handleWorkClick = (work: any) => {
  message.info(`查看作品: ${work.title}`)
  // 实际应用中跳转到作品详情页
}

// 解锁作品
const handleUnlock = (work: any) => {
  message.success(`正在购买: ${work.title}`)
  router.push('/recharge')
}

// 预览视频
const handlePreview = (work: any) => {
  message.info(`播放预览: ${work.title}`)
}
</script>

<style scoped>
.home-page {
  background: var(--color-dark-900);
  min-height: 100vh;
}

/* 英雄区域 */
.hero-section {
  position: relative;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero-bg-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.3;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(10, 10, 10, 0.7) 0%,
    rgba(10, 10, 10, 0.5) 50%,
    var(--color-dark-900) 100%
  );
}

.hero-content {
  position: relative;
  z-index: 10;
  text-align: center;
  max-width: 900px;
  padding: 0 24px;
}

.hero-title {
  font-family: var(--font-serif);
  font-size: clamp(2.5rem, 8vw, 5rem);
  font-weight: 900;
  line-height: 1.2;
  margin: 0 0 24px 0;
}

.title-line {
  display: block;
  color: white;
}

.hero-subtitle {
  font-size: clamp(1rem, 3vw, 1.25rem);
  color: var(--color-text-secondary);
  max-width: 700px;
  margin: 0 auto 40px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-btn {
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.hero-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(5, 217, 232, 0.4);
}

.hero-btn-secondary {
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.hero-btn-secondary:hover {
  border-color: var(--color-neon-pink);
  color: var(--color-neon-pink);
  transform: translateY(-2px);
}

.scroll-indicator {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  animation: bounce 2s infinite;
}

.scroll-link {
  color: rgba(255, 255, 255, 0.7);
  transition: color 0.3s ease;
  display: block;
}

.scroll-link:hover {
  color: var(--color-neon-blue);
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateX(-50%) translateY(0);
  }
  40% {
    transform: translateX(-50%) translateY(-20px);
  }
  60% {
    transform: translateX(-50%) translateY(-10px);
  }
}

/* 内容区域 */
.content-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

/* 统计区域 */
.stats-section {
  padding: 80px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 32px;
}

.stat-card {
  text-align: center;
  padding: 24px;
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: var(--color-neon-blue);
  transform: translateY(-4px);
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

/* 作品区域 */
.works-section {
  padding: 60px 0;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-title {
  font-family: var(--font-serif);
  font-size: clamp(1.5rem, 5vw, 3rem);
  font-weight: 700;
  margin: 0 0 16px 0;
}

.section-subtitle {
  font-size: 16px;
  color: var(--color-text-secondary);
  max-width: 600px;
  margin: 0 auto;
}

/* CTA 区域 */
.cta-section {
  padding: 80px 0;
}

.cta-card {
  background: linear-gradient(135deg, var(--color-neon-pink) 0%, var(--color-neon-purple) 100%);
  border-radius: 24px;
  padding: 64px 32px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.cta-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.2'/%3E%3C/svg%3E");
  opacity: 0.3;
}

.cta-icon {
  color: white;
  margin-bottom: 24px;
  position: relative;
}

.cta-title {
  font-family: var(--font-serif);
  font-size: 32px;
  font-weight: 700;
  color: white;
  margin: 0 0 16px 0;
  position: relative;
}

.cta-desc {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  max-width: 600px;
  margin: 0 auto 32px;
  line-height: 1.6;
  position: relative;
}

.cta-button {
  background: white;
  color: var(--color-neon-pink);
  font-weight: 700;
  font-size: 16px;
  padding: 14px 40px;
  border-radius: 50px;
  position: relative;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* 响应式 */
@media (max-width: 768px) {
  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .hero-btn {
    width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  .cta-card {
    padding: 48px 24px;
  }
  
  .content-container {
    padding: 0 16px;
  }
}
</style>
