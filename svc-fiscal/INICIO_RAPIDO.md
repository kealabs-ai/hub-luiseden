# 🚀 Guia Rápido de Início - Módulo Fiscal

## ⏱️ 5 Minutos para Começar

### 1️⃣ Instalar Dependências (1 min)

```bash
cd svc-fiscal
pip install -r requirements.txt
```

### 2️⃣ Configurar Banco de Dados (1 min)

```bash
# Executar migração SQL
mysql -u root -p hub_luis_eden < ../migrations/20250120_create_fiscal_tables.sql
```

### 3️⃣ Configurar Variáveis de Ambiente (1 min)

```bash
# Criar arquivo .env
cat > .env << EOF
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=hub_luis_eden
SECRET_KEY=sua-chave-secreta-muito-segura
EOF
```

### 4️⃣ Executar Serviço (1 min)

```bash
uvicorn main:app --reload --port 8000
```

### 5️⃣ Testar (1 min)

```bash
# Em outro terminal
curl http://localhost:8000/health
```

**Pronto! ✅ Serviço rodando em http://localhost:8000**

---

## 📋 Próximos Passos

### Passo 1: Obter Certificado de Teste

```bash
# Baixar em: https://www1.receita.fazenda.gov.br/
# Salvar em: /etc/ssl/certs/empresa.pfx
# Ou em qualquer local seguro
```

### Passo 2: Criar Configuração Fiscal

```bash
curl -X POST http://localhost:8000/v1/eden/fiscal/configuracao \
  -H "Authorization: Bearer seu-token-jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "empresaId": "empresa-001",
    "cnpj": "12.345.678/0001-90",
    "razaoSocial": "Luis Eden Paisagismo LTDA",
    "nomeFantasia": "Luis Eden",
    "inscricaoEstadual": "123.456.789.012",
    "certificadoPath": "/etc/ssl/certs/empresa.pfx",
    "certificadoSenha": "senha-do-certificado"
  }'
```

### Passo 3: Verificar Status SEFAZ

```bash
curl -X GET http://localhost:8000/v1/eden/fiscal/status-sefaz \
  -H "Authorization: Bearer seu-token-jwt"
```

### Passo 4: Criar NF-e

```bash
curl -X POST http://localhost:8000/v1/eden/fiscal/nfe \
  -H "Authorization: Bearer seu-token-jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "clienteId": "cliente-001",
    "dataEmissao": "2024-01-20T10:30:00",
    "itens": [
      {
        "produtoId": "produto-001",
        "descricao": "Serviço de Paisagismo",
        "quantidade": 1,
        "valorUnitarioCents": 500000,
        "ncm": "92110000",
        "cfop": "5102"
      }
    ]
  }'
```

### Passo 5: Autorizar NF-e

```bash
curl -X POST http://localhost:8000/v1/eden/fiscal/nfe/autorizar \
  -H "Authorization: Bearer seu-token-jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "notaFiscalId": "nfe-uuid-aqui"
  }'
```

---

## 🧪 Teste Rápido Automatizado

```bash
# Executar script de teste
python test_quick.py
```

Resultado esperado:
```
✅ Health Check
✅ Status SEFAZ
✅ Criar Configuração
✅ Obter Configuração
✅ Criar NF-e
✅ Obter NF-e
✅ Assinar NF-e
✅ Autorizar NF-e

Total: 8/8 testes passaram
```

---

## 📚 Documentação Completa

| Documento | Para Quem | Tempo |
|-----------|-----------|-------|
| README.md | Visão geral | 5 min |
| EXEMPLOS_USO.md | Exemplos práticos | 10 min |
| IMPLEMENTACAO.md | Próximos passos | 15 min |
| TROUBLESHOOTING.md | Problemas comuns | 10 min |
| RESUMO_EXECUTIVO.md | Apresentação | 5 min |

---

## 🐳 Executar com Docker

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

### Docker Compose
```bash
# Adicionar ao docker-compose.yml existente
# Ver arquivo: docker-compose.snippet.yml

docker-compose up -d svc-fiscal
```

---

## 🔧 Troubleshooting Rápido

### Erro: "Conexão recusada"
```bash
# Verificar se serviço está rodando
curl http://localhost:8000/health

# Se não funcionar, iniciar serviço
uvicorn main:app --reload --port 8000
```

### Erro: "Token inválido"
```bash
# Usar token JWT válido
# Gerar token no serviço de autenticação (svc-auth)
```

### Erro: "Certificado não encontrado"
```bash
# Verificar caminho do certificado
ls -la /etc/ssl/certs/empresa.pfx

# Verificar permissões
chmod 644 /etc/ssl/certs/empresa.pfx
```

### Erro: "SEFAZ indisponível"
```bash
# SEFAZ-MG realiza manutenção às terças-feiras
# Verificar status em: https://hnfe.fazenda.mg.gov.br/
```

---

## 📊 Fluxo Rápido

```
1. Criar NF-e
   ↓
2. Assinar
   ↓
3. Autorizar
   ↓
4. Consultar Protocolo
   ↓
5. NF-e Autorizada ✅
```

---

## 🎯 Checklist de Início

- [ ] Instalar dependências
- [ ] Configurar banco de dados
- [ ] Configurar variáveis de ambiente
- [ ] Executar serviço
- [ ] Testar health check
- [ ] Obter certificado de teste
- [ ] Criar configuração fiscal
- [ ] Verificar status SEFAZ
- [ ] Criar NF-e
- [ ] Autorizar NF-e

---

## 💡 Dicas

1. **Use o script de teste**: `python test_quick.py`
2. **Leia os exemplos**: `EXEMPLOS_USO.md`
3. **Consulte o FAQ**: `TROUBLESHOOTING.md`
4. **Verifique os logs**: `docker-compose logs -f svc-fiscal`
5. **Teste localmente primeiro**: Antes de ir para produção

---

## 📞 Precisa de Ajuda?

1. **Documentação**: Leia `README.md`
2. **Exemplos**: Veja `EXEMPLOS_USO.md`
3. **Problemas**: Consulte `TROUBLESHOOTING.md`
4. **Implementação**: Siga `IMPLEMENTACAO.md`

---

## ✅ Pronto!

Você está pronto para começar a usar o módulo fiscal!

**Próximo passo:** Obter certificado de teste e criar sua primeira NF-e.

---

**Módulo Fiscal - Versão 1.0.0**
**Status: ✅ Pronto para Usar**
