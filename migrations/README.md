# Migrations - HubLuisEden

## Ordem de execução

1. `create_tables.sql` — cria todas as tabelas do zero

## Executar manualmente

```bash
mysql -h <host> -u <user> -p <database> < create_tables.sql
```

As tabelas também são criadas automaticamente no startup de cada serviço via SQLAlchemy (`Base.metadata.create_all`).
