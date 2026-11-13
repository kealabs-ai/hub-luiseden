-- Migration: Add Quotations Table
-- Date: 2025-01-20
-- Description: Create cotacoes table for supplier quotations

CREATE TABLE IF NOT EXISTS cotacoes (
    id              VARCHAR(36)  NOT NULL,
    fornecedor_id   VARCHAR(36)  NOT NULL,
    descricao       VARCHAR(255) NOT NULL,
    quantidade      INT          NOT NULL DEFAULT 1,
    preco_custo_cents INT        NOT NULL DEFAULT 0,
    preco_venda_cents INT        NOT NULL DEFAULT 0,
    ativo           TINYINT(1)   NOT NULL DEFAULT 1,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_cotacoes_fornecedor_id (fornecedor_id),
    KEY idx_cotacoes_ativo (ativo),
    CONSTRAINT fk_cotacoes_fornecedor FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
