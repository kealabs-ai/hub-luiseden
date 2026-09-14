import os, uuid, enum
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://luiseden:senha@localhost:3306/luiseden")
SECRET_KEY   = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM    = "HS256"

engine       = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
bearer       = HTTPBearer()

def _hash(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

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

def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token inválido")

def require_admin(payload=Depends(verify_token)):
    if payload.get("role") != "admin":
        raise HTTPException(403, "Acesso negado")
    return payload

app = FastAPI(title="svc-usuarios")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-usuarios"}

class UsuarioIn(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    role: str = "operador"

class UsuarioUpdate(BaseModel):
    id: str
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    ativo: Optional[bool] = None

class UsuarioGetIn(BaseModel):
    id: str

def _to_dict(u: Usuario):
    return {"id": u.id, "nome": u.nome, "email": u.email, "role": u.role,
            "ativo": u.ativo, "createdAt": u.created_at.isoformat()}

@app.get("/v1/eden/usuarios")
def list_usuarios(db: Session = Depends(get_db), payload=Depends(require_admin)):
    return [_to_dict(u) for u in db.query(Usuario).all()]

@app.post("/v1/eden/usuarios/get")
def get_usuario(body: UsuarioGetIn, db: Session = Depends(get_db), payload=Depends(require_admin)):
    u = db.query(Usuario).filter_by(id=body.id).first()
    if not u: raise HTTPException(404, "Não encontrado")
    return _to_dict(u)

@app.post("/v1/eden/usuarios", status_code=201)
def create_usuario(body: UsuarioIn, db: Session = Depends(get_db), payload=Depends(require_admin)):
    if db.query(Usuario).filter_by(email=body.email).first():
        raise HTTPException(409, "E-mail já cadastrado")
    u = Usuario(nome=body.nome, email=body.email, senha_hash=_hash(body.senha), role=body.role)
    db.add(u); db.commit(); db.refresh(u)
    return _to_dict(u)

@app.post("/v1/eden/usuarios/update")
def update_usuario(body: UsuarioUpdate, db: Session = Depends(get_db), payload=Depends(require_admin)):
    u = db.query(Usuario).filter_by(id=body.id).first()
    if not u: raise HTTPException(404, "Não encontrado")
    data = body.model_dump(exclude_none=True, exclude={"id"})
    for k, v in data.items(): setattr(u, k, v)
    u.updated_at = datetime.utcnow()
    db.commit(); db.refresh(u)
    return _to_dict(u)

@app.post("/v1/eden/usuarios/delete")
def delete_usuario(body: UsuarioGetIn, db: Session = Depends(get_db), payload=Depends(require_admin)):
    u = db.query(Usuario).filter_by(id=body.id).first()
    if not u: raise HTTPException(404, "Não encontrado")
    u.ativo = False; db.commit()
    return {"ok": True}

class SenhaUpdate(BaseModel):
    id: str
    senha: str

@app.post("/v1/eden/usuarios/senha")
def update_senha(body: SenhaUpdate, db: Session = Depends(get_db), payload=Depends(require_admin)):
    u = db.query(Usuario).filter_by(id=body.id).first()
    if not u: raise HTTPException(404, "Não encontrado")
    u.senha_hash = _hash(body.senha)
    u.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True}

@app.post("/v1/eden/usuarios/minha-senha")
def update_minha_senha(body: SenhaUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    if payload["sub"] != body.id:
        raise HTTPException(403, "Acesso negado")
    u = db.query(Usuario).filter_by(id=body.id).first()
    if not u: raise HTTPException(404, "Não encontrado")
    u.senha_hash = _hash(body.senha)
    u.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True}
