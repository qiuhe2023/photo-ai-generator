#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试即梦4.0 API调用
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入即梦API调用模块
from jimeng_image_to_image_with_url import ArkImageGenerator

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_jimeng_api')

def test_ark_image_generation():
    """测试即梦API的图生图功能"""
    try:
        # 加载环境变量
        load_dotenv()
        
        # 获取API密钥
        api_key = os.getenv('ARK_API_KEY')
        if not api_key:
            logger.error("未找到ARK_API_KEY环境变量")
            return False
        
        logger.info(f"使用API密钥: {api_key[:4]}...{api_key[-4:]}")
        
        # 创建生成器实例
        generator = ArkImageGenerator(api_key)
        logger.info("成功初始化ArkImageGenerator")
        
        # 测试图片URL (使用一个简单的示例图片)
        image_url = "https://images.unsplash.com/photo-1618005198919-d3d4b5a92ead?w=500&auto=format&fit=crop"
        prompt = "一只可爱的小猫，油画风格"
        negative_prompt = "模糊，变形，低质量"
        strength = 0.7
        
        logger.info(f"开始生成图片，提示词: {prompt}")
        
        # 调用生成方法
        result = generator.generate_image_from_url(
            image_url=image_url,
            prompt=prompt,
            negative_prompt=negative_prompt,
            strength=strength
        )
        
        if result and "data" in result and result["data"]:
            logger.info("图片生成成功!")
            
            # 提取生成的图片URL
            generated_url = result["data"][0].get("url")
            if generated_url:
                logger.info(f"生成的图片URL: {generated_url}")
                
                # 保存生成的图片
                save_path = os.path.join(os.path.dirname(__file__), "test_result.jpg")
                if generator.save_generated_image(generated_url, save_path):
                    logger.info(f"图片已保存到: {save_path}")
                    return True
                else:
                    logger.error("图片保存失败")
                    return False
            else:
                logger.error("未在API响应中找到图片URL")
                return False
        else:
            logger.error("图片生成失败，未返回有效结果")
            return False
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("开始测试即梦API...")
    success = test_ark_image_generation()
    
    if success:
        logger.info("测试成功!")
        sys.exit(0)
    else:
        logger.info("测试失败!")
        sys.exit(1)
