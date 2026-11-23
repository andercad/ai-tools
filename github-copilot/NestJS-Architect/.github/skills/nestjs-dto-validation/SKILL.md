---
name: nestjs-dto-validation
description: 'Backend NestJS (API). DTOs NestJS: validación con class-validator, transformación con class-transformer, ValidationPipe global, PartialType/PickType/OmitType, DTOs de respuesta y serialización. Usar cuando: crear DTOs de entrada o salida, añadir reglas de validación, validar objetos anidados o arrays, transformar tipos de query params, ocultar campos en la respuesta.'
argument-hint: 'Describe el DTO o las reglas de validación que necesitas.'
---

# DTOs y validación

## Reglas

- Define DTOs en la carpeta `dto/` del módulo correspondiente.
- Los DTOs son **clases**, no interfaces: las interfaces desaparecen al compilar y no pueden validarse.
- Usa `class-validator` y `class-transformer` para validar y transformar (salvo que las guidelines definan otra estrategia, p. ej. Zod).
- **Nunca aceptes `any` en DTOs**; define todos los campos con tipos explícitos.
- DTOs separados por intención: `CreateXDto`, `UpdateXDto`, `XResponseDto`, `ListXQueryDto`.
- La validación del DTO es la frontera de seguridad de entrada: todo dato que llega por HTTP, GraphQL o mensajería pasa por ella. La asignación masiva, prototype pollution y ReDoS se tratan en `nestjs-security`.
- En un monorepo con el frontend, los DTO **no** se comparten con él: son clases del backend con decoradores. Lo que se comparte es una interfaz de contrato que el DTO implementa (ver `nestjs-monorepo`).

## DTO de entrada

```typescript
import { ApiProperty } from '@nestjs/swagger';
import { IsEmail, IsString, MaxLength, MinLength } from 'class-validator';
import { Transform } from 'class-transformer';

export class CreateUserDto {
  @ApiProperty({ example: 'ana@example.com' })
  @IsEmail()
  @Transform(({ value }: { value: unknown }) =>
    typeof value === 'string' ? value.trim().toLowerCase() : value,
  )
  email!: string;

  @ApiProperty({ minLength: 8, maxLength: 128 })
  @IsString()
  @MinLength(8)
  @MaxLength(128)
  password!: string;
}
```

- Usa el operador `!` (definite assignment) en las propiedades: con `strictPropertyInitialization` activo, una propiedad sin inicializar no compila. Los valores los asigna `class-transformer`.
- Pon límites (`@MaxLength`, `@Max`, `@ArrayMaxSize`) a todo campo de tamaño variable para evitar cargas excesivas.

## ValidationPipe global

Activa `ValidationPipe` globalmente con `transform: true` y `whitelist: true`:

```typescript
app.useGlobalPipes(
  new ValidationPipe({
    transform: true,
    whitelist: true,
    forbidNonWhitelisted: true,
  }),
);
```

- `whitelist` elimina las propiedades sin decorador; `forbidNonWhitelisted` responde 400 si llegan propiedades no declaradas.
- `useGlobalPipes` en `main.ts` no se aplica en los tests e2e que crean la app sin pasar por `bootstrap()`. Para que el pipe forme parte del módulo (y de los tests), regístralo con `APP_PIPE`:

```typescript
@Module({
  providers: [
    {
      provide: APP_PIPE,
      useValue: new ValidationPipe({ transform: true, whitelist: true, forbidNonWhitelisted: true }),
    },
  ],
})
export class AppModule {}
```

Usa uno de los dos mecanismos según las guidelines, no ambos.

El mismo `ValidationPipe` valida los `@InputType`/`@ArgsType` de GraphQL y los `@Payload()` de microservicios. Lanza `BadRequestException`; en esos contextos la traduce el filtro global multicontexto (ver `nestjs-error-handling`).

## DTOs derivados

Para actualizaciones parciales usa `PartialType(CreateUserDto)`. Si el proyecto usa `@nestjs/swagger`, importa los helpers **desde `@nestjs/swagger`** (no desde `@nestjs/mapped-types`), para que la documentación herede los decoradores `@ApiProperty`:

```typescript
import { OmitType, PartialType, PickType } from '@nestjs/swagger';

export class UpdateUserDto extends PartialType(OmitType(CreateUserDto, ['password'] as const)) {}

export class LoginDto extends PickType(CreateUserDto, ['email', 'password'] as const) {}
```

Usa `@nestjs/mapped-types` solo en proyectos sin Swagger. Para inputs de GraphQL, importa los helpers desde `@nestjs/graphql` (ver `nestjs-graphql`).

## Objetos anidados y arrays

`class-validator` no valida objetos anidados si no se indica explícitamente:

```typescript
export class CreateOrderDto {
  @ApiProperty({ type: [OrderLineDto] })
  @IsArray()
  @ArrayMinSize(1)
  @ArrayMaxSize(100)
  @ValidateNested({ each: true })
  @Type(() => OrderLineDto)
  lines!: OrderLineDto[];

  @ApiProperty({ type: AddressDto })
  @ValidateNested()
  @Type(() => AddressDto)
  shippingAddress!: AddressDto;
}
```

Sin `@ValidateNested()` + `@Type()`, el contenido anidado llega sin validar.

## Query params y tipos

Con Express 5 (Nest 11+), el parser de query por defecto es el simple: los objetos anidados (`?filter[name]=x`) ya no se convierten en objetos. Diseña los query DTOs con campos planos o, si el contrato lo necesita, activa `app.set('query parser', 'extended')` de forma consciente.

Los query params llegan siempre como `string`. Con `transform: true`, usa `@Type(() => Number)` explícito. Para booleanos, `@Type(() => Boolean)` convierte `'false'` en `true`; usa una transformación propia:

```typescript
@IsOptional()
@Transform(({ value }: { value: unknown }) => value === 'true' || value === true)
@IsBoolean()
active?: boolean;
```

## DTOs de respuesta y serialización

- No devuelvas entidades: mapea a un DTO de respuesta en el servicio (ver `nestjs-services`). Así ningún campo nuevo de la entidad (hash de contraseña, campos internos) se filtra por accidente.
- Alternativa: `ClassSerializerInterceptor` con `@Exclude()`/`@Expose()`. Si se usa, aplica `@Exclude()` por defecto a nivel de clase y `@Expose()` solo a los campos públicos, para que un campo nuevo no se publique sin querer.

```typescript
export class UserResponseDto {
  @ApiProperty()
  readonly id!: string;

  @ApiProperty()
  readonly email!: string;

  @ApiProperty()
  readonly createdAt!: Date;
}
```

## Checklist

- [ ] DTOs como clases, sin `any`, con `!` en propiedades
- [ ] Todos los campos con decoradores de validación y `@ApiProperty`
- [ ] Límites de longitud/tamaño en campos variables
- [ ] Objetos anidados con `@ValidateNested()` + `@Type()`
- [ ] `PartialType`/`PickType`/`OmitType` desde `@nestjs/swagger` si se usa Swagger
- [ ] `ValidationPipe` con `whitelist` y `forbidNonWhitelisted`
- [ ] Respuestas con DTOs, nunca entidades
