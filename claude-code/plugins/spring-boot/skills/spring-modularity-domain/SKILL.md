---
name: spring-modularity-domain
description: 'Asesoría arquitectónica sobre modularidad, dominio (DDD, bounded contexts), arquitectura hexagonal, monolito modular con Spring Modulith y microservicios en Spring Boot. Usar cuando se solicite decidir entre capas, puertos y adaptadores, monolito modular, servicios independientes o microservicios; definir bounded contexts, dependencias, ownership de datos o una transición arquitectónica. No usar como generador de código por defecto.'
---

# Modularidad, dominio y arquitectura hexagonal

## Objetivo
Decide entre arquitectura por capas, monolito modular, arquitectura hexagonal y microservicios sin imponer un patrón por moda. Define bounded contexts, ownership de datos, contratos, dependencias permitidas y estrategia de evolución. Considera Spring Modulith cuando aporte verificación de límites, eventos, pruebas de módulos y documentación.

## Cuándo compensa la arquitectura hexagonal
Recomiéndala cuando exista lógica de negocio relevante, varias entradas (REST, GraphQL, mensajería, jobs), varias salidas (JPA, APIs, brokers), necesidad de probar casos de uso sin Spring o previsión real de sustituir integraciones. Para un CRUD pequeño, explicita el coste de puertos, mapeos y más clases.

## Modelo hexagonal
- **Dominio**: entidades, value objects, invariantes y eventos de dominio; sin dependencias de Spring, JPA, HTTP ni mensajería cuando sea razonable.
- **Aplicación**: casos de uso y puertos de entrada; orquesta el dominio y fija límites transaccionales.
- **Puertos de salida**: contratos de repositorio, reloj, identidad, almacenamiento, eventos e integraciones.
- **Adaptadores de entrada**: controladores REST, resolvers GraphQL, consumidores, jobs y CLI. Validan y traducen el transporte, pero no contienen negocio.
- **Adaptadores de salida**: JPA/JDBC/R2DBC, `RestClient` o HTTP Service Clients, cache, Kafka/RabbitMQ y almacenamiento.
- **Configuración**: ensambla beans y adaptadores; el dominio no busca beans ni conoce el contenedor.

Estructura conceptual, adaptable al proyecto:

```text
orders/
  domain/
  application/
    port/in/
    port/out/
    usecase/
  adapter/
    in/web/
    in/graphql/
    in/messaging/
    out/persistence/
    out/http/
    out/messaging/
  configuration/
```

No conviertas esta estructura en una obligación física si los límites pueden verificarse mejor por módulos, package-private, ArchUnit o Spring Modulith.

## Monolito modular con Spring Modulith
Primera opción cuando el problema es acoplamiento interno y no hay drivers de despliegue independiente.
- **Módulo** = paquete de primer nivel bajo la aplicación; su API es lo público del paquete raíz y el resto es interno. Exponer subpaquetes requiere declararlo explícitamente (named interfaces).
- **Verificación**: `ApplicationModules.of(App.class).verify()` en un test detecta ciclos y accesos a internos; úsalo como fitness function en CI.
- **Comunicación entre módulos**: preferir eventos de aplicación (`@ApplicationModuleListener`) a llamadas directas cuando se quiera desacoplar; el registro de publicación de eventos da entrega fiable dentro del monolito y facilita extraer un módulo después. Llamadas síncronas a la API del módulo cuando se necesita respuesta inmediata.
- **Datos**: cada módulo es dueño de sus tablas; nada de joins ni repositorios cruzados. Es la condición para poder extraerlo como servicio.
- **Pruebas**: `@ApplicationModuleTest` para arrancar un módulo aislado; documentación generada (diagramas C4/PlantUML y canvas de módulos).
- **Alternativa sin Modulith**: ArchUnit, módulos Maven/Gradle o JPMS si se prefiere límite de compilación; coste mayor en build.
- Verifica nombres de anotaciones y artefactos en la versión de Spring Modulith compatible con el Boot instalado.

## Microservicios
Antes de recomendar microservicios, exige drivers como despliegue y escalado independientes, ownership por equipos, aislamiento regulatorio o disponibilidad diferenciada. Evalúa también monolito modular y servicios independientes. Define por servicio: bounded context, datos propios, contrato, SLO, modelo de fallos, observabilidad, estrategia de despliegue y rollback. Evita base de datos compartida y llamadas síncronas en cadena.

## Verificación
- Tests unitarios del dominio y casos de uso sin contexto Spring.
- Tests de contrato para puertos y adaptadores.
- Tests de módulo y reglas ArchUnit/Spring Modulith para dependencias.
- Pruebas de integración para persistencia, mensajería y clientes remotos.

## Salida
Antes de recomendar extraer servicios o microservicios, puntúa `reference/modularization-readiness.md`.
Entrega límites, puertos y adaptadores, diagrama de dependencias, alternativa no hexagonal, trade-offs, pruebas de arquitectura, migración incremental y ADR.

## Autoevaluación
Comprueba que el dominio no depende accidentalmente del framework, que los puertos corresponden a necesidades reales, que no hay abstracciones especulativas y que microservicios no se recomiendan sin drivers.
