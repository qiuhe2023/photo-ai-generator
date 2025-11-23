from app import create_app

# 创建Flask应用实例
app = create_app()

if __name__ == '__main__':
    # 设置最大请求体大小，解决413错误
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
    
    # 启动应用服务器
    app.run(host='0.0.0.0', port=5002, debug=True)