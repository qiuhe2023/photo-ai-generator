import requests
import json

def test_model_validation():
    """测试模型名称验证功能"""
    # API端点
    url = "http://localhost:5002/api/image-to-image"
    
    # 测试数据 - 使用一个有效的图片URL和提示词
    valid_image_url = "https://qiu-he-image1.tos-cn-shanghai.volces.com/photos/b7f5348cf90b48f0abe510ca68e4d4c6.jpg"
    prompt = "赛博朋克风格"
    
    # 1. 测试使用无效模型名称
    print("测试1: 使用无效模型名称 'model1'")
    invalid_model_data = {
        "image_url": valid_image_url,
        "prompt": prompt,
        "model": "model1",
        "watermark": True
    }
    
    try:
        response = requests.post(url, json=invalid_model_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 400:
            response_json = response.json()
            print(f"响应内容: {json.dumps(response_json, ensure_ascii=False)}")
            
            # 验证是否返回了正确的错误信息
            if ('success' in response_json and response_json['success'] is False and
                'error' in response_json and 'model1' in response_json['error']):
                print("✅ 测试通过: 正确拒绝了无效模型名称")
            else:
                print("❌ 测试失败: 没有返回预期的错误信息")
        else:
            print(f"❌ 测试失败: 期望状态码400，但得到了{response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: 请求出错 - {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 测试使用有效模型名称
    print("测试2: 使用有效模型名称 'doubao-seedream-4-0-250828'")
    valid_model_data = {
        "image_url": valid_image_url,
        "prompt": prompt,
        "model": "doubao-seedream-4-0-250828",
        "watermark": True
    }
    
    try:
        response = requests.post(url, json=valid_model_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_json = response.json()
            print(f"响应内容: {json.dumps(response_json, ensure_ascii=False)}")
            
            # 验证是否返回了成功信息
            if ('success' in response_json and response_json['success'] is True):
                print("✅ 测试通过: 正确接受了有效模型名称")
            else:
                print("❌ 测试失败: 没有返回预期的成功信息")
        else:
            print(f"❌ 测试失败: 期望状态码200，但得到了{response.status_code}")
            if response.status_code == 400:
                print(f"错误信息: {response.json()}")
    except Exception as e:
        print(f"❌ 测试失败: 请求出错 - {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 测试不提供模型名称（应该使用默认值）
    print("测试3: 不提供模型名称（使用默认值）")
    default_model_data = {
        "image_url": valid_image_url,
        "prompt": prompt,
        "watermark": True
    }
    
    try:
        response = requests.post(url, json=default_model_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_json = response.json()
            print(f"响应内容: {json.dumps(response_json, ensure_ascii=False)}")
            
            # 验证是否返回了成功信息
            if ('success' in response_json and response_json['success'] is True):
                print("✅ 测试通过: 正确使用了默认模型名称")
            else:
                print("❌ 测试失败: 没有返回预期的成功信息")
        else:
            print(f"❌ 测试失败: 期望状态码200，但得到了{response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: 请求出错 - {str(e)}")

if __name__ == "__main__":
    print("开始测试模型名称验证功能...\n")
    test_model_validation()
    print("\n测试完成")
