---
name: liferay-platform-customization
description: 'Asesoría arquitectónica sobre el diseño de customizaciones de plataforma en Liferay DXP: modelado con Objects (campos, relaciones, validaciones, acciones, permisos, API generada), módulos OSGi y SPI, Service Builder, Workflow, transacciones, eventos internos y su impacto en upgrades. Usar cuando se pida diseñar un modelo de datos en Liferay, decidir entre Objects y Service Builder, diseñar un módulo OSGi o un workflow, o evaluar los límites y el coste de una customización interna. No usar para elegir el mecanismo global de la solución, para integraciones externas ni como generador de código.'
---

# Customización de plataforma: Objects, OSGi, Service Builder y Workflow

## Objetivo
Diseñar modelos de datos y extensiones internas del portal con el menor acoplamiento posible, permisos y transacciones claros, y un coste de upgrade explícito.

## Criterios de decisión: Objects frente a Service Builder
| Criterio | Objects | Service Builder |
|---|---|---|
| Modelo administrativo simple o medio | Recomendado | Sobredimensionado |
| API REST/GraphQL generada y permisos integrados | Incluido | Hay que construirlo |
| Disponible en SaaS | Sí | No |
| Invariantes complejas y transacciones entre varias entidades | Limitado: evalúa | Adecuado |
| Consultas complejas o alto volumen | Mide y verifica límites | Control total |
| Coste de upgrade | Bajo | Alto |
Si el dominio es complejo y transaccional, valora también un servicio externo con su propia base de datos integrado por Headless antes que Service Builder.

## Diseño con Objects
- Define campos, relaciones, listas de selección, validaciones y acciones; el alcance (compañía o site) condiciona permisos y reutilización.
- Acciones de Objects hacia Client Extensions o webhooks para lógica externa; considera entrega al menos una vez e idempotencia.
- Permisos por rol y por entrada; no confíes en ocultar la UI.
- Planifica la evolución del esquema: cambios de campos y relaciones con datos existentes.
- Verifica capacidades (campos calculados, agregaciones, validaciones con expresiones o scripts) en la release.

## Módulos OSGi
- Solo para SPI, ciclo de vida o capacidades internas no externalizables.
- Usa puntos de extensión públicos; evita overrides de JSP o servicios internos y fragmentos de módulo salvo necesidad documentada.
- Declara dependencias con rangos de versión semánticos y minimiza dependencias de paquetes internos.
- Cada módulo con responsabilidad única y configuración OSGi externa.
- Indica el coste de upgrade de cada punto de extensión.

## Service Builder
Solo para persistencia interna con dominio complejo y en modalidades que lo permiten. Define límites transaccionales en la capa de servicio, permisos con el modelo de Liferay, índices de búsqueda si aplica y migraciones de esquema con procesos de upgrade. Nunca accedas a tablas de Liferay desde fuera de sus servicios.

## Workflow
- Usa el motor de workflow para aprobaciones; define estados, roles asignados, plazos y escalados.
- Acciones de workflow hacia Client Extensions para lógica externa.
- Versiona las definiciones y prueba recorridos completos, incluida la reasignación y el rechazo.

## Antipatrones
- Objects como sustituto universal de un dominio complejo.
- Service Builder para modelos que Objects cubre.
- Acceso directo a tablas de Liferay o SQL contra su esquema.
- Lógica de negocio pesada dentro de la JVM del portal sin justificación.
- Overrides de JSP como mecanismo habitual.

## Salida
Usa `templates/object-model.md` para el modelo de datos.
Decisión de mecanismo con matriz, modelo de datos (diagrama de entidades y relaciones), permisos por rol, frontera transaccional, workflow, puntos de extensión e impacto en upgrade, plan de pruebas, riesgos y ADR.

## Autoevaluación
¿He descartado Objects o un servicio externo con motivo antes de usar Service Builder? ¿Cada ejecución en la JVM está justificada? ¿Los permisos están en el servidor? ¿He evitado APIs internas y tablas? ¿He estimado el coste de upgrade?
