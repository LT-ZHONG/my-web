<template>
  <a-layout-footer :style="{
    background: '#f5f5f5',
    borderTop: '1px solid #e8e8e8',
    padding: '24px 0',
    marginTop: 'auto',
  }">
    <div :style="{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px' }">
      <a-row :gutter="[24, 24]">
        <!-- 网站信息 -->
        <a-col :xs="24" :sm="12" :md="8">
          <div :style="{ marginBottom: '16px' }">
            <div :style="{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '12px',
            }">
              <div :style="{
                width: 32,
                height: 32,
                background: 'linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%)',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '8px',
                color: 'white',
                fontSize: '14px',
              }">
                📸
              </div>
              <a-typography-text 
                strong 
                :style="{ fontSize: '16px' }"
              >
                我的生活
              </a-typography-text>
            </div>
            <a-typography-text 
              type="secondary" 
              :style="{ fontSize: '14px', lineHeight: 1.6 }"
            >
              分享生活的美好瞬间，记录每一个值得珍藏的回忆。
              在这里，你可以看到我的日常生活照片和视频，
              也可以与我进行实时交流。
            </a-typography-text>
          </div>
        </a-col>

        <!-- 快速链接 -->
        <a-col :xs="24" :sm="12" :md="8">
          <div :style="{ marginBottom: '16px' }">
            <a-typography-text 
              strong 
              :style="{ marginBottom: '12px', display: 'block' }"
            >
              快速链接
            </a-typography-text>
            <a-space direction="vertical" :size="8">
              <a-typography-link 
                :href="'/'"
                :style="{ color: '#666', fontSize: '14px' }"
              >
                首页
              </a-typography-link>
              <a-typography-link 
                :href="'/gallery'"
                :style="{ color: '#666', fontSize: '14px' }"
              >
                照片视频
              </a-typography-link>
              <a-typography-link 
                :href="'/chat'"
                :style="{ color: '#666', fontSize: '14px' }"
              >
                在线聊天
              </a-typography-link>
              <a-typography-link 
                :href="'/vip'"
                :style="{ color: '#666', fontSize: '14px' }"
              >
                VIP会员
              </a-typography-link>
            </a-space>
          </div>
        </a-col>

        <!-- 联系方式 -->
        <a-col :xs="24" :sm="24" :md="8">
          <div :style="{ marginBottom: '16px' }">
            <a-typography-text 
              strong 
              :style="{ marginBottom: '12px', display: 'block' }"
            >
              联系我
            </a-typography-text>
            <a-space direction="vertical" :size="12">
              <a-space>
                <MailOutlined :style="{ color: '#ff6b35' }" />
                <a-typography-text :style="{ fontSize: '14px', color: '#666' }">
                  your-email@example.com
                </a-typography-text>
              </a-space>
              <a-space>
                <WechatOutlined :style="{ color: '#ff6b35' }" />
                <a-typography-text :style="{ fontSize: '14px', color: '#666' }">
                  微信: your-wechat-id
                </a-typography-text>
              </a-space>
              <a-space :size="16">
                <a-typography-link 
                  href="https://github.com/your-username" 
                  target="_blank"
                  :style="{ color: '#666', fontSize: '18px' }"
                >
                  <GithubOutlined />
                </a-typography-link>
                <a-typography-link 
                  href="#"
                  :style="{ color: '#666', fontSize: '18px' }"
                >
                  <WechatOutlined />
                </a-typography-link>
                <a-typography-link 
                  href="mailto:your-email@example.com"
                  :style="{ color: '#666', fontSize: '18px' }"
                >
                  <MailOutlined />
                </a-typography-link>
              </a-space>
            </a-space>
          </div>
        </a-col>
      </a-row>

      <!-- 版权信息 -->
      <div :style="{
        borderTop: '1px solid #e8e8e8',
        paddingTop: '16px',
        marginTop: '24px',
        textAlign: 'center',
      }">
        <a-typography-text 
          type="secondary" 
          :style="{ fontSize: '12px' }"
        >
          © {{ currentYear }} 我的生活网站. Made with
          <HeartFilled :style="{ color: '#ff6b35', margin: '0 4px' }" />
          by Vue3 & Node.js
        </a-typography-text>
      </div>
    </div>
  </a-layout-footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  Layout as ALayout,
  Row as ARow,
  Col as ACol,
  Space as ASpace,
  Typography,
} from 'ant-design-vue'
import { 
  GithubOutlined, 
  WechatOutlined, 
  MailOutlined,
  HeartFilled,
} from '@ant-design/icons-vue'

// 获取当前年份
const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
/* 组件特定的样式可以在这里添加 */
</style>
