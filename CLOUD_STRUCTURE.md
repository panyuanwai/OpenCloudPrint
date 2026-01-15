# OpenCloudPrint 云端服务项目结构

```
netprint/
├── docker-compose.yml          # Docker Compose 编排文件
├── .env.example                # 环境变量示例文件
│
├── docker/                     # Docker 配置文件
│   ├── mysql/
│   │   └── init.sql           # MySQL 数据库初始化脚本
│   └── mosquitto/
│       ├── mosquitto.conf     # MQTT Broker 配置
│       └── passwd             # MQTT 用户密码文件 (需手动生成)
│
├── backend/                    # FastAPI 后端服务
│   ├── Dockerfile             # Backend 镜像构建文件
│   ├── requirements.txt       # Python 依赖
│   └── app/
│       ├── main.py            # 应用入口
│       ├── api/               # API 路由
│       │   └── v1/
│       │       ├── __init__.py
│       │       └── endpoints/  # API 端点
│       │           ├── auth.py      # 认证相关
│       │           ├── printers.py  # 打印机管理
│       │           ├── jobs.py      # 打印任务管理
│       │           └── agents.py    # Agent 管理
│       ├── core/              # 核心配置
│       │   ├── config.py      # 配置管理
│       │   └── database.py    # 数据库连接
│       ├── models/            # SQLAlchemy 数据模型 (待实现)
│       ├── schemas/           # Pydantic 数据模型 (待实现)
│       └── services/          # 业务逻辑层 (待实现)
│
└── worker/                     # Celery Worker (文档转换)
    ├── Dockerfile             # Worker 镜像构建文件
    ├── requirements.txt       # Python 依赖
    └── app/
        ├── core/              # 核心配置
        │   ├── config.py      # 配置管理
        │   └── database.py    # 数据库连接
        └── tasks/             # Celery 任务
            ├── celery_app.py  # Celery 应用配置
            ├── conversion.py  # 文档转换任务
            └── mqtt.py        # MQTT 发布任务
```

## 快速启动

### 1. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，修改必要的配置项
```

### 2. 生成 MQTT 密码文件
```bash
# 安装 mosquitto-clients
# 生成密码文件
mosquitto_passwd -b docker/mosquitto/passwd ocp_mqtt_user your_password
```

### 3. 启动所有服务
```bash
docker-compose up -d
```

### 4. 查看服务状态
```bash
docker-compose ps
```

### 5. 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

## 服务端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| Backend API | 8000 | FastAPI 服务，访问 http://localhost:8000/docs |
| MySQL | 3306 | 数据库 |
| Redis | 6379 | 缓存和消息队列 |
| MQTT Broker | 1883 | MQTT 协议端口 |
| MQTT WebSocket | 9001 | MQTT WebSocket 端口 |
| Flower | 5555 | Celery 任务监控，访问 http://localhost:5555 |

## API 文档

启动服务后，访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 下一步

- [ ] 实现 SQLAlchemy 数据模型 (backend/app/models/)
- [ ] 实现 Pydantic Schema 验证 (backend/app/schemas/)
- [ ] 实现业务逻辑服务层 (backend/app/services/)
- [ ] 实现微信小程序登录认证
- [ ] 实现文件上传和处理逻辑
- [ ] 实现 MQTT 消息订阅和状态回调
- [ ] 添加单元测试
- [ ] 配置 Nginx 反向代理 (生产环境)
