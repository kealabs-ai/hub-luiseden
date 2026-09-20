import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from urllib.parse import quote_plus
from dotenv import load_dotenv
load_dotenv()

def _build_database_url() -> str:
    host = os.getenv("luis_ed_DB_HOST")
    port = os.getenv("luis_ed_DB_PORT")
    name = os.getenv("luis_ed_DB_NAME")
    user = os.getenv("luis_ed_DB_USER")
    password = os.getenv("luis_ed_DB_PASSWORD")

    missing = [
        key for key, value in {
            "luis_ed_DB_HOST": host,
            "luis_ed_DB_PORT": port,
            "luis_ed_DB_NAME": name,
            "luis_ed_DB_USER": user,
            "luis_ed_DB_PASSWORD": password,
        }.items() if not value
    ]
    if missing:
        raise RuntimeError(f"Variáveis de ambiente do banco ausentes: {', '.join(missing)}")

    return f"mysql+pymysql://{user}:{quote_plus(password)}@{host}:{port}/{name}"

DATABASE_URL = _build_database_url()
SECRET_KEY   = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM    = "HS256"

engine       = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
bearer       = HTTPBearer()

class Base(DeclarativeBase): pass

class Manutencao(Base):
    __tablename__ = "manutencoes"
    id            = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id    = Column(String(36),  nullable=False)
    planta_id     = Column(String(36),  nullable=True)
    titulo        = Column(String(255), nullable=False)
    descricao     = Column(Text,        nullable=True)
    data_agendada = Column(String(10),  nullable=False)
    status        = Column(String(50),  default="agendada")
    created_at    = Column(DateTime,    default=datetime.utcnow)
    updated_at    = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

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

app = FastAPI(title="svc-manutencao")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-manutencao"}

class ManutencaoIn(BaseModel):
    titulo: str
    plantaId: Optional[str] = None
    descricao: Optional[str] = None
    dataAgendada: str
    status: str = "agendada"

class ManutencaoUpdate(BaseModel):
    id: str
    titulo: Optional[str] = None
    plantaId: Optional[str] = None
    descricao: Optional[str] = None
    dataAgendada: Optional[str] = None
    status: Optional[str] = None

class ManutencaoGetIn(BaseModel):
    id: str

def _to_dict(m: Manutencao):
    return {"id": m.id, "usuarioId": m.usuario_id, "plantaId": m.planta_id, "titulo": m.titulo,
            "descricao": m.descricao, "dataAgendada": m.data_agendada, "status": m.status,
            "createdAt": m.created_at.isoformat(), "updatedAt": m.updated_at.isoformat()}

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
    m = Manutencao(usuario_id=payload["sub"], titulo=body.titulo, planta_id=body.plantaId,
                   descricao=body.descricao, data_agendada=body.dataAgendada, status=body.status)
    db.add(m); db.commit(); db.refresh(m)
    return _to_dict(m)

@app.post("/v1/eden/manutencao/update")
def update_manutencao(body: ManutencaoUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = db.query(Manutencao).filter_by(id=body.id).first()
    if not m: raise HTTPException(404, "Não encontrado")
    data = body.model_dump(exclude_none=True, exclude={"id"})
    if "plantaId"     in data: m.planta_id     = data.pop("plantaId")
    if "dataAgendada" in data: m.data_agendada = data.pop("dataAgendada")
    for k, v in data.items(): setattr(m, k, v)
    m.updated_at = datetime.utcnow()
    db.commit(); db.refresh(m)
    return _to_dict(m)

@app.post("/v1/eden/manutencao/delete")
def delete_manutencao(body: ManutencaoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = db.query(Manutencao).filter_by(id=body.id).first()
    if not m: raise HTTPException(404, "Não encontrado")
    db.delete(m); db.commit()
    return {"ok": True}
