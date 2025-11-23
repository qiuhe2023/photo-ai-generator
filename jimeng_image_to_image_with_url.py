#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
即梦4.0 图生图 API 调用脚本（支持图片URL输入）
基于 ark.cn-beijing.volces.com API 实现
"""

import json
import os
import sys
import requests
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

class ArkImageGenerator:
    """
    即梦4.0 图像生成器类
    支持从图片URL生成新图像
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化图像生成器
        
        Args:
            api_key: Bearer Token API密钥，如果不提供则尝试从环境变量加载
        
        Raises:
            ValueError: 当未提供API密钥且环境变量中也不存在时
        """
        # 尝试从环境变量加载API密钥
        load_dotenv()
        
        # 优先使用传入的api_key，如果没有则从环境变量获取
        self.api_key = api_key or os.getenv('ARK_API_KEY')
        
        # 从.env文件中提取的API密钥（备选方案）
        if not self.api_key:
            try:
                with open('.env', 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'API Key:' in line:
                            self.api_key = line.split('API Key:')[-1].strip()
                            break
            except Exception as e:
                print(f"无法从.env文件读取API密钥: {e}")
        
        # 默认API密钥（最后的备选方案）
        if not self.api_key:
            self.api_key = "b6dafc52-e9dd-4d14-b221-1cba73bbe4fe"
        
        self.api_url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        
        # 设置默认请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_image_from_url(
        self,
        image_url: str,
        prompt: str,
        model: str = "doubao-seedream-4-0-250828",
        size: str = "2K",
        sequential_image_generation: str = "disabled",
        response_format: str = "url",
        stream: bool = False,
        watermark: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        从图片URL生成新图像
        
        Args:
            image_url: 输入图片的URL
            prompt: 提示词，描述期望生成的图像内容
            model: 使用的模型名称，默认 "doubao-seedream-4-0-250828"
            size: 图像尺寸，默认 "2K"
            sequential_image_generation: 顺序图像生成选项，默认 "disabled"
            response_format: 响应格式，默认 "url"
            stream: 是否流式响应，默认 False
            watermark: 是否添加水印，默认 True
            **kwargs: 其他可选参数
            
        Returns:
            包含生成图像信息的字典
            
        Raises:
            requests.exceptions.RequestException: HTTP请求错误
            ValueError: 参数验证失败
        """
        # 参数验证
        if not image_url or not prompt:
            raise ValueError("图片URL和提示词不能为空")
        
        # 构建请求体
        payload = {
            "model": model,
            "prompt": prompt,
            "image": image_url,  # 添加图片URL参数
            "sequential_image_generation": sequential_image_generation,
            "response_format": response_format,
            "size": size,
            "stream": stream,
            "watermark": watermark
        }
        
        # 添加额外参数
        payload.update(kwargs)
        
        # 发送请求
        try:
            print(f"\n正在发送图生图请求...")
            print(f"输入图片URL: {image_url}")
            print(f"提示词: {prompt}")
            print(f"使用模型: {model}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=120  # 图生图可能需要更长时间，增加超时设置
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 返回解析后的JSON响应
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            # 处理HTTP错误
            error_msg = f"HTTP错误: {e.response.status_code} - {e.response.text}"
            print(error_msg)
            raise
        except requests.exceptions.RequestException as e:
            # 处理其他网络错误
            error_msg = f"请求错误: {str(e)}"
            print(error_msg)
            raise
        except json.JSONDecodeError as e:
            # 处理JSON解析错误
            error_msg = f"JSON解析错误: {str(e)}"
            print(error_msg)
            raise

    def save_generated_image(
        self,
        image_url: str,
        save_path: str = None
    ) -> bool:
        """
        保存生成的图像到本地
        
        Args:
            image_url: 生成图像的URL
            save_path: 保存路径，默认根据时间戳生成
            
        Returns:
            bool: 保存成功返回True，否则返回False
        """
        try:
            # 如果未指定保存路径，生成一个时间戳命名的文件
            if save_path is None:
                import time
                timestamp = int(time.time())
                save_path = f"./generated_image_{timestamp}.jpg"
            
            print(f"\n正在保存生成的图像...")
            response = requests.get(image_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            print(f"图像已成功保存到: {save_path}")
            return True
            
        except Exception as e:
            print(f"保存图像失败: {str(e)}")
            return False

    def generate_image_from_base64(
        self,
        image_base64: str,
        prompt: str,
        model: str = "doubao-seedream-4-0-250828",
        size: str = "2K",
        sequential_image_generation: str = "disabled",
        response_format: str = "url",
        stream: bool = False,
        watermark: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        从base64编码的图片生成新图像
        
        Args:
            image_base64: 输入图片的base64编码
            prompt: 提示词，描述期望生成的图像内容
            model: 使用的模型名称，默认 "doubao-seedream-4-0-250828"
            size: 图像尺寸，默认 "2K"
            sequential_image_generation: 顺序图像生成选项，默认 "disabled"
            response_format: 响应格式，默认 "url"
            stream: 是否流式响应，默认 False
            watermark: 是否添加水印，默认 True
            **kwargs: 其他可选参数
            
        Returns:
            包含生成图像信息的字典
            
        Raises:
            requests.exceptions.RequestException: HTTP请求错误
            ValueError: 参数验证失败
        """
        # 参数验证
        if not image_base64 or not prompt:
            raise ValueError("图片base64编码和提示词不能为空")
        
        # 构建请求体
        payload = {
            "model": model,
            "prompt": prompt,
            "image": image_base64,  # 添加base64编码的图片
            "sequential_image_generation": sequential_image_generation,
            "response_format": response_format,
            "size": size,
            "stream": stream,
            "watermark": watermark
        }
        
        # 添加额外参数
        payload.update(kwargs)
        
        # 发送请求
        try:
            print(f"\n正在发送基于base64图片的图生图请求...")
            print(f"提示词: {prompt}")
            print(f"使用模型: {model}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=120  # 图生图可能需要更长时间，增加超时设置
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 返回解析后的JSON响应
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            # 处理HTTP错误
            error_msg = f"HTTP错误: {e.response.status_code} - {e.response.text}"
            print(error_msg)
            raise
        except requests.exceptions.RequestException as e:
            # 处理其他网络错误
            error_msg = f"请求错误: {str(e)}"
            print(error_msg)
            raise
        except json.JSONDecodeError as e:
            # 处理JSON解析错误
            error_msg = f"JSON解析错误: {str(e)}"
            print(error_msg)
            raise

    def validate_image_url(self, url: str) -> bool:
        """
        验证图片URL是否有效
        
        Args:
            url: 要验证的图片URL
            
        Returns:
            bool: URL有效返回True，否则返回False
        """
        try:
            # 检查URL格式
            if not url.startswith(('http://', 'https://')):
                print("错误: URL必须以http://或https://开头")
                return False
            
            # 发送HEAD请求检查URL是否可访问
            response = requests.head(url, timeout=10)
            if response.status_code != 200:
                print(f"错误: URL无法访问，状态码: {response.status_code}")
                return False
            
            # 检查Content-Type
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                print(f"警告: URL可能不是图片，Content-Type: {content_type}")
            
            return True
        except Exception as e:
            print(f"验证图片URL失败: {str(e)}")
            return False


def main():
    """
    主函数，提供命令行界面
    """
    print("即梦4.0 图生图 API 调用工具（支持图片URL输入）")
    print("=" * 60)
    
    try:
        # 初始化生成器
        generator = ArkImageGenerator()
        print(f"API密钥已加载")
        
        # 获取用户输入
        while True:
            image_url = input("\n请输入图片URL (输入 'exit' 退出): ")
            if image_url.lower() == 'exit':
                print("程序已退出")
                return 0
            
            # 验证图片URL
            if not generator.validate_image_url(image_url):
                continue
            
            prompt = input("请输入提示词: ")
            if not prompt or len(prompt.strip()) == 0:
                print("提示词不能为空")
                continue
            
            # 获取可选参数
            try:
                size = input("请输入图像尺寸 (默认: 2K): ") or "2K"
                watermark_input = input("是否添加水印? (y/n, 默认: n): ")
                watermark = watermark_input.lower() == 'y'
                
                # 生成图像
                print("\n开始生成图像，这可能需要一些时间...")
                result = generator.generate_image_from_url(
                    image_url=image_url,
                    prompt=prompt,
                    size=size,
                    watermark=watermark
                )
                
                # 处理响应结果
                print("\nAPI 响应成功!")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
                # 保存图像
                if "data" in result and result["data"]:
                    generated_url = result["data"][0].get("url")
                    if generated_url:
                        print(f"\n生成的图像URL: {generated_url}")
                        
                        save_choice = input("是否保存图像? (y/n): ")
                        if save_choice.lower() == 'y':
                            save_path = input("请输入保存路径 (默认自动命名): ") or None
                            generator.save_generated_image(generated_url, save_path)
                
            except Exception as e:
                print(f"生成图像时出错: {str(e)}")
                
            # 询问是否继续
            continue_choice = input("\n是否继续生成另一张图像? (y/n): ")
            if continue_choice.lower() != 'y':
                print("程序已退出")
                break
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        return 1
    except Exception as e:
        print(f"\n程序错误: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    # 检查是否安装了必要的依赖
    try:
        import requests
        from dotenv import load_dotenv
    except ImportError:
        print("错误: 缺少必要的依赖包")
        print("请运行: pip install requests python-dotenv")
        sys.exit(1)
    
    sys.exit(main())
