# ALTERAÇÕES - Serviço de Orçamentos (svc-orcamentos)

## 📋 Problema Identificado
Os itens do orçamento não estavam sendo salvos no banco de dados ao criar um novo orçamento.

## ✅ Solução Implementada

### 1. **Atualização do Schema Pydantic**

#### Antes:
```python
class OrcamentoIn(BaseModel):
    clienteNome: Optional[str] = None
    descricao: Optional[str] = None
    totalCents: int = 0
    validade: Optional[str] = None
```

#### Depois:
```python
class ItemOrcamentoIn(BaseModel):
    descricao: str
    quantidade: int = 1
    precoCents: int = 0

class OrcamentoIn(BaseModel):
    clienteNome: Optional[str] = None
    descricao: Optional[str] = None
    totalCents: int = 0
    status: str = "pendente"
    validade: Optional[str] = None
    itens: Optional[List[ItemOrcamentoIn]] = None
```

### 2. **Atualização da Função Create**

#### Antes:
```python
@app.post("/v1/eden/orcamentos", status_code=201)
def create_orcamento(body: OrcamentoIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = Orcamento(usuario_id=payload["sub"], cliente_nome=body.clienteNome,
                  descricao=body.descricao, total_cents=body.totalCents, validade=body.validade)
    db.add(o); db.commit(); db.refresh(o)
    return _to_dict(o)
```

#### Depois:
```python
@app.post("/v1/eden/orcamentos", status_code=201)
def create_orcamento(body: OrcamentoIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = Orcamento(
        usuario_id=payload["sub"],
        cliente_nome=body.clienteNome,
        descricao=body.descricao,
        total_cents=body.totalCents,
        status=body.status,
        validade=body.validade
    )
    db.add(o)
    db.commit()
    db.refresh(o)
    
    # Salvar itens do orçamento
    items = []
    if body.itens:
        for item_data in body.itens:
            item = ItemOrcamento(
                orcamento_id=o.id,
                descricao=item_data.descricao,
                quantidade=item_data.quantidade,
                preco_cents=item_data.precoCents
            )
            db.add(item)
            items.append(item)
        db.commit()
    
    return _to_dict(o, items)
```

### 3. **Atualização das Funções List e Get**

Agora retornam os itens junto com o orçamento:

```python
@app.get("/v1/eden/orcamentos")
def list_orcamentos(db: Session = Depends(get_db), payload=Depends(verify_token)):
    orcamentos = db.query(Orcamento).order_by(Orcamento.created_at.desc()).all()
    result = []
    for o in orcamentos:
        items = db.query(ItemOrcamento).filter_by(orcamento_id=o.id).all()
        result.append(_to_dict(o, items))
    return result

@app.post("/v1/eden/orcamentos/get")
def get_orcamento(body: OrcamentoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = db.query(Orcamento).filter_by(id=body.id).first()
    if not o: raise HTTPException(404, "Não encontrado")
    items = db.query(ItemOrcamento).filter_by(orcamento_id=o.id).all()
    return _to_dict(o, items)
```

### 4. **Atualização da Função Delete**

Agora deleta os itens junto com o orçamento:

```python
@app.post("/v1/eden/orcamentos/delete")
def delete_orcamento(body: OrcamentoGetIn, db: Session = Depends(get_db), payload=Depends(verify_token)):
    o = db.query(Orcamento).filter_by(id=body.id).first()
    if not o: raise HTTPException(404, "Não encontrado")
    
    # Deletar itens do orçamento
    db.query(ItemOrcamento).filter_by(orcamento_id=o.id).delete()
    db.delete(o)
    db.commit()
    return {"ok": True}
```

### 5. **Função de Conversão Atualizada**

```python
def _item_to_dict(item: ItemOrcamento):
    return {
        "id": item.id,
        "orcamentoId": item.orcamento_id,
        "descricao": item.descricao,
        "quantidade": item.quantidade,
        "precoCents": item.preco_cents
    }

def _to_dict(o: Orcamento, items: List[ItemOrcamento] = None):
    result = {
        "id": o.id,
        "usuarioId": o.usuario_id,
        "clienteNome": o.cliente_nome,
        "descricao": o.descricao,
        "totalCents": o.total_cents,
        "status": o.status,
        "validade": o.validade,
        "createdAt": o.created_at.isoformat(),
        "updatedAt": o.updated_at.isoformat()
    }
    if items:
        result["itens"] = [_item_to_dict(item) for item in items]
    return result
```

## 📝 Exemplo de Requisição

### POST /v1/eden/orcamentos

```json
{
  "clienteNome": "Dra. Sofia",
  "descricao": "Projeto residential - 3 itens",
  "totalCents": 140000,
  "status": "pendente",
  "itens": [
    {
      "descricao": "Rosa Vermelha",
      "quantidade": 5,
      "precoCents": 2500
    },
    {
      "descricao": "Lírio Branco",
      "quantidade": 3,
      "precoCents": 3000
    },
    {
      "descricao": "Orquídea Rosa",
      "quantidade": 2,
      "precoCents": 4000
    }
  ]
}
```

### Resposta

```json
{
  "id": "orcamento-123",
  "usuarioId": "user-456",
  "clienteNome": "Dra. Sofia",
  "descricao": "Projeto residential - 3 itens",
  "totalCents": 140000,
  "status": "pendente",
  "validade": null,
  "createdAt": "2025-01-22T10:30:00",
  "updatedAt": "2025-01-22T10:30:00",
  "itens": [
    {
      "id": "item-1",
      "orcamentoId": "orcamento-123",
      "descricao": "Rosa Vermelha",
      "quantidade": 5,
      "precoCents": 2500
    },
    {
      "id": "item-2",
      "orcamentoId": "orcamento-123",
      "descricao": "Lírio Branco",
      "quantidade": 3,
      "precoCents": 3000
    },
    {
      "id": "item-3",
      "orcamentoId": "orcamento-123",
      "descricao": "Orquídea Rosa",
      "quantidade": 2,
      "precoCents": 4000
    }
  ]
}
```

## 🚀 Próximos Passos

1. ✅ Reiniciar o serviço svc-orcamentos
2. ✅ Testar criação de novo orçamento com itens
3. ✅ Verificar se os itens aparecem no modal de visualização
4. ✅ Testar aprovação/rejeição de orçamento

## ✨ Benefícios

- ✅ Itens do orçamento são salvos no banco de dados
- ✅ Itens aparecem ao visualizar o orçamento
- ✅ Itens são deletados quando o orçamento é removido
- ✅ Estrutura consistente com outras tabelas de itens (vendas, etc)
