#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的图生图API测试脚本
用于调试403错误
"""

import requests
import json
import time

def test_image_to_image_api():
    """简化的测试/image-to-image API接口"""
    print("开始测试图生图API接口...")
    
    # 创建会话以保持cookie
    session = requests.Session()
    
    # 先访问ai_create页面以获取必要的cookie和会话信息
    print("\n1. 访问ai_create页面获取会话信息...")
    ai_create_url = "http://localhost:5002/ai_create"
    try:
        response = session.get(ai_create_url, timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   Cookie: {dict(session.cookies)}")
        print(f"   响应头: {dict(response.headers)}")
        # 保存响应到文件以便分析
        with open('ai_create_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("   响应内容已保存到ai_create_response.html")
    except Exception as e:
        print(f"   访问页面失败: {str(e)}")
    
    # API端点
    api_url = "http://localhost:5002/api/image-to-image"
    
    # 简化的测试数据
    test_data = {
        "image_url": "https://qiu-he-image1.tos-cn-shanghai.volces.com/photos/b7f5348cf90b48f0abe510ca68e4d4c6.jpg",
        "prompt": "将图片转换为水彩风格",
        "steps": 30,
        "creative_strength": 0.7
    }
    
    print(f"\n2. 准备发送请求到: {api_url}")
    print(f"   测试数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        # 准备请求头
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # 打印请求信息
        print(f"\n3. 发送POST请求...")
        print(f"   请求头: {headers}")
        
        # 发送请求
        start_time = time.time()
        response = session.post(
            api_url,
            headers=headers,
            json=test_data,
            timeout=60
        )
        
        end_time = time.time()
        print(f"   请求耗时: {end_time - start_time:.2f}秒")
        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        print(f"   响应内容长度: {len(response.text)}字符")
        
        # 尝试打印响应内容
        print(f"   响应内容: {'[空]' if not response.text else response.text[:500]}...")
        
        # 尝试解析JSON
        try:
            response_data = response.json()
            print(f"   JSON解析成功: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError:
            print("   JSON解析失败")
            # 保存响应内容到文件以便分析
            with open('api_response.txt', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("   响应内容已保存到api_response.txt")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    test_image_to_image_api()
    print("\n测试完成")
