# Troubleshooting e FAQ - Módulo Fiscal

## ❌ Problemas Comuns

### 1. Erro ao Carregar Certificado

**Erro:**
```
ValueError: Erro ao carregar certificado: /path/to/cert.pfx
```

**Causas e Soluções:**

1. **Arquivo não existe**
   ```bash
   # Verificar se arquivo existe
   ls -la /path/to/cert.pfx
   
   # Verificar permissões
   chmod 644 /path/to/cert.pfx
   ```

2. **Senha incorreta**
   ```python
   # Testar senha
   from cryptography.hazmat.primitives.serialization import pkcs12
   with open('cert.pfx', 'rb') as f:
       pkcs12.load_key_and_certificates(f.read(), b'senha-correta')
   ```

3. **Formato inválido**
   ```bash
   # Converter PEM para PFX
   openssl pkcs12 -export -in cert.pem -inkey key.pem -out cert.pfx -name "Empresa"
   
   # Verificar formato
   openssl pkcs12 -info -in cert.pfx
   ```

### 2. SEFAZ Indisponível

**Erro:**
```
HTTPException: SEFAZ indisponível
```

**Causas e Soluções:**

1. **Serviço em manutenção**
   - SEFAZ-MG realiza manutenção às terças-feiras
   - Verificar status em: https://hnfe.fazenda.mg.gov.br/

2. **Problema de conectividade**
   ```bash
   # Testar conexão
   curl -v https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeStatusServico4
   
   # Testar DNS
   nslookup hnfe.fazenda.mg.gov.br
   ```

3. **Certificado expirado**
   ```bash
   # Verificar data de expiração
   openssl pkcs12 -in cert.pfx -nokeys | openssl x509 -noout -dates
   ```

### 3. Erro de Validação XML

**Erro:**
```
cstat: 302
xmotivo: Falha na validação do schema XML
```

**Causas e Soluções:**

1. **XML malformado**
   ```bash
   # Validar XML
   xmllint --schema nfe_v4.00.xsd nfe.xml
   ```

2. **Campos obrigatórios faltando**
   - Verificar se todos os campos obrigatórios estão preenchidos
   - Consultar especificação técnica

3. **Valores inválidos**
   ```python
   # Exemplos de valores válidos
   tpNF = "1"  # 1 = Saída, 0 = Entrada
   tpAmb = "2"  # 1 = Produção, 2 = Homologação
   tpImp = "1"  # 1 = Retrato, 2 = Paisagem
   ```

### 4. Erro de Assinatura Digital

**Erro:**
```
Exception: Erro ao assinar XML
```

**Causas e Soluções:**

1. **Certificado sem chave privada**
   ```bash
   # Verificar se tem chave privada
   openssl pkcs12 -in cert.pfx -nocerts -noout
   ```

2. **Algoritmo não suportado**
   ```python
   # Usar SHA1 ou SHA256
   from cryptography.hazmat.primitives import hashes
   hashes.SHA1()  # Padrão NF-e
   ```

### 5. Timeout na Comunicação

**Erro:**
```
requests.exceptions.Timeout: Connection timeout
```

**Causas e Soluções:**

1. **Aumentar timeout**
   ```python
   # Em sefaz_client.py
   Transport(session=session, timeout=60)  # Aumentar de 30 para 60
   ```

2. **Problema de rede**
   ```bash
   # Testar latência
   ping hnfe.fazenda.mg.gov.br
   
   # Testar rota
   tracert hnfe.fazenda.mg.gov.br
   ```

### 6. Erro de Autenticação mTLS

**Erro:**
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Causas e Soluções:**

1. **Certificado não confiável**
   ```python
   # Verificar cadeia de certificados
   openssl verify -CAfile ca-bundle.crt cert.pem
   ```

2. **Certificado expirado**
   ```bash
   # Renovar certificado
   # Contatar AC (Autoridade Certificadora)
   ```

## ❓ FAQ

### P: Qual é a diferença entre ambiente de produção e homologação?

**R:** 
- **Homologação (tpAmb=2)**: Ambiente de testes, sem validade jurídica
- **Produção (tpAmb=1)**: Ambiente real, com validade jurídica
- Use homologação para testes antes de ir para produção

### P: Como obter certificado de teste?

**R:**
1. Acessar: https://www1.receita.fazenda.gov.br/
2. Baixar certificado de teste (válido por 90 dias)
3. Converter para PFX se necessário
4. Usar em ambiente de homologação

### P: Qual é o tempo de resposta esperado?

**R:**
- Status do serviço: < 1 segundo
- Autorização: 5-30 segundos
- Consulta de protocolo: < 5 segundos
- Cancelamento: 5-30 segundos

### P: Posso emitir múltiplas NF-e em paralelo?

**R:**
Sim, mas com cuidado:
```python
# Usar thread pool
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(autorizar_nfe, nfe_id) for nfe_id in nfe_ids]
    results = [f.result() for f in futures]
```

