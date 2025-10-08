<template>
  <div class="recharge-container">
    <div class="recharge-header">
      <a-typography-title :level="1" class="recharge-title">
        <DollarOutlined />
        积分充值
      </a-typography-title>
      <a-typography-paragraph class="recharge-description">
        1美元 = 10积分，可用于查看付费照片和视频。支持PayPal和USDT两种支付方式
      </a-typography-paragraph>
      <div class="current-balance">
        <a-statistic
          title="当前积分余额"
          :value="userCredits"
          suffix="积分"
          :value-style="{ color: '#1890ff', fontSize: '32px', fontWeight: 'bold' }"
        >
          <template #prefix>
            <WalletOutlined />
          </template>
        </a-statistic>
      </div>
    </div>

    <!-- 自定义充值金额 -->
    <a-card title="充值金额" :style="{ marginBottom: '24px' }">
      <a-form :model="rechargeForm" layout="vertical">
        <a-form-item label="输入充值金额 (美元)">
          <a-input-number
            v-model:value="rechargeForm.amount"
            :min="1"
            :max="10000"
            :step="1"
            :precision="2"
            style="width: 100%"
            size="large"
            placeholder="请输入充值金额"
          >
            <template #addonBefore>$</template>
            <template #addonAfter>USD</template>
          </a-input-number>
          <div v-if="rechargeForm.amount" class="credits-preview">
            将获得 <span class="credits-amount">{{ (rechargeForm.amount * 10).toFixed(0) }}</span> 积分
          </div>
        </a-form-item>

        <!-- 快捷金额选择 -->
        <a-form-item label="快捷选择">
          <a-space :size="12" wrap>
            <a-button
              v-for="quick in quickAmounts"
              :key="quick"
              :type="rechargeForm.amount === quick ? 'primary' : 'default'"
              @click="rechargeForm.amount = quick"
            >
              ${{ quick }}
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 支付方式选择 -->
    <a-card 
      v-if="rechargeForm.amount && rechargeForm.amount > 0"
      title="选择支付方式"
    >
      <a-row :gutter="[24, 24]">
        <a-col :xs="24" :md="12">
          <div 
            :class="['payment-method', { 'selected': paymentMethod === 'paypal' }]"
            @click="selectPaymentMethod('paypal')"
          >
            <div class="method-header">
              <PayCircleOutlined class="method-icon" />
              <h3>PayPal</h3>
            </div>
            <p>使用PayPal安全快捷支付</p>
          </div>
        </a-col>
        <a-col :xs="24" :md="12">
          <div 
            :class="['payment-method', { 'selected': paymentMethod === 'usdt' }]"
            @click="selectPaymentMethod('usdt')"
          >
            <div class="method-header">
              <WalletOutlined class="method-icon" />
              <h3>USDT (加密货币)</h3>
            </div>
            <p>使用USDT稳定币支付</p>
          </div>
        </a-col>
      </a-row>

      <!-- PayPal 支付 -->
      <div v-if="paymentMethod === 'paypal'" class="payment-details">
        <a-divider />
        <a-alert
          message="重要提示"
          description="付款时请务必在备注中注明您的注册邮箱，以便我们及时为您充值。"
          type="warning"
          show-icon
          :style="{ marginBottom: '24px' }"
        />
        <div class="payment-info">
          <h4>付款金额: ${{ rechargeForm.amount }} USD ({{ (rechargeForm.amount * 10).toFixed(0) }} 积分)</h4>
          <a-button 
            type="primary" 
            size="large"
            :loading="loading"
            @click="handleRecharge"
          >
            <PayCircleOutlined />
            创建充值订单
          </a-button>
          <p class="payment-tip">点击后将为您生成支付信息</p>
        </div>
      </div>

      <!-- USDT 支付 -->
      <div v-if="paymentMethod === 'usdt'" class="payment-details">
        <a-divider />
        <a-alert
          message="重要提示"
          description="付款时请务必在备注中注明您的注册邮箱，以便我们及时为您充值。建议使用Binance APP等加密货币钱包扫码或输入地址支付。"
          type="warning"
          show-icon
          :style="{ marginBottom: '24px' }"
        />
        <div class="payment-info">
          <h4>付款金额: ${{ rechargeForm.amount }} USDT ({{ (rechargeForm.amount * 10).toFixed(0) }} 积分)</h4>
          <a-button 
            type="primary" 
            size="large"
            :loading="loading"
            @click="handleRecharge"
          >
            <WalletOutlined />
            创建充值订单
          </a-button>
          <p class="payment-tip">点击后将为您生成支付地址和二维码</p>
        </div>
      </div>
    </a-card>

    <!-- 支付信息模态框 -->
    <a-modal
      v-model:visible="showPaymentModal"
      title="支付信息"
      :footer="null"
      width="600px"
    >
      <div v-if="paymentInfo" class="modal-payment-info">
        <!-- PayPal支付信息 -->
        <div v-if="paymentInfo.payment_method === 'paypal'">
          <a-result
            status="info"
            title="请完成PayPal支付"
            :sub-title="`订单号: ${paymentInfo.order_no}`"
          >
            <template #extra>
              <a-button 
                type="primary" 
                size="large"
                :href="paymentInfo.payment_info.payment_url"
                target="_blank"
              >
                <PayCircleOutlined />
                前往 PayPal 支付
              </a-button>
            </template>
          </a-result>
          <a-descriptions bordered :column="1" style="margin-top: 24px">
            <a-descriptions-item label="充值金额">${{ paymentInfo.amount }} USD</a-descriptions-item>
            <a-descriptions-item label="获得积分">{{ paymentInfo.credits }} 积分</a-descriptions-item>
            <a-descriptions-item label="备注">{{ paymentInfo.payment_info.note }}</a-descriptions-item>
          </a-descriptions>
        </div>

        <!-- USDT支付信息 -->
        <div v-if="paymentInfo.payment_method === 'usdt'">
          <a-result
            status="info"
            title="请完成USDT支付"
            :sub-title="`订单号: ${paymentInfo.order_no}`"
          />
          <div class="usdt-payment-modal">
            <div class="qr-code-modal">
              <img :src="`/${paymentInfo.payment_info.qr_code}`" alt="USDT Payment QR Code" />
              <p>扫码支付</p>
            </div>
            <a-descriptions bordered :column="1" style="margin-top: 24px">
              <a-descriptions-item label="充值金额">${{ paymentInfo.amount }} USDT</a-descriptions-item>
              <a-descriptions-item label="获得积分">{{ paymentInfo.credits }} 积分</a-descriptions-item>
              <a-descriptions-item label="收款地址">
                <a-input 
                  :value="paymentInfo.payment_info.address" 
                  readonly
                >
                  <template #suffix>
                    <a-button 
                      type="link" 
                      size="small"
                      @click="copyText(paymentInfo.payment_info.address)"
                    >
                      <CopyOutlined />
                      复制
                    </a-button>
                  </template>
                </a-input>
              </a-descriptions-item>
              <a-descriptions-item label="网络">{{ paymentInfo.payment_info.network }}</a-descriptions-item>
              <a-descriptions-item label="备注">{{ paymentInfo.payment_info.note }}</a-descriptions-item>
            </a-descriptions>
          </div>
        </div>

        <a-alert
          message="支付完成后"
          description="请耐心等待，管理员会在确认收款后为您充值积分。通常在5-30分钟内完成。"
          type="success"
          show-icon
          style="margin-top: 24px"
        />
      </div>
    </a-modal>

    <!-- 充值说明 -->
    <a-card 
      title="充值说明" 
      :style="{ marginTop: '48px' }"
    >
      <a-space direction="vertical" size="large" style="width: 100%">
        <div class="info-item">
          <CheckCircleOutlined class="info-icon" />
          <div>
            <h4>到账时间</h4>
            <p>PayPal支付通常1-5分钟内到账，USDT支付需要等待区块链确认，通常10-30分钟</p>
          </div>
        </div>
        <div class="info-item">
          <SafetyOutlined class="info-icon" />
          <div>
            <h4>安全保障</h4>
            <p>我们使用安全的支付渠道，您的资金和个人信息将得到充分保护</p>
          </div>
        </div>
        <div class="info-item">
          <CustomerServiceOutlined class="info-icon" />
          <div>
            <h4>客服支持</h4>
            <p>如遇到充值问题，请联系在线客服，我们将第一时间为您处理</p>
          </div>
        </div>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores'
