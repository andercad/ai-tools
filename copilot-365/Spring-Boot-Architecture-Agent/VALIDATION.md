# Validación

## Comprobaciones estáticas (`validation/validate.ps1`)
- 8 skills exactamente (límite de Microsoft 365 Copilot).
- `name` igual a la carpeta; `description` ≤ 1024 caracteres, única, con disparadores («Usar cuando») y sin texto genérico.
- Secciones `Objetivo`, `Salida` y `Autoevaluación` en cada skill; tamaño razonable.
- Routing de las ocho skills en `AGENT_INSTRUCTIONS.md`; instrucciones < 8000 caracteres.
- Términos clave por skill (hexagonal, GraphQL, outbox, BFF, SLO, strangler, etc.).
- ZIP regenerados desde `skills/` con `SKILL.md` en la raíz del ZIP (estructura de la documentación de Agent Builder) y verificados byte a byte contra la fuente.
- Al menos una plantilla o checklist por skill, referenciada desde `SKILL.md`, con tipo y profundidad admitidos e incluida en el ZIP; sin referencias a recursos inexistentes.
- Máximo de 3 preguntas aclaratorias en las instrucciones, igual que en los demás agentes.
- Recursos compartidos con otros agentes (`decision_matrix.py`, `eu-regulatory-map.md`, `backend-technology-selection.md`) idénticos byte a byte en todas las copias.
- Prueba de humo de `decision_matrix.py` cuando hay Python disponible. El script se probó con Python 3.12: casos robusto, sensible a pesos, empate, más de tres alternativas, pesos decimales y entradas no válidas.

Resultado de la última ejecución: **OK**.

## Recursos por skill
| Skill | Recurso |
|---|---|
| architecture-assessment | `templates/assessment-report.md` |
| modularity-domain | `reference/modularization-readiness.md` |
| api-integration | `reference/api-contract-checklist.md` |
| data-transactions | `reference/data-consistency-checklist.md` |
| security-identity | `reference/security-review-checklist.md`, `reference/eu-regulatory-map.md` |
| cloud-runtime | `reference/production-readiness-checklist.md` |
| observability-resilience | `templates/slo-resilience-policy.md` |
| modernization-governance | `templates/upgrade-plan.md`, `templates/adr-template.md`, `reference/backend-technology-selection.md`, `scripts/decision_matrix.py` |

## Cambios respecto a la versión anterior
- Seis skills eran plantillas genéricas con la misma descripción y procedimiento; se reescribieron con criterios de decisión, anti-patrones, notas de versión y salida específica.
- Las instrucciones añaden: modo sin acceso al código (≤3 preguntas aclaratorias), proporcionalidad de la respuesta, idioma, tratamiento de peticiones de código y reconciliación entre skills.
- Se eliminó el procedimiento duplicado en las skills.
- El validador en Python (requería un argumento no documentado) se sustituyó por `validate.ps1`, que además genera los ZIP.
- Se eliminaron los resultados contradictorios («0/8» con «sin errores», «FALLO» sin causa) del informe anterior.
- v3: mensajería/eventos y REST completo en `spring-api-integration`; Spring Modulith en `spring-modularity-domain`; estrategia de pruebas en `spring-modernization-governance`; plantillas comunes (matriz de decisión, registro de riesgos, diagramas) y consulta de fuentes oficiales en las instrucciones; conversation starters en el README.
- v4: una plantilla o checklist por skill (dos en modernización), cargada solo cuando se necesita; ZIP con `SKILL.md` en la raíz; máximo de preguntas aclaratorias unificado a 3 con los demás agentes.
- v5: derivaciones a los agentes Angular, Liferay y NestJS; IA generativa (integración, OWASP Top 10 para LLM, cuotas y coste); mapa de normativa UE; criterio Spring Boot frente a NestJS; script de matriz de decisión con análisis de sensibilidad; paquete para VS Code (`build-vscode.ps1` en la raíz). Prompts 24 a 26.

## Limitaciones
- **No se ha probado en Microsoft 365 Copilot.** La selección de skills la hace Agent Builder; hay que validarla con `validation/test-prompts.md`.
- Validación estática: comprueba presencia de contenido, no calidad de las respuestas.
- Las versiones y fechas de soporte no se fijan en el agente: las verifica en cada proyecto contra la documentación oficial. Las notas de versión en las skills (p. ej. Boot 3 → 4) son orientativas y deben contrastarse con la guía de migración oficial.
- No incluye documentación interna de la organización; añádela como conocimiento.
- `decision_matrix.py` solo se ejecuta donde el agente pueda ejecutar Python (sandbox de Agent Builder); en VS Code el agente es de solo lectura y hace el cálculo paso a paso.
- El mapa de normativa UE es orientativo y no sustituye al área legal o de cumplimiento.

## Riesgos abiertos
- La política de resiliencia tiene una sola dueña (`spring-observability-resilience`); `spring-api-integration` solo identifica dependencias y remite a ella.
- `spring-api-integration` es la skill más amplia (REST, GraphQL, eventos). Si en pruebas se invoca peor, recorta GraphQL a lo esencial antes de crear otra skill (el límite es 8).
- Una única skill de modernización cubre upgrades, pruebas y gobierno; si se invoca mal, ajusta su descripción antes de dividirla.
- Fuera de alcance deliberadamente: multi-tenancy, Spring Batch y FinOps. Añadir solo si aparecen en uso real.
