from fastapi import APIRouter, Form
from sztu_sys_module.services.vpn_service import login_vpn

router = APIRouter()

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    """
    登录接口，返回 cookies + 渲染 HTML + JSON 数据
    """
    return login_vpn(username, password)