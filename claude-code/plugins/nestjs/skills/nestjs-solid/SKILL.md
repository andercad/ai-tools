---
name: nestjs-solid
description: 'Diseño previo SOLID para código NestJS nuevo o refactorizado. Usar antes de escribir módulos, servicios, guards, interceptores o proveedores para decidir responsabilidades, dependencias, tokens de inyección y puntos de extensión. No usar para sintaxis de decoradores de Nest ni para decisiones de arquitectura de aplicación (agente nestjs-architect).'
---

# Diseño SOLID previo (antes de escribir)

Decide la estructura **antes** de generar código para acertar a la primera.

## Mini-diseño (5–8 líneas, si la pieza supera ~30 líneas o toca varias clases)
1. **Piezas y responsabilidad única**: controlador/resolver/handler traduce protocolo; servicio orquesta negocio; repositorio accede a datos; lógica pura en funciones.
2. **Dependencias por constructor**; abstracciones (tokens `UPPER_SNAKE_CASE`, clases abstractas) solo con ≥2 implementaciones reales o necesidad de sustituir en tests. Las interfaces no existen en runtime: no sirven de token.
3. **Extensión sin modificar**: variantes mediante estrategias, guards o interceptores, no `if/switch` crecientes.
4. **Interfaces pequeñas** y contratos sustituibles.
5. Sin capas, fábricas ni abstracciones prematuras: un CRUD simple no necesita hexagonal.

## Referencia
- [solid.md](references/solid.md): principios aplicados a NestJS, síntomas y checklist. Léela solo si dudas.
