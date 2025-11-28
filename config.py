from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SZTU ICampus Backend"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    VPN_URL: str = "https://home.sztu.edu.cn/bmportal"
    PLAYWRIGHT_HEADLESS: bool = True

settings = Settings()