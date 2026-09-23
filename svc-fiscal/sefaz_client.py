import os
from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
import ssl
from urllib3.util.ssl_ import create_urllib3_context

class SefazSOAPClient:
    """Cliente SOAP para comunicação com SEFAZ-MG com mTLS"""
    
    ENDPOINTS = {
        "status": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeStatusServico4",
        "autorizacao": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeAutorizacao4",
        "ret_autorizacao": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeRetAutorizacao4",
        "consulta_protocolo": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeConsultaProtocolo4",
        "inutilizacao": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeInutilizacao4",
        "evento": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeRecepcaoEvento4",
        "cadastro": "https://hnfe.fazenda.mg.gov.br/nfe2/services/CadConsultaCadastro4",
    }
    
    WSDL_URLS = {
        "status": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeStatusServico4?wsdl",
        "autorizacao": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeAutorizacao4?wsdl",
        "ret_autorizacao": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeRetAutorizacao4?wsdl",
        "consulta_protocolo": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeConsultaProtocolo4?wsdl",
        "inutilizacao": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeInutilizacao4?wsdl",
        "evento": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeRecepcaoEvento4?wsdl",
        "cadastro": "https://hnfe.fazenda.mg.gov.br/nfe2/services/CadConsultaCadastro4?wsdl",
    }
    
    def __init__(self, cert_path: str, cert_password: str = None):
        """
        Args:
            cert_path: Caminho para certificado .pfx ou .pem
            cert_password: Senha do certificado
        """
        self.cert_path = cert_path
        self.cert_password = cert_password
        self.clients = {}
    
    def _create_transport(self) -> Transport:
        """Cria transport com mTLS"""
        session = Session()
        session.cert = (self.cert_path, self.cert_path)
        session.verify = True
        
        # Configurar SSL
        ctx = create_urllib3_context()
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        
        adapter = session.get_adapter('https://')
        adapter.init_poolmanager(ssl_context=ctx)
        
        return Transport(session=session, timeout=30)
    
    def get_client(self, service: str) -> Client:
        """Obtém cliente SOAP para serviço específico"""
        if service not in self.clients:
            if service not in self.WSDL_URLS:
                raise ValueError(f"Serviço desconhecido: {service}")
            
            transport = self._create_transport()
            self.clients[service] = Client(
                wsdl=self.WSDL_URLS[service],
                transport=transport
            )
        
        return self.clients[service]
    
    def nfe_status_servico(self) -> dict:
        """Consulta status do serviço SEFAZ"""
        client = self.get_client("status")
        try:
            response = client.service.nfeStatusServicoNF(
                versaoXML="4.00",
                tpAmb=2  # 2 = Homologação
            )
            return {
                "status": "sucesso",
                "cstat": response.get("cStat"),
                "xmotivo": response.get("xMotivo"),
                "dhrecbto": response.get("dhRecbto"),
                "tMed": response.get("tMed")
            }
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}
    
    def nfe_autorizacao(self, xml_assinado: str) -> dict:
        """Envia NF-e para autorização"""
        client = self.get_client("autorizacao")
        try:
            response = client.service.nfeAutorizacaoLote(
                nfeDadosMsg=xml_assinado,
                idLote="1"
            )
            return {
                "status": "sucesso",
                "infRec": response.get("infRec"),
                "cstat": response.get("cStat"),
                "xmotivo": response.get("xMotivo")
            }
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}
    
    def nfe_ret_autorizacao(self, rec_id: str) -> dict:
        """Consulta resultado da autorização pelo recibo"""
        client = self.get_client("ret_autorizacao")
        try:
            response = client.service.nfeRetAutorizacaoLote(
                recId=rec_id
            )
            return {
                "status": "sucesso",
                "protNFe": response.get("protNFe"),
                "cstat": response.get("cStat"),
                "xmotivo": response.get("xMotivo")
            }
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}
    
    def nfe_consulta_protocolo(self, chave_nfe: str) -> dict:
        """Consulta protocolo de uma NF-e"""
        client = self.get_client("consulta_protocolo")
        try:
            response = client.service.nfeConsultaProtocolo(
                chNFe=chave_nfe,
                tpAmb=2
            )
            return {
                "status": "sucesso",
                "cstat": response.get("cStat"),
                "xmotivo": response.get("xMotivo"),
                "protNFe": response.get("protNFe")
            }
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}
    
    def nfe_inutilizacao(self, xml_inutilizacao: str) -> dict:
        """Inutiliza numeração de NF-e"""
        client = self.get_client("inutilizacao")
        try:
            response = client.service.nfeInutilizacaoNF(
                nfeDadosMsg=xml_inutilizacao
            )
            return {
                "status": "sucesso",
                "cstat": response.get("cStat"),
                "xmotivo": response.get("xMotivo"),
                "infInut": response.get("infInut")
            }
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}
    
    def nfe_evento(self, xml_evento: str) -> dict:
        """Envia evento (cancelamento, carta de correção, etc)"""
        client = self.get_client("evento")
        try:
            response = client.service.nfeRecepcaoEvento(
                nfeDadosMsg=xml_evento
            )
            return {
                "status": "sucesso",
                "cstat": response.get("cStat"),
                "xmotivo": response.get("xMotivo"),
                "retEvento": response.get("retEvento")
            }
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}
