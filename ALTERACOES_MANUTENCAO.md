# ALTERAÇÕES NECESSÁRIAS - Backend Manutenção

## 📋 Campos do Modal vs Banco de Dados

### Campos Enviados pelo Modal:
```javascript
{
  titulo: "Nome do Cliente/Residência",
  descricao: "Observações Técnicas",
  dataAgendada: "2024-01-15",
  status: "agendada",
  prioridade: "normal",
  frequencia: "monthly",
  valorCents: 50000,
  equipe: "carlos"
}
```

### Campos Atuais na Tabela `manutencoes`:
```sql
id, usuario_id, planta_id, titulo, descricao, data_agendada, status, created_at, updated_at
```

### ❌ Campos Faltando:
- `prioridade` (priority)
- `frequencia` (frequency)
- `valor_cents` (service value)
- `equipe` (team)
- `cliente_id` (client reference)
- `endereco` (client address)
- `telefone` (client phone)
- `proxima_manutencao` (next maintenance date)

---

## 🔧 ALTERAÇÕES NECESSÁRIAS

### 1. Criar Migration para Adicionar Campos

**Arquivo:** `migrations/20250122_add_maintenance_fields.sql`

```sql
-- Adicionar campos faltantes à tabela manutencoes
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS cliente_id VARCHAR(36) NULL AFTER usuario_id;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS prioridade VARCHAR(20) NOT NULL DEFAULT 'normal' AFTER status;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS frequencia VARCHAR(20) NOT NULL DEFAULT 'custom' AFTER prioridade;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS valor_cents INT NOT NULL DEFAULT 0 AFTER frequencia;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS equipe VARCHAR(100) NULL AFTER valor_cents;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS endereco VARCHAR(500) NULL AFTER equipe;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS telefone VARCHAR(50) NULL AFTER endereco;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS proxima_manutencao VARCHAR(10) NULL AFTER telefone;

-- Adicionar índices para melhor performance
ALTER TABLE manutencoes ADD KEY IF NOT EXISTS idx_manutencoes_cliente_id (cliente_id);
ALTER TABLE manutencoes ADD KEY IF NOT EXISTS idx_manutencoes_equipe (equipe);
ALTER TABLE manutencoes ADD KEY IF NOT EXISTS idx_manutencoes_prioridade (prioridade);
ALTER TABLE manutencoes ADD KEY IF NOT EXISTS idx_manutencoes_frequencia (frequencia);
```

### 2. Atualizar Schema Principal

**Arquivo:** `data/schema.sql`

Substituir a tabela `manutencoes`:

```sql
-- Manutenções agendadas
CREATE TABLE IF NOT EXISTS manutencoes (
    id                  VARCHAR(36)  NOT NULL,
    usuario_id          VARCHAR(36)  NOT NULL,
    cliente_id          VARCHAR(36)      NULL,
    planta_id           VARCHAR(36)      NULL,
    titulo              VARCHAR(255) NOT NULL,
    descricao           TEXT             NULL,
    data_agendada       VARCHAR(10)  NOT NULL COMMENT 'YYYY-MM-DD',
    status              VARCHAR(50)  NOT NULL DEFAULT 'agendada' COMMENT 'agendada | em_progresso | concluida | cancelada',
    prioridade          VARCHAR(20)  NOT NULL DEFAULT 'normal' COMMENT 'low | normal | high',
    frequencia          VARCHAR(20)  NOT NULL DEFAULT 'custom' COMMENT 'weekly | biweekly | monthly | quarterly | custom',
    valor_cents         INT          NOT NULL DEFAULT 0,
    equipe              VARCHAR(100)     NULL,
    endereco            VARCHAR(500)     NULL,
    telefone            VARCHAR(50)      NULL,
    proxima_manutencao  VARCHAR(10)      NULL COMMENT 'YYYY-MM-DD',
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_manutencoes_usuario_id (usuario_id),
    KEY idx_manutencoes_cliente_id (cliente_id),
    KEY idx_manutencoes_planta_id (planta_id),
    KEY idx_manutencoes_data_agendada (data_agendada),
    KEY idx_manutencoes_status (status),
    KEY idx_manutencoes_prioridade (prioridade),
    KEY idx_manutencoes_frequencia (frequencia),
    KEY idx_manutencoes_equipe (equipe)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3. Atualizar Modelo SQLAlchemy

**Arquivo:** `svc-manutencao/main.py`

```python
from sqlalchemy import Column, String, DateTime, Text, Integer

class Manutencao(Base):
    __tablename__ = "manutencoes"
    id                  = Column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id          = Column(String(36),  nullable=False)
    cliente_id          = Column(String(36),  nullable=True)
    planta_id           = Column(String(36),  nullable=True)
    titulo              = Column(String(255), nullable=False)
    descricao           = Column(Text,        nullable=True)
    data_agendada       = Column(String(10),  nullable=False)
    status              = Column(String(50),  default="agendada")
    prioridade          = Column(String(20),  default="normal")
    frequencia          = Column(String(20),  default="custom")
    valor_cents         = Column(Integer,     default=0)
    equipe              = Column(String(100), nullable=True)
    endereco            = Column(String(500), nullable=True)
    telefone            = Column(String(50),  nullable=True)
    proxima_manutencao  = Column(String(10),  nullable=True)
    created_at          = Column(DateTime,    default=datetime.utcnow)
    updated_at          = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 4. Atualizar Schemas Pydantic

