from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import or_
import random
import time
import os
import json
from . import db
from .models import Photo, Tag, ImageGenerationTask, GenerationResult, GenerationParameter
from .tos_client import tos_client
from werkzeug.utils import secure_filename
# 导入图生图功能
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jimeng_image_to_image_with_url import ArkImageGenerator

def generate_random_color():
    """生成随机的十六进制颜色"""
    # 定义一组美观的颜色
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#82E0AA', '#D7BDE2', '#85C1E9', '#F8C471',
        '#82E0AA', '#D7BDE2', '#F1948A', '#85C1E9', '#D7BDE2'
    ]
    return random.choice(colors)

# 定义蓝图
bp = Blueprint('api', __name__, template_folder='templates')

@bp.route('/')
def index():
    """首页"""
    return render_template('index.html')

@bp.route('/v1')
def v1():
    """v1版本页面"""
    return render_template('v1.html')

@bp.route('/search')
def search():
    """搜索页面"""
    return render_template('search.html')

@bp.route('/gallery')
def gallery():
    """图库页面"""
    return render_template('gallery.html')

@bp.route('/ai_create')
def ai_create():
    """AI二创页面"""
    # 从数据库获取最近生成的图片，最多获取10张
    generated_images = GenerationResult.query.order_by(GenerationResult.created_at.desc()).limit(10).all()
    # 转换为字典格式以便在模板中使用
    images_data = [image.to_dict() for image in generated_images]
    return render_template('ai_create.html', generated_images=images_data)

@bp.route('/creative')
def creative():
    """创意页面"""
    return render_template('creative.html')

