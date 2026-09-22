# ✅ Checklist de Deployment - Fornecedores

## 📋 Pré-Deployment

### Verificações Iniciais
- [ ] Todos os arquivos foram criados/modificados
- [ ] Código foi revisado
- [ ] Testes manuais foram executados
- [ ] Documentação foi lida
- [ ] Banco de dados está acessível

### Ambiente
- [ ] Python 3.12+ instalado
- [ ] Node.js 18+ instalado
- [ ] MySQL 8.0+ rodando
- [ ] Variáveis de ambiente configuradas

---

## 🗄️ Banco de Dados

### Passo 1: Executar Migração
```bash
# Conectar ao MySQL
mysql -u seu_usuario -p seu_banco

# Executar migração
source migrations/20250120_add_cotacoes_table.sql;

# Verificar tabela
SHOW TABLES LIKE 'cotacoes';
DESC cotacoes;
```

**Checklist:**
- [ ] Migração executada sem erros
- [ ] Tabela `cotacoes` criada
- [ ] Foreign key configurada
- [ ] Índices criados

### Passo 2: Verificar Dados
```sql
-- Verificar fornecedores existentes
SELECT COUNT(*) FROM fornecedores;

-- Verificar cotações (deve estar vazia)
SELECT COUNT(*) FROM cotacoes;

-- Verificar estrutura
SHOW CREATE TABLE cotacoes\G
```

**Checklist:**
- [ ] Fornecedores existentes intactos
- [ ] Tabela cotacoes vazia
- [ ] Estrutura correta

---

## 🔧 Backend

### Passo 1: Verificar Código
```bash
cd svc-fornecedores

# Verificar sintaxe Python
python -m py_compile main.py

# Verificar imports
python -c "from main import app, Cotacao, CotacaoIn"
```

**Checklist:**
- [ ] Sem erros de sintaxe
- [ ] Imports funcionam
- [ ] Modelos carregam

### Passo 2: Iniciar Serviço
```bash
# Modo desenvolvimento
python -m uvicorn main:app --reload --port 8007

# Modo produção
python -m uvicorn main:app --host 0.0.0.0 --port 8007
```

**Checklist:**
- [ ] Serviço inicia sem erros
- [ ] Porta 8007 está disponível
- [ ] Banco de dados conecta
- [ ] Tabelas são criadas automaticamente

### Passo 3: Testar Health Check
```bash
curl http://localhost:8007/health
```

**Resposta esperada:**
```json
{"status": "ok", "service": "svc-fornecedores"}
```

**Checklist:**
- [ ] Health check retorna 200
- [ ] Serviço está respondendo

### Passo 4: Testar Endpoints
```bash
# Obter token (substitua com seu token)
TOKEN="seu_token_jwt"

# Listar fornecedores
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8007/v1/eden/fornecedores

# Listar cotações
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8007/v1/eden/fornecedores/cotacoes
```

**Checklist:**
- [ ] GET /fornecedores retorna 200
- [ ] GET /fornecedores/cotacoes retorna 200
- [ ] Dados são retornados em JSON

---

## 🎨 Frontend

### Passo 1: Verificar Código
```bash
cd app

# Verificar sintaxe JavaScript
npm run build

# Verificar imports
grep -r "EditSupplierModal\|EditQuotationModal" src/
```

**Checklist:**
- [ ] Build sem erros
- [ ] Componentes importados corretamente
- [ ] Sem warnings críticos

### Passo 2: Iniciar Aplicação
```bash
npm start
```

**Checklist:**
- [ ] Aplicação inicia em http://localhost:3000
- [ ] Sem erros no console
- [ ] Página carrega

### Passo 3: Testar Página
1. Acesse `http://localhost:3000/supplier`
2. Verifique se as 2 abas aparecem
3. Clique em "Novo Fornecedor"
4. Verifique se o modal abre

**Checklist:**
- [ ] Página carrega
- [ ] Abas aparecem
- [ ] Modais abrem
- [ ] Sem erros no console

