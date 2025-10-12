<template>
  <div class="recharge-page">
    <!-- 页头 -->
    <section class="recharge-header">
      <h1 class="page-title text-neon-pink">积分充值</h1>
      <p class="page-subtitle">
        1美元 = 10积分，可用于查看付费照片和视频
      </p>
      
      <!-- 当前积分余额 -->
      <div class="balance-card">
        <div class="balance-icon">
          <n-icon size="48" color="var(--color-neon-blue)">
            <wallet-outline />
          </n-icon>
        </div>
        <div class="balance-content">
          <div class="balance-label">当前积分余额</div>
          <div class="balance-value">{{ userCredits }}</div>
        </div>
      </div>
    </section>

    <!-- 三档套餐 -->
    <section class="packages-section">
      <h2 class="section-title">积分套餐</h2>
      
      <div class="packages-grid">
        <!-- 套餐 1 -->
        <div class="package-card">
          <div class="package-decoration"></div>
          <h3 class="package-name">探索者</h3>
          <p class="package-price">¥99<span class="price-unit">/次</span></p>
          <ul class="package-features">
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-blue)">
                <checkmark-circle-outline />
              </n-icon>
              <span>100 积分</span>
            </li>
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-blue)">
                <checkmark-circle-outline />
              </n-icon>
              <span>适合个人使用</span>
            </li>
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-blue)">
                <checkmark-circle-outline />
              </n-icon>
              <span>永久有效</span>
            </li>
          </ul>
          <n-button class="package-btn" @click="selectPackage(10)">
            选择套餐
          </n-button>
        </div>
        
        <!-- 套餐 2 (推荐) -->
        <div class="package-card featured">
          <div class="featured-badge">最受欢迎</div>
          <div class="package-decoration pink"></div>
          <h3 class="package-name">创作者</h3>
          <p class="package-price">¥299<span class="price-unit">/次</span></p>
          <ul class="package-features">
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-pink)">
                <checkmark-circle-outline />
              </n-icon>
              <span>300 积分</span>
            </li>
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-pink)">
                <checkmark-circle-outline />
              </n-icon>
              <span>优惠10%</span>
            </li>
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-pink)">
                <checkmark-circle-outline />
              </n-icon>
              <span>适合创作者</span>
            </li>
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-pink)">
                <checkmark-circle-outline />
              </n-icon>
              <span>永久有效</span>
            </li>
          </ul>
          <n-button class="package-btn primary" @click="selectPackage(30)">
            选择套餐
          </n-button>
        </div>
        
        <!-- 套餐 3 -->
        <div class="package-card">
          <div class="package-decoration purple"></div>
          <h3 class="package-name">专业版</h3>
          <p class="package-price">¥599<span class="price-unit">/次</span></p>
          <ul class="package-features">
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-purple)">
                <checkmark-circle-outline />
              </n-icon>
              <span>600 积分</span>
            </li>
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-purple)">
                <checkmark-circle-outline />
              </n-icon>
              <span>优惠20%</span>
            </li>
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-purple)">
                <checkmark-circle-outline />
              </n-icon>
              <span>适合专业人士</span>
            </li>
            <li>
              <n-icon class="feature-icon" color="var(--color-neon-purple)">
                <checkmark-circle-outline />
              </n-icon>
              <span>永久有效</span>
            </li>
          </ul>
          <n-button class="package-btn" @click="selectPackage(60)">
            选择套餐
          </n-button>
        </div>
      </div>
    </section>
    
    <!-- 自定义充值 -->
    <section class="custom-recharge">
      <h2 class="section-title">自定义充值</h2>
      <div class="custom-card">
        <n-form :model="rechargeForm" class="custom-form">
          <n-form-item label="输入充值金额 (美元)">
            <n-input-number
              v-model:value="rechargeForm.amount"
              :min="1"
              :max="10000"
              :step="1"
              :precision="2"
              style="width: 100%"
              size="large"
              placeholder="请输入充值金额"
            >
              <template #prefix>$</template>
              <template #suffix>USD</template>
            </n-input-number>
          </n-form-item>
          
          <div v-if="rechargeForm.amount" class="credits-preview">
            将获得 <span class="credits-amount">{{ (rechargeForm.amount * 10).toFixed(0) }}</span> 积分
          </div>
          
          <!-- 快捷金额选择 -->
          <div class="quick-amounts">
            <button
              v-for="quick in quickAmounts"
              :key="quick"
              class="quick-btn"
              :class="{ active: rechargeForm.amount === quick }"
              @click="rechargeForm.amount = quick"
            >
              ${{ quick }}
            </button>
          </div>
        </n-form>
      </div>
    </section>

    <!-- 支付方式选择 -->
    <n-card 
      v-if="rechargeForm.amount && rechargeForm.amount > 0"
      title="选择支付方式"
    >
      <n-grid :cols="1" :md="2" :x-gap="24" :y-gap="24">
        <n-grid-item>
          <div 
            :class="['payment-method', { 'selected': paymentMethod === 'paypal' }]"
            @click="selectPaymentMethod('paypal')"
          >
            <div class="method-header">
              <n-icon size="32" color="#1890ff"><card-outline /></n-icon>
              <h3>PayPal</h3>
            </div>
            <p>使用PayPal安全快捷支付</p>
          </div>
        </n-grid-item>
        <n-grid-item>
          <div 
            :class="['payment-method', { 'selected': paymentMethod === 'usdt' }]"
            @click="selectPaymentMethod('usdt')"
          >
            <div class="method-header">
              <n-icon size="32" color="#1890ff"><wallet-outline /></n-icon>
              <h3>USDT (加密货币)</h3>
            </div>
            <p>使用USDT稳定币支付</p>
          </div>
        </n-grid-item>
      </n-grid>

      <!-- PayPal 支付 -->
      <div v-if="paymentMethod === 'paypal'" class="payment-details">
        <n-divider />
        <n-alert
          title="重要提示"
          type="warning"
          :style="{ marginBottom: '24px' }"
        >
          付款时请务必在备注中注明您的注册邮箱，以便我们及时为您充值。
        </n-alert>
        <div class="payment-info">
          <h4>付款金额: ${{ rechargeForm.amount }} USD ({{ (rechargeForm.amount * 10).toFixed(0) }} 积分)</h4>
          <n-button 
            type="primary" 
            size="large"
            :loading="loading"
            @click="handleRecharge"
          >
            <template #icon>
              <n-icon><card-outline /></n-icon>
            </template>
            创建充值订单
          </n-button>
          <p class="payment-tip">点击后将为您生成支付信息</p>
        </div>
      </div>

      <!-- USDT 支付 -->
      <div v-if="paymentMethod === 'usdt'" class="payment-details">
        <n-divider />
        <n-alert
          title="重要提示"
          type="warning"
          :style="{ marginBottom: '24px' }"
        >
          付款时请务必在备注中注明您的注册邮箱，以便我们及时为您充值。建议使用Binance APP等加密货币钱包扫码或输入地址支付。
        </n-alert>
        <div class="payment-info">
          <h4>付款金额: ${{ rechargeForm.amount }} USDT ({{ (rechargeForm.amount * 10).toFixed(0) }} 积分)</h4>
          <n-button 
            type="primary" 
            size="large"
            :loading="loading"
            @click="handleRecharge"
          >
            <template #icon>
              <n-icon><wallet-outline /></n-icon>
            </template>
            创建充值订单
          </n-button>
          <p class="payment-tip">点击后将为您生成支付地址和二维码</p>
        </div>
      </div>
    </n-card>

    <!-- 支付信息模态框 -->
    <n-modal
      v-model:show="showPaymentModal"
      preset="card"
      title="支付信息"
      :style="{ width: '600px', maxWidth: '90vw' }"
    >
      <div v-if="paymentInfo" class="modal-payment-info">
        <!-- PayPal支付信息 -->
        <div v-if="paymentInfo.payment_method === 'paypal'">
          <n-result
            status="info"
            title="请完成PayPal支付"
            :description="`订单号: ${paymentInfo.order_no}`"
          >
            <template #footer>
              <n-button 
                type="primary" 
                size="large"
                tag="a"
                :href="paymentInfo.payment_info.payment_url"
                target="_blank"
              >
                <template #icon>
                  <n-icon><card-outline /></n-icon>
                </template>
                前往 PayPal 支付
              </n-button>
            </template>
          </n-result>
          <n-descriptions bordered :column="1" style="margin-top: 24px">
            <n-descriptions-item label="充值金额">${{ paymentInfo.amount }} USD</n-descriptions-item>
            <n-descriptions-item label="获得积分">{{ paymentInfo.credits }} 积分</n-descriptions-item>
            <n-descriptions-item label="备注">{{ paymentInfo.payment_info.note }}</n-descriptions-item>
          </n-descriptions>
        </div>

        <!-- USDT支付信息 -->
        <div v-if="paymentInfo.payment_method === 'usdt'">
          <n-result
            status="info"
            title="请完成USDT支付"
            :description="`订单号: ${paymentInfo.order_no}`"
          />
          <div class="usdt-payment-modal">
            <div class="qr-code-modal">
              <img :src="`/${paymentInfo.payment_info.qr_code}`" alt="USDT Payment QR Code" />
              <p>扫码支付</p>
            </div>
            <n-descriptions bordered :column="1" style="margin-top: 24px">
              <n-descriptions-item label="充值金额">${{ paymentInfo.amount }} USDT</n-descriptions-item>
              <n-descriptions-item label="获得积分">{{ paymentInfo.credits }} 积分</n-descriptions-item>
              <n-descriptions-item label="收款地址">
                <n-input 
                  :value="paymentInfo.payment_info.address" 
                  readonly
                >
                  <template #suffix>
                    <n-button 
                      text
                      @click="copyText(paymentInfo.payment_info.address)"
                    >
                      <template #icon>
                        <n-icon><copy-outline /></n-icon>
                      </template>
                      复制
                    </n-button>
                  </template>
                </n-input>
              </n-descriptions-item>
              <n-descriptions-item label="网络">{{ paymentInfo.payment_info.network }}</n-descriptions-item>
              <n-descriptions-item label="备注">{{ paymentInfo.payment_info.note }}</n-descriptions-item>
            </n-descriptions>
          </div>
        </div>

        <n-alert
          title="支付完成后"
          type="success"
          style="margin-top: 24px"
        >
          请耐心等待，管理员会在确认收款后为您充值积分。通常在5-30分钟内完成。
        </n-alert>
      </div>
    </n-modal>

    <!-- 充值说明 -->
    <n-card 
      title="充值说明" 
      :style="{ marginTop: '48px' }"
    >
      <n-space vertical size="large" style="width: 100%">
        <div class="info-item">
          <n-icon size="28" color="#1890ff"><checkmark-circle-outline /></n-icon>
          <div>
            <h4>到账时间</h4>
            <p>PayPal支付通常1-5分钟内到账，USDT支付需要等待区块链确认，通常10-30分钟</p>
          </div>
        </div>
        <div class="info-item">
          <n-icon size="28" color="#1890ff"><shield-checkmark-outline /></n-icon>
          <div>
            <h4>安全保障</h4>
            <p>我们使用安全的支付渠道，您的资金和个人信息将得到充分保护</p>
          </div>
        </div>
        <div class="info-item">
          <n-icon size="28" color="#1890ff"><headset-outline /></n-icon>
          <div>
            <h4>客服支持</h4>
            <p>如遇到充值问题，请联系在线客服，我们将第一时间为您处理</p>
          </div>
        </div>
      </n-space>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '@/stores'
