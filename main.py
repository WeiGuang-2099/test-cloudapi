from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from typing import Optional

app = FastAPI(title="解析 API", description="一个用于数据解析的 API 服务")

# 定义请求数据模型
class ParseRequest(BaseModel):
    text: str
    format: Optional[str] = "json"

# 定义响应数据模型
class ParseResponse(BaseModel):
    success: bool
    data: dict
    message: str

@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "status": "healthy",
        "message": "解析 API 正在运行",
        "version": "1.0.0"
    }

@app.post("/parse", response_model=ParseResponse)
async def parse_data(request: ParseRequest):
    """
    解析文本数据的主要端点
    
    参数:
    - text: 要解析的文本
    - format: 输出格式（默认为 json）
    """
    try:
        # 这里实现你的解析逻辑
        # 示例：简单的 JSON 解析
        if request.format == "json":
            try:
                parsed_data = json.loads(request.text)
            except json.JSONDecodeError:
                # 如果不是 JSON，创建一个简单的结构化数据
                parsed_data = {
                    "original_text": request.text,
                    "word_count": len(request.text.split()),
                    "char_count": len(request.text),
                    "lines": request.text.split('\n')
                }
        else:
            parsed_data = {
                "text": request.text,
                "format": request.format
            }
        
        return ParseResponse(
            success=True,
            data=parsed_data,
            message="解析成功"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析错误: {str(e)}")

@app.get("/health")
async def health_check():
    """Kubernetes/Cloud Run 健康检查"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
