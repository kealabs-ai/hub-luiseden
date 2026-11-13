# 🔧 Correções Aplicadas - Módulo Fiscal

## ✅ Problemas Resolvidos

### 1. Conexão com Banco de Dados (Backend)
**Problema:** `ConnectionRefusedError: [Errno 111] Connection refused` ao conectar em `localhost`

**Solução:**
- Alterado host padrão de `localhost` para `db` (nome do serviço Docker)
- Adicionados valores padrão para variáveis de ambiente
- Arquivo: `svc-fiscal/database.py`

```python
# Antes
self.host = os.getenv("luis_ed_DB_HOST")  # Obrigatório

# Depois
self.host = os.getenv("luis_ed_DB_HOST", "db")  # Padrão: db
```

### 2. Variáveis de Ambiente (Frontend)
**Problema:** `ReferenceError: process is not defined` em `fiscalApi.js`

**Solução:**
- Alterado de `process.env.REACT_APP_API_URL` para `import.meta.env.VITE_API_URL`
- Seguido o mesmo padrão de `api.js` existente
- Adicionados interceptadores de autenticação
- Arquivo: `app/src/modules/fiscal/services/fiscalApi.js`

```javascript
// Antes
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

// Depois
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'https://srv1023256.hstgr.cloud').replace(/\/$/, '')
const API_PREFIX = '/v1/eden/fiscal'
```

## 📋 Variáveis de Ambiente Necessárias

### Backend (svc-fiscal/.env)
```env
# Banco de Dados
luis_ed_DB_HOST=db
luis_ed_DB_PORT=3306
luis_ed_DB_NAME=hub_luis_eden
luis_ed_DB_USER=root
luis_ed_DB_PASSWORD=

# Autenticação
SECRET_KEY=changeme-secret-key

# Fiscal
FISCAL_AMBIENTE=2
FISCAL_UF=MG
FISCAL_CODIGO_IBGE_UF=31

# Certificado Digital
CERTIFICADO_PATH=/etc/ssl/certs/empresa.pfx
CERTIFICADO_SENHA=
```

### Frontend (.env ou .env.local)
```env
VITE_API_URL=https://srv1023256.hstgr.cloud
```

## 🐳 Docker Compose

O serviço `svc-fiscal` deve estar configurado no `docker-compose.yml`:

```yaml
svc-fiscal:
  build:
    context: ./svc-fiscal
    dockerfile: Dockerfile
  container_name: eden-svc-fiscal
  ports:
    - "9010:8000"
  environment:
    - luis_ed_DB_HOST=db
    - luis_ed_DB_PORT=3306
    - luis_ed_DB_USER=root
    - luis_ed_DB_PASSWORD=${DB_PASSWORD}
    - luis_ed_DB_NAME=hub_luis_eden
    - SECRET_KEY=${SECRET_KEY}
  depends_on:
    - db
  networks:
    - hub-network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

## ✅ Verificação

### Backend
```bash
# Verificar saúde do serviço
curl http://localhost:9010/health

# Resposta esperada
{"status": "ok", "service": "svc-fiscal"}
```

### Frontend
```bash
# Verificar se a API está acessível
curl -H "Authorization: Bearer TOKEN" http://localhost:9010/v1/eden/fiscal/status-sefaz
```

## 📝 Notas Importantes

1. **Host do Banco**: Em Docker, use `db` (nome do serviço) em vez de `localhost`
2. **Variáveis de Ambiente**: Prefixo `luis_ed_` para manter consistência com outros serviços
3. **Vite vs Create React App**: O projeto usa Vite, então use `import.meta.env` em vez de `process.env`
4. **Interceptadores**: O `fiscalApi.js` agora usa os mesmos interceptadores de autenticação que `api.js`

## 🔗 Referências

- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Docker Networking](https://docs.docker.com/network/)
- [SQLAlchemy Connection Strings](https://docs.sqlalchemy.org/en/20/core/engines.html)
