#!/bin/bash
set -e

# 检查 Python3
if ! command -v python3 &>/dev/null; then
    echo "Python3 未安装或环境变量未配置，请检查！"
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 检查 data 目录
if [ ! -d "data" ]; then
    echo "创建 data 目录..."
    mkdir data
fi

# 检查数据库文件
DB_FILE="data/astra.db"
if [ ! -f "$DB_FILE" ]; then
    echo "数据库不存在，正在初始化..."
    python scripts/init_db.py
else
    echo "数据库已存在，跳过初始化。"
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo ".env 文件不存在，请上传配置文件后重试。"
    exit 1
fi

# 检查 systemd 服务文件
SERVICE_FILE="/etc/systemd/system/astra.service"
if [ ! -f "$SERVICE_FILE" ]; then
    echo "systemd 服务 astra.service 不存在，正在自动创建..."
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Telegram Astra Bot Service
After=network.target

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python3 -m src.astra
Restart=always
User=$(whoami)
EnvironmentFile=$(pwd)/.env

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable astra.service
fi

# 重启服务
echo "重启 astra 服务..."
sudo systemctl restart astra.service

echo "部署完成！"
