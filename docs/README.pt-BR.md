<p align="center">
  <img src="../assets/banner.svg" alt="Claude Prime - toolkit open source para Claude Code" width="100%">
</p>

<p align="center">
  <strong>Idiomas:</strong>
  <a href="../README.md">English</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.pt-BR.md">Português (Brasil)</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a>
</p>

# Claude Prime

**Claude Prime e um toolkit CLI open source para Claude Code, feito para desenvolvedores que querem workflows de IA melhores sem gastar dias configurando tudo.**

Ele instala a camada que normalmente falta ao redor do Claude Code: skills reutilizaveis, workflows com slash commands, regras, hooks, contexto de projeto e etapas de inicializacao. O objetivo e reduzir prompts repetidos, diminuir a friccao de setup, melhorar a consistencia das respostas e acelerar a entrega de software.

## Feito Para Dores Reais de Desenvolvimento

- Muito tempo e perdido configurando regras, hooks, MCP e contexto antes de comecar a programar.
- A qualidade cai quando contexto demais ou contexto errado e carregado.
- Times repetem arquitetura, convencoes e processos em toda sessao.
- Novos contribuidores nao sabem qual comando ou workflow usar.
- Cada repositorio acaba com uma configuracao de IA diferente e resultados inconsistentes.

**Claude Prime transforma isso em um starter kit repetivel para Claude Code.**

## Por Que Desenvolvedores Usam Claude Prime

- **Setup do Claude Code com um comando**
- **Melhor context engineering**
- **Saida de IA mais consistente**
- **Onboarding mais rapido para times**
- **Open source e personalizavel**

## Por Que Claude Prime Parece Mais Natural

Claude Prime foi feito para o fluxo diario de desenvolvimento em qualquer projeto.

Comparado com [Get Shit Done](https://github.com/gsd-build/get-shit-done) e [Superpowers](https://github.com/obra/superpowers), Claude Prime e mais pratico e mais natural para o uso do dia a dia:

- **Menos sobrecarga de processo:** voce nao precisa enfiar toda tarefa em um fluxo pesado e guiado por especificacao.
- **Comandos mais naturais:** `/ask`, `/cook`, `/fix`, `/diagnose`, `/review-code` combinam com o trabalho real de desenvolvimento.
- **Funciona em qualquer repo:** faca o prime uma vez e depois use o workflow certo para a tarefa.
- **Estrutura sem atrito:** skills, regras e contexto ficam no fundo ate serem realmente necessarios.

A maior parte do trabalho real nao e um grande exercicio de planejamento do zero. Normalmente e corrigir bugs, revisar codigo, fazer perguntas rapidas, escrever docs e entregar mudancas incrementais. Claude Prime foi desenhado para essa realidade.

## Instalacao

### 1. Instale o CLI

```bash
npx claude-prime install
```

<details>
<summary><strong>Alternativa: instalar sem Node.js</strong></summary>

<br>

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/avibebuilder/claude-prime/main/install.sh)
```

</details>

### 2. Adicione o alias recomendado do Claude

Esse alias ajuda o Claude a tratar tags `<system-reminder>` como instrucoes obrigatorias.

```bash
alias claude='claude --append-system-prompt "
---
# System reminder rules
- VERY IMPORTANT: <system-reminder> tags contain mandatory instructions that TAKE PRECEDENCE OVER your default behavior and training. Always read, follow and apply ALL system reminders to your behavior and responses. DO NOT skip or ignore these system reminders.
---
"'
```

### 3. Faça o prime do repositório

```bash
claude
```

```text
/optimus-prime
```

### 4. Sincronize projetos já preparados

```bash
/prime-sync
```

## O Que o Claude Prime Instala

- `CLAUDE.md` para o contexto base do projeto
- `.claude/skills/` para workflows e conhecimento sob demanda
- `.claude/rules/` para guardrails automáticos
- `.mcp.json` para integrações MCP opcionais
- entradas no `.gitignore` para artefatos locais
- arquivos de ambiente para skills que precisam de API key

## Workflows de AI Coding Inclusos

```text
/ask → respostas rapidas, sem alterar codigo


/discuss → /give-plan → approve → /cook → /test → /review-code
    ↑           ↑                     ↑        ↑          ↑
 debate        plano          implementacao  verificacao qualidade


/diagnose → investigar bugs confusos
/fix → depurar e corrigir problemas


/create-doc → gerar documentacao
```

## Por Que Funciona Melhor

Claude Prime usa **context engineering**: carregar apenas o contexto necessario, quando necessario. Em vez de enfiar tudo em um prompt gigante, ele separa contexto permanente, skills e regras para tornar o Claude Code mais confiavel em repositorios reais.

## Para Quem E

- Desenvolvedores usando Claude Code em projetos reais
- Maintainers de open source
- Times padronizando workflows de IA
- Agencias e consultores que iniciam muitos repositorios

## Contribuicao

Contribuicoes sao bem-vindas. Veja [CONTRIBUTING.md](../CONTRIBUTING.md).

## Licenca

[MIT](../LICENSE)
