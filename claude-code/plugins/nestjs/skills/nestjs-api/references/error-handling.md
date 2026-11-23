# Filtros de excepciones y manejo de errores

## Reglas

- **Nunca** dejes errores sin gestionar (`catch` vacío o solo con `console.error`).
- Usa el filtro de excepciones global para capturar errores no controlados.
- Errores de negocio: lanza `HttpException` o sus subclases (`NotFoundException`, `BadRequestException`, `ConflictException`, `ForbiddenException`...) con el código de estado correcto. Nunca lances `Error` genérico para un error de negocio.
- Si el dominio se ejecuta fuera de HTTP y no quieres acoplarlo, usa errores de dominio y tradúcelos en un filtro (ver `nestjs-modules-services`).
- Errores inesperados: deja que propaguen hasta el filtro global, que los loguea y devuelve `500` (o su equivalente en GraphQL y mensajería).
- **No expongas información sensible** (stack traces, mensajes de base de datos, variables de entorno, rutas internas) en respuestas de error.
- Solo captura (`try/catch`) un error si vas a hacer algo útil con él: traducirlo, añadir contexto o recuperarte. Si lo vuelves a lanzar, conserva el original como `cause`.
- En un monorepo, el filtro global y el formato de error comunes viven en una librería `util` compartida, para que todas las aplicaciones respondan igual (ver `nestjs-workspace`).

## Formato de error

Define un formato único para toda la API (o el del `CLAUDE.md` del proyecto):

```typescript
export interface ErrorResponse {
  readonly statusCode: number;
  readonly error: string;
  readonly message: string | string[];
  readonly path: string;
  readonly timestamp: string;
  readonly correlationId?: string;
}
```

## Filtro global (solo HTTP)

Para aplicaciones que solo exponen una API REST. Un único filtro `@Catch()` sin argumentos captura todo. Usa `HttpAdapterHost` para que funcione con Express y Fastify:

```typescript
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  private readonly logger = new Logger(AllExceptionsFilter.name);

  constructor(private readonly httpAdapterHost: HttpAdapterHost) {}

  catch(exception: unknown, host: ArgumentsHost): void {
    const { httpAdapter } = this.httpAdapterHost;
    const ctx = host.switchToHttp();
    const request = ctx.getRequest<{ url: string; headers: Record<string, string | undefined> }>();

    const isHttp = exception instanceof HttpException;
    const statusCode = isHttp ? exception.getStatus() : HttpStatus.INTERNAL_SERVER_ERROR;

    // getResponse() conserva el detalle (p. ej. la lista de errores de ValidationPipe);
    // exception.message lo perdería.
    const message = isHttp ? this.extractMessage(exception) : 'Internal server error';

    if (!isHttp) {
      // El detalle completo va al log, nunca a la respuesta
      this.logger.error(exception instanceof Error ? exception.stack : String(exception));
    }

    const body: ErrorResponse = {
      statusCode,
      error: HttpStatus[statusCode] ?? 'Error',
      message,
      path: request.url,
      timestamp: new Date().toISOString(),
      correlationId: request.headers['x-correlation-id'],
    };

    httpAdapter.reply(ctx.getResponse(), body, statusCode);
  }

  private extractMessage(exception: HttpException): string | string[] {
    const response = exception.getResponse();
    if (typeof response === 'string') return response;
    const { message } = response as { message?: string | string[] };
    return message ?? exception.message;
  }
}
```

Regístralo con `APP_FILTER` para que tenga acceso a la DI y se aplique también en los tests e2e:

```typescript
@Module({
  providers: [{ provide: APP_FILTER, useClass: AllExceptionsFilter }],
})
export class AppModule {}
```

## Filtro global multicontexto (GraphQL y microservicios)

El filtro anterior responde con `httpAdapter.reply()`, que solo funciona en peticiones HTTP. Un filtro registrado con `APP_FILTER` se ejecuta también en resolvers GraphQL y en handlers de mensajes, donde ese código falla. Si el proyecto usa GraphQL (`nestjs-graphql`) o microservicios (`nestjs-microservices`), usa esta versión, que decide el formato según el contexto:

