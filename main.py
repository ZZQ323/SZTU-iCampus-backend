from fastapi import FastAPI
from sztu_sys_module.api import usr_controller  # 假设 login 是 api 模块的接口
from sztu_sys_module.api import test_controller
app = FastAPI(title="SZTU ICampus Backend")

# 注册模块路由
app.include_router(test_controller.router, prefix="/v1/test", tags=["Test"])
app.include_router(usr_controller.router, prefix="/v1/usr", tags=["System"])
