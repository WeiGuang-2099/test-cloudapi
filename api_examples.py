#!/usr/bin/env python3
"""
API 调用示例集合
展示各种调用 Cloud Run API 的方法
"""

import requests
import json
import asyncio
import aiohttp

# 替换为你的 Cloud Run API URL
API_URL = "https://your-service-url.run.app"


def example_1_basic_call():
    """示例 1: 基础的同步调用"""
    print("=" * 50)
    print("示例 1: 基础调用")
    print("=" * 50)
    
    response = requests.post(
        f"{API_URL}/parse",
        json={
            "text": "Hello World",
            "format": "json"
        }
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    print()


def example_2_with_error_handling():
    """示例 2: 带错误处理的调用"""
    print("=" * 50)
    print("示例 2: 错误处理")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{API_URL}/parse",
            json={"text": "测试文本"},
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            print("✅ 成功:", result.get("message"))
            print(f"数据: {result.get('data')}")
        else:
            print("❌ 失败:", result.get("message"))
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")
    print()


def example_3_batch_processing():
    """示例 3: 批量处理多个文本"""
    print("=" * 50)
    print("示例 3: 批量处理")
    print("=" * 50)
    
    texts_to_parse = [
        "第一段文本",
        "第二段文本",
        '{"key": "JSON数据"}',
        "最后一段文本"
    ]
    
    results = []
    for i, text in enumerate(texts_to_parse, 1):
        print(f"处理第 {i}/{len(texts_to_parse)} 条...")
        
        response = requests.post(
            f"{API_URL}/parse",
            json={"text": text}
        )
        
        if response.status_code == 200:
            results.append(response.json())
            print(f"  ✅ 成功")
        else:
            print(f"  ❌ 失败: {response.status_code}")
    
    print(f"\n总共处理: {len(texts_to_parse)} 条")
    print(f"成功: {len(results)} 条")
    print()


async def example_4_async_call():
    """示例 4: 异步调用（适合大量请求）"""
    print("=" * 50)
    print("示例 4: 异步调用")
    print("=" * 50)
    
    async def parse_async(session, text):
        async with session.post(
            f"{API_URL}/parse",
            json={"text": text}
        ) as response:
            return await response.json()
    
    texts = [f"文本 {i}" for i in range(5)]
    
    async with aiohttp.ClientSession() as session:
        tasks = [parse_async(session, text) for text in texts]
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results, 1):
            print(f"结果 {i}: {result.get('message')}")
    
    print()


def example_5_with_retry():
    """示例 5: 带重试机制的调用"""
    print("=" * 50)
    print("示例 5: 重试机制")
    print("=" * 50)
    
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,  # 最多重试 3 次
        backoff_factor=1,  # 重试间隔递增
        status_forcelist=[429, 500, 502, 503, 504],  # 这些状态码会触发重试
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    try:
        response = session.post(
            f"{API_URL}/parse",
            json={"text": "重试测试"},
            timeout=10
        )
        print(f"✅ 请求成功: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 所有重试都失败: {e}")
    
    print()


def example_6_streaming_results():
    """示例 6: 处理大量数据并保存结果"""
    print("=" * 50)
    print("示例 6: 批量处理并保存")
    print("=" * 50)
    
    # 模拟大量文本数据
    texts = [f"文本数据 {i}" for i in range(10)]
    
    results = []
    for i, text in enumerate(texts, 1):
        response = requests.post(
            f"{API_URL}/parse",
            json={"text": text}
        )
        
        if response.status_code == 200:
            results.append(response.json())
            
        # 显示进度
        progress = (i / len(texts)) * 100
        print(f"进度: {progress:.1f}% ({i}/{len(texts)})")
    
    # 保存结果到文件
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 结果已保存到 results.json")
    print()


def example_7_with_custom_headers():
    """示例 7: 使用自定义请求头（如 API 密钥）"""
    print("=" * 50)
    print("示例 7: 自定义请求头")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "your-api-key-here",  # 如果 API 需要密钥
        "User-Agent": "MyApp/1.0",
    }
    
    response = requests.post(
        f"{API_URL}/parse",
        json={"text": "带自定义头的请求"},
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()


class ParseAPIClient:
    """示例 8: 封装成类以便重用"""
    
    def __init__(self, api_url, api_key=None, timeout=30):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def parse(self, text, format="json"):
        """调用解析 API"""
        response = self.session.post(
            f"{self.api_url}/parse",
            json={"text": text, "format": format},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self):
        """健康检查"""
        response = self.session.get(
            f"{self.api_url}/health",
            timeout=self.timeout
        )
        return response.json()
    
    def close(self):
        """关闭会话"""
        self.session.close()


def example_8_api_client():
    """使用 API 客户端类"""
    print("=" * 50)
    print("示例 8: API 客户端类")
    print("=" * 50)
    
    # 创建客户端
    client = ParseAPIClient(API_URL)
    
    try:
        # 健康检查
        health = client.health_check()
        print(f"健康状态: {health}")
        
        # 解析文本
        result = client.parse("使用客户端类调用")
        print(f"解析结果: {result}")
        
    finally:
        client.close()
    
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 50)
    print("Cloud Run API 调用示例集合")
    print("=" * 50 + "\n")
    
    print(f"API URL: {API_URL}")
    print(f"请确保已将上面的 URL 替换为你的实际 Cloud Run URL\n")
    
    # 运行各个示例
    try:
        example_1_basic_call()
        example_2_with_error_handling()
        example_3_batch_processing()
        
        # 异步示例需要特殊处理
        print("=" * 50)
        print("示例 4: 异步调用")
        print("=" * 50)
        try:
            asyncio.run(example_4_async_call())
        except Exception as e:
            print(f"异步示例跳过 (需要 aiohttp): {e}\n")
        
        example_5_with_retry()
        example_6_streaming_results()
        example_7_with_custom_headers()
        example_8_api_client()
        
    except Exception as e:
        print(f"\n❌ 运行示例时出错: {e}")
        print("请确保:")
        print("1. API_URL 已正确设置")
        print("2. Cloud Run 服务正在运行")
        print("3. 已安装必要的依赖: pip install requests aiohttp")
    
    print("=" * 50)
    print("所有示例运行完毕！")
    print("=" * 50)


if __name__ == "__main__":
    main()
