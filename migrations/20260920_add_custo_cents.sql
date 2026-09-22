-- Adds catalog cost used by dashboard margin calculations.
ALTER TABLE plantas
    ADD COLUMN custo_cents INT NOT NULL DEFAULT 0 AFTER preco_cents;
