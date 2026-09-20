# Deploy — HubLuisEden

## Pré-requisitos

- Docker + Docker Compose instalados no servidor
- Rede `easypanel` criada: `docker network create easypanel`
- Traefik configurado no Easypanel

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```bash
cp .env.example .env
```

Campos obrigatórios:
- `SECRET_KEY` — chave JWT (mínimo 32 caracteres)
- `luis_ed_DB_HOST` — host do MySQL
- `luis_ed_DB_PORT` — porta do MySQL
- `luis_ed_DB_NAME` — nome do banco
- `luis_ed_DB_USER` — usuário do banco
- `luis_ed_DB_PASSWORD` — senha do banco

Em produção, configure esses valores como credenciais secretas no Jenkins. O pipeline
gera `.env` apenas no servidor durante o deploy e remove o arquivo ao final. Não
adicione credenciais ao GitHub.

## Deploy local (desenvolvimento)

```bash
docker-compose up --build
```

Serviços disponíveis em:
- Gateway: http://localhost:8000/docs
- svc-auth: http://localhost:8001/docs
- svc-catalogo: http://localhost:8002/docs
- svc-vendas: http://localhost:8003/docs
- svc-financeiro: http://localhost:8004/docs
- svc-orcamentos: http://localhost:8005/docs
- svc-manutencao: http://localhost:8006/docs
- svc-fornecedores: http://localhost:8007/docs
- svc-usuarios: http://localhost:8008/docs

## Deploy produção (Easypanel/Hostinger)

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Health check

```bash
curl https://luiseden.com.br/v1/eden/health
```

## Primeiro acesso

Credenciais padrão criadas no startup:
- Email: `admin@luiseden.com.br`
- Senha: `admin123`

**Altere a senha imediatamente após o primeiro login.**
