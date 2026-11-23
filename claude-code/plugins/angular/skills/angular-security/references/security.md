
# Seguridad

Principio base: **el frontend no es una frontera de seguridad**. Todo lo que se ejecuta en el navegador puede ser inspeccionado y modificado. La validación y la autorización reales las hace siempre el backend.

## Datos sensibles — Dominio del proyecto

Ver el `CLAUDE.md` del proyecto → _Cliente y contexto_ para las restricciones específicas del dominio (tipo de datos, normativa aplicable). Reglas de implementación:

- **No almacenar** datos sensibles ni PII en `localStorage`, `sessionStorage`, IndexedDB ni cookies accesibles desde JavaScript.
- Mantener los datos sensibles **exclusivamente en memoria** (signals de servicio).
- **Limpiar el estado** al cerrar sesión: resetear todas las signals de estado, cancelar peticiones pendientes.
- No loguear datos sensibles en `console.*`, analíticas ni herramientas de monitorización.
- No incluir datos identificativos en parámetros de URL (query params o path params): quedan en historial, logs de servidor y cabecera `Referer`.

```typescript
@Injectable({ providedIn: 'root' })
export class SessionService {
  // ========== Dependencies ==========
  private readonly router = inject(Router);

  // ========== State ==========
  // ✅ Estado en memoria — nunca en localStorage
  private readonly _currentCustomer = signal<Customer | null>(null);
  readonly currentCustomer = this._currentCustomer.asReadonly();

  // ========== Public methods ==========
  logout(): void {
    // Limpiar TODO el estado sensible en memoria
    this._currentCustomer.set(null);
    this.router.navigate(['/login']);
  }
}
```

## Sanitización HTML y XSS

Angular escapa automáticamente el contenido interpolado (`{{ }}`) y sanitiza los bindings a propiedades peligrosas. Para HTML dinámico:

```html
<!-- ✅ innerHTML — Angular sanitiza antes de insertar -->
<div [innerHTML]="trustedHtml"></div>

<!-- ❌ Nunca construir HTML por concatenación -->
<div [innerHTML]="'<b>' + userName + '</b>'"></div>
```

Evitar `bypassSecurityTrustHtml` salvo casos documentados:

```typescript
// ⚠️ Solo cuando el HTML viene de una fuente controlada (ej. editor CMS propio),
// se ha sanitizado en el servidor con una librería de sanitización
// y no puede contener contenido aportado por usuarios no confiables.
// Documentar la justificación junto al código.
readonly safeContent = computed(() =>
  this.sanitizer.bypassSecurityTrustHtml(this.content())
  // Justificación: contenido generado por el editor interno,
  // sanitizado por el API antes de persistir.
);
```

Nunca usar:

- `bypassSecurityTrustScript`
- `bypassSecurityTrustResourceUrl` (salvo iframes de dominio propio, con justificación)
- `eval()`, `Function()`, `setTimeout(string)`
- `document.write()`

## Tokens de autenticación

- Almacenar tokens en **memoria** (service signal), no en `localStorage`.
- Si se necesita persistencia entre recargas, usar cookies `HttpOnly; Secure; SameSite` gestionadas por el servidor (o un patrón BFF), no almacenamiento accesible desde JavaScript.
- El token se adjunta **solo** en el `auth-interceptor`. Ningún componente ni servicio de negocio debe leer ni adjuntar tokens manualmente.
- Adjuntar el token **solo a peticiones dirigidas a la API propia**, nunca a dominios de terceros.
- No loguear tokens, no incluirlos en URLs, no exponerlos en mensajes de error.

```typescript
// ✅ auth-interceptor.ts — único punto de adjuntar el token
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const apiBaseUrl = inject(API_BASE_URL);
  const token = authService.getAccessToken(); // solo en memoria

  if (!token || !req.url.startsWith(apiBaseUrl) || isPublicEndpoint(req.url)) {
    return next(req);
  }

  return next(
    req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    }),
  );
};

function isPublicEndpoint(url: string): boolean {
  return ['/auth/login', '/auth/refresh', '/public/'].some((path) => url.includes(path));
}
```

## Validación de inputs

