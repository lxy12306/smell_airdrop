#!/bin/sh

# Configuration
# Use $0 instead of BASH_SOURCE for POSIX compatibility
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="Airdrop"
INSTALL_ROOT="$HOME/.local/share/Airdrop"
BIN_DIR="$HOME/.local/bin"
SHORTCUT_PATH="$BIN_DIR/ad"

# Source Directories
SRC_CLIENT="$SCRIPT_DIR/client"
SRC_SERVER="$SCRIPT_DIR/server"
SRC_OSS="$SCRIPT_DIR/oss"
SRC_WRAPPER="$SCRIPT_DIR/wrappers/ad"
SRC_REQ="$SCRIPT_DIR/requirements.txt"

# Destination Directories
DST_PYTHON="$INSTALL_ROOT/python"
DST_CLIENT="$INSTALL_ROOT/client"
DST_SERVER="$INSTALL_ROOT/server"
DST_OSS="$INSTALL_ROOT/oss"
DST_PYTHON_EXE="$DST_PYTHON/bin/python3"
DST_CLIENT_SCRIPT="$DST_CLIENT/client.py"

# Pack Function
do_pack() {
    echo "[INFO] Updating Python Package (Pack Mode)..."

    # 1. Determine Archive Name (Same logic as install)
    # We assume we are packing for the current OS/Arch if not specified
    # But usually this script runs on the dev machine.
    # Let's assume we are maintaining the archive for the CURRENT platform or specific mapped folders.
    
    # Check if we have specific folder "python_linux_x86" or similar?
    # For now, let's just support the structure we defined: SRC_PYTHON
    
    # We need to re-evaluate SRC_PYTHON based on logic or use what was set?
    # The top logic set SRC_PYTHON based on uname. 
    # If we are packing, we want to pack what we have.
    
    local _target_dir=$(basename "$SRC_PYTHON")
    echo "[INFO] Target Python Directory: $_target_dir, Archive: $SRC_PYTHON"
    
    if [ ! -d "$SRC_PYTHON" ]; then
        if [ -f "$SRC_PYTHON_ARCHIVE" ]; then
             echo "[INFO] Extracting archive $SRC_PYTHON_ARCHIVE..."
             case "$SRC_PYTHON_ARCHIVE" in
                *.tar.gz) tar -xzf "$SRC_PYTHON_ARCHIVE" -C "$SCRIPT_DIR" ;;
                *.tar.xz) tar -xf "$SRC_PYTHON_ARCHIVE" -C "$SCRIPT_DIR" ;;
            esac
            _CLEANUP_PYTHON=1
        else
             echo "[ERROR] No python source directory or archive found."
             exit 1
        fi
    fi
    
    # 2. Pip Install
    echo "[INFO] Installing requirements..."
    if [ -f "$SRC_REQ" ]; then
        "$SRC_PYTHON/bin/python3" -m pip install -r "$SRC_REQ" --no-warn-script-location >/dev/null 2>&1
    fi
    
    # 3. Cleanup
    echo "[INFO] Cleaning up pycache..."
    find "$SRC_PYTHON" -type d -name "__pycache__" -exec rm -rf {} +
    find "$SRC_PYTHON" -type f -name "*.pyc" -delete
    
    # 4. Repack
    echo "[INFO] Repacking to $SRC_PYTHON_ARCHIVE..."
    if [ -f "$SRC_PYTHON_ARCHIVE" ]; then
        mv "$SRC_PYTHON_ARCHIVE" "${SRC_PYTHON_ARCHIVE}.bak"
    fi
    
    # Identify compression
    case "$SRC_PYTHON_ARCHIVE" in
        *.tar.gz) tar -czf "$SRC_PYTHON_ARCHIVE" -C "$SCRIPT_DIR" "$_target_dir" ;;
        *.tar.xz) 
            echo "[INFO] Compressing with xz (-9e -T0)..."
            XZ_OPT="-9e -T0" tar -cJf "$SRC_PYTHON_ARCHIVE" -C "$SCRIPT_DIR" "$_target_dir" 
            ;;
    esac
    

    # 5. Cleanup if we extracted it
    if [ "$_CLEANUP_PYTHON" = "1" ]; then
        echo "[INFO] Cleaning up extracted Python environment..."
        rm -rf "$SRC_PYTHON"
    fi
    echo "[SUCCESS] Updated $SRC_PYTHON_ARCHIVE"
}

