---
name: liferay-content-search
description: 'Asesoría arquitectónica sobre contenido, experiencia y búsqueda en Liferay DXP: modelo de contenido (Liferay CMS con espacios y estructuras, Web Content clásico, Objects como contenido), capacidades en maintenance mode o deprecadas, sites y páginas, Fragments, Style Books y plantillas maestras, taxonomía (vocabularios, categorías, etiquetas), Document Library y DAM, previews y procesadores de documentos, Publications, staging y publicación, multi-idioma, y búsqueda con Elasticsearch u OpenSearch (topología, índices, reindexación, relevancia, búsqueda semántica). Usar cuando se pregunte cómo modelar y gobernar contenido, si usar el nuevo CMS o el contenido clásico, cómo organizar sites y páginas, cómo publicar entre entornos o cómo diseñar, dimensionar o diagnosticar la búsqueda. No usar como generador de código ni para permisos o SSO.'
---

# Contenido, experiencia y búsqueda

## Objetivo
Diseñar un modelo de contenido gobernable, separar contenido de presentación, definir la publicación y asegurar una búsqueda compatible, dimensionada y recuperable.

## Criterios de decisión: modelo de contenido
| Necesidad | Opción | Cuidado con |
|---|---|---|
| Contenido estructurado nuevo, reutilizable en varios canales | Liferay CMS: espacios y estructuras de contenido y de fichero, basado en Objects, con workflow por estructura | GA desde 2026.Q3; verifica capacidades y modalidad en la release del cliente |
| Contenido editorial existente | Web Content con estructuras (clásico) | En maintenance mode desde 2026.Q1: soportado, sin evolución funcional; planifica la transición |
| Datos estructurados con API y reglas | Objects | No es un CMS editorial completo; valida el flujo editorial |
| Composición visual por editores | Content Pages con Fragments | Gobierno de Fragments, rendimiento; las Widget Pages están deprecadas desde 2026.Q3 (hay conversor) |
| Ficheros y activos | Tipos de fichero del CMS o Documents and Media | Documents and Media en maintenance mode desde 2026.Q1; almacenamiento, tamaño, previews |
Separa contenido (estructura) de presentación (plantillas, Fragments, Style Books). Define dueños, ciclo de vida y caducidad.

## Estado de las capacidades
Desde 2026.Q1, Web Content, Blogs, Documents and Media, Knowledge Base, Asset Libraries y Publications están en maintenance mode y Liferay propone el Liferay CMS, utilizable en paralelo con el contenido clásico. En 2026.Q3 se deprecaron, entre otros, las Widget Pages y sus plantillas, y el soporte de Apache OpenOffice (sustituido por LibreOffice). Comprueba el estado en las notas de la release del cliente y no recomiendes capacidades en maintenance mode o deprecadas para proyectos nuevos sin un motivo explícito.

## Sites y experiencia
- Decide número de sites por audiencia, marca, idioma o gobierno, no por departamento interno.
- Plantillas maestras y Style Books para coherencia; Fragments reutilizables en colecciones gobernadas y versionadas.
- Multi-idioma: idioma por defecto, fallback y traducción (manual o servicio).
- Accesibilidad incorporada en Fragments y plantillas.
- Personalización por segmentos: la creación local de segmentos en DXP está deprecada desde 2026.Q1 y Liferay propone Analytics Cloud; verifica licencia y modalidad.

## Taxonomía
Vocabularios y categorías globales o por site, etiquetas con criterio limitado, dueños de la taxonomía y uso en navegación, búsqueda y personalización.

## Document Library
- En proyectos nuevos, evalúa los tipos de fichero del Liferay CMS antes que Documents and Media.
- Almacén compartido entre nodos (sistema de ficheros compartido u objeto compatible); nunca disco local en cluster.
- Previews y miniaturas dependen de procesadores externos (por ejemplo, LibreOffice, ImageMagick, Ghostscript; el soporte de Apache OpenOffice está deprecado desde 2026.Q3): dimensiona su coste y aíslalo; no atribuyas un fallo de previews sin correlacionar logs.
- Política de tamaño, tipos permitidos, antivirus y retención.

## Staging y publicación
| Opción | Encaja cuando | Cuidado con |
|---|---|---|
| Workflow y versionado del CMS | Contenido gestionado en el Liferay CMS | Publications no rastrea los cambios del CMS |
| Publicación directa con workflow | Equipos pequeños, cambios frecuentes | Revisión antes de publicar |
| Publications | Agrupar, revisar y revertir cambios de páginas y contenido clásico entre sites | Maintenance mode desde 2026.Q1 sin reemplazo directo; no cubre Objects |
| Local staging | Preparar sites completos en el mismo entorno | Liferay recomienda Publications salvo autoría y producción separadas; no cubre Objects |
| Remote Live staging | Autoría y producción en servidores distintos (única opción para ello) | Operación, red, versiones idénticas |
Verifica el estado de cada capacidad en la release; elige la más simple.

## Búsqueda
- Motor externo (remote) en producción; el modo embebido o sidecar solo para desarrollo. Verifica en la Compatibility Matrix la versión exacta de Elasticsearch u OpenSearch soportada por la release.
- Dimensiona nodos, shards y réplicas según volumen y SLO; protege el clúster de búsqueda con autenticación y TLS.
- Reindexación: planificada, por tipo de entidad cuando sea posible, con impacto medido y ventana definida. No borres índices ni reindexes masivamente sin plan y rollback.
- Relevancia: blueprints o configuración de búsqueda, sinónimos y pruebas con consultas reales.
- Búsqueda semántica o vectorial: verifica que la release, la licencia y la versión del motor la soportan; los resultados deben respetar los permisos del usuario.
- Los índices son reconstruibles desde la base de datos: cuenta con ello en DR, pero mide el tiempo de reconstrucción.

## Antipatrones
- Una estructura de Web Content por página.
- Proyectos nuevos sobre capacidades en maintenance mode o deprecadas (Web Content, Documents and Media, Publications, Widget Pages) sin evaluar el Liferay CMS ni documentar el motivo.
- Código para lo que resuelven plantillas, Fragments o configuración.
- Document Library en disco local de un nodo.
- Búsqueda embebida en producción; reindexaciones masivas sin plan.
- Taxonomía sin dueño.

## Salida
Usa `templates/content-model.md` para el modelo de contenido y la búsqueda.
Modelo de contenido y dueños, mapa de sites y páginas, taxonomía, estrategia de publicación, topología de búsqueda y reindexación, almacenamiento de documentos, plan operativo, validación, rollback y ADR.

## Autoevaluación
¿El contenido está separado de la presentación? ¿Cada pieza tiene dueño? ¿He verificado si las capacidades recomendadas están en maintenance mode o deprecadas? ¿La versión del motor de búsqueda está verificada? ¿Hay plan de reindexación y de reconstrucción en DR? ¿He elegido la opción de publicación más simple?
