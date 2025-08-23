#!/bin/bash
# Airdrop 启动脚本 - Linux/macOS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SERVER_SCRIPT="$SCRIPT_DIR/server/server.py"
CLIENT_SCRIPT="$SCRIPT_DIR/client/client.py"

VENV_DIR="$SCRIPT_DIR/python_linux"
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"

# 默认配置
DEFAULT_ROOT="/tmp/airdrop_storage"
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8888"

show_help() {
    echo "Airdrop 轻量级文件传输系统"
    echo ""
    echo "用法:"
    echo "  $0 server [OPTIONS] <root_directory>  启动文件传输服务器"
    echo "  $0 client [COMMAND] [OPTIONS]         运行客户端操作"
    echo "  $0 install                           安装客户端快捷命令"
    echo ""
    echo "服务器选项:"
    echo "  --host HOST     绑定主机地址 (默认: $DEFAULT_HOST - 所有网卡)"
    echo "  --port PORT     绑定端口号 (默认: $DEFAULT_PORT)"
    echo "  --max-size MB   最大文件大小限制 (默认: 500MB)"
    echo "  --debug         启用详细调试输出"
    echo ""
    echo "客户端命令:"
    echo "  setup URL                配置默认服务器地址"
    echo "  servers                  显示当前服务器配置"
    echo "  info                     查看服务器状态信息"
    echo "  put 本地文件 远程路径      上传文件到服务器"
    echo "  get 远程文件 本地路径      从服务器下载文件"
    echo "  list [远程目录]           列出远程目录内容"
    echo "  delete 远程文件           删除远程文件"
    echo ""
    echo "常用示例:"
    echo "  启动服务器:"
    echo "    $0 server /home/user/files"
    echo "    $0 server --port 9999 /home/user/files"
    echo ""
    echo "  配置客户端:"
    echo "    $0 client setup http://localhost:8888"
    echo "    $0 client servers"
    echo ""
    echo "  文件操作:"
    echo "    $0 client put image.jpg photos/"
    echo "    $0 client get photos/image.jpg downloaded.jpg"
    echo "    $0 client list photos"
    echo "    $0 client delete photos/old_image.jpg"
    echo ""
    echo "  安装快捷命令:"
    echo "    $0 install"
}

start_server() {
    if [ $# -lt 1 ]; then
        echo "错误: 请指定根目录"
        echo "用法: $0 server [OPTIONS] <root_directory>"
        exit 1
    fi
    
    # 解析参数
    ARGS=()
    while [[ $# -gt 0 ]]; do
        case $1 in
            --host)
                ARGS+=("--host" "$2")
                shift 2
                ;;
            --port)
                ARGS+=("--port" "$2")
                shift 2
                ;;
            --max-size)
                ARGS+=("--max-size" "$2")
                shift 2
                ;;
            --debug)
                ARGS+=("--debug")
                shift
                ;;
            -*)
                echo "未知选项: $1"
                exit 1
                ;;
            *)
                ROOT_DIR="$1"
                shift
                ;;
        esac
    done
    
    if [ -z "$ROOT_DIR" ]; then
        echo "错误: 请指定根目录"
        exit 1
    fi
    
    echo "启动 Airdrop 服务器..."
    echo "根目录: $ROOT_DIR"
    source "$ACTIVATE_SCRIPT"
    python "$SERVER_SCRIPT" "$ROOT_DIR" "${ARGS[@]}"
}



run_client() {
    source "$ACTIVATE_SCRIPT"
    python "$CLIENT_SCRIPT" "$@"
}



install_client() {
    source "$ACTIVATE_SCRIPT"
    python "$CLIENT_SCRIPT" install
}

# 主逻辑
case "${1:-help}" in
    server)
        shift
        start_server "$@"
        ;;
    client)
        shift
        run_client "$@"
        ;;
    install)
        install_client
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "未知命令: $1"
        echo "使用 '$0 help' 查看帮助"
        exit 1
        ;;
esac
