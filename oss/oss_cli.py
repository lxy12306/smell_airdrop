#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OSS Command Line Interface
基于阿里云 OSS 的命令行文件管理工具
"""

import os
import sys
import argparse
import oss2
from dotenv import load_dotenv, set_key

# 加载环境变量
# 首先尝试加载当前目录下的 .env
load_dotenv()
# 如果没有，尝试加载脚本所在目录下的 .env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # 确保 .env 文件存在，以便后续写入
    with open(env_path, 'w') as f:
        pass

def get_bucket():
    """获取并初始化 Bucket 对象"""
    access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
    access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
    endpoint = os.getenv('OSS_ENDPOINT', 'http://oss-cn-hangzhou.aliyuncs.com')
    bucket_name = os.getenv('OSS_BUCKET_NAME', 'smell')

    if not access_key_id or not access_key_secret:
        print("❌ 错误: 未找到 OSS_ACCESS_KEY_ID 或 OSS_ACCESS_KEY_SECRET 环境变量。")
        print(f"请检查 .env 文件配置。搜索路径包含: {os.getcwd()} 和 {script_dir}")
        sys.exit(1)

    try:
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        return bucket
    except Exception as e:
        print(f"❌ 初始化 OSS 客户端失败: {str(e)}")
        sys.exit(1)

def format_size(size_bytes):
    """格式化文件大小"""
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"

def cmd_upload(args):
    """处理上传命令"""
    local_path = args.local_file
    # 如果未指定远程路径，使用本地文件名
    remote_path = args.remote_file if args.remote_file else os.path.basename(local_path)
    
    if not os.path.exists(local_path):
        print(f"❌ 本地文件不存在: {local_path}")
        return

    bucket = get_bucket()
    try:
        print(f"🚀 正在上传: {local_path} -> {remote_path}")
        bucket.put_object_from_file(remote_path, local_path)
        print(f"✅ 上传成功")
    except Exception as e:
        print(f"❌ 上传失败: {str(e)}")

def cmd_download(args):
    """处理下载命令"""
    remote_path = args.remote_file
    # 如果未指定本地路径，使用远程文件名
    local_path = args.local_file if args.local_file else os.path.basename(remote_path)
    
    bucket = get_bucket()
    try:
        if not bucket.object_exists(remote_path):
             print(f"❌ 远程文件不存在: {remote_path}")
             return

        print(f"⬇️ 正在下载: {remote_path} -> {local_path}")
        bucket.get_object_to_file(remote_path, local_path)
        print(f"✅ 下载成功")
    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")

def cmd_list(args):
    """处理列举命令"""
    prefix = args.prefix
    bucket = get_bucket()
    
    print(f"📋 列出文件 (前缀: '{prefix}'):")
    count = 0
    total_size = 0
    
    try:
        for obj in oss2.ObjectIterator(bucket, prefix=prefix):
            print(f"  📄 {obj.key:<30} {format_size(obj.size):>10}  {obj.last_modified}")
            count += 1
            total_size += obj.size
        
        print("\nSUMMARY:")
        print(f"  数量: {count} 个文件")
        print(f"  总大小: {format_size(total_size)}")
        
    except Exception as e:
        print(f"❌获取列表失败: {str(e)}")

def cmd_delete(args):
    """处理删除命令"""
    remote_path = args.remote_path
    
    # 简单的确认机制
    if not args.force:
        confirm = input(f"⚠️ 确定要删除 '{remote_path}' 吗? [y/N]: ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return

    bucket = get_bucket()
    try:
        bucket.delete_object(remote_path)
        print(f"🗑️ 已删除: {remote_path}")
    except Exception as e:
        print(f"❌ 删除失败: {str(e)}")

def cmd_exists(args):
    """检查文件是否存在"""
    remote_path = args.remote_path
    bucket = get_bucket()
    try:
        exists = bucket.object_exists(remote_path)
        if exists:
            print(f"✅ 文件存在: {remote_path}")
        else:
            print(f"🚫 文件不存在: {remote_path}")
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")

def cmd_config(args):
    """处理配置命令"""
    if not (args.id or args.secret or args.endpoint or args.bucket):
        print("未提供任何配置项。请使用 --id, --secret, --endpoint, 或 --bucket")
        return

    try:
        if args.id:
            set_key(env_path, 'OSS_ACCESS_KEY_ID', args.id)
            print(f"✅ OSS_ACCESS_KEY_ID 已更新")
        if args.secret:
            set_key(env_path, 'OSS_ACCESS_KEY_SECRET', args.secret)
            print(f"✅ OSS_ACCESS_KEY_SECRET 已更新")
        if args.endpoint:
            set_key(env_path, 'OSS_ENDPOINT', args.endpoint)
            print(f"✅ OSS_ENDPOINT 已更新")
        if args.bucket:
            set_key(env_path, 'OSS_BUCKET_NAME', args.bucket)
            print(f"✅ OSS_BUCKET_NAME 已更新")
            
        print(f"配置已保存至: {env_path}")
    except Exception as e:
        print(f"❌ 配置更新失败: {str(e)}")

def main():
    description = """OSS 便捷管理工具

【配置说明】
  本工具会自动加载当前目录或脚本所在目录下的 .env 文件。
  
  方法 1: 命令行配置 (推荐)
    ad oss config --id <AccessKeyID> --secret <AccessKeySecret>
    ad oss config --bucket <BucketName> --endpoint <Endpoint>

  方法 2: 手动创建 .env 文件
    OSS_ACCESS_KEY_ID=xxx
    OSS_ACCESS_KEY_SECRET=xxx
    OSS_ENDPOINT=http://oss-cn-hangzhou.aliyuncs.com
    OSS_BUCKET_NAME=smell
"""
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    subparsers.required = True

    # Upload
    p_upload = subparsers.add_parser('put', help='上传文件')
    p_upload.add_argument('local_file', help='本地文件路径')
    p_upload.add_argument('remote_file', nargs='?', help='OSS 路径 (可选，默认同名)')
    # Config
    p_config = subparsers.add_parser('config', help='配置 OSS 鉴权信息')
    p_config.add_argument('--id', help='AccessKey ID')
    p_config.add_argument('--secret', help='AccessKey Secret')
    p_config.add_argument('--endpoint', help='Endpoint (例如: http://oss-cn-hangzhou.aliyuncs.com)')
    p_config.add_argument('--bucket', help='Bucket Name')
    p_config.set_defaults(func=cmd_config)

    p_upload.set_defaults(func=cmd_upload)

    # Download
    p_download = subparsers.add_parser('get', help='下载文件')
    p_download.add_argument('remote_file', help='OSS 文件路径')
    p_download.add_argument('local_file', nargs='?', help='本地保存路径 (可选，默认同名)')
    p_download.set_defaults(func=cmd_download)

    # List
    p_list = subparsers.add_parser('list', help='列出文件')
    p_list.add_argument('prefix', nargs='?', default='', help='文件前缀过滤')
    p_list.set_defaults(func=cmd_list)

    # Delete
    p_delete = subparsers.add_parser('delete', help='删除文件')
    p_delete.add_argument('remote_path', help='OSS 文件路径')
    p_delete.add_argument('-f', '--force', action='store_true', help='不询问直接删除')
    p_delete.set_defaults(func=cmd_delete)

    # Exists
    p_exists = subparsers.add_parser('exists', help='检查文件是否存在')
    p_exists.add_argument('remote_path', help='OSS 文件路径')
    p_exists.set_defaults(func=cmd_exists)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
