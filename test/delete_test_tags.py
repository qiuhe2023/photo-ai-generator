from app import create_app, db
from app.models import Tag

# 创建应用并设置上下文
app = create_app()

with app.app_context():
    # 删除测试标签（id 5和6）
    try:
        # 删除id为5的标签
        tag5 = Tag.query.get(5)
        if tag5:
            db.session.delete(tag5)
            print(f"已删除标签: {tag5.name} (id: 5)")
        else:
            print("标签id 5不存在")
        
        # 删除id为6的标签
        tag6 = Tag.query.get(6)
        if tag6:
            db.session.delete(tag6)
            print(f"已删除标签: {tag6.name} (id: 6)")
        else:
            print("标签id 6不存在")
        
        # 提交更改
        db.session.commit()
        print("数据库更改已提交")
        
    except Exception as e:
        db.session.rollback()
        print(f"删除标签时出错: {str(e)}")
        
    finally:
        if 'db' in locals():
            db.session.remove()