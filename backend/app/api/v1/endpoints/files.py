"""
文件管理模块 API
"""
import os
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, File, UploadFile, Depends, Query
from fastapi.responses import FileResponse
from app.api.deps import get_current_user

router = APIRouter()
UPLOAD_DIR = "backend/uploads"

@router.post("/upload", summary="上传文件")
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = Query("general", description="文件分类"),
    current_user = Depends(get_current_user)
):
    """上传文件"""
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "code": 0,
            "message": "文件上传成功",
            "data": {
                "file_id": f"FILE{timestamp}",
                "original_name": file.filename,
                "file_size": len(content),
                "upload_time": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.delete("/{file_id}", summary="删除文件")
async def delete_file(file_id: str, current_user = Depends(get_current_user)):
    """删除文件"""
    try:
        deleted = False
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                if filename.startswith(file_id.replace("FILE", "")):
                    os.remove(os.path.join(UPLOAD_DIR, filename))
                    deleted = True
                    break
        
        if not deleted:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return {
            "code": 0,
            "message": "文件删除成功",
            "data": {"file_id": file_id},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}") 