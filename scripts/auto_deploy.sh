#!/bin/bash
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无色

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

line() { echo -e "${YELLOW}----------------------------------------${NC}"; }

cd /opt/telegram-agent

line
info "1. 检查 Python3 环境"
if ! command -v python3 &>/dev/null; then
    error "Python3 未安装或环境变量未配置，请检查！"
    exit 1
else
    success "Python3 已安装"
fi
info "检查 python3-venv 依赖"
if ! python3 -m venv --help &>/dev/null; then
    warn "python3-venv 未安装，正在尝试安装..."
    sudo apt-get update && sudo apt-get install -y python3-venv
    if ! python3 -m venv --help &>/dev/null; then
        error "python3-venv 安装失败，请手动检查！"
        exit 1
    fi
    success "python3-venv 已安装"
else
    success "python3-venv 已安装"
fi

line
info "2. 检查 Python 虚拟环境"
if [ -d venv ]; then
    success "Python 虚拟环境已存在，跳过创建"
else
    info "Python 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    if [ ! -d venv ]; then
        error "虚拟环境创建失败，请检查 python3-venv 是否已安装"
        exit 1
    fi
    success "虚拟环境创建完成"
fi

line
info "3. 激活 Python 虚拟环境"
if [ ! -f venv/bin/activate ]; then
    error "找不到 venv/bin/activate，虚拟环境未正确创建！"
    exit 1
fi
source venv/bin/activate
success "虚拟环境已激活"

line
info "4. 安装依赖"
# pip install --upgrade pip 静默
python -m pip install --upgrade pip --quiet || { error "pip 升级失败"; exit 2; }

# 卸载所有依赖（静默，防止交互）
pip freeze > all_requirements.txt
pip uninstall -y -r all_requirements.txt > /dev/null 2>&1 || true
rm -f all_requirements.txt

# 安装 requirements.txt，静默输出，出错才显示
if ! pip install -r requirements.txt --quiet; then
    error "依赖安装失败，请检查 requirements.txt"
    pip install -r requirements.txt  # 显示详细错误
    exit 2
fi
success "依赖安装完成"

line
info "5. 检查 data 目录"
if [ ! -d "data" ]; then
    info "data 目录不存在，正在创建..."
    mkdir data
    success "data 目录已创建"
else
    success "data 目录已存在"
fi

line
info "6. 检查数据库文件"
DB_FILE="data/astra.db"
if [ ! -f "$DB_FILE" ]; then
    info "数据库不存在，正在初始化..."
    python scripts/init_db.py
    success "数据库初始化完成"
else
    success "数据库已存在，跳过初始化"
fi

line
info "7. 检查 .env 文件"
if [ ! -f ".env" ]; then
    warn ".env 文件不存在，使用默认文件"
    cp -f /opt/data/astra/.env /opt/telegram-agent/.env
    success ".env 文件已复制"
else
    success ".env 文件已存在"
fi

line
info "8. 检查 systemd 服务文件"
SERVICE_FILE="/etc/systemd/system/astra.service"
if [ ! -f "$SERVICE_FILE" ]; then
    warn "systemd 服务 astra.service 不存在，当前目录：$(pwd) ；正在自动创建..."
    # 使用 sudo 时假设脚本运行用户有免密 sudo 权限，否则会阻塞
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
    success "systemd 服务已创建并启用"
else
    success "systemd 服务 astra.service 已存在"
fi

line
info "9. 重启 astra 服务"
sudo systemctl stop astra.service || true
sleep 0.5
sudo systemctl start astra.service
success "astra 服务已重启"

line
info "10. 检查服务状态"
sleep 1
sudo systemctl status astra.service --no-pager
success "服务状态检查完成"

line
success "全部步骤执行完毕！"
exit 0
