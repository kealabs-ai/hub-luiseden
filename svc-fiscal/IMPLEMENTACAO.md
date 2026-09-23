# Guia de Implementação - Módulo Fiscal

## 🚀 Próximos Passos

### Fase 1: Setup Inicial (Hoje)

- [x] Estrutura de diretórios criada
- [x] Modelos de dados (SQLAlchemy)
- [x] Gerador de XML NF-e 4.00
- [x] Assinador digital (XMLDSig)
- [x] Cliente SOAP com mTLS
- [x] Endpoints FastAPI
- [x] Documentação

### Fase 2: Testes e Validação (Próxima)

#### 2.1 Obter Certificado de Teste
```bash
# Baixar certificado de teste em:
# https://www1.receita.fazenda.gov.br/

# Converter para PFX se necessário:
openssl pkcs12 -export -in cert.pem -inkey key.pem -out cert.pfx -name "Teste"
```

#### 2.2 Executar Localmente
```bash
cd svc-fiscal
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 2.3 Testar Endpoints
```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Criar configuração
curl -X POST http://localhost:8000/v1/eden/fiscal/configuracao \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d @config.json

# 3. Verificar status SEFAZ
curl http://localhost:8000/v1/eden/fiscal/status-sefaz \
  -H "Authorization: Bearer token"
```

### Fase 3: Integração com Frontend (Semana 2)

#### 3.1 Criar Página de Configuração Fiscal
```jsx
// app/src/modules/fiscal/pages/ConfiguracaoFiscal.jsx
- Formulário para CNPJ, IE, certificado
- Upload de certificado
- Teste de conexão SEFAZ
```

#### 3.2 Criar Página de Emissão de NF-e
```jsx
// app/src/modules/fiscal/pages/EmissaoNFe.jsx
- Seleção de cliente
- Adição de itens
- Pré-visualização
- Botão "Emitir e Autorizar"
```

#### 3.3 Criar Página de Consulta
```jsx
// app/src/modules/fiscal/pages/ConsultaNFe.jsx
- Busca por chave de acesso
- Filtros por status
- Visualização de protocolo
- Opção de cancelamento
```

### Fase 4: Melhorias e Recursos Avançados (Semana 3+)

#### 4.1 Suporte a A3 (Token)
```python
# svc-fiscal/a3_handler.py
- Integração com drivers de token
- Suporte a eToken, SmartCard
```

#### 4.2 Carta de Correção
```python
# svc-fiscal/carta_correcao.py
- Gerador de XML de evento
- Envio para SEFAZ
```

#### 4.3 Manifestação do Destinatário
```python
# svc-fiscal/manifestacao.py
- Confirmação de operação
- Desconhecimento da operação
- Operação não realizada
```

#### 4.4 Inutilização de Numeração
```python
# svc-fiscal/inutilizacao.py
- Gerador de XML de inutilização
- Envio para SEFAZ
```

#### 4.5 Backup e Recuperação
```python
# svc-fiscal/backup.py
- Backup automático de XMLs
- Recuperação de falhas
- Sincronização com SEFAZ
```

#### 4.6 Webhooks e Notificações
```python
# svc-fiscal/webhooks.py
- Notificação de autorização
- Notificação de rejeição
- Notificação de cancelamento
```

#### 4.7 Dashboard Fiscal
```jsx
// app/src/modules/fiscal/pages/Dashboard.jsx
- Resumo de NF-e emitidas
- Gráficos de status
- Alertas de rejeição
- Relatórios
```

## 📋 Checklist de Implementação

### Banco de Dados
- [ ] Executar migração SQL
- [ ] Verificar tabelas criadas
- [ ] Testar conexão

### Certificado Digital
- [ ] Obter certificado de teste
- [ ] Converter para PFX se necessário
- [ ] Armazenar em local seguro
- [ ] Testar carregamento

### Serviço Fiscal
- [ ] Instalar dependências
- [ ] Configurar variáveis de ambiente
- [ ] Testar health check
- [ ] Testar status SEFAZ

### Integração Frontend
- [ ] Criar páginas de configuração
- [ ] Criar páginas de emissão
- [ ] Criar páginas de consulta
- [ ] Integrar com API

### Testes
- [ ] Teste unitário de geração XML
- [ ] Teste de assinatura digital
- [ ] Teste de comunicação SOAP
- [ ] Teste de fluxo completo

## 🔧 Configuração de Ambiente

### .env
```env
# Banco de Dados
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=senha
DB_NAME=hub_luis_eden

