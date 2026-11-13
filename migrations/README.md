# Migrations - HubLuisEden

## Ordem de execução

1. `create_tables.sql` — cria todas as tabelas do zero
2. `add_data_venda.sql` — adiciona `data_venda` à tabela `vendas` existente

## Executar manualmente

```bash
mysql -h <host> -u <user> -p <database> < create_tables.sql

# Para uma instalação existente:
mysql -h <host> -u <user> -p <database> < add_data_venda.sql
```

As tabelas também são criadas automaticamente no startup de cada serviço via SQLAlchemy (`Base.metadata.create_all`).
