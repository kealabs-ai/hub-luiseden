import os, uuid, enum
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Enum as SAEnum, Text, Integer, Numeric
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from dotenv import load_dotenv

from database import DatabaseManager

load_dotenv()

db_manager = DatabaseManager.from_env()
SessionLocal = db_manager.SessionLocal
DATABASE_URL = db_manager.config.url
SECRET_KEY   = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM    = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 8

bearer       = HTTPBearer()

def _hash(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def _verify(p: str, h: str) -> bool:
    try:
        return bcrypt.checkpw(p.encode(), h.encode())
    except Exception:
        return False

class Base(DeclarativeBase): pass

class RoleEnum(str, enum.Enum):
    admin     = "admin"
    operador  = "operador"
    cliente   = "cliente"

class Usuario(Base):
    __tablename__ = "usuarios"
    id         = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    nome       = Column(String(255), nullable=False)
    email      = Column(String(255), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    role       = Column(SAEnum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.operador)
    ativo      = Column(Boolean,     default=True)
    created_at = Column(DateTime,    default=datetime.utcnow)
    updated_at = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

class Planta(Base):
    __tablename__ = "plantas"
    id          = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    nome        = Column(String(255), nullable=False)
    categoria   = Column(String(100), nullable=True)
    descricao   = Column(Text,        nullable=True)
    preco_cents = Column(Integer,     nullable=False, default=0)
    estoque     = Column(Integer,     nullable=False, default=0)
    imagem_url  = Column(String(500), nullable=True)
    ativo       = Column(Boolean,     default=True)
    created_at  = Column(DateTime,    default=datetime.utcnow)
    updated_at  = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

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

class Manutencao(Base):
    __tablename__ = "manutencoes"
    id           = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id   = Column(String(36),  nullable=False)
    planta_id    = Column(String(36),  nullable=True)
    titulo       = Column(String(255), nullable=False)
    descricao    = Column(Text,        nullable=True)
    data_agendada = Column(String(10), nullable=False)
    status       = Column(String(50),  default="agendada")
    created_at   = Column(DateTime,    default=datetime.utcnow)
    updated_at   = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

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
    for db in db_manager.get_db():
        yield db

def _init_db():
    try:
        Base.metadata.create_all(db_manager.engine)
        with SessionLocal() as db:
            admin = db.query(Usuario).filter_by(email="admin@luiseden.com.br").first()
            if not admin:
                db.add(Usuario(nome="Admin", email="admin@luiseden.com.br",
                               senha_hash=_hash("admin123"), role=RoleEnum.admin))
                db.commit()
    except Exception as e:
        print(f"[ERRO] DB init: {e}")
        raise

def _make_token(user: Usuario) -> str:
    exp = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user.id, "role": user.role, "exp": exp}, SECRET_KEY, ALGORITHM)

def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token inválido")

def require_admin(payload=Depends(verify_token)):
    if payload.get("role") != "admin":
        raise HTTPException(403, "Acesso negado")
    return payload

