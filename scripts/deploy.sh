#!/bin/bash
set -e

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 1. 安装依赖
echo "正在安装依赖..."
pip3 install -r requirements.txt

# 2. 检查并初始化数据库
DB_FILE="data/astra.db"
if [ ! -f "$DB_FILE" ]; then
    echo "数据库不存在，正在初始化..."
    python3 scripts/init_db.py
else
    echo "数据库已存在，跳过初始化。"
fi

# 3. 检查 logs 目录
if [ ! -d "logs" ]; then
    echo "创建 logs 目录..."
    mkdir logs
fi

# 4. 重启 systemd 服务（如未配置 systemd，可注释掉此行）
echo "重启 astra 服务..."
sudo systemctl restart astra

echo "部署完成！"
