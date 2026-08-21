# Backend API

## Executar

Na raiz do repositório:

```bash
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

A documentação interativa fica disponível em:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

```text
GET  /api/v1/health
POST /api/v1/preparations
GET  /api/v1/preparations/{session_id}
POST /api/v1/preparations/{session_id}/messages
```

O endpoint de criação recebe `multipart/form-data` com:

- `job_url`: URL pública da vaga na Gupy.
- `cv`: currículo em PDF.
- `question_limit`: quantidade de desafios, de 1 a 100.

Exemplo:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/preparations \
  -F 'job_url=https://empresa.gupy.io/jobs/123456' \
  -F 'cv=@./curriculo.pdf;type=application/pdf' \
  -F 'question_limit=10'
```

As preparações ficam em memória e são removidas quando o servidor reinicia. O
PDF é usado por meio de um arquivo temporário e removido ao final da requisição.

O endpoint de mensagens recebe o histórico recente da conversa e usa o
diagnóstico salvo na sessão como contexto do mentor.

Em Docker, configure `DATABASE_URL` com a URL `Session pooler` IPv4 do
Supabase, na porta 5432. A URL direta do projeto depende de conectividade IPv6.
