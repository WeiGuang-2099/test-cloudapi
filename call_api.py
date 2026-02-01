#!/usr/bin/env python3
"""
Cloud Run API 调用脚本
使用方法: python call_api.py [API_URL]
"""

import requests
import json
import sys

def call_parse_api(api_url, text_to_parse, output_format="json"):
    """
    调用解析 API
    
    参数:
    - api_url: API 的基础 URL
    - text_to_parse: 要解析的文本
    - output_format: 输出格式
    """
    
    # 构建完整的端点 URL
    endpoint = f"{api_url.rstrip('/')}/parse"
    
    # 准备请求数据
    payload = {
        "text": text_to_parse,
        "format": output_format
    }
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"正在调用 API: {endpoint}")
        print(f"请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        print("-" * 50)
        
        # 发送 POST 请求
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        print("✅ API 调用成功！")
        print("\n响应结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API 调用失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"错误详情: {e.response.text}")
        return None

def check_health(api_url):
    """检查 API 健康状态"""
    try:
        response = requests.get(f"{api_url.rstrip('/')}/health", timeout=10)
        response.raise_for_status()
        print(f"✅ API 健康检查通过: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API 健康检查失败: {e}")
        return False

def main():
    # 从命令行参数获取 API URL，或使用默认值
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    else:
        api_url = input("请输入 Cloud Run API URL: ").strip()
    
    if not api_url:
        print("错误: 未提供 API URL")
        sys.exit(1)
    
    print("=" * 50)
    print("Cloud Run API 测试脚本")
    print("=" * 50)
    print()
    
    # 1. 健康检查
    print("1. 执行健康检查...")
    if not check_health(api_url):
        print("健康检查失败，请检查 API 是否正常运行")
        sys.exit(1)
    print()
    
    # 2. 测试文本解析
    print("2. 测试文本解析...")
    test_text = """这是一段测试文本。
    包含多行内容。
    用于测试 API 的解析功能。"""
    
    result = call_parse_api(api_url, test_text)
    print()
    
    # 3. 测试 JSON 解析
    print("3. 测试 JSON 解析...")
    json_text = '{"name": "测试", "value": 123, "items": ["a", "b", "c"]}'
    
    result = call_parse_api(api_url, json_text, "json")
    print()
    
    print("=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
