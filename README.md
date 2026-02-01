# Cloud Run API 部署教程

这是一个完整的教程，教你如何使用 Google Cloud Run 部署一个 API 服务，并通过脚本调用它。

## 📋 项目结构

```
.
├── main.py              # FastAPI 应用主文件
├── requirements.txt     # Python 依赖
├── Dockerfile          # Docker 容器配置
├── .dockerignore       # Docker 忽略文件
├── deploy.sh           # 部署脚本
├── call_api.py         # API 调用脚本
└── README.md           # 本文档
```

## 🚀 快速开始

### 部署方式选择

本项目支持两种部署方式：

1. **GitHub Actions 自动部署（推荐）** - 推送代码自动部署到 Cloud Run
2. **本地手动部署** - 使用脚本或 gcloud 命令部署

### 方式 1: GitHub Actions 自动部署（推荐）

这是最简单的部署方式！设置一次后，每次推送到 `main` 分支都会自动部署。

**详细设置指南：** 请查看 [GITHUB_SETUP.md](GITHUB_SETUP.md)

**快速步骤：**

1. 在 GitHub 创建仓库并推送代码
2. 在 GitHub 仓库设置中添加两个 Secrets：
   - `GCP_PROJECT_ID`: 你的 GCP 项目 ID
   - `GCP_SA_KEY`: 服务账号密钥的完整 JSON 内容
3. 推送到 `main` 分支，自动触发部署！

完整设置说明见 [GITHUB_SETUP.md](GITHUB_SETUP.md)

### 方式 2: 本地手动部署

#### 前置要求

1. **安装 Google Cloud SDK**
   ```bash
   # macOS
   brew install google-cloud-sdk

   # Ubuntu/Debian
   sudo apt-get install google-cloud-sdk

   # 或从官网下载: https://cloud.google.com/sdk/docs/install
   ```

2. **安装 Docker**
   - 下载并安装 Docker Desktop: https://www.docker.com/products/docker-desktop

3. **创建 GCP 项目**
   - 访问 https://console.cloud.google.com
   - 创建新项目或选择现有项目
   - 记下项目 ID

4. **安装 Python 依赖**（用于本地测试和调用脚本）
   ```bash
   pip install requests
   ```

### 步骤 1: 初始化 GCP

```bash
# 登录 Google Cloud
gcloud auth login

# 设置默认项目（替换 YOUR-PROJECT-ID）
gcloud config set project YOUR-PROJECT-ID

# 登录 Docker 到 GCR
gcloud auth configure-docker
```

### 步骤 2: 本地测试（可选）

在部署之前，你可以先在本地测试 API：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py

# 在另一个终端测试
curl http://localhost:8080/
curl -X POST http://localhost:8080/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "测试文本", "format": "json"}'
```

### 步骤 3: 部署到 Cloud Run

**方法 1: 使用部署脚本**

```bash
# 1. 编辑 deploy.sh，修改 PROJECT_ID
nano deploy.sh  # 将 "your-project-id" 替换为你的项目 ID

# 2. 添加执行权限
chmod +x deploy.sh

# 3. 运行部署脚本
./deploy.sh
```

**方法 2: 手动部署**

```bash
# 设置变量
PROJECT_ID="your-project-id"
SERVICE_NAME="parse-api"
REGION="asia-east1"

# 构建并推送镜像
docker build -t gcr.io/${PROJECT_ID}/${SERVICE_NAME} .
docker push gcr.io/${PROJECT_ID}/${SERVICE_NAME}

# 部署到 Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated
```

部署完成后，会显示服务 URL，例如：
```
https://parse-api-xxxxx-xx.a.run.app
```

### 步骤 4: 调用 API

**方法 1: 使用 Python 脚本**

```bash
# 运行调用脚本
python call_api.py https://your-service-url.run.app
```

**方法 2: 使用 curl**

```bash
# 健康检查
curl https://your-service-url.run.app/

# 调用解析 API
curl -X POST https://your-service-url.run.app/parse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "这是要解析的文本",
    "format": "json"
  }'
