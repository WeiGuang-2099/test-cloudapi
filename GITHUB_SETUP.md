# GitHub Actions 部署到 Cloud Run 设置指南

## 前提条件

1. 一个 Google Cloud Platform (GCP) 项目
2. 一个 GitHub 仓库
3. GCP 服务账号密钥（JSON 文件）

## 步骤 1: 准备 GCP 服务账号

### 1.1 创建服务账号（如果还没有）

```bash
# 设置你的项目 ID
export PROJECT_ID="your-project-id"

# 创建服务账号
gcloud iam service-accounts create github-actions \
    --description="Service account for GitHub Actions" \
    --display-name="GitHub Actions"
```

### 1.2 授予必要的权限

```bash
# 服务账号邮箱
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# 授予 Cloud Run Admin 权限
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

# 授予 Storage Admin 权限（用于 GCR/Container Registry 推送）
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.admin"

# 授予 Artifact Registry 写入权限（推送镜像必需）
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.writer"

# 授予 Artifact Registry 管理员权限（首次推送时自动创建仓库需要 createOnPush）
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.admin"

# 授予 Service Account User 权限
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"
```

### 1.3 创建并下载密钥

```bash
# 创建密钥文件
gcloud iam service-accounts keys create key.json \
    --iam-account=${SA_EMAIL}
```

**重要：** 这个 `key.json` 文件包含敏感信息，不要提交到 Git！

## 步骤 2: 启用必要的 GCP API

**重要：** GitHub Actions 的 `setup-gcloud` 需要 Cloud Resource Manager API，否则会报错 "does not have permission to access projects instance"。

```bash
# 必须先启用 Cloud Resource Manager API（setup-gcloud 依赖它）
gcloud services enable cloudresourcemanager.googleapis.com

# 启用 Cloud Run API
gcloud services enable run.googleapis.com

# 启用 Container Registry API
gcloud services enable containerregistry.googleapis.com

# 启用 Artifact Registry API（workflow 已改用 Artifact Registry 推送镜像）
gcloud services enable artifactregistry.googleapis.com

# 启用 Cloud Build API（可选，用于更快的构建）
gcloud services enable cloudbuild.googleapis.com
```

或在浏览器中启用： [Cloud Resource Manager API](https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview)，
选择你的项目后点击「启用」。

## 步骤 2.5: 创建 Artifact Registry 仓库（必做一次）

workflow 使用 Artifact Registry 推送镜像，需先手动创建一个仓库，否则会报错。

**在 GCP 网页上操作：**

1. 打开 [Artifact Registry](https://console.cloud.google.com/artifacts)
2. 确认左上角选对项目（如 `plasma-streamer-448423-a3`）
3. 点击 **「创建仓库」**
4. 填写：
   - **名称**：`cloud-run`（必须与 workflow 里 `AR_REPO` 一致）
   - **格式**：Docker
   - **模式**：标准
   - **位置类型**：区域
   - **区域**：asia-east1（与 workflow 里 `REGION` 一致）
5. 点击 **「创建」**

完成后无需再改，之后每次部署都会往这个仓库推送镜像。

## 步骤 3: 在 GitHub 设置 Secrets

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret** 并添加以下 secrets：

### 必需的 Secrets：

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `GCP_PROJECT_ID` | 你的 GCP **项目 ID**（英文+数字，如 `my-project-123`） | 必须是项目 ID，不能是项目名称或项目编号。在 GCP 控制台「项目设置」中查看。 |
| `GCP_SA_KEY` | 服务账号密钥的完整 JSON 内容 | 从 `key.json` 复制完整内容 |

### 如何复制服务账号密钥：

#### Windows (PowerShell):
```powershell
Get-Content key.json | Set-Clipboard
```

#### macOS/Linux:
```bash
cat key.json | pbcopy  # macOS
cat key.json | xclip -selection clipboard  # Linux
```

或者直接用文本编辑器打开 `key.json`，复制所有内容。

## 步骤 4: 推送代码到 GitHub

```bash
# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/your-username/your-repo.git

# 添加文件
git add .

# 提交
git commit -m "Initial commit with Cloud Run deployment"

# 推送到 GitHub
git push -u origin main
```

## 步骤 5: 验证部署

1. 推送代码后，访问 GitHub 仓库的 **Actions** 标签
2. 查看 "Deploy to Cloud Run" workflow 的运行状态
3. 部署成功后，在 workflow 日志中找到服务 URL
4. 访问该 URL 测试你的 API

## 自定义配置

### 修改服务配置

编辑 [.github/workflows/deploy-to-cloudrun.yml](.github/workflows/deploy-to-cloudrun.yml) 文件：

```yaml
env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  SERVICE_NAME: parse-api  # 修改服务名称
  REGION: asia-east1       # 修改部署区域
```

### 修改资源配置

在 workflow 文件的 `Deploy to Cloud Run` 步骤中修改：

```yaml
flags: |
  --allow-unauthenticated
  --memory=512Mi           # 调整内存
  --cpu=1                  # 调整 CPU
  --max-instances=10       # 调整最大实例数
  --timeout=300            # 调整超时时间（秒）
```

## 常见问题

### 1. 部署失败：权限不足

**错误：** `Permission denied` 或 `403 Forbidden`

**解决方案：** 确保服务账号有正确的权限（参见步骤 1.2）

### 2. Docker 推送失败

**错误：** `unauthorized: authentication required`

**解决方案：** 确保 `GCP_SA_KEY` secret 设置正确，包含完整的 JSON 内容

### 3. 服务无法访问

**错误：** 部署成功但无法访问服务

**解决方案：**
- 检查 Cloud Run 服务是否设置为允许未经身份验证的访问
- 确保应用监听正确的端口（8080）

### 4. 如何查看日志

```bash
# 查看 Cloud Run 服务日志
gcloud run services logs read parse-api --region=asia-east1 --limit=50
```

或者在 GCP Console 中：
Cloud Run → 选择服务 → Logs 标签

## 手动部署（备用方案）

如果 GitHub Actions 遇到问题，你也可以使用本地部署脚本：

```bash
# 修改 deploy.sh 中的 PROJECT_ID
# 然后运行：
bash deploy.sh
```

## 安全最佳实践

1. ✅ **不要**将服务账号密钥提交到 Git
2. ✅ 定期轮换服务账号密钥
3. ✅ 使用最小权限原则
4. ✅ 为生产环境使用单独的服务账号
5. ✅ 考虑使用 Workload Identity Federation（更安全的认证方式）

## 监控和维护

### 查看部署状态
```bash
gcloud run services describe parse-api --region=asia-east1
```

### 查看实时流量
```bash
gcloud run services logs tail parse-api --region=asia-east1
```

### 更新服务配置
```bash
gcloud run services update parse-api \
    --region=asia-east1 \
    --memory=1Gi \
    --max-instances=20
```

## 下一步

- [ ] 设置自定义域名
- [ ] 添加 CI/CD 测试步骤
- [ ] 配置环境变量
- [ ] 设置监控和告警
- [ ] 实现蓝绿部署或金丝雀部署

## 支持

如果遇到问题，请检查：
- [Cloud Run 文档](https://cloud.google.com/run/docs)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [这个项目的 Issues](https://github.com/your-username/your-repo/issues)
