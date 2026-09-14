import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://luiseden:senha@localhost:3306/luiseden")
SECRET_KEY   = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM    = "HS256"

engine       = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
bearer       = HTTPBearer()

class Base(DeclarativeBase): pass

class Fornecedor(Base):
    __tablename__ = "fornecedores"
    id         = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    nome       = Column(String(255), nullable=False)
    email      = Column(String(255), nullable=True)
    telefone   = Column(String(50),  nullable=True)
    cpf_cnpj   = Column(String(20),  nullable=True)
    endereco   = Column(String(500), nullable=True)
    categoria  = Column(String(100), nullable=True)
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

app = FastAPI(title="svc-fornecedores")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-fornecedores"}

class FornecedorIn(BaseModel):
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    cpfCnpj: Optional[str] = None
    endereco: Optional[str] = None
    categoria: Optional[str] = None

class FornecedorUpdate(BaseModel):
    id: str
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    cpfCnpj: Optional[str] = None
    endereco: Optional[str] = None
    categoria: Optional[str] = None
    ativo: Optional[bool] = None

class FornecedorGetIn(BaseModel):
    id: str

def _to_dict(f: Fornecedor):
    return {"id": f.id, "nome": f.nome, "email": f.email, "telefone": f.telefone,
            "cpfCnpj": f.cpf_cnpj, "endereco": f.endereco, "categoria": f.categoria,
            "ativo": f.ativo, "createdAt": f.created_at.isoformat(), "updatedAt": f.updated_at.isoformat()}

@app.get("/v1/eden/fornecedores")
def list_fornecedores(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_to_dict(f) for f in db.query(Fornecedor).filter_by(ativo=True).all()]

@app.post("/v1/eden/fornecedores/get")
def get_fornecedor(body: FornecedorGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    f = db.query(Fornecedor).filter_by(id=body.id).first()
    if not f: raise HTTPException(404, "Não encontrado")
    return _to_dict(f)

@app.post("/v1/eden/fornecedores", status_code=201)
def create_fornecedor(body: FornecedorIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    f = Fornecedor(nome=body.nome, email=body.email, telefone=body.telefone,
                   cpf_cnpj=body.cpfCnpj, endereco=body.endereco, categoria=body.categoria)
    db.add(f); db.commit(); db.refresh(f)
    return _to_dict(f)

@app.post("/v1/eden/fornecedores/update")
def update_fornecedor(body: FornecedorUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    f = db.query(Fornecedor).filter_by(id=body.id).first()
    if not f: raise HTTPException(404, "Não encontrado")
    data = body.model_dump(exclude_none=True, exclude={"id"})
    if "cpfCnpj" in data: f.cpf_cnpj = data.pop("cpfCnpj")
    for k, v in data.items(): setattr(f, k, v)
    f.updated_at = datetime.utcnow()
    db.commit(); db.refresh(f)
    return _to_dict(f)

@app.post("/v1/eden/fornecedores/delete")
def delete_fornecedor(body: FornecedorGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    f = db.query(Fornecedor).filter_by(id=body.id).first()
    if not f: raise HTTPException(404, "Não encontrado")
    f.ativo = False; db.commit()
    return {"ok": True}
