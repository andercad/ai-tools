# Prompts de prueba para Microsoft 365 Copilot Agent Builder

Ejecuta cada prompt en la pestaña **Try it**, anota la skill usada y el modo de respuesta, y marca el resultado. Un prompt falla si usa otra skill, ignora el modo esperado, inventa releases, compatibilidades o APIs, salta la escalera de mecanismos sin motivo o implementa código sin que se lo pidan.

| # | Prompt | Skill esperada | Modo esperado | Debe | No debe | Resultado |
|---|--------|----------------|---------------|------|---------|-----------|
| 1 | Revisa la arquitectura de nuestra instalación Liferay (sin adjuntos) | architecture-assessment | Estándar | Pedir release, modalidad e inventario (máx. 3 preguntas) o declarar supuestos | Emitir hallazgos graves sin evidencia | |
| 2 | Tenemos 60 módulos OSGi y varios overrides de JSP: ¿qué hacemos? | architecture-assessment (+ version-upgrade) | Completo | Inventario con alternativa estándar y coste de upgrade por customización | Proponer reescritura completa | |
| 3 | Las previews de documentos fallan desde hace una semana | architecture-assessment (+ content-search) | Estándar | Separar capas, correlacionar logs, hipótesis y pruebas discriminantes | Culpar a LibreOffice sin evidencia | |
| 4 | Necesitamos gestionar solicitudes de clientes con 5 campos y aprobación | solution-architecture | Estándar | Escalera de mecanismos: Objects + workflow antes que código | Proponer Service Builder u OSGi de entrada | |
| 5 | ¿Esta lógica de cálculo debe ir en un módulo OSGi o fuera del portal? | solution-architecture | Estándar | Criterios dentro/fuera de la JVM, modalidad, coste de upgrade | Elegir OSGi sin necesidad de SPI | |
| 6 | Estamos en Liferay SaaS, ¿podemos desplegar un módulo OSGi propio? | solution-architecture | Rápido | Indicar la restricción de la modalidad y alternativas; verificar en la documentación | Afirmar que sí | |
| 7 | ¿Qué tipo de Client Extension usamos para reaccionar al alta de un Object? | client-extensions-integration | Estándar | Object Action hacia microservicio; idempotencia y autenticación de la llamada | Inventar propiedades de `client-extension.yaml` | |
| 8 | Integra un servicio Spring Boot que calcula precios con Liferay | client-extensions-integration | Completo | Responsabilidad, OpenAPI, OAuth2 con scopes mínimos, resiliencia, operación | Servicio proxy sin responsabilidad | |
| 9 | ¿Cómo desplegamos una aplicación Angular como Client Extension? | client-extensions-integration | Estándar | Contrato Liferay y remisión al agente Angular para el diseño del frontend | Diseñar internamente la aplicación Angular | |
| 10 | ¿Objects o Service Builder para un dominio de expedientes con reglas complejas? | platform-customization | Estándar | Matriz; considerar servicio externo; modalidad | Elegir sin comparar | |
| 11 | Necesitamos consultar datos de usuarios directamente en la base de datos de Liferay | platform-customization | Rápido | Rechazar acceso a tablas y ofrecer APIs Headless o servicios | Proponer SQL contra el esquema | |
| 12 | Diseña el workflow de aprobación de contenidos en dos niveles | platform-customization | Estándar | Estados, roles asignados, plazos, escalados, pruebas | Código de workflow personalizado sin necesidad | |
| 13 | ¿Cómo modelamos el contenido de 3 marcas en 4 idiomas? | content-search | Completo | Sites por audiencia o marca, estructuras, taxonomía, dueños, idiomas | Una estructura por página | |
| 14 | ¿Qué versión de Elasticsearch u OpenSearch usamos con nuestra release? | content-search | Rápido | Remitir a la Compatibility Matrix y marcar como pendiente si no puede verificarlo | Inventar una versión | |
| 15 | ¿Local staging o remote staging? | content-search | Estándar | Opción más simple; operación y riesgos de cada una | Recomendar remote staging por defecto | |
| 16 | SSO con Entra ID: ¿SAML u OpenID Connect? | security-identity | Estándar | Criterios, mapeo de claims a verificar, aprovisionamiento y baja | Inventar claims o endpoints | |
| 17 | Modela roles y permisos para 40 organizaciones | security-identity | Completo | Roles por ámbito asignados a grupos, mínimo privilegio, matriz | Permisos usuario a usuario | |
| 18 | ¿AKS o Liferay PaaS con un equipo de 3 personas? | cloud-operations | Estándar | Opción más simple que cumple; coste operativo de Kubernetes | Imponer Kubernetes | |
| 19 | Queremos escalar a 4 nodos, ¿qué hay que cambiar? | cloud-operations | Estándar | Estado compartido (documentos, búsqueda, sesiones), cluster, probes | Escalar sin resolver el estado | |
| 20 | Define backup, restore y DR para Liferay | cloud-operations | Completo | Backup coherente BD + documentos, reindexación, RPO/RTO medidos | Backups nunca restaurados | |
| 21 | ¿Vamos a la última Quarterly Release o a la LTS? | version-upgrade | Estándar | Criterios, verificar soporte en fuente oficial | Inventar fechas de soporte | |
| 22 | Planifica el upgrade desde 7.4 a la LTS vigente | version-upgrade | Completo | Inventario, Compatibility Matrix, ensayo con datos reales, go/no-go, rollback | Mezclar upgrade y nuevas funcionalidades | |
| 23 | Escribe el módulo OSGi del portlet de pedidos | (fuera de perfil) | Rápido | Declinar implementar; ofrecer diseño y criterios de aceptación | Generar el código | |
| 24 | Lanza una reindexación completa en producción ahora | (fuera de perfil) | Rápido | No ejecutar; explicar el límite y el plan necesario | Simular la ejecución | |
| 25 | Proyecto nuevo de contenidos en 2026.Q3: ¿Web Content clásico o el nuevo CMS? | content-search | Estándar | Señalar el maintenance mode de Web Content y Documents and Media, el CMS como opción recomendada y verificar en la release del cliente | Recomendar Web Content clásico por defecto | |
| 26 | Queremos resumir y clasificar con IA los contenidos al publicarlos | client-extensions-integration | Estándar | Lógica fuera de la JVM, acción de Objects o de workflow, revisión humana, verificar capacidades de IA de la release | Módulo OSGi que llama al modelo | |
| 27 | Buscador semántico sobre nuestros contenidos que respete los permisos | content-search (+ security-identity) | Estándar | Verificar soporte en release, licencia y motor; permisos en los resultados | Copiar contenido a un almacén vectorial sin permisos | |
| 28 | ¿Qué normativa UE afecta a nuestro portal? | security-identity | Estándar | Mapa UE, preguntas de sector, controles y evidencias | Afirmar cumplimiento o dar asesoramiento legal | |

## Registro de resultados
Copia la tabla y añade las columnas `Skill invocada`, `OK/KO` y `Observaciones`. Si una skill no se invoca de forma fiable, ajusta primero su `description` (disparadores) y después el cuerpo.
