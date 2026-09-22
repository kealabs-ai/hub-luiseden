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

class Manutencao(Base):
    __tablename__ = "manutencoes"
    id                  = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id          = Column(String(36),  nullable=False)
    cliente_id          = Column(String(36),  nullable=True)
    planta_id           = Column(String(36),  nullable=True)
    titulo              = Column(String(255), nullable=False)
    descricao           = Column(Text,        nullable=True)
    data_agendada       = Column(String(10),  nullable=False)
    status              = Column(String(50),  default="agendada")
    prioridade          = Column(String(20),  default="normal")
    frequencia          = Column(String(20),  default="custom")
    valor_cents         = Column(Integer,     default=0)
    equipe              = Column(String(100), nullable=True)
    endereco            = Column(String(500), nullable=True)
    telefone            = Column(String(50),  nullable=True)
    proxima_manutencao  = Column(String(10),  nullable=True)
    created_at          = Column(DateTime,    default=datetime.utcnow)
    updated_at          = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    for db in db_manager.get_db():
        yield db

def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token inválido")

app = FastAPI(title="svc-manutencao")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(db_manager.engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-manutencao"}

class ManutencaoIn(BaseModel):
    titulo: str
    clienteId: Optional[str] = None
    plantaId: Optional[str] = None
    descricao: Optional[str] = None
    dataAgendada: str
    status: str = "agendada"
    prioridade: str = "normal"
    frequencia: str = "custom"
    valorCents: int = 0
    equipe: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    proximaManutencao: Optional[str] = None

class ManutencaoUpdate(BaseModel):
    id: str
    titulo: Optional[str] = None
    clienteId: Optional[str] = None
    plantaId: Optional[str] = None
    descricao: Optional[str] = None
    dataAgendada: Optional[str] = None
    status: Optional[str] = None
    prioridade: Optional[str] = None
    frequencia: Optional[str] = None
    valorCents: Optional[int] = None
    equipe: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    proximaManutencao: Optional[str] = None

class ManutencaoGetIn(BaseModel):
    id: str

def _to_dict(m: Manutencao):
    return {
        "id": m.id,
        "usuarioId": m.usuario_id,
        "clienteId": m.cliente_id,
        "plantaId": m.planta_id,
        "titulo": m.titulo,
        "descricao": m.descricao,
        "dataAgendada": m.data_agendada,
        "status": m.status,
        "prioridade": m.prioridade,
        "frequencia": m.frequencia,
        "valorCents": m.valor_cents,
        "equipe": m.equipe,
        "endereco": m.endereco,
        "telefone": m.telefone,
        "proximaManutencao": m.proxima_manutencao,
        "createdAt": m.created_at.isoformat(),
        "updatedAt": m.updated_at.isoformat()
    }

@app.get("/v1/eden/manutencao")
def list_manutencoes(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_to_dict(m) for m in db.query(Manutencao).order_by(Manutencao.data_agendada).all()]

@app.post("/v1/eden/manutencao/get")
def get_manutencao(body: ManutencaoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = db.query(Manutencao).filter_by(id=body.id).first()
    if not m: raise HTTPException(404, "Não encontrado")
    return _to_dict(m)

@app.post("/v1/eden/manutencao", status_code=201)
def create_manutencao(body: ManutencaoIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = Manutencao(
        usuario_id=payload["sub"],
        cliente_id=body.clienteId,
        titulo=body.titulo,
        planta_id=body.plantaId,
        descricao=body.descricao,
        data_agendada=body.dataAgendada,
        status=body.status,
        prioridade=body.prioridade,
        frequencia=body.frequencia,
        valor_cents=body.valorCents,
        equipe=body.equipe,
        endereco=body.endereco,
        telefone=body.telefone,
        proxima_manutencao=body.proximaManutencao
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return _to_dict(m)

@app.post("/v1/eden/manutencao/update")
def update_manutencao(body: ManutencaoUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = db.query(Manutencao).filter_by(id=body.id).first()
    if not m: raise HTTPException(404, "Não encontrado")
    
    data = body.model_dump(exclude_none=True, exclude={"id"})
    
    # Mapear camelCase para snake_case
    field_mapping = {
        "clienteId": "cliente_id",
        "plantaId": "planta_id",
        "dataAgendada": "data_agendada",
        "valorCents": "valor_cents",
        "proximaManutencao": "proxima_manutencao"
    }
    
    for camel_key, snake_key in field_mapping.items():
        if camel_key in data:
            data[snake_key] = data.pop(camel_key)
    
    for k, v in data.items():
        setattr(m, k, v)
    
    m.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(m)
    return _to_dict(m)

@app.post("/v1/eden/manutencao/delete")
def delete_manutencao(body: ManutencaoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = db.query(Manutencao).filter_by(id=body.id).first()
    if not m: raise HTTPException(404, "Não encontrado")
    db.delete(m)
    db.commit()
    return {"ok": True}
