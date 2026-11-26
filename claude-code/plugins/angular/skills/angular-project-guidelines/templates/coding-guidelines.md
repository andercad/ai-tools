# Coding Guidelines — Plantilla de proyecto

Este fichero recoge las convenciones **específicas de un proyecto**. El agente debe leerlo **antes de cualquier acción** para adaptar el código al contexto concreto de la aplicación.

> **Cómo usar esta plantilla**: copia el fichero a tu proyecto y rellena cada sección. Cada apartado explica **qué información necesita** y muestra un **ejemplo** orientativo. Elimina los ejemplos y las secciones que no apliquen.

---

## Cliente y contexto

**Qué necesita**: identificar para quién es el proyecto, qué hace la aplicación y si maneja datos sensibles (personales, sanitarios, financieros...). Si existen restricciones de tratamiento de datos, indícalas de forma explícita y accionable para que el agente las respete al generar código.

- **Cliente**: nombre de la organización.
- **Aplicación**: descripción breve del propósito y de los usuarios.
- **Dominio sensible**: tipo de datos sensibles y reglas obligatorias sobre su almacenamiento y ciclo de vida.

**Ejemplo**:

- **Cliente**: ACME Seguros
- **Aplicación**: Portal de gestión de pólizas para agentes comerciales
- **Dominio sensible**: La aplicación maneja datos personales y bancarios de clientes. No almacenes PII ni datos bancarios en `localStorage`, `sessionStorage` ni cookies. Mantén los datos sensibles solo en memoria y limpia el estado al cerrar sesión.

---

## Idiomas del portal

**Qué necesita**: la lista de idiomas soportados (código y nombre) y la regla de mantenimiento de traducciones. Si la aplicación es monolingüe, indícalo para que el agente no genere claves de traducción innecesarias.

**Ejemplo**:

El portal está disponible en tres idiomas. **Añade siempre las traducciones en todos los ficheros**:

| Código | Idioma     |
| ------ | ---------- |
| `es`   | Castellano |
| `en`   | Inglés     |
| `eu`   | Euskera    |

---

## Estructura de carpetas

**Qué necesita**: la organización vigente de `src/app/` (o equivalente), con el propósito de cada carpeta de primer nivel. Sirve para que el agente sepa dónde ubicar cada nuevo artefacto (componente, servicio, guard, util...).

**Ejemplo** (por defecto del plugin, ver skill `angular-conventions`): `src/app/shared/` más una carpeta por funcionalidad. No hay `core/`; lo global va en la subcarpeta de `shared/`.

| Carpeta                         | Propósito                                                         |
| ------------------------------- | ----------------------------------------------------------------- |
| `shared/`                       | Común y global: components, pipes, directives, services, models, guards, interceptors, utils |
| `<funcionalidad>/`              | Una por funcionalidad (p. ej. `policies/`, `claims/`)             |
| `<funcionalidad>/pages/`        | Componentes de ruta (cada uno con su `.html`, `export default class`; rutas con `loadComponent: () => import(...)` sin `.then`) |
| `<funcionalidad>/components/`    | Componentes reutilizables de la funcionalidad                     |
| `<funcionalidad>/services/`     | Servicios con lógica de negocio y acceso a API                    |
| `<funcionalidad>/models/`       | Tipos e interfaces                                                |
| `<funcionalidad>/guards/` `interceptors/` `utils/` | Solo si la funcionalidad los necesita          |
| `<funcionalidad>/<funcionalidad>.routes.ts` | Rutas de la funcionalidad                             |

---

## Alias de `tsconfig.json`

**Qué necesita**: los alias definidos en `compilerOptions.paths`, la ruta a la que apunta cada uno y la política de uso (obligatorio o no, excepciones permitidas, qué hacer al crear una carpeta nueva).

**Ejemplo**:

Usa **siempre** los alias configurados. No uses imports relativos salvo dependencia cíclica documentada:

| Alias             | Ruta                     |
| ----------------- | ------------------------ |
| `@shared/*`       | `src/app/shared/*`       |
| `@policies/*`     | `src/app/policies/*`     |
| `@claims/*`       | `src/app/claims/*`       |
| `@environments/*` | `src/environments/*`     |

Un alias por funcionalidad y uno para `shared`. Cuando crees una carpeta de funcionalidad en `src/app/`, añade su alias en `tsconfig.json` antes de usarla.

```typescript
// ✅ Correcto
import { PolicyService } from '@policies/services/policy-service';
import { Button } from '@shared/components/button/button';

// ❌ Evitar
import { PolicyService } from '../../services/policy-service';
```

---

## Internacionalización — scopes existentes

**Qué necesita**: la librería de i18n usada, la ubicación de los ficheros de traducción globales y por funcionalidad, la lista de scopes existentes y la forma correcta de registrarlos (helpers propios, APIs a evitar).

