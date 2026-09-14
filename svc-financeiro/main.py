import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, DateTime, Integer
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

class Transacao(Base):
    __tablename__ = "transacoes"
    id          = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id  = Column(String(36),  nullable=False)
    tipo        = Column(String(20),  nullable=False)  # entrada | saida
    categoria   = Column(String(100), nullable=True)
    descricao   = Column(String(500), nullable=True)
    valor_cents = Column(Integer,     nullable=False)
    data        = Column(String(10),  nullable=False)
    created_at  = Column(DateTime,    default=datetime.utcnow)
    updated_at  = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

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

app = FastAPI(title="svc-financeiro")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-financeiro"}

class TransacaoIn(BaseModel):
    tipo: str
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    valorCents: int
    data: str

class TransacaoUpdate(BaseModel):
    id: str
    tipo: Optional[str] = None
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    valorCents: Optional[int] = None
    data: Optional[str] = None

class TransacaoGetIn(BaseModel):
    id: str

def _to_dict(t: Transacao):
    return {"id": t.id, "usuarioId": t.usuario_id, "tipo": t.tipo, "categoria": t.categoria,
            "descricao": t.descricao, "valorCents": t.valor_cents, "data": t.data,
            "createdAt": t.created_at.isoformat(), "updatedAt": t.updated_at.isoformat()}

@app.get("/v1/eden/financeiro")
def list_transacoes(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_to_dict(t) for t in db.query(Transacao).order_by(Transacao.data.desc()).all()]

@app.post("/v1/eden/financeiro/get")
def get_transacao(body: TransacaoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    t = db.query(Transacao).filter_by(id=body.id).first()
    if not t: raise HTTPException(404, "Não encontrado")
    return _to_dict(t)

@app.post("/v1/eden/financeiro", status_code=201)
def create_transacao(body: TransacaoIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    t = Transacao(usuario_id=payload["sub"], tipo=body.tipo, categoria=body.categoria,
                  descricao=body.descricao, valor_cents=body.valorCents, data=body.data)
    db.add(t); db.commit(); db.refresh(t)
    return _to_dict(t)

@app.post("/v1/eden/financeiro/update")
def update_transacao(body: TransacaoUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    t = db.query(Transacao).filter_by(id=body.id).first()
    if not t: raise HTTPException(404, "Não encontrado")
    data = body.model_dump(exclude_none=True, exclude={"id"})
    if "valorCents" in data: t.valor_cents = data.pop("valorCents")
    for k, v in data.items(): setattr(t, k, v)
    t.updated_at = datetime.utcnow()
    db.commit(); db.refresh(t)
    return _to_dict(t)

@app.post("/v1/eden/financeiro/delete")
def delete_transacao(body: TransacaoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    t = db.query(Transacao).filter_by(id=body.id).first()
    if not t: raise HTTPException(404, "Não encontrado")
    db.delete(t); db.commit()
    return {"ok": True}

@app.get("/v1/eden/financeiro/dashboard")
def dashboard(db: Session = Depends(get_db), payload=Depends(verify_token)):
    rows = db.query(Transacao).all()
    entradas = sum(t.valor_cents for t in rows if t.tipo == "entrada")
    saidas   = sum(t.valor_cents for t in rows if t.tipo == "saida")
    return {"totalEntradas": entradas, "totalSaidas": saidas, "saldo": entradas - saidas,
            "totalTransacoes": len(rows)}