import { apiClient } from '../utils/api'
import type { CreditRechargeRequest, CreditRechargeResponse } from '@/types'
import {
  NButton,
  NSpace,
  NAlert,
  NInput,
  NInputNumber,
  NForm,
  NFormItem,
  NModal,
  NResult,
  NDescriptions,
  NDescriptionsItem,
  NIcon,
} from 'naive-ui'
import {
  CardOutline,
  WalletOutline,
  CopyOutline,
  CheckmarkCircleOutline,
  ShieldCheckmarkOutline,
  HeadsetOutline,
} from '@vicons/ionicons5'

const authStore = useAuthStore()
const message = useMessage()

// 充值表单
const rechargeForm = ref({
  amount: 10
})

// 快捷金额选项
const quickAmounts = ref([10, 20, 50, 100, 200, 500])

// 用户积分余额
const userCredits = computed(() => authStore.user?.credits || 0)

// 支付方式
const paymentMethod = ref<'paypal' | 'usdt' | null>(null)

// 加载状态
const loading = ref(false)

// 支付信息模态框
const showPaymentModal = ref(false)
const paymentInfo = ref<CreditRechargeResponse | null>(null)

// 选择套餐
const selectPackage = (amount: number) => {
  rechargeForm.value.amount = amount
  message.success(`已选择 ${amount} 美元套餐`)
}

