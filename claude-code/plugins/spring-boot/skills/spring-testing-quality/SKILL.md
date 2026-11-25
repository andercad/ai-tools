---
name: spring-testing-quality
description: 'Backend Spring Boot. Tests y calidad. Usar al crear o corregir tests con JUnit 5, AssertJ y Mockito, slices (@WebMvcTest, @DataJpaTest), @SpringBootTest, Testcontainers con @ServiceConnection, @MockitoBean, MockMvc, tests de seguridad y cobertura JaCoCo, y al aplicar formato, análisis estático, SonarQube y logging con SLF4J. No usar para diseño de clases (spring-solid).'
---

# Tests y calidad

## Reglas clave
- Test de menor alcance que demuestre el comportamiento: unitario sin Spring, luego slice, luego integración.
- `tests: required` → `*Test.java` por cada servicio, controlador, componente, listener o advice nuevo, en el mismo paso; `it: required` → `*IT.java` (Testcontainers/`@SpringBootTest`) por endpoint o repositorio con consultas propias.
- Testcontainers con `@ServiceConnection` frente a bases de datos en memoria distintas de la real; `@MockitoBean` en lugar de `@MockBean` en las versiones recientes.
- Cobertura según `coverage` (JaCoCo): sin tests triviales que solo ejecutan líneas.
- Logging con SLF4J parametrizado; nunca `System.out`/`printStackTrace`; sin contraseñas, tokens ni datos personales en logs.
- Ejecuta `verify` antes de dar el paso por terminado.

## Referencias
| Tema | Fichero |
|---|---|
| JUnit 5, Mockito, slices, Testcontainers, seguridad, cobertura | [testing.md](references/testing.md) |
| Formato, análisis estático, Sonar, logging, checklist | [quality.md](references/quality.md) |
