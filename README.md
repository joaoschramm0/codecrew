# CodeCrew

Preparação personalizada para entrevistas a partir do currículo do candidato e
de uma vaga real.

## Fluxo da V1

1. Coleta e normaliza uma vaga publicada na Gupy.
2. Extrai o texto de um currículo em PDF e o estrutura com IA.
3. Compara currículo e vaga para encontrar pontos fortes e lacunas.
4. Usa o diagnóstico para definir tópicos e dificuldade de programação.
5. Seleciona desafios compatíveis no PostgreSQL.

As interações de IA usam o OpenRouter com o modelo
`deepseek/deepseek-v4-flash` por padrão.

## Requisitos

- Python 3.12+
- PostgreSQL com a tabela `questions` carregada
- Chave de API do OpenRouter

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
```

Preencha o `.env`:

```env
OPENROUTER_API_KEY=coloque_sua_chave_aqui
OPENROUTER_MODEL=deepseek/deepseek-v4-flash
DATABASE_URL=postgresql+psycopg2://postgres.PROJECT_REF:SENHA@aws-0-REGIAO.pooler.supabase.com:5432/postgres
```

Para executar com Docker em uma rede sem IPv6, use a conexão `Session pooler`
do Supabase, disponível em `Connect > Session pooler`. A conexão direta
`db.PROJECT_REF.supabase.co:5432` usa IPv6 por padrão e pode não funcionar na
rede interna do Docker.

## Carregar o banco de desafios

O coletor do LeetCode é um utilitário independente, usado somente para criar e
popular a tabela `questions`:

```bash
python -m backend.scripts.load_leetcode
```

Ele não faz parte do fluxo executado para cada candidato.

## Executar o fluxo completo

```bash
python -m backend.app.services.pipeline \
  "https://empresa.gupy.io/jobs/123456" \
  --cv "./curriculo.pdf" \
  --limit 10
```

O resultado é um JSON com este formato:

```json
{
  "job": {},
  "candidate": {},
  "match": {
    "aderencia": 75,
    "resumo": "...",
    "pontos_fortes": [],
    "lacunas": [],
    "focos_de_preparacao": []
  },
  "algorithm_profile": {
    "tags": ["array", "hash-table", "string"],
    "difficulty": "Medium"
  },
  "questions": []
}
```

## Executar a demo

Com Docker Compose:

```bash
docker compose up --build
```

No Ubuntu, caso o subcomando `docker compose` não esteja disponível:

```bash
sudo apt install docker-compose-v2
```

Abra `http://localhost:5173`. A API também fica disponível em
`http://localhost:8000/docs`.

Para executar sem Docker, inicie a API na raiz do repositório:

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload
```

Em outro terminal, inicie a interface:

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`, informe a URL pública de uma vaga da Gupy e
selecione um currículo em PDF.

## Estrutura

```text
backend/
├── app/
│   ├── api/           # rotas HTTP e dependências
│   ├── integrations/  # Gupy e OpenRouter
│   ├── repositories/  # armazenamento das sessões
│   ├── schemas/       # contratos de entrada e saída
│   └── services/      # análise, preparação e mentor
├── scripts/           # utilitários operacionais
└── requirements.txt
frontend/              # interface React/Vite
```

O carregador do catálogo do LeetCode fica em
`backend/scripts/load_leetcode.py`. A orquestração do fluxo fica em
`backend/app/services/pipeline.py`.

## Limites atuais

- A coleta automática aceita vagas da Gupy.
- O currículo precisa ser um PDF com texto selecionável; não há OCR.
- O banco de desafios deve ser carregado antes da execução.
- As sessões ficam em memória e são perdidas ao reiniciar a API.

## Autores

Rodrigo Rodrigues, Joao Schramm e Augusto Krause.
