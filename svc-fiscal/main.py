import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

from database import DatabaseManager
from models import (
    Base, NotaFiscal, ItemNotaFiscal, EventoFiscal, ConfiguracaoFiscal,
    NotaFiscalIn, NotaFiscalOut, AutorizacaoNFeIn, ConsultaProtocoloIn,
    CancelamentoNFeIn, CartaCorrectionIn
)
from nfe_generator import NFeXMLGenerator
from xml_signer import XMLSigner
from sefaz_client import SefazSOAPClient

db_manager = DatabaseManager.from_env()
SessionLocal = db_manager.SessionLocal
SECRET_KEY = os.getenv("SECRET_KEY", "changeme-secret-key")
ALGORITHM = "HS256"
bearer = HTTPBearer()

def get_db():
    for db in db_manager.get_db():
        yield db

def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token inválido")

app = FastAPI(title="svc-fiscal")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(db_manager.engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "svc-fiscal"}

# ============ CONFIGURAÇÃO FISCAL ============

class ConfiguracaoFiscalIn(BaseModel):
    empresaId: str
    cnpj: str
    razaoSocial: str
    nomeFantasia: Optional[str] = None
    inscricaoEstadual: Optional[str] = None
    certificadoPath: str
    certificadoSenha: Optional[str] = None

