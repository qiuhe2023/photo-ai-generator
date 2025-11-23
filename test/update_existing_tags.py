from app import create_app, db
from app.models import Tag
import random

def generate_random_color():
    # 预设颜色列表，确保颜色美观且可区分
    colors = [
        '#E74C3C', '#3498DB', '#2ECC71', '#F39C12',  # 红、蓝、绿、橙
        '#9B59B6', '#1ABC9C', '#E67E22', '#8E44AD',  # 紫、青、深橙、深紫
        '#34495E', '#16A085', '#D35400', '#7F8C8D',  # 深蓝灰、深绿、深橙、灰
        '#2C3E50', '#18BC9C', '#D9A21C', '#95A5A6',  # 深灰蓝、青绿、金黄、浅灰
        '#C0392B', '#27AE60', '#F1C40F', '#8E44AD',  # 深红、绿、黄、紫
        '#16A085', '#2980B9', '#E74C3C', '#F39C12',  # 青绿、蓝、红、橙
        '#9B59B6', '#ECF0F1', '#34495E', '#E67E22',  # 紫、浅灰、深蓝灰、橙
        '#1ABC9C', '#3498DB', '#E74C3C', '#F1C40F',  # 青绿、蓝、红、黄
        '#9B59B6', '#2ECC71', '#F39C12', '#8E44AD',  # 紫、绿、橙、紫
        '#1ABC9C', '#3498DB', '#E67E22', '#95A5A6'   # 青绿、蓝、橙、灰
    ]
    return random.choice(colors)

# 创建应用并设置上下文
app = create_app()

with app.app_context():
    try:
        # 获取id为1-4的标签
        tags = Tag.query.filter(Tag.id.in_([1, 2, 3, 4])).all()
        
        if tags:
            print(f"找到 {len(tags)} 个原有标签")
            for tag in tags:
                # 为每个标签分配随机颜色
                new_color = generate_random_color()
                tag.color = new_color
                print(f"已更新标签: {tag.name} (id: {tag.id}) - 颜色: {new_color}")
            
            # 提交更改
            db.session.commit()
            print("所有标签颜色更新已提交")
        else:
            print("没有找到id为1-4的标签")
            
    except Exception as e:
        db.session.rollback()
        print(f"更新标签颜色时出错: {str(e)}")
        
    finally:
        if 'db' in locals():
            db.session.remove()