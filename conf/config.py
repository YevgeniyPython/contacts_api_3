from pydantic_settings import BaseSettings

from pydantic import EmailStr, Extra

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    mail_username: EmailStr
    mail_password: str
    mail_from: EmailStr
    mail_from_name: str
    mail_port: int
    mail_server: str
    redis_host: str
    redis_port: int
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        extra = 'allow'
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()





