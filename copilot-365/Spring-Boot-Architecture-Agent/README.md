# Spring Boot Architecture Advisor

Agente para Microsoft 365 Copilot (Agent Builder) orientado a arquitectura, no a desarrollo cotidiano.

## Contenido
- `AGENT_INSTRUCTIONS.md`: instrucciones del agente (menos de 8000 caracteres).
- `skills/`: fuentes de las ocho skills (editar aquí). Cada una incluye al menos una plantilla o checklist en `templates/` o `reference/`, que el agente carga solo cuando la necesita. `spring-modernization-governance` incluye además el script `scripts/decision_matrix.py`.
- `skill-packages/`: ocho ZIP generados desde `skills/` (`SKILL.md` y recursos en la raíz del ZIP), listos para subir. No editar a mano.
- `validation/validate.ps1`: valida el paquete y regenera los ZIP.
- `validation/test-prompts.md`: 26 prompts de prueba para validar el agente en Copilot.
- `VALIDATION.md`: estado de la validación y limitaciones.

## Instalación
1. Crea el agente y pega `AGENT_INSTRUCTIONS.md` en sus instrucciones.
2. Sube los ocho ZIP de `skill-packages/` como skills. El límite de Microsoft 365 Copilot es de ocho skills por agente; no añadas más: fusiona o reparte contenido entre las existentes.
3. Añade como conocimiento los estándares y la documentación interna que correspondan.
4. Si tu tenant lo permite, activa búsqueda web limitada a fuentes oficiales para reducir errores de versión: `docs.spring.io`, `spring.io/blog`, `github.com/spring-projects` (wikis de notas de versión y guías de migración) y `learn.microsoft.com` si despliegas en Azure.
5. Configura los conversation starters (abajo).
6. Ejecuta los prompts de `validation/test-prompts.md` y ajusta las `description` de las skills que no se invoquen bien.

## Conversation starters
| Título | Prompt |
|---|---|
| Evaluar mi aplicación | Evalúa la arquitectura de mi aplicación Spring Boot y prioriza riesgos y deuda técnica. |
| ¿Monolito o microservicios? | Tenemos un monolito Spring Boot. ¿Nos conviene un monolito modular o microservicios? |
| Diseñar una API | Ayúdame a decidir entre REST, GraphQL o eventos para integrar estos sistemas. |
| Planificar un upgrade | Planifica el upgrade de nuestra aplicación a la última versión soportada de Spring Boot. |
| Seguridad e identidad | ¿Qué arquitectura de autenticación y autorización recomiendas para nuestra SPA y API? |
| Redactar un ADR | Redacta un ADR para esta decisión de arquitectura. |

## GitHub Copilot en VS Code
Las mismas skills sirven para GitHub Copilot en VS Code (formato Agent Skills). No hay script de empaquetado en este repo: copia cada carpeta de `skills/<skill>` a `.github/skills/` del repositorio que quieras analizar (o a `~/.copilot/skills` para uso personal) y usa `AGENT_INSTRUCTIONS.md` como contenido de un agente en `.github/agents/`.
- En VS Code el agente lee el repositorio, así que la evaluación parte de ficheros reales y no de supuestos.
- Solo tiene herramientas de lectura, búsqueda y web: no edita ficheros ni ejecuta comandos. Si necesitas la matriz de decisión calculada, ejecuta `decision_matrix.py` o pide el cálculo paso a paso.
- Los botones para pasar la conversación a otro de los cuatro agentes (handoffs) solo están disponibles en el harness Local.

## Mantenimiento
Tras editar cualquier `SKILL.md` o las instrucciones, ejecuta:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File validation\validate.ps1
```

Comprueba frontmatter, descripciones (≤1024 caracteres, únicas, con «Usar cuando»), secciones obligatorias, routing, tamaño de las instrucciones, máximo de preguntas aclaratorias, recursos referenciados y cobertura de contenido, y regenera y verifica los ZIP.

## Skills
| Skill | Ámbito |
|---|---|
| `spring-architecture-assessment` | Evaluación y descubrimiento |
| `spring-modularity-domain` | Modularidad, hexagonal, monolito modular y microservicios |
| `spring-api-integration` | REST, GraphQL, mensajería/eventos, integración e IA generativa |
| `spring-data-transactions` | Persistencia, transacciones, outbox, migraciones |
| `spring-security-identity` | Identidad, OAuth/OIDC, autorización, amenazas, IA generativa, normativa UE |
| `spring-cloud-runtime` | Plataforma, contenedores, native, despliegue, DR |
| `spring-observability-resilience` | SLO, telemetría, resiliencia, capacidad, cuotas y coste de IA |
| `spring-modernization-governance` | Upgrades, strangler, pruebas, ADR, quality gates, Spring Boot frente a NestJS, matriz de decisión |
