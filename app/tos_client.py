import os
import hashlib
import uuid
from io import BytesIO
from PIL import Image, ImageOps
import tos
from flask import current_app

class TOSClient:
    """火山引擎TOS客户端"""
    
    def __init__(self):
        self.client = None
    
    def _init_client(self):
        """初始化TOS客户端"""
        try:
            self.client = tos.TosClientV2(
                region=current_app.config['TOS_REGION'],
                ak=current_app.config['TOS_ACCESS_KEY'],
                sk=current_app.config['TOS_SECRET_KEY'],
                endpoint=current_app.config['TOS_ENDPOINT']
            )
        except Exception as e:
            print(f"TOS客户端初始化失败: {e}")
            raise e
    
    def generate_filename(self, original_filename: str) -> str:
        """生成唯一文件名"""
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
        return f"{uuid.uuid4().hex}.{ext}"
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """计算文件MD5哈希值"""
        return hashlib.md5(file_content).hexdigest()
    
    def get_image_info(self, file_content: bytes) -> dict:
        """获取图片信息"""
        try:
            with Image.open(BytesIO(file_content)) as img:
                img = ImageOps.exif_transpose(img)
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                }
        except Exception as e:
            print(f"获取图片信息失败: {e}")
            return {'width': 0, 'height': 0, 'format': 'Unknown', 'mode': 'Unknown'}
    
    def create_thumbnail(self, file_content: bytes, size: tuple = (400, 400)) -> bytes:
        """创建缩略图"""
        try:
            with Image.open(BytesIO(file_content)) as img:
                # 自动旋转图片
                img = ImageOps.exif_transpose(img)
                
                # 如果是RGBA，转换为RGB
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # 创建缩略图
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 保存为字节流
                thumbnail_buffer = BytesIO()
                img.save(thumbnail_buffer, format='JPEG', optimize=True, quality=85)
                return thumbnail_buffer.getvalue()
                
        except Exception as e:
            print(f"创建缩略图失败: {e}")
            return None
    
    def upload_file(self, file_content: bytes, filename: str, content_type: str) -> str:
        """上传文件到TOS"""
        if not self.client:
            self._init_client()
            
        try:
            bucket_name = current_app.config['TOS_BUCKET_NAME']
            key = f"photos/{filename}"
            
            # 上传文件
            result = self.client.put_object(
                bucket=bucket_name,
                key=key,
                content=file_content,
                content_type=content_type
            )
            
            # 返回文件URL，使用正确的TOS域名格式
            if current_app.config.get('TOS_CDN_DOMAIN'):
                return f"https://{current_app.config['TOS_CDN_DOMAIN']}/{key}"
            else:
                # 清理TOS_ENDPOINT，确保不包含https://前缀
                tos_endpoint = current_app.config['TOS_ENDPOINT']
                if tos_endpoint.startswith('https://'):
                    tos_endpoint = tos_endpoint[8:]
                elif tos_endpoint.startswith('http://'):
                    tos_endpoint = tos_endpoint[7:]
                
                # 使用正确的URL格式
                return f"https://{bucket_name}.{tos_endpoint}/{key}"
                
        except Exception as e:
            print(f"上传文件失败: {e}")
            raise e
    
    def upload_thumbnail(self, thumbnail_content: bytes, filename: str) -> str:
        """上传缩略图到TOS"""
        if not self.client:
            self._init_client()
            
        try:
            bucket_name = current_app.config['TOS_BUCKET_NAME']
            key = f"thumbnails/{filename}"
            
            result = self.client.put_object(
                bucket=bucket_name,
                key=key,
                content=thumbnail_content,
                content_type='image/jpeg'
            )
            
            # 返回缩略图URL，使用正确的TOS域名格式
            if current_app.config.get('TOS_CDN_DOMAIN'):
                return f"https://{current_app.config['TOS_CDN_DOMAIN']}/{key}"
            else:
                # 清理TOS_ENDPOINT，确保不包含https://前缀
                tos_endpoint = current_app.config['TOS_ENDPOINT']
                if tos_endpoint.startswith('https://'):
                    tos_endpoint = tos_endpoint[8:]
                elif tos_endpoint.startswith('http://'):
                    tos_endpoint = tos_endpoint[7:]
                
                # 使用正确的URL格式
                return f"https://{bucket_name}.{tos_endpoint}/{key}"
                
        except Exception as e:
            print(f"上传缩略图失败: {e}")
            raise e
    
    def delete_file(self, filename: str):
        """删除文件"""
        if not self.client:
            self._init_client()
            
        try:
            bucket_name = current_app.config['TOS_BUCKET_NAME']
            
            # 删除原图和缩略图
            try:
                self.client.delete_object(bucket=bucket_name, key=f"photos/{filename}")
            except:
                pass
            try:
                self.client.delete_object(bucket=bucket_name, key=f"thumbnails/{filename}")
            except:
                pass
                
        except Exception as e:
            print(f"删除文件失败: {e}")

# 全局TOS客户端实例
tos_client = TOSClient()