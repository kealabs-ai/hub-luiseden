import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", 3306))
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "hub_luis_eden")
        self.url = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(self.config.url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    @classmethod
    def from_env(cls):
        return cls(DatabaseConfig())

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
