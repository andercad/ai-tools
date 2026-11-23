
# Configuración de Entorno y Librerías de Terceros

Antes de nada, comprueba en el `CLAUDE.md` del proyecto qué mecanismo de configuración usa el proyecto. Esta skill documenta el flujo `.env` → `scripts/set-env.js` → `src/environments/`. Si el proyecto usa otro mecanismo (`fileReplacements`, configuración en runtime cargada desde un JSON, etc.), respeta el del proyecto.

**Regla absoluta**: nada de lo que se genera en `environment.ts` es secreto. Todo acaba en el bundle que descarga el navegador. Nunca incluyas claves privadas, secretos de cliente OAuth confidenciales ni credenciales.

**En un monorepo**, la configuración es **por aplicación**: cada aplicación tiene su propio `environment`, su `.env.template` y su paso de generación (rutas bajo `projects/<app>/` o `apps/<app>/`). No compartas un único `environment.ts` entre aplicaciones. Una librería no lee la configuración directamente: la recibe mediante un `InjectionToken` o una función `provideXxx()` que configura cada aplicación (ver `library.md` y `monorepo.md`).

## Estructura de variables de entorno

```
.env.template     ← Plantilla en el repo (sin valores reales)
.env              ← Fichero local con valores reales (gitignored)
scripts/set-env.js  ← Genera src/environments/ a partir de .env
src/environments/
  environment.ts            ← Generado (gitignored)
  environment.development.ts  ← Generado (gitignored)
```

**Reglas**:

- `.env` y `src/environments/` están en `.gitignore`. **Nunca commitearlos**.
- `.env.template` sí se commitea — es la documentación de qué variables se necesitan.

## Cómo añadir una nueva variable de entorno

### 1. Añadir al `.env.template`

```bash
# .env.template
PRODUCTION=false
BASE_URL=https://your-app-url.com
API_URL=https://your-api-url.com/api
# Nueva variable:
FEATURE_FLAG_NUEVA=false
```

### 2. Añadir al `.env` local

```bash
# .env (local, gitignored)
PRODUCTION=false
BASE_URL=http://localhost:4200
API_URL=http://localhost:8080/api
FEATURE_FLAG_NUEVA=true
```

### 3. Registrar en `scripts/set-env.js`

```javascript
// scripts/set-env.js
const REQUIRED_ENV_VARS = [
  { key: 'PRODUCTION', label: 'PRODUCTION' },
  { key: 'BASE_URL', label: 'BASE_URL' },
  { key: 'API_URL', label: 'API_URL' },
  { key: 'FEATURE_FLAG_NUEVA', label: 'FEATURE_FLAG_NUEVA' }, // ← añadir
];
```

Actualizar también la generación del fichero `environment.ts` en el mismo script para incluir la nueva variable.

### 4. Actualizar la interfaz de Environment

```typescript
// La interfaz se define manualmente (fichero versionado), aunque environment.ts se genere
export interface Environment {
  production: boolean;
  baseUrl: string;
  apiUrl: string;
  featureFlagNueva: boolean; // ← añadir
}
```

### 5. Ejecutar el script

```powershell
npm run set-envs
```

## Acceder a variables de entorno en la app

Usar el servicio `AppConfigService` o el `InjectionToken` correspondiente, nunca importar `environment` directamente en componentes:

```typescript
// ✅ Via servicio de configuración inyectable
@Injectable({ providedIn: 'root' })
export class AppConfigService {
  private readonly _config = signal<AppConfig | null>(null);
  readonly config = this._config.asReadonly();

  readonly apiUrl = computed(() => this._config()?.apiUrl ?? '');
}

// ✅ Via InjectionToken
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL');

// En app.config.ts
{
  provide: API_BASE_URL,
  useFactory: () => inject(AppConfigService).apiUrl(),
}

// En el servicio que lo necesita
private readonly apiBaseUrl = inject(API_BASE_URL);
```

Ten en cuenta que `useFactory` se evalúa una sola vez: si la configuración se carga de forma asíncrona, asegúrate de que está disponible antes (por ejemplo con `provideAppInitializer`) o inyecta el servicio y lee la signal en el momento de uso.

Con SSR, la URL de la API que usa el servidor puede ser distinta de la del navegador (red interna); ver la skill `angular-developer` (oficial).

## Librerías de terceros — Proceso de evaluación

Antes de instalar cualquier paquete, seguir este proceso:

### 1. ¿Ya existe en el proyecto?

```powershell
# Revisar dependencias actuales
cat package.json | Select-String "\"dependencies\"" -A 50
```

### 2. ¿Cubre la necesidad Angular, Angular CDK o una librería ya instalada?

Comprueba primero en `package.json` qué hay instalado.

| Necesidad                   | Primera opción                                             |
| --------------------------- | ---------------------------------------------------------- |
| Focus trap, overlay, portal | `@angular/cdk`                                             |
| Virtual scroll              | `@angular/cdk/scrolling`                                   |
| Drag & drop                 | `@angular/cdk/drag-drop`                                   |
| Accordion, tabs, modal      | Componentes del framework CSS del proyecto o CDK           |
| Gráficas                    | Librería de gráficas ya usada en el proyecto (evaluar)     |
| Máscaras de input           | Evaluar librería específica                                |
| Date pickers                | Componente del framework del proyecto o librería (evaluar) |

