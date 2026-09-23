# Exemplos de Uso - Módulo Fiscal

## 1. Configurar Empresa

```bash
curl -X POST http://localhost:8000/v1/eden/fiscal/configuracao \
  -H "Authorization: Bearer seu-token-jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "empresaId": "empresa-123",
    "cnpj": "12.345.678/0001-90",
    "razaoSocial": "Luis Eden Paisagismo LTDA",
    "nomeFantasia": "Luis Eden",
    "inscricaoEstadual": "123.456.789.012",
    "certificadoPath": "/etc/ssl/certs/empresa.pfx",
    "certificadoSenha": "senha-do-certificado"
  }'
```

**Response:**
```json
{
  "id": "config-uuid-123",
  "status": "criada"
}
```

## 2. Obter Configuração

```bash
curl -X GET http://localhost:8000/v1/eden/fiscal/configuracao/empresa-123 \
  -H "Authorization: Bearer seu-token-jwt"
```

**Response:**
```json
{
  "id": "config-uuid-123",
  "cnpj": "12.345.678/0001-90",
  "razaoSocial": "Luis Eden Paisagismo LTDA",
  "nomeFantasia": "Luis Eden",
  "inscricaoEstadual": "123.456.789.012",
  "uf": "MG",
  "ambiente": 2,
  "proximoNumero": 1
}
```

## 3. Verificar Status SEFAZ

```bash
curl -X GET http://localhost:8000/v1/eden/fiscal/status-sefaz \
  -H "Authorization: Bearer seu-token-jwt"
```

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

## 4. Criar NF-e (Rascunho)

```bash
curl -X POST http://localhost:8000/v1/eden/fiscal/nfe \
  -H "Authorization: Bearer seu-token-jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "clienteId": "cliente-456",
    "dataEmissao": "2024-01-20T10:30:00",
    "itens": [
      {
        "produtoId": "produto-789",
        "descricao": "Serviço de Paisagismo - Projeto Residencial",
        "quantidade": 1,
        "valorUnitarioCents": 500000,
        "ncm": "92110000",
        "cfop": "5102"
      },
      {
        "produtoId": "produto-790",
        "descricao": "Manutenção Mensal",
        "quantidade": 4,
        "valorUnitarioCents": 100000,
        "ncm": "92110000",
        "cfop": "5102"
      }
    ]
  }'
```

**Response:**
```json
{
  "id": "nfe-uuid-001",
  "numero": 1,
  "status": "rascunho"
}
```

## 5. Obter Dados da NF-e

```bash
curl -X GET http://localhost:8000/v1/eden/fiscal/nfe/nfe-uuid-001 \
  -H "Authorization: Bearer seu-token-jwt"
```

**Response:**
```json
{
  "id": "nfe-uuid-001",
  "chaveNfe": null,
  "numero": 1,
  "serie": 1,
  "clienteId": "cliente-456",
  "dataEmissao": "2024-01-20T10:30:00",
  "valorTotalCents": 900000,
  "status": "rascunho",
  "protocolo": null,
  "dataAutorizacao": null,
  "motivoRejeicao": null,
  "itens": [
    {
      "id": "item-uuid-001",
      "produtoId": "produto-789",
      "descricao": "Serviço de Paisagismo - Projeto Residencial",
      "quantidade": 1,
      "valorUnitarioCents": 500000,
      "valorTotalCents": 500000,
      "ncm": "92110000",
      "cfop": "5102"
    },
    {
      "id": "item-uuid-002",
      "produtoId": "produto-790",
      "descricao": "Manutenção Mensal",
      "quantidade": 4,
      "valorUnitarioCents": 100000,
      "valorTotalCents": 400000,
      "ncm": "92110000",
      "cfop": "5102"
    }
  ]
}
```

## 6. Assinar NF-e

```bash
curl -X POST http://localhost:8000/v1/eden/fiscal/nfe/assinar \
  -H "Authorization: Bearer seu-token-jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "notaFiscalId": "nfe-uuid-001"
  }'
```

**Response:**
```json
{
  "status": "assinada",
  "nfeId": "nfe-uuid-001"
}
```

## 7. Autorizar NF-e (Enviar para SEFAZ)

