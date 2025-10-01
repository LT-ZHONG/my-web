import type { RouteRecordRaw } from 'vue-router'
import Home from '../pages/Home.vue'
import Gallery from '../pages/Gallery.vue'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Profile from '../pages/Profile.vue'
import Chat from '../pages/Chat.vue'
import VIP from '../pages/VIP.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首页 - giffalena',
      requireAuth: false,
    },
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: Gallery,
    meta: {
      title: '照片视频 - giffalena',
      requireAuth: false,
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: '登录 - giffalena',
      requireAuth: false,
      hideForAuth: true, // 已登录用户不显示
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      title: '注册 - giffalena',
      requireAuth: false,
      hideForAuth: true, // 已登录用户不显示
    },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: {
      title: '个人资料 - giffalena',
      requireAuth: true,
    },
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat,
    meta: {
      title: '聊天 - giffalena',
      requireAuth: false,
    },
  },
  {
    path: '/vip',
    name: 'VIP',
    component: VIP,
    meta: {
      title: 'VIP会员 - giffalena',
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
