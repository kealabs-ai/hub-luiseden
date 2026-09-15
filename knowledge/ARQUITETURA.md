# HubLuisEden — Arquitetura

## Visão Geral

Backend de microserviços para o sistema de gestão Luis Eden (paisagismo/plantas).

## Stack

- **Runtime**: Python 3.12
- **Framework**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0
- **Banco**: MySQL (via PyMySQL)
- **Auth**: JWT (python-jose) + bcrypt
- **Deploy**: Docker + Traefik (Easypanel/Hostinger)

## Microserviços

| Serviço          | Porta local | Rota base              | Responsabilidade              |
|------------------|-------------|------------------------|-------------------------------|
| hubluiseden      | 8000        | /v1/eden/*             | Gateway monolítico (dev)      |
| svc-auth         | 8001        | /v1/eden/auth          | Login, JWT                    |
| svc-catalogo     | 8002        | /v1/eden/catalogo      | Plantas, estoque              |
| svc-vendas       | 8003        | /v1/eden/vendas        | Vendas, itens, dashboard      |
| svc-financeiro   | 8004        | /v1/eden/financeiro    | Fluxo de caixa, transações    |
| svc-orcamentos   | 8005        | /v1/eden/orcamentos    | Orçamentos de paisagismo      |
| svc-manutencao   | 8006        | /v1/eden/manutencao    | Agenda de manutenção          |
| svc-fornecedores | 8007        | /v1/eden/fornecedores  | Cadastro de fornecedores      |
| svc-usuarios     | 8008        | /v1/eden/usuarios      | Gestão de usuários (admin)    |

## Padrão de endpoints

Todos os serviços seguem o padrão:
- `GET    /v1/eden/<recurso>`         — listar
- `POST   /v1/eden/<recurso>`         — criar
- `POST   /v1/eden/<recurso>/get`     — buscar por id
- `POST   /v1/eden/<recurso>/update`  — atualizar
- `POST   /v1/eden/<recurso>/delete`  — remover (soft ou hard delete)
- `GET    /health`                    — health check

## Autenticação

Todos os endpoints (exceto `/health` e `/v1/eden/auth/login`) exigem header:
```
Authorization: Bearer <token>
```

## Roles

- `admin` — acesso total
- `operador` — acesso operacional (vendas, catálogo, etc.)
- `cliente` — acesso restrito (futuro)