@bp.route('/api/photos', methods=['GET'])
def get_photos():
    """获取图片列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    # 同时支持tag和tag_id参数以兼容前端
    tag_id = request.args.get('tag_id', type=int) or request.args.get('tag', type=int)
    search = request.args.get('search', '').strip()
    
    # 构建查询
    query = Photo.query.filter_by(is_public=True)
    
    # 按标签筛选
    if tag_id:
        query = query.join(Photo.tags).filter(Tag.id == tag_id)
    
    # 搜索
    if search:
        query = query.filter(
            or_(
                Photo.title.contains(search),
                Photo.description.contains(search)
            )
        )
    
    # 分页
    photos = query.order_by(Photo.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'photos': [photo.to_dict() for photo in photos.items],
        'pagination': {
            'page': photos.page,
            'pages': photos.pages,
            'per_page': photos.per_page,
            'total': photos.total,
            'has_prev': photos.has_prev,
            'has_next': photos.has_next
        }
    })

@bp.route('/api/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    """获取单张图片详情"""
    photo = Photo.query.get_or_404(photo_id)
    
    # 增加浏览次数
    photo.view_count += 1
    db.session.commit()
    
    return jsonify(photo.to_dict())

@bp.route('/api/upload', methods=['POST'])
def upload_photos():
    """上传图片"""
    if 'files' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': '没有选择文件'}), 400
    
    uploaded_photos = []
    errors = []
    
    for file in files:
        if file and file.filename:
            try:
                # 读取文件内容
                file_content = file.read()
                file_size = len(file_content)
                
                # 检查文件大小
                if file_size > 100 * 1024 * 1024:  # 100MB
                    errors.append(f'{file.filename}: 文件大小超过限制')
                    continue
                
                # 计算文件哈希值，检查重复
                file_hash = tos_client.calculate_file_hash(file_content)
                existing_photo = Photo.query.filter_by(hash_value=file_hash).first()
                if existing_photo:
                    errors.append(f'{file.filename}: 文件已存在')
                    continue
                
                # 生成文件名并上传到TOS
                filename = tos_client.generate_filename(file.filename)
                tos_url = tos_client.upload_file(file_content, filename, file.content_type)
                
                # 创建并上传缩略图
                thumbnail_content = tos_client.create_thumbnail(file_content)
                thumbnail_url = None
                if thumbnail_content:
                    thumbnail_url = tos_client.upload_thumbnail(thumbnail_content, filename)
                
                # 获取图片信息
                img_info = tos_client.get_image_info(file_content)
                
                # 保存到数据库
                photo = Photo(
                    title=secure_filename(file.filename).rsplit('.', 1)[0],
                    filename=filename,
                    original_filename=file.filename,
                    tos_url=tos_url,
                    thumbnail_url=thumbnail_url,
                    file_size=file_size,
                    width=img_info.get('width', 0),
                    height=img_info.get('height', 0),
                    mime_type=file.content_type,
                    hash_value=file_hash
                )
                
                db.session.add(photo)
                db.session.commit()
                
                uploaded_photos.append(photo.to_dict())
                
            except Exception as e:
                db.session.rollback()
                errors.append(f'{file.filename}: 上传失败 - {str(e)}')
    
    return jsonify({
        'success': len(uploaded_photos) > 0,
        'count': len(uploaded_photos),
        'errors': errors
    })

@bp.route('/api/photos/<int:photo_id>/tags', methods=['POST'])
def add_photo_tags(photo_id):
    """为图片添加标签"""
    photo = Photo.query.get_or_404(photo_id)
    data = request.get_json()
    
    # 支持两种格式：直接是字符串数组 或者 包含tags字段的对象
    tag_names = data if isinstance(data, list) else data.get('tags', [])
    
    if not isinstance(tag_names, list):
        return jsonify({'error': '标签必须是数组格式'}), 400
    
    added_tags = []
    for tag_name in tag_names:
        tag_name = tag_name.strip()
        if not tag_name:
            continue
            
        # 查找或创建标签
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name, color=generate_random_color())
            db.session.add(tag)
        
        # 添加标签到图片
        if tag not in photo.tags:
            photo.tags.append(tag)
            tag.usage_count += 1
            added_tags.append(tag.to_dict())
    
    db.session.commit()
    return jsonify({'added_tags': added_tags, 'photo': photo.to_dict()})

@bp.route('/api/tags', methods=['GET'])
def get_tags():
    """获取标签列表"""
    tags = Tag.query.order_by(Tag.usage_count.desc()).limit(50).all()
    return jsonify([tag.to_dict() for tag in tags])

@bp.route('/api/photos/<int:photo_id>/tags/<int:tag_id>', methods=['DELETE'])
def remove_photo_tag(photo_id, tag_id):
    """从图片中移除标签"""
    photo = Photo.query.get_or_404(photo_id)
    tag = Tag.query.get_or_404(tag_id)
    
    # 检查标签是否在图片上
    if tag in photo.tags:
        # 移除标签并减少使用次数
        photo.tags.remove(tag)
        if tag.usage_count > 0:
            tag.usage_count -= 1
        db.session.commit()
        return jsonify({'message': '标签移除成功'})
    else:
        return jsonify({'error': '标签不存在于该图片上'}), 404

@bp.route('/api/photos/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    """删除图片"""
    photo = Photo.query.get_or_404(photo_id)
    
    try:
        # 删除TOS文件
        tos_client.delete_file(photo.filename)
        
        # 删除数据库记录
        db.session.delete(photo)
        db.session.commit()
        
        return jsonify({'message': '图片删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

@bp.route('/api/photos/<int:photo_id>', methods=['PUT'])
def update_photo(photo_id):
    """更新图片信息"""
    photo = Photo.query.get_or_404(photo_id)
    data = request.get_json()
    
    if 'title' in data:
        photo.title = data['title']
    if 'description' in data:
        photo.description = data['description']
    if 'is_public' in data:
        photo.is_public = data['is_public']
    
    db.session.commit()
    return jsonify(photo.to_dict())

@bp.route('/api/generated-images/<int:result_id>', methods=['DELETE'])
def delete_generated_image(result_id):
    """删除生成的图片"""
    print(f"=== 删除请求开始处理 - result_id: {result_id} ===")
    try:
        print(f"步骤1: 查找生成结果记录 ID={result_id}")
        # 查找生成结果记录
        result = GenerationResult.query.get_or_404(result_id)
        print(f"找到生成结果记录: {result.id}")
        
        # 保存photo_id以便后续验证
        photo_id = None
        if result.generated_image:
            photo_id = result.generated_image.id
            print(f"步骤2: 关联的Photo记录ID: {photo_id}")
        else:
            print("步骤2: 未发现关联的Photo记录")
        
        print("步骤3: 开始准备删除流程")
        try:
            # 先分离关联，确保正确删除
            photo_to_delete = None
            if result.generated_image:
                print("步骤4: 发现关联的Photo对象，准备分离关联")
                photo_to_delete = result.generated_image
                # 断开关系
                result.generated_image_id = None
                result.generated_image = None
                print("步骤4.1: 已断开GenerationResult与Photo的关联")
            
            # 删除Photo记录
            if photo_to_delete:
                print(f"步骤5: 处理Photo记录 (ID: {photo_id})")
                # 删除TOS文件
                if hasattr(tos_client, 'delete_file') and photo_to_delete.filename:
                    print(f"步骤5.1: 准备删除TOS文件: {photo_to_delete.filename}")
                    try:
                        tos_client.delete_file(photo_to_delete.filename)
                        print(f"步骤5.2: TOS文件删除成功: {photo_to_delete.filename}")
                    except Exception as e:
                        # 记录错误但不中断流程
                        print(f"步骤5.2: 警告 - 删除TOS文件时出错: {str(e)}")
                else:
                    print("步骤5.1: 未找到有效文件名或delete_file方法，跳过TOS文件删除")
                
                # 直接删除Photo记录
                db.session.delete(photo_to_delete)
                print(f"步骤5.3: 已标记Photo记录(ID: {photo_id})为删除")
            else:
                print("步骤5: 无关联的Photo记录，跳过Photo处理")
            
            # 删除生成结果记录
            print(f"步骤6: 标记GenerationResult记录(ID: {result_id})为删除")
            db.session.delete(result)
            print("步骤6.1: 已标记GenerationResult记录为删除")
            
            # 提交事务
            print("步骤7: 提交数据库事务")
            db.session.commit()
            print("步骤7.1: 数据库事务提交成功")
            
            # 验证删除是否成功
            print("步骤8: 验证删除结果")
            # 验证GenerationResult是否被删除
            deleted_result = GenerationResult.query.get(result_id)
            if deleted_result is None:
                print(f"步骤8.1: 验证成功 - 生成结果记录ID {result_id} 已被删除")
            else:
                print(f"步骤8.1: 验证失败 - 生成结果记录ID {result_id} 仍然存在")
            
            # 验证Photo是否被删除
            if photo_id:
                deleted_photo = Photo.query.get(photo_id)
                if deleted_photo is None:
                    print(f"步骤8.2: 验证成功 - Photo记录ID {photo_id} 已被删除")
                else:
                    print(f"步骤8.2: 验证失败 - Photo记录ID {photo_id} 仍然存在")
            
            print(f"=== 删除请求处理完成 - result_id: {result_id} ===")
            return jsonify({'message': '生成的图片删除成功'})
        except Exception as e:
            print(f"步骤7.2: 事务处理过程中发生错误: {str(e)}")
            import traceback
            print(f"错误详细信息: {traceback.format_exc()}")
            raise
    except Exception as e:
        print(f"=== 删除过程中发生严重错误 - result_id: {result_id} ===")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        import traceback
        print(f"完整错误堆栈: {traceback.format_exc()}")
        db.session.rollback()
        print("事务已回滚")
        print(f"=== 删除请求处理失败 - result_id: {result_id} ===")
        return jsonify({'error': f'删除失败: {str(e)}'}), 500
    finally:
        print(f"=== 删除请求处理结束 - result_id: {result_id} ===")



@bp.route('/api/image-to-image', methods=['POST'])
def image_to_image():
    """图生图API"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        if ('image_url' not in data and 'image_base64' not in data) or 'prompt' not in data:
            return jsonify({'error': '缺少必要参数image_url或image_base64，以及prompt'}), 400
        
        # 获取参数
        image_url = data.get('image_url')
        image_base64 = data.get('image_base64')
        prompt = data['prompt']
        negative_prompt = data.get('negative_prompt', '')
        
        # 验证模型名称
        valid_models = ['doubao-seedream-4-0-250828']  # 支持的有效模型列表
        model = data.get('model', 'doubao-seedream-4-0-250828')
        
        # 如果用户提供了模型名称但不在有效列表中，则返回错误
        if model not in valid_models:
            return jsonify({
                'success': False,
                'message': '图片生成失败',
                'error': f'无效的模型名称: {model}。有效的模型名称为: {valid_models}'
            }), 400
        
        size = data.get('size', '2K')
        num_images = data.get('num_images', 1)
        steps = data.get('steps', 30)
        creative_strength = data.get('creative_strength', 0.7)
        watermark = data.get('watermark', False)
        
        # 初始化图像生成器
        generator = ArkImageGenerator()
        
        # 验证图片源
        if image_url and not generator.validate_image_url(image_url):
            return jsonify({
                'success': False,
                'message': '图片生成失败',
                'error': '无效的图片URL'
            }), 400
        
        # 创建生成任务记录
        task = ImageGenerationTask(
            input_image_url=image_url if image_url else None,
            prompt=prompt,
            model=model,
            size=size,
            watermark=watermark,
            status='processing'
        )
        db.session.add(task)
        db.session.flush()  # 获取task.id
        
        # 保存生成参数
        parameters = [
            GenerationParameter(task_id=task.id, parameter_name='prompt', parameter_value=prompt),
            GenerationParameter(task_id=task.id, parameter_name='negative_prompt', parameter_value=negative_prompt),
            GenerationParameter(task_id=task.id, parameter_name='model', parameter_value=model),
            GenerationParameter(task_id=task.id, parameter_name='size', parameter_value=size),
            GenerationParameter(task_id=task.id, parameter_name='steps', parameter_value=str(steps)),
            GenerationParameter(task_id=task.id, parameter_name='creative_strength', parameter_value=str(creative_strength)),
            GenerationParameter(task_id=task.id, parameter_name='watermark', parameter_value=str(watermark))
        ]
        db.session.add_all(parameters)
        
        generated_results = []
        
        # 生成图片（循环生成多张图片）
        for i in range(num_images):
            try:
                # 根据输入类型调用不同的生成方法
                if image_url:
                    result = generator.generate_image_from_url(
                        image_url=image_url,
                        prompt=prompt,
                        model=model,
                        size=size,
                        watermark=watermark,
                        steps=steps,
                        strength=creative_strength,
                        negative_prompt=negative_prompt
                    )
                elif image_base64:
                    # 如果是base64图片，调用处理base64的方法
                    # 注意：这里需要ArkImageGenerator类支持base64输入
                    # 暂时使用与URL相同的参数结构
                    result = generator.generate_image_from_base64(
                        image_base64=image_base64,
                        prompt=prompt,
                        model=model,
                        size=size,
                        watermark=watermark,
                        steps=steps,
                        strength=creative_strength,
                        negative_prompt=negative_prompt
                    )
                
                # 保存API响应到任务记录
                task.api_response = json.dumps(result)
                
                # 处理生成结果
                if "data" in result and result["data"]:
                    generated_url = result["data"][0].get("url")
                    if generated_url:
                        # 创建结果记录
                        gen_result = GenerationResult(
                            task_id=task.id,
                            generated_image_url=generated_url,
                            model=model
                        )
                        db.session.add(gen_result)
                        generated_results.append({
                            'image_url': generated_url,
                            'image_id': gen_result.id
                        })
                
            except Exception as e:
                # 记录单张图片生成失败
                # 保存异常信息到api_response字段
                task.api_response = json.dumps({"error": str(e)})
                print(f"生成第{i+1}张图片失败: {str(e)}")
        
        # 更新任务状态
        if generated_results:
            task.status = 'completed'
            task.completed_at = db.func.current_timestamp()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'task_id': task.id,
                'results': generated_results,
                'message': f'成功生成{len(generated_results)}/{num_images}张图片'
            })
        else:
            task.status = 'failed'
            task.error_message = '所有图片生成失败'
            task.completed_at = db.func.current_timestamp()
            db.session.commit()
            
            return jsonify({
                'success': False,
                'task_id': task.id,
                'results': generated_results,
                'message': '图片生成失败',
                'error': '所有图片生成失败，请检查提示词和图片是否合适'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"图生图请求处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '图片生成失败',
            'error': f'处理请求时出错: {str(e)}'
        }), 500


