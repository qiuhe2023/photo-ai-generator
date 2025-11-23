#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图生图API接口
验证修改后的JSON格式请求是否正常工作
"""

import requests
import json
import time
from bs4 import BeautifulSoup

def test_image_to_image_api():
    """测试/image-to-image API接口"""
    print("开始测试图生图API接口...")
    
    # 创建一个会话来保持cookie
    session = requests.Session()
    
    # 获取CSRF令牌
    print("\n正在获取CSRF令牌...")
    csrf_token = None
    try:
        # 访问首页获取CSRF令牌
        response = session.get("http://localhost:5000/ai_create", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试从meta标签获取CSRF令牌
        meta_token = soup.find('meta', attrs={'name': 'csrf-token'})
        if meta_token:
            csrf_token = meta_token.get('content')
            print(f"从meta标签获取CSRF令牌: {csrf_token[:10]}...")
        else:
            # 尝试从表单隐藏字段获取
            csrf_input = soup.find('input', attrs={'name': 'csrf_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
                print(f"从表单获取CSRF令牌: {csrf_token[:10]}...")
            else:
                print("未找到CSRF令牌，尝试使用cookie中的令牌")
                
        # 如果仍然没有找到，尝试从cookie中获取
        if not csrf_token and 'csrf_token' in session.cookies:
            csrf_token = session.cookies['csrf_token']
            print(f"从cookie获取CSRF令牌: {csrf_token[:10]}...")
            
    except Exception as e:
        print(f"获取CSRF令牌时出错: {str(e)}")
    
    # API端点
    api_url = "http://localhost:5002/api/image-to-image"
    
    # 测试数据 - 使用URL方式
    test_data = {
        "image_url": "https://qiu-he-image1.tos-cn-shanghai.volces.com/photos/b7f5348cf90b48f0abe510ca68e4d4c6.jpg",
        "prompt": "将图片转换为水彩风格",
        "negative_prompt": "模糊，扭曲，低质量",
        "steps": 30,
        "creative_strength": 0.7,
        "model": "doubao-seedream-4-0-250828",
        "size": "2K",
        "num_images": 1,
        "watermark": True
    }
    
    print(f"测试数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        # 准备请求头
        headers = {
            "Content-Type": "application/json",
        }
        
        # 如果有CSRF令牌，添加到请求头
        if csrf_token:
            headers["X-CSRFToken"] = csrf_token
            headers["X-CSRF-Token"] = csrf_token  # 有些框架使用这种格式
            print("已添加CSRF令牌到请求头")
        
        # 发送JSON格式请求
        print(f"\n正在发送POST请求到: {api_url}")
        for key, value in headers.items():
            print(f"{key}: {value}")
        
        start_time = time.time()
        
        response = session.post(
            api_url,
            headers=headers,
            json=test_data,
            timeout=180  # 增加超时时间，因为图像生成可能需要较长时间
        )
        
        end_time = time.time()
        print(f"请求耗时: {end_time - start_time:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        
        # 尝试解析JSON响应
        try:
            response_data = response.json()
            print(f"响应内容: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 检查是否成功
            if response.status_code == 200 and response_data.get('success'):
                print("✅ API调用成功!")
                print(f"生成了 {len(response_data.get('results', []))} 张图片")
                return True
            else:
                print("❌ API调用失败")
                error_msg = response_data.get('error', '未知错误')
                print(f"错误信息: {error_msg}")
                return False
                
        except json.JSONDecodeError:
            print("❌ 无法解析响应为JSON")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络连接或服务器状态")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 请求发生异常: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_image_to_image_api()
    print(f"\n测试{'成功' if success else '失败'}")
    exit(0 if success else 1)