# OS and Architecture Detection
OS_TYPE=$(uname -s)
ARCH_TYPE=$(uname -m)

if [ "$OS_TYPE" = "Darwin" ]; then
    SRC_PYTHON="$SCRIPT_DIR/python_mac"
    SRC_PYTHON_ARCHIVE="${SRC_PYTHON}.tar.gz"
else
    # Linux
    if [ "$ARCH_TYPE" = "x86_64" ]; then
        SRC_PYTHON="$SCRIPT_DIR/python_linux_x86"
        SRC_PYTHON_ARCHIVE="$SCRIPT_DIR/python_linux_x86.tar.xz"
    elif [ "$ARCH_TYPE" = "aarch64" ] || [ "$ARCH_TYPE" = "arm64" ]; then
        echo "[ERROR] ARM architecture ($ARCH_TYPE) is not currently supported."
        exit 1
    else
        # Default fallback
        SRC_PYTHON="$SCRIPT_DIR/python_linux"
        SRC_PYTHON_ARCHIVE="${SRC_PYTHON}.tar.gz"
    fi
fi

if [ "$1" = "pack" ]; then
    do_pack
    exit 0
fi

# Helper function to process a single config file
# Arguments: $1=file_path, $2=action, $3=bin_path
process_config_file() {
    _config_file="$1"
    _action="$2"
    _bin_dir="$3"
    
    # Define the exact line we add/remove
    _path_line='export PATH="$PATH:'"$_bin_dir"'"'
    
    if [ ! -f "$_config_file" ]; then
        return
    fi
    
    if [ "$_action" = "install" ]; then
        # Check if file contains the bin_dir path
        # Using grep -F for fixed string search
        if grep -Fq "$_bin_dir" "$_config_file"; then
             echo "  [SKIP] $_config_file (already contains path)"
        else
             echo "" >> "$_config_file"
             echo "# Added by Airdrop installer" >> "$_config_file"
             echo "$_path_line" >> "$_config_file"
             echo "  [UPDATED] $_config_file"
        fi
    elif [ "$_action" = "uninstall" ]; then
         # Check if the exact line exists before trying to remove
         if grep -Fq "$_path_line" "$_config_file"; then
             # Use a temporary file for sed-like behavior
             _temp_file=$(mktemp)
             # Remove the export line and the comment
             grep -vF "$_path_line" "$_config_file" | grep -v "# Added by Airdrop installer" > "$_temp_file"
             mv "$_temp_file" "$_config_file"
             echo "  [CLEANED] $_config_file"
         fi
    fi
}

update_shell_config() {
    _act="$1"
    echo "[INFO] Managing PATH in shell configuration files ($_act)..."
    
    # Process common shell config files manually (no arrays)
    process_config_file "$HOME/.bashrc" "$_act" "$BIN_DIR"
    process_config_file "$HOME/.zshrc" "$_act" "$BIN_DIR"
    process_config_file "$HOME/.bash_profile" "$_act" "$BIN_DIR"
    process_config_file "$HOME/.profile" "$_act" "$BIN_DIR"
}

