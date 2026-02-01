# 快速开始指南 - GitHub Actions 部署到 Cloud Run

## 最快 5 分钟部署

### 步骤 1: 准备 GCP 服务账号密钥（1分钟）

如果你已经有服务账号密钥文件（*.json），跳到步骤 2。

否则，运行以下命令创建：

```bash
# 设置你的项目 ID
export PROJECT_ID="your-project-id"

# 创建服务账号
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions"

# 授予权限
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"

# 创建密钥文件
gcloud iam service-accounts keys create key.json \
    --iam-account=${SA_EMAIL}
```

### 步骤 2: 在 GitHub 创建仓库（1分钟）

1. 访问 https://github.com/new
2. 创建一个新仓库（例如：`my-cloudrun-api`）
3. 不要初始化 README、.gitignore 或 license（我们已经有了）

### 步骤 3: 设置 GitHub Secrets（2分钟）

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加两个 secrets：

**Secret 1: GCP_PROJECT_ID**
- Name: `GCP_PROJECT_ID`
- Value: 你的 GCP 项目 ID（例如：`my-project-123456`）

**Secret 2: GCP_SA_KEY**
- Name: `GCP_SA_KEY`
- Value: 打开 `key.json` 文件，复制**完整内容**粘贴进去

### 步骤 4: 推送代码到 GitHub（1分钟）

```bash
# 在项目目录中运行：
git add .
git commit -m "Initial commit with GitHub Actions deployment"
git branch -M main
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

### 步骤 5: 查看部署（立即）

1. 访问你的 GitHub 仓库
2. 点击 **Actions** 标签
3. 你会看到 "Deploy to Cloud Run" workflow 正在运行
4. 等待约 2-3 分钟完成
5. 部署成功后，在日志中找到你的服务 URL！

## 验证设置

在推送之前，可以运行验证脚本：

```bash
bash verify_setup.sh
```

## 测试你的 API

部署成功后，使用以下命令测试：

```bash
# 替换为你的服务 URL
export API_URL="https://parse-api-xxxxx-xx.a.run.app"

# 健康检查
curl $API_URL/

# 测试解析端点
curl -X POST $API_URL/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World", "format": "json"}'

# 或使用 Python 脚本
python call_api.py $API_URL
```

## 常见问题

### 问题：部署失败，显示权限错误

**解决方案：** 确保服务账号有正确的权限（参见步骤 1）

### 问题：找不到 GCP_SA_KEY

**解决方案：**
1. 打开 `key.json` 文件
2. 复制**完整内容**（从 `{` 到 `}`，包括所有内容）
3. 粘贴到 GitHub Secret 中

### 问题：Docker 推送失败

**解决方案：** 确保启用了 Container Registry API：

```bash
gcloud services enable containerregistry.googleapis.com
```

## 后续步骤

- [ ] 为生产环境设置自定义域名
- [ ] 添加环境变量配置
- [ ] 设置监控和告警
- [ ] 添加 CI/CD 测试步骤

## 需要更多帮助？

查看详细文档：
- [完整 GitHub Actions 设置指南](GITHUB_SETUP.md)
- [项目 README](README.md)
