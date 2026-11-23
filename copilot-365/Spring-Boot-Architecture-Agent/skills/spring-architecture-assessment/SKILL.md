---
name: spring-architecture-assessment
description: 'Evalúa y descubre la arquitectura de un sistema Spring Boot existente o propuesto: mapa de contexto, inventario de componentes, deuda técnica, riesgos, NFR y decisiones pendientes. Usar cuando se pida revisar, auditar, diagnosticar o entender una aplicación Spring Boot, evaluar la salud arquitectónica, preparar un due diligence técnico, priorizar deuda técnica o decidir por dónde empezar un cambio. No usar para decisiones de patrón concretas (modularidad, datos, seguridad, etc.) ni como generador de código.'
---

# Evaluación arquitectónica y descubrimiento

## Objetivo
Construir una imagen fiable del sistema antes de prescribir nada: qué es, cómo está construido, qué duele y qué riesgos tiene. Es la skill de entrada; cuando aparezca una decisión específica, deriva a la skill del ámbito.

## Inventario mínimo
Registra cada dato con su fuente (`observado`, `declarado por el usuario`, `inferido`, `desconocido`).
- **Plataforma**: Java, Spring Boot, Spring Framework, Spring Cloud, build, BOM/dependencias gestionadas, fecha de fin de soporte de la línea usada (verificar en la documentación oficial).
- **Estructura**: monolito o multimódulo, paquetes por capa o por dominio, tamaño aproximado, dependencias cíclicas.
- **Entradas y salidas**: REST/GraphQL/mensajería/jobs; bases de datos, brokers, APIs de terceros.
- **Datos**: motor, ownership por componente, migraciones, volumen, retención.
- **Seguridad**: autenticación, autorización, secretos, datos sensibles.
- **Operación**: despliegue, entornos, observabilidad, SLO existentes, incidentes recientes.
- **Equipo**: tamaño, ownership, cadencia de releases, cobertura y fiabilidad de pruebas.

## Preguntas de descubrimiento (sin acceso al código)
Si no puedes leer el proyecto, haz como máximo 3 preguntas aclaratorias, elegidas por este orden de prioridad entre las que cambien la conclusión: 1) versiones de Java y Spring Boot; 2) problema o motivo del encargo; 3) NFR críticos (carga, disponibilidad, latencia, cumplimiento); 4) tamaño y organización del equipo; 5) plataforma de despliegue. Continúa con supuestos explícitos si no hay respuesta.

## Señales de riesgo a buscar
- Versión fuera de soporte o salto de línea mayor pendiente.
- Lógica de negocio en controladores, entidades JPA expuestas en la API, repositorios usados desde la capa web.
- `@Transactional` en capas incorrectas, transacciones largas, llamadas remotas dentro de transacciones.
- Base de datos compartida entre servicios; dependencias cíclicas entre módulos.
- Configuración y secretos en el repositorio; ausencia de perfiles por entorno.
- Sin timeouts en clientes HTTP; sin métricas, trazas ni correlación de logs.
- Pruebas inexistentes, lentas o que dependen de entornos compartidos.
- Microservicios sin ownership claro o con despliegue acoplado («monolito distribuido»).

## Clasificación de la deuda
Para cada hallazgo indica **impacto** (alto/medio/bajo sobre calidad o negocio), **esfuerzo relativo** (S/M/L), **riesgo de no actuar** y **dependencias**. Prioriza por impacto/esfuerzo y por lo que bloquea otras decisiones (p. ej. el upgrade de versión antes que optimizaciones).

## Salida
Usa `templates/assessment-report.md` como estructura del informe.
1. Resumen ejecutivo con las 3 conclusiones principales.
2. Mapa de contexto y contenedores (diagrama textual o Mermaid).
3. Tabla de hechos / supuestos / desconocidos.
4. Registro de riesgos y deuda priorizado.
5. Decisiones pendientes con la skill que debe tratarlas.
6. Próximos pasos de menor riesgo (30/60/90 días).

## Autoevaluación
Verifica que ninguna conclusión se apoya en un dato inferido sin marcarlo, que las prioridades son coherentes con los NFR, que no recomiendas rediseños sin evidencia y que cada riesgo tiene mitigación.
