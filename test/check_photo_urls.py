import os
import pymysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '12345')
DB_NAME = os.getenv('DB_NAME', 'photo_gallery')

def check_photo_urls():
    """
    检查数据库中所有图片的URL
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
        print("\n图片URL详情:")
        print("-" * 80)
        print(f"{'ID':<5} {'Filename':<30} {'TOS URL':<60} {'Thumbnail URL':<60}")
        print("-" * 80)
        
        for photo_id, filename, tos_url, thumbnail_url in photos:
            print(f"{photo_id:<5} {filename:<30} {str(tos_url):<60} {str(thumbnail_url):<60}")
        
        # 检查URL格式
        print("\nURL格式分析:")
        for photo_id, filename, tos_url, thumbnail_url in photos:
            print(f"图片 {photo_id}:")
            if tos_url:
                print(f"  - TOS URL: {tos_url}")
                print(f"    格式是否正确: {'https://' in tos_url and '.volces.com' in tos_url}")
            else:
                print("  - TOS URL: 空")
            if thumbnail_url:
                print(f"  - Thumbnail URL: {thumbnail_url}")
                print(f"    格式是否正确: {'https://' in thumbnail_url and '.volces.com' in thumbnail_url}")
            else:
                print("  - Thumbnail URL: 空")
    
    except Exception as e:
        print(f"检查图片URL时出错: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_photo_urls()