### 3. Criterios de evaluación antes de instalar

Revisar el paquete **antes** de instalarlo:

```powershell
# Metadatos: versión, fecha de publicación, peerDependencies, licencia
npm view <package-name> version time.modified peerDependencies license

# Simular la instalación sin modificar node_modules ni package.json
npm install <package-name> --dry-run
```

`npm audit` se ejecuta sobre el árbol instalado, no sobre un paquete suelto: para auditar un paquete nuevo, instálalo en una rama de trabajo y ejecuta `npm audit`. Complementa con Snyk Advisor (`https://snyk.io/advisor/npm-package/<package-name>`) u OSV (`https://osv.dev/`).

Criterios por defecto. **Si el `CLAUDE.md` del proyecto o la política corporativa definen otros umbrales (licencias aceptadas, etc.), prevalecen.**

| Criterio                | Valor orientativo                                                     |
| ----------------------- | --------------------------------------------------------------------- |
| Mantenimiento activo    | Publicaciones o actividad reciente; desconfiar de proyectos abandonados |
| Adopción                | Uso significativo en npm (orientativo: >10.000 descargas/semana)      |
| Vulnerabilidades        | Sin críticas ni altas sin parche                                      |
| Compatibilidad Angular  | `peerDependencies` compatibles con la versión instalada               |
| Bundle size             | Evaluar con [bundlephobia.com](https://bundlephobia.com/)             |
| Licencia                | Según política del proyecto (habitualmente MIT, Apache-2.0 o BSD)     |
| SSR / tree-shaking      | Compatible si el proyecto usa SSR; módulos ESM tree-shakeables        |

Un paquete estable y pequeño puede publicar con poca frecuencia sin estar abandonado: el criterio de mantenimiento se interpreta, no se aplica mecánicamente.

En un monorepo con una sola versión de cada dependencia (lo habitual), un paquete nuevo afecta a todos los proyectos: evalúa también su compatibilidad con el resto de aplicaciones.

### 4. Proponer al usuario — no instalar sin confirmación

Antes de ejecutar `npm install`, presentar:

- Nombre del paquete y versión
- Tamaño del bundle (de bundlephobia)
- Resultado de la revisión de vulnerabilidades
- Licencia
- Alternativas evaluadas
- Justificación de por qué esta es la mejor opción

### 5. Registrar providers en el componente lazy correcto

```typescript
// ✅ En el componente lazy — no en app.config.ts
@Component({
  // ...resto de metadatos
  providers: [
    provideCharts(withDefaultRegisterables()), // Solo se carga con este componente
  ],
})
export class ChartComponent { ... }
```

## Actualización de dependencias

```powershell
# Ver dependencias desactualizadas
npm outdated

# Actualizar Angular (usar Angular CLI)
ng update @angular/core @angular/cli

# Actualizar otras dependencias (una a la vez, probar entre cada una)
npm update <package-name>

# Verificar integridad tras actualizar
npm audit
ng build
ng test
```

### Actualizar Angular de versión

1. Consulta la guía oficial de actualización (`angular.dev/update-guide`) para el salto origen → destino: requisitos de Node y TypeScript, cambios incompatibles y pasos manuales.
2. Actualiza **una versión mayor cada vez** (21 → 22, no 20 → 22), en una rama dedicada.
3. **Workspace de Angular CLI** (una aplicación o multiproyecto): `ng update @angular/core @angular/cli` aplica las migraciones automáticas de la versión; después actualiza el resto de paquetes `@angular/*` (incluido `@angular/ssr` si existe) y las librerías con `peerDependencies` de Angular (CDK, Transloco, librerías de gráficas, librerías propias...).
   **Monorepo Nx**: no uses `ng update`. Ejecuta `nx migrate` (actualiza Nx, Angular y los plugins), instala y aplica `nx migrate --run-migrations`. Con Angular, una versión mayor cada vez es obligatorio (ver `monorepo.md`).
4. Revisa el diff de las migraciones: no aceptes cambios sin entenderlos.
5. Las migraciones opcionales de modernización (control flow, `inject()`, signal inputs/outputs/queries...) se ejecutan con `ng generate @angular/core:<migración>`; comprueba los nombres disponibles en la referencia de migraciones de la versión instalada y aplícalas en commits separados.
6. Valida: build, tests, lint y prueba manual de los flujos críticos de **todas** las aplicaciones afectadas. Revisa en especial los cambios de valores por defecto de la nueva versión (por ejemplo, `OnPush` por defecto en v22, o la hidratación incremental activada por defecto con `provideClientHydration()` en v22).

**Reglas**:

- Actualizar Angular CLI + Core juntos siempre, siguiendo la guía oficial de actualización de la versión destino.
- No mezclar actualizaciones mayores en el mismo PR.
- Commitear siempre el lockfile actualizado.
