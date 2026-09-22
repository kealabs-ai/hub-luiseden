-- Migration: Campos adicionais em cotacoes e plantas
-- Date: 2026-09-22

-- cotacoes: adiciona aprovada e categoria
ALTER TABLE cotacoes
    ADD COLUMN IF NOT EXISTS aprovada     TINYINT(1)   NOT NULL DEFAULT 0 AFTER preco_venda_cents,
    ADD COLUMN IF NOT EXISTS categoria    VARCHAR(100)     NULL AFTER aprovada;

-- plantas: adiciona rastreabilidade da origem
ALTER TABLE plantas
    ADD COLUMN IF NOT EXISTS fornecedor_id VARCHAR(36) NULL AFTER imagem_url,
    ADD COLUMN IF NOT EXISTS cotacao_id    VARCHAR(36) NULL AFTER fornecedor_id,
    ADD KEY IF NOT EXISTS idx_plantas_fornecedor_id (fornecedor_id),
    ADD KEY IF NOT EXISTS idx_plantas_cotacao_id    (cotacao_id);
