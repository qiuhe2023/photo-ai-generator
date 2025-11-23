# 即梦4.0 图生图功能使用说明

## 功能概述

本脚本实现了基于即梦4.0 API的图生图功能，可以将一张或多张输入图片根据提示词生成新的图像。主要特点包括：

- 支持单图或多图输入（最多10张）
- 完整的HMAC签名认证
- 任务提交、状态查询和结果轮询功能
- 参数验证和错误处理
- 支持从环境变量或代码中配置API密钥

## 环境准备

### 安装依赖

脚本需要以下Python库：

- requests
- python-dotenv

可以通过以下命令安装：

```bash
pip install requests python-dotenv
```

### 配置API密钥

有两种方式配置火山引擎的访问凭证：

#### 方式一：环境变量（推荐）

设置以下环境变量：

```bash
export VOLC_ACCESS_KEY=你的AccessKey
export VOLC_SECRET_KEY=你的SecretKey
```

#### 方式二：在代码中直接设置

修改 `main()` 函数中的初始化部分，取消注释并填入实际值：

```python
generator = JimengImageGenerator(
    access_key='YOUR_ACCESS_KEY',
    secret_key='YOUR_SECRET_KEY'
)
```

## 使用方法

### 命令行使用

直接运行脚本：

```bash
python jimeng_image_to_image.py
```

### 在代码中使用

可以将 `JimengImageGenerator` 类集成到其他项目中：

```python
from jimeng_image_to_image import JimengImageGenerator

# 初始化生成器
generator = JimengImageGenerator()

# 提交图生图任务
result = generator.generate_image_from_images(
    image_urls=['https://example.com/input.jpg'],
    prompt='将图片转换为油画风格',
    force_single=True
)

# 获取任务ID
task_id = result['TaskId']

# 轮询获取结果
task_result = generator.poll_task_result(task_id)

# 处理生成的图片URLs
generated_images = task_result['Result']['Data']
```

## 参数说明

### generate_image_from_images 方法参数

- **image_urls** (必选)：图片URL列表，最多支持10张图片
- **prompt** (必选)：提示词，描述生成图像的要求，最长不超过800字符
- **size** (可选)：生图面积，默认4194304(2048×2048)
- **width/height** (可选)：指定图像宽度和高度，需同时设置
- **scale** (可选)：文本描述影响程度，默认0.5，范围0-1
- **force_single** (可选)：是否强制生成单图，默认False
- **min_ratio/max_ratio** (可选)：最小/最大宽高比，默认1/3和3

## 注意事项

1. **图片URL要求**：提供的图片URL必须是公网可访问的
2. **API限流**：请遵守火山引擎API的调用频率限制
3. **费用**：使用即梦4.0 API会产生相应费用，请关注费用账单
4. **错误处理**：脚本包含基本错误处理，但建议在生产环境中增强异常捕获
5. **示例URL**：代码中的示例URL `https://example.com/image1.jpg` 需要替换为实际的图片URL

## 常见问题

### 1. 为什么提示"请提供Access Key和Secret Key"？

请检查是否正确设置了环境变量或在代码中直接配置了API密钥。

### 2. 图片URL有什么要求？

图片URL必须是公网可访问的，支持常见图片格式如JPG、PNG等。

### 3. 任务执行需要多长时间？

一般情况下，图生图任务需要几秒钟到几分钟不等，取决于图片复杂度和当前服务负载。

### 4. 如何调整生成图片的质量？

可以通过调整 `size` 参数或指定 `width` 和 `height` 来控制图片分辨率，影响最终质量。

## 示例场景

### 图片风格转换

```python
# 将图片转换为梵高风格油画
generator.generate_image_from_images(
    image_urls=['https://example.com/photo.jpg'],
    prompt='梵高风格油画，星空效果，强烈的色彩对比',
    scale=0.7,  # 增强文本描述的影响
    force_single=True
)
```

### 多图融合

```python
# 融合两张图片的元素
generator.generate_image_from_images(
    image_urls=[
        'https://example.com/landscape.jpg',
        'https://example.com/character.jpg'
    ],
    prompt='将人物放置在风景中，保持两者的风格一致',
    width=1024,
    height=1024
)
```

## 扩展开发

如需扩展功能，可以考虑：

1. 添加本地图片上传功能
2. 实现批量处理
3. 添加更多参数控制
4. 构建Web界面

---

**作者**: AI Assistant
**创建时间**: 2024
**版本**: 1.0