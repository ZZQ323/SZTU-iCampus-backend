"""
文件管理模块 API
提供文件上传、下载、删除等功能
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
        # 确保上传目录存在
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        file_info = {
            "file_id": f"FILE{timestamp}",
            "original_name": file.filename,
            "stored_name": filename,
            "file_path": file_path,
            "file_size": len(content),
            "content_type": file.content_type,
            "category": category,
            "uploader_id": current_user.get("person_id"),
            "upload_time": datetime.now().isoformat()
        }
        
        return {
            "code": 0,
            "message": "文件上传成功",
            "data": file_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.get("/{file_id}", summary="下载文件")
async def download_file(file_id: str):
    """下载文件"""
    
    # 模拟文件信息查询
    file_info = {
        "file_id": file_id,
        "original_name": "test_document.pdf",
        "stored_name": "20250115_143000_test_document.pdf",
        "file_path": os.path.join(UPLOAD_DIR, "20250115_143000_test_document.pdf")
    }
    
    if not os.path.exists(file_info["file_path"]):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_info["file_path"],
        filename=file_info["original_name"],
        media_type="application/octet-stream"
    )


@router.delete("/{file_id}", summary="删除文件")
async def delete_file(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """删除文件"""
    
    # 模拟文件删除
    return {
        "code": 0,
        "message": "文件删除成功",
        "data": {"file_id": file_id},
        "timestamp": datetime.now().isoformat()
    }


@router.get("/{file_id}/info", summary="获取文件信息")
async def get_file_info(file_id: str):
    """获取文件信息"""
    
    file_info = {
        "file_id": file_id,
        "original_name": "test_document.pdf",
        "file_size": 2048576,
        "content_type": "application/pdf",
        "category": "document",
        "upload_time": "2025-01-15T14:30:00Z",
        "download_count": 5,
        "is_public": False
    }
    
    return {
        "code": 0,
        "message": "success",
        "data": file_info,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/batch-upload", summary="批量上传文件")
async def batch_upload(
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user)
):
    """批量上传文件"""
    
    results = []
    
    for file in files:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            
            file_info = {
                "file_id": f"FILE{timestamp}",
                "original_name": file.filename,
                "stored_name": filename,
                "file_size": 0,  # 实际应该计算文件大小
                "status": "success"
            }
            results.append(file_info)
            
        except Exception as e:
            results.append({
                "original_name": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "code": 0,
        "message": f"批量上传完成，成功{len([r for r in results if r.get('status') == 'success'])}个",
        "data": {"results": results},
        "timestamp": datetime.now().isoformat()
    }


@router.get("/my-files", summary="获取我的文件列表")
async def get_my_files(
    category: Optional[str] = Query(None, description="文件分类"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量"),
    current_user = Depends(get_current_user)
):
    """获取我的文件列表"""
    
    # 模拟文件列表
    files = [
        {
            "file_id": "FILE20250115001",
            "original_name": "课程设计报告.docx",
            "file_size": 1024576,
            "category": "document",
            "upload_time": "2025-01-15T10:00:00Z",
            "download_count": 3
        },
        {
            "file_id": "FILE20250115002",
            "original_name": "实验数据.xlsx",
            "file_size": 512000,
            "category": "data",
            "upload_time": "2025-01-15T14:30:00Z",
            "download_count": 1
        }
    ]
    
    if category:
        files = [f for f in files if f["category"] == category]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "files": files[offset:offset + limit],
            "pagination": {
                "total": len(files),
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < len(files)
            }
        },
        "timestamp": datetime.now().isoformat()
    } 