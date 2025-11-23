from app import create_app, db

# 创建Flask应用实例
app = create_app()

# 在应用上下文中创建数据库表
with app.app_context():
    try:
        # 只创建新的表，不影响已存在的表
        # 如果Favorite表已存在，这不会报错
        db.create_all()
        print('数据库表创建/更新完成，Favorite表已添加')
    except Exception as e:
        print(f'创建数据库表时出错: {str(e)}')
