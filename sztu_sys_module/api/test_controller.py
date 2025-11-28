from fastapi import APIRouter, Form

router = APIRouter()
# templates = Jinja2Templates(directory="templates")  # 放模板的目录

# POST 接口示例
@router.post("/hello")
def say_hello(username: str = Form(...), password: str = Form(...)):
    return {"message": f"Hello {username}!"}

# GET 接口示例
# http://127.0.0.1:8080/v1/test/hello?username=1
@router.get("/hello")
def say_hello_get(username: str):
    return {"message": f"Hello {username}!"}