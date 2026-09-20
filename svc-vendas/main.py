import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from dotenv import load_dotenv
load_dotenv()

from database import DatabaseManager

db_manager = DatabaseManager.from_env()
SessionLocal = db_manager.SessionLocal
DATABASE_URL = db_manager.config.url
SECRET_KEY   = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM    = "HS256"

bearer       = HTTPBearer()

class Base(DeclarativeBase): pass

class Venda(Base):
    __tablename__ = "vendas"
    id           = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id   = Column(String(36),  nullable=False)
    cliente_nome = Column(String(255), nullable=True)
    total_cents  = Column(Integer,     nullable=False, default=0)
    status       = Column(String(50),  default="concluida")
    observacoes  = Column(Text,        nullable=True)
    created_at   = Column(DateTime,    default=datetime.utcnow)
    updated_at   = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

class ItemVenda(Base):
    __tablename__ = "itens_venda"
    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    venda_id    = Column(String(36), nullable=False)
    planta_id   = Column(String(36), nullable=False)
    quantidade  = Column(Integer,    nullable=False, default=1)
    preco_cents = Column(Integer,    nullable=False, default=0)

def get_db():
    for db in db_manager.get_db():
        yield db

def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token inválido")

app = FastAPI(title="svc-vendas")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(db_manager.engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-vendas"}

class VendaIn(BaseModel):
    clienteNome: Optional[str] = None
    totalCents: int
    status: str = "concluida"
    observacoes: Optional[str] = None

class VendaUpdate(BaseModel):
    id: str
    clienteNome: Optional[str] = None
    totalCents: Optional[int] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

class VendaGetIn(BaseModel):
    id: str

def _to_dict(v: Venda):
    return {"id": v.id, "usuarioId": v.usuario_id, "clienteNome": v.cliente_nome,
            "totalCents": v.total_cents, "status": v.status, "observacoes": v.observacoes,
            "createdAt": v.created_at.isoformat(), "updatedAt": v.updated_at.isoformat()}

@app.get("/v1/eden/vendas")
def list_vendas(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_to_dict(v) for v in db.query(Venda).order_by(Venda.created_at.desc()).all()]

@app.post("/v1/eden/vendas/get")
def get_venda(body: VendaGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    v = db.query(Venda).filter_by(id=body.id).first()
    if not v: raise HTTPException(404, "Não encontrado")
    return _to_dict(v)

@app.post("/v1/eden/vendas", status_code=201)
def create_venda(body: VendaIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    v = Venda(usuario_id=payload["sub"], cliente_nome=body.clienteNome,
              total_cents=body.totalCents, status=body.status, observacoes=body.observacoes)
    db.add(v); db.commit(); db.refresh(v)
    return _to_dict(v)

@app.post("/v1/eden/vendas/update")
def update_venda(body: VendaUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    v = db.query(Venda).filter_by(id=body.id).first()
    if not v: raise HTTPException(404, "Não encontrado")
    data = body.model_dump(exclude_none=True, exclude={"id"})
    if "clienteNome" in data: v.cliente_nome = data.pop("clienteNome")
    if "totalCents"  in data: v.total_cents  = data.pop("totalCents")
    for k, val in data.items(): setattr(v, k, val)
    v.updated_at = datetime.utcnow()
    db.commit(); db.refresh(v)
    return _to_dict(v)

@app.post("/v1/eden/vendas/delete")
def delete_venda(body: VendaGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    v = db.query(Venda).filter_by(id=body.id).first()
    if not v: raise HTTPException(404, "Não encontrado")
    db.delete(v); db.commit()
    return {"ok": True}

@app.get("/v1/eden/vendas/dashboard")
def dashboard(db: Session = Depends(get_db), payload=Depends(verify_token)):
    vendas = db.query(Venda).all()
    return {"totalVendas": len(vendas),
            "totalCents": sum(v.total_cents for v in vendas),
            "concluidas": sum(1 for v in vendas if v.status == "concluida"),
            "canceladas": sum(1 for v in vendas if v.status == "cancelada")}
