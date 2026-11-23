# Controladores y documentación de la API

Este documento cubre la API REST. Para GraphQL ver `nestjs-graphql`; para handlers de mensajes, `nestjs-microservices`.

## Reglas de controladores

- Cada controlador gestiona las rutas de un único recurso.
- Usa siempre `@Controller('recurso')` con prefijo de ruta en kebab-case y en plural (`'users'`, `'order-items'`).
- Decora cada método con el verbo HTTP correcto (`@Get`, `@Post`, `@Put`, `@Patch`, `@Delete`).
- Los métodos del controlador **no contienen lógica de negocio**: delegan en servicios.
- Usa `@Param()`, `@Query()`, `@Body()` con tipos DTO explícitos y pipes de parseo para los parámetros.
- Devuelve siempre DTOs de respuesta, nunca entidades.

```typescript
@ApiTags('users')
@ApiBearerAuth()
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  // --- Lectura ---
  @Get()
  @ApiOperation({ summary: 'Lista paginada de usuarios' })
  @ApiOkResponse({ type: PaginatedUsersDto })
  findAll(@Query() query: ListUsersQueryDto): Promise<PaginatedUsersDto> {
    return this.usersService.findAll(query);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Obtiene un usuario por id' })
  @ApiOkResponse({ type: UserResponseDto })
  @ApiNotFoundResponse({ description: 'Usuario no encontrado' })
  findOne(@Param('id', ParseUUIDPipe) id: string): Promise<UserResponseDto> {
    return this.usersService.findOne(id);
  }

  // --- Escritura ---
  @Post()
  @ApiOperation({ summary: 'Crea un usuario' })
  @ApiCreatedResponse({ type: UserResponseDto })
  @ApiBadRequestResponse({ description: 'Datos de entrada no válidos' })
  create(@Body() createUserDto: CreateUserDto): Promise<UserResponseDto> {
    return this.usersService.create(createUserDto);
  }

  @Patch(':id')
  @ApiOperation({ summary: 'Actualiza parcialmente un usuario' })
  @ApiOkResponse({ type: UserResponseDto })
  update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() updateUserDto: UpdateUserDto,
  ): Promise<UserResponseDto> {
    return this.usersService.update(id, updateUserDto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: 'Elimina un usuario' })
  @ApiNoContentResponse()
  remove(@Param('id', ParseUUIDPipe) id: string): Promise<void> {
    return this.usersService.remove(id);
  }
}
```

## Códigos de estado

| Operación                        | Código por defecto en Nest | Qué hacer                                  |
| -------------------------------- | -------------------------- | ------------------------------------------ |
| `GET` correcto                   | 200                        | Nada                                       |
| `POST` que crea                  | 201                        | Nada (`@HttpCode(201)` es redundante)      |
| `POST` que no crea (acción)      | 201                        | `@HttpCode(HttpStatus.OK)`                 |
| `DELETE` / `PUT` sin cuerpo      | 200                        | `@HttpCode(HttpStatus.NO_CONTENT)` (204)   |
| Recurso no encontrado            | —                          | Lanzar `NotFoundException` desde el servicio |
| Conflicto (duplicado)            | —                          | Lanzar `ConflictException`                 |

Usa la enumeración `HttpStatus` en lugar de números literales.

## Parámetros y paginación

- Parámetros de ruta con pipe de parseo: `ParseUUIDPipe` para identificadores públicos (ver `nestjs-security`), `ParseIntPipe` solo para valores numéricos que no son identificadores.
- Query params agrupados en un DTO validado, con límites máximos para evitar consultas costosas:

```typescript
export class ListUsersQueryDto {
  @ApiPropertyOptional({ default: 1, minimum: 1 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  page = 1;

  @ApiPropertyOptional({ default: 20, minimum: 1, maximum: 100 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100)
  limit = 20;
}
```

- No accedas a `@Req()`/`@Res()` salvo que sea imprescindible. Si usas `@Res()`, Nest deja de gestionar la respuesta (interceptores y serialización incluidos); usa `@Res({ passthrough: true })` si solo necesitas fijar cabeceras o cookies.
- Para obtener el usuario autenticado, usa un decorador `@CurrentUser()` en lugar de leer `req.user` (ver `nestjs-security`).

## Documentación de la API (Swagger / OpenAPI)

- Usa `@nestjs/swagger` para generar la documentación OpenAPI.
- Decora todos los controladores con `@ApiTags()`.
- Decora todos los endpoints con `@ApiOperation()` y las respuestas correspondientes (`@ApiOkResponse`, `@ApiCreatedResponse`, `@ApiNotFoundResponse`... o `@ApiResponse({ status, type })`).
- Decora los DTOs con `@ApiProperty()` / `@ApiPropertyOptional()` en todos sus campos (ver `nestjs-api`). Alternativa: el plugin CLI de Swagger en `nest-cli.json` genera gran parte de esos decoradores; usa uno u otro según el `CLAUDE.md` del proyecto.
- Los endpoints protegidos llevan `@ApiBearerAuth()` (o el esquema de seguridad que corresponda).

### Configuración en main.ts

Exponer la documentación es una decisión de cada proyecto (ver el `CLAUDE.md` del proyecto). Por defecto, solo fuera de producción. Se lee el entorno desde `ConfigService`, no desde `process.env`:

```typescript
// main.ts
async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule);
  const config = app.get(ConfigService);

  if (config.get<string>('NODE_ENV') !== 'production') {
    const swaggerConfig = new DocumentBuilder()
      .setTitle('API')
      .setVersion('1.0')
      .addBearerAuth()
      .build();
    const document = SwaggerModule.createDocument(app, swaggerConfig);
    SwaggerModule.setup('api', app, document);
  }

  await app.listen(config.get<number>('PORT', 3000));
}
void bootstrap();
```

Si el proyecto necesita la documentación en producción, protégela (autenticación o red interna) en lugar de exponerla públicamente.

## Checklist

- [ ] Un recurso por controlador, rutas en kebab-case
- [ ] Sin lógica de negocio en el controlador
- [ ] Parámetros con pipes de parseo y DTOs validados
- [ ] Respuestas tipadas con DTOs, nunca entidades
- [ ] Códigos de estado correctos (204 en borrados sin cuerpo)
- [ ] Sin `@Res()` salvo justificación
- [ ] Endpoints documentados (`@ApiTags`, `@ApiOperation`, respuestas)
- [ ] Endpoints protegidos con su guard y `@ApiBearerAuth()`
