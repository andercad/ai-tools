---
name: liferay-search
description: 'Liferay DXP. Búsqueda: conexión con Elasticsearch u OpenSearch en modo remoto (producción) frente al modo de desarrollo, versiones soportadas, reindexado, contribuidores de documentos de índice para entidades propias (módulos -indexer), Search Blueprints, sinónimos, rankings de resultados, widgets de búsqueda y facetas, y búsqueda con permisos. Usar cuando: configurar el motor de búsqueda, los resultados no aparecen o están desactualizados, reindexar, añadir campos al índice, ajustar la relevancia de los resultados, construir una página de búsqueda.'
---

# Búsqueda

## Motor de búsqueda

- **Producción**: Elasticsearch u OpenSearch **remoto**, en una versión soportada por tu versión de Liferay (consulta la matriz de compatibilidad). El modo de desarrollo (sidecar o embebido) **no** es para producción.
- La conexión se configura con el `.config` del conector de tu versión (exporta la configuración desde System Settings para obtener el PID exacto) o, en PaaS, con el servicio `search` (ver `liferay-config-operations`). En SaaS lo gestiona Liferay.
- Credenciales y certificados por variables de entorno o secretos, no en el repositorio.
- En clúster, todos los nodos de Liferay apuntan al mismo motor.

## Reindexado

- Desde Control Panel → Search → Index Actions: reindexar todo o por tipo de entidad.
- Reindexa tras restaurar una base de datos, tras un upgrade si la guía lo indica, o al cambiar la configuración del índice.
- En instalaciones grandes, reindexa por tipos y fuera de horas de carga; vigila memoria y tiempo.
- Si los resultados están desactualizados, comprueba primero la conexión y los logs antes de reindexar.

## Entidades propias en el índice (módulos `-indexer`)

**Requiere módulos OSGi: no disponible en SaaS.**

```java
@Component(
	property = "indexer.class.name=com.acme.orders.model.AcmeOrder",
	service = ModelDocumentContributor.class
)
public class AcmeOrderModelDocumentContributor implements ModelDocumentContributor<AcmeOrder> {

	@Override
	public void contribute(Document document, AcmeOrder acmeOrder) {
		document.addKeyword(Field.STATUS, acmeOrder.getStatus());
		document.addText("reference", acmeOrder.getReference());
		document.addDate(Field.MODIFIED_DATE, acmeOrder.getModifiedDate());
	}

}
```

- Para entidades de Service Builder, registra la búsqueda con los contribuidores del framework de búsqueda (*model search registrar*, contribuidores de documento, consulta y resumen); copia la estructura de un módulo de Liferay de tu versión.
- Los **Objects** se indexan automáticamente: configura en cada campo si es buscable o indexable.
- `addKeyword` para valores exactos (filtros, facetas), `addText` para texto completo.
- No añadas al índice datos sensibles que no deban aparecer en búsquedas.

## Relevancia y experiencia de búsqueda

- **Search Blueprints**: ajustan la consulta (boost por categorías, recencia, filtros por site...) sin código. Versiona sus definiciones exportándolas.
- **Sinónimos** por idioma y **rankings de resultados** (fijar u ocultar resultados para una consulta).
- Página de búsqueda con los widgets de búsqueda: barra, resultados, facetas (categorías, tipo, fecha, campos propios), sugerencias.
- Los resultados **se filtran por permisos** del usuario: no hace falta (ni conviene) filtrar a mano.

## Checklist

- [ ] Motor remoto en versión soportada; sin modo de desarrollo en producción
- [ ] Conexión con el `.config` del conector de la versión; credenciales en secretos
- [ ] Reindexado planificado tras restauraciones, upgrades o cambios de índice
- [ ] Entidades propias con contribuidores del framework de la versión; Objects con campos indexables configurados
- [ ] Relevancia con Search Blueprints, sinónimos y rankings, versionados
