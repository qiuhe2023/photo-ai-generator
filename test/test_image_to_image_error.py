import requests
import json
import time
from urllib.parse import urljoin

# 测试配置
BASE_URL = "http://localhost:5002"
API_ENDPOINT = "/api/image-to-image"

# 创建一个会导致生成失败的测试数据（使用无效的图片URL）
def test_image_to_image_error():
    print("开始测试图生图API错误处理...")
    
    # 使用无效的图片URL来模拟生成失败的情况
    test_data = {
        "image_url": "https://invalid-url-that-will-cause-error.com/nonexistent.jpg",
        "prompt": "这是一个测试提示词",
        "negative_prompt": "模糊，扭曲，低质量",
        "steps": 30,
        "creative_strength": 0.7,
        "model": "doubao-seedream-4-0-250828",
        "size": "2K",
        "num_images": 1,
        "watermark": True
    }
    
    print(f"测试数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print(f"\n正在发送POST请求到: {urljoin(BASE_URL, API_ENDPOINT)}")
    print("Content-Type: application/json")
    
    start_time = time.time()
    try:
        # 发送POST请求
        response = requests.post(
            urljoin(BASE_URL, API_ENDPOINT),
            json=test_data,
            timeout=180  # 增加超时时间以确保有足够时间处理
        )
        
        request_time = time.time() - start_time
        print(f"请求耗时: {request_time:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        
        # 尝试解析JSON响应
        try:
            response_data = response.json()
            print(f"响应内容: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 验证错误处理是否正确
            if response_data.get('success') is False and 'error' in response_data:
                print("✅ 错误处理验证成功! API正确返回了错误状态和信息")
                return True
            else:
                print("❌ 错误处理验证失败! API没有正确返回错误状态和信息")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {str(e)}")
            print(f"原始响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_image_to_image_error()
    if success:
        print("\n测试成功完成")
        exit(0)
    else:
        print("\n测试失败")
        exit(1)