app = FastAPI(title="HubLuisEden API")
app.add_middleware(CORSMiddleware,
    allow_origins=["https://luiseden.com.br", "https://www.luiseden.com.br", "http://localhost:5173"],
    allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

@app.on_event("startup")
def startup_event():
    _init_db()

@app.get("/health")
def health():
    return {"status": "ok", "service": "hubluiseden"}

@app.get("/v1/eden/health")
def health_v1():
    return {"status": "ok", "service": "hubluiseden"}

# ── AUTH ──────────────────────────────────────────────────────────────────────

class LoginIn(BaseModel):
    email: EmailStr
    senha: str

class AuthOut(BaseModel):
    id: str
    nome: str
    email: str
    role: str
    accessToken: str

@app.post("/v1/eden/auth/login", response_model=AuthOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter_by(email=body.email, ativo=True).first()
    if not user or not _verify(body.senha, user.senha_hash):
        raise HTTPException(401, "Credenciais inválidas")
    return AuthOut(id=user.id, nome=user.nome, email=user.email,
                   role=user.role, accessToken=_make_token(user))

@app.get("/v1/eden/auth/me")
def me(payload=Depends(verify_token)):
    return payload

# ── CATALOGO ──────────────────────────────────────────────────────────────────

class PlantaIn(BaseModel):
    nome: str
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    precoCents: int = 0
    estoque: int = 0
    imagemUrl: Optional[str] = None

def _planta_dict(p: Planta):
    return {"id": p.id, "nome": p.nome, "categoria": p.categoria, "descricao": p.descricao,
            "precoCents": p.preco_cents, "estoque": p.estoque, "imagemUrl": p.imagem_url,
            "ativo": p.ativo, "createdAt": p.created_at.isoformat()}

@app.get("/v1/eden/catalogo")
def list_plantas(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_planta_dict(p) for p in db.query(Planta).filter_by(ativo=True).all()]

@app.post("/v1/eden/catalogo", status_code=201)
def create_planta(body: PlantaIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    p = Planta(nome=body.nome, categoria=body.categoria, descricao=body.descricao,
               preco_cents=body.precoCents, estoque=body.estoque, imagem_url=body.imagemUrl)
    db.add(p); db.commit(); db.refresh(p)
    return _planta_dict(p)

@app.post("/v1/eden/catalogo/update")
def update_planta(body: dict, db: Session = Depends(get_db), payload=Depends(verify_token)):
    p = db.query(Planta).filter_by(id=body.get("id")).first()
    if not p: raise HTTPException(404, "Não encontrado")
    for k, v in body.items():
        if k == "precoCents": p.preco_cents = v
        elif k == "imagemUrl": p.imagem_url = v
        elif hasattr(p, k) and k != "id": setattr(p, k, v)
    p.updated_at = datetime.utcnow()
    db.commit(); db.refresh(p)
    return _planta_dict(p)

@app.post("/v1/eden/catalogo/delete")
def delete_planta(body: dict, db: Session = Depends(get_db), payload=Depends(verify_token)):
    p = db.query(Planta).filter_by(id=body.get("id")).first()
    if not p: raise HTTPException(404, "Não encontrado")
    p.ativo = False; db.commit()
    return {"ok": True}

# ── VENDAS ────────────────────────────────────────────────────────────────────

class VendaIn(BaseModel):
    clienteNome: Optional[str] = None
    totalCents: int
    status: str = "concluida"
    observacoes: Optional[str] = None

def _venda_dict(v: Venda):
    return {"id": v.id, "usuarioId": v.usuario_id, "clienteNome": v.cliente_nome,
            "totalCents": v.total_cents, "status": v.status,
            "createdAt": v.created_at.isoformat()}

@app.get("/v1/eden/vendas")
def list_vendas(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_venda_dict(v) for v in db.query(Venda).order_by(Venda.created_at.desc()).all()]

@app.post("/v1/eden/vendas", status_code=201)
def create_venda(body: VendaIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    v = Venda(usuario_id=payload["sub"], cliente_nome=body.clienteNome,
              total_cents=body.totalCents, status=body.status, observacoes=body.observacoes)
    db.add(v); db.commit(); db.refresh(v)
    return _venda_dict(v)

@app.get("/v1/eden/vendas/dashboard")
def vendas_dashboard(db: Session = Depends(get_db), payload=Depends(verify_token)):
    vendas = db.query(Venda).all()
    return {"totalVendas": len(vendas),
            "totalCents": sum(v.total_cents for v in vendas),
            "concluidas": sum(1 for v in vendas if v.status == "concluida")}

# ── FINANCEIRO ────────────────────────────────────────────────────────────────

class TransacaoIn(BaseModel):
    tipo: str
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    valorCents: int
    data: str

def _transacao_dict(t: Transacao):
    return {"id": t.id, "tipo": t.tipo, "categoria": t.categoria, "descricao": t.descricao,
            "valorCents": t.valor_cents, "data": t.data, "createdAt": t.created_at.isoformat()}

@app.get("/v1/eden/financeiro")
def list_transacoes(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_transacao_dict(t) for t in db.query(Transacao).order_by(Transacao.data.desc()).all()]

@app.post("/v1/eden/financeiro", status_code=201)
def create_transacao(body: TransacaoIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    t = Transacao(usuario_id=payload["sub"], tipo=body.tipo, categoria=body.categoria,
                  descricao=body.descricao, valor_cents=body.valorCents, data=body.data)
    db.add(t); db.commit(); db.refresh(t)
    return _transacao_dict(t)

@app.get("/v1/eden/financeiro/dashboard")
def financeiro_dashboard(db: Session = Depends(get_db), payload=Depends(verify_token)):
    rows = db.query(Transacao).all()
    entradas = sum(t.valor_cents for t in rows if t.tipo == "entrada")
    saidas   = sum(t.valor_cents for t in rows if t.tipo == "saida")
    return {"totalEntradas": entradas, "totalSaidas": saidas, "saldo": entradas - saidas}

@app.post("/v1/eden/financeiro/delete")
def delete_transacao(body: dict, db: Session = Depends(get_db), payload=Depends(verify_token)):
    t = db.query(Transacao).filter_by(id=body.get("id")).first()
    if not t: raise HTTPException(404, "Não encontrado")
    db.delete(t); db.commit()
    return {"ok": True}

# ── ORCAMENTOS ────────────────────────────────────────────────────────────────

class OrcamentoIn(BaseModel):
    clienteNome: Optional[str] = None
    descricao: Optional[str] = None
    totalCents: int = 0
    validade: Optional[str] = None

def _orc_dict(o: Orcamento):
    return {"id": o.id, "clienteNome": o.cliente_nome, "descricao": o.descricao,
            "totalCents": o.total_cents, "status": o.status, "validade": o.validade,
            "createdAt": o.created_at.isoformat()}

@app.get("/v1/eden/orcamentos")
def list_orcamentos(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_orc_dict(o) for o in db.query(Orcamento).order_by(Orcamento.created_at.desc()).all()]

@app.post("/v1/eden/orcamentos", status_code=201)
def create_orcamento(body: OrcamentoIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = Orcamento(usuario_id=payload["sub"], cliente_nome=body.clienteNome,
                  descricao=body.descricao, total_cents=body.totalCents, validade=body.validade)
    db.add(o); db.commit(); db.refresh(o)
    return _orc_dict(o)

@app.post("/v1/eden/orcamentos/update")
def update_orcamento(body: dict, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = db.query(Orcamento).filter_by(id=body.get("id")).first()
    if not o: raise HTTPException(404, "Não encontrado")
    for k, v in body.items():
        if k == "totalCents": o.total_cents = v
        elif k == "clienteNome": o.cliente_nome = v
        elif hasattr(o, k) and k != "id": setattr(o, k, v)
    o.updated_at = datetime.utcnow()
    db.commit(); db.refresh(o)
    return _orc_dict(o)

@app.post("/v1/eden/orcamentos/delete")
def delete_orcamento(body: dict, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = db.query(Orcamento).filter_by(id=body.get("id")).first()
    if not o: raise HTTPException(404, "Não encontrado")
    db.delete(o); db.commit()
    return {"ok": True}

# ── MANUTENCAO ────────────────────────────────────────────────────────────────

class ManutencaoIn(BaseModel):
    titulo: str
    plantaId: Optional[str] = None
    descricao: Optional[str] = None
    dataAgendada: str
    status: str = "agendada"

def _man_dict(m: Manutencao):
    return {"id": m.id, "titulo": m.titulo, "plantaId": m.planta_id, "descricao": m.descricao,
            "dataAgendada": m.data_agendada, "status": m.status, "createdAt": m.created_at.isoformat()}

@app.get("/v1/eden/manutencao")
def list_manutencoes(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_man_dict(m) for m in db.query(Manutencao).order_by(Manutencao.data_agendada).all()]

@app.post("/v1/eden/manutencao", status_code=201)
def create_manutencao(body: ManutencaoIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = Manutencao(usuario_id=payload["sub"], titulo=body.titulo, planta_id=body.plantaId,
                   descricao=body.descricao, data_agendada=body.dataAgendada, status=body.status)
    db.add(m); db.commit(); db.refresh(m)
    return _man_dict(m)

@app.post("/v1/eden/manutencao/update")
def update_manutencao(body: dict, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = db.query(Manutencao).filter_by(id=body.get("id")).first()
    if not m: raise HTTPException(404, "Não encontrado")
    for k, v in body.items():
        if k == "plantaId": m.planta_id = v
        elif k == "dataAgendada": m.data_agendada = v
        elif hasattr(m, k) and k != "id": setattr(m, k, v)
    m.updated_at = datetime.utcnow()
    db.commit(); db.refresh(m)
    return _man_dict(m)

@app.post("/v1/eden/manutencao/delete")
def delete_manutencao(body: dict, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = db.query(Manutencao).filter_by(id=body.get("id")).first()
    if not m: raise HTTPException(404, "Não encontrado")
    db.delete(m); db.commit()
    return {"ok": True}

# ── FORNECEDORES ──────────────────────────────────────────────────────────────

class FornecedorIn(BaseModel):
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    cpfCnpj: Optional[str] = None
    endereco: Optional[str] = None
    categoria: Optional[str] = None

def _forn_dict(f: Fornecedor):
    return {"id": f.id, "nome": f.nome, "email": f.email, "telefone": f.telefone,
            "cpfCnpj": f.cpf_cnpj, "endereco": f.endereco, "categoria": f.categoria,
            "ativo": f.ativo, "createdAt": f.created_at.isoformat()}

@app.get("/v1/eden/fornecedores")
def list_fornecedores(db: Session = Depends(get_db), payload=Depends(verify_token)):
    return [_forn_dict(f) for f in db.query(Fornecedor).filter_by(ativo=True).all()]

@app.post("/v1/eden/fornecedores", status_code=201)
def create_fornecedor(body: FornecedorIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    f = Fornecedor(nome=body.nome, email=body.email, telefone=body.telefone,
                   cpf_cnpj=body.cpfCnpj, endereco=body.endereco, categoria=body.categoria)
    db.add(f); db.commit(); db.refresh(f)
    return _forn_dict(f)

@app.post("/v1/eden/fornecedores/update")
def update_fornecedor(body: dict, db: Session = Depends(get_db), payload=Depends(verify_token)):
    f = db.query(Fornecedor).filter_by(id=body.get("id")).first()
    if not f: raise HTTPException(404, "Não encontrado")
    for k, v in body.items():
        if k == "cpfCnpj": f.cpf_cnpj = v
        elif hasattr(f, k) and k != "id": setattr(f, k, v)
    f.updated_at = datetime.utcnow()
    db.commit(); db.refresh(f)
    return _forn_dict(f)

@app.post("/v1/eden/fornecedores/delete")
def delete_fornecedor(body: dict, db: Session = Depends(get_db), payload=Depends(verify_token)):
    f = db.query(Fornecedor).filter_by(id=body.get("id")).first()
    if not f: raise HTTPException(404, "Não encontrado")
    f.ativo = False; db.commit()
    return {"ok": True}

# ── USUARIOS ──────────────────────────────────────────────────────────────────

class UsuarioIn(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    role: str = "operador"

class UsuarioUpdate(BaseModel):
    id: str
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    ativo: Optional[bool] = None

class UsuarioGetIn(BaseModel):
    id: str

class SenhaUpdate(BaseModel):
    id: str
    senha: str

def _usuario_dict(u: Usuario):
    return {"id": u.id, "nome": u.nome, "email": u.email, "role": u.role,
            "ativo": u.ativo, "createdAt": u.created_at.isoformat()}

@app.get("/v1/eden/usuarios")
def list_usuarios(db: Session = Depends(get_db), payload=Depends(require_admin)):
    return [_usuario_dict(u) for u in db.query(Usuario).all()]

@app.post("/v1/eden/usuarios/get")
def get_usuario(body: UsuarioGetIn, db: Session = Depends(get_db), payload=Depends(require_admin)):
    u = db.query(Usuario).filter_by(id=body.id).first()
    if not u: raise HTTPException(404, "Não encontrado")
    return _usuario_dict(u)

@app.post("/v1/eden/usuarios", status_code=201)
def create_usuario(body: UsuarioIn, db: Session = Depends(get_db), payload=Depends(require_admin)):
    if db.query(Usuario).filter_by(email=body.email).first():
        raise HTTPException(409, "E-mail já cadastrado")
    u = Usuario(nome=body.nome, email=body.email, senha_hash=_hash(body.senha), role=body.role)
    db.add(u); db.commit(); db.refresh(u)
    return _usuario_dict(u)

@app.post("/v1/eden/usuarios/update")
def update_usuario(body: UsuarioUpdate, db: Session = Depends(get_db), payload=Depends(require_admin)):
    u = db.query(Usuario).filter_by(id=body.id).first()
    if not u: raise HTTPException(404, "Não encontrado")
    data = body.model_dump(exclude_none=True, exclude={"id"})
    for k, v in data.items(): setattr(u, k, v)
    u.updated_at = datetime.utcnow()
    db.commit(); db.refresh(u)
    return _usuario_dict(u)

@app.post("/v1/eden/usuarios/senha")
def update_senha(body: SenhaUpdate, db: Session = Depends(get_db), payload=Depends(require_admin)):
    u = db.query(Usuario).filter_by(id=body.id).first()
    if not u: raise HTTPException(404, "Não encontrado")
    u.senha_hash = _hash(body.senha)
    u.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True}

@app.post("/v1/eden/usuarios/minha-senha")
def update_minha_senha(body: SenhaUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    if payload["sub"] != body.id:
        raise HTTPException(403, "Acesso negado")
    u = db.query(Usuario).filter_by(id=body.id).first()
    if not u: raise HTTPException(404, "Não encontrado")
    u.senha_hash = _hash(body.senha)
    u.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True}

@app.post("/v1/eden/usuarios/delete")
def delete_usuario(body: UsuarioGetIn, db: Session = Depends(get_db), payload=Depends(require_admin)):
    u = db.query(Usuario).filter_by(id=body.id).first()
    if not u: raise HTTPException(404, "Não encontrado")
    u.ativo = False; db.commit()
    return {"ok": True}
