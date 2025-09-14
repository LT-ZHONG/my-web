# 🚀 一对一私聊系统部署指南

## 📦 快速部署

### 1. 环境准备

确保你的系统已安装：
- **Python 3.11+**
- **Node.js 18+**
- **npm 9+**

### 2. 后端部署

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（创建管理员账户）
python scripts/init_db.py

# 启动后端服务
python start.py
```

**默认管理员账户**：
- 用户名：`admin`
- 密码：`admin123456`  
- 邮箱：`admin@example.com`

### 3. 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 或构建生产版本
npm run build
```

### 4. 访问系统

- **前端地址**: `http://localhost:3000`
- **后端地址**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs`

## 🔧 配置说明

### 后端配置

主要配置文件：`backend/config.py`

```python
# 数据库配置
DATABASE_URL = "sqlite+aiosqlite:///./data/myweb.db"

# JWT 配置
SECRET_KEY = "your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 跨域配置
CORS_ORIGINS = ["http://localhost:3000"]
```

### 前端配置

配置文件：`frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 📋 功能验证

### 测试流程

1. **注册普通用户**
   - 访问 `http://localhost:3000`
   - 点击"注册"创建普通用户账户

2. **体验用户聊天**
   - 使用普通用户登录
   - 进入"聊天"页面
   - 与管理员开始对话

3. **体验管理员功能**
   - 使用管理员账户登录
   - 进入"聊天"页面
   - 查看左侧用户列表
   - 点击用户进行对话

## 🚦 服务状态检查

### 后端健康检查
```bash
curl http://localhost:8000/health
```

### WebSocket 连接测试
- 登录后进入聊天页面
- 查看连接状态指示器
- 发送测试消息

## 🔧 故障排除

### 常见问题

#### 1. 后端启动失败
```bash
# 检查Python版本
python --version

# 检查依赖安装
pip list

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

#### 2. 数据库初始化失败
```bash
# 删除现有数据库
rm backend/data/myweb.db

# 重新初始化
python scripts/init_db.py
```

#### 3. WebSocket 连接失败
- 检查后端服务是否正常运行
- 确认端口 8000 未被占用
- 检查防火墙设置

#### 4. 前端构建失败
```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules 重新安装
rm -rf node_modules
npm install
```

## 🔒 安全配置

### 生产环境建议

1. **修改默认密码**
   ```bash
   # 登录管理员账户后立即修改密码
   ```

2. **更新 JWT Secret**
   ```python
   # backend/config.py
   SECRET_KEY = "your-very-secure-secret-key-here"
   ```

3. **配置 HTTPS**
   ```python
   # backend/config.py
   CORS_ORIGINS = ["https://yourdomain.com"]
   ```

4. **数据库备份**
   ```bash
   # 定期备份 SQLite 数据库
   cp backend/data/myweb.db backup/myweb_$(date +%Y%m%d).db
   ```

## 📊 性能监控

### 日志查看
```bash
# 后端日志
tail -f backend/logs/app.log

# 访问日志
tail -f backend/logs/access.log
```

### 数据库管理
```bash
# 查看数据库文件大小
ls -lh backend/data/myweb.db

# SQLite 命令行工具
sqlite3 backend/data/myweb.db
```

## 🚢 Docker 部署（可选）

### 使用 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
      - ./backend/static:/app/static
    environment:
      - DEBUG=false
      - CORS_ORIGINS=http://localhost:3000

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

### 启动 Docker 服务
```bash
docker-compose up -d
```

## 📈 扩展建议

### 生产环境优化

1. **使用 PostgreSQL**
   ```python
   DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"
   ```

2. **添加 Redis 缓存**
   ```python
   REDIS_URL = "redis://localhost:6379"
   ```

3. **配置 Nginx 反向代理**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location /api/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location / {
           proxy_pass http://localhost:3000;
       }
   }
   ```

4. **SSL 证书配置**
   ```bash
   # 使用 Let's Encrypt
   certbot --nginx -d yourdomain.com
   ```

## 📞 技术支持

如果在部署过程中遇到问题，请检查：

1. **系统日志**：查看详细错误信息
2. **网络连接**：确保端口可访问
3. **权限设置**：检查文件读写权限
4. **版本兼容**：确认 Python/Node.js 版本

---

🎯 **部署完成后**，你就拥有了一个功能完整的一对一私聊系统，用户可以与你进行实时对话交流！
