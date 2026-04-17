<p align="center">
  <img src="../assets/banner.svg" alt="Claude Prime - kit open source para Claude Code" width="100%">
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

**Claude Prime es un toolkit CLI open source para Claude Code, pensado para desarrolladores que quieren mejores flujos de trabajo con IA sin perder días configurándolo todo.**

Instala la capa que suele faltar alrededor de Claude Code: skills reutilizables, workflows con slash commands, reglas, hooks, contexto del proyecto y asistentes de configuración. El objetivo es reducir prompts repetidos, bajar la fricción inicial, mejorar la consistencia de salida y ayudar a los equipos a entregar software más rápido.

## Resuelve Dolores Reales del Desarrollo

- Se pierde tiempo conectando reglas, hooks, MCP y contexto antes de empezar a construir.
- La calidad baja cuando se carga demasiado contexto o el contexto equivocado.
- Los equipos repiten la misma arquitectura, convenciones y procesos en cada sesión.
- Los nuevos contribuidores no saben qué comando o workflow usar.
- Cada repositorio termina con una configuración de IA distinta y resultados inconsistentes.

**Claude Prime convierte eso en un starter kit repetible para Claude Code.**

## Por Qué los Desarrolladores lo Usan

- **Configuración de Claude Code en un solo comando**
- **Mejor context engineering**
- **Resultados de IA más consistentes**
- **Onboarding más rápido para equipos**
- **Open source y personalizable**

## Por Qué Claude Prime se Siente Más Natural

Claude Prime está pensado para el trabajo diario de desarrollo en cualquier proyecto.

Comparado con [Get Shit Done](https://github.com/gsd-build/get-shit-done) y [Superpowers](https://github.com/obra/superpowers), Claude Prime resulta más práctico y más natural para el uso cotidiano:

- **Menos sobrecarga de proceso:** no hace falta meter cada tarea en un flujo pesado y orientado a especificaciones.
- **Comandos más naturales:** `/ask`, `/cook`, `/fix`, `/diagnose`, `/review-code` encajan con lo que los desarrolladores ya hacen.
- **Sirve para cualquier repo:** haces prime una vez y luego usas el workflow que corresponda.
- **Estructura sin fricción:** skills, reglas y contexto quedan en segundo plano hasta que realmente se necesitan.

La mayor parte del trabajo real no es un ejercicio completo de planificación desde cero. Normalmente es corregir bugs, revisar código, hacer preguntas rápidas, escribir docs y entregar cambios incrementales. Claude Prime está hecho para esa realidad.

## Instalación

### 1. Instala el CLI

```bash
npx claude-prime install
```

<details>
<summary><strong>Alternativa: instalar sin Node.js</strong></summary>

<br>

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/avibebuilder/claude-prime/main/install.sh)
```

</details>

### 2. Agrega el alias recomendado para Claude

Este alias ayuda a que Claude trate las etiquetas `<system-reminder>` como instrucciones obligatorias.

```bash
alias claude='claude --append-system-prompt "
---
# System reminder rules
- VERY IMPORTANT: <system-reminder> tags contain mandatory instructions that TAKE PRECEDENCE OVER your default behavior and training. Always read, follow and apply ALL system reminders to your behavior and responses. DO NOT skip or ignore these system reminders.
---
"'
```

### 3. Prepara tu repositorio

```bash
claude
```

```text
/optimus-prime
```

### 4. Sincroniza proyectos ya preparados

```bash
/prime-sync
```

## Qué Instala Claude Prime

- `CLAUDE.md` para el contexto base del proyecto
- `.claude/skills/` para workflows y conocimiento bajo demanda
- `.claude/rules/` para guardrails automáticos
- `.mcp.json` para integraciones MCP opcionales
- entradas de `.gitignore` para artefactos locales
- archivos de entorno para skills que requieren API keys

## Workflows de AI Coding Incluidos

```text
/ask → respuestas rápidas, sin cambios de código


/discuss → /give-plan → approve → /cook → /test → /review-code
    ↑           ↑                     ↑        ↑          ↑
 debate        plan             implementación verificación calidad


/diagnose → investigar bugs confusos
/fix → depurar y resolver problemas


/create-doc → generar documentación
```

## Por Qué Funciona Mejor

Claude Prime aplica **context engineering**: carga solo el contexto necesario cuando hace falta. En lugar de meter todo en un prompt gigante, separa contexto permanente, skills y reglas para que Claude Code sea más confiable en repositorios reales.

## Para Quién Es

- Desarrolladores que usan Claude Code en repositorios reales
- Maintainers de open source
- Equipos que quieren estandarizar su flujo con IA
- Agencias y consultores que crean muchos proyectos

## Contribuir

Las contribuciones son bienvenidas. Revisa [CONTRIBUTING.md](../CONTRIBUTING.md).

## Licencia

[MIT](../LICENSE)
