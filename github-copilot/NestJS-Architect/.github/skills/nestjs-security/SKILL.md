---
name: nestjs-security
description: 'Backend NestJS (API). Seguridad del código en NestJS frente a vulnerabilidades (OWASP Top 10 y OWASP API Security): inyección SQL/NoSQL/comandos, path traversal, SSRF, asignación masiva, prototype pollution, ReDoS, subida de ficheros, límites de tamaño y rate limiting, helmet, CORS, cookies y CSRF, secretos, criptografía, fugas de información, dependencias y revisión de seguridad. Usar cuando: revisar código por vulnerabilidades, manejar ficheros, llamar a URLs externas, ejecutar procesos, endurecer la configuración, auditar dependencias o preparar una revisión de seguridad antes de un PR.'
argument-hint: 'Describe el código a revisar o el escenario (ficheros, URLs externas, cabeceras, dependencias...).'
---

# Seguridad del código

Esta skill cubre **que el código no sea vulnerable**. La autenticación, los guards de roles y la autorización por recurso están en `nestjs-auth`.

Principio base: **toda entrada externa es hostil** hasta validarla. Entrada externa es el body, query, params y cabeceras HTTP, los argumentos GraphQL, los payloads de mensajes, los ficheros subidos, las respuestas de APIs de terceros y las variables de entorno.

## Validación como frontera (A03 / API3)

- Toda entrada pasa por DTOs validados con `ValidationPipe` (`whitelist: true`, `forbidNonWhitelisted: true`, `transform: true`). Detalle en `nestjs-dto-validation`.
- Límites en todo campo de tamaño variable (`@MaxLength`, `@Max`, `@ArrayMaxSize`): sin ellos, un único campo puede consumir memoria o CPU.

### Asignación masiva

Un DTO que acepta campos que el usuario no debe controlar (`role`, `isAdmin`, `ownerId`, `price`) permite escalar privilegios aunque la autenticación sea correcta.

```typescript
// ❌ El usuario puede enviar { "role": "admin" }
await this.userRepository.update(id, body as Partial<UserEntity>);

// ✅ DTO específico con solo los campos editables por el usuario
export class UpdateProfileDto {
  @IsOptional() @IsString() @MaxLength(100) displayName?: string;
  @IsOptional() @IsString() @MaxLength(500) bio?: string;
}

await this.userRepository.update(id, {
  displayName: dto.displayName,
  bio: dto.bio,
});
```

- Nunca pases el body, o un objeto derivado de él, directamente a `save`, `update`, `create` ni a un `Object.assign` sobre una entidad.
- Copia campo a campo desde el DTO validado; los campos sensibles (`role`, `ownerId`) se asignan en el servicio a partir del usuario autenticado.

### Prototype pollution

- No hagas *merge* profundo de objetos de entrada sobre objetos existentes (`lodash.merge`, `Object.assign` recursivo propio) sin filtrar `__proto__`, `constructor` y `prototype`.
- `whitelist: true` sobre DTOs de clase elimina las claves no declaradas; es la principal defensa. Evita aceptar `Record<string, unknown>` libre en DTOs.

### ReDoS

- Las expresiones regulares con cuantificadores anidados (`(a+)+`, `(.*)*`) aplicadas a entrada del usuario pueden bloquear el event loop de Node con una entrada diseñada para ello: un único hilo bloqueado deja sin servicio a toda la aplicación.
- Usa validadores de `class-validator` en lugar de expresiones propias cuando existan, limita la longitud **antes** de aplicar la expresión y revisa las expresiones complejas.

## Inyección (A03)

### SQL y NoSQL

- Consultas siempre **parametrizadas**, nunca concatenación de strings (ver `nestjs-persistence`):

```typescript
// ✅ Parametrizado
await this.dataSource.query('SELECT * FROM users WHERE email = $1', [email]);
// ❌ Inyección SQL
await this.dataSource.query(`SELECT * FROM users WHERE email = '${email}'`);
```

