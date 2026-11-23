---
name: angular-ssr
description: 'Frontend Angular. Renderizado en servidor (SSR), prerenderizado (SSG) e hidratación en Angular con @angular/ssr. Usar cuando: activar o configurar SSR, decidir el modo de renderizado de cada ruta (Server, Prerender, Client), prerenderizar rutas con parámetros, hidratación e hidratación incremental, errores como "window is not defined" o "document is not defined", código que debe funcionar en servidor y navegador, acceder a la petición o fijar códigos de estado y cabeceras en el servidor, transferir datos al navegador sin repetir peticiones, rutas o redirecciones que fallan solo en producción con SSR, allowedHosts, desplegar el servidor Node. Cubre app.routes.server.ts, RenderMode, getPrerenderParams, provideClientHydration, REQUEST, RESPONSE_INIT, TransferState, seguridad y diagnóstico.'
argument-hint: 'Describe qué necesitas: activar SSR, configurar una ruta, un error en servidor o un problema que solo ocurre en producción.'
---

# SSR, prerenderizado e hidratación

**No actives SSR por iniciativa propia.** Aplica esta skill cuando el proyecto ya usa `@angular/ssr` o cuando se pida expresamente. Las APIs de SSR han cambiado en cada versión reciente (v19, v20, v22): comprueba la versión instalada y la guía oficial antes de copiar un ejemplo.

## Cuándo compensa

| Modo | Qué hace | Úsalo para |
|---|---|---|
| `RenderMode.Prerender` (SSG) | HTML generado en el build | Páginas públicas cuyo contenido es igual para todos (landing, ayuda, catálogo estable) |
| `RenderMode.Server` (SSR) | HTML generado en cada petición | Páginas públicas con datos cambiantes o que dependen de la petición (SEO + datos frescos) |
| `RenderMode.Client` (CSR) | El navegador renderiza todo | Áreas privadas tras login, pantallas muy interactivas, rutas que dependen de APIs del navegador |

SSR mejora LCP y SEO, pero añade un servidor Node que operar, código que debe funcionar en dos entornos y riesgos de seguridad nuevos. En una aplicación interna detrás de login, el beneficio suele ser bajo.

## Activar SSR

```powershell
# Proyecto nuevo
ng new mi-app --ssr

# Proyecto existente (en un monorepo, indica la aplicación: ng add @angular/ssr --project portal)
ng add @angular/ssr
```

En un monorepo Nx, las aplicaciones con SSR se generan con la opción `--ssr` del generador de `@nx/angular` o se añade con su generador de SSR; comprueba el nombre del generador en la versión instalada (ver `angular-monorepo`).

Ficheros que añade (pueden variar según versión):

```
server.ts                         ← servidor Node (Express) que usa el motor de Angular
src/main.server.ts                ← arranque de la aplicación en servidor
src/app/app.config.server.ts      ← providers solo de servidor
src/app/app.routes.server.ts      ← modo de renderizado por ruta
```

`outputMode` en `angular.json` decide el resultado del build: `server` (servidor Node + rutas prerenderizadas) o `static` (solo ficheros estáticos, sin servidor).

## Rutas de servidor

```typescript
// app.routes.server.ts
import { inject } from '@angular/core';
import { RenderMode, type ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  { path: '', renderMode: RenderMode.Prerender },
  { path: 'ayuda', renderMode: RenderMode.Prerender },
  {
    path: 'productos/:id',
    renderMode: RenderMode.Prerender,
    async getPrerenderParams() {
      const catalog = inject(CatalogService);
      const ids = await catalog.getPublishedIds(); // Promise<string[]>
      return ids.map((id) => ({ id })); // genera /productos/1, /productos/2...
    },
  },
  { path: 'noticias/:slug', renderMode: RenderMode.Server },
  { path: 'area-privada/**', renderMode: RenderMode.Client },
  { path: 'no-encontrado', renderMode: RenderMode.Server, status: 404 },
  { path: '**', renderMode: RenderMode.Server },
];
```

```typescript
// app.config.server.ts
import { mergeApplicationConfig, type ApplicationConfig } from '@angular/core';
import { provideServerRendering, withRoutes } from '@angular/ssr';
import { appConfig } from './app.config';
import { serverRoutes } from './app.routes.server';

const serverConfig: ApplicationConfig = {
  providers: [provideServerRendering(withRoutes(serverRoutes))],
};

export const config = mergeApplicationConfig(appConfig, serverConfig);
```

**Reglas**:

- Cada `path` de servidor debe corresponder a una ruta de `app.routes.ts`. Un patrón que no coincide (por ejemplo, una ruta cliente con `matcher` personalizado) produce un error en el build.
- Una ruta con parámetros en modo `Prerender` necesita `getPrerenderParams`; sin él, el build falla. Si los parámetros no se conocen en build, usa `RenderMode.Server`.
- `getPrerenderParams` se ejecuta en el build: no puede depender de la petición ni del usuario.
- El orden importa: rutas específicas antes que `**`.
- `status` y `headers` en la ruta fijan código y cabeceras HTTP (por ejemplo, `Cache-Control` para CDN).
- En versiones anteriores a la API `provideServerRendering(withRoutes(...))` (v19) se usaba `provideServerRoutesConfig`; no mezcles ambas.

