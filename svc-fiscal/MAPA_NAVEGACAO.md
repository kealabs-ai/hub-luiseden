# 🗺️ Mapa de Navegação - Módulo Fiscal

## 📍 Você está aqui

```
svc-fiscal/
├── 📄 MAPA_NAVEGACAO.md ← VOCÊ ESTÁ AQUI
├── 📄 SUMARIO_FINAL.md
├── 📄 INICIO_RAPIDO.md
├── 📄 README.md
├── 📄 EXEMPLOS_USO.md
├── 📄 IMPLEMENTACAO.md
├── 📄 TROUBLESHOOTING.md
├── 📄 ENTREGA.md
├── 📄 INDICE.md
├── 📄 RESUMO_EXECUTIVO.md
├── 📄 CHECKLIST.md
├── 🐍 main.py
├── 🐍 database.py
├── 🐍 models.py
├── 🐍 nfe_generator.py
├── 🐍 xml_signer.py
├── 🐍 sefaz_client.py
├── 🧪 test_quick.py
├── 📋 requirements.txt
├── 🐳 Dockerfile
└── 🐳 docker-compose.snippet.yml
```

---

## 🎯 Escolha seu Caminho

### 👤 Sou Desenvolvedor - Quero Começar Rápido

1. **Leia:** [INICIO_RAPIDO.md](INICIO_RAPIDO.md) (5 min)
2. **Execute:** `pip install -r requirements.txt`
3. **Teste:** `python test_quick.py`
4. **Consulte:** [EXEMPLOS_USO.md](EXEMPLOS_USO.md)

### 👨‍💼 Sou Gerente - Quero Entender o Projeto

1. **Leia:** [RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md) (5 min)
2. **Veja:** [SUMARIO_FINAL.md](SUMARIO_FINAL.md) (5 min)
3. **Consulte:** [CHECKLIST.md](CHECKLIST.md) (5 min)

### 🔧 Sou DevOps - Quero Fazer Deploy

1. **Leia:** [README.md](README.md) - Seção Docker
2. **Use:** `docker-compose.snippet.yml`
3. **Configure:** Variáveis de ambiente
4. **Deploy:** `docker-compose up -d svc-fiscal`

### 🐛 Tenho um Problema - Preciso de Ajuda

1. **Consulte:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **Procure:** Seu problema na seção "Problemas Comuns"
3. **Siga:** As soluções propostas
4. **Se não resolver:** Verifique os logs

### 📚 Quero Aprender Tudo

1. **Comece:** [README.md](README.md) (10 min)
2. **Entenda:** [INDICE.md](INDICE.md) (10 min)
3. **Implemente:** [IMPLEMENTACAO.md](IMPLEMENTACAO.md) (30 min)
4. **Pratique:** [EXEMPLOS_USO.md](EXEMPLOS_USO.md) (20 min)

---

## 📄 Guia de Documentos

### 🚀 Para Começar

| Documento | Tempo | Para Quem | O que Contém |
|-----------|-------|-----------|-------------|
| [INICIO_RAPIDO.md](INICIO_RAPIDO.md) | 5 min | Desenvolvedores | Passos para começar em 5 minutos |
| [RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md) | 5 min | Gerentes | Visão geral do projeto |
| [SUMARIO_FINAL.md](SUMARIO_FINAL.md) | 5 min | Todos | Resumo visual de tudo |

### 📖 Para Entender

| Documento | Tempo | Para Quem | O que Contém |
|-----------|-------|-----------|-------------|
| [README.md](README.md) | 10 min | Todos | Documentação completa |
| [INDICE.md](INDICE.md) | 10 min | Desenvolvedores | Índice de arquivos |
| [ENTREGA.md](ENTREGA.md) | 10 min | Gerentes | O que foi entregue |

### 💻 Para Usar