**Arquivo:** `svc-manutencao/main.py`

```python
class ManutencaoIn(BaseModel):
    titulo: str
    clienteId: Optional[str] = None
    plantaId: Optional[str] = None
    descricao: Optional[str] = None
    dataAgendada: str
    status: str = "agendada"
    prioridade: str = "normal"
    frequencia: str = "custom"
    valorCents: int = 0
    equipe: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    proximaManutencao: Optional[str] = None

class ManutencaoUpdate(BaseModel):
    id: str
    titulo: Optional[str] = None
    clienteId: Optional[str] = None
    plantaId: Optional[str] = None
    descricao: Optional[str] = None
    dataAgendada: Optional[str] = None
    status: Optional[str] = None
    prioridade: Optional[str] = None
    frequencia: Optional[str] = None
    valorCents: Optional[int] = None
    equipe: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    proximaManutencao: Optional[str] = None
```

### 5. Atualizar Função de Conversão

**Arquivo:** `svc-manutencao/main.py`

```python
def _to_dict(m: Manutencao):
    return {
        "id": m.id,
        "usuarioId": m.usuario_id,
        "clienteId": m.cliente_id,
        "plantaId": m.planta_id,
        "titulo": m.titulo,
        "descricao": m.descricao,
        "dataAgendada": m.data_agendada,
        "status": m.status,
        "prioridade": m.prioridade,
        "frequencia": m.frequencia,
        "valorCents": m.valor_cents,
        "equipe": m.equipe,
        "endereco": m.endereco,
        "telefone": m.telefone,
        "proximaManutencao": m.proxima_manutencao,
        "createdAt": m.created_at.isoformat(),
        "updatedAt": m.updated_at.isoformat()
    }
```

### 6. Atualizar Função Create

**Arquivo:** `svc-manutencao/main.py`

```python
@app.post("/v1/eden/manutencao", status_code=201)
def create_manutencao(body: ManutencaoIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = Manutencao(
        usuario_id=payload["sub"],
        cliente_id=body.clienteId,
        titulo=body.titulo,
        planta_id=body.plantaId,
        descricao=body.descricao,
        data_agendada=body.dataAgendada,
        status=body.status,
        prioridade=body.prioridade,
        frequencia=body.frequencia,
        valor_cents=body.valorCents,
        equipe=body.equipe,
        endereco=body.endereco,
        telefone=body.telefone,
        proxima_manutencao=body.proximaManutencao
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return _to_dict(m)
```

### 7. Atualizar Função Update

**Arquivo:** `svc-manutencao/main.py`

```python
@app.post("/v1/eden/manutencao/update")
def update_manutencao(body: ManutencaoUpdate, db: Session = Depends(get_db), payload=Depends(verify_token)):
    m = db.query(Manutencao).filter_by(id=body.id).first()
    if not m:
        raise HTTPException(404, "Não encontrado")
    
    data = body.model_dump(exclude_none=True, exclude={"id"})
    
    # Mapear camelCase para snake_case
    field_mapping = {
        "clienteId": "cliente_id",
        "plantaId": "planta_id",
        "dataAgendada": "data_agendada",
        "valorCents": "valor_cents",
        "proximaManutencao": "proxima_manutencao"
    }
    
    for camel_key, snake_key in field_mapping.items():
        if camel_key in data:
            data[snake_key] = data.pop(camel_key)
    
    for k, v in data.items():
        setattr(m, k, v)
    
    m.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(m)
    return _to_dict(m)
```

---

## 📝 RESUMO DAS ALTERAÇÕES

| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| cliente_id | VARCHAR(36) | NULL | Referência ao cliente |
| prioridade | VARCHAR(20) | 'normal' | low, normal, high |
| frequencia | VARCHAR(20) | 'custom' | weekly, biweekly, monthly, quarterly, custom |
| valor_cents | INT | 0 | Valor do serviço em centavos |
| equipe | VARCHAR(100) | NULL | Nome da equipe responsável |
| endereco | VARCHAR(500) | NULL | Endereço do cliente |
| telefone | VARCHAR(50) | NULL | Telefone do cliente |
| proxima_manutencao | VARCHAR(10) | NULL | Data da próxima manutenção (YYYY-MM-DD) |

---

## 🚀 PASSOS PARA IMPLEMENTAR

1. ✅ Executar migration SQL
2. ✅ Atualizar modelo SQLAlchemy
3. ✅ Atualizar schemas Pydantic
4. ✅ Atualizar função `_to_dict()`
5. ✅ Atualizar função `create_manutencao()`
6. ✅ Atualizar função `update_manutencao()`
7. ✅ Testar endpoints com Postman
8. ✅ Atualizar frontend para enviar novos campos

---

## 🧪 TESTE COM POSTMAN

### Create Manutenção (POST /v1/eden/manutencao)
```json
{
  "titulo": "Condomínio Verde",
  "clienteId": "client-123",
  "descricao": "Poda de rosas, adubação, irrigação",
  "dataAgendada": "2024-01-15",
  "status": "agendada",
  "prioridade": "normal",
  "frequencia": "monthly",
  "valorCents": 50000,
  "equipe": "carlos",
  "endereco": "Rua das Flores, 123",
  "telefone": "(11) 98765-4321",
  "proximaManutencao": "2024-02-15"
}
```

### Update Manutenção (POST /v1/eden/manutencao/update)
```json
{
  "id": "maint-123",
  "status": "em_progresso",
  "prioridade": "high"
}
```
