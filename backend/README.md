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
- Pydantic V2

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

## 媒体上传流程分析

### 🖼️ 上传界面
从 `MediaUpload.vue` 组件可以看到：
- 支持拖拽上传，支持图片（`image/*`）和视频（`video/*`）文件
- 文件大小限制：**50MB**
- 支持设置标题、描述、标签、付费价格等信息
- 提供文件预览功能

### 📁 文件存储位置

根据配置和代码分析，文件上传后的存储结构如下：

```
项目根目录/
└── static/
    └── uploads/           # 主上传目录
        ├── image/         # 图片文件夹
        │   └── {用户ID}/  # 按用户ID分类
        │       ├── abc123.jpg      # 原始文件（重命名后）
        │       └── thumb_abc123.jpg # 缩略图
        └── video/         # 视频文件夹
            └── {用户ID}/  # 按用户ID分类
                └── def456.mp4
```

### 🔄 具体上传流程

1. **前端处理**：
   ```javascript
   // 用户在 MediaUpload.vue 中选择文件
   // 调用 mediaStore.uploadMedia(file, formData)
   // 发送到 /api/v1/media/upload 端点
   ```

2. **后端处理** (`backend/api/v1/media.py`):
   - 接收 `UploadFile` 和表单数据
   - 调用 `MediaService.upload_media()` 处理

3. **文件处理** (`backend/utils/file_utils.py`):
   ```python
   # 验证文件类型和大小
   validate_file_type(file)  # 检查MIME类型
   validate_file_size(file)  # 检查是否超过50MB
   
   # 生成存储路径
   # static/uploads/{image|video}/{user_id}/
   upload_path = get_upload_path(file_type, user_id)
   
   # 生成唯一文件名
   filename = generate_filename(file.filename)  # UUID + 扩展名
   ```

4. **数据库记录**：
   - 在 `Media` 表中创建记录
   - 存储文件路径、URL、尺寸、MIME类型等信息

### 📊 文件信息

**支持的格式**：
- **图片**: JPEG, PNG, GIF, WebP
- **视频**: MP4, AVI, MOV, WMV

**文件处理**：
- 生成UUID作为文件名，防止冲突
- 图片自动生成缩略图（300x300像素）
- 获取图片尺寸信息
- 计算文件大小和MIME类型

### 🔗 访问路径

上传成功后，文件可通过以下URL访问：
```
http://your-domain/static/uploads/image/123/abc123.jpg     # 原图
http://your-domain/static/uploads/image/123/thumb_abc123.jpg  # 缩略图
```

### 💾 存储配置

在 `backend/config.py` 中的关键配置：
- `UPLOAD_DIR = "static/uploads"`  # 上传目录
- `MAX_FILE_SIZE = 50MB`  # 最大文件大小
- 文件类型白名单限制

这样的设计确保了：
✅ 文件按用户分类存储，便于管理  
✅ 自动生成缩略图，提升访问速度  
✅ 使用UUID文件名，避免文件名冲突  
✅ 严格的文件类型和大小验证，确保安全性