### Passo 4: Testar Funcionalidades
```
Teste 1: Criar Fornecedor
- [ ] Clique em "Novo Fornecedor"
- [ ] Preencha os campos
- [ ] Clique em "Cadastrar"
- [ ] Verifique se aparece na tabela
- [ ] Verifique se o toast de sucesso aparece

Teste 2: Editar Fornecedor
- [ ] Clique no ícone de editar
- [ ] Modifique um campo
- [ ] Clique em "Salvar"
- [ ] Verifique se a mudança aparece

Teste 3: Criar Cotação
- [ ] Clique na aba "Cotações"
- [ ] Clique em "Nova Cotação"
- [ ] Selecione um fornecedor
- [ ] Preencha os campos
- [ ] Verifique se a margem é calculada
- [ ] Clique em "Cadastrar"
- [ ] Verifique se aparece na tabela

Teste 4: Editar Cotação
- [ ] Clique no ícone de editar
- [ ] Modifique um campo
- [ ] Verifique se a margem é recalculada
- [ ] Clique em "Salvar"
- [ ] Verifique se a mudança aparece

Teste 5: Deletar
- [ ] Clique no ícone de deletar
- [ ] Confirme a exclusão
- [ ] Verifique se desaparece da tabela
```

**Checklist:**
- [ ] Todos os testes passam
- [ ] Sem erros no console
- [ ] Dados sincronizam corretamente

---

## 🔐 Segurança

### Verificações
- [ ] Token JWT é obrigatório
- [ ] Validação de entrada funciona
- [ ] Soft delete está ativo
- [ ] Foreign keys estão configuradas
- [ ] Sem dados sensíveis em logs

### Teste de Segurança
```bash
# Tentar acessar sem token (deve retornar 401)
curl http://localhost:8007/v1/eden/fornecedores

# Tentar com token inválido (deve retornar 401)
curl -H "Authorization: Bearer invalid_token" \
  http://localhost:8007/v1/eden/fornecedores
```

**Checklist:**
- [ ] Sem token retorna 401
- [ ] Token inválido retorna 401
- [ ] Apenas usuários autenticados acessam

---

## 📊 Testes de Integração

### Teste 1: Fluxo Completo
```
1. Criar fornecedor via frontend
2. Verificar se aparece no banco
3. Criar cotação para esse fornecedor
4. Verificar se a cotação aparece no banco
5. Editar cotação
6. Verificar se a mudança aparece no banco
7. Deletar cotação
8. Verificar se está marcada como inativa
9. Deletar fornecedor
10. Verificar se está marcado como inativo
```

**Checklist:**
- [ ] Todos os passos funcionam
- [ ] Dados sincronizam corretamente
- [ ] Sem erros

### Teste 2: Validações
```
1. Tentar criar fornecedor sem nome (deve falhar)
2. Tentar criar fornecedor com email inválido (deve falhar)
3. Tentar criar cotação sem fornecedor (deve falhar)
4. Tentar criar cotação com preço negativo (deve falhar)
5. Tentar criar cotação com quantidade 0 (deve falhar)
```

**Checklist:**
- [ ] Validações funcionam
- [ ] Mensagens de erro aparecem
- [ ] Dados não são salvos

### Teste 3: Performance
```
1. Criar 100 fornecedores
2. Criar 500 cotações
3. Listar fornecedores (deve ser rápido)
4. Listar cotações (deve ser rápido)
5. Editar cotação (deve ser rápido)
```

**Checklist:**
- [ ] Listagem < 1 segundo
- [ ] Edição < 500ms
- [ ] Sem travamentos

---

## 📱 Responsividade

### Desktop (1920x1080)
- [ ] Tabelas aparecem corretamente
- [ ] Modais estão centralizados
- [ ] Sem overflow horizontal

### Tablet (768x1024)
- [ ] Tabelas são responsivas
- [ ] Modais se adaptam
- [ ] Botões são clicáveis