- Los nombres de columna o de ordenación que llegan del cliente se validan contra una lista permitida; no se pueden parametrizar:

```typescript
const SORTABLE = ['createdAt', 'email'] as const;
export class ListUsersQueryDto {
  @IsOptional() @IsIn(SORTABLE) sortBy?: (typeof SORTABLE)[number];
}
```

- Con bases de datos NoSQL (MongoDB), no pases objetos de entrada sin validar como filtros: `{ "password": { "$ne": null } }` evita la comparación. Valida que los campos sean del tipo primitivo esperado.

### Comandos del sistema

- Evita ejecutar procesos. Si es imprescindible, usa `execFile`/`spawn` con el ejecutable y los argumentos separados, **nunca** `exec` con un string construido a partir de entrada del usuario (se interpreta por la shell):

```typescript
// ❌ Inyección de comandos: filename = "a.pdf; rm -rf /"
exec(`convert ${filename} out.png`);

// ✅ Sin shell; argumentos como array, valor validado previamente
execFile('convert', [validatedPath, outputPath]);
```

### Path traversal

Una ruta construida con entrada del usuario puede salir del directorio previsto (`../../etc/passwd`):

```typescript
const UPLOAD_ROOT = resolve(config.getOrThrow<string>('UPLOAD_DIR'));

function safePath(fileName: string): string {
  const target = resolve(UPLOAD_ROOT, fileName);
  if (!target.startsWith(UPLOAD_ROOT + sep)) {
    throw new BadRequestException('Invalid file name');
  }
  return target;
}
```

Mejor aún: no uses el nombre que envía el usuario; genera el nombre en el servidor (`randomUUID()`) y guarda el nombre original solo como metadato.

## SSRF — peticiones a URLs externas (A10 / API7)

Si el servidor hace peticiones a una URL que aporta el usuario (webhooks, importar desde URL, vista previa de enlaces), un atacante puede apuntar a servicios internos (`http://localhost`, `http://169.254.169.254` de metadatos cloud, la red interna).

- Usa una **lista permitida** de dominios cuando sea posible.
- Si no, acepta solo `https`, resuelve el DNS y rechaza IPs privadas, de loopback, link-local y de metadatos; vuelve a comprobar tras las redirecciones (o desactívalas).
- Timeout y límite de tamaño de respuesta en toda petición saliente.
- Nunca devuelvas al cliente el contenido o los errores en bruto de la petición interna.

## Subida de ficheros

```typescript
@Post('avatar')
@UseInterceptors(FileInterceptor('file', { limits: { fileSize: 2 * 1024 * 1024, files: 1 } }))
uploadAvatar(
  @UploadedFile(
    new ParseFilePipeBuilder()
      .addFileTypeValidator({ fileType: /^image\/(png|jpeg|webp)$/ })
      .addMaxSizeValidator({ maxSize: 2 * 1024 * 1024 })
      .build({ errorHttpStatusCode: HttpStatus.UNPROCESSABLE_ENTITY }),
  )
  file: Express.Multer.File,
  @CurrentUser() user: AuthenticatedUser,
): Promise<void> {
  return this.avatarsService.store(user.id, file);
}
```

- Límites de tamaño y número de ficheros en el interceptor (si no, Multer acepta lo que llegue).
- No confíes en la extensión ni en el `Content-Type` del cliente: comprueba el tipo real por contenido (*magic bytes*) cuando sea relevante. La validación de tipo del pipe depende de la versión de Nest; compruébala.
- Nombre generado en el servidor; nunca rutas a partir del nombre original.
- Guarda los ficheros fuera del directorio servido como estático, o en almacenamiento de objetos, y sírvelos con `Content-Disposition: attachment` si no son imágenes de confianza.
- Para ficheros de usuarios no confiables, considera análisis antivirus.
- El adaptador por defecto (Multer) es de Express; con Fastify se usa otro plugin.

## Límites y protección frente a abuso (API4)

### Rate limiting

