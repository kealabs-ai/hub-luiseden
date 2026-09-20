import os
from dataclasses import dataclass
from typing import Generator
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: str
    name: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        values = {
            "luis_ed_DB_HOST": os.getenv("luis_ed_DB_HOST"),
            "luis_ed_DB_PORT": os.getenv("luis_ed_DB_PORT"),
            "luis_ed_DB_NAME": os.getenv("luis_ed_DB_NAME"),
            "luis_ed_DB_USER": os.getenv("luis_ed_DB_USER"),
            "luis_ed_DB_PASSWORD": os.getenv("luis_ed_DB_PASSWORD"),
        }
        missing = [key for key, value in values.items() if not value]
        if missing:
            raise RuntimeError(f"Variáveis de ambiente do banco ausentes: {', '.join(missing)}")

        return cls(
            host=values["luis_ed_DB_HOST"],
            port=values["luis_ed_DB_PORT"],
            name=values["luis_ed_DB_NAME"],
            user=values["luis_ed_DB_USER"],
            password=values["luis_ed_DB_PASSWORD"],
        )

    @property
    def url(self) -> str:
        return (
            f"mysql+pymysql://{self.user}:{quote_plus(self.password)}@"
            f"{self.host}:{self.port}/{self.name}"
        )


class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(
            config.url,
            pool_pre_ping=True,
            pool_recycle=280,
            pool_size=5,
            max_overflow=10,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
        )

    @classmethod
    def from_env(cls) -> "DatabaseManager":
        return cls(DatabaseConfig.from_env())

    def get_db(self) -> Generator[Session, None, None]:
        db = self.SessionLocal()
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
