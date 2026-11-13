from lxml import etree
from datetime import datetime
import uuid

class NFeXMLGenerator:
    """Gerador de XML NF-e conforme layout 4.00"""
    
    NS = {
        "nfe": "http://www.portalfiscal.inf.br/nfe",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance"
    }
    
    def __init__(self, config: dict):
        """
        Args:
            config: Dicionário com configurações da empresa
                - cnpj: CNPJ da empresa
                - razao_social: Razão social
                - inscricao_estadual: IE
                - uf: UF (ex: MG)
                - codigo_ibge_uf: Código IBGE da UF
        """
        self.config = config
    
    def _create_element(self, tag: str, text: str = None, attrib: dict = None) -> etree._Element:
        """Cria elemento XML"""
        elem = etree.Element(tag, attrib=attrib or {})
        if text:
            elem.text = str(text)
        return elem
    
    def _add_child(self, parent: etree._Element, tag: str, text: str = None, attrib: dict = None) -> etree._Element:
        """Adiciona filho a elemento"""
        child = self._create_element(tag, text, attrib)
        parent.append(child)
        return child
    
    def generate_nfe(self, numero: int, serie: int, cliente: dict, itens: list, data_emissao: datetime = None) -> str:
        """
        Gera XML de NF-e
        
        Args:
            numero: Número da NF-e
            serie: Série da NF-e
            cliente: Dict com dados do cliente (nome, cpf/cnpj, endereco, etc)
            itens: Lista de itens (descricao, quantidade, valor_unitario, ncm, cfop)
            data_emissao: Data de emissão (padrão: agora)
        
        Returns:
            XML em string
        """
        if not data_emissao:
            data_emissao = datetime.utcnow()
        
        # Gerar chave de acesso (29 dígitos)
        chave = self._gerar_chave(numero, serie, data_emissao)
        
        # Root NFe
        nfe = etree.Element(
            f"{{{self.NS['nfe']}}}NFe",
            attrib={f"{{{self.NS['xsi']}}}schemaLocation": "http://www.portalfiscal.inf.br/nfe http://www.portalfiscal.inf.br/nfe/v4.00/nfe_v4.00.xsd"}
        )
        
        # infNFe
        inf_nfe = self._add_child(nfe, f"{{{self.NS['nfe']}}}infNFe", attrib={"Id": f"NFe{chave}"})
        
        # ide
        ide = self._add_child(inf_nfe, f"{{{self.NS['nfe']}}}ide")
        self._add_child(ide, f"{{{self.NS['nfe']}}}cUF", str(self.config['codigo_ibge_uf']))
        self._add_child(ide, f"{{{self.NS['nfe']}}}cNF", str(numero).zfill(8))
        self._add_child(ide, f"{{{self.NS['nfe']}}}mod", "55")  # 55 = NF-e
        self._add_child(ide, f"{{{self.NS['nfe']}}}serie", str(serie))
        self._add_child(ide, f"{{{self.NS['nfe']}}}nNF", str(numero))
        self._add_child(ide, f"{{{self.NS['nfe']}}}dhEmi", data_emissao.isoformat())
        self._add_child(ide, f"{{{self.NS['nfe']}}}dhSaiEnt", data_emissao.isoformat())
        self._add_child(ide, f"{{{self.NS['nfe']}}}tpNF", "1")  # 1 = Saída
        self._add_child(ide, f"{{{self.NS['nfe']}}}idDest", "1")  # 1 = Operação interna
        self._add_child(ide, f"{{{self.NS['nfe']}}}cMunFG", "3106200")  # Belo Horizonte
        self._add_child(ide, f"{{{self.NS['nfe']}}}tpImp", "1")  # 1 = Retrato
        self._add_child(ide, f"{{{self.NS['nfe']}}}tpEmis", "1")  # 1 = Normal
        self._add_child(ide, f"{{{self.NS['nfe']}}}cDV", str(self._calc_dv(chave)))
        self._add_child(ide, f"{{{self.NS['nfe']}}}tpAmb", "2")  # 2 = Homologação
        self._add_child(ide, f"{{{self.NS['nfe']}}}finNFe", "1")  # 1 = NF-e normal
        self._add_child(ide, f"{{{self.NS['nfe']}}}indFinal", "0")  # 0 = Não
        self._add_child(ide, f"{{{self.NS['nfe']}}}indPres", "1")  # 1 = Operação presencial
        self._add_child(ide, f"{{{self.NS['nfe']}}}procEmi", "0")  # 0 = Emissão normal
        self._add_child(ide, f"{{{self.NS['nfe']}}}verProc", "1.0")
        
        # emit
        emit = self._add_child(inf_nfe, f"{{{self.NS['nfe']}}}emit")
        self._add_child(emit, f"{{{self.NS['nfe']}}}CNPJ", self.config['cnpj'].replace('.', '').replace('/', '').replace('-', ''))
        self._add_child(emit, f"{{{self.NS['nfe']}}}xNome", self.config['razao_social'])
        self._add_child(emit, f"{{{self.NS['nfe']}}}xFant", self.config.get('nome_fantasia', self.config['razao_social']))
        
        # enderEmit
        ender_emit = self._add_child(emit, f"{{{self.NS['nfe']}}}enderEmit")
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}xLgr", "Rua Exemplo")
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}nro", "123")
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}xCpl", "Apto 1")
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}xBairro", "Centro")
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}cMun", "3106200")
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}xMun", "Belo Horizonte")
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}UF", self.config['uf'])
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}CEP", "30130100")
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}cPais", "1058")
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}xPais", "Brasil")
        self._add_child(ender_emit, f"{{{self.NS['nfe']}}}fone", "3133334444")
        
        self._add_child(emit, f"{{{self.NS['nfe']}}}IE", self.config.get('inscricao_estadual', ''))
        self._add_child(emit, f"{{{self.NS['nfe']}}}IEST", "")
        self._add_child(emit, f"{{{self.NS['nfe']}}}IM", "")
        self._add_child(emit, f"{{{self.NS['nfe']}}}CNAE", "")
        self._add_child(emit, f"{{{self.NS['nfe']}}}CRT", "1")  # 1 = Simples Nacional
        
        # dest
        dest = self._add_child(inf_nfe, f"{{{self.NS['nfe']}}}dest")
        if len(cliente.get('cpf_cnpj', '').replace('.', '').replace('/', '').replace('-', '')) == 14:
            self._add_child(dest, f"{{{self.NS['nfe']}}}CNPJ", cliente['cpf_cnpj'].replace('.', '').replace('/', '').replace('-', ''))
        else:
            self._add_child(dest, f"{{{self.NS['nfe']}}}CPF", cliente['cpf_cnpj'].replace('.', '').replace('-', ''))
        self._add_child(dest, f"{{{self.NS['nfe']}}}xNome", cliente['nome'])
        self._add_child(dest, f"{{{self.NS['nfe']}}}indIEDest", "9")  # 9 = Não contribuinte
        
        # enderDest
        ender_dest = self._add_child(dest, f"{{{self.NS['nfe']}}}enderDest")
        self._add_child(ender_dest, f"{{{self.NS['nfe']}}}xLgr", cliente.get('endereco', 'Rua Exemplo'))
        self._add_child(ender_dest, f"{{{self.NS['nfe']}}}nro", cliente.get('numero', '123'))
        self._add_child(ender_dest, f"{{{self.NS['nfe']}}}xBairro", cliente.get('bairro', 'Centro'))
        self._add_child(ender_dest, f"{{{self.NS['nfe']}}}cMun", cliente.get('codigo_municipio', '3106200'))
        self._add_child(ender_dest, f"{{{self.NS['nfe']}}}xMun", cliente.get('municipio', 'Belo Horizonte'))
        self._add_child(ender_dest, f"{{{self.NS['nfe']}}}UF", cliente.get('uf', 'MG'))
        self._add_child(ender_dest, f"{{{self.NS['nfe']}}}CEP", cliente.get('cep', '30130100'))
        self._add_child(ender_dest, f"{{{self.NS['nfe']}}}cPais", "1058")
        self._add_child(ender_dest, f"{{{self.NS['nfe']}}}xPais", "Brasil")
        
        # det (itens)
        valor_total = 0
        for idx, item in enumerate(itens, 1):
            det = self._add_child(inf_nfe, f"{{{self.NS['nfe']}}}det", attrib={"nItem": str(idx)})
            
            prod = self._add_child(det, f"{{{self.NS['nfe']}}}prod")
            self._add_child(prod, f"{{{self.NS['nfe']}}}CProd", str(idx))
            self._add_child(prod, f"{{{self.NS['nfe']}}}CFOP", item.get('cfop', '5102'))
            self._add_child(prod, f"{{{self.NS['nfe']}}}xProd", item['descricao'])
            self._add_child(prod, f"{{{self.NS['nfe']}}}NCM", item.get('ncm', '00000000'))
            self._add_child(prod, f"{{{self.NS['nfe']}}}CEST", "")
            self._add_child(prod, f"{{{self.NS['nfe']}}}indEscala", "N")
            self._add_child(prod, f"{{{self.NS['nfe']}}}CNPJFab", "")
            self._add_child(prod, f"{{{self.NS['nfe']}}}cBenef", "")
            self._add_child(prod, f"{{{self.NS['nfe']}}}EXTIPI", "")
            self._add_child(prod, f"{{{self.NS['nfe']}}}genero", "")
            self._add_child(prod, f"{{{self.NS['nfe']}}}tipMed", "")
            self._add_child(prod, f"{{{self.NS['nfe']}}}qCom", str(item['quantidade']))
            self._add_child(prod, f"{{{self.NS['nfe']}}}vUnCom", f"{item['valor_unitario_cents']/100:.2f}")
            valor_item = item['quantidade'] * (item['valor_unitario_cents'] / 100)
            self._add_child(prod, f"{{{self.NS['nfe']}}}vProd", f"{valor_item:.2f}")
            self._add_child(prod, f"{{{self.NS['nfe']}}}vItem12741", "0.00")
            self._add_child(prod, f"{{{self.NS['nfe']}}}indTot", "1")
            valor_total += valor_item
            
            # imposto
            imposto = self._add_child(det, f"{{{self.NS['nfe']}}}imposto")
            icms = self._add_child(imposto, f"{{{self.NS['nfe']}}}ICMS")
            icms00 = self._add_child(icms, f"{{{self.NS['nfe']}}}ICMS00")
            self._add_child(icms00, f"{{{self.NS['nfe']}}}orig", "0")
            self._add_child(icms00, f"{{{self.NS['nfe']}}}CST", "00")
            self._add_child(icms00, f"{{{self.NS['nfe']}}}modBC", "0")
            self._add_child(icms00, f"{{{self.NS['nfe']}}}vBC", f"{valor_item:.2f}")
            self._add_child(icms00, f"{{{self.NS['nfe']}}}pICMS", "18.00")
            self._add_child(icms00, f"{{{self.NS['nfe']}}}vICMS", f"{valor_item * 0.18:.2f}")
            self._add_child(icms00, f"{{{self.NS['nfe']}}}pFCP", "0.00")
            self._add_child(icms00, f"{{{self.NS['nfe']}}}vFCP", "0.00")
            
            pis = self._add_child(imposto, f"{{{self.NS['nfe']}}}PIS")
            pisnt = self._add_child(pis, f"{{{self.NS['nfe']}}}PISNT")
            self._add_child(pisnt, f"{{{self.NS['nfe']}}}CST", "06")
            
            cofins = self._add_child(imposto, f"{{{self.NS['nfe']}}}COFINS")
            cofinsnt = self._add_child(cofins, f"{{{self.NS['nfe']}}}COFINSNT")
            self._add_child(cofinsnt, f"{{{self.NS['nfe']}}}CST", "06")
        
        # total
        total = self._add_child(inf_nfe, f"{{{self.NS['nfe']}}}total")
        icms_tot = self._add_child(total, f"{{{self.NS['nfe']}}}ICMSTot")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vBC", f"{valor_total:.2f}")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vICMS", f"{valor_total * 0.18:.2f}")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vICMSDeson", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vFCP", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vBCST", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vST", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vFCPST", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vFCPSTRet", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vProd", f"{valor_total:.2f}")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vFrete", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vSeg", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vDesc", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vII", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vIPI", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vIPIDevol", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vPIS", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vCOFINS", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vOutro", "0.00")
        self._add_child(icms_tot, f"{{{self.NS['nfe']}}}vNF", f"{valor_total:.2f}")
        
        # transp
        transp = self._add_child(inf_nfe, f"{{{self.NS['nfe']}}}transp")
        self._add_child(transp, f"{{{self.NS['nfe']}}}modFrete", "9")  # 9 = Sem frete
        
        # pag
        pag = self._add_child(inf_nfe, f"{{{self.NS['nfe']}}}pag")
        detpag = self._add_child(pag, f"{{{self.NS['nfe']}}}detPag")
        self._add_child(detpag, f"{{{self.NS['nfe']}}}tPag", "01")  # 01 = Dinheiro
        self._add_child(detpag, f"{{{self.NS['nfe']}}}vPag", f"{valor_total:.2f}")
        
        # infAdic
        inf_adic = self._add_child(inf_nfe, f"{{{self.NS['nfe']}}}infAdic")
        self._add_child(inf_adic, f"{{{self.NS['nfe']}}}infCpl", "Documento emitido por sistema autorizado")
        
        return etree.tostring(nfe, encoding='unicode', pretty_print=True)
    
    def _gerar_chave(self, numero: int, serie: int, data_emissao: datetime) -> str:
        """Gera chave de acesso (29 dígitos)"""
        uf = str(self.config['codigo_ibge_uf']).zfill(2)
        data = data_emissao.strftime('%y%m%d')
        cnpj = self.config['cnpj'].replace('.', '').replace('/', '').replace('-', '')
        mod = '55'
        serie_str = str(serie).zfill(3)
        numero_str = str(numero).zfill(8)
        tipo = '0'
        emitente = '0'
        
        chave_base = f"{uf}{data}{cnpj}{mod}{serie_str}{numero_str}{tipo}{emitente}"
        dv = self._calc_dv(chave_base)
        
        return f"{chave_base}{dv}"
    
    def _calc_dv(self, chave: str) -> str:
        """Calcula dígito verificador da chave"""
        seq = "2987654321"
        soma = sum(int(chave[i]) * int(seq[i % 10]) for i in range(len(chave)))
        resto = soma % 11
        return "0" if resto == 0 else str(11 - resto) if resto != 1 else "0"
