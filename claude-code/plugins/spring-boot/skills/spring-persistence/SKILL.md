---
name: spring-persistence
description: 'Backend Spring Boot. Persistencia con Spring Data JPA. Usar al crear entidades, repositorios, consultas derivadas, JPQL o nativas, proyecciones, paginación, relaciones, problema N+1, bloqueos optimista y pesimista, auditoría, migraciones Flyway o Liquibase y ajuste de open-in-view y ddl-auto. No usar para lógica de transacciones de negocio (spring-structure-services) ni arquitectura de datos (spring-data-transactions).'
---

# Persistencia (Spring Data JPA)

## Reglas clave
- Consultas siempre parametrizadas; nunca concatenes JPQL/SQL con entrada del usuario.
- `spring.jpa.open-in-view=false`; `ddl-auto` solo `validate` o `none` fuera de desarrollo; los cambios de esquema van en migraciones (Flyway o Liquibase).
- Evita el N+1: relaciones `LAZY`, `join fetch`/`@EntityGraph` o proyecciones; pagina siempre las listas grandes.
- Las entidades JPA no son records ni se exponen en la API; `equals`/`hashCode` coherentes y sin `@Data` de Lombok.
- Transacciones en la capa de servicio (`spring-structure-services`), no en repositorios ni controladores.
- Otras funcionalidades no usan el repositorio directamente: llaman al servicio.

## Referencias
| Tema | Fichero |
|---|---|
| Entidades, repositorios, consultas, N+1, bloqueos, auditoría, migraciones | [persistence.md](references/persistence.md) |
