
# Calidad de Código

Esta skill cubre lint, formato, análisis estático y el quality gate previo a un PR. **Cómo diseñar y escribir los tests** está en la skill `angular-developer` (oficial).

Lee siempre la configuración real del proyecto (`eslint.config.js`, configuración de Prettier, `sonar-project.properties`) antes de aplicar las reglas de esta skill: si difieren, prevalece la del proyecto.

## ESLint — Configuración del proyecto

El proyecto usa `eslint.config.js` (flat config) con:

- `@eslint/js` recommended
- `typescript-eslint` recommended + stylistic
- `angular-eslint` tsRecommended + templateRecommended + **templateAccessibility**

```javascript
// eslint.config.js (resumen de reglas activas relevantes)
// TypeScript files
{
  '@angular-eslint/directive-selector': ['error', { type: 'attribute', prefix: 'app', style: 'camelCase' }],
  '@angular-eslint/component-selector': ['error', { type: 'element', prefix: 'app', style: 'kebab-case' }],
  // + typescript-eslint/recommended: no-unused-vars, no-explicit-any, ...
  // + typescript-eslint/stylistic: consistent-type-imports, prefer-nullish-coalescing...
}

// HTML templates
{
  // templateRecommended: no-output-on-prefix, no-inputs-metadata-property...
  // templateAccessibility: alt-text, label-for, interactive-supports-focus...
}
```

En proyectos de librería, el prefijo de los selectores es el de la librería, no `app` (ver `library.md`). En un monorepo, cada proyecto tiene su configuración de ESLint que extiende la de la raíz, y en Nx incluye la regla de límites entre librerías (ver `monorepo.md`).

## Errores ESLint más frecuentes y soluciones

```typescript
// ❌ @typescript-eslint/no-explicit-any
function process(data: any): any { ... }
// ✅ Tipar o usar unknown
function process(data: unknown): ProcessedData { ... }

// ❌ @typescript-eslint/no-unused-vars
const unusedVar = computeSomething();

// ❌ @angular-eslint/no-output-on-prefix
readonly onClick = output<void>(); // prefijo "on" prohibido
// ✅
readonly clicked = output<void>();

// ❌ @angular-eslint/prefer-standalone — no aplica en v20+ (standalone por defecto)

// ❌ @typescript-eslint/consistent-type-imports — import de valor usado solo como tipo
import { OnInit } from '@angular/core';
// ✅
import type { OnInit } from '@angular/core';
// Nota: los decoradores (Component, Injectable...) y lo que se usa en runtime NO son import type
```

```html
<!-- ❌ @angular-eslint/template/no-autofocus — puede ser un problema de accesibilidad -->
<input autofocus />
<!-- ✅ Gestionar el foco programáticamente con afterNextRender() -->
```

**Regla**: corregir la causa. No desactivar reglas con `eslint-disable` salvo excepción justificada y comentada en la propia línea. Tampoco la regla de límites de Nx (`@nx/enforce-module-boundaries`): si salta, el código está en la librería equivocada.

## Prettier — Configuración del proyecto

```json
// package.json → "prettier"
{
  "printWidth": 100,
  "singleQuote": true,
  "overrides": [
    {
      "files": "*.html",
      "options": { "parser": "angular" }
    }
  ]
}
```

**Reglas que afectan al código generado**:

- Líneas máx. **100 caracteres** — dividir líneas largas de template
- **Comillas simples** en TypeScript: `'value'`, no `"value"`
- Punto y coma al final de sentencias
- Trailing commas en objetos y arrays multilínea

```typescript
// ✅ Dentro de los 100 caracteres — evitar líneas largas
readonly filteredItems = computed(() =>
  this._items().filter((item) => item.status === 'active' && item.visible),
);
```

```html
<!-- ✅ Template con atributos en múltiples líneas si superan 100 chars -->
<input
  id="customer-name"
  type="text"
  class="form-control"
  formControlName="name"
  [attr.aria-required]="'true'"
/>
```

## SonarQube — Issues frecuentes

### Complejidad cognitiva

Mantener la complejidad cognitiva baja. El umbral lo fija el quality gate del proyecto (el valor por defecto de Sonar es **15 por función**).

