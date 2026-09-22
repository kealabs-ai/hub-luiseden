import os, uuid, json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from dotenv import load_dotenv
load_dotenv()

from database import DatabaseManager

db_manager = DatabaseManager.from_env()
SessionLocal = db_manager.SessionLocal
DATABASE_URL = db_manager.config.url
SECRET_KEY = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM = "HS256"

bearer = HTTPBearer()

class Base(DeclarativeBase): pass

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    telefone = Column(String(20), nullable=True)
    data_aniversario = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    for db in db_manager.get_db():
        yield db

def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token inválido")

app = FastAPI(title="svc-clientes")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(db_manager.engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-clientes"}

class ClienteIn(BaseModel):
    nome: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    data_aniversario: Optional[str] = None

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    data_aniversario: Optional[str] = None

def _to_dict(c: Cliente):
    return {
        "id": c.id,
        "nome": c.nome,
        "email": c.email,
        "telefone": c.telefone,
        "data_aniversario": c.data_aniversario,
        "created_at": c.created_at.isoformat()
    }

@app.get("/v1/eden/clientes")
def list_clientes(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_to_dict(c) for c in db.query(Cliente).all()]

@app.get("/v1/eden/clientes/{cliente_id}")
def get_cliente(cliente_id: str, db: Session = Depends(get_db), payload=Depends(verify_token)):
    c = db.query(Cliente).filter_by(id=cliente_id).first()
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    return _to_dict(c)

@app.post("/v1/eden/clientes", status_code=201)
def create_cliente(body: ClienteIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    c = Cliente(
        nome=body.nome,
        email=body.email,
        telefone=body.telefone,
        data_aniversario=body.data_aniversario
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return _to_dict(c)

@app.put("/v1/eden/clientes/{cliente_id}")
def update_cliente(cliente_id: str, body: ClienteUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    c = db.query(Cliente).filter_by(id=cliente_id).first()
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    
    data = body.model_dump(exclude_none=True)
    for k, v in data.items():
        setattr(c, k, v)
    c.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(c)
    return _to_dict(c)

@app.delete("/v1/eden/clientes/{cliente_id}")
def delete_cliente(cliente_id: str, db: Session = Depends(get_db), payload=Depends(verify_token)):
    c = db.query(Cliente).filter_by(id=cliente_id).first()
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    db.delete(c)
    db.commit()
    return {"ok": True}
