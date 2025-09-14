from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    # DB ayarları
    DB_DRIVER: str = 'ODBC Driver 17 for SQL Server'
    DB_SERVER: str = 'DESKTOP-V79CIPP\\SQLEXPRESS01'
    DB_NAME: str = 'NotesAppDB'

    # JWT ayarları
    JWT_SECRET: str = 'PABFK_1005_KEBEB'
    JWT_ALGORITHMS: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = '.env'

    # DATABASE_URL property (Windows Auth)
    @property
    def DATABASE_URL(self) -> str:
        return URL.create(
            "mssql+pyodbc",
            host=self.DB_SERVER,
            database=self.DB_NAME,
            query={
                "driver": self.DB_DRIVER,
                "trusted_connection": "yes",  # Windows Authentication
                "TrustServerCertificate": "yes"
            }
        )


settings = Settings()
