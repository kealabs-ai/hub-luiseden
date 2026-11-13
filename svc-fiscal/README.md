# Módulo Fiscal - Integração SEFAZ-MG NF-e 4.00

## 📋 Visão Geral

Módulo backend para integração com SEFAZ-MG em ambiente de homologação (testes). Implementa:

- ✅ Geração de XML NF-e conforme layout 4.00
- ✅ Assinatura digital com certificado A1/A3
- ✅ Comunicação SOAP com mTLS
- ✅ Autorização, consulta e cancelamento de NF-e
- ✅ Tratamento de eventos (cancelamento, carta de correção)
- ✅ Persistência de dados e protocolos

## 🏗️ Arquitetura

```
svc-fiscal/
├── main.py                 # Endpoints FastAPI
├── database.py             # Configuração de BD
├── models.py               # Modelos SQLAlchemy + Pydantic
├── nfe_generator.py        # Gerador de XML NF-e 4.00
├── xml_signer.py           # Assinatura digital XMLDSig
├── sefaz_client.py         # Cliente SOAP com mTLS
├── requirements.txt        # Dependências
└── Dockerfile              # Containerização
```

## 🔧 Configuração

### 1. Variáveis de Ambiente (.env)

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=senha
DB_NAME=hub_luis_eden
SECRET_KEY=sua-chave-secreta
```

### 2. Certificado Digital

- Formato: `.pfx` (PKCS#12) ou `.pem`
- Tipo: A1 (arquivo) ou A3 (token)
- Armazenar em local seguro (ex: `/etc/ssl/certs/`)
- Passar caminho na configuração fiscal

## 📡 Endpoints

### Configuração Fiscal

#### POST `/v1/eden/fiscal/configuracao`
Cria configuração fiscal da empresa

```json
{
  "empresaId": "uuid-empresa",
  "cnpj": "12.345.678/0001-90",
  "razaoSocial": "Luis Eden Paisagismo LTDA",
  "nomeFantasia": "Luis Eden",
  "inscricaoEstadual": "123.456.789.012",
  "certificadoPath": "/etc/ssl/certs/empresa.pfx",
  "certificadoSenha": "senha-certificado"
}
```

**Response:**
```json
{
  "id": "config-uuid",
  "status": "criada"
}
```

#### GET `/v1/eden/fiscal/configuracao/{empresa_id}`
Obtém configuração fiscal

**Response:**
```json
{
  "id": "config-uuid",
  "cnpj": "12.345.678/0001-90",
  "razaoSocial": "Luis Eden Paisagismo LTDA",
  "nomeFantasia": "Luis Eden",
  "inscricaoEstadual": "123.456.789.012",
  "uf": "MG",
  "ambiente": 2,
  "proximoNumero": 1
}
```

### Notas Fiscais

#### POST `/v1/eden/fiscal/nfe`
Cria rascunho de NF-e

```json
{
  "clienteId": "cliente-uuid",
  "dataEmissao": "2024-01-20T10:30:00",
  "itens": [
    {
      "produtoId": "produto-uuid",
      "descricao": "Serviço de Paisagismo",
      "quantidade": 1,
      "valorUnitarioCents": 50000,
      "ncm": "92110000",
      "cfop": "5102"
    }
  ]
}
```

**Response:**
```json
{
  "id": "nfe-uuid",
  "numero": 1,
  "status": "rascunho"
}
```

#### GET `/v1/eden/fiscal/nfe/{nfe_id}`
Obtém dados completos da NF-e

**Response:**
```json
{
  "id": "nfe-uuid",
  "chaveNfe": "35240101234567000123550010000000011234567890",
  "numero": 1,
  "serie": 1,
  "clienteId": "cliente-uuid",
  "dataEmissao": "2024-01-20T10:30:00",
  "valorTotalCents": 50000,
  "status": "autorizada",
  "protocolo": "135240101234567",
  "dataAutorizacao": "2024-01-20T10:35:00",
  "motivoRejeicao": null,
  "itens": [
    {
      "id": "item-uuid",
      "produtoId": "produto-uuid",
      "descricao": "Serviço de Paisagismo",
      "quantidade": 1,
      "valorUnitarioCents": 50000,
      "valorTotalCents": 50000,
      "ncm": "92110000",
      "cfop": "5102"
    }
  ]
}
```

### Assinatura e Autorização

#### POST `/v1/eden/fiscal/nfe/assinar`
Assina XML com certificado digital

```json
{
  "notaFiscalId": "nfe-uuid"
}
```

**Response:**
```json
{
  "status": "assinada",
  "nfeId": "nfe-uuid"
}
```

#### POST `/v1/eden/fiscal/nfe/autorizar`
Envia NF-e para autorização na SEFAZ

```json
{
  "notaFiscalId": "nfe-uuid"
}
```

**Response:**
```json
{
  "status": "enviada",
  "nfeId": "nfe-uuid",
  "numeroRecibo": "123456789012345",
  "cstat": "103"
}
```

### Consultas

#### POST `/v1/eden/fiscal/nfe/consulta-protocolo`
Consulta protocolo de autorização

```json
{
  "chaveNfe": "35240101234567000123550010000000011234567890"
}
```

**Response:**
```json
{
  "chaveNfe": "35240101234567000123550010000000011234567890",
  "status": "autorizada",
  "protocolo": "135240101234567",
  "cstat": "100",
  "xmotivo": "Autorizado o uso da NF-e"
}
```

#### GET `/v1/eden/fiscal/status-sefaz`
Verifica status do serviço SEFAZ

**Response:**
```json
{
  "status": "sucesso",
  "cstat": "107",
  "xmotivo": "Serviço em operação",
  "dhrecbto": "2024-01-20T10:30:00",
  "tMed": 5
}
```

### Cancelamento

#### POST `/v1/eden/fiscal/nfe/cancelar`
Cancela NF-e autorizada

```json
{
  "notaFiscalId": "nfe-uuid",
  "justificativa": "Operação cancelada pelo contribuinte"
}
```

**Response:**
```json
{
  "status": "cancelamento_enviado",
  "nfeId": "nfe-uuid"
}
```

## 🔐 Segurança

### mTLS (Mutual TLS)

O cliente SOAP utiliza certificado digital para autenticação:

```python
session.cert = (cert_path, cert_path)
session.verify = True
```

### Validação de Certificado

- Verificação de hostname habilitada
- Validação de cadeia de certificados
- Timeout de 30 segundos

## 📊 Fluxo de Autorização

```
1. Criar NF-e (rascunho)
   ↓
