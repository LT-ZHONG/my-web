import { createPinia } from 'pinia'

export const pinia = createPinia()

// 导出所有store
export { useAuthStore } from './auth'
export { useUserStore } from './user'
export { useMediaStore } from './media'
export { useChatStore } from './chat'
