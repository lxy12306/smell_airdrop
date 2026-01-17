#!/usr/bin/env python3
"""
Airdrop Client - 文件传输客户端
支持文件上传下载，快速访问远程文件系统
"""

import os
import sys
import argparse
import json
import requests
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict, Any
import shlex
import subprocess
import platform
import fnmatch

class AirdropClient:
    def __init__(self, server_url: str, timeout: int = 30):
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """发送HTTP请求"""
        url = f"{self.server_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        response = self._make_request('GET', '/api/info')
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Server error: {response.status_code}")
    
    def upload_file(self, local_file: str, remote_file: str, overwrite: bool = False) -> Dict[str, Any]:
        """上传文件"""
        local_file = Path(local_file)
        if not local_file.exists():
            raise Exception(f"Local file not found: {local_file}")

        if not local_file.is_file():
            raise Exception(f"Path is not a file: {local_file}")
        
        # 如果 remote_file 存在，则使用 remote_file 的名字，否则使用 local_file 的名字
        # 并通过斜杠区分路径和文件名
        remote_file_path = Path(remote_file) if remote_file else Path(local_file.name)
        remote_file_name = remote_file_path.name  # 提取文件名
        remote_file_dir = remote_file_path.parent  # 提取路径
        
        with open(local_file, 'rb') as f:
            files = {'file': (remote_file_name, f, 'application/octet-stream')}
            data = {
                'path': remote_file_dir,  # 使用 remote_file 的路径
                'overwrite': str(overwrite).lower()
            }
            
            response = self._make_request('POST', '/api/upload', files=files, data=data)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 409:
                raise Exception(f"File already exists (use --overwrite to replace)")
            else:
                try:
                    error_msg = response.json().get('error', 'Unknown error')
                except:
                    error_msg = f"HTTP {response.status_code}"
                raise Exception(f"Upload failed: {error_msg}")
    
    def download_file(self, remote_file: str, local_file: str, overwrite: bool = False) -> None:
        """下载文件"""
        local_file = Path(local_file)

        # 检查本地文件是否存在
        if local_file.exists() and not overwrite:
            raise Exception(f"Local file already exists: {local_file} (use --overwrite to replace)")

        # 创建父目录
        local_file.parent.mkdir(parents=True, exist_ok=True)

        # 编码远程路径
        encoded_path = urllib.parse.quote(str(remote_file), safe='/')
        response = self._make_request('GET', f'/api/download/{encoded_path}')

        if response.status_code == 200:
            with open(local_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            raise Exception(f"Download failed: HTTP {response.status_code}")
    
    def list_files(self, remote_path: str = '') -> Dict[str, Any]:
        """列出远程目录文件"""
        if remote_path:
            encoded_path = urllib.parse.quote(remote_path, safe='/')
            endpoint = f'/api/list/{encoded_path}'
        else:
            endpoint = '/api/list'

        response = self._make_request('GET', endpoint)

        if response.status_code == 200:
            result = response.json()
            # 确保返回值包含必要的字段
            if 'items' not in result:
                result['items'] = []
            if 'path' not in result:
                result['path'] = remote_path
            if 'total' not in result:
                result['total'] = 0
            return result
        else:
            try:
                error_msg = response.json().get('error', 'Unknown error')
            except:
                error_msg = f"HTTP {response.status_code}"
            raise Exception(f"List failed: {error_msg}")
    
    def delete_file(self, remote_path: str) -> Dict[str, Any]:
        """删除远程文件"""
        encoded_path = urllib.parse.quote(remote_path, safe='/')
        response = self._make_request('DELETE', f'/api/delete/{encoded_path}')
        
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_msg = response.json().get('error', 'Unknown error')
            except:
                error_msg = f"HTTP {response.status_code}"
            raise Exception(f"Delete failed: {error_msg}")

class AirdropCLI:
    def __init__(self):
        self.config_file = Path.home() / '.airdrop_config.json'
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 确保配置格式正确
                    if 'servers' not in config:
                        config['servers'] = {}
                    if 'default' not in config['servers']:
                        config['servers']['default'] = {'url': ''}
                    config['default_server'] = 'default'
                    return config
            except:
                pass
        return {'servers': {'default': {'url': ''}}, 'default_server': 'default'}
    
    def _save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _get_client(self, server_name: Optional[str] = None) -> AirdropClient:
        """获取客户端实例"""
        if server_name is None:
            server_name = 'default'  # 默认使用 'default' server
        
        if server_name not in self.config['servers']:
            raise Exception(f"Server '{server_name}' not found in configuration. Please run 'setup' command first.")
        
        server_url = self.config['servers'][server_name]['url']
        if not server_url:
            raise Exception("Default server URL is not configured. Please run 'setup <url>' command first.")
        
        return AirdropClient(server_url)
    
    def setup_server(self, name: str, url: str, set_default: bool = False):
        """设置服务器配置"""
        # 直接设置为默认服务器，而不是添加到服务器列表
        if 'default' not in self.config['servers']:
            self.config['servers']['default'] = {}
        
        self.config['servers']['default']['url'] = url
        self.config['default_server'] = 'default'
        
        self._save_config()
        print(f"Default server configured successfully")
        print(f"Server URL: {url}")
    
    def list_servers(self):
        """列出已配置的服务器"""
        if not self.config['servers'] or 'default' not in self.config['servers']:
            print("No default server configured")
            print("Run 'setup' command to configure the default server")
            return
        
        print("Default server configuration:")
        print(f"  URL: {self.config['servers']['default']['url']}")
    
    def info(self, server: Optional[str] = None):
        """获取服务器信息"""
        client = self._get_client(server)
        try:
            info = client.server_info()
            print(f"Server Status: {info['status']}")
            print(f"Root Directory: {info['root_dir']}")
            print(f"Max File Size: {info['max_file_size_mb']} MB")
            print(f"Server Time: {info['timestamp']}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    def upload(self, local_file: str, remote_file: str, server: Optional[str] = None, overwrite: bool = False):
        """上传文件"""
        client = self._get_client(server)
        try:
            result = client.upload_file(local_file, remote_file, overwrite)
            print(f"Upload successful:")
            print(f"  Local: {local_file}")
            print(f"  Remote: {result['path']}")
            print(f"  Size: {result['size']} bytes")
            print(f"  Hash: {result['hash']}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    def download(self, remote_path: str, local_path: str, server: Optional[str] = None, overwrite: bool = False):
        """下载文件"""
        client = self._get_client(server)
        try:
            client.download_file(remote_path, local_path, overwrite)
            print(f"Download successful:")
            print(f"  Remote: {remote_path}")
            print(f"  Local: {local_path}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    def list_files(self, remote_path: str = '', server: Optional[str] = None):
        """列出文件"""
        client = self._get_client(server)
        try:
            result = client.list_files(remote_path)
            print(f"Directory: /{result['path']}")
            print(f"Total items: {result['total']}")
            print()
            
            if not result['items']:
                print("(empty)")
                return
            
            # 分别显示目录和文件
            dirs = [item for item in result['items'] if item['type'] == 'directory']
            files = [item for item in result['items'] if item['type'] == 'file']
            
            if dirs:
                print("Directories:")
                for item in dirs:
                    print(f"  📁 {item['name']}/")
                print()
            
            if files:
                print("Files:")
                for item in files:
                    size_str = self._format_size(int(item['size'])) if 'size' in item else ""
                    print(f"  📄 {item['name']} {size_str}")
            return result
                    
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    def delete(self, remote_path: str, server: Optional[str] = None):
        """删除文件"""
        client = self._get_client(server)
        try:
            result = client.delete_file(remote_path)
            print(result['message'])
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        size = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"({size:.1f}{unit})"
            size /= 1024.0
        return f"({size:.1f}TB)"

def main():
    parser = argparse.ArgumentParser(description='Airdrop Client - 轻量级文件传输客户端')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # setup命令
    setup_parser = subparsers.add_parser('setup', help='配置默认服务器')
    setup_parser.add_argument('url', help='服务器地址 (例如: http://localhost:8000)')
    setup_parser.add_argument('--default', action='store_true', help='已弃用：现在总是设置为默认服务器')
    
    # servers命令
    subparsers.add_parser('servers', help='显示当前服务器配置')
    
    # info命令
    info_parser = subparsers.add_parser('info', help='显示服务器信息和状态')
    info_parser.add_argument('--server', '-s', help='服务器名称 (可选，默认使用配置的服务器)')
    
    # put命令 (原upload)
    put_parser = subparsers.add_parser('put', help='上传文件到服务器')
    put_parser.add_argument('local_file', help='本地文件路径')
    put_parser.add_argument('remote_file', help='远程保存路径 (例如: images/, data/file.txt)', nargs='?')
    
    # get命令 (原download)
    get_parser = subparsers.add_parser('get', help='从服务器下载文件')
    get_parser.add_argument('remote_file', help='远程文件路径')
    get_parser.add_argument('local_file', help='本地保存路径', nargs='?')
    get_parser.add_argument('--overwrite', action='store_true', help='覆盖已存在的本地文件')
    
    # list命令
    list_parser = subparsers.add_parser('list', help='列出远程目录内容')
    list_parser.add_argument('remote_path', nargs='?', default='', help='远程目录路径 (默认为根目录)')
    
    # delete命令
    delete_parser = subparsers.add_parser('delete', help='删除远程文件')
    delete_parser.add_argument('remote_path', help='要删除的远程文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = AirdropCLI()
    
    try:
        if args.command == 'setup':
            cli.setup_server('default', args.url, args.default)
        elif args.command == 'servers':
            cli.list_servers()
        elif args.command == 'info':
            cli.info(args.server)
        elif args.command == 'put':
            remote_file = args.remote_file if args.remote_file else os.path.basename(args.local_file)
            overwrite = True
            cli.upload(args.local_file, remote_file, None, overwrite)
        elif args.command == 'get':
            # 如果未提供 local_file，则使用 remote_file 的文件名作为默认值
            local_file = args.local_file if args.local_file else os.path.basename(args.remote_file)

            # 默认覆盖文件
            overwrite = True

            # 下载文件
            cli.download(args.remote_file, local_file, None, args.overwrite)
        elif args.command == 'list':
            cli.list_files(args.remote_path, None)
        elif args.command == 'delete':
            # 支持通配符删除
            import fnmatch

            # 获取所有匹配的文件路径
            remote_path_pattern = args.remote_path
            files_response = cli.list_files()
            print(files_response)
            all_files = files_response['items'] if files_response else []  # 确保 list_files 不返回 None
            matching_files = [item['path'] for item in all_files if fnmatch.fnmatch(item['path'], remote_path_pattern)]

            if not matching_files:
                print(f"No files matched the pattern: {remote_path_pattern}")
                return

            print(matching_files)

            # 删除匹配的文件
            for file_path in matching_files:
                cli.delete(file_path, None)
                print(f"Deleted: {file_path}")
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
