// 导出所有API服务
export { authAPI } from './auth'
export { userAPI } from './user'
export { mediaAPI } from './media'

// 统一导出
export default {
  auth: () => import('./auth'),
  user: () => import('./user'),
  media: () => import('./media')
}
