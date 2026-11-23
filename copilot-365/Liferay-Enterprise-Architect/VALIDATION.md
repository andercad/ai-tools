# Validación

## Resultado de las comprobaciones estáticas
Ejecutadas con `validation/validate.ps1 -Build`: **455 comprobaciones superadas, 0 fallos** (456 cuando hay Python disponible y se ejecuta la prueba de humo del script).

Límites de Agent Builder ([Custom skills in declarative agents](https://learn.microsoft.com/microsoft-365/copilot/extensibility/declarative-agent-skills)):
- Instrucciones del agente: 7090 caracteres (límite 8000).
- 8 skills (límite 8 por agente).
- `SKILL.md` de menos de 20.000 caracteres, con `name` y `description` en el front matter.
- ZIP de 50 MB o menos, con `SKILL.md` en la raíz, tipos de archivo soportados, profundidad 3 o menos y 350 archivos o menos.

Calidad del contenido:
- Descripciones únicas, ≤1024 caracteres, con «Usar cuando», «No usar» y límite explícito de uso como generador.
- Secciones obligatorias en cada skill: `Objetivo`, `Criterios de decisión`, `Antipatrones`, `Salida` y `Autoevaluación`.
- Orientación a arquitectura: ni las instrucciones ni las skills contienen pautas de desarrollo; las instrucciones declaran el rol de asesor, los modos Rápido/Estándar/Completo, las preguntas aclaratorias, «Pendiente de verificar», la matriz de decisión y el ADR.
- Sin contenido duplicado entre skills ni el bloque de reglas genérico de la versión anterior.
- Conceptos clave por skill (escalera de mecanismos, dentro o fuera de la JVM, idempotencia, Compatibility Matrix, go/no-go, Service Access Policies, etc.).
- 24 escenarios de enrutamiento: la skill esperada contiene el disparador en su descripción.
- `test-prompts.md` con 20 prompts o más y al menos uno por skill.
- Al menos una plantilla o checklist por skill, referenciada desde `SKILL.md`, existente, sin codificación corrupta ni pautas de desarrollo, e incluida en el ZIP.
- Máximo de 3 preguntas aclaratorias en las instrucciones, igual que en los demás agentes.
- Recursos compartidos con otros agentes (`decision_matrix.py`, `eu-regulatory-map.md`) idénticos byte a byte; prueba de humo del script si hay Python.

## Recursos por skill
| Skill | Recurso |
|---|---|
| architecture-assessment | `templates/assessment-report.md` |
| solution-architecture | `templates/adr-template.md`, `scripts/decision_matrix.py` |
| client-extensions-integration | `reference/integration-checklist.md` |
| platform-customization | `templates/object-model.md` |
| content-search | `templates/content-model.md` |
| security-identity | `templates/permissions-matrix.md`, `reference/eu-regulatory-map.md` |
| cloud-operations | `reference/production-readiness-checklist.md` |
| version-upgrade | `templates/upgrade-assessment.md` |

## Cambios respecto a la versión anterior
- Las ocho skills eran plantillas de ~1300 caracteres con el mismo bloque de reglas y orientación a implementación. Se reescribieron como skills de decisión con criterios, matrices, antipatrones, salida y autoevaluación propios.
- `liferay-platform-development` pasó a `liferay-platform-customization` y `liferay-diagnostics-review` a `liferay-architecture-assessment` (foco en diseño y evaluación, con inventario de customizaciones y coste de upgrade).
- Se añadió de forma explícita la escalera de mecanismos (configuración → low-code → Client Extensions → servicio externo → OSGi → Service Builder) y las restricciones por modalidad (self-hosted, PaaS, SaaS).
- Instrucciones reescritas con el mismo esquema que los agentes de Spring Boot y NestJS y movidas de `agent/` a `AGENT_INSTRUCTIONS.md`.
- `TEST-CASES.md` (6 frases sin criterio) pasó a `validation/test-prompts.md` con 24 prompts, resultado esperado y criterio de fallo.
- Actualización 2026 contrastada con learn.liferay.com: Liferay CMS (GA en 2026.Q3), capacidades en maintenance mode desde 2026.Q1 (Web Content, Blogs, Documents and Media, Knowledge Base, Asset Libraries, Publications), segmentos locales deprecados en 2026.Q1 y deprecaciones de 2026.Q3 (Widget Pages, Apache OpenOffice). Prompt 25 añadido.
- Después: lectura del repositorio cuando hay acceso (VS Code), integración con IA generativa fuera de la JVM con RAG que respeta permisos, búsqueda semántica, mapa de normativa UE, script `decision_matrix.py`. Prompts 26 a 28.

## Limitaciones
- Validación estática: comprueba estructura y contenido, no la calidad de las respuestas.
- No se ha ejecutado en un tenant de Microsoft 365 Copilot; usa `validation/test-prompts.md`.
- Los tipos de Client Extension, las capacidades de Objects, las versiones de motor de búsqueda soportadas y las restricciones de PaaS y SaaS cambian entre releases: las skills obligan a verificarlas en learn.liferay.com y en la Compatibility Matrix; no fijan valores.
- Durante la preview no se pueden combinar skills con archivos embebidos.

## Riesgos abiertos
- Solapamiento entre `liferay-solution-architecture` (elige el mecanismo) y `liferay-platform-customization` (diseña el mecanismo elegido). Si el enrutamiento falla, refuerza «elegir» frente a «diseñar» en sus descripciones.
- Fuera de alcance deliberadamente: Liferay Commerce, Analytics Cloud y personalización avanzada. Añadir solo si aparecen en uso real.
