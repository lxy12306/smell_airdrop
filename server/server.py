#!/usr/bin/env python3
"""
Airdrop Server - 文件传输服务器
支持文件上传下载，类似OSS服务
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import hashlib
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('airdrop_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AirdropServer:
    def __init__(self, root_dir: str, host: str = '0.0.0.0', port: int = 8888, max_file_size: int = 500):
        self.root_dir = Path(root_dir).resolve()
        self.host = host
        self.port = port
        self.max_file_size = max_file_size * 1024 * 1024  # MB to bytes
        
        # 创建根目录
        self.root_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化Flask应用
        self.app = Flask(__name__)
        self.app.config['MAX_CONTENT_LENGTH'] = self.max_file_size
        
        # 注册路由
        self._register_routes()
        
        logger.info(f"Airdrop Server initialized with root: {self.root_dir}")
    
    def _register_routes(self):
        """注册所有路由"""
        
        @self.app.route('/api/info', methods=['GET'])
        def server_info():
            """获取服务器信息"""
            return jsonify({
                'status': 'running',
                'root_dir': str(self.root_dir),
                'max_file_size_mb': self.max_file_size // (1024 * 1024),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/upload', methods=['POST'])
        def upload_file():
            """上传文件"""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                # 获取目标路径
                target_path = request.form.get('path', '')
                if not target_path:
                    return jsonify({'error': 'No target path provided'}), 400
                
                # 安全化文件名和路径
                filename = secure_filename(file.filename)
                if not filename:
                    return jsonify({'error': 'Invalid filename'}), 400
                
                # 构建完整路径
                full_path = self.root_dir / target_path.strip('/')
                full_path.mkdir(parents=True, exist_ok=True)
                file_path = full_path / filename
                
                # 检查是否覆盖
                overwrite = request.form.get('overwrite', 'false').lower() == 'true'
                if file_path.exists() and not overwrite:
                    return jsonify({
                        'error': 'File already exists',
                        'path': str(file_path.relative_to(self.root_dir))
                    }), 409
                
                # 保存文件
                file.save(str(file_path))
                
                # 计算文件哈希
                file_hash = self._calculate_file_hash(file_path)
                file_size = file_path.stat().st_size
                
                logger.info(f"File uploaded: {file_path.relative_to(self.root_dir)}")
                
                return jsonify({
                    'message': 'File uploaded successfully',
                    'path': str(file_path.relative_to(self.root_dir)),
                    'filename': filename,
                    'size': file_size,
                    'hash': file_hash,
                    'timestamp': datetime.now().isoformat()
                })
                
            except RequestEntityTooLarge:
                return jsonify({'error': 'File too large'}), 413
            except Exception as e:
                logger.error(f"Upload error: {str(e)}")
                return jsonify({'error': f'Upload failed: {str(e)}'}), 500
        
        @self.app.route('/api/download/<path:file_path>', methods=['GET'])
        def download_file(file_path):
            """下载文件"""
            try:
                full_path = self.root_dir / file_path.strip('/')
                
                if not full_path.exists():
                    abort(404, description='File not found')
                
                if not full_path.is_file():
                    abort(400, description='Path is not a file')
                
                # 检查路径是否在根目录内（安全检查）
                try:
                    full_path.resolve().relative_to(self.root_dir.resolve())
                except ValueError:
                    abort(403, description='Access denied')
                
                logger.info(f"File downloaded: {file_path}")
                return send_file(str(full_path), as_attachment=True)
                
            except Exception as e:
                logger.error(f"Download error: {str(e)}")
                abort(500, description=f'Download failed: {str(e)}')
        
        @self.app.route('/api/list', methods=['GET'])
        @self.app.route('/api/list/<path:dir_path>', methods=['GET'])
        def list_files(dir_path=''):
            """列出目录文件"""
            try:
                target_dir = self.root_dir / dir_path.strip('/')
                
                if not target_dir.exists():
                    return jsonify({'error': 'Directory not found'}), 404
                
                if not target_dir.is_dir():
                    return jsonify({'error': 'Path is not a directory'}), 400
                
                # 检查路径是否在根目录内
                try:
                    target_dir.resolve().relative_to(self.root_dir.resolve())
                except ValueError:
                    return jsonify({'error': 'Access denied'}), 403
                
                items = []
                for item in sorted(target_dir.iterdir()):
                    rel_path = item.relative_to(self.root_dir)
                    item_info = {
                        'name': item.name,
                        'path': str(rel_path),
                        'type': 'directory' if item.is_dir() else 'file',
                        'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    }
                    
                    if item.is_file():
                        item_info['size'] = str(item.stat().st_size)
                    
                    items.append(item_info)
                
                return jsonify({
                    'path': dir_path,
                    'items': items,
                    'total': len(items)
                })
                
            except Exception as e:
                logger.error(f"List error: {str(e)}")
                return jsonify({'error': f'List failed: {str(e)}'}), 500
        
        @self.app.route('/api/delete/<path:file_path>', methods=['DELETE'])
        def delete_file(file_path):
            """删除文件"""
            try:
                full_path = self.root_dir / file_path.strip('/')
                
                if not full_path.exists():
                    return jsonify({'error': 'File not found'}), 404
                
                # 检查路径是否在根目录内
                try:
                    full_path.resolve().relative_to(self.root_dir.resolve())
                except ValueError:
                    return jsonify({'error': 'Access denied'}), 403
                
                if full_path.is_file():
                    full_path.unlink()
                    logger.info(f"File deleted: {file_path}")
                    return jsonify({'message': 'File deleted successfully'})
                elif full_path.is_dir():
                    # 检查是否为空目录
                    if any(full_path.iterdir()):
                        return jsonify({'error': 'Directory not empty'}), 400
                    full_path.rmdir()
                    logger.info(f"Directory deleted: {file_path}")
                    return jsonify({'message': 'Directory deleted successfully'})
                else:
                    return jsonify({'error': 'Invalid path'}), 400
                    
            except Exception as e:
                logger.error(f"Delete error: {str(e)}")
                return jsonify({'error': f'Delete failed: {str(e)}'}), 500
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件MD5哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def run(self, debug: bool = False):
        """启动服务器"""
        logger.info(f"Starting Airdrop Server on {self.host}:{self.port}")
        logger.info(f"Root directory: {self.root_dir}")
        
        try:
            self.app.run(host=self.host, port=self.port, debug=debug, threaded=True)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Airdrop Server - 文件传输服务器')
    parser.add_argument('root_dir', help='Root directory for file storage')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8888, help='Port to bind to (default: 8888)')
    parser.add_argument('--max-size', type=int, default=500, help='Maximum file size in MB (default: 500)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # 检查根目录
    root_path = Path(args.root_dir)
    if not root_path.exists():
        try:
            root_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created root directory: {root_path}")
        except Exception as e:
            logger.error(f"Failed to create root directory: {e}")
            sys.exit(1)
    
    # 启动服务器
    server = AirdropServer(
        root_dir=args.root_dir,
        host=args.host,
        port=args.port,
        max_file_size=args.max_size
    )
    
    server.run(debug=args.debug)

if __name__ == '__main__':
    main()