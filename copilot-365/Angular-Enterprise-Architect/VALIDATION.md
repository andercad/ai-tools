# Validación

## Resultado de las comprobaciones estáticas
Ejecutadas con `validation/validate.ps1 -Build`: **460 comprobaciones superadas, 0 fallos** (461 cuando hay Python disponible y se ejecuta la prueba de humo del script).

Límites de Agent Builder ([Custom skills in declarative agents](https://learn.microsoft.com/microsoft-365/copilot/extensibility/declarative-agent-skills)):
- Instrucciones del agente: 7261 caracteres (límite 8000).
- 8 skills (límite 8 por agente).
- `SKILL.md` de menos de 20.000 caracteres, con `name` y `description` en el front matter.
- ZIP de 50 MB o menos, con `SKILL.md` en la raíz, tipos de archivo soportados, profundidad 3 o menos y 350 archivos o menos.

Calidad del contenido:
- Descripciones únicas, ≤1024 caracteres, con «Usar cuando», «No usar» y límite explícito de uso como generador.
- Secciones obligatorias en cada skill: `Objetivo`, `Criterios de decisión`, `Antipatrones`, `Salida` y `Autoevaluación`.
- Orientación a arquitectura: ni las instrucciones ni las skills contienen pautas de desarrollo («archivos completos», «copiables», «árbol de archivos»); las instrucciones declaran el rol de asesor, los modos Rápido/Estándar/Completo, las preguntas aclaratorias, «Pendiente de verificar», la matriz de decisión y el ADR.
- Sin contenido duplicado entre skills ni el bloque de reglas genérico de la versión anterior.
- Conceptos clave por skill (BFF, PKCE, SSR, LCP, WCAG, zoneless, `ng update`, strangler, etc.).
- 24 escenarios de enrutamiento: la skill esperada contiene el disparador en su descripción.
- `test-prompts.md` con 20 prompts o más y al menos uno por skill.
- Al menos una plantilla o checklist por skill, referenciada desde `SKILL.md`, existente, sin codificación corrupta ni pautas de desarrollo, e incluida en el ZIP.
- Máximo de 3 preguntas aclaratorias en las instrucciones, igual que en los demás agentes.
- Recursos compartidos con otros agentes (`decision_matrix.py`, `eu-regulatory-map.md`) idénticos byte a byte; prueba de humo del script si hay Python.

## Recursos por skill
| Skill | Recurso |
|---|---|
| architecture-assessment | `templates/assessment-report.md` |
| architecture | `reference/microfrontends-readiness.md` |
| reactivity-state | `templates/state-map.md` |
| rendering-performance | `templates/rendering-strategy.md` |
| quality-security | `reference/production-readiness-checklist.md`, `reference/eu-regulatory-map.md` |
| backend-integration | `reference/integration-contract-checklist.md` |
| liferay-integration | `templates/custom-element-contract.md` |
| modernization-governance | `templates/upgrade-plan.md`, `templates/adr-template.md`, `scripts/decision_matrix.py` |

## Cambios respecto a la versión anterior
- Las ocho skills eran plantillas de ~1300 caracteres con el mismo bloque de reglas y orientación a implementación («Entrega código… copiables», «archivos completos»). Se reescribieron como skills de decisión: criterios, matrices, antipatrones, salida y autoevaluación propios.
- `angular-development` (implementación de componentes, forms, HTTP) se sustituyó por `angular-modernization-governance`; sus decisiones de diseño se repartieron entre `angular-architecture`, `angular-reactivity-state` y `angular-backend-integration`.
- `backend-integration` y `diagnostics-devops-review` se renombraron a `angular-backend-integration` y `angular-architecture-assessment` (prefijo común y foco en evaluación).
- Instrucciones reescritas con el mismo esquema que los agentes de Spring Boot y NestJS: rol de asesor, contexto sin acceso al repositorio, proporcionalidad, reglas de decisión, plantillas, formato completo, enrutamiento y límites. Se movieron de `agent/` a `AGENT_INSTRUCTIONS.md`.
- `TEST-CASES.md` (6 frases sin criterio) pasó a `validation/test-prompts.md` con 24 prompts, resultado esperado y criterio de fallo.
- Después: lectura del repositorio cuando hay acceso (VS Code), funcionalidades con IA generativa (BFF, streaming) y presentación segura del contenido generado, mapa de normativa UE, script `decision_matrix.py`. Prompts 25 a 28.

## Limitaciones
- Validación estática: comprueba estructura y contenido, no la calidad de las respuestas.
- No se ha ejecutado en un tenant de Microsoft 365 Copilot; la selección de skills depende de Agent Builder: usa `validation/test-prompts.md`.
- Las APIs de Angular cambian de estado (experimental, developer preview, estable) entre versiones; las skills obligan a verificarlas, no fijan versiones.
- Durante la preview no se pueden combinar skills con archivos embebidos.

## Riesgos abiertos
- `angular-architecture` es la skill más amplia (estructura, routing, i18n, design system, microfrontends). Si se invoca peor, mueve i18n y design system a la descripción de otra skill antes de crear una novena (el límite es 8).
- Solapamiento entre `angular-liferay-integration` y el agente Liferay: la regla es que Angular diseña la aplicación y Liferay decide mecanismo, OAuth2 y permisos.
