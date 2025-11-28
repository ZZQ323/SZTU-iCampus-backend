# from pydantic import BaseSettings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SZTU ICampus Backend"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    VPN_URL: str = "https://home.sztu.edu.cn/bmportal"
    PLAYWRIGHT_HEADLESS: bool = True

settings = Settings()