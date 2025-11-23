#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
即梦4.0 API 图生图功能实现脚本
根据即梦4.0 API调用方案文档创建
用于图像编辑和多图组合生成
"""

import json
import sys
import os
import datetime
import hashlib
import hmac
import requests
import time
from dotenv import load_dotenv

# 加载环境变量（可选，如果使用.env文件存储凭证）
load_dotenv()

# 接口配置
METHOD = 'POST'
HOST = 'visual.volcengineapi.com'
REGION = 'cn-north-1'
ENDPOINT = 'https://visual.volcengineapi.com'
SERVICE = 'cv'

class JimengImageGenerator:
    """
    即梦4.0 API图像生成器类
    提供图生图功能的封装
    """
    
    def __init__(self, access_key=None, secret_key=None):
        """
        初始化即梦图像生成器
        
        Args:
            access_key: 访问密钥，如果不提供则尝试从环境变量获取
            secret_key: 密钥，如果不提供则尝试从环境变量获取
        """
        self.access_key = access_key or os.getenv('VOLC_ACCESS_KEY')
        self.secret_key = secret_key or os.getenv('VOLC_SECRET_KEY')
        
        if not self.access_key or not self.secret_key:
            raise ValueError("请提供Access Key和Secret Key或设置环境变量VOLC_ACCESS_KEY和VOLC_SECRET_KEY")
    
    def _sign(self, key, msg):
        """HMAC签名函数"""
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    
    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        """生成签名密钥"""
        k_date = self._sign(key.encode('utf-8'), date_stamp)
        k_region = self._sign(k_date, region_name)
        k_service = self._sign(k_region, service_name)
        k_signing = self._sign(k_service, 'request')
        return k_signing
    
    def _format_query(self, parameters):
        """格式化查询参数"""
        request_parameters_init = ''
        for key in sorted(parameters):
            request_parameters_init += key + '=' + parameters[key] + '&'
        request_parameters = request_parameters_init[:-1] if request_parameters_init else ''
        return request_parameters
    
    def _sign_v4_request(self, service, req_query, req_body):
        """
        生成V4签名并发送请求
        
        Args:
            service: 服务名称
            req_query: 请求查询参数
            req_body: 请求体参数
            
        Returns:
            解析后的API响应
        """
        if self.access_key is None or self.secret_key is None:
            raise ValueError('No access key is available.')

        # 获取当前时间
        t = datetime.datetime.utcnow()
        current_date = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')  # 用于凭证范围的日期
        
        # 构建规范化请求
        canonical_uri = '/'
        canonical_querystring = req_query
        signed_headers = 'content-type;host;x-content-sha256;x-date'
        payload_hash = hashlib.sha256(req_body.encode('utf-8')).hexdigest()
        content_type = 'application/json'
        canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + HOST + '\n' + \
            'x-content-sha256:' + payload_hash + '\n' + 'x-date:' + current_date + '\n'
        canonical_request = METHOD + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + \
            canonical_headers + '\n' + signed_headers + '\n' + payload_hash
        
        # 构建签名字符串
        algorithm = 'HMAC-SHA256'
        credential_scope = datestamp + '/' + REGION + '/' + service + '/' + 'request'
        string_to_sign = algorithm + '\n' + current_date + '\n' + credential_scope + '\n' + \
            hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        
        # 计算签名
        signing_key = self._get_signature_key(self.secret_key, datestamp, REGION, service)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # 构建授权头
        authorization_header = algorithm + ' ' + 'Credential=' + self.access_key + '/' + \
            credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
        
        # 请求头
        headers = {
            'X-Date': current_date,
            'Authorization': authorization_header,
            'X-Content-Sha256': payload_hash,
            'Content-Type': content_type
        }
        
        # 发送请求
        request_url = ENDPOINT + ('?' + canonical_querystring if canonical_querystring else '')
        
        print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
        print('Request URL =', request_url)
        try:
            r = requests.post(request_url, headers=headers, data=req_body, timeout=30)
            r.raise_for_status()  # 检查是否有HTTP错误
        except requests.exceptions.RequestException as err:
            print(f'Error occurred: {err}')
            if hasattr(err, 'response') and err.response is not None:
                print(f'Response content: {err.response.text}')
            raise
        else:
            print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
            print(f'Response code: {r.status_code}\n')
            # 使用 replace 方法将 \u0026 替换为 &
            resp_str = r.text.replace("\\u0026", "&")
            print(f'Response body: {resp_str}\n')
            # 返回解析后的响应
            return json.loads(resp_str)
    
    def generate_image_from_images(self, image_urls, prompt, size=None, width=None, height=None,
                                  scale=0.5, force_single=False, min_ratio=1/3, max_ratio=3):
        """
        图生图功能 - 使用输入图片生成新图像
        
        Args:
            image_urls: 图片URL列表，最多10张
            prompt: 提示词，最长不超过800字符
            size: 可选，生图面积，默认4194304(2048×2048)
            width: 可选，图像宽度（与height同时使用）
            height: 可选，图像高度（与width同时使用）
            scale: 可选，文本描述影响程度，默认0.5
            force_single: 可选，是否强制生成单图，默认False
            min_ratio: 可选，最小宽高比，默认1/3
            max_ratio: 可选，最大宽高比，默认3
            
        Returns:
            解析后的API响应，包含TaskId
        """
        # 验证输入参数
        if not image_urls or not isinstance(image_urls, list):
            raise ValueError("image_urls必须是非空列表")
        
        if len(image_urls) > 10:
            raise ValueError("image_urls最多支持10张图片")
        
        if not prompt or len(prompt) > 800:
            raise ValueError("prompt必须非空且长度不超过800字符")
        
        # 请求Query参数
        query_params = {
            'Action': 'CVSync2AsyncSubmitTask',
            'Version': '2022-08-31',
        }
        formatted_query = self._format_query(query_params)
        
        # 请求Body参数
        body_params = {
            "req_key": "jimeng_t2i_v40",  # 即梦4.0服务标识
            "prompt": prompt,
            "image_urls": image_urls,
            "scale": scale,
            "force_single": force_single,
            "min_ratio": min_ratio,
            "max_ratio": max_ratio
        }
        
        # 添加可选参数
        if size:
            body_params["size"] = size
        
        if width and height:
            body_params["width"] = width
            body_params["height"] = height
        
        formatted_body = json.dumps(body_params)
        
        # 调用API
        return self._sign_v4_request(SERVICE, formatted_query, formatted_body)
    
    def query_task_result(self, task_id):
        """
        查询任务执行结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果响应
        """
        # 请求Query参数
        query_params = {
            'Action': 'CVSync2AsyncGetResult',
            'Version': '2022-08-31',
        }
        formatted_query = self._format_query(query_params)
        
        # 请求Body参数
        body_params = {
            "task_id": task_id
        }
        formatted_body = json.dumps(body_params)
        
        # 调用API
        return self._sign_v4_request(SERVICE, formatted_query, formatted_body)
    
    def poll_task_result(self, task_id, max_retries=30, interval=5):
        """
        轮询查询任务结果
        
        Args:
            task_id: 任务ID
            max_retries: 最大重试次数，默认30次
            interval: 轮询间隔（秒），默认5秒
            
        Returns:
            成功时返回任务结果
            
        Raises:
            TimeoutError: 轮询超时
            Exception: 任务失败时抛出异常
        """
        for i in range(max_retries):
            result = self.query_task_result(task_id)
            status = result.get('Result', {}).get('Status')
            
            if status == 'Success':
                return result
            elif status == 'Failed':
                error_msg = result.get('Result', {}).get('ErrorMessage', 'Unknown error')
                raise Exception(f"Task failed: {error_msg}")
            
            print(f"轮询任务状态中 (尝试 {i+1}/{max_retries})...")
            time.sleep(interval)
        
        raise TimeoutError("任务轮询超时")


def main():
    """
    主函数 - 提供图生图功能的命令行使用示例
    """
    print("即梦4.0 图生图功能演示")
    print("=" * 50)
    
    try:
        # 初始化生成器
        # 注意：这里默认尝试从环境变量获取凭证
        # 如果需要直接在代码中设置，请取消下面的注释并填入实际值
        # generator = JimengImageGenerator(
        #     access_key='YOUR_ACCESS_KEY',
        #     secret_key='YOUR_SECRET_KEY'
        # )
        generator = JimengImageGenerator()
        
        # 图生图示例 - 替换为实际的图片URL和提示词
        image_urls = [
            "https://example.com/image1.jpg",  # 替换为实际的图片URL
            # "https://example.com/image2.jpg"  # 可以添加更多图片（最多10张）
        ]
        
        prompt = "将这张图片转换为油画风格，保持原有的构图和色彩"
        
        print(f"\n提交图生图任务...")
        print(f"输入图片数量: {len(image_urls)}")
        print(f"提示词: {prompt}")
        
        # 提交任务
        submit_result = generator.generate_image_from_images(
            image_urls=image_urls,
            prompt=prompt,
            size=4194304,  # 2K分辨率
            force_single=True
        )
        
        # 获取任务ID
        if 'TaskId' in submit_result:
            task_id = submit_result['TaskId']
            print(f"任务提交成功，任务ID: {task_id}")
            
            # 轮询获取结果
            print("\n开始轮询任务结果（可能需要几秒钟到几分钟）...")
            try:
                result = generator.poll_task_result(task_id)
                
                # 处理成功结果
                if 'Result' in result and 'Data' in result['Result']:
                    print("\n任务执行成功！")
                    print("生成的图片URL：")
                    for i, image_url in enumerate(result['Result']['Data'], 1):
                        print(f"  {i}. {image_url}")
                else:
                    print("\n任务成功但未返回图片数据。")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    
            except Exception as e:
                print(f"\n轮询任务结果时出错: {str(e)}")
        else:
            error_info = submit_result.get('Error', 'Unknown error')
            print(f"任务提交失败: {error_info}")
            
    except Exception as e:
        print(f"\n错误: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
