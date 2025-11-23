# 即梦4.0 图生图工具使用说明（支持图片URL输入）

本文档介绍如何使用 `jimeng_image_to_image_with_url.py` 脚本，通过输入图片URL和提示词来生成新图像。

## 功能特点

- 支持从图片URL生成新图像
- 自动从 `.env` 文件加载API密钥
- 提供友好的命令行交互界面
- 支持自定义图像尺寸和水印设置
- 可选择保存生成的图像到本地
- 包含图片URL验证功能

## 环境准备

### 1. 安装依赖

```bash
pip install requests python-dotenv
```

### 2. API密钥配置

脚本会自动从以下位置尝试加载API密钥（按优先级）：

1. 脚本运行时传入的参数
2. 环境变量 `ARK_API_KEY`
3. `.env` 文件中的 `API Key:` 行
4. 默认内置的API密钥

如果您想使用自己的API密钥，可以：

- 在 `.env` 文件中确保有一行类似 `API Key:your_api_key` 的配置
- 或者设置环境变量：`export ARK_API_KEY=your_api_key`

## 使用方法

### 1. 运行脚本

```bash
python jimeng_image_to_image_with_url.py
```

### 2. 交互式操作

脚本启动后，会提供以下交互式操作步骤：

1. **输入图片URL**：输入一个有效的图片URL地址（支持http和https）
2. **输入提示词**：描述您期望生成的图像内容
3. **选择图像尺寸**：默认为"2K"，可根据需要修改
4. **选择是否添加水印**：默认为添加水印（输入y/n）
5. **查看生成结果**：脚本会显示API响应结果和生成的图像URL
6. **选择是否保存图像**：输入y/n决定是否保存，保存时可指定路径
7. **选择是否继续生成**：输入y/n决定是否生成另一张图像

## 示例

```
即梦4.0 图生图 API 调用工具（支持图片URL输入）
============================================================
API密钥已加载

请输入图片URL (输入 'exit' 退出): https://example.com/sample.jpg
请输入提示词: 将这张图片转换为油画风格，增加鲜艳的色彩
请输入图像尺寸 (默认: 2K): 2K
是否添加水印? (y/n, 默认: y): y

开始生成图像，这可能需要一些时间...

正在发送图生图请求...
输入图片URL: https://example.com/sample.jpg
提示词: 将这张图片转换为油画风格，增加鲜艳的色彩
使用模型: doubbao-seedream-4-0-250828

API 响应成功!
{"data": [{"url": "https://example.com/generated_image.jpg", "model": "doubao-seedream-4-0-250828"}], "object": "list"}

生成的图像URL: https://example.com/generated_image.jpg
是否保存图像? (y/n): y
请输入保存路径 (默认自动命名): ./output/oil_painting.jpg

正在保存生成的图像...
图像已成功保存到: ./output/oil_painting.jpg

是否继续生成另一张图像? (y/n): n
程序已退出
```

## 注意事项

1. **网络连接**：确保您的网络连接稳定，特别是在上传和下载图片时
2. **图片URL**：确保提供的图片URL是公开可访问的，且支持外部访问
3. **API限制**：请注意即梦4.0 API可能有调用频率限制和配额
4. **生成时间**：图像生成可能需要几秒钟到几分钟不等，取决于网络状况和API响应时间
5. **错误处理**：如果遇到API错误，请检查您的API密钥是否有效，以及网络连接是否正常

## 常见问题

### 1. 脚本无法运行

**可能原因**：缺少依赖包
**解决方案**：运行 `pip install requests python-dotenv` 安装必要的依赖

### 2. API密钥无效

**可能原因**：API密钥错误或已过期
**解决方案**：检查 `.env` 文件中的API密钥格式是否正确

### 3. 图片URL验证失败

**可能原因**：URL格式不正确或图片无法访问
**解决方案**：确保URL以http://或https://开头，且图片是公开可访问的

### 4. 图像生成超时

**可能原因**：网络延迟或API处理时间过长
**解决方案**：检查网络连接，稍后重试

## 高级用法

### 在其他Python代码中集成

您可以在自己的Python代码中导入并使用 `ArkImageGenerator` 类：

```python
from jimeng_image_to_image_with_url import ArkImageGenerator

# 初始化生成器
generator = ArkImageGenerator()

# 生成图像
result = generator.generate_image_from_url(
    image_url="https://example.com/sample.jpg",
    prompt="转换为水彩画风格",
    size="2K",
    watermark=False
)

# 保存图像
if "data" in result and result["data"]:
    generated_url = result["data"][0].get("url")
    if generated_url:
        generator.save_generated_image(generated_url, "./watercolor_style.jpg")
```

---

**作者**: AI Assistant  
**创建时间**: 2024  
**版本**: 1.0