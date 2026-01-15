import os
import time
import json
import requests
import subprocess
import paho.mqtt.client as mqtt
from pathlib import Path

# ========== 配置区域 (请修改这里) ==========
# 云服务器 IP (请换成你云服务器的公网 IP)
SERVER_IP = "YOUR_CLOUD_SERVER_IP" 
# 打印机名称 (必须与 NAS CUPS 里的名字完全一致，根据你的截图是 HP_Laser_178nw)
PRINTER_NAME = "HP_Laser_178nw" 
# 设备唯一 ID (自己取一个英文名)
DEVICE_ID = "nas_home_001" 
# =========================================

# API 和 MQTT 配置
API_BASE_URL = f"http://{SERVER_IP}:8000/api/v1"
MQTT_BROKER = SERVER_IP
MQTT_PORT = 1883
TEMP_DIR = "/tmp/print_jobs"

# 确保临时目录存在
Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ 已连接到云端 MQTT中心! 设备ID: {DEVICE_ID}")
        # 订阅指令频道: printers/{device_id}/command
        topic = f"printers/{DEVICE_ID}/command"
        client.subscribe(topic)
        print(f"📡 正在监听指令: {topic}")
    else:
        print(f"❌ 连接失败, 错误码: {rc}")

def on_message(client, userdata, msg):
    try:
        print("📩 收到新消息...")
        payload = json.loads(msg.payload.decode())
        
        if payload.get('type') == 'print':
            handle_print_job(payload)
            
    except Exception as e:
        print(f"❌ 消息处理出错: {e}")

def handle_print_job(job_data):
    """处理打印任务：下载 -> 打印"""
    job_id = job_data.get('job_id')
    # 注意：这里假设云端返回的是相对路径或完整 URL，需要根据实际 API 调整
    file_url = job_data.get('file_url') 
    
    # 如果 URL 不含 http，手动拼接
    if not file_url.startswith("http"):
        file_url = f"http://{SERVER_IP}:8000{file_url}"

    print(f"🖨️ 开始处理任务 {job_id}, 下载地址: {file_url}")
    
    # 1. 下载文件
    local_filename = f"{TEMP_DIR}/{job_id}.pdf"
    try:
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("✅ 文件下载完成")
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return

    # 2. 调用 CUPS 打印
    # lp -d [打印机名] [文件名]
    cmd = ["lp", "-d", PRINTER_NAME, local_filename]
    try:
        subprocess.run(cmd, check=True)
        print(f"🚀 指令已发送给打印机 ({PRINTER_NAME})")
        # TODO: 可以通过 MQTT 发送回执告诉云端“打印成功”
    except subprocess.CalledProcessError as e:
        print(f"❌ 打印命令执行失败: {e}")

def start_agent():
    client = mqtt.Client(client_id=f"agent_{DEVICE_ID}")
    client.on_connect = on_connect
    client.on_message = on_message
    
    # 自动重连机制
    while True:
        try:
            print(f"🔄 正在连接云端 {MQTT_BROKER}...")
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_forever() # 阻塞运行
        except Exception as e:
            print(f"⚠️ 连接断开或失败: {e}")
            print("⏳ 5秒后重试...")
            time.sleep(5)

if __name__ == "__main__":
    start_agent()