### Mobile (375x667)
- [ ] Tabelas scrollam horizontalmente
- [ ] Modais ocupam 90% da tela
- [ ] Botões são grandes o suficiente

---

## 🚀 Deployment em Produção

### Passo 1: Preparar Ambiente
```bash
# Backend
cd svc-fornecedores
pip install -r requirements.txt

# Frontend
cd app
npm install
npm run build
```

**Checklist:**
- [ ] Dependências instaladas
- [ ] Build gerado sem erros

### Passo 2: Configurar Variáveis
```bash
# .env
luis_ed_DB_HOST=seu_host
luis_ed_DB_PORT=3306
luis_ed_DB_NAME=seu_banco
luis_ed_DB_USER=seu_usuario
luis_ed_DB_PASSWORD=sua_senha
SECRET_KEY=sua_chave_secreta
```

**Checklist:**
- [ ] Todas as variáveis configuradas
- [ ] Sem valores padrão

### Passo 3: Iniciar Serviços
```bash
# Backend (via Docker ou systemd)
docker run -d -p 8007:8007 svc-fornecedores

# Frontend (via Nginx ou similar)
nginx -c /etc/nginx/nginx.conf
```

**Checklist:**
- [ ] Backend rodando
- [ ] Frontend acessível
- [ ] Logs sem erros

### Passo 4: Verificar Saúde
```bash
# Health check backend
curl https://seu_dominio/v1/eden/health

# Acessar frontend
https://seu_dominio/supplier
```

**Checklist:**
- [ ] Backend respondendo
- [ ] Frontend carregando
- [ ] SSL/TLS configurado

---

## 📚 Documentação

### Verificar Documentação
- [ ] SUPPLIER_IMPLEMENTATION.md existe
- [ ] SUPPLIER_QUICK_START.md existe
- [ ] API_EXAMPLES.md existe
- [ ] IMPLEMENTATION_SUMMARY.md existe
- [ ] FILE_STRUCTURE.md existe

### Verificar Conteúdo
- [ ] Instruções de setup estão claras
- [ ] Exemplos de API funcionam
- [ ] Troubleshooting está completo
- [ ] Próximas melhorias estão listadas

**Checklist:**
- [ ] Documentação completa
- [ ] Exemplos testados
- [ ] Sem erros de digitação

---

## 🎯 Pós-Deployment

### Monitoramento
- [ ] Logs estão sendo registrados
- [ ] Erros estão sendo capturados
- [ ] Performance está sendo monitorada
- [ ] Alertas estão configurados

### Backup
- [ ] Banco de dados está sendo feito backup
- [ ] Código está em controle de versão
- [ ] Documentação está versionada

### Comunicação
- [ ] Equipe foi notificada
- [ ] Documentação foi compartilhada
- [ ] Suporte foi treinado

---

## ✅ Checklist Final

### Antes de Ir para Produção
- [ ] Todos os testes passam
- [ ] Documentação está completa
- [ ] Código foi revisado
- [ ] Segurança foi verificada
- [ ] Performance está OK
- [ ] Backup está configurado
- [ ] Monitoramento está ativo
- [ ] Equipe foi notificada

### Após Deployment
- [ ] Usuários conseguem acessar
- [ ] Funcionalidades funcionam
- [ ] Sem erros nos logs
- [ ] Performance está OK
- [ ] Suporte está disponível

---

## 📞 Contato de Suporte

Em caso de problemas:
1. Consulte `SUPPLIER_IMPLEMENTATION.md`
2. Verifique os logs
3. Teste via Postman
4. Contate o desenvolvedor

---

## 📝 Notas

- Data de Deployment: _______________
- Versão: 1.0.0
- Ambiente: [ ] Desenvolvimento [ ] Staging [ ] Produção
- Responsável: _______________
- Observações: _______________

---

**Status:** ✅ Pronto para Deployment
**Data:** 2025-01-20
**Versão:** 1.0.0
