# 项目技术规格说明书：OpenCloudPrint (SaaS 物联网云打印系统)

## 1. 项目概述
我们要构建一个名为 **"OpenCloudPrint"** 的私有化 SaaS 模式云打印系统。
该系统允许用户通过微信小程序上传文档（PDF、Word、图片）。这些文档在云端进行处理（转换格式），然后通过运行在 NAS 或树莓派上的“边缘端 Agent”，推送到位于不同局域网内的指定打印机进行打印。

**核心特性：**
* **多用户与多租户：** 用户可以绑定多台打印机；打印机可以被分享给不同用户。
* **实时打印：** 使用 MQTT 协议，实现云端指令到边缘设备的毫秒级推送。
* **内网穿透：** 边缘设备通过 MQTT 出站连接连入云端，打印机所在的网络无需拥有公网 IP。
* **格式转换：** 云端服务器负责处理文档兼容性，自动将 Word/Excel 转换为 PDF（使用 LibreOffice）。

## 2. 技术栈
* **云端后端 (Cloud Backend):** Python 3.9+ (FastAPI 框架), MySQL (元数据存储), Redis (缓存), Celery (异步任务，用于文档转换)。
* **消息代理 (Message Broker):** MQTT 协议 (推荐 Mosquitto 或 EMQX)。
* **边缘端代理 (Edge Agent):** Python 3.9+ (以 Docker 容器运行在 NAS 上), Paho-MQTT 库, CUPS-Client (调用 lp 命令)。
* **前端 (Frontend):** 微信小程序 (原生开发 或 Uni-app)。

## 3. 系统架构

```mermaid
graph TD
    %% 角色
    User((C端用户))
    Admin((设备所有者))

    %% 前端
    subgraph Client [微信小程序]
        UI_Upload[上传页面]
        UI_Bind[扫码绑定设备]
    end

    %% 云端基础设施
    subgraph Cloud_Server [云端服务器 (VPS)]
        API[FastAPI 网关]
        DB[(MySQL 数据库)]
        Redis[(Redis 缓存)]
        Worker[Celery 任务节点<br/>(LibreOffice 转换)]
        MQTT_Broker[MQTT 消息代理<br/>(Mosquitto)]
        FileStore[本地存储 / MinIO]
    end

    %% 边缘端基础设施 (家庭/办公室)
    subgraph Edge_Node [NAS / 边缘设备]
        Agent[Python 边缘 Agent]
        CUPS[CUPS 打印服务]
        Physical_Printer{物理打印机}
    end

    %% 数据流转
    User -->|1. 上传文件| UI_Upload
    UI_Upload -->|2. HTTPS POST 请求| API
    API -->|3. 保存原始文件| FileStore
    API -->|4. 创建打印任务记录| DB
    API -->|5. 触发转换任务| Worker
    Worker -->|6. 将 docx 转为 pdf| FileStore
    Worker -->|7. 发布 'Print' 指令| MQTT_Broker
    
    Agent -->|8. 订阅 'cmd' 主题| MQTT_Broker
    MQTT_Broker -->|9. 推送指令| Agent
    Agent -->|10. 下载 PDF 文件| API
    Agent -->|11. 调用 lp 命令| CUPS
    CUPS -->|12. 执行打印| Physical_Printer
    
    Agent -->|13. 发布 'Status' 状态| MQTT_Broker
    MQTT_Broker -->|14. 更新任务状态| API