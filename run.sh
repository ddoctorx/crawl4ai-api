#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 检查python3是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到python3。请先安装Python 3.8+${NC}"
    exit 1
fi

# 显示帮助信息的函数
show_help() {
    echo -e "使用方法: $0 [选项]"
    echo -e "选项:"
    echo -e "  --help          显示帮助信息"
    echo -e "  --uv            使用uv代替pip安装依赖 (如果已安装)"
    echo -e "  --no-venv       不创建虚拟环境"
    echo -e "  --install-only  只安装依赖，不启动服务"
    echo -e "  --port=NUMBER   指定端口号 (默认: 8000)"
    exit 0
}

# 默认配置
USE_UV=false
USE_VENV=true
INSTALL_ONLY=false
PORT=8000

# 解析命令行参数
for arg in "$@"; do
    case $arg in
        --help)
            show_help
            ;;
        --uv)
            USE_UV=true
            ;;
        --no-venv)
            USE_VENV=false
            ;;
        --install-only)
            INSTALL_ONLY=true
            ;;
        --port=*)
            PORT="${arg#*=}"
            ;;
        *)
            echo -e "${YELLOW}警告: 未知选项 $arg${NC}"
            ;;
    esac
done

# 项目目录
PROJECT_DIR=$(pwd)

# 设置虚拟环境
if [ "$USE_VENV" = true ]; then
    echo -e "${GREEN}设置虚拟环境...${NC}"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}错误: 无法创建虚拟环境。请安装venv模块: pip3 install virtualenv${NC}"
            exit 1
        fi
    fi

    # 激活虚拟环境
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 无法激活虚拟环境${NC}"
        exit 1
    fi
    echo -e "${GREEN}虚拟环境已激活${NC}"
fi

# 安装依赖
echo -e "${GREEN}安装项目依赖...${NC}"
if [ "$USE_UV" = true ]; then
    # 检查uv是否安装
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}警告: 未找到uv。将使用pip3代替安装${NC}"
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
    else
        uv pip install -r requirements.txt
    fi
else
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 安装依赖失败${NC}"
    exit 1
fi

# 安装Playwright
echo -e "${GREEN}安装Playwright浏览器...${NC}"
python3 -m playwright install
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 安装Playwright浏览器失败${NC}"
    exit 1
fi

echo -e "${GREEN}设置完成!${NC}"

# 如果只是安装依赖，则退出
if [ "$INSTALL_ONLY" = true ]; then
    echo -e "${GREEN}已完成依赖安装。使用 '$0' 启动服务。${NC}"
    exit 0
fi

# 启动服务
echo -e "${GREEN}启动Crawl4AI API服务在端口 $PORT...${NC}"
echo -e "${YELLOW}按Ctrl+C停止服务${NC}"

# 创建.env文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "PORT=$PORT" > .env
    echo -e "${GREEN}已创建.env文件，设置端口为 $PORT${NC}"
fi

# 启动应用
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload

# 如果使用了虚拟环境，退出虚拟环境
if [ "$USE_VENV" = true ]; then
    deactivate
fi