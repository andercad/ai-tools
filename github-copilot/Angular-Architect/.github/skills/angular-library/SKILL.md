---
name: angular-library
description: 'Frontend Angular. Creación de librerías y paquetes Angular propios con ng-packagr. Usar cuando: crear una librería de componentes, servicios o utilidades compartida entre aplicaciones, extraer código de una aplicación a un paquete, definir la API pública (public-api.ts), añadir entry points secundarios, gestionar peerDependencies, compilar para publicar (compilación parcial), versionar y publicar en npm o en un registro privado (Azure Artifacts, GitHub Packages, Nexus...), consumir y probar la librería en local, configurar la librería para las aplicaciones (provideXxx), estilos y assets en librerías.'
argument-hint: 'Describe la librería o paquete: qué contiene, quién la consume y dónde se publicará.'
---

# Librerías y paquetes Angular

## Antes de crear una librería

| Situación | Opción |
|---|---|
| Código compartido dentro de una sola aplicación | Carpeta `shared/` con alias en `tsconfig.json`; no hace falta librería |
| Varias aplicaciones en el mismo repositorio | Librería del monorepo, consumida sin publicar (ver `angular-monorepo`) |
| Aplicaciones en repositorios distintos o equipos distintos | Librería publicada en un registro, con versionado semántico |

Una librería publicada es un contrato: cada cambio en su API pública obliga a versionar, documentar y coordinar a los consumidores. No extraigas a librería código que todavía cambia cada semana.

**Librerías dentro de un monorepo**: en un workspace multiproyecto de Angular CLI, la librería se compila con ng-packagr y la aplicación la consume desde `dist/`. En Nx, por defecto las librerías **no** se compilan por separado: la aplicación las compila desde el código fuente, y solo las librerías `--buildable` o `--publishable` usan ng-packagr. Las reglas de esta skill sobre API pública, dependencias y diseño de componentes aplican igualmente; las de compilación, publicación y versionado, solo a las librerías que se distribuyen fuera del monorepo.

## Crear la librería

```powershell
# Workspace dedicado a librerías (sin aplicación)
ng new acme-workspace --no-create-application
cd acme-workspace
ng generate library @acme/ui --prefix=acme

# O dentro de un workspace existente
ng generate library @acme/ui --prefix=acme

# En Nx, librería publicable
nx g @nx/angular:library libs/ui --publishable --import-path=@acme/ui --prefix=acme
```

- El proyecto queda en `projects/acme/ui` con `projectType: "library"` y el builder `@angular/build:ng-packagr` (el nombre exacto del builder depende de la versión; no lo cambies a mano).
- **Nombre**: con scope de organización (`@acme/ui`). No uses el prefijo `ng-` (reservado para Angular); para paquetes públicos sin scope, la convención es `ngx-`.
- **Prefijo de selectores** propio (`acme`), distinto de `app`, para no colisionar con las aplicaciones. Configura ESLint de la librería con ese prefijo.

```
projects/acme/ui/
├── ng-package.json            ← configuración de ng-packagr
├── package.json               ← nombre, versión, peerDependencies
├── tsconfig.lib.json
├── tsconfig.lib.prod.json     ← compilación para publicar
└── src/
    ├── public-api.ts          ← API pública: lo único que ven los consumidores
    └── lib/
        ├── badge/
        ├── config/
        └── ...
```

## API pública

```typescript
// projects/acme/ui/src/public-api.ts
export { AcmeBadge, type BadgeTone } from './lib/badge/badge';
export { provideAcmeUi, type AcmeUiConfig } from './lib/config/provide-acme-ui';
// Lo que no se exporta aquí es interno y puede cambiar sin romper a nadie
```

- Exporta de forma **explícita** (por nombre), no `export *` de carpetas enteras: así nada interno se vuelve público por accidente.
- Todo lo exportado es API: renombrarlo o eliminarlo es un cambio incompatible (versión mayor).
- Los consumidores importan siempre desde el nombre del paquete (`@acme/ui`), nunca desde rutas internas (`@acme/ui/src/lib/...`).

