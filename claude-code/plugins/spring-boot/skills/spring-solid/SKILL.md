---
name: spring-solid
description: 'Backend Spring Boot. Principios SOLID en Spring. Usar al diseñar o refactorizar servicios, decidir si crear una interfaz, desacoplar una implementación (persistencia, proveedor externo, mensajería), elegir entre varias implementaciones con @Qualifier o @Primary o inyectar List/Map de beans como estrategias. No usar para estructura de paquetes (spring-structure-services).'
---

# SOLID en Spring

## Reglas clave
- Solo inyección por constructor con campos `final`; nunca `@Autowired` en campos, `new` de beans ni búsquedas en el `ApplicationContext`.
- Una razón de cambio por clase; un constructor con más de 5-6 parámetros delata demasiadas responsabilidades; un servicio no conoce detalles del transporte (HTTP, cabeceras, mensajes).
- Variantes reales como implementaciones inyectadas (`List`/`Map` de beans) en lugar de `if`/`switch`.
- Implementaciones intercambiables: mismo contrato y comportamiento; composición antes que herencia de implementación.
- Interfaces solo en fronteras o con varias implementaciones; sin `XService` + `XServiceImpl` automáticos. Sin capas ni abstracciones prematuras.
- Con varias implementaciones del mismo tipo, `@Qualifier` explícito o `List`/`Map` antes que `@Primary`.

## Referencias
| Tema | Fichero |
|---|---|
| Principios SOLID, inyección, estrategias, checklist de diseño | [solid.md](references/solid.md) |
