# NestJS Architecture Advisor

Agente para Microsoft 365 Copilot (Agent Builder) orientado a arquitectura NestJS/Node.js, no a desarrollo cotidiano.

## Contenido
- `AGENT_INSTRUCTIONS.md`: instrucciones del agente (menos de 8000 caracteres, límite de Agent Builder).
- `skills/`: fuentes de las ocho skills (el máximo permitido por agente). Cada una incluye una plantilla o checklist en `templates/` o `reference/`, que el agente carga solo cuando la necesita. `nestjs-modernization-governance` incluye además el script `scripts/decision_matrix.py`.
- `skill-packages/`: un ZIP por skill, listos para subir (`SKILL.md` en la raíz, más sus recursos).
- `validation/validate.ps1`: validación estática. `-Build` regenera los ZIP.
- `validation/test-prompts.md`: 25 prompts para probar el enrutamiento y el comportamiento en el tenant.
- `VALIDATION.md`: estado de la validación y limitaciones.

## Skills
| Skill | Ámbito |
|---|---|
| `nestjs-architecture-assessment` | Revisión y diagnóstico de arquitecturas existentes |
| `nestjs-modularity-domain` | Módulos, hexagonal, monolito modular, microservicios, monorepo |
| `nestjs-api-integration` | REST, GraphQL, OpenAPI, webhooks, integraciones, IA generativa |
| `nestjs-data-messaging` | ORM, transacciones, migraciones, caché, brokers, outbox |
| `nestjs-security-identity` | Identidad, autorización, OWASP, secretos, IA generativa, normativa UE |
| `nestjs-runtime-deployment` | Node, contenedores, plataformas, probes, CI/CD |
| `nestjs-observability-resilience` | SLO, OpenTelemetry, rendimiento, resiliencia, cuotas y coste de IA |
| `nestjs-modernization-governance` | Upgrades, migraciones, ADR, quality gates, NestJS frente a Spring Boot, matriz de decisión |

## Instalación
Requisitos: las skills en Agent Builder están en preview y solo se ofrecen a organizaciones del programa Microsoft Frontier. No están disponibles en tenants con Microsoft Purview Information Barriers.

1. Crea el agente y pega `AGENT_INSTRUCTIONS.md` en sus instrucciones.
2. En **Configure > Skills > Add**, sube los ocho ZIP de `skill-packages/` (uno por skill, con `SKILL.md` en la raíz del ZIP).
3. Conocimiento: **no subas archivos embebidos**. Durante la preview, un agente no puede combinar skills y archivos embebidos. Usa en su lugar:
   - Sitios de SharePoint con tus estándares, ADR existentes, guías de seguridad y catálogo de plataformas.
   - Sitios web públicos de referencia, como `docs.nestjs.com`, `nodejs.org/en/about/previous-releases` y `owasp.org/API-Security`, para fundamentar versiones y compatibilidades.
   No pongas instrucciones en esos documentos: el contenido de conocimiento no se trata como instrucciones del agente.
4. Añade las sugerencias de conversación de abajo.
5. Prueba los prompts de `validation/test-prompts.md` en la pestaña **Try it** y registra los resultados.

## Sugerencias de conversación
- Revisa la arquitectura de mi aplicación NestJS (te pego package.json y la estructura de módulos).
- ¿Monolito modular o microservicios para mi caso?
- ¿REST o GraphQL para web y móvil?
- Diseña la autenticación con Entra ID para una SPA y una API NestJS.
- ¿Cómo publico eventos de forma fiable al guardar en la base de datos?
- Redacta un ADR para actualizar NestJS y Node a la última LTS.

## GitHub Copilot en VS Code
Las mismas skills sirven para GitHub Copilot en VS Code (formato Agent Skills). No hay script de empaquetado en este repo: copia cada carpeta de `skills/<skill>` a `.github/skills/` del repositorio que quieras analizar (o a `~/.copilot/skills` para uso personal) y usa `AGENT_INSTRUCTIONS.md` como contenido de un agente en `.github/agents/`.
- En VS Code el agente lee el repositorio, así que la evaluación parte de ficheros reales y no de supuestos.
- Solo tiene herramientas de lectura, búsqueda y web: no edita ficheros ni ejecuta comandos. Si necesitas la matriz de decisión calculada, ejecuta `decision_matrix.py` o pide el cálculo paso a paso.
- Los botones para pasar la conversación a otro de los cuatro agentes (handoffs) solo están disponibles en el harness Local.

## Mantenimiento
Edita siempre `skills/` y luego ejecuta `powershell -File validation\validate.ps1 -Build` para regenerar los ZIP y validar. No edites los ZIP a mano.

## Diseño
- Agente asesor: no implementa, no despliega y no modifica sistemas. Tiene tres modos de respuesta (Rápido, Estándar, Completo) para evitar respuestas largas a preguntas simples.
- Sin acceso al repositorio (Microsoft 365): el agente pide `package.json`, versiones y estructura, y marca los supuestos. Con acceso (VS Code), lee esos ficheros primero.
- Cada skill aporta criterios de decisión, antipatrones, salida y autoevaluación propios. El flujo común vive en las instrucciones del agente.