2. Assinar XML com certificado
   ↓
3. Verificar status SEFAZ
   ↓
4. Enviar para autorização
   ↓
5. Obter número de recibo
   ↓
6. Consultar protocolo (polling)
   ↓
7. NF-e autorizada com protocolo
```

## 🔄 Códigos de Status (cStat)

| Código | Significado |
|--------|-------------|
| 100 | Autorizado |
| 102 | Inutilizado |
| 103 | Denegado |
| 104 | Uso Denegado |
| 105 | Cancelado |
| 106 | Cancelado Extemporâneo |
| 107 | Serviço em operação |
| 108 | Serviço indisponível |
| 109 | Autorizado Adição Interesses |
| 110 | Autorizado Cancelamento |

## 🛠️ Desenvolvimento Local

### Instalação

```bash
cd svc-fiscal
pip install -r requirements.txt
```

### Executar

```bash
uvicorn main:app --reload --port 8000
```

### Testes

```bash
# Verificar saúde
curl http://localhost:8000/health

# Criar configuração
curl -X POST http://localhost:8000/v1/eden/fiscal/configuracao \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d @config.json
```

## 🐳 Docker

### Build

```bash
docker build -t svc-fiscal:latest .
```

### Run

```bash
docker run -p 8000:8000 \
  -e DB_HOST=db \
  -e DB_USER=root \
  -e DB_PASSWORD=senha \
  -v /path/to/certs:/etc/ssl/certs:ro \
  svc-fiscal:latest
```

## 📝 Notas Importantes

### Ambiente de Homologação

- **Não tem validade jurídica**
- Usado apenas para testes
- Dados não são registrados na SEFAZ
- Certificado de teste disponível em: https://www1.receita.fazenda.gov.br/

### Próximas Implementações

- [ ] Suporte a A3 (token)
- [ ] Carta de correção
- [ ] Manifestação do destinatário
- [ ] Consulta de cadastro (CadConsultaCadastro4)
- [ ] Inutilização de numeração
- [ ] Backup automático de XMLs
- [ ] Webhook para notificações
- [ ] Dashboard de status

## 🔗 Referências

- [Portal NF-e](https://www.nfe.fazenda.gov.br/)
- [Manual de Integração SEFAZ-MG](https://hnfe.fazenda.mg.gov.br/)
- [Especificação Técnica NF-e 4.00](https://www1.receita.fazenda.gov.br/manuais/)
- [Zeep Documentation](https://docs.python-zeep.org/)
