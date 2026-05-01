# TCC 2 — Análise Comparativa de Ferramentas para Geração de APIs REST a partir de Bancos de Dados PostgreSQL

Este repositório contém os artefatos do TCC 2, incluindo os testes de desempenho e flexibilidade das ferramentas **PostgREST**, **pREST**, **DreamFactory** e **NocoDB**.

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.8+](https://www.python.org/downloads/)
- [Grafana k6](https://grafana.com/docs/k6/latest/set-up/install-k6/)

---

## 1. Instalação do Grafana k6

### Windows

Baixe o instalador em <https://dl.k6.io/msi/k6-latest-amd64.msi> ou use o Chocolatey:

```powershell
choco install k6
```

Verifique a instalação:

```bash
k6 version
```

---

## 2. Subir os projetos no Docker

Todos os serviços compartilham a rede Docker `test_network`. Siga a ordem abaixo.

### 2.1 Banco de dados (PostgreSQL + seed)

```bash
docker compose -f docker-compose-database.yml up -d
```

O arquivo `seed.sql` é carregado automaticamente na primeira inicialização, populando o banco `marketplace`.

### 2.2 Ferramentas API

Suba apenas as ferramentas que deseja testar (ou todas de uma vez):

```bash
# PostgREST — porta 3000
docker compose -f docker-compose-postgrest.yml up -d

# pREST — porta 3001
docker compose -f docker-compose-prest.yml up -d

# DreamFactory — porta 3002
docker compose -f docker-compose-dreamfactory.yml up -d

# NocoDB — porta 8080
docker compose -f docker-compose-nocodb.yml up -d
```

> **DreamFactory**: na primeira inicialização, aguarde alguns minutos até o container ficar saudável antes de executar os testes.

### 2.3 Verificar os serviços

```bash
docker ps
```

| Serviço | Container | Porta |
|---|---|---|
| PostgreSQL | `postgres_database` | 5432 |
| PostgREST | `postgrest_api` | 3000 |
| pREST | `prest_api` | 3001 |
| DreamFactory | `dreamfactory_api` | 3002 |
| NocoDB | `nocodb_api` | 8080 |

---

## 3. Testes de Desempenho

Os scripts Python na pasta `teste-desempenho/` orquestram o k6 e monitoram o consumo de RAM dos containers via `docker stats`. Os resultados são salvos em arquivos JSON na mesma pasta do script executado.

### Cenários disponíveis

| Cenário | Proporção leitura/escrita | Script agregado |
|---|---|---|
| 100 % GET | Apenas leituras | `all_performance.py` |
| 80/20 | 80 % GET / 20 % POST | `all_performance_80_20.py` |
| 60/40 | 60 % GET / 40 % POST | `all_performance_60_40.py` |

Cada cenário roda quatro perfis de carga do k6: **load**, **stress**, **spike** e **soak**.

### 3.1 Executar todos os testes de uma ferramenta

Você pode executar os scripts individualmente por ferramenta. Por exemplo, para o PostgREST:

```bash
# Cenário 100% GET
python teste-desempenho/postgrest/postgrest_performance.py

# Cenário 80/20
python teste-desempenho/postgrest/postgrest_performance_80_20.py

# Cenário 60/40
python teste-desempenho/postgrest/postgrest_performance_60_40.py
```

Substitua `postgrest` por `nocodb`, `prest` ou `dreamfactory` para testar as outras ferramentas.

### 3.2 Executar todos os testes de todas as ferramentas

Os scripts `all_performance*.py` executam sequencialmente todos os scripts individuais de cada ferramenta:

```bash
# Cenário 100% GET (todas as ferramentas)
python teste-desempenho/all_performance.py

# Cenário 80/20 (todas as ferramentas)
python teste-desempenho/all_performance_80_20.py

# Cenário 60/40 (todas as ferramentas)
python teste-desempenho/all_performance_60_40.py
```

> ⚠️ A execução completa pode levar **várias horas**. Garanta que todos os containers estejam em execução antes de iniciar.

### 3.3 Resultados em JSON

Ao final de cada execução, os resultados são salvos na pasta da ferramenta correspondente com o timestamp no nome:

```
teste-desempenho/postgrest/results_postgrest_get_100_YYYYMMDD-HHMMSS.json
teste-desempenho/postgrest/results_postgrest_80_20_YYYYMMDD-HHMMSS.json
teste-desempenho/postgrest/results_postgrest_60_40_YYYYMMDD-HHMMSS.json
```

Cada arquivo contém métricas por perfil de carga (`load`, `stress`, `spike`, `soak`):

```json
{
  "ferramenta": "PostgREST",
  "cenario": "100% GET",
  "timestamp": "20251118-081853",
  "testes": {
    "load":   { "avg_ms": ..., "p95_ms": ..., "throughput_rps": ..., "fail_rate": ..., "success_rate": ..., "peak_mem_gb": ... },
    "stress": { ... },
    "spike":  { ... },
    "soak":   { ... }
  }
}
```

---

## 4. Testes de Flexibilidade

Os testes de flexibilidade verificam quais operações HTTP e consultas cada ferramenta suporta. Eles podem ser executados em qualquer ferramenta capaz de realizar requisições HTTP (Insomnia, Postman, curl, etc.).

Os arquivos de coleção estão na pasta `teste-flexibilidade/`:

| Arquivo | Descrição |
|---|---|
| `testes_HTTP.yaml` | Operações básicas HTTP: GET, POST, PUT, PATCH e DELETE |
| `testes_Q1-Q5.yaml` | Consultas de flexibilidade: Q1 (simples), Q2 (ordenação/paginação), Q3 (agregação), Q4 (JOIN simples), Q5 (JOIN múltiplo) |

### 4.1 Importar no Insomnia

1. Abra o [Insomnia](https://insomnia.rest/download).
2. Clique em **Import** → **From File**.
3. Selecione `testes_HTTP.yaml` ou `testes_Q1-Q5.yaml`.
4. As variáveis de ambiente já estão configuradas nos arquivos com os valores padrão abaixo.

### 4.2 Variáveis de ambiente

| Variável | Valor padrão |
|---|---|
| `postgrest_url` | `http://localhost:3000` |
| `prest_url` | `http://localhost:3001/marketplace/public` |
| `dreamfactory_url` | `http://localhost:3002/api/v2/public/_table` |
| `dreamfactory_key` | `46624cdc2e657389f229066bf9092e8accea917c0c426fe2b8e0ac2edf80b0ac` |
| `nocodb_url` | `http://localhost:8080/api/v2` |
| `nocodb_token` | `wYf774fyGotOY30u0yHQnzb7p6VYsT-t5UCRE97W` |

### 4.3 Executar com curl (exemplo)

Os testes podem ser executados em qualquer ambiente que consiga fazer requisições HTTP. Exemplos com `curl`:

```bash
# PostgREST — GET produto por ID
curl "http://localhost:3000/products?id=eq.1"

# pREST — GET produto por ID
curl "http://localhost:3001/marketplace/public/products?id=1"

# DreamFactory — GET produto por ID (requer API Key)
curl -H "X-DreamFactory-Api-Key: 46624cdc2e657389f229066bf9092e8accea917c0c426fe2b8e0ac2edf80b0ac" \
     "http://localhost:3002/api/v2/public/_table/products/1"

# NocoDB — GET registro por ID (requer token)
curl -H "xc-token: wYf774fyGotOY30u0yHQnzb7p6VYsT-t5UCRE97W" \
     "http://localhost:8080/api/v2/tables/mnjffmzxhy9jt2t/records/1"
```

---

## 5. Derrubar os serviços

```bash
docker compose -f docker-compose-postgrest.yml down
docker compose -f docker-compose-prest.yml down
docker compose -f docker-compose-dreamfactory.yml down
docker compose -f docker-compose-nocodb.yml down
docker compose -f docker-compose-database.yml down
```

Para remover também os volumes (apaga os dados do banco):

```bash
docker compose -f docker-compose-database.yml down -v
```
