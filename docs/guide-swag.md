---
id: "cloudsummit-procedure-guide-swag"
title: "Procedimento de Publicação e Resgate de Swag — Track 3"
type: procedure
status: active
owner: "Emerson Bernardino"
last_reviewed: 2026-09-23
confidence: high
tags:
  - procedure
  - swag
  - github
  - submission
  - build-with-gemini
relations:
  depends_on:
    - "[[docs/index]]"
    - "[[project_brief]]"
  related_to:
    - "[[docs/architecture]]"
    - "[[docs/log]]"
  supersedes: []
---

# 🎁 Procedimento de Publicação e Resgate de Swag — Track 3

Este guia descreve os requisitos, procedimentos de publicação no GitHub e submissão do formulário oficial para concorrer ao **swag (moletom oficial Build with Gemini)** e inclusão na galeria oficial de projetos do evento.

---

## 1. Requisitos para Elegibilidade ao Swag

Para ter direito ao moletom oficial e à insígnia Google Developer Program (GDP), o projeto deve cumprir:
1. **Nome do Repositório:** Seguir o padrão obrigatório `buildwithgemini-[NOME-DO-APP]` (ex.: `buildwithgemini-cloudsummit`).
2. **Repositório Público:** O repositório no GitHub deve ser público.
3. **Escaneamento de Segredos Aprovado:** Nenhuma chave de API, arquivo `.env`, credencial de service account ou chave privada pode estar versionada.
4. **Capacidades Mínimas Implementadas:** Ter a estrutura ADK com ferramentas, brief do projeto, documentação e frontend funcional.
5. **Formulário Oficial Enviado:** Submeter o formulário Google com a URL do repositório público.

---

## 2. Passo a Passo Operacional

### Passo 1: Preparação do Repositório Local
Execute a validação automatizada de segredos e higienização do git:
```bash
bash .agents/skills/publish-to-github/publish.sh prep
```
*O script verifica se há chaves ou arquivos sensíveis em stage e prepara o repositório.*

### Passo 2: Autenticação no GitHub
Verifique se a sessão do GitHub CLI está ativa com a conta pessoal:
```bash
gh auth status
```
Caso seja necessário autenticar:
```bash
printf 'y\n' | gh auth login --hostname github.com --git-protocol https --web
```

### Passo 3: Criação e Publicação do Repositório Remoto
Crie o repositório público na sua conta pessoal do GitHub:
```bash
gh repo create buildwithgemini-cloudsummit --public --source=. --remote=origin --push
```

### Passo 4: Obtenção do Link Pré-Preenchido do Formulário
Gere a URL de submissão com os parâmetros do projeto já configurados:
```bash
bash .agents/skills/publish-to-github/publish.sh formlink "https://github.com/erbernardino/buildwithgemini-cloudsummit"
```

---

## 3. Submissão do Formulário

Abra o formulário no navegador e preencha os dados pessoais restantes:
- **Nome Completo** de inscrição no evento.
- **E-mail** cadastrado.
- Confirmação de resgate da **insígnia GDP**.
- Consentimento para destaque do projeto na **Galeria Oficial do Build with Gemini**.