```typescript
// ❌ Alta complejidad cognitiva
filterCustomers(customers: Customer[], filters: Filters): Customer[] {
  const result = [];
  for (const customer of customers) {       // +1
    if (filters.age) {                       // +2 (anidado)
      if (customer.age < filters.age.min ||  // +3 (anidado) +1 (operador)
          customer.age > filters.age.max) {
        continue;
      }
    }
    if (filters.tags?.length) {              // +2
      let hasMatch = false;
      for (const tag of filters.tags) {      // +3
        if (customer.tags.includes(tag)) {   // +4
          hasMatch = true;
          break;
        }
      }
      if (!hasMatch) continue;               // +3
    }
    result.push(customer);
  }
  return result;
}

// ✅ Extraer condiciones a funciones con nombres descriptivos
filterCustomers(customers: Customer[], filters: Filters): Customer[] {
  return customers
    .filter((c) => this.matchesAgeFilter(c, filters.age))
    .filter((c) => this.matchesTagsFilter(c, filters.tags));
}

private matchesAgeFilter(customer: Customer, ageFilter?: AgeRange): boolean {
  if (!ageFilter) return true;
  return customer.age >= ageFilter.min && customer.age <= ageFilter.max;
}

private matchesTagsFilter(customer: Customer, tags?: string[]): boolean {
  if (!tags?.length) return true;
  return tags.every((t) => customer.tags.includes(t));
}
```

### Código duplicado

```typescript
// ❌ Lógica duplicada en múltiples componentes
// ComponenteA.ts
const formatted = value.trim().toLowerCase().replace(/\s+/g, '-');
// ComponenteB.ts
const formatted = value.trim().toLowerCase().replace(/\s+/g, '-');

// ✅ Extraer a shared/utils (alias @shared/utils/...)
// shared/utils/string-utils.ts
export function toKebabCase(value: string): string {
  return value.trim().toLowerCase().replace(/\s+/g, '-');
}
```

Extraer cuando la duplicación representa **el mismo concepto**. Dos fragmentos parecidos que evolucionan por razones distintas no deben unificarse a la fuerza. Si se repite entre varias aplicaciones del mismo monorepo, extráelo a una librería `util` (ver `monorepo.md`); entre repositorios distintos, a una librería publicada (ver `library.md`).

### console.log en producción

```typescript
// ❌ console.log — SonarQube lo marca como code smell
console.log('customer data:', customerData);
console.error('error occurred');

// ✅ En desarrollo: usar condición de entorno
if (!environment.production) {
  console.debug('debug info'); // Solo en desarrollo, nunca con datos sensibles
}

// ✅ En producción: usar servicio de logging/monitoring del proyecto
// (o simplemente eliminar los logs)
```

### Código muerto

```typescript
// ❌ Código inalcanzable o nunca usado
export class CustomerService {
  // Método que nadie llama — SonarQube: "Remove this unused method"
  private formatLegacy(data: unknown): string { ... }

  // Variable inicializada pero nunca leída
  private readonly _cache = new Map<string, Customer>();
}
```

## Checklist pre-PR de calidad

Proyecto de una aplicación:

```powershell
# Ejecutar lint
ng lint

# Ejecutar tests con cobertura (estrategia de tests: ver angular-testing)
ng test --coverage

# Verificar formato (dry-run)
npx prettier --check "src/**/*.{ts,html,scss}"

# Aplicar formato
npx prettier --write "src/**/*.{ts,html,scss}"

# Build de producción
ng build
```

Monorepo (ver `monorepo.md`):

```powershell
# Angular CLI multiproyecto: por proyecto afectado
ng lint portal
ng test portal --coverage
ng build portal

# Nx: solo lo afectado por los cambios
nx affected -t lint test build
nx format:check
```

- [ ] Lint sin warnings ni errores (en un monorepo, de todos los proyectos afectados)
- [ ] Prettier formateado
- [ ] Build de producción sin errores
- [ ] Sin `console.log` en código de producción
- [ ] Sin variables/métodos sin usar
- [ ] Complejidad cognitiva dentro del umbral del quality gate (por defecto ≤ 15 por función)
- [ ] Sin código duplicado (extraer a `utils/` o a una librería `util`)
- [ ] Sin `any` — usar tipos concretos o `unknown`
- [ ] Sin signals escribibles expuestas a la plantilla ni `.set()`/`.update()` en plantillas
- [ ] Sin violaciones de límites entre librerías ni imports profundos (monorepo)
- [ ] Cobertura según el umbral definido en el `CLAUDE.md` del proyecto (o el solicitado para la tarea)
