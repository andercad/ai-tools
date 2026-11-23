# Configuración

## Reglas

- Usa `@nestjs/config` con `ConfigModule.forRoot({ isGlobal: true, validate })` en `AppModule`.
- Define un esquema de validación con `class-validator` o `joi` para las variables de entorno. La aplicación **no arranca** si falta una variable obligatoria o tiene un formato inválido.
- Inyecta `ConfigService` en servicios para acceder a variables de entorno. **Nunca uses `process.env` directamente** fuera del esquema de configuración.
- Las variables de entorno se definen en `.env.template` (en el repo, sin valores reales) y `.env` (ignorado por git).
- **Nunca** persistas `.env` en el repositorio. En entornos desplegados, los secretos llegan por el gestor de secretos o variables del entorno de ejecución, no por ficheros versionados.

## Monorepos

- **Configuración por aplicación**: cada aplicación valida su propio esquema (solo las variables que usa) y tiene su `.env.template` en su carpeta. Una aplicación no debe fallar al arrancar por una variable que solo necesita otra.
- **Ruta del `.env` en desarrollo**: en un monorepo, `ConfigModule` busca el `.env` en el directorio de trabajo del proceso, que suele ser la raíz. Indica el de la aplicación con `envFilePath` (ruta relativa a ese directorio de trabajo) y comprueba que funciona con el comando con el que arrancas (`nest start <app>`, `nx serve <app>`). En entornos desplegados no se usan ficheros `.env`: las variables llegan del entorno.
- **Lo común en una librería**: piezas de validación reutilizables (por ejemplo, la de la conexión a la base de datos) en una librería `util` que cada aplicación compone en su esquema. Una librería **nunca** lee `process.env`: recibe su configuración por `forRoot`/`forRootAsync` o un token (ver `nestjs-modules-services`).

```typescript
// apps/billing/src/app.module.ts
ConfigModule.forRoot({
  isGlobal: true,
  envFilePath: ['apps/billing/.env'], // relativo al directorio de trabajo (la raíz del monorepo)
  validate: validateBillingEnv,
});
```

## Validación del esquema

```typescript
// config/env.validation.ts
import { plainToInstance, Type } from 'class-transformer';
import { IsEnum, IsInt, IsString, IsUrl, Max, Min, MinLength, validateSync } from 'class-validator';

enum NodeEnv {
  Development = 'development',
  Test = 'test',
  Production = 'production',
}

class EnvironmentVariables {
  @IsEnum(NodeEnv)
  NODE_ENV!: NodeEnv;

  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(65535)
  PORT!: number;

  @IsUrl({ require_tld: false, protocols: ['postgres', 'postgresql'] })
  DATABASE_URL!: string;

  @IsString()
  @MinLength(32)
  JWT_SECRET!: string;
}

export function validate(config: Record<string, unknown>): EnvironmentVariables {
  const validated = plainToInstance(EnvironmentVariables, config, {
    enableImplicitConversion: true,
  });
  const errors = validateSync(validated, { skipMissingProperties: false });
  if (errors.length > 0) {
    // Lista qué variables fallan, nunca sus valores (pueden ser secretos)
    const names = errors.map((e) => e.property).join(', ');
    throw new Error(`Invalid environment configuration: ${names}`);
  }
  return validated;
}
```

```typescript
// app.module.ts
ConfigModule.forRoot({ isGlobal: true, validate, cache: true });
```

Añade al esquema las variables de GraphQL o del broker de mensajería (`RABBITMQ_URL`, `KAFKA_BROKERS`...) cuando el proyecto las use.

## Lectura de la configuración

```typescript
@Injectable()
export class DatabaseService {
  constructor(private readonly config: ConfigService) {}

  getConnectionUrl(): string {
    return this.config.getOrThrow<string>('DATABASE_URL');
  }
}
```

- `getOrThrow()` para valores obligatorios; `get(key, defaultValue)` solo para opcionales con un valor por defecto razonable.
- En módulos que se configuran al arrancar, usa `forRootAsync`/`registerAsync` + `inject: [ConfigService]` (ver `nestjs-modules-services`).
- En `main.ts`, obtén `ConfigService` con `app.get(ConfigService)`.

## Configuración tipada por área

Para agrupar variables relacionadas y obtener tipado, usa `registerAs`:

```typescript
// config/database.config.ts
export const databaseConfig = registerAs('database', () => ({
  url: process.env.DATABASE_URL as string, // único lugar donde se lee process.env
  poolSize: Number(process.env.DATABASE_POOL_SIZE ?? 10),
}));

// app.module.ts
ConfigModule.forRoot({ isGlobal: true, validate, load: [databaseConfig] });

// Uso tipado
@Injectable()
export class ReportsService {
  constructor(
    @Inject(databaseConfig.KEY)
    private readonly dbConfig: ConfigType<typeof databaseConfig>,
  ) {}
}
```

Los ficheros `registerAs` forman parte del esquema de configuración: son el único lugar, junto a la validación, donde se permite leer `process.env`.

## Añadir una nueva variable

1. Añadirla a `.env.template` (de la aplicación que la usa, en un monorepo) con un valor de ejemplo no real y un comentario.
2. Añadirla al `.env` local.
3. Añadirla a la clase de validación con sus decoradores.
4. Si pertenece a un área, añadirla a su `registerAs`.
5. Leerla con `ConfigService` o con la configuración tipada.
6. Documentar el cambio para que se configure en cada entorno desplegado.

## Checklist

- [ ] Esquema validado al arrancar
- [ ] Sin `process.env` fuera del esquema / `registerAs`
- [ ] `getOrThrow` en variables obligatorias
- [ ] `.env.template` actualizado; `.env` sin versionar
- [ ] Ningún secreto en el código, en logs ni en mensajes de error de validación
- [ ] En un monorepo, esquema y `.env.template` por aplicación; librerías sin `process.env`