```bash
curl -X POST http://localhost:8000/v1/eden/fiscal/nfe/autorizar \
  -H "Authorization: Bearer seu-token-jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "notaFiscalId": "nfe-uuid-001"
  }'
```

**Response:**
```json
{
  "status": "enviada",
  "nfeId": "nfe-uuid-001",
  "numeroRecibo": "123456789012345",
  "cstat": "103"
}
```

## 8. Consultar Protocolo

```bash
curl -X POST http://localhost:8000/v1/eden/fiscal/nfe/consulta-protocolo \
  -H "Authorization: Bearer seu-token-jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "chaveNfe": "35240101234567000123550010000000011234567890"
  }'
```

**Response (Autorizado):**
```json
{
  "chaveNfe": "35240101234567000123550010000000011234567890",
  "status": "autorizada",
  "protocolo": "135240101234567",
  "cstat": "100",
  "xmotivo": "Autorizado o uso da NF-e"
}
```

**Response (Rejeitado):**
```json
{
  "chaveNfe": "35240101234567000123550010000000011234567890",
  "status": "rejeitada",
  "protocolo": null,
  "cstat": "302",
  "xmotivo": "Falha na validação do schema XML"
}
```

## 9. Cancelar NF-e

```bash
curl -X POST http://localhost:8000/v1/eden/fiscal/nfe/cancelar \
  -H "Authorization: Bearer seu-token-jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "notaFiscalId": "nfe-uuid-001",
    "justificativa": "Operação cancelada pelo contribuinte"
  }'
```

**Response:**
```json
{
  "status": "cancelamento_enviado",
  "nfeId": "nfe-uuid-001"
}
```

## Fluxo Completo em Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN = "seu-token-jwt"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Verificar status SEFAZ
resp = requests.get(f"{BASE_URL}/v1/eden/fiscal/status-sefaz", headers=HEADERS)
print("Status SEFAZ:", resp.json())

# 2. Criar NF-e
nfe_data = {
    "clienteId": "cliente-456",
    "dataEmissao": "2024-01-20T10:30:00",
    "itens": [
        {
            "produtoId": "produto-789",
            "descricao": "Serviço de Paisagismo",
            "quantidade": 1,
            "valorUnitarioCents": 500000,
            "ncm": "92110000",
            "cfop": "5102"
        }
    ]
}
resp = requests.post(f"{BASE_URL}/v1/eden/fiscal/nfe", json=nfe_data, headers=HEADERS)
nfe_id = resp.json()["id"]
print("NF-e criada:", nfe_id)

# 3. Assinar
resp = requests.post(
    f"{BASE_URL}/v1/eden/fiscal/nfe/assinar",
    json={"notaFiscalId": nfe_id},
    headers=HEADERS
)
print("NF-e assinada:", resp.json())

# 4. Autorizar
resp = requests.post(
    f"{BASE_URL}/v1/eden/fiscal/nfe/autorizar",
    json={"notaFiscalId": nfe_id},
    headers=HEADERS
)
print("NF-e autorizada:", resp.json())

# 5. Consultar protocolo (polling)
import time
chave_nfe = "35240101234567000123550010000000011234567890"
for i in range(10):
    resp = requests.post(
        f"{BASE_URL}/v1/eden/fiscal/nfe/consulta-protocolo",
        json={"chaveNfe": chave_nfe},
        headers=HEADERS
    )
    result = resp.json()
    print(f"Tentativa {i+1}: {result['status']}")
    
    if result["status"] in ["autorizada", "rejeitada"]:
        print(f"Protocolo: {result.get('protocolo')}")
        break
    
    time.sleep(5)
```

## Tratamento de Erros

### Certificado Inválido
```json
{
  "detail": "Erro ao assinar: Erro ao carregar certificado"
}
```

### SEFAZ Indisponível
```json
{
  "detail": "SEFAZ indisponível"
}
```

### NF-e Rejeitada
```json
{
  "detail": "Rejeição: Falha na validação do schema XML"
}
```

## Dicas de Teste

1. **Use certificado de teste**: Disponível em https://www1.receita.fazenda.gov.br/
2. **Ambiente de homologação**: Não tem validade jurídica
3. **Polling**: Aguarde 5-10 segundos entre consultas de protocolo
4. **Logs**: Verifique logs do serviço para detalhes de erros
5. **Validação XML**: Use ferramentas como xmllint para validar XMLs gerados
