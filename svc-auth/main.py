import os, uuid, enum, json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import jwt, JWTError
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum, Text, text
from sqlalchemy.orm import DeclarativeBase, Session

from database import DatabaseManager

db_manager = DatabaseManager.from_env()
SessionLocal = db_manager.SessionLocal
DATABASE_URL = db_manager.config.url
SECRET_KEY   = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM    = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 8

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
    permissoes = Column(Text, nullable=True)
    ativo      = Column(Boolean,     default=True)
    created_at = Column(DateTime,    default=datetime.utcnow)
    updated_at = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    for db in db_manager.get_db():
        yield db

def _ensure_admin_user(db: Session):
    admin = db.query(Usuario).filter_by(email="admin@luiseden.com.br").first()
    if not admin:
        db.add(Usuario(nome="Admin", email="admin@luiseden.com.br",
                       senha_hash=_hash("admin123"), role=RoleEnum.admin))
        db.commit()
        return

    updated = False
    if admin.role != RoleEnum.admin:
        admin.role = RoleEnum.admin
        updated = True
    if not admin.ativo:
        admin.ativo = True
        updated = True
    if not _verify("admin123", admin.senha_hash):
        admin.senha_hash = _hash("admin123")
        updated = True

    if updated:
        db.commit()


def _init_db():
    Base.metadata.create_all(db_manager.engine)
    with SessionLocal() as db:
        _ensure_admin_user(db)

def _make_token(user: Usuario) -> str:
    exp = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user.id, "role": user.role, "exp": exp}, SECRET_KEY, ALGORITHM)

def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token inválido")

app = FastAPI(title="svc-auth")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://peru-lemur-870410.hostingersite.com",
        "https://srv1023256.hstgr.cloud",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

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

    permissoes: list[str] = []

def _get_permissions(user: Usuario):
    if user.role == RoleEnum.admin or user.role == "admin":
        return ["dashboard", "catalog", "sales", "budget", "cashflow", "maintenance", "supplier", "users"]
    if user.permissoes:
        try:
            return json.loads(user.permissoes)
        except json.JSONDecodeError:
            pass
    return {"operador": ["dashboard", "catalog", "sales", "cashflow"], "cliente": ["dashboard"]}.get(str(user.role), ["dashboard"])

@app.post("/v1/eden/auth/login", response_model=AuthOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter_by(email=body.email, ativo=True).first()
    if not user or not _verify(body.senha, user.senha_hash):
        raise HTTPException(401, "Credenciais inválidas")
    return AuthOut(id=user.id, nome=user.nome, email=user.email,
                   role=user.role, accessToken=_make_token(user),
                   permissoes=_get_permissions(user))

@app.get("/v1/eden/auth/me")
def me(payload=Depends(verify_token)):
    return payload

@app.get("/health")
def health():
    with db_manager.engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok", "service": "svc-auth"}
