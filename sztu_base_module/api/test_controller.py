from typing import Optional
from fastapi import APIRouter
from sztu_base_module.models.command.login_command import LoginRequest

router = APIRouter()
# templates = Jinja2Templates(directory="templates")  # 放模板的目录

# POST 接口示例

@router.post("/hello")
def report_hello3(form: LoginRequest):
    return {
        "message": "welcome login!",
        "username": form.username,
        "password": form.password
    }

# GET 接口示例
# http://127.0.0.1:8080/v1/test/hello?username=1
@router.get("/hello")
def say_hello_to_get(username: Optional[str] = None):
    if(username is None):
        return {"message": f"Hello there!What's your name?"}
    return {"message": f"Hello {username}!"}

