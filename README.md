# calculadora_estudo

Calculadora de Tempo de Estudo — um servidor HTTP em Python que registra sessões de estudo em um arquivo CSV, permitindo mensurar quanto tempo foi dedicado a cada assunto durante a semana.

## Pré-requisitos

- Python 3.8+
- pip

## Instalação

```bash
pip install -r requirements.txt
```

## Como usar

### 1. Iniciar o servidor

```bash
python app.py
```

O servidor sobe em `http://localhost:5000`.

---

### Endpoints

#### `POST /iniciar`
Inicia uma sessão de estudo.

**Body (JSON):**
```json
{ "assunto": "Python" }
```

**Resposta de sucesso (200):**
```json
{
  "mensagem": "Sessão iniciada.",
  "assunto": "Python",
  "inicio": "2024-01-15 09:00:00"
}
```

---

#### `POST /finalizar`
Finaliza a sessão ativa e grava no CSV.

**Resposta de sucesso (200):**
```json
{
  "mensagem": "Sessão finalizada e registrada.",
  "assunto": "Python",
  "inicio": "2024-01-15 09:00:00",
  "fim": "2024-01-15 10:30:00",
  "duracao_minutos": 90.0
}
```

---

#### `GET /sessoes`
Lista todas as sessões já registradas.

**Resposta (200):**
```json
[
  {
    "assunto": "Python",
    "data_inicio": "2024-01-15 09:00:00",
    "data_fim": "2024-01-15 10:30:00",
    "duracao_minutos": "90.0"
  }
]
```

---

#### `GET /resumo_semanal`
Retorna o resumo de minutos estudados por assunto na semana atual (segunda a domingo).

**Resposta (200):**
```json
{
  "semana": "2024-01-15 a 2024-01-21",
  "resumo_por_assunto": {
    "Python": 90.0,
    "Docker": 45.0
  },
  "total_minutos": 135.0
}
```

---

## Estrutura do CSV (`estudos.csv`)

| assunto | data_inicio         | data_fim            | duracao_minutos |
|---------|---------------------|---------------------|-----------------|
| Python  | 2024-01-15 09:00:00 | 2024-01-15 10:30:00 | 90.0            |

O arquivo é criado automaticamente na primeira execução.

---

## Extensões sugeridas

- Migrar o armazenamento para um banco relacional (SQLite, PostgreSQL) ou não relacional (MongoDB, Redis).
- Adicionar autenticação por usuário.
- Criar uma interface web ou CLI para facilitar o uso.
