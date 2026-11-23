---
name: spring-structure-services
description: Backend Spring Boot. Estructura de paquetes por funcionalidad, visibilidad, límites entre módulos, clases @Configuration y beans, servicios, transacciones, mapeo entidad-DTO, y convenciones de nombres, orden de miembros, records, Lombok y Javadoc. Usar al crear una funcionalidad, decidir dónde va una clase, escribir servicios con @Transactional, mapear entidades a DTOs o resolver dependencias circulares. No usar para controladores (spring-api) ni consultas JPA (spring-persistence).
---

# Estructura, servicios y convenciones

## Reglas clave
- Paquetes por funcionalidad, no por capa técnica global; `common` solo para lo transversal. La clase `@SpringBootApplication` en el paquete raíz.
- Clases internas package-private; `public` solo lo que usan otras funcionalidades. Ninguna funcionalidad usa el repositorio o la entidad de otra: llama a su servicio.
- Beans de librerías en `@Configuration(proxyBeanMethods = false)`; sin dependencias circulares ni `allow-circular-references`.
- La lógica de negocio vive en servicios; `@Transactional` en métodos públicos de servicio (lecturas con `readOnly = true`), nunca en controladores.
- Los servicios no devuelven entidades hacia fuera; copia campo a campo desde el DTO validado.
- Nombres con sufijo descriptivo (`UserController`, `UserService`, `CreateUserRequest`); records para DTOs, eventos y propiedades, no para entidades JPA.
- Orden de miembros: constantes, logger, dependencias, constructor, métodos públicos (lectura, escritura), privados. Javadoc conciso en API pública si `docs: javadoc`.

## Referencias
| Tema | Fichero |
|---|---|
| Paquetes, visibilidad, Modulith, configuración, ciclos, arranque | [structure.md](references/structure.md) |
| Servicios, transacciones, mapeo, excepciones de dominio | [services.md](references/services.md) |
| Nombres, orden de miembros, records, nulos, Lombok/MapStruct, Javadoc | [conventions.md](references/conventions.md) |
