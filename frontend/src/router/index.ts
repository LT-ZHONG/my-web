import type { RouteRecordRaw } from 'vue-router'
import Home from '../pages/Home.vue'
import Gallery from '../pages/Gallery.vue'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Profile from '../pages/Profile.vue'
import Chat from '../pages/Chat.vue'
import VIP from '../pages/Recharge.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首页',
      requireAuth: false,
    },
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: Gallery,
    meta: {
      title: '照片视频',
      requireAuth: false,
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: '登录',
      requireAuth: false,
      hideForAuth: true, // 已登录用户不显示
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      title: '注册',
      requireAuth: false,
      hideForAuth: true, // 已登录用户不显示
    },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: {
      title: '个人资料',
      requireAuth: true,
    },
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat,
    meta: {
      title: '聊天',
      requireAuth: false,
    },
  },
  {
    path: '/recharge',
    name: 'Recharge',
    component: VIP,
    meta: {
      title: '账户充值',
      requireAuth: false,
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/',
  },
]

export default routes