```

**方法 3: 使用 Python requests**

```python
import requests
import json

api_url = "https://your-service-url.run.app"

# 调用 API
response = requests.post(
    f"{api_url}/parse",
    json={
        "text": "要解析的文本",
        "format": "json"
    }
)

result = response.json()
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## 📊 API 文档

### 端点

#### `GET /`
健康检查端点

**响应示例:**
```json
{
  "status": "healthy",
  "message": "解析 API 正在运行",
  "version": "1.0.0"
}
```

#### `POST /parse`
解析文本数据

**请求体:**
```json
{
  "text": "要解析的文本内容",
  "format": "json"  // 可选，默认为 "json"
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "original_text": "要解析的文本内容",
    "word_count": 5,
    "char_count": 9,
    "lines": ["要解析的文本内容"]
  },
  "message": "解析成功"
}
```

#### `GET /health`
Kubernetes/Cloud Run 健康检查

**响应示例:**
```json
{
  "status": "ok"
}
```

### 交互式文档

部署后，访问以下 URL 查看自动生成的 API 文档：
- Swagger UI: `https://your-service-url.run.app/docs`
- ReDoc: `https://your-service-url.run.app/redoc`

## 🔧 自定义解析逻辑

在 `main.py` 的 `parse_data` 函数中修改解析逻辑：

```python
@app.post("/parse", response_model=ParseResponse)
async def parse_data(request: ParseRequest):
    # 在这里添加你的自定义解析逻辑
    parsed_data = your_custom_parser(request.text)
    
    return ParseResponse(
        success=True,
        data=parsed_data,
        message="解析成功"
    )
```

## 💰 成本估算

Cloud Run 采用按使用量计费：
- **免费额度**: 每月 200 万次请求免费
- **付费**: 超出后约 $0.40/百万次请求
- **内存**: $0.0000025/GB-秒
- **CPU**: $0.00002400/vCPU-秒

对于小型项目，Cloud Run 几乎是免费的！

## 🔐 安全建议

### 1. 添加身份验证

修改部署命令，移除 `--allow-unauthenticated`：

```bash
gcloud run deploy parse-api \
  --image gcr.io/${PROJECT_ID}/parse-api \
  --region asia-east1 \
  --no-allow-unauthenticated
```

调用时需要添加认证：

```python
import google.auth.transport.requests
import google.oauth2.id_token

auth_req = google.auth.transport.requests.Request()
id_token = google.oauth2.id_token.fetch_id_token(auth_req, api_url)

headers = {"Authorization": f"Bearer {id_token}"}
response = requests.post(f"{api_url}/parse", json=data, headers=headers)
```

### 2. 添加 API 密钥

在 `main.py` 中添加简单的 API 密钥验证：

```python
from fastapi import Header, HTTPException

API_KEY = "your-secret-api-key"

@app.post("/parse")
async def parse_data(
    request: ParseRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="无效的 API 密钥")
    # ... 其余代码
```

### 3. 设置速率限制

可以使用 `slowapi` 库添加速率限制：

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/parse")
@limiter.limit("10/minute")
async def parse_data(request: ParseRequest):
    # ... 代码
```

## 🐛 故障排查

### 问题 1: 构建失败

```bash
# 检查 Docker 是否运行
docker ps

# 清理旧镜像
docker system prune -a
```

### 问题 2: 部署失败

```bash
# 检查日志
gcloud run services logs read parse-api --region=asia-east1

# 验证镜像
gcloud container images list
```

### 问题 3: API 无响应

```bash
# 检查服务状态
gcloud run services describe parse-api --region=asia-east1

# 测试健康检查
curl https://your-service-url.run.app/health
```

## 📚 扩展阅读

- [Cloud Run 官方文档](https://cloud.google.com/run/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Docker 入门](https://docs.docker.com/get-started/)

## 🤝 需要帮助？

如有问题，可以：
1. 查看 Cloud Run 日志
2. 检查 API 文档 `/docs` 端点
3. 使用 `call_api.py` 脚本进行调试

---

祝你部署顺利！🎉
