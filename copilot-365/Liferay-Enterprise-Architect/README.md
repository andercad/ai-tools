# Liferay Architecture Advisor

Agente para Microsoft 365 Copilot (Agent Builder) orientado a decisiones de arquitectura y diseño sobre Liferay DXP, no a desarrollo cotidiano.

## Contenido
- `AGENT_INSTRUCTIONS.md`: instrucciones del agente (menos de 8000 caracteres, límite de Agent Builder).
- `skills/`: fuentes de las ocho skills (el máximo por agente). Editar aquí. Cada una incluye al menos una plantilla o checklist en `templates/` o `reference/`, que el agente carga solo cuando la necesita. `liferay-solution-architecture` incluye además el script `scripts/decision_matrix.py`.
- `skill-packages/`: un ZIP por skill con `SKILL.md` en la raíz, listos para subir. No editar a mano.
- `validation/validate.ps1`: validación estática. `-Build` regenera los ZIP.
- `validation/test-prompts.md`: 28 prompts para probar enrutamiento y comportamiento en el tenant.
- `VALIDATION.md`: estado de la validación y limitaciones.

## Skills
| Skill | Ámbito |
|---|---|
| `liferay-architecture-assessment` | Evaluación, inventario de customizaciones, deuda, diagnóstico |
| `liferay-solution-architecture` | Selección de mecanismo, dentro o fuera de la JVM, modalidad, ADR, matriz de decisión |
| `liferay-client-extensions-integration` | Client Extensions, Headless, OAuth2, Angular, Spring Boot, NestJS, IA generativa |
| `liferay-platform-customization` | Objects, OSGi, Service Builder, Workflow |
| `liferay-content-search` | Liferay CMS y contenido clásico, sites, Fragments, Document Library, publicación, búsqueda semántica |
| `liferay-security-identity` | SSO, aprovisionamiento, roles y permisos, OAuth2, auditoría, IA generativa, normativa UE |
| `liferay-cloud-operations` | Modalidad, plataforma, cluster, rendimiento, observabilidad, DR |
| `liferay-version-upgrade` | Releases, LTS, compatibilidad, upgrades, feature flags |

## Instalación
Requisitos: las skills en Agent Builder están en preview y solo se ofrecen a organizaciones del programa Microsoft Frontier.

1. Crea el agente y pega `AGENT_INSTRUCTIONS.md` en sus instrucciones.
2. En **Configure > Skills > Add**, sube los ocho ZIP de `skill-packages/`.
3. Conocimiento: durante la preview no se pueden combinar skills y archivos embebidos. Usa sitios de SharePoint (estándares, ADR, inventario de customizaciones) y sitios web oficiales como `learn.liferay.com` (documentación, Compatibility Matrix, notas de release) y `learn.microsoft.com` si despliegas en Azure.
4. Añade las sugerencias de conversación de abajo.
5. Ejecuta los prompts de `validation/test-prompts.md` y ajusta las `description` de las skills que no se invoquen bien.

## Sugerencias de conversación
- Evalúa nuestra instalación Liferay y prioriza la deuda de customización.
- ¿Objects, Client Extension u OSGi para este requisito?
- ¿Cómo integramos un servicio Spring Boot o NestJS con Liferay?
- Diseña el SSO con Entra ID y el modelo de roles.
- ¿Self-hosted en AKS, PaaS o SaaS para nuestro caso?
- Planifica el upgrade a la LTS vigente.

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
El diseño interno del frontend Angular corresponde al agente Angular; el interior de los servicios, a los agentes de Spring Boot y NestJS. Este agente decide mecanismo, contrato con Liferay, OAuth2, permisos y despliegue.
