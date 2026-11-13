# Implementação da Tela de Fornecedores (/supplier)

## 📋 Resumo

Implementação completa da funcionalidade de gerenciamento de fornecedores e cotações com frontend (React) e backend (FastAPI).

## 🏗️ Arquitetura

### Backend (svc-fornecedores)

**Arquivo:** `svc-fornecedores/main.py`

#### Modelos de Dados

1. **Fornecedor** - Cadastro de fornecedores
   - `id`: UUID único
   - `nome`: Nome da empresa
   - `email`: Email de contato
   - `telefone`: Telefone
   - `cpf_cnpj`: CPF/CNPJ
   - `endereco`: Endereço
   - `categoria`: Categoria (Flores, Plantas, Insumos, etc)
   - `ativo`: Status ativo/inativo
   - `created_at`, `updated_at`: Timestamps

2. **Cotacao** - Cotações de preços
   - `id`: UUID único
   - `fornecedor_id`: Referência ao fornecedor
   - `descricao`: Descrição do produto
   - `quantidade`: Quantidade
   - `preco_custo_cents`: Preço de custo em centavos
   - `preco_venda_cents`: Preço de venda em centavos
   - `ativo`: Status ativo/inativo
   - `created_at`, `updated_at`: Timestamps

#### Endpoints da API

**Fornecedores:**
- `GET /v1/eden/fornecedores` - Listar fornecedores ativos
- `POST /v1/eden/fornecedores` - Criar novo fornecedor
- `POST /v1/eden/fornecedores/get` - Buscar fornecedor por ID
- `POST /v1/eden/fornecedores/update` - Atualizar fornecedor
- `POST /v1/eden/fornecedores/delete` - Deletar fornecedor (soft delete)

**Cotações:**
- `GET /v1/eden/fornecedores/cotacoes` - Listar cotações ativas
- `POST /v1/eden/fornecedores/cotacoes` - Criar nova cotação
- `POST /v1/eden/fornecedores/cotacoes/get` - Buscar cotação por ID
- `POST /v1/eden/fornecedores/cotacoes/update` - Atualizar cotação
- `POST /v1/eden/fornecedores/cotacoes/delete` - Deletar cotação (soft delete)

### Frontend (React)

**Localização:** `app/src/modules/supplier/`

#### Componentes

1. **Supplier.jsx** - Página principal
   - Abas: Fornecedores e Cotações
   - Listagem com tabelas
   - Integração com API
   - Gerenciamento de estado

2. **NewSupplierModal.jsx** - Modal para criar fornecedor
   - Formulário com validação
   - Campos: nome, email, telefone, endereço, categoria
   - Integração com API

3. **EditSupplierModal.jsx** - Modal para editar fornecedor
   - Pré-preenchimento de dados
   - Checkbox para ativar/desativar
   - Integração com API

4. **NewQuotationModal.jsx** - Modal para criar cotação
   - Seleção de fornecedor
   - Cálculo automático de margem
   - Campos: descrição, quantidade, preço custo, preço venda

5. **EditQuotationModal.jsx** - Modal para editar cotação
   - Pré-preenchimento de dados
   - Cálculo automático de margem
   - Checkbox para ativar/desativar

#### Serviços

**api.js** - Integração com backend
```javascript
export const supplierApi = {
  list: () => api.get('/fornecedores'),
  create: (data) => api.post('/fornecedores', data),
  update: (data) => api.post('/fornecedores/update', data),
  remove: (id) => api.post('/fornecedores/delete', { id })
}

export const quotationApi = {
  list: () => api.get('/fornecedores/cotacoes'),
  create: (data) => api.post('/fornecedores/cotacoes', data),
  update: (data) => api.post('/fornecedores/cotacoes/update', data),
  remove: (id) => api.post('/fornecedores/cotacoes/delete', { id })
}
```

## 🗄️ Banco de Dados

### Tabelas

**fornecedores** - Já existente
```sql
CREATE TABLE fornecedores (
    id VARCHAR(36) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefone VARCHAR(50),
    cpf_cnpj VARCHAR(20),
    endereco VARCHAR(500),
    categoria VARCHAR(100),
    ativo TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**cotacoes** - Nova tabela
```sql
CREATE TABLE cotacoes (
    id VARCHAR(36) PRIMARY KEY,
    fornecedor_id VARCHAR(36) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    quantidade INT DEFAULT 1,
    preco_custo_cents INT DEFAULT 0,
    preco_venda_cents INT DEFAULT 0,
    ativo TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE CASCADE
);
```

### Migração

Arquivo: `migrations/20250120_add_cotacoes_table.sql`

Execute para criar a tabela de cotações:
```bash
mysql -u user -p database < migrations/20250120_add_cotacoes_table.sql
```

## 🚀 Como Usar

### Backend

1. **Iniciar o serviço:**
```bash
cd svc-fornecedores
python -m uvicorn main:app --reload --port 8007
```

2. **Testar endpoints:**
```bash
# Listar fornecedores
curl -H "Authorization: Bearer <token>" http://localhost:8007/v1/eden/fornecedores

