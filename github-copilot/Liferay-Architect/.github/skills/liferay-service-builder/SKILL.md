---
name: liferay-service-builder
description: 'Liferay DXP. Service Builder frente a Objects: cuándo una entidad nueva debe ser un Object y cuándo Service Builder, mantenimiento de módulos existentes (service.xml, buildService, LocalServiceImpl y ServiceImpl, finders, permisos de recurso, upgrade steps), consumo desde otros módulos con @Reference al LocalService, y migración a Objects. Usar cuando: crear una entidad o modelo de datos y dudar entre Objects y Service Builder, modificar una entidad de Service Builder, añadir una columna o un finder, regenerar servicios, migrar datos heredados a Objects.'
argument-hint: 'Describe la entidad, sus reglas de negocio y las restricciones del proyecto (microservicios permitidos, volumen, consultas).'
---

# Service Builder y Objects

**Service Builder no está disponible en Liferay SaaS.**

## Objects por defecto

Las entidades nuevas se crean con **Objects** (ver `liferay-objects`): API REST y GraphQL generada, permisos, workflow, búsqueda, formularios y exportación sin código, y funcionan en todos los modelos de despliegue.

Las client extensions de microservicio (acciones y validaciones de objeto, gestor de entradas) están disponibles en **todos** los modelos de despliegue: en SaaS las aloja Liferay; en self-hosted y PaaS las despliegas tú. Son la forma de añadir lógica a un Object sin código dentro del servidor.

## Cuándo usar Service Builder

Usa Service Builder cuando el Object **no pueda cubrir** el requisito. Criterios:

| Criterio | Ejemplo |
|---|---|
| Lógica de negocio que no se resuelve con acciones, validaciones ni microservicios | Reglas que deben ejecutarse dentro de la transacción de la entidad con otras entidades del servidor |
| El proyecto **no permite** microservicios externos y la lógica no cabe en las alternativas de abajo | Política del cliente |
| Consultas complejas o finders propios | Consultas SQL personalizadas, agregaciones, joins que la API del Object no ofrece |
| Transacciones que abarcan varias entidades propias | Alta de una cabecera y sus líneas con reglas cruzadas |
| Rendimiento medido con volúmenes altos | Mediciones reales, no suposiciones |
| Tablas de otro esquema o existentes | Integración con una base de datos heredada |

Si el proyecto prohíbe microservicios, antes de pasar a Service Builder valora (en self-hosted y PaaS):

- Acciones estándar de Objects: notificaciones, actualizar campos, webhooks.
- Validaciones con expresiones o con scripts Groovy, y acciones con scripts Groovy (solo administradores; revisa la política del proyecto sobre scripts).
- Model listeners sobre las entradas del Object (comprueba en tu versión que se admiten para Objects).

Documenta la decisión (por qué no Object) en el módulo o en la documentación del proyecto.

## Estructura

```
modules/<carpeta de Service Builder según guidelines>/orders/
  orders-api/       ← interfaces y modelos generados (exportados)
  orders-service/   ← service.xml, implementaciones (paquetes .service.impl), persistencia
```

```xml
<?xml version="1.0"?>
<!DOCTYPE service-builder PUBLIC "-//Liferay//DTD Service Builder 7.4.0//EN" "http://www.liferay.com/dtd/liferay-service-builder_7_4_0.dtd">

<service-builder dependency-injector="ds" package-path="com.acme.orders">
	<namespace>Acme</namespace>
	<entity local-service="true" name="Order" remote-service="true" uuid="true">
		<column name="orderId" primary="true" type="long" />
		<column name="groupId" type="long" />
		<column name="companyId" type="long" />
		<column name="userId" type="long" />
		<column name="createDate" type="Date" />
		<column name="modifiedDate" type="Date" />
		<column name="reference" type="String" />
		<column name="status" type="int" />
		<order by="desc">
			<order-column name="createDate" />
		</order>
		<finder name="GroupId" return-type="Collection">
			<finder-column name="groupId" />
		</finder>
	</entity>
</service-builder>
```

- Usa la **DTD de la versión** del proyecto (la que genera Blade) y `dependency-injector="ds"`.
- Columnas de auditoría (`groupId`, `companyId`, `userId`, fechas) y `uuid="true"` para exportación/importación y staging.
- Los cambios en `service.xml` requieren `./gradlew buildService` y, si cambian tablas existentes, un **upgrade step** (ver `liferay-upgrades`).

## Implementaciones y consumo

- La lógica va en `*LocalServiceImpl` (sin comprobación de permisos) y la API remota en `*ServiceImpl`, que **comprueba permisos** y delega en el local.
- **Nunca** modifiques las clases generadas (`*BaseImpl`, `*Persistence*`, modelos base): se sobrescriben al regenerar.
- **Consumo desde otros módulos**: inyecta el `*LocalService` (o el `*Service` remoto si actúa por un usuario) con `@Reference`, nunca con `*LocalServiceUtil`. La dependencia al módulo `-api`, con `compileOnly project(...)` (ver `liferay-workspace`).
- Permisos de recurso: `resource-actions` (`default.xml`) y `ModelResourcePermission` registrado como componente (ver `liferay-security`).
- Para exponer la entidad por API, prefiere **REST Builder** sobre los servicios JSON-WS generados (ver `liferay-headless`).

## Migrar a Objects

1. Crear el Object equivalente (campos, relaciones, permisos) como código (ver `liferay-objects`).
2. Migrar los datos con la API headless o batch del Object, no con SQL.
3. Sustituir los consumidores (portlets, plantillas) por los del Object.
4. Retirar el módulo de Service Builder y, si procede, eliminar sus tablas con un upgrade step.

Hazlo por entidades y con datos reales de prueba; mantén la compatibilidad mientras conviven ambos.

## Checklist

- [ ] Entidad nueva como Object, o Service Builder justificado con los criterios y documentado
- [ ] Alternativas sin microservicios valoradas si el proyecto los prohíbe
- [ ] DTD de la versión y `dependency-injector="ds"`
- [ ] Columnas de auditoría y `uuid`
- [ ] Lógica en `*LocalServiceImpl`; permisos en `*ServiceImpl`
- [ ] Consumo con `@Reference`, nunca `*LocalServiceUtil`
- [ ] Clases generadas sin modificar; cambios de esquema con upgrade step
