-- Tabela de Configuração Fiscal
CREATE TABLE IF NOT EXISTS configuracoes_fiscais (
    id VARCHAR(36) PRIMARY KEY,
    empresa_id VARCHAR(36) NOT NULL UNIQUE,
    cnpj VARCHAR(14) NOT NULL,
    razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255),
    inscricao_estadual VARCHAR(20),
    ambiente INT DEFAULT 2,
    uf VARCHAR(2) DEFAULT 'MG',
    codigo_ibge_uf INT DEFAULT 31,
    certificado_path VARCHAR(500) NOT NULL,
    certificado_senha VARCHAR(255),
    serie_nfe INT DEFAULT 1,
    proximo_numero INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_empresa_id (empresa_id)
);

-- Tabela de Notas Fiscais
CREATE TABLE IF NOT EXISTS notas_fiscais (
    id VARCHAR(36) PRIMARY KEY,
    chave_nfe VARCHAR(44) UNIQUE,
    numero INT NOT NULL,
    serie INT DEFAULT 1,
    cliente_id VARCHAR(36) NOT NULL,
    data_emissao DATETIME DEFAULT CURRENT_TIMESTAMP,
    valor_total_cents INT NOT NULL,
    status VARCHAR(50) DEFAULT 'rascunho',
    xml_assinado LONGTEXT,
    protocolo VARCHAR(15),
    numero_recibo VARCHAR(20),
    data_autorizacao DATETIME,
    motivo_rejeicao LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cliente_id (cliente_id),
    INDEX idx_chave_nfe (chave_nfe),
    INDEX idx_status (status),
    INDEX idx_numero (numero, serie)
);

-- Tabela de Itens da Nota Fiscal
CREATE TABLE IF NOT EXISTS itens_nota_fiscal (
    id VARCHAR(36) PRIMARY KEY,
    nota_fiscal_id VARCHAR(36) NOT NULL,
    produto_id VARCHAR(36) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    quantidade DECIMAL(10, 2) NOT NULL,
    valor_unitario_cents INT NOT NULL,
    valor_total_cents INT NOT NULL,
    ncm VARCHAR(8),
    cfop VARCHAR(4),
    FOREIGN KEY (nota_fiscal_id) REFERENCES notas_fiscais(id) ON DELETE CASCADE,
    INDEX idx_nota_fiscal_id (nota_fiscal_id),
    INDEX idx_produto_id (produto_id)
);

-- Tabela de Eventos Fiscais (Cancelamento, Carta de Correção, etc)
CREATE TABLE IF NOT EXISTS eventos_fiscais (
    id VARCHAR(36) PRIMARY KEY,
    nota_fiscal_id VARCHAR(36) NOT NULL,
    tipo_evento VARCHAR(50) NOT NULL,
    numero_sequencial INT DEFAULT 1,
    xml_evento LONGTEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pendente',
    protocolo_evento VARCHAR(15),
    motivo_rejeicao LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (nota_fiscal_id) REFERENCES notas_fiscais(id) ON DELETE CASCADE,
    INDEX idx_nota_fiscal_id (nota_fiscal_id),
    INDEX idx_tipo_evento (tipo_evento),
    INDEX idx_status (status),
    UNIQUE KEY uk_evento (nota_fiscal_id, tipo_evento, numero_sequencial)
);

-- Tabela de Log de Comunicação SEFAZ
CREATE TABLE IF NOT EXISTS logs_sefaz (
    id VARCHAR(36) PRIMARY KEY,
    nota_fiscal_id VARCHAR(36),
    tipo_requisicao VARCHAR(50) NOT NULL,
    xml_enviado LONGTEXT,
    xml_resposta LONGTEXT,
    cstat VARCHAR(3),
    xmotivo TEXT,
    tempo_resposta_ms INT,
    status_http INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nota_fiscal_id) REFERENCES notas_fiscais(id) ON DELETE SET NULL,
    INDEX idx_nota_fiscal_id (nota_fiscal_id),
    INDEX idx_tipo_requisicao (tipo_requisicao),
    INDEX idx_created_at (created_at)
);

-- Tabela de Auditoria
CREATE TABLE IF NOT EXISTS auditoria_fiscal (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(36) NOT NULL,
    nota_fiscal_id VARCHAR(36),
    acao VARCHAR(100) NOT NULL,
    detalhes LONGTEXT,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nota_fiscal_id) REFERENCES notas_fiscais(id) ON DELETE SET NULL,
    INDEX idx_usuario_id (usuario_id),
    INDEX idx_nota_fiscal_id (nota_fiscal_id),
    INDEX idx_acao (acao),
    INDEX idx_created_at (created_at)
);