**Ejemplo**:

Las traducciones globales van en `public/i18n/<idioma>.json`. Las específicas de funcionalidad van en `public/i18n/<scope>/<idioma>.json`. Scopes actuales:

| Scope       | Descripción                  |
| ----------- | ---------------------------- |
| `dashboard` | Página principal             |
| `policies`  | Listado y detalle de pólizas |
| `claims`    | Gestión de siniestros        |

Los scopes se registran en los ficheros `*.routes.ts` con el helper `withTranslocoScope()` de `@shared/utils/...`. **No uses `provideTranslocoScope` directamente en rutas**:

```typescript
withTranslocoScope(['dashboard'], {
  path: '',
  loadComponent: () => import('@dashboard/pages/dashboard/dashboard'),
  title: 'dashboard-title',
});

// Para scopes de subcarpetas con nombre largo, usa alias:
withTranslocoScope({ scope: 'claims/new-claim', alias: 'newClaim' }, { ... })
```

---

## Cadena de interceptores HTTP

**Qué necesita**: los interceptores registrados, su orden de ejecución y la responsabilidad de cada uno. Añade las reglas derivadas: qué errores **no** deben gestionarse en servicios/componentes porque ya los cubre un interceptor, y cuáles sí deben propagarse.

**Ejemplo**:

El orden en `app.config.ts` es fijo. **Respétalo al generar código**:

| Orden | Interceptor          | Responsabilidad                                     |
| ----- | -------------------- | --------------------------------------------------- |
| 1     | `base-url`           | Antepone la URL base a rutas relativas de API       |
| 2     | `auth`               | Adjunta token Bearer; gestiona refresco ante `401`  |
| 3     | `error-notification` | Notifica errores de red y `5xx` al usuario          |

- No manejes `401` en componentes ni servicios; lo gestiona `auth`.
- No captures errores de red ni `5xx` en servicios; los gestiona `error-notification`.
- Los errores de negocio (`4xx` excepto `401`) se propagan al servicio/componente que realizó la llamada.

---

## Accesibilidad

**Qué necesita**: el estándar y nivel de conformidad exigido (p. ej. WCAG 2.1 AA, EN 301 549) y, si existen, requisitos adicionales: herramientas de auditoría, tecnologías de apoyo con las que se valida o patrones obligatorios.

**Ejemplo**:

El proyecto exige **WCAG 2.1 nivel AA** como mínimo.

- Todo elemento interactivo debe ser accesible por teclado y tener foco visible.
- Los iconos decorativos llevan `aria-hidden="true"`; los funcionales, `aria-label`.
- Se valida con axe DevTools y NVDA antes de cada entrega.

---

## Librería de diseño

**Qué necesita**: la librería o sistema de diseño utilizado (Bootstrap, Angular Material, PrimeNG, design system propio...), la librería de iconos, las reglas de estilado (prioridad de utilidades frente a CSS propio, variables/tokens a usar, prácticas a evitar) y los componentes más habituales con su uso en el proyecto.

**Ejemplo**:

El proyecto usa **Angular Material** y **Material Symbols**:

- Usa los componentes de Material **antes de crear componentes propios** equivalentes.
- Personaliza estilos mediante los tokens del tema (`--mat-sys-primary`, tipografía, densidad...).
- Usa **Material Symbols** (`<mat-icon>`) para iconografía. No uses otras librerías de iconos.
- Evita `!important` y `::ng-deep`.

### Componentes habitualmente usados

| Componente     | Uso en el proyecto                         |
| -------------- | ------------------------------------------ |
| `mat-card`     | Tarjetas de resumen de pólizas             |
| `mat-table`    | Listados paginados                         |
| `mat-snackbar` | Notificaciones al usuario                  |
| `mat-dialog`   | Diálogos de confirmación y detalle         |

---

## Documentación y separadores de sección

**Qué necesita**: las convenciones de documentación del código (JSDoc/TSDoc obligatorio o no, etiquetas requeridas como `@example`) y, si se usan, los separadores que delimitan los bloques de miembros dentro de las clases, con su orden canónico y excepciones.

**Ejemplo**:

Usa separadores de sección en clases para delimitar los bloques canónicos de miembros:

```typescript
// ========== Dependencies ==========
// ========== Inputs ==========
// ========== Outputs ==========
// ========== State ==========
// ========== Computed ==========
// ========== Lifecycle ==========
// ========== Public methods ==========
// ========== Private methods ==========
```

- Incluye solo los bloques que contengan al menos un miembro.
- Adapta el nombre del bloque cuando añada claridad (ej. `// ========== HTTP ==========` en un servicio con muchas llamadas a la API).
- Los componentes de página **no necesitan `@example`** en su JSDoc. Los componentes reutilizables sí.