// 选择支付方式
const selectPaymentMethod = (method: 'paypal' | 'usdt') => {
  paymentMethod.value = method
  message.info(`已选择 ${method === 'paypal' ? 'PayPal' : 'USDT'} 支付`)
}

// 处理充值
const handleRecharge = async () => {
  if (!rechargeForm.value.amount || rechargeForm.value.amount <= 0) {
    message.error('请输入有效的充值金额')
    return
  }

  if (!paymentMethod.value) {
    message.error('请选择支付方式')
    return
  }

  loading.value = true
  try {
    const requestData: CreditRechargeRequest = {
      amount: rechargeForm.value.amount,
      payment_method: paymentMethod.value
    }

    const response = await apiClient.post<CreditRechargeResponse>(
      '/payment/credits/recharge',
      requestData
    )

    paymentInfo.value = response
    showPaymentModal.value = true
    message.success(response.message)
  } catch (error: any) {
    console.error('充值失败:', error)
    message.error(error.response?.data?.detail || '创建充值订单失败')
  } finally {
    loading.value = false
  }
}

// 复制文本
const copyText = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    message.success('已复制到剪贴板')
  } catch (err) {
    message.error('复制失败，请手动复制')
  }
}

// 初始化时刷新用户信息
onMounted(async () => {
  if (authStore.isAuthenticated) {
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
})
</script>

<style scoped>
.recharge-page {
  min-height: 100vh;
  background: var(--color-dark-900);
  padding: 80px 24px 48px;
}

/* 页头 */
.recharge-header {
  text-align: center;
  margin-bottom: 64px;
}

.page-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: bold;
  margin: 0 0 16px;
  text-shadow: 
    0 0 20px rgba(255, 42, 109, 0.5),
    0 0 40px rgba(255, 42, 109, 0.3);
}

