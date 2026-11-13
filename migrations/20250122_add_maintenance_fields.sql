-- Migration: Adicionar campos de manutenção completos
-- Data: 2025-01-22
-- Descrição: Adiciona campos para suportar todos os dados do modal "Agendar Manutenção"

ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS cliente_id VARCHAR(36) NULL AFTER usuario_id;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS prioridade VARCHAR(20) NOT NULL DEFAULT 'normal' AFTER status;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS frequencia VARCHAR(20) NOT NULL DEFAULT 'custom' AFTER prioridade;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS valor_cents INT NOT NULL DEFAULT 0 AFTER frequencia;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS equipe VARCHAR(100) NULL AFTER valor_cents;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS endereco VARCHAR(500) NULL AFTER equipe;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS telefone VARCHAR(50) NULL AFTER endereco;
ALTER TABLE manutencoes ADD COLUMN IF NOT EXISTS proxima_manutencao VARCHAR(10) NULL AFTER telefone;

-- Adicionar índices para melhor performance
ALTER TABLE manutencoes ADD KEY IF NOT EXISTS idx_manutencoes_cliente_id (cliente_id);
ALTER TABLE manutencoes ADD KEY IF NOT EXISTS idx_manutencoes_equipe (equipe);
ALTER TABLE manutencoes ADD KEY IF NOT EXISTS idx_manutencoes_prioridade (prioridade);
ALTER TABLE manutencoes ADD KEY IF NOT EXISTS idx_manutencoes_frequencia (frequencia);
