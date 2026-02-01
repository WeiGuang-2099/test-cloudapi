#!/bin/bash

# GitHub Actions 设置验证脚本
# 使用方法: bash verify_setup.sh

echo "========================================"
echo "GitHub Actions 设置验证"
echo "========================================"
echo ""

# 检查 git 仓库
echo "1. 检查 Git 仓库..."
if [ -d .git ]; then
    echo "   ✓ Git 仓库已初始化"
else
    echo "   ✗ Git 仓库未初始化"
    echo "   运行: git init"
    exit 1
fi

# 检查 .gitignore
echo "2. 检查 .gitignore..."
if [ -f .gitignore ]; then
    if grep -q "*.json" .gitignore; then
        echo "   ✓ .gitignore 已配置（保护 JSON 密钥文件）"
    else
        echo "   ⚠ .gitignore 存在但可能没有保护 JSON 文件"
    fi
else
    echo "   ✗ .gitignore 文件不存在"
fi

# 检查 GitHub Actions workflow
echo "3. 检查 GitHub Actions workflow..."
if [ -f .github/workflows/deploy-to-cloudrun.yml ]; then
    echo "   ✓ GitHub Actions workflow 已配置"
else
    echo "   ✗ GitHub Actions workflow 文件不存在"
    exit 1
fi

# 检查必需文件
echo "4. 检查必需的项目文件..."
required_files=("main.py" "Dockerfile" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file 存在"
    else
        echo "   ✗ $file 不存在"
        exit 1
    fi
done

# 检查 Docker
echo "5. 检查 Docker..."
if command -v docker &> /dev/null; then
    echo "   ✓ Docker 已安装"
    if docker ps &> /dev/null; then
        echo "   ✓ Docker 正在运行"
    else
        echo "   ⚠ Docker 已安装但未运行"
    fi
else
    echo "   ⚠ Docker 未安装（本地测试需要）"
fi

# 检查 gcloud
echo "6. 检查 Google Cloud SDK..."
if command -v gcloud &> /dev/null; then
    echo "   ✓ gcloud 已安装"
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -n "$PROJECT_ID" ]; then
        echo "   ✓ 当前项目: $PROJECT_ID"
    else
        echo "   ⚠ 未设置默认项目"
    fi
else
    echo "   ⚠ gcloud 未安装（本地部署需要）"
fi

# 检查是否有远程仓库
echo "7. 检查 GitHub 远程仓库..."
if git remote -v | grep -q origin; then
    REMOTE_URL=$(git remote get-url origin)
    echo "   ✓ 已设置远程仓库: $REMOTE_URL"
else
    echo "   ⚠ 未设置 GitHub 远程仓库"
    echo "   运行: git remote add origin https://github.com/your-username/your-repo.git"
fi

# 检查敏感文件
echo "8. 检查敏感文件..."
if ls *.json 1> /dev/null 2>&1; then
    echo "   ⚠ 发现 JSON 文件，请确保它们不会被提交到 Git！"
    if git check-ignore *.json 2>/dev/null; then
        echo "   ✓ JSON 文件已被 .gitignore 忽略"
    else
        echo "   ✗ JSON 文件可能会被提交！请检查 .gitignore"
    fi
else
    echo "   ✓ 未发现敏感 JSON 文件"
fi

echo ""
echo "========================================"
echo "验证完成"
echo "========================================"
echo ""
echo "下一步："
echo "1. 确保在 GitHub 仓库设置中添加了以下 Secrets："
echo "   - GCP_PROJECT_ID: 你的 GCP 项目 ID"
echo "   - GCP_SA_KEY: 服务账号密钥的完整 JSON 内容"
echo ""
echo "2. 推送代码到 GitHub："
echo "   git add ."
echo "   git commit -m \"Initial commit with GitHub Actions\""
echo "   git push -u origin main"
echo ""
echo "3. 在 GitHub 仓库的 Actions 标签查看部署进度"
echo ""
echo "详细设置指南: GITHUB_SETUP.md"
echo ""