.text-neon-pink {
  color: var(--color-neon-pink);
}

.page-subtitle {
  font-size: 1.125rem;
  color: var(--color-text-secondary);
  margin: 0 0 32px;
}

/* 余额卡片 */
.balance-card {
  max-width: 400px;
  margin: 0 auto;
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 16px;
  padding: 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  transition: all 0.3s ease;
}

.balance-card:hover {
  border-color: var(--color-neon-blue);
  box-shadow: 0 8px 32px rgba(5, 217, 232, 0.2);
}

.balance-icon {
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  background: rgba(5, 217, 232, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.balance-content {
  flex: 1;
}

.balance-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.balance-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-neon-blue);
  text-shadow: 0 0 20px rgba(5, 217, 232, 0.3);
}

/* 套餐区域 */
.packages-section {
  max-width: 1200px;
  margin: 0 auto 64px;
}

.section-title {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  text-align: center;
  margin-bottom: 48px;
  color: var(--color-text-primary);
}

.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
}

.package-card {
  background: var(--color-dark-700);
  border: 1px solid var(--color-dark-600);
  border-radius: 16px;
  padding: 40px 32px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.package-card:hover {
  transform: translateY(-8px);
  border-color: var(--color-neon-blue);
  box-shadow: 0 12px 40px rgba(5, 217, 232, 0.2);
}

.package-card.featured {
  border-color: var(--color-neon-pink);
  transform: scale(1.05);
  z-index: 10;
  box-shadow: 0 12px 40px rgba(255, 42, 109, 0.2);
}

.package-card.featured:hover {
  transform: scale(1.05) translateY(-8px);
  border-color: var(--color-neon-pink);
  box-shadow: 0 16px 48px rgba(255, 42, 109, 0.3);
}

.package-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 120px;
  height: 120px;
  background: rgba(5, 217, 232, 0.1);
  border-radius: 50%;
  transform: translate(40px, -40px);
  transition: all 0.3s ease;
}

.package-decoration.pink {
  background: rgba(255, 42, 109, 0.1);
}

.package-decoration.purple {
  background: rgba(211, 0, 197, 0.1);
}

.package-card:hover .package-decoration {
  background: rgba(5, 217, 232, 0.2);
}

.package-card.featured .package-decoration {
  background: rgba(255, 42, 109, 0.15);
}

.featured-badge {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background: var(--color-neon-pink);
  color: var(--color-dark-900);
  text-align: center;
  padding: 8px;
  font-size: 0.875rem;
  font-weight: 700;
}

.package-name {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 16px;
  position: relative;
  z-index: 1;
}

.package-card.featured .package-name {
  margin-top: 24px;
}

.package-price {
  font-size: 3rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 32px;
  position: relative;
  z-index: 1;
}

.price-unit {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  font-weight: 400;
}

