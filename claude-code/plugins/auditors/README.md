# Plugin Auditors para Claude Code

Agentes auditores de **solo lectura** para cualquier proyecto web. Proponen correcciones, nunca las aplican, y guardan su estado en `references/` del proyecto.

## Qué incluye
- **`lighthouse-auditor`**: informe como el de Lighthouse de Chrome, con score oficial 0-100 de Rendimiento, Accesibilidad, Prácticas recomendadas, SEO y Navegación agéntica (Lighthouse CLI), en mobile y desktop. Lo complementa con la traza de rendimiento, la consola y el árbol de accesibilidad (Chrome DevTools MCP). Con dos apps compara paridad. Memoria: `references/lighthouse/lighthouse-audit.md`.
- **`security-auditor`**: audita código, configuración, dependencias y BD (autodetecta el proveedor) contra las normas del proyecto o, si no hay, contra el checklist genérico. Memoria: `references/security/security-audit.md`.
- **Skill `security-checklist`** (no invocable, precargada en `security-auditor`): checklist genérico con IDs estables (`SEC-xx`, `DB-xx`…). Si el proyecto tiene `references/security/security-checklist.md`, prevalece.

## Requisitos
- **Node/npx**, para `npx lighthouse@latest`, y **Chrome** instalado.
- **Chrome DevTools MCP** (plugin `chrome-devtools-mcp`) para la traza, la consola y el snapshot de `lighthouse-auditor`. Los nombres de herramienta del agente asumen `mcp__plugin_chrome-devtools-mcp_chrome-devtools__*`; si lo instalas con otro nombre, ajusta `tools` en `agents/lighthouse-auditor.md`.
- Permiso de `Bash` para `curl` y `npx` (lo usa `lighthouse-auditor`).

## Instalación
```bash
claude plugin marketplace add ./claude-code      # desde la raíz de este repo
claude plugin install auditors@ai-tools
```
Prueba sin instalar: `claude --plugin-dir claude-code/plugins/auditors`.

### Actualización
```bash
claude plugin marketplace update ai-tools
claude plugin update auditors@ai-tools
```
Reinicia Claude Code para aplicar.

## Uso
Los agentes se invocan por nombre o por su descripción ("auditoría lighthouse", "audita la seguridad"). Lanza `lighthouse-auditor` con la app en ejecución; si no responde, marca los checks como "no verificado".

## Regla de proyecto
Los plugins no distribuyen reglas (`rules/`), así que `security-auditor` crea `.claude/rules/security-auditor.md` en el proyecto la primera vez que se ejecuta, con una regla genérica (propone lanzarlo tras tocar auth, migraciones, config, secretos o dependencias). Si ya existe no la toca: amplíala a mano (`paths`, viñetas).

## Mantenimiento (desarrolladores)
Tras editar el plugin, sube `version` en `.claude-plugin/plugin.json`: sin cambio de versión, Claude Code usa la caché. Después valida, haz commit/push y avisa al equipo.

```bash
claude plugin validate claude-code/plugins/auditors
```

## Origen del contenido
Los agentes viven solo en el plugin (se eliminaron los sueltos de `claude-code/.claude/agents/`).
