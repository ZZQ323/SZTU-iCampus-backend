from fastapi import FastAPI
from sztu_sys_module.api import login  # 假设 login 是 api 模块的接口

app = FastAPI(title="SZTU ICampus Backend")

# 注册模块路由
app.include_router(login.router, prefix="/v1/login", tags=["Login"])