@bp.route('/api/generate-image', methods=['POST'])
def generate_image():
    """生成图片并上传到TOS"""
    try:
        data = request.get_json()
        
        if not data or 'image_url' not in data:
            return jsonify({'error': '缺少必要参数image_url'}), 400
        
        image_url = data['image_url']
        title = data.get('title', f'Generated Image {int(time.time())}')
        description = data.get('description', '')
        
        # 下载生成的图片
        response = requests.get(image_url, stream=True, timeout=60)
        response.raise_for_status()
        
        # 读取图片内容
        image_content = response.content
        file_size = len(image_content)
        
        # 生成文件名并上传到TOS
        filename = tos_client.generate_filename(f"generated_{int(time.time())}.jpg")
        tos_url = tos_client.upload_file(image_content, filename, 'image/jpeg')
        
        # 创建并上传缩略图
        thumbnail_content = tos_client.create_thumbnail(image_content)
        thumbnail_url = None
        if thumbnail_content:
            thumbnail_url = tos_client.upload_thumbnail(thumbnail_content, filename)
        
        # 获取图片信息
        img_info = tos_client.get_image_info(image_content)
        
        # 计算文件哈希值
        file_hash = tos_client.calculate_file_hash(image_content)
        
        # 保存到数据库
        photo = Photo(
            title=title,
            description=description,
            filename=filename,
            original_filename=f"generated_{int(time.time())}.jpg",
            tos_url=tos_url,
            thumbnail_url=thumbnail_url,
            file_size=file_size,
            width=img_info.get('width', 0),
            height=img_info.get('height', 0),
            mime_type='image/jpeg',
            hash_value=file_hash,
            is_ai_generated=True
        )
        
        db.session.add(photo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'photo': photo.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"保存生成图片失败: {str(e)}")
        return jsonify({'error': f'保存图片时出错: {str(e)}'}), 500