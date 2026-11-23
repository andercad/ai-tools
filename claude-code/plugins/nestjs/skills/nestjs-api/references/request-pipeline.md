# Interceptores, pipes y middleware

## Orden de ejecución

Petición → **Middleware** → **Guards** → **Interceptores (antes)** → **Pipes** → Controlador → **Interceptores (después)** → **Filtros de excepción** (si hay error) → Respuesta.

| Necesidad                                        | Usa             |
| ------------------------------------------------ | --------------- |
| Acceso temprano a la petición (correlación, logs) | Middleware      |
| Decidir si la petición puede continuar           | Guard (ver `nestjs-security`; rate limiting en `nestjs-security`) |
| Envolver el handler (tiempos, transformación, timeout, caché) | Interceptor |
| Validar o transformar un argumento               | Pipe            |
| Convertir una excepción en respuesta             | Filtro (ver `nestjs-api`) |

El middleware solo se ejecuta en peticiones HTTP (incluido el endpoint HTTP de GraphQL), no en handlers de mensajes de microservicios. Guards, interceptores, pipes y filtros se ejecutan en todos los contextos.

En un monorepo, los interceptores, pipes, filtros y middleware comunes a varias aplicaciones viven en una librería `util`; cada aplicación los registra en su `AppModule` (ver `nestjs-workspace`).

## Interceptores

- Implementa `NestInterceptor` como clase con `@Injectable()`.
- Cada interceptor tiene **una única responsabilidad** (logging, transformación de respuesta, caché, etc.):

```typescript
export interface ResponseEnvelope<T> {
  readonly data: T;
  readonly timestamp: string;
}

@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, ResponseEnvelope<T>> {
  intercept(context: ExecutionContext, next: CallHandler<T>): Observable<ResponseEnvelope<T>> {
    return next.handle().pipe(map((data) => ({ data, timestamp: new Date().toISOString() })));
  }
}
```

- Un envoltorio de respuesta (`{ data, timestamp }`) cambia el contrato de toda la API: aplícalo solo si el `CLAUDE.md` del proyecto lo define, y refléjalo en Swagger. No lo apliques a resolvers GraphQL: rompería la forma de los tipos.

```typescript
@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger('HTTP');

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    if (context.getType() !== 'http') {
      return next.handle(); // GraphQL y mensajería tienen su propio logging
    }
    const request = context.switchToHttp().getRequest<{ method: string; url: string }>();
    const start = Date.now();
    return next.handle().pipe(
      tap(() => this.logger.log(`${request.method} ${request.url} ${Date.now() - start}ms`)),
    );
  }
}

@Injectable()
export class TimeoutInterceptor implements NestInterceptor {
  intercept(_context: ExecutionContext, next: CallHandler): Observable<unknown> {
    return next.handle().pipe(
      timeout(10_000),
      catchError((error: unknown) =>
        throwError(() => (error instanceof TimeoutError ? new RequestTimeoutException() : error)),
      ),
    );
  }
}
```

- No registres en logs el body ni las cabeceras completas (pueden contener contraseñas, tokens o datos personales).
- Un interceptor global se ejecuta también en resolvers GraphQL y en handlers de mensajes. Si usa `switchToHttp()`, comprueba antes `context.getType()` (`'http'`, `'graphql'`, `'rpc'`) y obtén los datos de cada contexto (`GqlExecutionContext`, `context.switchToRpc()`), o sáltalo en los contextos que no correspondan.
- Registra interceptores globales con `app.useGlobalInterceptors()` o con `APP_INTERCEPTOR` en el módulo para acceso a DI. Prefiere `APP_INTERCEPTOR`: también se aplica en los tests e2e que no ejecutan `main.ts`.

## Pipes

- Implementa `PipeTransform` para transformación y validación personalizada.
- Usa los pipes built-in (`ParseIntPipe`, `ParseUUIDPipe`, `ParseEnumPipe`, `ParseBoolPipe`, `DefaultValuePipe`) antes de crear uno propio.
- Los pipes personalizados deben ser `@Injectable()` para poder inyectar dependencias.

```typescript
@Injectable()
export class ParsePositiveIntPipe implements PipeTransform<string, number> {
  transform(value: string, metadata: ArgumentMetadata): number {
    const parsed = Number(value);
    if (!Number.isInteger(parsed) || parsed <= 0) {
      throw new BadRequestException(`${metadata.data ?? 'value'} must be a positive integer`);
    }
    return parsed;
  }
}
```

- Un pipe valida o transforma; no consulta reglas de negocio complejas (eso es del servicio).

## Middleware

- Usa middleware para lógica transversal previa al enrutamiento (logging de petición, correlación de IDs).
- Implementa `NestMiddleware` o usa funciones Express/Fastify directamente.
- Registra en el `AppModule` o en el módulo afectado mediante `configure(consumer: MiddlewareConsumer)`.
- Prefiere interceptores para transformaciones de respuesta; reserva middleware para acceso temprano al ciclo de vida.

```typescript
@Injectable()
export class CorrelationIdMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: () => void): void {
    const incoming = req.header('x-correlation-id');
    // Aceptar solo valores con formato válido para evitar inyección en logs
    const correlationId = incoming && /^[\w-]{1,64}$/.test(incoming) ? incoming : randomUUID();
    req.headers['x-correlation-id'] = correlationId;
    res.setHeader('x-correlation-id', correlationId);
    next();
  }
}

@Module({ ... })
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer.apply(CorrelationIdMiddleware).forRoutes('{*splat}'); // todas las rutas, incluida la raíz
  }
}
```

- Los tipos `Request`/`Response` dependen del adaptador (Express o Fastify). Usa los del adaptador instalado; con Fastify los middleware reciben los objetos raw de Node.
- **Comodines (Nest 11+, Express 5)**: deben tener nombre. Usa `'{*splat}'` (incluye la raíz) o `'*splat'`; el nombre es libre. Nest convierte `'*'` con un aviso, pero no lo uses en código nuevo. Lo mismo aplica a rutas de controladores (`@Get('files/*splat')`). En Nest 10 o anterior (Express 4) la sintaxis era `'*'`.
- Al publicar mensajes, propaga el `correlationId` en el payload o las cabeceras del mensaje (ver `nestjs-microservices`).

## Checklist

- [ ] Cada pieza en la capa correcta del ciclo de vida
- [ ] Una responsabilidad por interceptor, pipe o middleware
- [ ] Globales con `APP_INTERCEPTOR`/`APP_PIPE` cuando necesitan DI
- [ ] Interceptores globales compatibles con los contextos del proyecto (`http`, `graphql`, `rpc`)
- [ ] Pipes built-in antes que propios
- [ ] Sin datos sensibles en los logs de petición
- [ ] Tipos de `Request`/`Response` del adaptador instalado