| Documento | Tempo | Para Quem | O que Contém |
|-----------|-------|-----------|-------------|
| [EXEMPLOS_USO.md](EXEMPLOS_USO.md) | 20 min | Desenvolvedores | 9 exemplos práticos |
| [IMPLEMENTACAO.md](IMPLEMENTACAO.md) | 30 min | Desenvolvedores | Guia de implementação |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 15 min | Todos | FAQ e problemas comuns |

### ✅ Para Verificar

| Documento | Tempo | Para Quem | O que Contém |
|-----------|-------|-----------|-------------|
| [CHECKLIST.md](CHECKLIST.md) | 10 min | Gerentes | Checklist de verificação |

---

## 🔗 Navegação Rápida

### Endpoints
- [POST /v1/eden/fiscal/configuracao](README.md#post-v1edenfiscalconfiguração)
- [GET /v1/eden/fiscal/configuracao/{empresa_id}](README.md#get-v1edenfiscalconfiguracaoempresa_id)
- [POST /v1/eden/fiscal/nfe](README.md#post-v1edenfiscalnfe)
- [GET /v1/eden/fiscal/nfe/{nfe_id}](README.md#get-v1edenfiscalnfenfe_id)
- [POST /v1/eden/fiscal/nfe/assinar](README.md#post-v1edenfiscalnfeassinador)
- [POST /v1/eden/fiscal/nfe/autorizar](README.md#post-v1edenfiscalnfeautorizar)
- [POST /v1/eden/fiscal/nfe/consulta-protocolo](README.md#post-v1edenfiscalnfeconsulta-protocolo)
- [POST /v1/eden/fiscal/nfe/cancelar](README.md#post-v1edenfiscalnfecancelar)
- [GET /v1/eden/fiscal/status-sefaz](README.md#get-v1edenfiscalstatus-sefaz)

### Exemplos
- [Configurar Empresa](EXEMPLOS_USO.md#1-configurar-empresa)
- [Criar NF-e](EXEMPLOS_USO.md#4-criar-nf-e-rascunho)
- [Autorizar NF-e](EXEMPLOS_USO.md#7-autorizar-nf-e-enviar-para-sefaz)
- [Consultar Protocolo](EXEMPLOS_USO.md#8-consultar-protocolo)
- [Fluxo Completo](EXEMPLOS_USO.md#fluxo-completo-em-python)

### Problemas
- [Erro ao Carregar Certificado](TROUBLESHOOTING.md#1-erro-ao-carregar-certificado)
- [SEFAZ Indisponível](TROUBLESHOOTING.md#2-sefaz-indisponível)
- [Erro de Validação XML](TROUBLESHOOTING.md#3-erro-de-validação-xml)
- [Erro de Assinatura Digital](TROUBLESHOOTING.md#4-erro-de-assinatura-digital)
- [Timeout na Comunicação](TROUBLESHOOTING.md#5-timeout-na-comunicação)

---

## 🎓 Roteiros de Aprendizado

### Roteiro 1: Iniciante (1 hora)
```
1. INICIO_RAPIDO.md (5 min)
   ↓
2. Instalar e executar (10 min)
   ↓
3. EXEMPLOS_USO.md - Exemplo 1 (10 min)
   ↓
4. Testar com curl (15 min)
   ↓
5. Ler README.md (20 min)
```

### Roteiro 2: Intermediário (2 horas)
```
1. README.md (15 min)
   ↓
2. EXEMPLOS_USO.md - Todos os exemplos (30 min)
   ↓
3. Testar script test_quick.py (10 min)
   ↓
4. IMPLEMENTACAO.md (30 min)
   ↓
5. Criar primeira NF-e (35 min)
```

### Roteiro 3: Avançado (4 horas)
```
1. Todos os documentos (1 hora)
   ↓
2. Analisar código Python (1 hora)
   ↓
3. Integrar com frontend (1 hora)
   ↓
4. Testar fluxo completo (1 hora)
```

---

## 🔍 Busca Rápida

### Procurando por...

**"Como começar?"**
→ [INICIO_RAPIDO.md](INICIO_RAPIDO.md)

**"Como usar os endpoints?"**
→ [EXEMPLOS_USO.md](EXEMPLOS_USO.md)

**"Como fazer deploy?"**
→ [README.md](README.md#-docker) ou [IMPLEMENTACAO.md](IMPLEMENTACAO.md#-docker)

**"Tenho um erro, o que fazer?"**
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**"Qual é o status do projeto?"**
→ [ENTREGA.md](ENTREGA.md) ou [CHECKLIST.md](CHECKLIST.md)

**"Quero entender a arquitetura"**
→ [README.md](README.md#-arquitetura) ou [INDICE.md](INDICE.md)

**"Quero ver exemplos"**
→ [EXEMPLOS_USO.md](EXEMPLOS_USO.md)

**"Quero implementar novos recursos"**
→ [IMPLEMENTACAO.md](IMPLEMENTACAO.md)

---

## 📞 Fluxo de Suporte

```
Tenho uma dúvida
    ↓
Procuro em TROUBLESHOOTING.md
    ↓
Encontrei? → Problema resolvido ✅
    ↓
Não encontrei?
    ↓
Procuro em README.md
    ↓
Encontrei? → Problema resolvido ✅
    ↓
Não encontrei?
    ↓
Procuro em EXEMPLOS_USO.md
    ↓
Encontrei? → Problema resolvido ✅
    ↓
Não encontrei?
    ↓
Procuro em IMPLEMENTACAO.md
    ↓
Encontrei? → Problema resolvido ✅
    ↓
Não encontrei?
    ↓
Verifique os logs e o código
```

---

## 🎯 Próximos Passos

### Imediato (Hoje)
1. Ler [INICIO_RAPIDO.md](INICIO_RAPIDO.md)
2. Instalar dependências
3. Executar serviço
4. Testar health check

### Curto Prazo (Esta Semana)
1. Obter certificado de teste
2. Criar configuração fiscal
3. Criar primeira NF-e
4. Autorizar NF-e

### Médio Prazo (Próximas 2 Semanas)
1. Integrar com frontend
2. Criar páginas de configuração
3. Criar páginas de emissão
4. Criar páginas de consulta

### Longo Prazo (Próximo Mês)
1. Implementar recursos avançados
2. Fazer deploy em produção
3. Monitorar e otimizar
4. Adicionar novos recursos

---

## 📊 Estrutura de Documentação

```
MAPA_NAVEGACAO.md (Este arquivo)
    ├── INICIO_RAPIDO.md (5 min)
    ├── RESUMO_EXECUTIVO.md (5 min)
    ├── SUMARIO_FINAL.md (5 min)
    ├── README.md (10 min)
    ├── EXEMPLOS_USO.md (20 min)
    ├── IMPLEMENTACAO.md (30 min)
    ├── TROUBLESHOOTING.md (15 min)
    ├── ENTREGA.md (10 min)
    ├── INDICE.md (10 min)
    └── CHECKLIST.md (10 min)
```

---

## ✅ Checklist de Leitura

- [ ] Li INICIO_RAPIDO.md
- [ ] Li README.md
- [ ] Li EXEMPLOS_USO.md
- [ ] Testei os endpoints
- [ ] Li TROUBLESHOOTING.md
- [ ] Li IMPLEMENTACAO.md
- [ ] Entendi a arquitetura
- [ ] Estou pronto para usar

---

## 🎉 Bem-vindo!

Você está no lugar certo! Este mapa de navegação vai ajudá-lo a encontrar o que precisa.

**Comece por:** [INICIO_RAPIDO.md](INICIO_RAPIDO.md)

---

**Módulo Fiscal SEFAZ-MG - Versão 1.0.0**
**Mapa de Navegação - Última atualização: 20 de Janeiro de 2024**
