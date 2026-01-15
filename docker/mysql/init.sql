-- OpenCloudPrint 数据库初始化脚本
-- MySQL 8.0+

-- 字符集设置
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    openid VARCHAR(128) NOT NULL UNIQUE COMMENT '微信 OpenID',
    nickname VARCHAR(64) DEFAULT NULL COMMENT '用户昵称',
    avatar_url VARCHAR(512) DEFAULT NULL COMMENT '头像 URL',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_openid (openid),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 打印机表
CREATE TABLE IF NOT EXISTS printers (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    printer_id VARCHAR(64) NOT NULL UNIQUE COMMENT '打印机唯一标识 (UUID)',
    printer_name VARCHAR(128) NOT NULL COMMENT '打印机名称',
    agent_id VARCHAR(64) NOT NULL COMMENT '边缘 Agent ID',
    owner_id BIGINT UNSIGNED NOT NULL COMMENT '所有者用户 ID',
    model VARCHAR(128) DEFAULT NULL COMMENT '打印机型号',
    location VARCHAR(256) DEFAULT NULL COMMENT '位置描述',
    status ENUM('online', 'offline', 'error') DEFAULT 'offline' COMMENT '打印机状态',
    last_heartbeat DATETIME DEFAULT NULL COMMENT '最后心跳时间',
    is_shared BOOLEAN DEFAULT FALSE COMMENT '是否已分享',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_printer_id (printer_id),
    INDEX idx_agent_id (agent_id),
    INDEX idx_owner_id (owner_id),
    INDEX idx_status (status),
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打印机表';

-- 打印机授权表 (用户-打印机多对多关系)
CREATE TABLE IF NOT EXISTS printer_permissions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    printer_id BIGINT UNSIGNED NOT NULL COMMENT '打印机 ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '授权用户 ID',
    permission ENUM('read', 'print', 'admin') DEFAULT 'print' COMMENT '权限级别',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
    INDEX idx_printer_user (printer_id, user_id),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (printer_id) REFERENCES printers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_printer_user (printer_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打印机授权表';

-- 打印任务表
CREATE TABLE IF NOT EXISTS print_jobs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL UNIQUE COMMENT '任务唯一标识 (UUID)',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '提交任务的用户 ID',
    printer_id BIGINT UNSIGNED NOT NULL COMMENT '目标打印机 ID',
    file_name VARCHAR(256) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(512) NOT NULL COMMENT '原始文件存储路径',
    file_size BIGINT UNSIGNED DEFAULT 0 COMMENT '文件大小 (字节)',
    file_type VARCHAR(32) NOT NULL COMMENT '文件类型 (pdf/docx/xlsx/img)',
    converted_path VARCHAR(512) DEFAULT NULL COMMENT '转换后的 PDF 文件路径',
    status ENUM('pending', 'converting', 'queued', 'printing', 'completed', 'failed', 'cancelled') DEFAULT 'pending' COMMENT '任务状态',
    copies INT DEFAULT 1 COMMENT '打印份数',
    page_range VARCHAR(64) DEFAULT NULL COMMENT '页面范围 (如: 1-5,8,11-13)',
    color_mode ENUM('color', 'grayscale') DEFAULT 'color' COMMENT '色彩模式',
    duplex_mode ENUM('simplex', 'duplex-long-edge', 'duplex-short-edge') DEFAULT 'simplex' COMMENT '双面打印模式',
    error_message TEXT DEFAULT NULL COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    completed_at DATETIME DEFAULT NULL COMMENT '完成时间',
    INDEX idx_job_id (job_id),
    INDEX idx_user_id (user_id),
    INDEX idx_printer_id (printer_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (printer_id) REFERENCES printers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打印任务表';

-- Agent 表
CREATE TABLE IF NOT EXISTS agents (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL UNIQUE COMMENT 'Agent 唯一标识 (UUID)',
    agent_name VARCHAR(128) NOT NULL COMMENT 'Agent 名称',
    agent_version VARCHAR(32) DEFAULT '1.0.0' COMMENT 'Agent 版本',
    os_info VARCHAR(64) DEFAULT NULL COMMENT '操作系统信息',
    arch VARCHAR(32) DEFAULT NULL COMMENT 'CPU 架构',
    status ENUM('online', 'offline') DEFAULT 'offline' COMMENT 'Agent 状态',
    last_heartbeat DATETIME DEFAULT NULL COMMENT '最后心跳时间',
    ip_address VARCHAR(64) DEFAULT NULL COMMENT 'IP 地址',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_agent_id (agent_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='边缘 Agent 表';

-- 任务日志表 (可选)
CREATE TABLE IF NOT EXISTS job_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    job_id BIGINT UNSIGNED NOT NULL COMMENT '打印任务 ID',
    level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') DEFAULT 'INFO' COMMENT '日志级别',
    message TEXT NOT NULL COMMENT '日志消息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_job_id (job_id),
    INDEX idx_level (level),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (job_id) REFERENCES print_jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打印任务日志表';