# Criar fornecedor
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Flores Brasil","email":"contato@flores.com","telefone":"11987654321"}' \
  http://localhost:8007/v1/eden/fornecedores

# Listar cotações
curl -H "Authorization: Bearer <token>" http://localhost:8007/v1/eden/fornecedores/cotacoes
```

### Frontend

1. **Acessar a página:**
   - URL: `http://localhost:3000/supplier`
   - Requer autenticação

2. **Funcionalidades:**
   - **Aba Fornecedores:**
     - Listar fornecedores
     - Criar novo fornecedor
     - Editar fornecedor
     - Deletar fornecedor
     - Importar Excel

   - **Aba Cotações:**
     - Listar cotações
     - Criar nova cotação
     - Editar cotação
     - Deletar cotação
     - Visualizar margem de lucro

## 📊 Fluxo de Dados

```
Frontend (React)
    ↓
API Service (axios)
    ↓
Backend (FastAPI)
    ↓
Database (MySQL)
```

### Exemplo: Criar Fornecedor

1. Usuário clica em "Novo Fornecedor"
2. Modal `NewSupplierModal` abre
3. Usuário preenche formulário
4. Clica em "Cadastrar Fornecedor"
5. `supplierApi.create()` envia POST para `/v1/eden/fornecedores`
6. Backend valida e insere no banco
7. Resposta retorna ao frontend
8. Toast de sucesso é exibido
9. Lista é recarregada automaticamente

## 🔐 Autenticação

Todos os endpoints requerem token JWT no header:
```
Authorization: Bearer <token>
```

O token é obtido no login e armazenado em `localStorage`.

## 🎨 UI/UX

- **Design:** Tailwind CSS
- **Cores:** Verde primário (#2d5016), Verde claro (#4a7c2c)
- **Ícones:** Font Awesome
- **Responsividade:** Mobile-first
- **Modais:** Componentes reutilizáveis

## 📝 Validações

### Frontend
- Campos obrigatórios
- Formato de email
- Valores numéricos positivos
- Confirmação antes de deletar

### Backend
- Validação de modelo Pydantic
- Verificação de existência de recursos
- Soft delete (marca como inativo)

## 🔄 Sincronização de Dados

Usa sistema de eventos customizado:
```javascript
// Notificar mudança
notifyDataChanged('fornecedores')

// Listener
window.addEventListener('eden:data-changed', loadSuppliers)
```

## 📦 Dependências

### Backend
- FastAPI
- SQLAlchemy
- PyMySQL
- python-jose (JWT)
- pydantic

### Frontend
- React 18
- axios
- react-router-dom
- Tailwind CSS

## 🐛 Troubleshooting

### Erro: "Token inválido"
- Verifique se o token está no localStorage
- Faça login novamente

### Erro: "Não encontrado"
- Verifique se o ID do recurso existe
- Confirme se o recurso não foi deletado

### Erro: "Conexão recusada"
- Verifique se o backend está rodando
- Confirme a porta (8007 para svc-fornecedores)

## 📚 Referências

- [Arquitetura do Projeto](../knowledge/ARQUITETURA.md)
- [API Documentation](../postman/hubluiseden.postman_collection.json)
- [Schema do Banco](../data/schema.sql)

## ✅ Checklist de Implementação

- [x] Modelo Cotacao no backend
- [x] Endpoints CRUD para cotações
- [x] Componente Supplier.jsx
- [x] Modal NewSupplierModal
- [x] Modal EditSupplierModal
- [x] Modal NewQuotationModal
- [x] Modal EditQuotationModal
- [x] Integração com API
- [x] Tabela de cotações no banco
- [x] Migração SQL
- [x] Sincronização de dados
- [x] Validações
- [x] Tratamento de erros
- [x] UI/UX responsiva

## 🎯 Próximas Melhorias

- [ ] Filtros avançados
- [ ] Exportar para Excel
- [ ] Gráficos de margem
- [ ] Histórico de cotações
- [ ] Comparação de preços
- [ ] Notificações de preço
- [ ] Integração com catálogo
