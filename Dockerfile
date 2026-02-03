# 使用官方轻量级 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 防止 Python 生成 .pyc 文件，并让日志立即输出
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖 (编译 asyncpg 可能需要)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# 复制源代码
COPY src/ ./src/

# 启动命令
CMD ["python", "-m", "src.main"]