from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from typing import Optional, List

class Base(DeclarativeBase):
    pass

class NotaFiscal(Base):
    __tablename__ = "notas_fiscais"
    
    id = Column(String(36), primary_key=True)
    chave_nfe = Column(String(44), unique=True, nullable=True)
    numero = Column(Integer, nullable=False)
    serie = Column(Integer, default=1)
    cliente_id = Column(String(36), nullable=False)
    data_emissao = Column(DateTime, default=datetime.utcnow)
    valor_total_cents = Column(Integer, nullable=False)
    status = Column(String(50), default="rascunho")  # rascunho, assinada, autorizada, cancelada
    xml_assinado = Column(Text, nullable=True)
    protocolo = Column(String(15), nullable=True)
    numero_recibo = Column(String(20), nullable=True)
    data_autorizacao = Column(DateTime, nullable=True)
    motivo_rejeicao = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ItemNotaFiscal(Base):
    __tablename__ = "itens_nota_fiscal"
    
    id = Column(String(36), primary_key=True)
    nota_fiscal_id = Column(String(36), ForeignKey("notas_fiscais.id"), nullable=False)
    produto_id = Column(String(36), nullable=False)
    descricao = Column(String(255), nullable=False)
    quantidade = Column(Float, nullable=False)
    valor_unitario_cents = Column(Integer, nullable=False)
    valor_total_cents = Column(Integer, nullable=False)
    ncm = Column(String(8), nullable=True)
    cfop = Column(String(4), nullable=True)

class EventoFiscal(Base):
    __tablename__ = "eventos_fiscais"
    
    id = Column(String(36), primary_key=True)
    nota_fiscal_id = Column(String(36), ForeignKey("notas_fiscais.id"), nullable=False)
    tipo_evento = Column(String(50), nullable=False)  # cancelamento, carta_correcao, etc
    numero_sequencial = Column(Integer, default=1)
    xml_evento = Column(Text, nullable=False)
    status = Column(String(50), default="pendente")  # pendente, enviado, autorizado, rejeitado
    protocolo_evento = Column(String(15), nullable=True)
    motivo_rejeicao = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConfiguracaoFiscal(Base):
    __tablename__ = "configuracoes_fiscais"
    
    id = Column(String(36), primary_key=True)
    empresa_id = Column(String(36), nullable=False, unique=True)
    cnpj = Column(String(14), nullable=False)
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255), nullable=True)
    inscricao_estadual = Column(String(20), nullable=True)
    ambiente = Column(Integer, default=2)  # 1 = Produção, 2 = Homologação
    uf = Column(String(2), default="MG")
    codigo_ibge_uf = Column(Integer, default=31)  # MG = 31
    certificado_path = Column(String(500), nullable=False)
    certificado_senha = Column(String(255), nullable=True)
    serie_nfe = Column(Integer, default=1)
    proximo_numero = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models

class ItemNotaFiscalIn(BaseModel):
    produtoId: str
    descricao: str
    quantidade: float
    valorUnitarioCents: int
    ncm: Optional[str] = None
    cfop: Optional[str] = None

class NotaFiscalIn(BaseModel):
    clienteId: str
    dataEmissao: Optional[datetime] = None
    itens: List[ItemNotaFiscalIn]
    observacoes: Optional[str] = None

class NotaFiscalOut(BaseModel):
    id: str
    chaveNfe: Optional[str]
    numero: int
    serie: int
    clienteId: str
    dataEmissao: datetime
    valorTotalCents: int
    status: str
    protocolo: Optional[str]
    dataAutorizacao: Optional[datetime]
    motivoRejeicao: Optional[str]

class AutorizacaoNFeIn(BaseModel):
    notaFiscalId: str

class ConsultaProtocoloIn(BaseModel):
    chaveNfe: str

class CancelamentoNFeIn(BaseModel):
    notaFiscalId: str
    justificativa: str

class CartaCorrectionIn(BaseModel):
    notaFiscalId: str
    texto_correcao: str
