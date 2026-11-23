---
name: nestjs-auth
description: 'Backend NestJS (API). Autenticación y autorización en NestJS: guards de autenticación y de roles, endpoints públicos con @Public(), Passport y JWT, refresh tokens, contraseñas, @CurrentUser(), autorización por recurso y guards en HTTP, GraphQL y microservicios. Usar cuando: añadir login o registro, proteger endpoints, crear guards o decoradores de roles/permisos, gestionar tokens, comprobar que un usuario solo accede a sus recursos.'
argument-hint: 'Describe qué necesitas autenticar o autorizar (login, roles, permisos, acceso a un recurso).'
---

# Autenticación y autorización

Esta skill cubre **quién es el usuario y qué puede hacer**. La protección del código frente a vulnerabilidades (inyección, SSRF, ficheros, cabeceras, rate limiting, dependencias...) está en `nestjs-security`.

## Guards

- Implementa `CanActivate` como clase con `@Injectable()`:

```typescript
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}
```

- Usa `@UseGuards()` a nivel de controlador o método.
- Un guard tiene **una única responsabilidad**: autenticación o autorización, no ambas.
- Los guards globales que necesitan inyección de dependencias se registran con `APP_GUARD` en un módulo, no con `app.useGlobalGuards()` (que no tiene acceso a la DI del módulo). El orden de registro es el orden de ejecución:

```typescript
@Module({
  providers: [
    { provide: APP_GUARD, useClass: JwtAuthGuard }, // primero autenticación
    { provide: APP_GUARD, useClass: RolesGuard },   // después autorización
  ],
})
export class AppModule {}
```

- En un monorepo, los guards, estrategias y decoradores de autenticación compartidos por varias aplicaciones viven en una librería `util`; cada aplicación los registra en su propio `AppModule` (ver `nestjs-monorepo`).

### Seguro por defecto: endpoints públicos explícitos

Con la autenticación global, todo endpoint queda protegido salvo que se marque explícitamente como público. Es más seguro que proteger endpoint a endpoint, donde un olvido deja un endpoint abierto:

```typescript
export const IS_PUBLIC_KEY = 'isPublic';
export const Public = (): CustomDecorator => SetMetadata(IS_PUBLIC_KEY, true);

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  constructor(private readonly reflector: Reflector) {
    super();
  }

  canActivate(context: ExecutionContext): boolean | Promise<boolean> | Observable<boolean> {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    return isPublic ? true : super.canActivate(context);
  }
}

// Uso
@Public()
@Post('login')
login(@Body() dto: LoginDto): Promise<TokenResponseDto> { ... }
```

## Roles y permisos

Para roles, crea un decorator personalizado `@Roles()` y un `RolesGuard` separado:

```typescript
export const ROLES_KEY = 'roles';
export const Roles = (...roles: Role[]): CustomDecorator => SetMetadata(ROLES_KEY, roles);

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<Role[] | undefined>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (!requiredRoles?.length) return true;

    const { user } = context.switchToHttp().getRequest<{ user?: AuthenticatedUser }>();
    if (!user) return false; // sin usuario autenticado no hay autorización

    return requiredRoles.some((role) => user.roles.includes(role));
  }
}
```

- Usa una constante (`ROLES_KEY`) para la clave de metadatos, no un string repetido.
- Aplica el principio de mínimo privilegio en guards de roles.
- Si el modelo es de permisos finos (`orders:read`, `orders:write`) en lugar de roles, aplica el mismo patrón con `@Permissions()` y `PermissionsGuard`, o una librería de autorización (p. ej. CASL) si las guidelines la definen.

## Usuario autenticado

```typescript
export const CurrentUser = createParamDecorator(
  (_data: unknown, ctx: ExecutionContext): AuthenticatedUser => {
    const request = ctx.switchToHttp().getRequest<{ user: AuthenticatedUser }>();
    return request.user;
  },
);

// Uso
@Get('me')
me(@CurrentUser() user: AuthenticatedUser): Promise<UserResponseDto> {
  return this.usersService.findOne(user.id);
}
```

- `AuthenticatedUser` contiene solo lo necesario para autorizar (id, roles/permisos), no la entidad completa.
- Nunca tomes el identificador del usuario de un parámetro de la petición (`body.userId`, `query.userId`) para decidir permisos: tómalo siempre del usuario autenticado.

## Autorización por recurso

Los roles deciden qué tipo de operación puede hacer un usuario; **no** deciden sobre qué recursos. Comprueba la propiedad o el permiso sobre cada recurso concreto (OWASP API1: Broken Object Level Authorization):

