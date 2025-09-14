# 个人生活展示网站 - 后端API

基于 FastAPI 构建的现代化后端服务，支持用户管理、媒体展示、实时聊天和支付功能。

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Redis 6.0+（可选，用于缓存和会话管理）

**注意**: 已使用SQLite作为主数据库，无需单独安装数据库服务器。

### 本地开发

1. **克隆项目并进入后端目录**
   ```bash
   cd backend
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量（可选）**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，自定义配置（SQLite 使用默认配置即可运行）
   ```

5. **启动服务**
   ```bash
   python start.py
   # 或
   uvicorn main:app --reload
   ```

6. **访问服务**
   - API文档: http://localhost:8000/docs
   - 健康检查: http://localhost:8000/health

### Docker 部署

1. **使用 Docker Compose（推荐）**
   ```bash
   docker-compose up -d
   ```

2. **单独构建镜像**
   ```bash
   docker build -t mywebsite-backend .
   docker run -p 8000:8000 mywebsite-backend
   ```

## 📖 API 文档

### 认证 API

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新令牌
- `POST /api/v1/auth/change-password` - 修改密码
- `GET /api/v1/auth/me` - 获取当前用户信息

### 用户 API

- `GET /api/v1/users/me` - 获取个人信息
- `PUT /api/v1/users/me` - 更新个人信息
- `GET /api/v1/users/{user_id}` - 获取用户信息
- `GET /api/v1/users/` - 获取用户列表（管理员）

### 媒体 API

#### 媒体文件管理
- `GET /api/v1/media/` - 获取媒体列表（支持分页、搜索、过滤）
- `POST /api/v1/media/upload` - 上传媒体文件（支持图片和视频）
- `GET /api/v1/media/{media_id}` - 获取媒体详情
- `PUT /api/v1/media/{media_id}` - 更新媒体信息
- `DELETE /api/v1/media/{media_id}` - 删除媒体文件
- `POST /api/v1/media/{media_id}/like` - 点赞/取消点赞
- `GET /api/v1/media/{media_id}/download` - 下载媒体文件
- `GET /api/v1/media/stats/overview` - 获取媒体统计信息

#### 媒体分类管理
- `GET /api/v1/media/categories/` - 获取分类列表
- `POST /api/v1/media/categories/` - 创建分类（管理员）
- `GET /api/v1/media/categories/{category_id}` - 获取分类详情
- `PUT /api/v1/media/categories/{category_id}` - 更新分类（管理员）
- `DELETE /api/v1/media/categories/{category_id}` - 删除分类（管理员）

### 聊天 API（开发中）

- `GET /api/v1/chat/rooms` - 获取聊天室列表
- `WebSocket /api/v1/chat/ws` - WebSocket 聊天连接

### 支付 API（开发中）

- `GET /api/v1/payment/plans` - 获取 VIP 套餐
- `POST /api/v1/payment/orders` - 创建订单
- `GET /api/v1/payment/orders` - 获取订单列表

## 🏗️ 项目结构

```
backend/
├── api/                    # API 路由层
│   └── v1/                 # API v1 版本
│       ├── auth.py         # 认证相关 API
│       ├── users.py        # 用户相关 API
│       ├── media.py        # 媒体相关 API
│       ├── chat.py         # 聊天相关 API
│       ├── payment.py      # 支付相关 API
│       └── admin.py        # 管理员相关 API
├── models/                 # 数据库模型
│   ├── user.py             # 用户模型
│   ├── media.py            # 媒体模型
│   ├── chat.py             # 聊天模型
│   └── payment.py          # 支付模型
├── schemas/                # Pydantic 模式
│   ├── user.py             # 用户模式
│   ├── media.py            # 媒体模式
│   ├── chat.py             # 聊天模式
│   └── payment.py          # 支付模式
├── services/               # 业务逻辑层
│   └── user_service.py     # 用户服务
├── utils/                  # 工具函数
│   ├── auth.py             # 认证工具
│   ├── file_utils.py       # 文件处理工具
│   ├── exceptions.py       # 自定义异常
│   └── middleware.py       # 中间件
├── scripts/                # 脚本
│   └── init_db.py          # 数据库初始化
├── static/                 # 静态文件
│   └── uploads/            # 上传文件目录
├── data/                   # SQLite 数据库文件目录
├── main.py                 # 应用入口
├── config.py               # 配置管理
├── database.py             # 数据库连接
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 配置
├── docker-compose.yml      # Docker Compose 配置
└── start.py                # 启动脚本
```

## 🔧 配置说明

### 环境变量

主要配置项请参考 `.env.example` 文件：

- `DEBUG`: 调试模式
- `SECRET_KEY`: JWT 密钥
- `DATABASE_URL`: SQLite 数据库文件路径（默认: `sqlite+aiosqlite:///./data/myweb.db`）
- `REDIS_URL`: Redis 连接字符串（可选）

### 数据库配置

1. **SQLite** - 主数据库，存储所有应用数据（用户、媒体、聊天、订单等）
2. **Redis** - 缓存和会话存储（可选）

#### SQLite 优势

- **🚀 零配置部署**: 无需安装和配置单独的数据库服务器
- **📁 文件型存储**: 数据库存储为单个文件，便于备份和迁移
- **🔧 开发友好**: 开发环境设置简单，支持并发读取
- **💾 轻量高效**: 适合中小型项目，性能优秀
- **🐳 Docker优化**: 容器化部署更简单，资源占用更少
- **🗄️ 功能完整**: 支持JSON字段、全文搜索、事务等现代数据库特性

## 🔒 安全特性

- JWT 认证机制
- 密码 bcrypt 加密
- API 请求限流
- CORS 跨域保护
- 文件上传安全验证
- SQL 注入防护
- XSS 防护

## 📊 功能特性

### ✅ 已完成

- [x] 项目架构搭建
- [x] 用户认证系统（注册、登录、JWT）
- [x] 数据库模型设计
- [x] 基础 API 框架
- [x] 安全中间件
- [x] Docker 部署配置
- [x] 媒体管理 API（上传、下载、分类、统计等）

### 🚧 开发中

- [ ] WebSocket 实时聊天
- [ ] 支付系统集成
- [ ] 管理员后台
- [ ] 文件存储优化

### 📋 计划中

- [ ] 单元测试
- [ ] API 文档优化
- [ ] 性能监控
- [ ] 日志系统
- [ ] 缓存优化

## 🧪 测试

```bash
# 运行测试（开发中）
pytest

# 测试覆盖率
pytest --cov=.
```

## 📝 API 使用示例

### 用户注册

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "confirm_password": "password123",
    "full_name": "测试用户"
  }'
```

### 用户登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 上传媒体文件

```bash
# 先获取访问令牌
TOKEN="your_access_token_here"

# 上传图片
curl -X POST "http://localhost:8000/api/v1/media/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "title=我的照片" \
  -F "description=这是一张美丽的照片" \
  -F "tags=风景,旅行,摄影" \
  -F "is_paid=false" \
  -F "price=0.0"
```

### 获取媒体列表

```bash
curl -X GET "http://localhost:8000/api/v1/media/?page=1&page_size=20&media_type=image" \
  -H "Authorization: Bearer $TOKEN"
```

### 获取媒体统计

```bash
curl -X GET "http://localhost:8000/api/v1/media/stats/overview" \
  -H "Authorization: Bearer $TOKEN"
```