## Código que funciona en servidor y navegador

En el servidor no existen `window`, `document` del navegador, `localStorage`, `sessionStorage`, `navigator` ni las APIs de layout. Los constructores, inicializadores de campo, `effect()`, guards, resolvers e interceptores **se ejecutan en ambos entornos**.

| Necesitas | Solución |
|---|---|
| Tocar el DOM real o una librería de navegador (gráficas, mapas) | `afterNextRender()` (solo se ejecuta en el navegador) |
| El `Document` (título, meta, `<link>`) | `inject(DOCUMENT)` o los servicios `Title`/`Meta`; nunca `document` global |
| `localStorage`, `navigator`, `matchMedia` | Un servicio abstraído con implementación de navegador y de servidor |
| Saber dónde se ejecuta | `isPlatformBrowser(inject(PLATFORM_ID))` — último recurso, no la primera opción |
| Componente imposible de hidratar (manipula el DOM directamente) | Atributo `ngSkipHydration` en su host, documentando el motivo |

```typescript
// Abstracción del almacenamiento: el componente no sabe en qué plataforma está
export abstract class PreferencesStorage {
  abstract read(key: string): string | null;
  abstract write(key: string, value: string): void;
}

@Injectable()
export class BrowserPreferencesStorage extends PreferencesStorage {
  read(key: string): string | null {
    return localStorage.getItem(key);
  }
  write(key: string, value: string): void {
    localStorage.setItem(key, value);
  }
}

@Injectable()
export class ServerPreferencesStorage extends PreferencesStorage {
  read(): string | null {
    return null; // en el servidor no hay preferencias del usuario
  }
  write(): void {
    // sin efecto en el servidor
  }
}

// app.config.ts → { provide: PreferencesStorage, useClass: BrowserPreferencesStorage }
// app.config.server.ts → { provide: PreferencesStorage, useClass: ServerPreferencesStorage }
```

```typescript
// Librería de navegador: inicializar solo tras el primer render en el navegador
@Component({
  selector: 'app-sales-chart',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<canvas #canvas aria-hidden="true"></canvas>`,
})
export class SalesChartComponent {
  // ========== Inputs ==========
  readonly data = input.required<SalesPoint[]>();

  // ========== Queries ==========
  private readonly canvas = viewChild.required<ElementRef<HTMLCanvasElement>>('canvas');

  // ========== Effects ==========
  private readonly init = afterNextRender(() => {
    this.chart = createChart(this.canvas().nativeElement, this.data());
  });

  // ========== Properties ==========
  private chart?: ChartInstance;
}
```

## Hidratación

```typescript
// app.config.ts
provideClientHydration(withEventReplay()),
```

- La hidratación reutiliza el DOM generado en el servidor. El HTML del servidor y el del primer render del navegador **deben coincidir**: si difieren (fechas con `new Date()`, valores aleatorios, contenido que depende de `localStorage`), Angular avisa de errores de desajuste de hidratación en consola.
- `withEventReplay()` reproduce los clics hechos antes de terminar la hidratación.
- **Hidratación incremental**: activada por defecto con `provideClientHydration()` desde v22, que deja `withIncrementalHydration()` deprecado. En v21 hay que añadir `withIncrementalHydration()`. Se controla con triggers en `@defer`:

```html
@defer (hydrate on viewport) {
<app-related-products [productId]="productId()" />
} @placeholder {
<div class="placeholder-glow" style="height: 240px;" aria-hidden="true"></div>
}

