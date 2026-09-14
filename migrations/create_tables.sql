CREATE TABLE IF NOT EXISTS usuarios (
    id         VARCHAR(36)  PRIMARY KEY,
    nome       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    role       ENUM('admin','operador','cliente') NOT NULL DEFAULT 'operador',
    ativo      BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS plantas (
    id          VARCHAR(36)  PRIMARY KEY,
    nome        VARCHAR(255) NOT NULL,
    categoria   VARCHAR(100),
    descricao   TEXT,
    preco_cents INT          NOT NULL DEFAULT 0,
    estoque     INT          NOT NULL DEFAULT 0,
    imagem_url  VARCHAR(500),
    ativo       BOOLEAN DEFAULT TRUE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendas (
    id           VARCHAR(36)  PRIMARY KEY,
    usuario_id   VARCHAR(36)  NOT NULL,
    cliente_nome VARCHAR(255),
    total_cents  INT          NOT NULL DEFAULT 0,
    status       VARCHAR(50)  DEFAULT 'concluida',
    observacoes  TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS itens_venda (
    id          VARCHAR(36) PRIMARY KEY,
    venda_id    VARCHAR(36) NOT NULL,
    planta_id   VARCHAR(36) NOT NULL,
    quantidade  INT         NOT NULL DEFAULT 1,
    preco_cents INT         NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transacoes (
    id          VARCHAR(36)  PRIMARY KEY,
    usuario_id  VARCHAR(36)  NOT NULL,
    tipo        VARCHAR(20)  NOT NULL,
    categoria   VARCHAR(100),
    descricao   VARCHAR(500),
    valor_cents INT          NOT NULL,
    data        VARCHAR(10)  NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orcamentos (
    id           VARCHAR(36)  PRIMARY KEY,
    usuario_id   VARCHAR(36)  NOT NULL,
    cliente_nome VARCHAR(255),
    descricao    TEXT,
    total_cents  INT          NOT NULL DEFAULT 0,
    status       VARCHAR(50)  DEFAULT 'pendente',
    validade     VARCHAR(10),
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS itens_orcamento (
    id           VARCHAR(36)  PRIMARY KEY,
    orcamento_id VARCHAR(36)  NOT NULL,
    descricao    VARCHAR(500) NOT NULL,
    quantidade   INT          NOT NULL DEFAULT 1,
    preco_cents  INT          NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS manutencoes (
    id            VARCHAR(36)  PRIMARY KEY,
    usuario_id    VARCHAR(36)  NOT NULL,
    planta_id     VARCHAR(36),
    titulo        VARCHAR(255) NOT NULL,
    descricao     TEXT,
    data_agendada VARCHAR(10)  NOT NULL,
    status        VARCHAR(50)  DEFAULT 'agendada',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fornecedores (
    id         VARCHAR(36)  PRIMARY KEY,
    nome       VARCHAR(255) NOT NULL,
    email      VARCHAR(255),
    telefone   VARCHAR(50),
    cpf_cnpj   VARCHAR(20),
    endereco   VARCHAR(500),
    categoria  VARCHAR(100),
    ativo      BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
