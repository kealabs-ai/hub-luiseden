import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Integer
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

class Planta(Base):
    __tablename__ = "plantas"
    id          = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    nome        = Column(String(255), nullable=False)
    categoria   = Column(String(100), nullable=True)
    descricao   = Column(Text,        nullable=True)
    preco_cents = Column(Integer,     nullable=False, default=0)
    custo_cents = Column(Integer,     nullable=False, default=0)
    estoque     = Column(Integer,     nullable=False, default=0)
    imagem_url  = Column(String(500), nullable=True)
    ativo       = Column(Boolean,     default=True)
    created_at  = Column(DateTime,    default=datetime.utcnow)
    updated_at  = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    for db in db_manager.get_db():
        yield db

def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token inválido")

app = FastAPI(title="svc-catalogo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(db_manager.engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-catalogo"}

class PlantaIn(BaseModel):
    nome: str
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    precoCents: int = 0
    custoCents: int = 0
    estoque: int = 0
    imagemUrl: Optional[str] = None

class PlantaUpdate(BaseModel):
    id: str
    nome: Optional[str] = None
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    precoCents: Optional[int] = None
    custoCents: Optional[int] = None
    estoque: Optional[int] = None
    imagemUrl: Optional[str] = None
    ativo: Optional[bool] = None

class PlantaDeleteIn(BaseModel):
    id: str

class QuotationApprovalIn(BaseModel):
    cotacaoId: str
    descricao: str
    quantidade: int
    precoCents: int
    custoCents: int

def _to_dict(p: Planta):
    return {"id": p.id, "nome": p.nome, "categoria": p.categoria, "descricao": p.descricao,
            "precoCents": p.preco_cents, "custoCents": p.custo_cents, "estoque": p.estoque, "imagemUrl": p.imagem_url,
            "ativo": p.ativo, "createdAt": p.created_at.isoformat(), "updatedAt": p.updated_at.isoformat()}

@app.get("/v1/eden/catalogo")
def list_plantas(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_to_dict(p) for p in db.query(Planta).filter_by(ativo=True).all()]

@app.get("/v1/eden/catalogo/todos")
def list_plantas_todos(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_to_dict(p) for p in db.query(Planta).all()]

@app.post("/v1/eden/catalogo/get")
def get_planta(body: PlantaDeleteIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    p = db.query(Planta).filter_by(id=body.id).first()
    if not p: raise HTTPException(404, "Não encontrado")
    return _to_dict(p)

@app.post("/v1/eden/catalogo", status_code=201)
def create_planta(body: PlantaIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    p = Planta(nome=body.nome, categoria=body.categoria, descricao=body.descricao,
               preco_cents=body.precoCents, custo_cents=body.custoCents,
               estoque=body.estoque, imagem_url=body.imagemUrl)
    db.add(p); db.commit(); db.refresh(p)
    return _to_dict(p)

@app.post("/v1/eden/catalogo/update")
def update_planta(body: PlantaUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    p = db.query(Planta).filter_by(id=body.id).first()
    if not p: raise HTTPException(404, "Não encontrado")
    data = body.model_dump(exclude_none=True, exclude={"id"})
    if "precoCents" in data: p.preco_cents = data.pop("precoCents")
    if "custoCents" in data: p.custo_cents = data.pop("custoCents")
    if "imagemUrl"  in data: p.imagem_url  = data.pop("imagemUrl")
    for k, v in data.items(): setattr(p, k, v)
    p.updated_at = datetime.utcnow()
    db.commit(); db.refresh(p)
    return _to_dict(p)

@app.post("/v1/eden/catalogo/delete")
def delete_planta(body: PlantaDeleteIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    p = db.query(Planta).filter_by(id=body.id).first()
    if not p: raise HTTPException(404, "Não encontrado")
    p.ativo = False; db.commit()
    return {"ok": True}

@app.post("/v1/eden/catalogo/from-quotation")
def add_from_quotation(body: QuotationApprovalIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    existing = db.query(Planta).filter_by(nome=body.descricao).first()
    if existing:
        existing.estoque += body.quantidade
        existing.preco_cents = body.precoCents
        existing.custo_cents = body.custoCents
        existing.updated_at = datetime.utcnow()
        db.commit(); db.refresh(existing)
        return {"ok": True, "action": "updated", "planta": _to_dict(existing)}
    else:
        p = Planta(nome=body.descricao, preco_cents=body.precoCents,
                   custo_cents=body.custoCents, estoque=body.quantidade)
        db.add(p); db.commit(); db.refresh(p)
        return {"ok": True, "action": "created", "planta": _to_dict(p)}