### P: Como fazer polling de protocolo?

**R:**
```python
import time

for i in range(10):
    resp = client.nfe_consulta_protocolo(chave_nfe)
    if resp["cstat"] in ["100", "102", "103"]:  # Autorizado, Inutilizado, Denegado
        return resp
    time.sleep(5)  # Aguardar 5 segundos
```

### P: O que fazer se a NF-e for rejeitada?

**R:**
1. Verificar motivo da rejeição (xmotivo)
2. Corrigir dados
3. Criar nova NF-e com número incrementado
4. Inutilizar número rejeitado (opcional)

### P: Como cancelar uma NF-e?

**R:**
```python
# Apenas NF-e autorizada pode ser cancelada
# Enviar evento de cancelamento
# Aguardar protocolo de cancelamento
```

### P: Qual é o limite de itens por NF-e?

**R:**
- Não há limite técnico
- Recomendado: até 120 itens por NF-e
- Acima disso, considerar dividir em múltiplas NF-e

### P: Como fazer backup de XMLs?

**R:**
```python
# Salvar XML assinado no banco de dados
nfe.xml_assinado = xml_assinado
db.commit()

# Ou em arquivo
with open(f"nfe_{chave_nfe}.xml", "w") as f:
    f.write(xml_assinado)
```

### P: Como integrar com sistema de nota fiscal impressa?

**R:**
1. Gerar DANFE (Documento Auxiliar da NF-e)
2. Imprimir com código de barras
3. Usar biblioteca como `reportlab` ou `weasyprint`

### P: Qual é o custo de usar NF-e?

**R:**
- Gratuito (sem taxa de emissão)
- Apenas custos de certificado digital (anual)
- Certificado de teste: gratuito

### P: Como monitorar saúde do serviço?

**R:**
```python
# Verificar status regularmente
import schedule

def check_sefaz_health():
    client = SefazSOAPClient(cert_path, cert_password)
    resp = client.nfe_status_servico()
    if resp["cstat"] != "107":
        send_alert("SEFAZ indisponível")

schedule.every(5).minutes.do(check_sefaz_health)
```

## 🔍 Debug

### Ativar Logs Detalhados

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('zeep').setLevel(logging.DEBUG)
logging.getLogger('requests').setLevel(logging.DEBUG)
```

### Inspecionar XML Gerado

```python
from lxml import etree

# Salvar XML para inspeção
with open("nfe_debug.xml", "w") as f:
    f.write(etree.tostring(root, encoding='unicode', pretty_print=True))

# Validar XML
import subprocess
subprocess.run(["xmllint", "--schema", "nfe_v4.00.xsd", "nfe_debug.xml"])
```

### Testar Certificado

```python
from cryptography.hazmat.primitives.serialization import pkcs12

with open('cert.pfx', 'rb') as f:
    private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
        f.read(), b'senha'
    )
    print(f"Certificado válido até: {certificate.not_valid_after}")
    print(f"Chave privada: {private_key is not None}")
```

### Testar Conexão SEFAZ

```python
import requests
from requests.auth import HTTPBasicAuth

# Teste simples
response = requests.get(
    'https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeStatusServico4',
    cert=('cert.pfx', 'cert.pfx'),
    verify=True,
    timeout=10
)
print(f"Status: {response.status_code}")
```

## 📊 Performance

### Otimizações

1. **Cache de cliente SOAP**
   ```python
   # Reutilizar cliente
   self.clients = {}  # Cache
   ```

2. **Connection pooling**
   ```python
   # Usar session com pool
   session = Session()
   adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
   session.mount('https://', adapter)
   ```

3. **Batch de requisições**
   ```python
   # Enviar múltiplas NF-e em um lote
   # Usar NFeAutorizacaoLote em vez de individual
   ```

## 🆘 Contato e Suporte

### SEFAZ-MG
- **Portal**: https://hnfe.fazenda.mg.gov.br/
- **Email**: nfe@fazenda.mg.gov.br
- **Telefone**: (31) 3915-6000

### Receita Federal
- **Portal**: https://www.nfe.fazenda.gov.br/
- **Manuais**: https://www1.receita.fazenda.gov.br/manuais/

### Comunidade
- **Fórum**: https://www.nfe.fazenda.gov.br/portal/
- **GitHub**: Buscar por "nfe-python"
- **Stack Overflow**: Tag `nfe` ou `sefaz`

## 📚 Referências

- [Especificação Técnica NF-e 4.00](https://www1.receita.fazenda.gov.br/manuais/)
- [Manual de Integração SEFAZ-MG](https://hnfe.fazenda.mg.gov.br/)
- [Zeep Documentation](https://docs.python-zeep.org/)
- [Cryptography Documentation](https://cryptography.io/)
- [XMLDSig Specification](https://www.w3.org/TR/xmldsig-core/)
