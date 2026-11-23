# Modelo de contenido y búsqueda: <portal>

## 1. Sites y espacios
| Site | Audiencia o marca | Idiomas | Dueño | Motivo de la separación |
|---|---|---|---|---|

| Espacio del CMS | Contenido | Estructuras disponibles | Permisos por defecto | Dueño |
|---|---|---|---|---|

## 2. Tipos de contenido
| Tipo | Mecanismo (Liferay CMS, Web Content clásico, Object, Content Page, documento) | Estado de la capacidad en la release (GA, maintenance mode, deprecada) | Campos clave | Presentación (plantillas o Fragments) | Dueño | Ciclo de vida y caducidad |
|---|---|---|---|---|---|---|

## 3. Taxonomía
| Vocabulario | Global o por site | Categorías principales | Uso (navegación, búsqueda, personalización) | Dueño |
|---|---|---|---|---|

## 4. Experiencia
- Plantillas maestras: <...>
- Style Books: <...>
- Colecciones de Fragments, dueño y versionado: <...>
- Requisitos de accesibilidad: <...>

## 5. Documentos
- Almacén compartido: <tipo> · tamaño y tipos permitidos: <...> · antivirus: <...>
- Previews y procesadores externos: <cuáles, dimensionado y aislamiento>
- Retención: <...>

## 6. Publicación
| Opción | Elegida | Motivo | Riesgos |
|---|---|---|---|
| Workflow y versionado del CMS | | | |
| Directa con workflow | | | |
| Publications (maintenance mode) | | | |
| Local staging | | | |
| Remote Live staging | | | |

## 7. Búsqueda
| Elemento | Decisión | Verificación |
|---|---|---|
| Motor y versión | Elasticsearch u OpenSearch <v> | Compatibility Matrix de la release |
| Topología | Nodos, shards y réplicas | Volumen y SLO |
| Seguridad | Autenticación y TLS | |
| Relevancia | Blueprints o configuración, sinónimos | Consultas reales de prueba |

## 8. Reindexación
| Situación | Alcance (completa o por entidad) | Duración medida | Ventana | Impacto | Rollback |
|---|---|---|---|---|---|
| Tras un upgrade | | | | | |
| Recuperación en DR | | | | | |

## 9. Riesgos
| Riesgo | Mitigación | Responsable |
|---|---|---|
