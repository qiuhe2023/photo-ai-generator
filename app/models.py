from datetime import datetime
from . import db

# 关联表
photo_tag = db.Table('photo_tag',
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Photo(db.Model):
    """图片模型"""
    __tablename__ = 'photo'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    original_filename = db.Column(db.String(255), nullable=False)
    
    # TOS存储相关
    tos_url = db.Column(db.String(500), nullable=False)  # 原图TOS URL
    thumbnail_url = db.Column(db.String(500))  # 缩略图TOS URL
    
    # 文件信息
    file_size = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    mime_type = db.Column(db.String(50))
    hash_value = db.Column(db.String(64), unique=True, index=True)  # 防重复上传
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 状态
    is_public = db.Column(db.Boolean, default=True, index=True)
    view_count = db.Column(db.Integer, default=0)
    
    # 关系
    tags = db.relationship('Tag', secondary='photo_tag', back_populates='photos')
    
    def __repr__(self):
        return f'<Photo {self.title}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'tos_url': self.tos_url,
            'thumbnail_url': self.thumbnail_url,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'mime_type': self.mime_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'view_count': self.view_count,
            'tags': [{'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in self.tags]
        }

class Tag(db.Model):
    """标签模型"""
    __tablename__ = 'tag'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    color = db.Column(db.String(7), default='#007bff')  # 十六进制颜色
    usage_count = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    photos = db.relationship('Photo', secondary='photo_tag', back_populates='tags')
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'usage_count': self.usage_count
        }


class ImageGenerationTask(db.Model):
    """图片生成任务模型"""
    __tablename__ = 'image_generation_task'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.String(100), unique=True, index=True)
    input_image_url = db.Column(db.String(1000), nullable=False)
    input_image_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    prompt = db.Column(db.Text, nullable=False)
    model = db.Column(db.String(100), default='doubao-seedream-4-0-250828')
    size = db.Column(db.String(50), default='2K')
    watermark = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    api_response = db.Column(db.Text)
    
    # 关系
    results = db.relationship('GenerationResult', back_populates='task', cascade='all, delete-orphan')
    parameters = db.relationship('GenerationParameter', back_populates='task', cascade='all, delete-orphan')
    input_image = db.relationship('Photo', foreign_keys=[input_image_id])

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'input_image_url': self.input_image_url,
            'input_image_id': self.input_image_id,
            'prompt': self.prompt,
            'model': self.model,
            'size': self.size,
            'watermark': self.watermark,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }


class GenerationResult(db.Model):
    """生成结果模型"""
    __tablename__ = 'generation_result'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('image_generation_task.id'), nullable=False)
    generated_image_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    generated_image_url = db.Column(db.String(1000), nullable=False)
    model = db.Column(db.String(100))
    content_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    task = db.relationship('ImageGenerationTask', back_populates='results')
    generated_image = db.relationship('Photo', foreign_keys=[generated_image_id], cascade='all')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'generated_image_id': self.generated_image_id,
            'generated_image_url': self.generated_image_url,
            'model': self.model,
            'content_type': self.content_type,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class GenerationParameter(db.Model):
    """生成参数模型"""
    __tablename__ = 'generation_parameter'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('image_generation_task.id'), nullable=False)
    parameter_name = db.Column(db.String(100), nullable=False)
    parameter_value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    task = db.relationship('ImageGenerationTask', back_populates='parameters')
    
    __table_args__ = (
        db.UniqueConstraint('task_id', 'parameter_name', name='_task_parameter_uc'),
    )

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'parameter_name': self.parameter_name,
            'parameter_value': self.parameter_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }