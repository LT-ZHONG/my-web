# 个人生活展示网站

一个功能完整的个人展示网站，支持媒体上传、用户管理、实时聊天、VIP会员系统等功能。

## 🏗️ 项目架构

本项目采用前后端分离架构：

- **前端**: Vue 3 + TypeScript + Pinia + Ant Design Vue
- **后端**: FastAPI + SQLAlchemy + SQLite
- **实时通信**: WebSocket
- **认证**: JWT Token
- **部署**: Docker + Docker Compose

## 📁 项目结构

```
my-web/
├── frontend/           # Vue 3前端应用
│   ├── src/
│   │   ├── components/  # 通用组件
│   │   ├── pages/       # 页面组件
│   │   ├── stores/      # Pinia状态管理
│   │   ├── services/    # API服务层
│   │   ├── utils/       # 工具函数
│   │   └── types/       # TypeScript类型定义
│   └── README.md
├── backend/            # FastAPI后端服务
│   ├── api/            # API路由
│   ├── models/         # 数据库模型
│   ├── schemas/        # Pydantic模式
│   ├── services/       # 业务逻辑
│   └── README.md
├── DEPLOYMENT_GUIDE.md  # 部署指南
└── PRIVATE_CHAT_GUIDE.md # 私聊功能说明
```

## 🚀 快速开始

### 环境要求

- Node.js 18.0+
- Python 3.11+
- Docker (可选)

### 本地开发

1. **克隆项目**
   ```bash
   git clone <your-repo-url>
   cd my-web
   ```

2. **启动后端服务**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python start.py
   ```

3. **启动前端服务**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **访问应用**
   - 前端: http://localhost:3000
   - 后端API: http://localhost:8000
   - API文档: http://localhost:8000/docs

### Docker部署

```bash
# 后端服务
cd backend
docker-compose up -d

# 前端服务需要单独构建（详见DEPLOYMENT_GUIDE.md）
```

## ✨ 主要功能

### 已完成功能 ✅

- **用户系统**: 注册、登录、个人资料管理、权限控制
- **媒体管理**: 图片/视频上传、预览、下载、点赞、分类
- **VIP系统**: 会员权限控制、付费内容访问
- **响应式设计**: 完美适配手机、平板、电脑
- **类型安全**: 完整的TypeScript类型系统
- **状态管理**: 基于Pinia的响应式状态管理
- **API对接**: REST-ful API，自动token管理和错误处理

### 开发中功能 🚧

- **实时聊天**: WebSocket聊天室，在线状态显示
- **支付系统**: 多种支付方式，订单管理
- **管理员后台**: 用户管理、内容审核

### 计划功能 📋

- **消息推送**: 实时通知系统
- **数据分析**: 访问统计、用户行为分析
- **SEO优化**: 搜索引擎优化
- **PWA支持**: 离线访问支持

## 🔧 技术特性

### 前端技术亮点

- **Vue 3 Composition API**: 现代化的组件开发方式
- **TypeScript**: 完整的类型系统，提升开发效率和代码质量
- **Pinia**: 轻量级状态管理，替代Vuex
- **Ant Design Vue**: 企业级UI组件库
- **Vite**: 快速的开发构建工具
- **自动类型推导**: 全链路类型安全

### 后端技术亮点

- **FastAPI**: 高性能、自动API文档生成
- **SQLAlchemy**: ORM，支持异步操作
- **SQLite**: 零配置数据库，便于部署
- **JWT认证**: 无状态认证，支持token刷新
- **RESTful API**: 标准化的API设计

### 开发规范

- **代码规范**: ESLint + Prettier自动格式化
- **Git规范**: 语义化提交信息
- **类型安全**: 严格的TypeScript配置
- **错误处理**: 统一的错误处理机制
- **API设计**: RESTful风格，标准化响应格式

## 📊 项目状态

### 代码质量

- ✅ TypeScript类型覆盖率: 100%
- ✅ ESLint检查: 无错误
- ✅ API响应类型安全
- ✅ 统一错误处理机制

### 性能优化

- ✅ 前端打包体积优化
- ✅ 图片懒加载
- ✅ 路由懒加载
- ✅ API请求缓存
- ✅ 分页加载优化

## 📝 开发指南

### 提交代码前检查

```bash
# 前端检查
cd frontend
npm run lint      # 代码检查
npm run build     # 构建检查

# 后端检查
cd backend
python -m flake8  # 代码规范检查
```

### API开发规范

1. **响应格式**: 统一使用 `ApiResponse<T>` 格式
2. **错误处理**: 使用标准HTTP状态码和错误信息
3. **类型安全**: 前后端类型定义保持一致
4. **文档**: 使用FastAPI自动生成API文档

### 前端开发规范

1. **组件命名**: PascalCase
2. **文件命名**: kebab-case
3. **类型定义**: 放在 `types/index.ts` 中
4. **状态管理**: 使用Pinia，按功能模块划分
5. **API调用**: 通过service层，统一错误处理

