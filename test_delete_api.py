import requests
import sys

# 确保有足够的参数
if len(sys.argv) != 2:
    print("用法: python test_delete_api.py <image_id>")
    sys.exit(1)

image_id = sys.argv[1]
url = f"http://localhost:5002/api/generated-images/{image_id}"

print(f"测试删除API - 图片ID: {image_id}")
print(f"请求URL: {url}")
print(f"请求方法: DELETE")

# 设置请求头
headers = {
    'Content-Type': 'application/json'
}

# 发送请求
try:
    response = requests.delete(url, headers=headers)
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    # 尝试解析JSON响应
    try:
        json_data = response.json()
        print("\nJSON响应:")
        for key, value in json_data.items():
            print(f"  {key}: {value}")
    except ValueError:
        print("\n警告: 响应不是有效的JSON格式")
        
    if response.status_code >= 200 and response.status_code < 300:
        print("\n✅ 删除请求成功")
    else:
        print(f"\n❌ 删除请求失败 - 状态码: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ 请求发送失败: {e}")
    print(f"错误类型: {type(e).__name__}")

print("\n测试完成")