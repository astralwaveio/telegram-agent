#!/bin/bash
set -e

cd /opt/telegram-agent

# 检查 Python3
if ! command -v python3 &>/dev/null; then
    echo "Python3 未安装或环境变量未配置，请检查！"
fi

rm -rf venv
echo "创建 Python 虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "激活 Python 虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ 依赖安装完成！ 检查 data 目录"

# 检查 data 目录
if [ ! -d "data" ]; then
    echo "创建 data 目录..."
    mkdir data
fi

# 检查数据库文件
echo "检查数据库文件..."
DB_FILE="data/astra.db"
if [ ! -f "$DB_FILE" ]; then
    echo "数据库不存在，正在初始化..."
    python scripts/init_db.py
else
    echo "✅ 数据库已存在，跳过初始化。"
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo ".env 文件不存在，使用默认文件。"
    cp -f /opt/data/astra/.env /opt/telegram-agent/.env
fi

echo "✅ .env 文件已存在，检查通过。"
# 检查 systemd 服务文件
SERVICE_FILE="/etc/systemd/system/astra.service"
if [ ! -f "$SERVICE_FILE" ]; then
    echo "⚠️ systemd 服务 astra.service 不存在，正在自动创建..."
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
else
    echo "✅ systemd 服务 astra.service 已存在，检查通过。"
fi

# 重启服务
echo "重启 astra 服务..."
sudo systemctl stop astra.service
sudo systemctl start astra.service
echo "✅ astra 服务已重启！"

echo "检查服务状态..."
sudo systemctl status astra.service
echo "✅ 服务状态检查完成！"
exit 0