<!-- Contenido estático que nunca necesita interactividad -->
@defer (hydrate never) {
<app-legal-footer />
}
```

## Petición, respuesta y estado

```typescript
// Página 404 renderizada en servidor con el código correcto
@Component({
  selector: 'app-not-found',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<h1>{{ 'errors.not-found' | transloco }}</h1>`,
  imports: [TranslocoPipe],
})
export default class NotFoundComponent implements OnInit {
  // ========== Dependencies ==========
  private readonly responseInit = inject(RESPONSE_INIT, { optional: true });

  // ========== Lifecycle ==========
  ngOnInit(): void {
    if (this.responseInit) {
      this.responseInit.status = 404;
    }
  }
}
```

- `REQUEST`, `RESPONSE_INIT` y `REQUEST_CONTEXT` se importan de `@angular/core` e **inyéctalos siempre con `{ optional: true }`**: valen `null` en el navegador, durante el prerenderizado y mientras se genera el manifiesto de rutas.
- **Datos HTTP**: con `provideClientHydration()`, las respuestas `GET`/`HEAD` hechas con `HttpClient` en el servidor se envían en el HTML y el navegador no repite la petición. Por defecto **no** se cachean las peticiones con cabecera `Authorization`. Ajusta con `withHttpTransferCacheOptions(...)` solo con un motivo claro.
- **Datos que no vienen de `HttpClient`**: `TransferState` con `makeStateKey` para pasar el valor del servidor al navegador.
- **Tareas pendientes**: el servidor espera a que la aplicación se estabilice antes de enviar el HTML. Un `setInterval`, un polling o un WebSocket abiertos en el servidor retrasan o bloquean la respuesta. Arráncalos en `afterNextRender()`. Para trabajo asíncrono propio que el servidor deba esperar, usa `PendingTasks`.

## Autenticación con SSR

El token en memoria del navegador (ver `angular-security`) **no existe en el servidor**. Opciones, de más simple a más compleja:

1. Áreas privadas con `RenderMode.Client`: el servidor solo renderiza lo público. Opción por defecto.
2. Sesión en cookie `HttpOnly` gestionada por un BFF, que el servidor de SSR reenvía al backend. Requiere diseño de seguridad (CSRF, qué cabeceras se reenvían).

Nunca actives `includeRequestsWithAuthHeaders` en la caché de transferencia sin analizarlo: incrusta respuestas privadas en el HTML.

## Seguridad

- **Hosts permitidos (SSRF)**: el motor de SSR valida el `Host` de la petición y responde **400 Bad Request** a los que no conoce. Configúralos en `angular.json` (`build.options.security.allowedHosts`), con la variable `NG_ALLOWED_HOSTS` o en las opciones del motor. Detrás de un proxy, revisa también la confianza en cabeceras `X-Forwarded-*` (`trustProxyHeaders`). No uses comodines sin validar.
- **Estado entre peticiones**: cada petición crea una instancia de la aplicación, así que los servicios `providedIn: 'root'` no se comparten entre usuarios. Las **variables de módulo** (fuera de clases y de DI) sí persisten en el proceso Node: nunca guardes en ellas datos de un usuario.
- **Secretos**: el código del servidor puede leer variables de entorno, pero todo lo que acabe en el HTML o en la caché de transferencia lo verá el navegador.
- **URLs de API**: el servidor puede necesitar una URL interna distinta de la pública. No construyas URLs a partir de cabeceras de la petición sin validar.

## Diagnóstico: "funciona con `ng serve` pero no en producción"

Ejemplo típico: las rutas inválidas no redirigen a la ruta por defecto solo en producción.

1. **Quién atiende la petición**: ¿el servidor Node (`node dist/<app>/server/server.mjs`) o un servidor estático (nginx) sirviendo `dist/<app>/browser`? Con `outputMode: static` o con nginx delante, las rutas no prerenderizadas no las procesa Angular en servidor.
2. **Respuesta real**: `curl -I https://host/ruta-inexistente`. Mira el código (200, 302, 400, 404) y la cabecera `Location`.
   - **400 Bad Request** → host no incluido en `allowedHosts`.
   - **404 del servidor web** → la petición no llega a Angular: falta el fallback del servidor estático o la ruta no está en el servidor.
3. **Rutas de servidor**: comprueba que `**` está en `app.routes.server.ts` con `RenderMode.Server`. Una ruta comodín no se puede prerenderizar: si todo es `Prerender`, las URLs desconocidas no existen como fichero.
4. **`server.ts`**: el motor (`AngularNodeAppEngine.handle`) devuelve `null` cuando ninguna ruta coincide y la petición pasa al siguiente middleware de Express. Revisa qué hace ese middleware.
5. **Build**: revisa los ficheros generados en `dist/<app>/browser` (qué rutas se prerenderizaron) y la salida del build, que lista los modos de cada ruta.
6. Reproduce en local con el servidor de producción (`ng build` + `node dist/.../server.mjs`), no con `ng serve`.

## Tests y verificación

- Prueba la rama de servidor de un servicio proveyendo `{ provide: PLATFORM_ID, useValue: 'server' }` en `TestBed`.
- Comprueba que el HTML del servidor contiene el contenido: `curl -s https://host/ruta | grep "texto esperado"`.
- Comprueba códigos y redirecciones con `curl -I`.
- Revisa la consola del navegador en la primera carga: sin errores de hidratación.

## Checklist

- [ ] SSR justificado y solicitado; modo de renderizado decidido por ruta
- [ ] Rutas de servidor que corresponden a las de cliente; `**` en `RenderMode.Server` si debe resolverse en servidor
- [ ] `getPrerenderParams` en rutas `Prerender` con parámetros
- [ ] Sin `window`/`document`/`localStorage` fuera de `afterNextRender()` o de un servicio abstraído
- [ ] `REQUEST`/`RESPONSE_INIT` inyectados como opcionales
- [ ] Sin timers, polling ni sockets abiertos en el servidor
- [ ] HTML de servidor y cliente coherentes (sin errores de hidratación)
- [ ] Áreas privadas en `RenderMode.Client` o con diseño de sesión explícito
- [ ] `allowedHosts` configurado; sin datos de usuario en variables de módulo
- [ ] Verificado con el servidor de producción y `curl`, no solo con `ng serve`
