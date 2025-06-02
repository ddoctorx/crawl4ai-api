#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 显示帮助信息
show_help() {
    echo -e "${BLUE}Crawl4AI API 测试运行器${NC}"
    echo -e "使用方法: $0 [选项]"
    echo -e ""
    echo -e "选项:"
    echo -e "  ${GREEN}--help${NC}            显示帮助信息"
    echo -e "  ${GREEN}--unit${NC}            只运行单元测试"
    echo -e "  ${GREEN}--integration${NC}     只运行集成测试"
    echo -e "  ${GREEN}--coverage${NC}        生成覆盖率报告"
    echo -e "  ${GREEN}--html${NC}            生成HTML覆盖率报告"
    echo -e "  ${GREEN}--verbose${NC}         详细输出"
    echo -e "  ${GREEN}--file=<path>${NC}     运行特定测试文件"
    echo -e "  ${GREEN}--mark=<marker>${NC}   运行特定标记的测试"
    echo -e "  ${GREEN}--no-cov${NC}          不计算覆盖率"
    echo -e "  ${GREEN}--watch${NC}           监视模式（文件变化时重新运行）"
    echo -e "  ${GREEN}--lint${NC}            运行代码检查"
    echo -e "  ${GREEN}--format${NC}          格式化代码"
    echo -e ""
    echo -e "示例:"
    echo -e "  $0                        # 运行所有测试"
    echo -e "  $0 --unit                 # 只运行单元测试"
    echo -e "  $0 --coverage --html      # 运行测试并生成HTML报告"
    echo -e "  $0 --file=tests/test_crawler_service.py  # 运行特定文件"
    exit 0
}

# 默认配置
RUN_UNIT=true
RUN_INTEGRATION=true
COVERAGE=false
HTML_REPORT=false
VERBOSE=""
SPECIFIC_FILE=""
SPECIFIC_MARK=""
NO_COV=false
WATCH_MODE=false
RUN_LINT=false
FORMAT_CODE=false

# 解析命令行参数
for arg in "$@"; do
    case $arg in
        --help)
            show_help
            ;;
        --unit)
            RUN_UNIT=true
            RUN_INTEGRATION=false
            ;;
        --integration)
            RUN_UNIT=false
            RUN_INTEGRATION=true
            ;;
        --coverage)
            COVERAGE=true
            ;;
        --html)
            HTML_REPORT=true
            COVERAGE=true
            ;;
        --verbose)
            VERBOSE="-v"
            ;;
        --file=*)
            SPECIFIC_FILE="${arg#*=}"
            ;;
        --mark=*)
            SPECIFIC_MARK="${arg#*=}"
            ;;
        --no-cov)
            NO_COV=true
            ;;
        --watch)
            WATCH_MODE=true
            ;;
        --lint)
            RUN_LINT=true
            ;;
        --format)
            FORMAT_CODE=true
            ;;
        *)
            echo -e "${YELLOW}警告: 未知选项 $arg${NC}"
            ;;
    esac
done

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}警告: 未检测到虚拟环境${NC}"
    echo -e "${BLUE}尝试激活虚拟环境...${NC}"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}错误: 未找到虚拟环境。请先运行 './run.sh --install-only'${NC}"
        exit 1
    fi
fi

# 安装测试依赖
if [ ! -f ".test_deps_installed" ]; then
    echo -e "${BLUE}安装测试依赖...${NC}"
    pip install -r requirements-test.txt
    touch .test_deps_installed
fi

# 格式化代码
if [ "$FORMAT_CODE" = true ]; then
    echo -e "${BLUE}格式化代码...${NC}"
    black app tests --line-length 100
    isort app tests --profile black
    echo -e "${GREEN}代码格式化完成！${NC}"
    exit 0
fi

# 运行代码检查
if [ "$RUN_LINT" = true ]; then
    echo -e "${BLUE}运行代码检查...${NC}"

    echo -e "\n${YELLOW}运行 Black 检查...${NC}"
    black --check app tests --line-length 100

    echo -e "\n${YELLOW}运行 isort 检查...${NC}"
    isort --check-only app tests --profile black

    echo -e "\n${YELLOW}运行 Flake8...${NC}"
    flake8 app tests --max-line-length 100 --exclude=__pycache__

    echo -e "\n${YELLOW}运行 MyPy...${NC}"
    mypy app --ignore-missing-imports

    echo -e "\n${GREEN}代码检查完成！${NC}"
    exit 0
fi

# 构建pytest命令
PYTEST_CMD="pytest"

# 添加详细输出
if [ "$VERBOSE" != "" ]; then
    PYTEST_CMD="$PYTEST_CMD $VERBOSE"
fi

# 添加特定文件
if [ "$SPECIFIC_FILE" != "" ]; then
    PYTEST_CMD="$PYTEST_CMD $SPECIFIC_FILE"
else
    # 添加标记过滤
    MARKS=""
    if [ "$RUN_UNIT" = true ] && [ "$RUN_INTEGRATION" = false ]; then
        MARKS="unit"
    elif [ "$RUN_UNIT" = false ] && [ "$RUN_INTEGRATION" = true ]; then
        MARKS="integration"
    fi

    if [ "$SPECIFIC_MARK" != "" ]; then
        if [ "$MARKS" != "" ]; then
            MARKS="$MARKS and $SPECIFIC_MARK"
        else
            MARKS="$SPECIFIC_MARK"
        fi
    fi

    if [ "$MARKS" != "" ]; then
        PYTEST_CMD="$PYTEST_CMD -m \"$MARKS\""
    fi
fi

# 添加覆盖率选项
if [ "$COVERAGE" = true ] && [ "$NO_COV" = false ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=term-missing"

    if [ "$HTML_REPORT" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=html"
    fi
fi

# 监视模式
if [ "$WATCH_MODE" = true ]; then
    echo -e "${BLUE}启动监视模式...${NC}"
    echo -e "${YELLOW}按 Ctrl+C 退出${NC}"

    # 安装 pytest-watch 如果没有
    pip install pytest-watch

    ptw -- $PYTEST_CMD
else
    # 运行测试
    echo -e "${BLUE}运行测试...${NC}"
    echo -e "${YELLOW}命令: $PYTEST_CMD${NC}\n"

    eval $PYTEST_CMD
    TEST_RESULT=$?

    # 显示结果
    if [ $TEST_RESULT -eq 0 ]; then
        echo -e "\n${GREEN}✓ 所有测试通过！${NC}"

        if [ "$HTML_REPORT" = true ]; then
            echo -e "${BLUE}HTML覆盖率报告已生成: htmlcov/index.html${NC}"
            # 尝试在浏览器中打开报告
            if command -v open &> /dev/null; then
                open htmlcov/index.html
            elif command -v xdg-open &> /dev/null; then
                xdg-open htmlcov/index.html
            fi
        fi
    else
        echo -e "\n${RED}✗ 测试失败！${NC}"
        exit $TEST_RESULT
    fi
fi

# 清理
rm -f .coverage.*