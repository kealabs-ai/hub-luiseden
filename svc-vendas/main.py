import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean
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
    id          = Column(String(36), primary_key=True)
    nome        = Column(String(255), nullable=False)
    categoria   = Column(String(100), nullable=True)
    descricao   = Column(Text, nullable=True)
    preco_cents = Column(Integer, nullable=False, default=0)
    custo_cents = Column(Integer, nullable=False, default=0)
    estoque     = Column(Integer, nullable=False, default=0)
    imagem_url  = Column(String(500), nullable=True)
    ativo       = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow)

class Venda(Base):
    __tablename__ = "vendas"
    id           = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id   = Column(String(36),  nullable=False)
    cliente_nome = Column(String(255), nullable=True)
    data_venda   = Column(DateTime,    nullable=True)
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

class ItemVendaIn(BaseModel):
    plantaId: str
    quantidade: int
    precoCents: int

class Transacao(Base):
    __tablename__ = "transacoes"
    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id  = Column(String(36), nullable=False)
    tipo        = Column(String(20), nullable=False)
    categoria   = Column(String(100), nullable=True)
    descricao   = Column(String(500), nullable=True)
    valor_cents = Column(Integer, nullable=False)
    data        = Column(String(10), nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow)

class VendaCancelIn(BaseModel):
    id: str
    motivo: Optional[str] = None

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
    dataVenda: Optional[datetime] = None
    totalCents: int
    status: str = "concluida"
    observacoes: Optional[str] = None
    itens: list[ItemVendaIn] = []

class VendaUpdate(BaseModel):
    id: str
    clienteNome: Optional[str] = None
    dataVenda: Optional[datetime] = None
    totalCents: Optional[int] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

class VendaGetIn(BaseModel):
    id: str

def _to_dict(v: Venda, db: Session):
    items = db.query(ItemVenda).filter_by(venda_id=v.id).all()
    item_data = []
    for item in items:
        planta = db.query(Planta).filter_by(id=item.planta_id).first()
        item_data.append({"plantaId": item.planta_id, "quantidade": item.quantidade,
                          "precoCents": item.preco_cents,
                          "custoCents": planta.custo_cents if planta else 0})
    return {"id": v.id, "usuarioId": v.usuario_id, "clienteNome": v.cliente_nome,
            "dataVenda": v.data_venda.isoformat(),
            "totalCents": v.total_cents, "status": v.status, "observacoes": v.observacoes,
            "createdAt": v.created_at.isoformat(), "updatedAt": v.updated_at.isoformat(), "itens": item_data}

@app.get("/v1/eden/vendas")
def list_vendas(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_to_dict(v, db) for v in db.query(Venda).order_by(Venda.created_at.desc()).all()]

@app.post("/v1/eden/vendas/get")
def get_venda(body: VendaGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    v = db.query(Venda).filter_by(id=body.id).first()
    if not v: raise HTTPException(404, "Não encontrado")
    return _to_dict(v, db)

@app.post("/v1/eden/vendas", status_code=201)
def create_venda(body: VendaIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    quantities = {}
    for item in body.itens:
        if item.quantidade < 1:
            raise HTTPException(400, "A quantidade deve ser maior que zero")
        quantities[item.plantaId] = quantities.get(item.plantaId, 0) + item.quantidade

    plants = {}
    for planta_id, quantity in quantities.items():
        planta = db.query(Planta).filter_by(id=planta_id, ativo=True).with_for_update().first()
        if not planta:
            raise HTTPException(404, f"Planta não encontrada: {planta_id}")
        if planta.estoque < quantity:
            raise HTTPException(409, f"Estoque insuficiente para {planta.nome}. Disponível: {planta.estoque}")
        plants[planta_id] = planta

    v = Venda(usuario_id=payload["sub"], cliente_nome=body.clienteNome,
              data_venda=body.dataVenda or datetime.utcnow(), total_cents=body.totalCents,
              status=body.status, observacoes=body.observacoes)
    db.add(v)
    db.flush()
    for item in body.itens:
        plants[item.plantaId].estoque -= item.quantidade
        db.add(ItemVenda(venda_id=v.id, planta_id=item.plantaId,
                         quantidade=item.quantidade, preco_cents=item.precoCents))
    db.commit(); db.refresh(v)
    return _to_dict(v, db)

@app.post("/v1/eden/vendas/cancel")
def cancel_venda(body: VendaCancelIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    venda = db.query(Venda).filter_by(id=body.id).with_for_update().first()
    if not venda:
        raise HTTPException(404, "Venda não encontrada")
    if venda.status == "cancelada":
        raise HTTPException(409, "A venda já está cancelada")

    items = db.query(ItemVenda).filter_by(venda_id=venda.id).all()
    for item in items:
        planta = db.query(Planta).filter_by(id=item.planta_id).with_for_update().first()
        if planta:
            planta.estoque += item.quantidade

    motivo = body.motivo or "Sem motivo informado"
    venda.status = "cancelada"
    venda.observacoes = f"{venda.observacoes or ''} Cancelamento: {motivo}".strip()
    db.add(Transacao(usuario_id=payload["sub"], tipo="saida", categoria="cancelamento_venda",
                     descricao=f"Cancelamento da venda {venda.id}: {motivo}",
                     valor_cents=venda.total_cents,
                     data=(venda.data_venda or datetime.utcnow()).date().isoformat()))
    venda.updated_at = datetime.utcnow()
    db.commit(); db.refresh(venda)
    return _to_dict(venda, db)

@app.post("/v1/eden/vendas/update")
def update_venda(body: VendaUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    v = db.query(Venda).filter_by(id=body.id).first()
    if not v: raise HTTPException(404, "Não encontrado")
    data = body.model_dump(exclude_none=True, exclude={"id"})
    if "clienteNome" in data: v.cliente_nome = data.pop("clienteNome")
    if "dataVenda" in data: v.data_venda = data.pop("dataVenda")
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
    vendas = db.query(Venda).filter(Venda.status != "cancelada").all()
    return {"totalVendas": len(vendas),
            "totalCents": sum(v.total_cents for v in vendas),
            "concluidas": sum(1 for v in vendas if v.status == "concluida"),
            "canceladas": sum(1 for v in vendas if v.status == "cancelada")}
