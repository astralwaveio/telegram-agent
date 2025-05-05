#!/bin/bash
set -e
export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH

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

# 切换到项目目录
DEPLOY_DIR="/opt/telegram-agent"
cd "$DEPLOY_DIR"

line
info "0. 环境与目录检查"
info "当前目录: $(pwd)"
ls -al
df -h
whoami

line
info "1. 检查 Python3 环境"
if ! command -v python3 &>/dev/null; then
    error "Python3 未安装或环境变量未配置，请检查！"
    exit 1
else
    success "Python3 已安装"
fi
info "Python3 版本: $(python3 --version)"

line
info "1.1 检查 python3-venv 依赖"
if ! python3 -m venv --help &>/dev/null; then
    warn "python3-venv 未安装，正在尝试安装..."
    if [ "$(id -u)" -eq 0 ]; then
        apt-get update && apt-get install -y python3-venv
    else
        sudo apt-get update && sudo apt-get install -y python3-venv
    fi
    if ! python3 -m venv --help &>/dev/null; then
        error "python3-venv 安装失败，请手动检查！"
        exit 1
    fi
    success "python3-venv 已安装"
else
    success "python3-venv 已安装"
fi

line
info "2. 删除并重新创建 Python 虚拟环境"
if [ -d venv ]; then
    warn "发现旧的 venv 目录，正在删除..."
    rm -rf venv
    success "旧的 venv 目录已删除"
fi
info "正在创建新的虚拟环境..."
/usr/bin/python3 -m venv venv
if [ ! -d venv ]; then
    error "虚拟环境创建失败，请检查 python3-venv 是否已安装、磁盘空间和权限"
    exit 1
fi
ls -al venv || true
ls -al venv/bin || true
success "虚拟环境创建完成"

line
info "3. 激活 Python 虚拟环境"
echo "当前目录: $(pwd)"
ls -al
if [ ! -f venv/bin/activate ]; then
    error "找不到 venv/bin/activate，虚拟环境未正确创建！"
    exit 1
fi
source venv/bin/activate
success "虚拟环境已激活"

line
info "4. 安装依赖"
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
    if [ "$(id -u)" -eq 0 ]; then
        TEE_CMD="tee"
        SYSTEMCTL_CMD="systemctl"
    else
        TEE_CMD="sudo tee"
        SYSTEMCTL_CMD="sudo systemctl"
    fi
    $TEE_CMD "$SERVICE_FILE" > /dev/null <<EOF
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
    $SYSTEMCTL_CMD daemon-reload
    $SYSTEMCTL_CMD enable astra.service
    success "systemd 服务已创建并启用"
else
    success "systemd 服务 astra.service 已存在"
fi

line
info "9. 重启 astra 服务"
if [ "$(id -u)" -eq 0 ]; then
    systemctl stop astra.service || true
    sleep 0.5
    systemctl start astra.service
else
    sudo systemctl stop astra.service || true
    sleep 0.5
    sudo systemctl start astra.service
fi
success "astra 服务已重启"

line
info "10. 检查服务状态"
sleep 1
if [ "$(id -u)" -eq 0 ]; then
    systemctl status astra.service --no-pager
else
    sudo systemctl status astra.service --no-pager
fi
success "服务状态检查完成"

line
success "全部步骤执行完毕！"
exit 0
