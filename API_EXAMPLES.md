# API Examples - Fornecedores e Cotações

## Base URL
```
http://localhost:8007/v1/eden
```

## Headers Obrigatórios
```
Authorization: Bearer <seu_token_jwt>
Content-Type: application/json
```

---

## 📦 FORNECEDORES

### 1. Listar Fornecedores
```http
GET /fornecedores
```

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nome": "Flores Brasil",
    "email": "contato@flores.com",
    "telefone": "(11) 98765-4321",
    "cpfCnpj": "12.345.678/0001-90",
    "endereco": "Rua das Flores, 123, São Paulo, SP",
    "categoria": "Flores",
    "ativo": true,
    "createdAt": "2025-01-20T10:30:00",
    "updatedAt": "2025-01-20T10:30:00"
  }
]
```

---

### 2. Criar Fornecedor
```http
POST /fornecedores
```

**Request Body:**
```json
{
  "nome": "Plantas Premium",
  "email": "vendas@plantaspremium.com",
  "telefone": "(11) 3456-7890",
  "cpfCnpj": "98.765.432/0001-12",
  "endereco": "Av. Paulista, 1000, São Paulo, SP",
  "categoria": "Plantas"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "nome": "Plantas Premium",
  "email": "vendas@plantaspremium.com",
  "telefone": "(11) 3456-7890",
  "cpfCnpj": "98.765.432/0001-12",
  "endereco": "Av. Paulista, 1000, São Paulo, SP",
  "categoria": "Plantas",
  "ativo": true,
  "createdAt": "2025-01-20T11:00:00",
  "updatedAt": "2025-01-20T11:00:00"
}
```

---

### 3. Buscar Fornecedor por ID
```http
POST /fornecedores/get
```

**Request Body:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "Flores Brasil",
  "email": "contato@flores.com",
  "telefone": "(11) 98765-4321",
  "cpfCnpj": "12.345.678/0001-90",
  "endereco": "Rua das Flores, 123, São Paulo, SP",
  "categoria": "Flores",
  "ativo": true,
  "createdAt": "2025-01-20T10:30:00",
  "updatedAt": "2025-01-20T10:30:00"
}
```

---

### 4. Atualizar Fornecedor
```http
POST /fornecedores/update
```

**Request Body:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "Flores Brasil Ltda",
  "email": "novo@flores.com",
  "telefone": "(11) 99999-9999",
  "categoria": "Flores Premium",
  "ativo": true
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "Flores Brasil Ltda",
  "email": "novo@flores.com",
  "telefone": "(11) 99999-9999",
  "cpfCnpj": "12.345.678/0001-90",
  "endereco": "Rua das Flores, 123, São Paulo, SP",
  "categoria": "Flores Premium",
  "ativo": true,
  "createdAt": "2025-01-20T10:30:00",
  "updatedAt": "2025-01-20T11:15:00"
}
```

---

### 5. Deletar Fornecedor
```http
POST /fornecedores/delete
```

**Request Body:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200):**
```json
{
  "ok": true
}
```

---

## 💰 COTAÇÕES

### 1. Listar Cotações
```http
GET /fornecedores/cotacoes
```

**Response (200):**
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "fornecedorId": "550e8400-e29b-41d4-a716-446655440000",
    "descricao": "Rosa Vermelha Premium",
    "quantidade": 100,
    "precoCustoCents": 2500,
    "precoVendaCents": 4500,
    "ativo": true,
    "createdAt": "2025-01-20T10:45:00",
    "updatedAt": "2025-01-20T10:45:00"
  }
]
```

---

### 2. Criar Cotação
```http
POST /fornecedores/cotacoes
```

**Request Body:**
```json
{
  "fornecedorId": "550e8400-e29b-41d4-a716-446655440000",
  "descricao": "Orquídea Branca Importada",
  "quantidade": 50,
  "precoCustoCents": 4000,
  "precoVendaCents": 6500
}
```

**Response (201):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "fornecedorId": "550e8400-e29b-41d4-a716-446655440000",
  "descricao": "Orquídea Branca Importada",
  "quantidade": 50,
  "precoCustoCents": 4000,
  "precoVendaCents": 6500,
  "ativo": true,
  "createdAt": "2025-01-20T11:00:00",
  "updatedAt": "2025-01-20T11:00:00"
}
```

**Cálculo de Margem:**
- Custo: R$ 40,00
- Venda: R$ 65,00
- Margem: ((65 - 40) / 40) × 100 = 62,5%

---

### 3. Buscar Cotação por ID
```http
POST /fornecedores/cotacoes/get
```

**Request Body:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "fornecedorId": "550e8400-e29b-41d4-a716-446655440000",
  "descricao": "Rosa Vermelha Premium",
  "quantidade": 100,
  "precoCustoCents": 2500,
  "precoVendaCents": 4500,
  "ativo": true,
  "createdAt": "2025-01-20T10:45:00",
  "updatedAt": "2025-01-20T10:45:00"
}
```

---

### 4. Atualizar Cotação
```http
POST /fornecedores/cotacoes/update
```

**Request Body:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "descricao": "Rosa Vermelha Premium - Importada",
  "quantidade": 150,
  "precoCustoCents": 2300,
  "precoVendaCents": 4200,
  "ativo": true
}
```

**Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "fornecedorId": "550e8400-e29b-41d4-a716-446655440000",
  "descricao": "Rosa Vermelha Premium - Importada",
  "quantidade": 150,
  "precoCustoCents": 2300,
  "precoVendaCents": 4200,
  "ativo": true,
  "createdAt": "2025-01-20T10:45:00",
  "updatedAt": "2025-01-20T11:30:00"
}
```

---

### 5. Deletar Cotação
```http
POST /fornecedores/cotacoes/delete
```

**Request Body:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200):**
```json
{
  "ok": true
}
```

---

## 🔍 Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 400 | Requisição inválida |
| 401 | Token inválido ou ausente |
| 404 | Recurso não encontrado |
| 500 | Erro interno do servidor |

---

## 📝 Notas Importantes

1. **Preços em centavos:** Sempre envie preços multiplicados por 100
   - R$ 25,00 = 2500 centavos

2. **Soft Delete:** Deletar marca como inativo, não remove do banco

3. **Timestamps:** Sempre em ISO 8601 (UTC)

4. **IDs:** UUIDs gerados automaticamente

5. **Validações:**
   - Nome obrigatório
   - Email deve ser válido
   - Preços devem ser positivos
   - Quantidade deve ser >= 1

---

## 🧪 Teste Rápido com cURL

```bash
# 1. Listar fornecedores
curl -H "Authorization: Bearer <token>" \
  http://localhost:8007/v1/eden/fornecedores

# 2. Criar fornecedor
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Teste","email":"teste@test.com"}' \
  http://localhost:8007/v1/eden/fornecedores

# 3. Listar cotações
curl -H "Authorization: Bearer <token>" \
  http://localhost:8007/v1/eden/fornecedores/cotacoes
```

---

**Última atualização:** 2025-01-20
**Versão da API:** 1.0.0
