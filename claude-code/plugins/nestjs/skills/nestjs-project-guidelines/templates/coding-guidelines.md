# Coding Guidelines NestJS — Plantilla de proyecto

Convenciones **específicas de un proyecto** para añadir al `CLAUDE.md` (tras el bloque `## Convenciones NestJS`). Rellena cada sección; elimina ejemplos y secciones que no apliquen.

---

## Cliente y contexto

**Qué necesita**: para quién es el proyecto, qué hace la API y si maneja datos sensibles (personales, sanitarios, financieros). Indica restricciones de tratamiento de forma accionable.

**Ejemplo**:
- **Cliente**: ACME Seguros
- **API**: gestión de pólizas para agentes comerciales
- **Dominio sensible**: datos personales y bancarios. No los registres en logs; cífralos en reposo; no los incluyas en URLs.

---

## Estructura de carpetas y alias

**Qué necesita**: organización vigente de `src/` (o `apps/` y `libs/`) y alias de `tsconfig.json` (`compilerOptions.paths`), con política de uso.

**Ejemplo**:

| Carpeta / alias | Propósito |
|---|---|
| `@orders/*` → `src/orders/*` | Módulo de dominio (controller, service, dto, entities) |
| `@common/*` → `src/common/*` | Guards, interceptores, filtros, pipes, decoradores |
| `@config/*` → `src/config/*` | Esquema de configuración y `registerAs` |

Imports siempre por alias; al crear una carpeta de primer nivel, añade antes su alias.

---

## Base de datos y persistencia

**Qué necesita**: motor, ORM (TypeORM/Prisma/otro), herramienta de migraciones, convenciones de nombres y política de borrado.

**Ejemplo**: PostgreSQL con TypeORM; migraciones en `src/migrations`, nunca `synchronize`; borrado lógico con `deletedAt`; ids UUID v7.

---

## Autenticación y autorización

**Qué necesita**: mecanismo (JWT propio, OIDC/Entra ID, API keys), guards globales, endpoints públicos, modelo de roles/permisos y reglas de autorización por recurso.

**Ejemplo**: JWT validado contra Entra ID; `JwtAuthGuard` global y `@Public()` para salud y login; roles `admin|agent`; un agente solo ve sus pólizas (`ownerId`).

---

## Formato de errores y logging

**Qué necesita**: formato único de error de la API, logger usado, campos obligatorios (id de correlación) y datos que nunca se registran.

**Ejemplo**: `{ statusCode, code, message, correlationId }`; `nestjs-pino` con `x-correlation-id`; nunca tokens, contraseñas ni PII.

---

## Documentación de API y contratos

**Qué necesita**: si se publica OpenAPI/Swagger y dónde, política de versionado y, en monorepo, la librería de contratos compartidos con el frontend.

**Ejemplo**: Swagger en `/docs` solo fuera de producción; versionado por URI (`/v1`); contratos de solo tipos en `libs/shared/api-contracts`.

---

## Documentación y separadores de sección

**Qué necesita**: reglas de JSDoc y separadores de bloques en clases, con su orden canónico.

**Ejemplo**:

```typescript
// --- Dependencies ---
// --- Public methods ---
// --- Private methods ---
```

Incluye solo los bloques con al menos un miembro. No documentes lo evidente.
