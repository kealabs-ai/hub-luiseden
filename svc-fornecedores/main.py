import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from dotenv import load_dotenv
import httpx
load_dotenv()

from database import DatabaseManager

db_manager = DatabaseManager.from_env()
SessionLocal = db_manager.SessionLocal
DATABASE_URL = db_manager.config.url
SECRET_KEY   = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM    = "HS256"
CATALOGO_URL = os.getenv("CATALOGO_URL", "http://localhost:8002")

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

class Cotacao(Base):
    __tablename__ = "cotacoes"
    id              = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    fornecedor_id   = Column(String(36),  ForeignKey("fornecedores.id"), nullable=False)
    descricao       = Column(String(255), nullable=False)
    quantidade      = Column(Integer,     nullable=False, default=1)
    preco_custo_cents = Column(Integer,   nullable=False, default=0)
    preco_venda_cents = Column(Integer,   nullable=False, default=0)
    aprovada        = Column(Boolean,     default=False)
    ativo           = Column(Boolean,     default=True)
    created_at      = Column(DateTime,    default=datetime.utcnow)
    updated_at      = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    for db in db_manager.get_db():
        yield db

def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token inválido")

app = FastAPI(title="svc-fornecedores")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(db_manager.engine)

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

class CotacaoIn(BaseModel):
    fornecedorId: str
    descricao: str
    quantidade: int = 1
    precoCustoCents: int
    precoVendaCents: int

class CotacaoUpdate(BaseModel):
    id: str
    descricao: Optional[str] = None
    quantidade: Optional[int] = None
    precoCustoCents: Optional[int] = None
    precoVendaCents: Optional[int] = None
    aprovada: Optional[bool] = None
    ativo: Optional[bool] = None

class CotacaoGetIn(BaseModel):
    id: str

class CotacaoApproveIn(BaseModel):
    id: str

def _to_dict(f: Fornecedor):
    return {"id": f.id, "nome": f.nome, "email": f.email, "telefone": f.telefone,
            "cpfCnpj": f.cpf_cnpj, "endereco": f.endereco, "categoria": f.categoria,
            "ativo": f.ativo, "createdAt": f.created_at.isoformat(), "updatedAt": f.updated_at.isoformat()}

def _cotacao_to_dict(c: Cotacao):
    return {"id": c.id, "fornecedorId": c.fornecedor_id, "descricao": c.descricao,
            "quantidade": c.quantidade, "precoCustoCents": c.preco_custo_cents,
            "precoVendaCents": c.preco_venda_cents, "aprovada": c.aprovada, "ativo": c.ativo,
            "createdAt": c.created_at.isoformat(), "updatedAt": c.updated_at.isoformat()}

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

@app.get("/v1/eden/fornecedores/cotacoes")
def list_cotacoes(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_cotacao_to_dict(c) for c in db.query(Cotacao).filter_by(ativo=True).all()]

@app.post("/v1/eden/fornecedores/cotacoes/get")
def get_cotacao(body: CotacaoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    c = db.query(Cotacao).filter_by(id=body.id).first()
    if not c: raise HTTPException(404, "Não encontrado")
    return _cotacao_to_dict(c)

@app.post("/v1/eden/fornecedores/cotacoes", status_code=201)
def create_cotacao(body: CotacaoIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    c = Cotacao(fornecedor_id=body.fornecedorId, descricao=body.descricao,
                quantidade=body.quantidade, preco_custo_cents=body.precoCustoCents,
                preco_venda_cents=body.precoVendaCents)
    db.add(c); db.commit(); db.refresh(c)
    return _cotacao_to_dict(c)

@app.post("/v1/eden/fornecedores/cotacoes/update")
def update_cotacao(body: CotacaoUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    c = db.query(Cotacao).filter_by(id=body.id).first()
    if not c: raise HTTPException(404, "Não encontrado")
    data = body.model_dump(exclude_none=True, exclude={"id"})
    for k, v in data.items():
        if k == "precoCustoCents": setattr(c, "preco_custo_cents", v)
        elif k == "precoVendaCents": setattr(c, "preco_venda_cents", v)
        else: setattr(c, k, v)
    c.updated_at = datetime.utcnow()
    db.commit(); db.refresh(c)
    return _cotacao_to_dict(c)

@app.post("/v1/eden/fornecedores/cotacoes/delete")
def delete_cotacao(body: CotacaoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    c = db.query(Cotacao).filter_by(id=body.id).first()
    if not c: raise HTTPException(404, "Não encontrado")
    c.ativo = False; db.commit()
    return {"ok": True}

@app.post("/v1/eden/fornecedores/cotacoes/approve")
def approve_cotacao(body: CotacaoApproveIn, db: Session = Depends(get_db), creds: HTTPAuthorizationCredentials = Depends(bearer)):
    c = db.query(Cotacao).filter_by(id=body.id).first()
    if not c: raise HTTPException(404, "Cotação não encontrada")
    c.aprovada = True
    c.updated_at = datetime.utcnow()
    db.commit()
    
    try:
        token = creds.credentials
        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client() as client:
            response = client.post(
                f"{CATALOGO_URL}/v1/eden/catalogo/from-quotation",
                json={
                    "cotacaoId": c.id,
                    "descricao": c.descricao,
                    "quantidade": c.quantidade,
                    "precoCents": c.preco_venda_cents,
                    "custoCents": c.preco_custo_cents
                },
                headers=headers,
                timeout=10
            )
            if response.status_code not in [200, 201]:
                print(f"Erro ao integrar com catálogo: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro ao integrar com catálogo: {e}")
    
    return _cotacao_to_dict(c)