Validar en cliente mejora la experiencia de usuario y evita peticiones inútiles. **No sustituye la validación del servidor**: el backend debe validar y autorizar siempre, porque cualquier petición puede enviarse sin pasar por la aplicación.

```typescript
// En servicios: verificar precondiciones antes de llamar
createOrder(data: OrderForm): Observable<Order> {
  if (!data.customerId || !data.productCode) {
    throw new Error('customerId y productCode son obligatorios');
  }

  // Normalizar strings antes de enviar
  const payload: CreateOrderDto = {
    customerId: data.customerId.trim(),
    productCode: data.productCode.trim().toUpperCase(),
    quantity: data.quantity,
  };

  return this.http.post<Order>('/api/orders', payload);
}
```

## Identificadores y autorización

Usar identificadores no secuenciales (UUID) en URLs públicas reduce la enumeración, pero **no es un control de acceso**. El backend debe comprobar que el usuario tiene permiso sobre cada recurso solicitado.

## Auditoría de dependencias

Antes de instalar cualquier paquete de terceros (proceso completo en `environment.md`):

```powershell
# 1. Auditar vulnerabilidades del árbol actual
npm audit

# 2. Revisar metadatos y licencia del paquete antes de instalar
npm view <package-name> version license

# 3. Tras instalarlo en una rama de trabajo, volver a auditar
npm audit

# 4. Verificar en Snyk Advisor u OSV
# https://snyk.io/advisor/npm-package/<package-name>
# https://osv.dev/
```

**Criterios de bloqueo** (salvo política corporativa distinta):

- ❌ Vulnerabilidades **críticas** o **altas** sin parche → no instalar
- ⚠️ Vulnerabilidades **moderadas** → evaluar impacto y alternativas
- ✅ Solo vulnerabilidades **bajas** → aceptable con documentación

Mantener `npm audit` limpio en el CI. No acumular deuda de seguridad.

## CSRF

CSRF afecta a las peticiones en las que el navegador adjunta credenciales automáticamente (cookies). Analiza el modelo real de autenticación:

- Si **todas** las llamadas a la API se autentican solo con `Authorization: Bearer` y no hay cookies de sesión, el riesgo CSRF clásico no aplica a esas llamadas.
- Si hay **cookies de sesión** (incluido un BFF o un refresh token en cookie), el servidor debe implementar protección CSRF (token + `SameSite`). El cliente lee el token de la cookie `XSRF-TOKEN` y lo envía en la cabecera `X-XSRF-TOKEN`:

```typescript
// app.config.ts — si se usan cookies de sesión
provideHttpClient(
  withInterceptors([...]),
  withXsrfConfiguration({
    cookieName: 'XSRF-TOKEN',
    headerName: 'X-XSRF-TOKEN',
  }),
)
```

## Content Security Policy (CSP)

La configuración de CSP es responsabilidad del servidor (ver la configuración del servidor web del proyecto, p. ej. `nginx.conf`). No usar `unsafe-inline` ni `unsafe-eval` en scripts. Si se necesita CSP con nonce para estilos/scripts de Angular, consultar la documentación oficial de la versión instalada (`ngCspNonce` / `CSP_NONCE`).

## SSR y monorepos

- Con SSR aparece código que se ejecuta en un servidor Node: validación de hosts permitidos (SSRF), estado compartido entre peticiones y caché de respuestas HTTP transferidas al navegador. Ver la sección de seguridad de la skill `angular-developer` (oficial).
- En un monorepo con el backend, el frontend nunca importa librerías del backend: incluiría código de servidor en el bundle que descarga el navegador (ver `monorepo.md`).

## Checklist de seguridad por PR

- [ ] No hay datos sensibles/PII en `localStorage`, `sessionStorage`, IndexedDB ni cookies legibles por JS
- [ ] No hay tokens en URLs, logs ni mensajes de error
- [ ] El token solo se adjunta a la API propia
- [ ] No hay `bypassSecurityTrust*` sin comentario de justificación
- [ ] No hay `eval()`, `Function()` ni `document.write()`
- [ ] Los inputs de formulario están validados en cliente (UX) y el backend los valida igualmente
- [ ] `npm audit` sin vulnerabilidades críticas o altas
- [ ] No hay `console.*` con datos personales o sensibles
- [ ] No hay datos identificativos en path/query params
