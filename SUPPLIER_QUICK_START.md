# 🚀 Guia Rápido - Implementação de Fornecedores

## ✅ O que foi implementado

### Backend (svc-fornecedores)
- ✅ Modelo `Cotacao` com relacionamento com `Fornecedor`
- ✅ 5 endpoints para CRUD de cotações
- ✅ Validação de dados com Pydantic
- ✅ Soft delete (marca como inativo)

### Frontend (React)
- ✅ Página `/supplier` com 2 abas
- ✅ 4 componentes de modal (New/Edit Supplier, New/Edit Quotation)
- ✅ Integração completa com API
- ✅ Sincronização automática de dados
- ✅ Cálculo de margem de lucro
- ✅ Tratamento de erros e validações

### Banco de Dados
- ✅ Tabela `cotacoes` com foreign key
- ✅ Migração SQL pronta

## 🔧 Passos para Ativar

### 1. Banco de Dados
```bash
# Execute a migração
mysql -u seu_usuario -p seu_banco < migrations/20250120_add_cotacoes_table.sql
```

### 2. Backend
```bash
# Reinicie o serviço (ele criará a tabela automaticamente)
cd svc-fornecedores
python -m uvicorn main:app --reload --port 8007
```

### 3. Frontend
```bash
# Já está pronto, apenas acesse
# http://localhost:3000/supplier
```

## 📋 Funcionalidades

### Aba Fornecedores
| Ação | Descrição |
|------|-----------|
| Listar | Mostra todos os fornecedores ativos |
| Criar | Novo fornecedor com validação |
| Editar | Atualiza dados do fornecedor |
| Deletar | Remove fornecedor (soft delete) |
| Importar | Excel (já existente) |

### Aba Cotações
| Ação | Descrição |
|------|-----------|
| Listar | Mostra todas as cotações ativas |
| Criar | Nova cotação com cálculo de margem |
| Editar | Atualiza cotação |
| Deletar | Remove cotação (soft delete) |

## 🧪 Testar

### Via Postman
1. Importe: `postman/hubluiseden.postman_collection.json`
2. Configure token JWT
3. Teste endpoints em `/fornecedores/cotacoes`

### Via Frontend
1. Acesse `http://localhost:3000/supplier`
2. Clique em "Novo Fornecedor"
3. Preencha e salve
4. Clique em "Nova Cotação"
5. Selecione fornecedor e preencha

## 📁 Arquivos Criados/Modificados

### Criados
```
svc-fornecedores/main.py (atualizado)
app/src/components/EditSupplierModal.jsx
app/src/components/NewQuotationModal.jsx
app/src/components/EditQuotationModal.jsx
app/src/modules/supplier/pages/Supplier.jsx (atualizado)
app/src/services/api.js (atualizado)
app/src/components/AppNavigation.jsx (atualizado)
migrations/20250120_add_cotacoes_table.sql
```

## 🔗 Endpoints da API

### Fornecedores
```
GET    /v1/eden/fornecedores
POST   /v1/eden/fornecedores
POST   /v1/eden/fornecedores/get
POST   /v1/eden/fornecedores/update
POST   /v1/eden/fornecedores/delete
```

### Cotações
```
GET    /v1/eden/fornecedores/cotacoes
POST   /v1/eden/fornecedores/cotacoes
POST   /v1/eden/fornecedores/cotacoes/get
POST   /v1/eden/fornecedores/cotacoes/update
POST   /v1/eden/fornecedores/cotacoes/delete
```

## 💡 Exemplos de Uso

### Criar Fornecedor
```bash
curl -X POST http://localhost:8007/v1/eden/fornecedores \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Flores Brasil",
    "email": "contato@flores.com",
    "telefone": "(11) 98765-4321",
    "endereco": "Rua das Flores, 123",
    "categoria": "Flores"
  }'
```

### Criar Cotação
```bash
curl -X POST http://localhost:8007/v1/eden/fornecedores/cotacoes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "fornecedorId": "uuid-do-fornecedor",
    "descricao": "Rosa Vermelha Premium",
    "quantidade": 100,
    "precoCustoCents": 2500,
    "precoVendaCents": 4500
  }'
```

## 🎯 Próximas Etapas (Opcional)

1. **Filtros avançados** - Por categoria, status, data
2. **Exportar Excel** - Relatório de cotações
3. **Gráficos** - Margem de lucro por fornecedor
4. **Histórico** - Rastrear mudanças de preço
5. **Notificações** - Alertas de preço

## ❓ Dúvidas?

Consulte:
- `SUPPLIER_IMPLEMENTATION.md` - Documentação completa
- `knowledge/ARQUITETURA.md` - Arquitetura geral
- `postman/hubluiseden.postman_collection.json` - Exemplos de API

---

**Status:** ✅ Pronto para produção
**Versão:** 1.0.0
**Data:** 2025-01-20
