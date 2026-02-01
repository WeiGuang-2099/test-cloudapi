#!/bin/bash

# Cloud Run 部署脚本
# 使用方法: ./deploy.sh

# 配置变量
PROJECT_ID="your-project-id"  # 替换为你的 GCP 项目 ID
SERVICE_NAME="parse-api"       # Cloud Run 服务名称
REGION="asia-east1"            # 区域（可选择离你更近的区域）
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "开始部署到 Cloud Run..."

# 1. 确保已登录 gcloud
echo "检查 gcloud 认证状态..."
gcloud auth list

# 2. 设置项目
echo "设置 GCP 项目..."
gcloud config set project ${PROJECT_ID}

# 3. 启用必要的 API
echo "启用 Cloud Run 和 Container Registry API..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 4. 构建 Docker 镜像
echo "构建 Docker 镜像..."
docker build -t ${IMAGE_NAME} .

# 5. 推送镜像到 Google Container Registry
echo "推送镜像到 GCR..."
docker push ${IMAGE_NAME}

# 6. 部署到 Cloud Run
echo "部署到 Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 300

# 7. 获取服务 URL
echo "获取服务 URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format 'value(status.url)')

echo "=========================================="
echo "部署完成！"
echo "服务 URL: ${SERVICE_URL}"
echo "=========================================="
echo ""
echo "测试命令:"
echo "curl ${SERVICE_URL}/"
echo ""
echo "或使用 Python 脚本:"
echo "python call_api.py ${SERVICE_URL}"
