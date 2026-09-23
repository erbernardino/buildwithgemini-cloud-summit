---
id: "cloudsummit-reference-project-brief"
title: "Project Brief — Cloud Summit AI Concierge"
type: reference
status: active
owner: "Emerson Bernardino"
last_reviewed: 2026-09-23
confidence: high
tags:
  - agent
  - cloud-summit
  - gemini
  - adk
  - a2ui
relations:
  depends_on: []
  related_to:
    - "[[docs/index]]"
    - "[[docs/architecture]]"
    - "[[docs/guide-swag]]"
  supersedes: []
---

# My agent: Cloud Summit AI Concierge
One-liner: Assistente inteligente de IA para o Google Cloud Summit, com navegação de agenda técnica, recomendações de sessões, persistência no Firestore, geração de crachás visuais com Gemini e interface conversacional com A2UI.

Tool coverage:
- Memory: Lembra as preferências técnicas do participante (ex.: nível de senioridade, interesse em IA Generativa/DevOps/Data, alergias e restrições alimentares para o coffee break) entre sessões via Vertex AI Memory Bank.
- Tools: Busca de sessões no catálogo da conferência (`search_sessions`), consulta de detalhes de palestras (`get_session_details`), agendamento/favoritos no Firestore (`bookmark_session`, `list_bookmarked_sessions`), e cálculo de grade horária (`calculate_schedule_timing`).
- Catalog/UI: Catálogo de palestras, palestrantes, salas e crachás visuais renderizados em formato de cards estruturados e tabelas interativas utilizando A2UI v0.8.
- Image gen: Geração de crachás personalizados e passes de acesso da conferência com imagem estilizada gerada pelo modelo `gemini-3.1-flash-lite-image` (Nano Banana 2 Lite), salvando artefato e publicando no Google Cloud Storage (GCS).
- Sandbox: Execução isolada em sandbox para cálculo de cronograma, tempo de deslocamento entre auditórios e estimativas de dimensionamento de nuvem nos workshops.

Core rails (everyone): memory, tools, eval, deploy, frontend
My stretch menu (pick later): A2UI rich visual cards, Cloud Storage asset upload, Firestore session bookmarks, Cloud Run FastAPI frontend proxy
First eval question: "Quais são as palestras disponíveis sobre Agentes de IA e Gemini no Google Cloud Summit?"
