from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 初始化数据库
db = SQLAlchemy()

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置应用
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'photo-gallery-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///gallery.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 配置TOS
    app.config['TOS_REGION'] = os.environ.get('TOS_REGION', 'cn-beijing')
    app.config['TOS_ACCESS_KEY'] = os.environ.get('TOS_ACCESS_KEY')
    app.config['TOS_SECRET_KEY'] = os.environ.get('TOS_SECRET_KEY')
    app.config['TOS_BUCKET_NAME'] = os.environ.get('TOS_BUCKET_NAME', 'photo-gallery')
    app.config['TOS_ENDPOINT'] = os.environ.get('TOS_ENDPOINT', f'https://tos-s3-{app.config["TOS_REGION"]}.volc.com')
    app.config['TOS_CDN_DOMAIN'] = os.environ.get('TOS_CDN_DOMAIN', '')
    
    # 上传限制
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)  # 启用CORS
    
    # 创建数据库表
    with app.app_context():
        from .models import Photo, Tag, ImageGenerationTask, GenerationResult, GenerationParameter
        db.create_all()
    
    # 注册路由
    from .routes import bp as api_bp
    app.register_blueprint(api_bp)
    
    return app