## Componentes de librería

```typescript
export type BadgeTone = 'neutral' | 'success' | 'warning' | 'danger';

/**
 * Indicador de estado.
 *
 * @example
 * <acme-badge tone="success">Activo</acme-badge>
 */
@Component({
  selector: 'acme-badge',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    class: 'acme-badge',
    '[class.acme-badge--success]': "tone() === 'success'",
    '[class.acme-badge--warning]': "tone() === 'warning'",
    '[class.acme-badge--danger]': "tone() === 'danger'",
  },
  template: `<ng-content />`,
  styles: `
    :host {
      display: inline-block;
      padding: var(--acme-badge-padding, 0.125rem 0.5rem);
      border-radius: var(--acme-badge-radius, 999px);
      background: var(--acme-badge-bg, #e9ecef);
      color: var(--acme-badge-color, #212529);
    }
    :host(.acme-badge--success) { --acme-badge-bg: var(--acme-color-success, #198754); --acme-badge-color: #fff; }
    :host(.acme-badge--warning) { --acme-badge-bg: var(--acme-color-warning, #ffc107); }
    :host(.acme-badge--danger) { --acme-badge-bg: var(--acme-color-danger, #dc3545); --acme-badge-color: #fff; }
  `,
})
export class AcmeBadge {
  readonly tone = input<BadgeTone>('neutral');
}
```

**Reglas**:

- Mismas restricciones que en aplicaciones (standalone, signals, `OnPush` según versión, `host`, estado privado con `asReadonly()`), y además:
- **Sin dependencias de la aplicación**: nada de servicios, aliases, rutas ni scopes de traducción de una app concreta. La librería no conoce a sus consumidores.
- **Textos**: no fijes texto visible en la librería. Recíbelo por `input()`, por proyección de contenido (`<ng-content>`) o por un token de configuración, para que cada aplicación lo traduzca con su propio sistema.
- **Estilos personalizables con variables CSS** (`--acme-*`) con valores por defecto, en lugar de depender del framework CSS de la aplicación.
- **Compatibles con SSR**: sin acceso directo a `window`/`document` (ver `angular-ssr`); una librería no sabe si se ejecutará en servidor.
- **Accesibles** por defecto (ver `angular-accessibility`): los consumidores heredan sus fallos.

## Configuración desde la aplicación

```typescript
// lib/config/provide-acme-ui.ts
export interface AcmeUiConfig {
  readonly apiBaseUrl: string;
  readonly dateFormat?: string;
}

export const ACME_UI_CONFIG = new InjectionToken<AcmeUiConfig>('ACME_UI_CONFIG');

export function provideAcmeUi(config: AcmeUiConfig): EnvironmentProviders {
  return makeEnvironmentProviders([
    { provide: ACME_UI_CONFIG, useValue: { dateFormat: 'dd/MM/yyyy', ...config } },
  ]);
}
```

```typescript
// app.config.ts de la aplicación consumidora
providers: [provideAcmeUi({ apiBaseUrl: 'https://api.example.com' })],
```

- Función `provideXxx()` que devuelve `EnvironmentProviders`: es el patrón de las librerías oficiales de Angular.
- Los servicios internos usan `providedIn: 'root'` solo si no necesitan configuración; si la necesitan, inyectan el token.

## Entry points secundarios

Para separar partes con dependencias distintas (por ejemplo, un `@acme/ui/charts` que depende de una librería de gráficas, o `@acme/ui/testing` con utilidades de test):

```
projects/acme/ui/
├── ng-package.json
├── src/public-api.ts            → @acme/ui
├── charts/
│   ├── ng-package.json          → {}   (basta con un objeto vacío)
│   └── src/public-api.ts        → @acme/ui/charts
└── testing/
    ├── ng-package.json          → {}
    └── src/public-api.ts        → @acme/ui/testing
```

- Así, quien no usa gráficas no instala ni carga esa dependencia.
- Los assets de los entry points secundarios se declaran en el `ng-package.json` **principal**.
- Un entry point puede importar de otro solo por su nombre público (`@acme/ui`), nunca por ruta relativa.

## Dependencias

```json
{
  "name": "@acme/ui",
  "version": "1.2.0",
  "peerDependencies": {
    "@angular/core": "^21.0.0 || ^22.0.0",
    "@angular/common": "^21.0.0 || ^22.0.0"
  },
  "dependencies": {
    "tslib": "^2.3.0"
  }
}
```

- **`peerDependencies`** para Angular y para cualquier librería que la aplicación también use (RxJS, CDK, Transloco): evita duplicados en el bundle e instancias distintas de servicios.
- **`dependencies`** solo para paquetes internos de la librería. ng-packagr rechaza dependencias no listadas en `allowedNonPeerDependencies` de `ng-package.json`; añádelas ahí de forma consciente.
- El rango de versiones de Angular debe ser el que **has probado**, no uno abierto.

## Compilar para publicar

```powershell
ng build @acme/ui --configuration production
```

- La configuración de producción usa `"compilationMode": "partial"` (en `tsconfig.lib.prod.json`). La compilación parcial permite que la aplicación consumidora termine de compilar la librería con su propia versión de Angular. Comprueba en la guía oficial de compatibilidad de librerías qué versiones de aplicación admite una librería compilada con una versión dada.
- **Nunca publiques un build de desarrollo** (compilación completa): queda atado a una versión exacta de Angular.
- El resultado (`dist/acme/ui`) está en Angular Package Format. Revisa el `package.json` generado (`exports`, `sideEffects`) antes de publicar.

## Desarrollo y consumo en local

- En el mismo workspace de Angular CLI, `ng generate library` añade a `tsconfig.json` un `paths` hacia `dist/...`: hay que compilar la librería antes que la aplicación.
- Durante el desarrollo: `ng build @acme/ui --watch` en una terminal y la aplicación en otra.
- En Nx, las librerías no compilables se consumen desde el código fuente sin este paso (ver `angular-monorepo`).
- Para probar contra otra aplicación sin publicar: `npm pack` en `dist/acme/ui` e instala el `.tgz` en la aplicación. Es más fiable que `npm link`, que suele provocar copias duplicadas de `@angular/core`.

## Publicar

```powershell
# Registro privado: .npmrc con el scope apuntando al registro (credenciales fuera del repositorio)
# @acme:registry=https://<registro-privado>/npm/

cd dist/acme/ui
npm publish
```

- Publica siempre desde `dist/`, nunca desde el código fuente.
- **Versionado semántico**: corrección → patch; funcionalidad compatible → minor; cambio en la API pública, en `peerDependencies` o en el comportamiento → major.
- Mantén un `CHANGELOG` y documenta los pasos de migración de cada versión mayor.
- Publica desde CI (build, tests, lint y después publicación), no desde la máquina de un desarrollador.
- Credenciales del registro como secreto de CI; nunca en `.npmrc` versionado.

## Tests

```powershell
ng test @acme/ui
```

- Tests de la librería como los de cualquier proyecto (ver `angular-testing`), centrados en la **API pública**: inputs, outputs, providers y comportamiento observable.
- Antes de publicar una versión, prueba el paquete construido en una aplicación real (`npm pack` + instalación), incluido el build de producción de la aplicación y, si la usa, con SSR.

## Checklist

- [ ] La librería está justificada (compartida, con API estable)
- [ ] Nombre con scope y prefijo de selectores propio
- [ ] `public-api.ts` con exportaciones explícitas; nada interno expuesto
- [ ] Sin dependencias de la aplicación (servicios, aliases, scopes de traducción)
- [ ] Textos recibidos desde fuera; estilos personalizables con variables CSS
- [ ] Compatible con SSR y accesible
- [ ] Configuración mediante `provideXxx()` y `InjectionToken`
- [ ] Angular y librerías compartidas en `peerDependencies` con rangos probados
- [ ] Compilación parcial para publicar; publicación desde `dist/` y desde CI
- [ ] Versión semántica y CHANGELOG actualizados
- [ ] Paquete probado en una aplicación real antes de publicar