```typescript
@Module({
  imports: [ThrottlerModule.forRoot([{ ttl: 60_000, limit: 100 }])],
  providers: [{ provide: APP_GUARD, useClass: ThrottlerGuard }],
})
export class AppModule {}

// Límite específico en endpoints sensibles
@Throttle({ default: { limit: 5, ttl: 60_000 } })
@Public()
@Post('login')
login(@Body() dto: LoginDto): Promise<TokenResponseDto> { ... }
```

- Límites más estrictos en login, registro, recuperación de contraseña, envío de emails/SMS y operaciones costosas.
- Detrás de un proxy o balanceador, configura `trust proxy` para que el throttler use la IP real del cliente y no la del proxy.
- Con varias réplicas, el almacenamiento por defecto (memoria) no se comparte: usa un *storage* distribuido (Redis) o aplica el límite en el API gateway.
- En GraphQL, el throttler necesita adaptarse al contexto (`GqlThrottlerGuard`, ver `nestjs-graphql`).

### Tamaño y coste de las peticiones

- Limita el tamaño del body en el adaptador HTTP (`app.useBodyParser('json', { limit: '1mb' })` en Express, `bodyLimit` en Fastify).
- Paginación obligatoria con tamaño máximo en todos los listados.
- Timeouts en peticiones salientes y en el procesamiento (ver `TimeoutInterceptor` en `nestjs-request-pipeline`).
- En GraphQL, límites de profundidad y complejidad (ver `nestjs-graphql`).

## Configuración segura (A05)

### Cabeceras

```typescript
// main.ts (Express)
app.use(helmet());
// Fastify: await app.register(helmet) con @fastify/helmet
```

- `helmet()` añade cabeceras de seguridad HTTP. Si sirves Swagger UI o una interfaz de exploración GraphQL, puede requerir ajustar la CSP en los entornos donde estén habilitadas.
- Oculta `X-Powered-By` (helmet lo hace) y no expongas versiones de librerías.

### CORS

```typescript
app.enableCors({
  origin: config.getOrThrow<string>('CORS_ORIGINS').split(','),
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  credentials: true,
});
```

- Configura CORS explícitamente con una lista de orígenes: nunca `origin: '*'` en producción, y nunca `'*'` (ni reflejar cualquier `Origin`) junto con `credentials: true`.
- Declara los métodos permitidos de forma explícita: con Fastify 5 (Nest 11+), por defecto solo se permiten los métodos simples y las peticiones `PUT`/`PATCH`/`DELETE` del navegador fallarían.
- CORS protege a los navegadores, no a la API: no sustituye a la autenticación.

### Cookies y CSRF

Si la autenticación viaja en cookies (sesión o token en cookie), el navegador las adjunta automáticamente y la aplicación es vulnerable a CSRF:

- Cookies `HttpOnly; Secure; SameSite=Lax` (o `Strict`), con el ámbito (`Path`, `Domain`) mínimo.
- Protección CSRF (token sincronizado o *double submit*) en las operaciones que modifican estado.
- Con autenticación solo por cabecera `Authorization: Bearer` y sin cookies, el CSRF clásico no aplica.

### Entornos

- Documentación de la API, introspección GraphQL y endpoints de depuración desactivados o protegidos en producción.
- Nunca `synchronize: true` en producción (ver `nestjs-persistence`).

## Secretos (A02 / A05)

- Secretos solo en variables de entorno o en un gestor de secretos; **nunca** en el código, en `.env` versionado, en tests ni en ejemplos (ver `nestjs-config`).
- Ni en logs, ni en mensajes de error, ni en respuestas de la API.
- Si un secreto se ha commiteado, **rótalo**: borrarlo del historial no basta.
- Credenciales distintas por entorno y por servicio, con permisos mínimos (base de datos, broker, APIs externas). En un monorepo, cada aplicación tiene las suyas.

## Criptografía (A02)

