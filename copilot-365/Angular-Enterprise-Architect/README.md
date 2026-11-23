# Angular Architecture Advisor

Agente para Microsoft 365 Copilot (Agent Builder) orientado a decisiones de arquitectura y diseño de frontends Angular, no a desarrollo cotidiano.

## Contenido
- `AGENT_INSTRUCTIONS.md`: instrucciones del agente (menos de 8000 caracteres, límite de Agent Builder).
- `skills/`: fuentes de las ocho skills (el máximo por agente). Editar aquí. Cada una incluye al menos una plantilla o checklist en `templates/` o `reference/`, que el agente carga solo cuando la necesita. `angular-modernization-governance` incluye además el script `scripts/decision_matrix.py`.
- `skill-packages/`: un ZIP por skill con `SKILL.md` en la raíz, listos para subir. No editar a mano.
- `validation/validate.ps1`: validación estática. `-Build` regenera los ZIP.
- `validation/test-prompts.md`: 28 prompts para probar enrutamiento y comportamiento en el tenant.
- `VALIDATION.md`: estado de la validación y limitaciones.

## Skills
| Skill | Ámbito |
|---|---|
| `angular-architecture-assessment` | Evaluación, deuda técnica, diagnóstico de problemas de arquitectura |
| `angular-architecture` | Estructura por features, límites, routing, i18n, design system, monorepo, microfrontends |
| `angular-reactivity-state` | Signals, RxJS, stores, estado de servidor, concurrencia, formularios |
| `angular-rendering-performance` | CSR/SSR/SSG, hydration, Web Vitals, hosting, entrega |
| `angular-quality-security` | Estrategia de pruebas, accesibilidad, seguridad del frontend, quality gates, contenido generado por IA, normativa UE |
| `angular-backend-integration` | BFF, OAuth2/OIDC, OpenAPI, errores y reintentos con Spring Boot y NestJS, IA generativa |
| `angular-liferay-integration` | Custom Element Client Extensions, Headless, convivencia en página |
| `angular-modernization-governance` | Upgrades, migraciones, AngularJS, ADR, fitness functions, matriz de decisión |

## Instalación
Requisitos: las skills en Agent Builder están en preview y solo se ofrecen a organizaciones del programa Microsoft Frontier.

1. Crea el agente y pega `AGENT_INSTRUCTIONS.md` en sus instrucciones.
2. En **Configure > Skills > Add**, sube los ocho ZIP de `skill-packages/`.
3. Conocimiento: durante la preview no se pueden combinar skills y archivos embebidos. Usa sitios de SharePoint (estándares, ADR, design system) y sitios web oficiales como `angular.dev`, `learn.liferay.com` y `learn.microsoft.com`.
4. Añade las sugerencias de conversación de abajo.
5. Ejecuta los prompts de `validation/test-prompts.md` y ajusta las `description` de las skills que no se invoquen bien.

## Sugerencias de conversación
- Evalúa la arquitectura de mi aplicación Angular (te pego `package.json` y el árbol de `src/app`).
- ¿Aplicación única, monorepo o microfrontends para nuestros equipos?
- ¿Necesitamos SSR o basta con CSR?
- ¿BFF o PKCE para autenticar nuestra SPA con Entra ID?
- ¿Cómo llevamos nuestra aplicación Angular a páginas de Liferay?
- Planifica el upgrade de Angular a la versión soportada actual.

## GitHub Copilot en VS Code
Las mismas skills sirven para GitHub Copilot en VS Code (formato Agent Skills). No hay script de empaquetado en este repo: copia cada carpeta de `skills/<skill>` a `.github/skills/` del repositorio que quieras analizar (o a `~/.copilot/skills` para uso personal) y usa `AGENT_INSTRUCTIONS.md` como contenido de un agente en `.github/agents/`.
- En VS Code el agente lee el repositorio, así que la evaluación parte de ficheros reales y no de supuestos.
- Solo tiene herramientas de lectura, búsqueda y web: no edita ficheros ni ejecuta comandos. Si necesitas la matriz de decisión calculada, ejecuta `decision_matrix.py` o pide el cálculo paso a paso.
- Los botones para pasar la conversación a otro de los cuatro agentes (handoffs) solo están disponibles en el harness Local.

## Mantenimiento
Edita siempre `skills/` y ejecuta:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File validation\validate.ps1 -Build
```

## Relación con otros agentes
Las decisiones internas de Liferay corresponden al agente Liferay; las del interior de los backends, a los agentes de Spring Boot y NestJS. Este agente define el contrato que necesita el frontend y remite.
