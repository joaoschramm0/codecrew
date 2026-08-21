# Interface da demo

Este frontend consome a API FastAPI para gerar a preparação e conversar com o
mentor contextual.

As regras visuais e os tokens usados pelas telas estão em [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md).

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload
```

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173` e percorra o fluxo com uma URL pública da Gupy e
um currículo em PDF:

1. Onboarding com URL e currículo PDF.
2. Processamento real pelo FastAPI.
3. Resumo do match em stories.
4. Workspace com mentor, assuntos e desafios reais.

Os desafios abrem dentro do workspace em um leitor Markdown próprio. O link
para o LeetCode continua disponível na tela de leitura.

No desenvolvimento, o Vite encaminha `/api` para `http://127.0.0.1:8000`. Em
outro ambiente, defina `VITE_API_BASE_URL` com a origem da API.

Para gerar a versão de produção:

```bash
npm run build
```