do_install() {
    echo "[INFO] Installing $APP_NAME..."

    # 1. Check Python Source
    if [ ! -d "$SRC_PYTHON" ]; then
        if [ -f "$SRC_PYTHON_ARCHIVE" ]; then
            echo "[INFO] Extracting $(basename "$SRC_PYTHON_ARCHIVE")..."
            # Check file extension to permit .tar.gz or .tar.xz
            case "$SRC_PYTHON_ARCHIVE" in
                *.tar.gz) tar -xzf "$SRC_PYTHON_ARCHIVE" -C "$SCRIPT_DIR" ;;
                *.tar.xz) tar -xf "$SRC_PYTHON_ARCHIVE" -C "$SCRIPT_DIR" ;;
                *) echo "[WARNING] Unknown archive format: $SRC_PYTHON_ARCHIVE" ;;
            esac
            _CLEANUP_PYTHON=1
        fi
    fi

    # Check again
    if [ ! -d "$SRC_PYTHON" ] || [ ! -x "$SRC_PYTHON/bin/python3" ]; then
        echo "[WARNING] Embedded Python not found or invalid at: $SRC_PYTHON"
        echo "Will attempt to use system 'python3' as fallback."
        DST_PYTHON_EXE="python3"
    else
         # 2. Copy Python Environment
        echo "[INFO] Copying Python environment..."
        mkdir -p "$INSTALL_ROOT"
        rm -rf "$DST_PYTHON"
        cp -r "$SRC_PYTHON" "$DST_PYTHON"
        DST_PYTHON_EXE="$DST_PYTHON/bin/python3"
    fi

    # 3. Copy Client Code
    echo "[INFO] Copying Client code..."
    mkdir -p "$DST_CLIENT"
    cp -r "$SRC_CLIENT/"* "$DST_CLIENT/"

    # Copy Server Code
    echo "[INFO] Copying Server code..."
    mkdir -p "$DST_SERVER"
    cp -r "$SRC_SERVER/"* "$DST_SERVER/"

    # Copy OSS Code
    echo "[INFO] Copying OSS tools..."
    mkdir -p "$DST_OSS"
    cp -r "$SRC_OSS/"* "$DST_OSS/"
    # Remove .env if it was copied
    rm -f "$DST_OSS/.env"

    # 4. Install Dependencies
    if [ -f "$SRC_REQ" ]; then
        echo "[INFO] Installing dependencies..."
        cp "$SRC_REQ" "$INSTALL_ROOT/"
        # Try to install if we are using embedded python or if user wants us to
        # Note: quiet install
        "$DST_PYTHON_EXE" -m pip install -r "$INSTALL_ROOT/requirements.txt" --no-warn-script-location >/dev/null 2>&1
    fi

    # 5. Create Shortcut
    echo "[INFO] Installing wrapper script..."
    mkdir -p "$BIN_DIR"
    
    # Use tr to ensure Unix line endings (LF) even if source is Windows (CRLF)
    cat "$SRC_WRAPPER" | tr -d '\r' > "$SHORTCUT_PATH"
    chmod +x "$SHORTCUT_PATH"
    echo "  [SUCCESS] Created: $SHORTCUT_PATH"

    # 6. Update PATH
    update_shell_config "install"

    # 7. Cleanup extracted Python
    if [ "$_CLEANUP_PYTHON" = "1" ]; then
        echo "[INFO] Cleaning up extracted Python environment..."
        rm -rf "$SRC_PYTHON"
    fi

    echo ""
    echo "[DONE] Installation complete!"
    echo "You may need to restart your terminal or run 'source ~/.bashrc' (or ~/.zshrc) to use 'ad'."
}

do_uninstall() {
    echo "[INFO] Uninstalling $APP_NAME..."

    # 1. Remove Shortcut
    if [ -f "$SHORTCUT_PATH" ]; then
        rm "$SHORTCUT_PATH"
        echo "  [REMOVED] $SHORTCUT_PATH"
    fi

    # 2. Remove Install Directory
    if [ -d "$INSTALL_ROOT" ]; then
        rm -rf "$INSTALL_ROOT"
        echo "  [REMOVED] $INSTALL_ROOT"
    fi

    # 3. Clean PATH from Config
    update_shell_config "uninstall"

    echo ""
    echo "[DONE] Uninstallation complete."
    echo "Note: If you still see 'No such file or directory' when running 'ad', it is because your shell"
    echo "has cached the command location. Run 'hash -r' (bash) or restart your terminal to fix it."
}

show_help() {
    echo "Usage: $0 {install|uninstall|help}"
    echo ""
    echo "Commands:"
    echo "  install    Install Airdrop client and dependencies"
    echo "  uninstall  Remove Airdrop client"
    echo "  help       Show this help message"
}

# Main Dispatch
# Case structure is POSIX compliant
case "$1" in
    uninstall)
        do_uninstall
        ;;
    help|--help|-h)
        show_help
        ;;
    install|"")
        do_install
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
