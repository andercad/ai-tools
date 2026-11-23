---
name: liferay-testing-quality
description: 'Liferay DXP. Tests y calidad: unitarios con JUnit y Mockito (módulos -test), integración con Arquillian (testIntegration) contra un Liferay en ejecución, tests de APIs headless y client extensions, Playwright; Source Formatter (formatSource, checkSourceFormatting), convenciones de Liferay, baseline de bnd y versionado semántico, SonarQube, dependencias de terceros y checklist pre-PR. Usar al escribir o arreglar tests, formatear código, corregir avisos de Source Formatter o SonarQube, cambiar la API exportada de un módulo o revisar un PR. No usar para diagnosticar incidencias en runtime (liferay-config-operations).'
---

# Testing y calidad

## Reglas clave
- Unitarios con JUnit/Mockito en el propio módulo o en un módulo `-test`; integración con Arquillian (`testIntegration`) solo cuando haga falta un Liferay real.
- Cada test sigue la política `tests`/`it` del `CLAUDE.md` del proyecto.
- Cambios en paquetes exportados: respeta el baseline de bnd y el versionado semántico.
- Si `format: source-formatter`, ejecuta `formatSource` del módulo antes de dar el paso por terminado.

## Referencias
| Tema | Fichero |
|---|---|
| Unitarios, Arquillian, APIs, client extensions, Playwright | [testing.md](references/testing.md) |
| Source Formatter, convenciones, baseline, SonarQube, pre-PR | [quality.md](references/quality.md) |

## Checklists
### Unitarios
- [ ] Tipo de test de menor alcance suficiente
- [ ] Lógica extraída y probada sin contenedor cuando sea posible
- [ ] Integración con Arquillian para servicios y permisos, con utilidades de la versión
- [ ] APIs probadas con 200/401/403/404 y validación
- [ ] Microservicios probados con JWT inválido e idempotencia
- [ ] E2E solo para flujos críticos, con datos reproducibles y selectores estables
