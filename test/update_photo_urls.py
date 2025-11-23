import os
import sys
import pymysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '12345')
DB_NAME = os.getenv('DB_NAME', 'photo_gallery')

# TOS配置
TOS_BUCKET_NAME = os.getenv('TOS_BUCKET_NAME', 'qiu-he-image1')
TOS_ENDPOINT = os.getenv('TOS_ENDPOINT', 'tos-cn-shanghai.volces.com')

def update_photo_urls():
    """
    更新数据库中所有图片的URL为真实的TOS URL
    """
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        print(f"成功连接到数据库: {DB_NAME}")
        
        # 查询所有图片记录
        cursor.execute("SELECT id, filename, tos_url, thumbnail_url FROM photo")
        photos = cursor.fetchall()
        
        if not photos:
            print("数据库中没有图片记录")
            return
        
        print(f"找到 {len(photos)} 条图片记录")
        
        # 清理TOS_ENDPOINT，确保不包含https://前缀
        cleaned_endpoint = TOS_ENDPOINT
        if cleaned_endpoint.startswith('https://'):
            cleaned_endpoint = cleaned_endpoint[8:]
        elif cleaned_endpoint.startswith('http://'):
            cleaned_endpoint = cleaned_endpoint[7:]
        
        # 更新每张图片的URL
        updated_count = 0
        for photo_id, filename, tos_url, thumbnail_url in photos:
            # 无论是否是占位符URL，都重新生成正确的URL
            # 生成真实的TOS URL
            new_tos_url = f"https://{TOS_BUCKET_NAME}.{cleaned_endpoint}/photos/{filename}"
            new_thumbnail_url = f"https://{TOS_BUCKET_NAME}.{cleaned_endpoint}/thumbnails/{filename}"
            
            # 更新数据库
            cursor.execute(
                "UPDATE photo SET tos_url = %s, thumbnail_url = %s WHERE id = %s",
                (new_tos_url, new_thumbnail_url, photo_id)
            )
            updated_count += 1
            print(f"更新图片 {photo_id}: {new_tos_url}")
        
        # 提交更改
        conn.commit()
        print(f"成功更新 {updated_count} 条图片URL")
        
    except Exception as e:
        print(f"更新图片URL时出错: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    print("\n注意事项:")
    print("1. 请确保这些图片实际上已经上传到TOS存储桶中")
    print("2. 新上传的图片将自动使用正确的TOS URL")
    print("3. 如需验证URL是否可访问，请在浏览器中直接打开URL")

def main():
    """
    主函数
    """
    print("=== 图片URL更新工具 ===")
    print(f"将使用以下配置更新图片URL:")
    print(f"- 存储桶: {TOS_BUCKET_NAME}")
    print(f"- 终端节点: {TOS_ENDPOINT}")
    print(f"- 数据库: {DB_HOST}/{DB_NAME}")
    print()
    
    # 确认操作
    confirm = input("确认要更新所有图片URL吗？(y/N): ")
    if confirm.lower() == 'y':
        update_photo_urls()
    else:
        print("操作已取消")

if __name__ == "__main__":
    main()