# Autenticação
SECRET_KEY=sua-chave-secreta-muito-segura

# Fiscal
FISCAL_AMBIENTE=2  # 1=Produção, 2=Homologação
FISCAL_UF=MG
FISCAL_CODIGO_IBGE_UF=31

# Certificado
CERTIFICADO_PATH=/etc/ssl/certs/empresa.pfx
CERTIFICADO_SENHA=senha-do-certificado
```

## 🐳 Deployment

### Docker Compose
```bash
# Adicionar svc-fiscal ao docker-compose.yml
# Ver arquivo: docker-compose.snippet.yml

# Build
docker-compose build svc-fiscal

# Run
docker-compose up -d svc-fiscal

# Logs
docker-compose logs -f svc-fiscal
```

### Kubernetes (Futuro)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: svc-fiscal
spec:
  replicas: 2
  selector:
    matchLabels:
      app: svc-fiscal
  template:
    metadata:
      labels:
        app: svc-fiscal
    spec:
      containers:
      - name: svc-fiscal
        image: svc-fiscal:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          value: db-service
        volumeMounts:
        - name: certs
          mountPath: /etc/ssl/certs
          readOnly: true
      volumes:
      - name: certs
        secret:
          secretName: fiscal-certs
```

## 🧪 Testes

### Teste de Unidade
```python
# svc-fiscal/tests/test_nfe_generator.py
def test_generate_nfe():
    generator = NFeXMLGenerator(config)
    xml = generator.generate_nfe(numero=1, serie=1, cliente={}, itens=[])
    assert "NFe" in xml
    assert "infNFe" in xml

# svc-fiscal/tests/test_xml_signer.py
def test_sign_xml():
    signer = XMLSigner(cert_path, cert_password)
    signed = signer.sign_xml(xml_string)
    assert "Signature" in signed
```

### Teste de Integração
```python
# svc-fiscal/tests/test_sefaz_integration.py
def test_status_servico():
    client = SefazSOAPClient(cert_path, cert_password)
    resp = client.nfe_status_servico()
    assert resp["status"] == "sucesso"
    assert resp["cstat"] == "107"
```

### Teste E2E
```bash
# Fluxo completo: criar → assinar → autorizar → consultar
pytest tests/test_e2e.py -v
```

## 📊 Monitoramento

### Métricas
- Tempo de resposta SEFAZ
- Taxa de autorização
- Taxa de rejeição
- Número de NF-e emitidas

### Alertas
- SEFAZ indisponível
- Certificado próximo de expirar
- Taxa de rejeição > 5%
- Erro de comunicação

### Logs
```bash
# Ver logs do serviço
docker-compose logs -f svc-fiscal

# Filtrar por erro
docker-compose logs svc-fiscal | grep ERROR

# Exportar logs
docker-compose logs svc-fiscal > logs.txt
```

## 🔐 Segurança

### Certificado Digital
- [ ] Armazenar em local seguro
- [ ] Usar variáveis de ambiente para senha
- [ ] Rotacionar certificado antes de expirar
- [ ] Backup seguro

### Dados Sensíveis
- [ ] Não logar XMLs completos
- [ ] Mascarar CNPJ/CPF em logs
- [ ] Usar HTTPS em produção
- [ ] Validar entrada de dados

### Acesso
- [ ] Autenticação JWT obrigatória
- [ ] Autorização por empresa
- [ ] Auditoria de ações
- [ ] Rate limiting

## 📞 Suporte

### Documentação
- [Portal NF-e](https://www.nfe.fazenda.gov.br/)
- [Manual SEFAZ-MG](https://hnfe.fazenda.mg.gov.br/)
- [Especificação Técnica](https://www1.receita.fazenda.gov.br/manuais/)

### Contato
- Email: suporte@luiseden.com.br
- Telefone: (31) 3333-4444
- WhatsApp: (31) 99999-9999

## 📝 Notas

- Ambiente de homologação não tem validade jurídica
- Certificado de teste disponível gratuitamente
- Suporte SEFAZ-MG: https://hnfe.fazenda.mg.gov.br/
- Fórum de discussão: https://www.nfe.fazenda.gov.br/portal/
