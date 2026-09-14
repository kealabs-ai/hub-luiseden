import os, uuid, enum
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://luiseden:senha@localhost:3306/luiseden")
SECRET_KEY   = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM    = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 8

engine       = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
bearer       = HTTPBearer()

def _hash(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def _verify(p: str, h: str) -> bool:
    try:
        return bcrypt.checkpw(p.encode(), h.encode())
    except Exception:
        return False

class Base(DeclarativeBase): pass

class RoleEnum(str, enum.Enum):
    admin    = "admin"
    operador = "operador"
    cliente  = "cliente"

class Usuario(Base):
    __tablename__ = "usuarios"
    id         = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    nome       = Column(String(255), nullable=False)
    email      = Column(String(255), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    role       = Column(SAEnum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.operador)
    ativo      = Column(Boolean,     default=True)
    created_at = Column(DateTime,    default=datetime.utcnow)
    updated_at = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def _init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.query(Usuario).filter_by(email="admin@luiseden.com.br").first():
            db.add(Usuario(nome="Admin", email="admin@luiseden.com.br",
                           senha_hash=_hash("admin123"), role=RoleEnum.admin))
            db.commit()

def _make_token(user: Usuario) -> str:
    exp = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user.id, "role": user.role, "exp": exp}, SECRET_KEY, ALGORITHM)

def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token inválido")

app = FastAPI(title="svc-auth")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    _init_db()

class LoginIn(BaseModel):
    email: EmailStr
    senha: str

class AuthOut(BaseModel):
    id: str
    nome: str
    email: str
    role: str
    accessToken: str

@app.post("/v1/eden/auth/login", response_model=AuthOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter_by(email=body.email, ativo=True).first()
    if not user or not _verify(body.senha, user.senha_hash):
        raise HTTPException(401, "Credenciais inválidas")
    return AuthOut(id=user.id, nome=user.nome, email=user.email,
                   role=user.role, accessToken=_make_token(user))

@app.get("/v1/eden/auth/me")
def me(payload=Depends(verify_token)):
    return payload

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-auth"}
