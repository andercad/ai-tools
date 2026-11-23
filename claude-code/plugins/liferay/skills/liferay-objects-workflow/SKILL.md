---
name: liferay-objects-workflow
description: 'Liferay DXP. Objects y Workflow: modelos de datos sin código (campos, picklists, relaciones, validaciones, reglas de estado, acciones, permisos), APIs headless generadas, definiciones desplegadas como código con batch, Liferay Forms, y definiciones Kaleo (estados, tareas, transiciones, asignaciones, notificaciones), acciones como client extension. Usar para crear una entidad o modelo de datos nuevo, añadir campos o relaciones, ejecutar lógica al crear o actualizar un registro, exponer datos por API, construir un formulario, crear flujos de aprobación o asignar revisores. No usar para mantener entidades de Service Builder existentes (liferay-osgi).'
---

# Objects y Workflow

## Reglas clave
- Entidad nueva = Object por defecto; ERC estables y legibles (`acme-order-status-picklist`).
- Definiciones, picklists, acciones y workflow se despliegan desde el repositorio (config como código), no a mano en cada entorno.
- Lógica ante eventos con client extensions (acciones y validaciones), no con scripts incrustados.
- Define permisos del Object y comprueba el volumen antes de elegir campos indexados o relaciones.

## Referencias
| Tema | Fichero |
|---|---|
| Definición, objects como código, APIs, lógica, Forms | [objects.md](references/objects.md) |
| Definiciones Kaleo, acciones, workflow como código | [workflow.md](references/workflow.md) |

## Checklists
### Definición
- [ ] Nombre y ámbito (company/site) decididos antes de publicar
- [ ] ERC estables en definiciones, campos, picklists y registros migrados
- [ ] Permisos por rol; *account restriction* si aplica
- [ ] Definición desplegada como código (batch o site initializer), no creada a mano
- [ ] Lógica externa como acción o validación de client extension, con JWT validado e idempotencia
- [ ] Contrato de la API comprobado en el API Explorer

### Definiciones Kaleo
- [ ] Flujo mínimo que cumple el requisito, diseñado en el editor visual
- [ ] Asignaciones a roles; notificaciones traducidas; temporizadores si hay plazos
- [ ] Definición basada en la exportada por la versión del proyecto
- [ ] Lógica externa en acciones de workflow como client extension; scripts mínimos
- [ ] Definiciones versionadas y desplegadas como código
