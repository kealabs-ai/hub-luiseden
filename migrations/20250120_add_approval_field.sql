-- Migration: Add Approval Field to Quotations
-- Date: 2025-01-20
-- Description: Add aprovada field to track quotation approval status

ALTER TABLE cotacoes ADD COLUMN aprovada TINYINT(1) NOT NULL DEFAULT 0 AFTER preco_venda_cents;

-- Create index for approval status
CREATE INDEX idx_cotacoes_aprovada ON cotacoes(aprovada);