```typescript
async findOrder(user: AuthenticatedUser, orderId: string): Promise<OrderResponseDto> {
  const order = await this.orderRepository.findOne({
    where: { id: orderId, userId: user.id }, // filtra por propietario
  });
  if (!order) {
    throw new NotFoundException(); // 404 para no revelar si existe
  }
  return this.toDto(order);
}
```

- La comprobación va en el servicio (o en la consulta), aplicada a **todas** las operaciones sobre el recurso: lectura, edición, borrado, listados y exportaciones.
- No expongas IDs secuenciales de base de datos; usa UUIDs en rutas públicas. Reduce la enumeración, pero **no sustituye** la comprobación anterior.
- Comprueba también la autorización a nivel de **propiedad**: un usuario puede editar su perfil, pero no su campo `role` (ver asignación masiva en `nestjs-security`).

## Contraseñas

- Usa `argon2` (preferido) o `bcrypt` para almacenar contraseñas. **Nunca almacenes contraseñas en texto plano** ni las registres en logs.
- `bcrypt` trunca las contraseñas a 72 bytes: limita la longitud en el DTO o usa `argon2`.
- Encapsula el algoritmo en un provider (`PasswordHasher`) para poder cambiarlo o ajustar sus parámetros sin tocar los servicios.
- En login, responde el mismo error y en un tiempo similar ante usuario inexistente o contraseña incorrecta, para no revelar qué cuentas existen.
- Limita los intentos de login (ver rate limiting en `nestjs-security`).

## Tokens (JWT)

- Los JWT deben tener expiración corta (`expiresIn`); usa refresh tokens para sesiones largas.
- Refresh tokens con **rotación** (cada uso emite uno nuevo e invalida el anterior) y **revocación** (logout, cambio de contraseña). Guárdalos hasheados en base de datos, nunca en claro.
- El secreto o la clave de firma se lee de `ConfigService` y nunca se versiona (ver `nestjs-config`).
- Al verificar, fija el algoritmo esperado y valida emisor (`iss`) y audiencia (`aud`) cuando se usen.
- No incluyas datos sensibles en el payload del JWT: está codificado, no cifrado, y es legible por cualquiera.

```typescript
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(config: ConfigService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: config.getOrThrow<string>('JWT_SECRET'),
      algorithms: ['HS256'],
    });
  }

  validate(payload: JwtPayload): AuthenticatedUser {
    return { id: payload.sub, roles: payload.roles };
  }
}
```

- Si el token viaja en una cookie en lugar de la cabecera `Authorization`, la protección CSRF y la configuración de la cookie están en `nestjs-security`.
- Si la autenticación la gestiona un proveedor externo (OIDC, Keycloak, Azure AD...), valida los tokens contra sus claves públicas (JWKS) en lugar de emitirlos tú.

## GraphQL y microservicios

Los ejemplos anteriores leen la petición con `context.switchToHttp()`, que solo funciona en HTTP:

- **GraphQL**: los guards y `@CurrentUser()` deben obtener la petición con `GqlExecutionContext`. Usa el helper `getRequest(context)` de `nestjs-graphql`. Protege también los `@ResolveField` que exponen datos sensibles.
- **Microservicios**: un guard de autenticación HTTP registrado con `APP_GUARD` también se ejecuta en los handlers de mensajes, donde no hay cabecera `Authorization`, y los rechazaría. Haz que distinga el contexto `rpc` (ver `nestjs-microservices`). Si un mensaje actúa en nombre de un usuario, vuelve a comprobar la autorización en el consumidor.

## Tests

- Prueba los guards con cada rama: sin metadatos, sin usuario, con y sin el rol requerido, y cada contexto que soporten (ver `nestjs-testing`).
- E2E: un endpoint protegido responde 401 sin token y 403 con un usuario sin permisos; un recurso ajeno responde 404.

## Checklist

- [ ] Endpoints protegidos por defecto; los públicos marcados con `@Public()`
- [ ] Guards globales con `APP_GUARD`, compatibles con todos los contextos del proyecto
- [ ] Autorización por recurso (y por propiedad) además de por rol
- [ ] Identidad tomada del usuario autenticado, nunca de la petición
- [ ] Contraseñas con argon2/bcrypt, nunca en logs
- [ ] JWT con expiración corta, algoritmo fijado y secreto fuera del repositorio
- [ ] Refresh tokens con rotación y revocación, guardados hasheados
- [ ] Sin datos sensibles en el payload del JWT