.package-features {
  list-style: none;
  padding: 0;
  margin: 0 0 32px;
}

.package-features li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
  color: var(--color-text-secondary);
}

.feature-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.package-btn {
  width: 100%;
  padding: 14px 32px;
  border-radius: 50px;
  font-weight: 600;
  background: transparent;
  border: 1px solid var(--color-neon-blue);
  color: var(--color-neon-blue);
  transition: all 0.3s ease;
}

.package-btn:hover {
  background: var(--color-neon-blue);
  color: var(--color-dark-900);
  box-shadow: 0 8px 24px rgba(5, 217, 232, 0.4);
}

.package-btn.primary {
  background: var(--color-neon-pink);
  border-color: var(--color-neon-pink);
  color: white;
}

.package-btn.primary:hover {
  background: transparent;
  color: var(--color-neon-pink);
}

/* 自定义充值 */
.custom-recharge {
  max-width: 800px;
  margin: 0 auto 64px;
}

.custom-card {
  background: var(--color-dark-800);
  border: 1px solid var(--color-dark-600);
  border-radius: 16px;
  padding: 32px;
}

.custom-form :deep(.n-form-item-label) {
  color: var(--color-text-primary);
}

.custom-form :deep(.n-input-number) {
  background: var(--color-dark-700);
  border-color: var(--color-dark-600);
}

.custom-form :deep(.n-input-number__input) {
  color: var(--color-text-primary);
}

.custom-form :deep(.n-input-number:hover) {
  border-color: var(--color-neon-pink);
}

.custom-form :deep(.n-input-number.n-input-number--focus) {
  border-color: var(--color-neon-pink);
  box-shadow: 0 0 0 2px rgba(255, 42, 109, 0.2);
}

.credits-preview {
  margin-top: 16px;
  font-size: 1.125rem;
  color: var(--color-neon-blue);
  font-weight: 500;
  text-align: center;
}

.credits-amount {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-neon-pink);
  text-shadow: 0 0 20px rgba(255, 42, 109, 0.3);
}

.quick-amounts {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.quick-btn {
  padding: 12px 24px;
  border-radius: 50px;
  background: var(--color-dark-700);
  border: 1px solid var(--color-dark-600);
  color: var(--color-text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-btn:hover {
  border-color: var(--color-neon-blue);
  color: var(--color-neon-blue);
}

.quick-btn.active {
  background: var(--color-neon-blue);
  border-color: var(--color-neon-blue);
  color: var(--color-dark-900);
  box-shadow: 0 4px 16px rgba(5, 217, 232, 0.3);
}

/* 支付方式 */
.payment-method {
  padding: 24px;
  border: 2px solid var(--color-dark-600);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--color-dark-700);
}

.payment-method:hover {
  border-color: var(--color-neon-blue);
  box-shadow: 0 4px 16px rgba(5, 217, 232, 0.2);
}

.payment-method.selected {
  border-color: var(--color-neon-pink);
  background: rgba(255, 42, 109, 0.1);
  box-shadow: 0 4px 16px rgba(255, 42, 109, 0.2);
}

.method-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.payment-method h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.payment-method p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

/* 支付详情 */
.payment-details {
  margin-top: 24px;
}

.payment-info {
  text-align: center;
}

.payment-info h4 {
  font-size: 20px;
  margin-bottom: 24px;
  color: var(--color-text-primary);
}

.payment-tip {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin: 16px 0 0 0;
}

/* USDT 支付 */
.modal-payment-info {
  padding: 12px 0;
}

.qr-code-modal {
  text-align: center;
  margin-bottom: 24px;
}

.qr-code-modal img {
  width: 200px;
  height: 200px;
  border: 2px solid var(--color-dark-600);
  border-radius: 8px;
  padding: 8px;
  background: white;
}

.qr-code-modal p {
  margin-top: 12px;
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* 充值说明 */
.info-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.info-item h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: var(--color-text-primary);
  font-weight: 600;
}

.info-item p {
  margin: 0;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* 响应式 */
@media (max-width: 768px) {
  .recharge-page {
    padding: 64px 16px 32px;
  }

  .recharge-header {
    margin-bottom: 48px;
  }
  
  .balance-card {
    flex-direction: column;
    text-align: center;
  }
  
  .packages-grid {
    grid-template-columns: 1fr;
  }
  
  .package-card.featured {
    transform: none;
  }
  
  .package-card.featured:hover {
    transform: translateY(-8px);
  }
}
</style>
