<template>
  <footer class="site-footer">
    <div class="footer-container">
      <div class="footer-grid">
        <!-- 网站信息 -->
        <div class="footer-section">
          <router-link to="/" class="footer-brand">
            <span class="brand-text text-neon-blue">LUMINOUS</span>
          </router-link>
          <p class="footer-desc">
            用镜头捕捉光影，用照片讲述故事，每一幅作品都是时光的印记。
          </p>
          <div class="social-links">
            <n-button 
              circle 
              quaternary
              class="social-btn"
              tag="a"
              href="#"
              target="_blank"
            >
              <template #icon>
                <n-icon :component="LogoInstagram" />
              </template>
            </n-button>
            <n-button 
              circle 
              quaternary
              class="social-btn"
              tag="a"
              href="#"
              target="_blank"
            >
              <template #icon>
                <n-icon :component="LogoTwitter" />
              </template>
            </n-button>
            <n-button 
              circle 
              quaternary
              class="social-btn"
              tag="a"
              href="#"
              target="_blank"
            >
              <template #icon>
                <n-icon :component="LogoWechat" />
              </template>
            </n-button>
            <n-button 
              circle 
              quaternary
              class="social-btn"
              tag="a"
              href="#"
              target="_blank"
            >
              <template #icon>
                <n-icon :component="LogoGithub" />
              </template>
            </n-button>
          </div>
        </div>

        <!-- 快速链接 -->
        <div class="footer-section">
          <h4 class="footer-title">快速链接</h4>
          <ul class="footer-links">
            <li>
              <router-link to="/" class="footer-link">首页</router-link>
            </li>
            <li>
              <router-link to="/gallery" class="footer-link">作品展示</router-link>
            </li>
            <li>
              <router-link to="/profile" class="footer-link">关于我</router-link>
            </li>
            <li>
              <router-link to="/recharge" class="footer-link">购买作品</router-link>
            </li>
            <li>
              <router-link to="/chat" class="footer-link">联系我</router-link>
            </li>
          </ul>
        </div>

        <!-- 作品分类 -->
        <div class="footer-section">
          <h4 class="footer-title">作品分类</h4>
          <ul class="footer-links">
            <li>
              <a href="#" class="footer-link">城市夜景</a>
            </li>
            <li>
              <a href="#" class="footer-link">人文肖像</a>
            </li>
            <li>
              <a href="#" class="footer-link">自然风光</a>
            </li>
            <li>
              <a href="#" class="footer-link">街头瞬间</a>
            </li>
            <li>
              <a href="#" class="footer-link">星空摄影</a>
            </li>
          </ul>
        </div>

        <!-- 订阅更新 -->
        <div class="footer-section">
          <h4 class="footer-title">订阅更新</h4>
          <p class="footer-desc">
            订阅 Newsletter，获取最新作品和活动信息
          </p>
          <n-form class="subscribe-form">
            <div class="subscribe-input-group">
              <n-input 
                v-model:value="subscribeEmail" 
                placeholder="您的邮箱地址"
                class="subscribe-input"
              />
              <n-button 
                type="primary"
                @click="handleSubscribe"
                class="subscribe-btn"
              >
                订阅
              </n-button>
            </div>
          </n-form>
        </div>
      </div>

      <!-- 版权信息 -->
      <div class="footer-bottom">
        <p class="copyright">
          © {{ currentYear }} LUMINOUS 摄影工作室. 保留所有权利.
        </p>
        <div class="footer-bottom-links">
          <a href="#" class="bottom-link">隐私政策</a>
          <a href="#" class="bottom-link">使用条款</a>
          <a href="#" class="bottom-link">退款政策</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { NButton, NIcon, NInput, NForm, useMessage } from 'naive-ui'
import { 
  LogoInstagram, 
  LogoTwitter, 
  LogoWechat,
  LogoGithub,
} from '@vicons/ionicons5'

const message = useMessage()

// 订阅表单
const subscribeEmail = ref('')

// 获取当前年份
const currentYear = computed(() => new Date().getFullYear())

// 订阅功能
const handleSubscribe = () => {
  if (!subscribeEmail.value.trim()) {
    message.error('请输入您的邮箱地址')
    return
  }
  
  // 在实际应用中，这里会发送订阅请求
  message.success('订阅成功！您将收到最新作品和活动信息')
  subscribeEmail.value = ''
}
</script>

<style scoped>
.site-footer {
  background: var(--color-dark-900);
  border-top: 1px solid var(--color-dark-600);
  padding: 60px 0 24px;
  margin-top: auto;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 48px;
  margin-bottom: 48px;
}

.footer-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.footer-brand {
  text-decoration: none;
  display: inline-block;
  margin-bottom: 8px;
}

.brand-text {
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 900;
  letter-spacing: 1px;
}

.footer-desc {
  color: var(--color-text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.social-links {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.social-btn {
  width: 40px;
  height: 40px;
  color: var(--color-text-secondary);
  transition: all 0.3s ease;
}

.social-btn:hover {
  color: var(--color-neon-pink);
  transform: translateY(-2px);
}

.footer-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 12px 0;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-link {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
  display: inline-block;
}

.footer-link:hover {
  color: var(--color-neon-blue);
  padding-left: 8px;
}

.subscribe-form {
  margin-top: 8px;
}

.subscribe-input-group {
  display: flex;
  gap: 8px;
}

.subscribe-input {
  flex: 1;
}

.subscribe-btn {
  flex-shrink: 0;
}

.footer-bottom {
  border-top: 1px solid var(--color-dark-600);
  padding-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.copyright {
  color: var(--color-text-tertiary);
  font-size: 13px;
  margin: 0;
}

.footer-bottom-links {
  display: flex;
  gap: 24px;
}

.bottom-link {
  color: var(--color-text-tertiary);
  text-decoration: none;
  font-size: 13px;
  transition: color 0.3s ease;
}

.bottom-link:hover {
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .site-footer {
    padding: 40px 0 20px;
  }
  
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 32px;
    margin-bottom: 32px;
  }
  
  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
  
  .subscribe-input-group {
    flex-direction: column;
  }
  
  .subscribe-btn {
    width: 100%;
  }
}
</style>
