# 使用官方 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY main.py .

# Cloud Run 会设置 PORT 环境变量，默认使用 8080
ENV PORT=8080

# 暴露端口
EXPOSE 8080

# 运行应用
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
