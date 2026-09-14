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

def _build_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url and url.strip().lower() not in ("", "null", "none"):
        return url.strip()
    host     = os.getenv("luis_ed_DB_HOST",     "localhost")
    port     = os.getenv("luis_ed_DB_PORT",     "3306")
    name     = os.getenv("luis_ed_DB_NAME",     "luiseden")
    user     = os.getenv("luis_ed_DB_USER",     "luiseden")
    password = os.getenv("luis_ed_DB_PASSWORD", "senha")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

DATABASE_URL = _build_database_url()
SECRET_KEY   = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM    = "HS256"

engine       = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
bearer       = HTTPBearer()

class Base(DeclarativeBase): pass

class Orcamento(Base):
    __tablename__ = "orcamentos"
    id           = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id   = Column(String(36),  nullable=False)
    cliente_nome = Column(String(255), nullable=True)
    descricao    = Column(Text,        nullable=True)
    total_cents  = Column(Integer,     nullable=False, default=0)
    status       = Column(String(50),  default="pendente")
    validade     = Column(String(10),  nullable=True)
    created_at   = Column(DateTime,    default=datetime.utcnow)
    updated_at   = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

class ItemOrcamento(Base):
    __tablename__ = "itens_orcamento"
    id           = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    orcamento_id = Column(String(36),  nullable=False)
    descricao    = Column(String(500), nullable=False)
    quantidade   = Column(Integer,     nullable=False, default=1)
    preco_cents  = Column(Integer,     nullable=False, default=0)

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

app = FastAPI(title="svc-orcamentos")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-orcamentos"}

class OrcamentoIn(BaseModel):
    clienteNome: Optional[str] = None
    descricao: Optional[str] = None
    totalCents: int = 0
    validade: Optional[str] = None

class OrcamentoUpdate(BaseModel):
    id: str
    clienteNome: Optional[str] = None
    descricao: Optional[str] = None
    totalCents: Optional[int] = None
    status: Optional[str] = None
    validade: Optional[str] = None

class OrcamentoGetIn(BaseModel):
    id: str

def _to_dict(o: Orcamento):
    return {"id": o.id, "usuarioId": o.usuario_id, "clienteNome": o.cliente_nome,
            "descricao": o.descricao, "totalCents": o.total_cents, "status": o.status,
            "validade": o.validade, "createdAt": o.created_at.isoformat(), "updatedAt": o.updated_at.isoformat()}

@app.get("/v1/eden/orcamentos")
def list_orcamentos(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_to_dict(o) for o in db.query(Orcamento).order_by(Orcamento.created_at.desc()).all()]

@app.post("/v1/eden/orcamentos/get")
def get_orcamento(body: OrcamentoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = db.query(Orcamento).filter_by(id=body.id).first()
    if not o: raise HTTPException(404, "Não encontrado")
    return _to_dict(o)

@app.post("/v1/eden/orcamentos", status_code=201)
def create_orcamento(body: OrcamentoIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = Orcamento(usuario_id=payload["sub"], cliente_nome=body.clienteNome,
                  descricao=body.descricao, total_cents=body.totalCents, validade=body.validade)
    db.add(o); db.commit(); db.refresh(o)
    return _to_dict(o)

@app.post("/v1/eden/orcamentos/update")
def update_orcamento(body: OrcamentoUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = db.query(Orcamento).filter_by(id=body.id).first()
    if not o: raise HTTPException(404, "Não encontrado")
    data = body.model_dump(exclude_none=True, exclude={"id"})
    if "clienteNome" in data: o.cliente_nome = data.pop("clienteNome")
    if "totalCents"  in data: o.total_cents  = data.pop("totalCents")
    for k, v in data.items(): setattr(o, k, v)
    o.updated_at = datetime.utcnow()
    db.commit(); db.refresh(o)
    return _to_dict(o)

@app.post("/v1/eden/orcamentos/delete")
def delete_orcamento(body: OrcamentoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = db.query(Orcamento).filter_by(id=body.id).first()
    if not o: raise HTTPException(404, "Não encontrado")
    db.delete(o); db.commit()
    return {"ok": True}