import { apiClient } from '../utils/api'
import type { CreditRechargeRequest, CreditRechargeResponse } from '@/types'
import {
  Row as ARow,
  Col as ACol,
  Card as ACard,
  Button as AButton,
  Divider as ADivider,
  Space as ASpace,
  Alert as AAlert,
  Input as AInput,
  InputNumber as AInputNumber,
  Form as AForm,
  FormItem as AFormItem,
  Modal as AModal,
  Result as AResult,
  Descriptions as ADescriptions,
  DescriptionsItem as ADescriptionsItem,
  Statistic as AStatistic,
} from 'ant-design-vue'
import {
  DollarOutlined,
  PayCircleOutlined,
  WalletOutlined,
  CopyOutlined,
  CheckCircleOutlined,
  SafetyOutlined,
  CustomerServiceOutlined,
} from '@ant-design/icons-vue'

const authStore = useAuthStore()

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
.recharge-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.recharge-header {
  text-align: center;
  margin-bottom: 48px;
}

.recharge-title {
  color: #1890ff;
  margin-bottom: 16px;
}

.recharge-description {
  font-size: 18px;
  color: #666;
  max-width: 700px;
  margin: 0 auto 24px;
}

.current-balance {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.credits-preview {
  margin-top: 12px;
  font-size: 16px;
  color: #52c41a;
  font-weight: 500;
}

.credits-amount {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}


/* 支付方式 */
.payment-method {
  padding: 24px;
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.payment-method:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.2);
}

.payment-method.selected {
  border-color: #1890ff;
  background: #e6f7ff;
}

.method-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.method-icon {
  font-size: 32px;
  color: #1890ff;
}

.payment-method h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.payment-method p {
  margin: 0;
  color: #666;
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
  color: #333;
}

.payment-info .ant-btn {
  margin-bottom: 16px;
}

.payment-tip {
  color: #999;
  font-size: 14px;
  margin: 0;
}

/* USDT 支付 */
.usdt-payment {
  display: flex;
  gap: 48px;
  align-items: flex-start;
  justify-content: center;
  margin-top: 24px;
  flex-wrap: wrap;
}

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
  border: 2px solid #e8e8e8;
  border-radius: 8px;
  padding: 8px;
  background: white;
}

.qr-code-modal p {
  margin-top: 12px;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* 充值说明 */
.info-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.info-icon {
  font-size: 28px;
  color: #1890ff;
  margin-top: 4px;
}

.info-item h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.info-item p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

/* 响应式 */
@media (max-width: 768px) {
  .recharge-container {
    padding: 16px;
  }

  .recharge-header {
    margin-bottom: 32px;
  }

  .price {
    font-size: 36px;
  }

  .usdt-payment {
    flex-direction: column;
    align-items: center;
  }

  .address-info {
    width: 100%;
  }
}
</style>