- Valores aleatorios con fines de seguridad (tokens de reseteo, identificadores no adivinables, nonces) con `crypto.randomUUID()` / `crypto.randomBytes()`, **nunca** `Math.random()`.
- Comparación de secretos (tokens, firmas HMAC de webhooks) en tiempo constante con `crypto.timingSafeEqual`:

```typescript
function isValidSignature(payload: Buffer, signature: string, secret: string): boolean {
  const expected = createHmac('sha256', secret).update(payload).digest();
  const received = Buffer.from(signature, 'hex');
  return received.length === expected.length && timingSafeEqual(received, expected);
}
```

- No implementes algoritmos criptográficos propios. Para cifrar datos usa AES-GCM con claves gestionadas fuera del código.
- Contraseñas: ver `nestjs-auth`.
- Tráfico siempre con TLS, también entre servicios y hacia la base de datos y el broker.

## Fugas de información (A04 / A09)

- Errores sin stack traces, mensajes de base de datos ni rutas internas (ver `nestjs-error-handling`).
- Respuestas con DTOs, nunca entidades: evita exponer campos internos (ver `nestjs-dto-validation`). En listados, devuelve solo los campos necesarios (API3: exposición excesiva de datos).
- Logs sin contraseñas, tokens, cabeceras `Authorization`, cuerpos completos ni datos personales (ver `nestjs-quality`).
- Mensajes que no revelen la existencia de recursos o cuentas (404 ante recursos ajenos, mismo error en login).
- En un monorepo con el frontend, ninguna librería del backend (entidades, configuración, servicios) puede llegar al bundle del navegador: compártelo solo mediante contratos de tipos (ver `nestjs-monorepo`).

## Deserialización y datos de terceros (A08)

- No uses `eval`, `new Function`, `vm` ni deserializadores que ejecuten código con datos externos.
- Valida las respuestas de APIs externas y los payloads de webhooks (firma + esquema) antes de usarlos.

## Dependencias (A06)

```powershell
npm audit                  # vulnerabilidades del árbol instalado
npm audit --omit=dev       # solo dependencias de producción
npm ci                     # instalación reproducible a partir del lockfile
```

- Lockfile siempre versionado; en CI se instala con `npm ci`.
- Antes de añadir un paquete: mantenimiento, uso, licencia, vulnerabilidades conocidas y necesidad real.
- Sin vulnerabilidades críticas o altas sin parche en producción; las moderadas se evalúan y documentan.
- Actualizaciones periódicas, una dependencia (o familia compatible) cada vez, con build y tests.

## Logging y monitorización de seguridad (A09)

- Registra los eventos relevantes: logins fallidos, accesos denegados (401/403), cambios de permisos, errores de validación repetidos y límites de rate alcanzados.
- Con `correlationId` y sin datos sensibles, para poder investigar incidentes.

## Checklist de revisión de seguridad

- [ ] Toda entrada validada con DTOs de clase, con límites de tamaño
- [ ] Sin asignación masiva: DTOs específicos y copia campo a campo
- [ ] Autenticación y autorización por recurso revisadas (ver `nestjs-auth`)
- [ ] Consultas parametrizadas; columnas de ordenación en lista permitida
- [ ] Sin `exec` con entrada del usuario; rutas de fichero dentro del directorio previsto
- [ ] URLs externas controladas frente a SSRF, con timeout
- [ ] Subidas con límite de tamaño, tipo validado y nombre generado en el servidor
- [ ] Expresiones regulares seguras sobre entrada limitada
- [ ] Rate limiting (estricto en endpoints sensibles), límite de body y paginación
- [ ] Helmet, CORS con lista de orígenes y métodos, y cookies/CSRF correctos
- [ ] Sin secretos en código, logs, errores ni respuestas
- [ ] `randomUUID`/`randomBytes` y `timingSafeEqual` donde corresponda
- [ ] Errores y respuestas sin información interna
- [ ] `npm audit` sin vulnerabilidades críticas o altas
- [ ] Eventos de seguridad registrados