@app.post("/v1/eden/fiscal/configuracao")
def criar_configuracao(body: ConfiguracaoFiscalIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    """Cria configuração fiscal da empresa"""
    config = db.query(ConfiguracaoFiscal).filter_by(empresa_id=body.empresaId).first()
    if config:
        raise HTTPException(409, "Configuração já existe")
    
    config = ConfiguracaoFiscal(
        id=str(uuid.uuid4()),
        empresa_id=body.empresaId,
        cnpj=body.cnpj,
        razao_social=body.razaoSocial,
        nome_fantasia=body.nomeFantasia,
        inscricao_estadual=body.inscricaoEstadual,
        certificado_path=body.certificadoPath,
        certificado_senha=body.certificadoSenha
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return {"id": config.id, "status": "criada"}

@app.get("/v1/eden/fiscal/configuracao/{empresa_id}")
def obter_configuracao(empresa_id: str, db: Session = Depends(get_db), payload=Depends(verify_token)):
    """Obtém configuração fiscal da empresa"""
    config = db.query(ConfiguracaoFiscal).filter_by(empresa_id=empresa_id).first()
    if not config:
        raise HTTPException(404, "Configuração não encontrada")
    return {
        "id": config.id,
        "cnpj": config.cnpj,
        "razaoSocial": config.razao_social,
        "nomeFantasia": config.nome_fantasia,
        "inscricaoEstadual": config.inscricao_estadual,
        "uf": config.uf,
        "ambiente": config.ambiente,
        "proximoNumero": config.proximo_numero
    }

# ============ NOTAS FISCAIS ============

@app.post("/v1/eden/fiscal/nfe", status_code=201)
def criar_nfe(body: NotaFiscalIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    """Cria rascunho de NF-e"""
    config = db.query(ConfiguracaoFiscal).filter_by(empresa_id=payload.get("empresa_id")).first()
    if not config:
        raise HTTPException(404, "Configuração fiscal não encontrada")
    
    nfe = NotaFiscal(
        id=str(uuid.uuid4()),
        numero=config.proximo_numero,
        serie=config.serie_nfe,
        cliente_id=body.clienteId,
        data_emissao=body.dataEmissao or datetime.utcnow(),
        valor_total_cents=sum(int(item.valorUnitarioCents * item.quantidade) for item in body.itens),
        status="rascunho"
    )
    db.add(nfe)
    db.flush()
    
    for item in body.itens:
        item_nfe = ItemNotaFiscal(
            id=str(uuid.uuid4()),
            nota_fiscal_id=nfe.id,
            produto_id=item.produtoId,
            descricao=item.descricao,
            quantidade=item.quantidade,
            valor_unitario_cents=item.valorUnitarioCents,
            valor_total_cents=int(item.valorUnitarioCents * item.quantidade),
            ncm=item.ncm,
            cfop=item.cfop
        )
        db.add(item_nfe)
    
    db.commit()
    db.refresh(nfe)
    return {"id": nfe.id, "numero": nfe.numero, "status": nfe.status}

@app.get("/v1/eden/fiscal/nfe/{nfe_id}")
def obter_nfe(nfe_id: str, db: Session = Depends(get_db), payload=Depends(verify_token)):
    """Obtém dados da NF-e"""
    nfe = db.query(NotaFiscal).filter_by(id=nfe_id).first()
    if not nfe:
        raise HTTPException(404, "NF-e não encontrada")
    
    itens = db.query(ItemNotaFiscal).filter_by(nota_fiscal_id=nfe_id).all()
    return {
        "id": nfe.id,
        "chaveNfe": nfe.chave_nfe,
        "numero": nfe.numero,
        "serie": nfe.serie,
        "clienteId": nfe.cliente_id,
        "dataEmissao": nfe.data_emissao.isoformat(),
        "valorTotalCents": nfe.valor_total_cents,
        "status": nfe.status,
        "protocolo": nfe.protocolo,
        "dataAutorizacao": nfe.data_autorizacao.isoformat() if nfe.data_autorizacao else None,
        "motivoRejeicao": nfe.motivo_rejeicao,
        "itens": [
            {
                "id": i.id,
                "produtoId": i.produto_id,
                "descricao": i.descricao,
                "quantidade": i.quantidade,
                "valorUnitarioCents": i.valor_unitario_cents,
                "valorTotalCents": i.valor_total_cents,
                "ncm": i.ncm,
                "cfop": i.cfop
            }
            for i in itens
        ]
    }

# ============ ASSINATURA E AUTORIZAÇÃO ============

@app.post("/v1/eden/fiscal/nfe/assinar")
def assinar_nfe(body: AutorizacaoNFeIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    """Assina XML da NF-e com certificado digital"""
    nfe = db.query(NotaFiscal).filter_by(id=body.notaFiscalId).first()
    if not nfe:
        raise HTTPException(404, "NF-e não encontrada")
    
    if nfe.status != "rascunho":
        raise HTTPException(409, f"NF-e não pode ser assinada (status: {nfe.status})")
    
    config = db.query(ConfiguracaoFiscal).filter_by(empresa_id=payload.get("empresa_id")).first()
    if not config:
        raise HTTPException(404, "Configuração fiscal não encontrada")
    
    # Gerar XML
    itens = db.query(ItemNotaFiscal).filter_by(nota_fiscal_id=nfe.id).all()
    cliente = {"nome": "Cliente", "cpf_cnpj": "00000000000000"}  # TODO: buscar do BD
    
    generator = NFeXMLGenerator({
        "cnpj": config.cnpj,
        "razao_social": config.razao_social,
        "nome_fantasia": config.nome_fantasia,
        "inscricao_estadual": config.inscricao_estadual,
        "uf": config.uf,
        "codigo_ibge_uf": config.codigo_ibge_uf
    })
    
    xml_nfe = generator.generate_nfe(
        numero=nfe.numero,
        serie=nfe.serie,
        cliente=cliente,
        itens=[
            {
                "descricao": i.descricao,
                "quantidade": i.quantidade,
                "valor_unitario_cents": i.valor_unitario_cents,
                "ncm": i.ncm,
                "cfop": i.cfop
            }
            for i in itens
        ],
        data_emissao=nfe.data_emissao
    )
    
    # Assinar XML
    try:
        signer = XMLSigner(config.certificado_path, config.certificado_senha)
        xml_assinado = signer.sign_xml(xml_nfe)
        
        nfe.xml_assinado = xml_assinado
        nfe.status = "assinada"
        db.commit()
        db.refresh(nfe)
        
        return {"status": "assinada", "nfeId": nfe.id}
    except Exception as e:
        raise HTTPException(500, f"Erro ao assinar: {str(e)}")

@app.post("/v1/eden/fiscal/nfe/autorizar")
def autorizar_nfe(body: AutorizacaoNFeIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    """Envia NF-e para autorização na SEFAZ"""
    nfe = db.query(NotaFiscal).filter_by(id=body.notaFiscalId).first()
    if not nfe:
        raise HTTPException(404, "NF-e não encontrada")
    
    if nfe.status not in ["assinada", "rascunho"]:
        raise HTTPException(409, f"NF-e não pode ser autorizada (status: {nfe.status})")
    
    config = db.query(ConfiguracaoFiscal).filter_by(empresa_id=payload.get("empresa_id")).first()
    if not config:
        raise HTTPException(404, "Configuração fiscal não encontrada")
    
    # Se não estiver assinada, assinar primeiro
    if nfe.status == "rascunho":
        # TODO: chamar assinar_nfe
        pass
    
    try:
        client = SefazSOAPClient(config.certificado_path, config.certificado_senha)
        
        # Verificar status do serviço
        status_resp = client.nfe_status_servico()
        if status_resp["status"] != "sucesso":
            raise HTTPException(503, "SEFAZ indisponível")
        
        # Enviar para autorização
        auth_resp = client.nfe_autorizacao(nfe.xml_assinado)
        
        if auth_resp["status"] == "sucesso":
            nfe.numero_recibo = auth_resp.get("infRec", {}).get("nRec")
            nfe.status = "pendente_protocolo"
            db.commit()
            db.refresh(nfe)
            
            return {
                "status": "enviada",
                "nfeId": nfe.id,
                "numeroRecibo": nfe.numero_recibo,
                "cstat": auth_resp.get("cstat")
            }
        else:
            nfe.motivo_rejeicao = auth_resp.get("xmotivo")
            nfe.status = "rejeitada"
            db.commit()
            
            raise HTTPException(400, f"Rejeição: {auth_resp.get('xmotivo')}")
    except Exception as e:
        raise HTTPException(500, f"Erro ao autorizar: {str(e)}")

# ============ CONSULTAS ============

@app.post("/v1/eden/fiscal/nfe/consulta-protocolo")
def consultar_protocolo(body: ConsultaProtocoloIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    """Consulta protocolo de autorização"""
    nfe = db.query(NotaFiscal).filter_by(chave_nfe=body.chaveNfe).first()
    if not nfe:
        raise HTTPException(404, "NF-e não encontrada")
    
    config = db.query(ConfiguracaoFiscal).filter_by(empresa_id=payload.get("empresa_id")).first()
    if not config:
        raise HTTPException(404, "Configuração fiscal não encontrada")
    
    try:
        client = SefazSOAPClient(config.certificado_path, config.certificado_senha)
        resp = client.nfe_consulta_protocolo(body.chaveNfe)
        
        if resp["status"] == "sucesso":
            cstat = resp.get("cstat")
            if cstat == "100":  # Autorizado
                nfe.protocolo = resp.get("protNFe", {}).get("infProt", {}).get("nProt")
                nfe.status = "autorizada"
                nfe.data_autorizacao = datetime.utcnow()
            elif cstat == "102":  # Inutilizado
                nfe.status = "inutilizada"
            else:
                nfe.motivo_rejeicao = resp.get("xmotivo")
                nfe.status = "rejeitada"
            
            db.commit()
            db.refresh(nfe)
        
        return {
            "chaveNfe": body.chaveNfe,
            "status": nfe.status,
            "protocolo": nfe.protocolo,
            "cstat": resp.get("cstat"),
            "xmotivo": resp.get("xmotivo")
        }
    except Exception as e:
        raise HTTPException(500, f"Erro ao consultar: {str(e)}")

# ============ CANCELAMENTO ============

@app.post("/v1/eden/fiscal/nfe/cancelar")
def cancelar_nfe(body: CancelamentoNFeIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    """Cancela NF-e autorizada"""
    nfe = db.query(NotaFiscal).filter_by(id=body.notaFiscalId).first()
    if not nfe:
        raise HTTPException(404, "NF-e não encontrada")
    
    if nfe.status != "autorizada":
        raise HTTPException(409, "Apenas NF-e autorizada pode ser cancelada")
    
    config = db.query(ConfiguracaoFiscal).filter_by(empresa_id=payload.get("empresa_id")).first()
    if not config:
        raise HTTPException(404, "Configuração fiscal não encontrada")
    
    # TODO: Gerar XML de evento de cancelamento
    # TODO: Assinar XML de evento
    # TODO: Enviar para SEFAZ
    
    evento = EventoFiscal(
        id=str(uuid.uuid4()),
        nota_fiscal_id=nfe.id,
        tipo_evento="cancelamento",
        numero_sequencial=1,
        xml_evento="",  # TODO
        status="pendente"
    )
    db.add(evento)
    nfe.status = "cancelada"
    db.commit()
    
    return {"status": "cancelamento_enviado", "nfeId": nfe.id}

# ============ STATUS ============

@app.get("/v1/eden/fiscal/status-sefaz")
def status_sefaz(db: Session = Depends(get_db), payload=Depends(verify_token)):
    """Verifica status do serviço SEFAZ"""
    config = db.query(ConfiguracaoFiscal).filter_by(empresa_id=payload.get("empresa_id")).first()
    if not config:
        raise HTTPException(404, "Configuração fiscal não encontrada")
    
    try:
        client = SefazSOAPClient(config.certificado_path, config.certificado_senha)
        resp = client.nfe_status_servico()
        return resp
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
