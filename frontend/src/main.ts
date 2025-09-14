import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import zhCN from 'ant-design-vue/locale/zh_CN'
import 'ant-design-vue/dist/reset.css'

import App from './App.vue'
import routes from './router/index'
import './styles/global.css'

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 创建Pinia store
const pinia = createPinia()

// 创建Vue应用实例
const app = createApp(App)

// 配置Ant Design Vue主题
app.provide('$antLocale', zhCN)

// 注册插件和中间件
app.use(pinia)
app.use(router)
app.use(Antd)

// 配置全局属性
app.config.globalProperties.$THEME = {
  token: {
    colorPrimary: '#ff6b35', // 橙色主题
    colorBgContainer: '#ffffff', // 白色背景
    colorText: '#333333', // 黑色文字
  },
}

// 挂载应用
app.mount('#root')