```typescript
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  private readonly logger = new Logger(AllExceptionsFilter.name);

  constructor(private readonly httpAdapterHost: HttpAdapterHost) {}

  catch(exception: unknown, host: ArgumentsHost): unknown {
    switch (host.getType<string>()) {
      case 'graphql':
        // GraphQL añade el error devuelto al array `errors` de la respuesta
        return this.toGraphqlError(exception);
      case 'rpc':
        // Los transportes de microservicios esperan un Observable que falle
        return throwError(() => this.toRpcError(exception));
      default:
        this.replyHttp(exception, host);
        return undefined;
    }
  }

  // --- HTTP ---
  private replyHttp(exception: unknown, host: ArgumentsHost): void {
    // Mismo cuerpo que el método catch() del filtro solo-HTTP (ErrorResponse + httpAdapter.reply)
  }

  // --- GraphQL ---
  private toGraphqlError(exception: unknown): GraphQLError {
    if (exception instanceof GraphQLError) {
      return exception;
    }
    if (exception instanceof HttpException) {
      const message = this.extractMessage(exception);
      return new GraphQLError(Array.isArray(message) ? 'Validation failed' : message, {
        extensions: {
          code: HttpStatus[exception.getStatus()] ?? 'ERROR', // NOT_FOUND, BAD_REQUEST...
          ...(Array.isArray(message) ? { details: message } : {}),
        },
      });
    }
    this.logUnexpected(exception);
    return new GraphQLError('Internal server error', {
      extensions: { code: 'INTERNAL_SERVER_ERROR' },
    });
  }

  // --- Microservicios ---
  private toRpcError(exception: unknown): RpcErrorPayload {
    if (exception instanceof RpcException) {
      const error = exception.getError();
      return typeof error === 'string'
        ? { statusCode: 500, error: 'RPC_ERROR', message: error }
        : (error as RpcErrorPayload);
    }
    if (exception instanceof HttpException) {
      const statusCode = exception.getStatus();
      return { statusCode, error: HttpStatus[statusCode] ?? 'ERROR', message: this.extractMessage(exception) };
    }
    this.logUnexpected(exception);
    return { statusCode: 500, error: 'INTERNAL_SERVER_ERROR', message: 'Internal server error' };
  }

  // --- Comunes ---
  private extractMessage(exception: HttpException): string | string[] {
    const response = exception.getResponse();
    if (typeof response === 'string') return response;
    const { message } = response as { message?: string | string[] };
    return message ?? exception.message;
  }

  private logUnexpected(exception: unknown): void {
    this.logger.error(exception instanceof Error ? exception.stack : String(exception));
  }
}

interface RpcErrorPayload {
  readonly statusCode: number;
  readonly error: string;
  readonly message: string | string[];
}
```

- `GraphQLError` se importa de `graphql`; `RpcException`, de `@nestjs/microservices`. Elimina las ramas de los contextos que el proyecto no use.
- Los errores de dominio se traducen con la misma idea: código estable en `extensions.code` (GraphQL) o en `error` (mensajería).
- En microservicios, que el filtro devuelva un error **no sustituye** a la estrategia de ack/nack, reintentos y DLQ (ver `nestjs-microservices`).

## Filtros específicos

Un filtro concreto para un tipo de error, por ejemplo errores de dominio en una API REST:

```typescript
@Catch(DomainError)
export class DomainExceptionFilter implements ExceptionFilter {
  constructor(private readonly httpAdapterHost: HttpAdapterHost) {}

  catch(exception: DomainError, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const statusCode = DOMAIN_ERROR_STATUS[exception.code] ?? HttpStatus.UNPROCESSABLE_ENTITY;
    this.httpAdapterHost.httpAdapter.reply(
      ctx.getResponse(),
      { statusCode, error: exception.code, message: exception.message },
      statusCode,
    );
  }
}

const DOMAIN_ERROR_STATUS: Record<string, HttpStatus> = {
  EMAIL_ALREADY_REGISTERED: HttpStatus.CONFLICT,
};
```

Cuando hay varios filtros globales, Nest prueba primero el último registrado: registra el filtro catch-all **antes** que los específicos. Si el proyecto tiene varios contextos, el filtro específico debe aplicar la misma lógica por contexto que el filtro multicontexto.

## Errores de base de datos

Traduce los errores conocidos del driver sin exponer el mensaje original:

```typescript
// Ejemplo PostgreSQL + TypeORM: violación de unicidad
try {
  return await this.userRepository.save(user);
} catch (error: unknown) {
  if (error instanceof QueryFailedError && (error.driverError as { code?: string }).code === '23505') {
    throw new ConflictException('Email already registered', { cause: error });
  }
  throw error;
}
```

Con Prisma, el equivalente es `PrismaClientKnownRequestError` con código `P2002`. Los códigos dependen del motor y del ORM: compruébalos en su documentación.

## Checklist

- [ ] Sin `catch` vacíos ni `console.error`
- [ ] Excepciones HTTP o errores de dominio; nunca `Error` genérico para negocio
- [ ] Filtro global `@Catch()` registrado con `APP_FILTER`
- [ ] Filtro multicontexto si hay GraphQL o microservicios
- [ ] Formato de error único en toda la API
- [ ] Detalle de validación conservado (`getResponse()`)
- [ ] Stack y mensajes internos solo en logs, nunca en la respuesta
- [ ] Errores de base de datos conocidos traducidos (unicidad → 409)
