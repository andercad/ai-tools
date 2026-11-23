# Módulos

## Reglas

- Cada dominio funcional tiene su propio módulo (`@Module`).
- `AppModule` solo registra módulos de dominio y configuración global; no contiene lógica de negocio.
- Usa `forRoot()` / `forRootAsync()` para módulos que requieren configuración dinámica (ej. `TypeOrmModule`, `ConfigModule`, `JwtModule`, `GraphQLModule`, `ClientsModule`).
- Usa `forFeature()` para registrar entidades y repositorios por módulo (TypeORM). Con Prisma no existe `forFeature`: se inyecta un `PrismaService` exportado por un módulo de infraestructura (ver `nestjs-persistence`).
- Orden de las propiedades del decorador: `imports`, `controllers`, `providers`, `exports`.
- Exporta solo lo que otros módulos necesiten usar:

```typescript
@Module({
  imports: [TypeOrmModule.forFeature([UserEntity])],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
```

- Un módulo que consume un provider de otro módulo debe **importar ese módulo**, no volver a declarar el provider en sus `providers` (eso crea una segunda instancia).
- Los resolvers GraphQL se registran en `providers`; los controladores de mensajes, en `controllers`.
- En un monorepo, una librería compartida expone **su módulo** desde su `index.ts` y la aplicación lo importa por el alias de la librería; la configuración que dependa de cada aplicación entra por `forRoot`/`forRootAsync` o `ConfigurableModuleBuilder` (ver `nestjs-workspace`).

## AppModule

```typescript
@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, validate }), // ver nestjs-config
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        type: 'postgres',
        url: config.getOrThrow<string>('DATABASE_URL'),
        autoLoadEntities: true,
        synchronize: false, // nunca true en producción; usar migraciones
      }),
    }),
    UsersModule,
    OrdersModule,
  ],
})
export class AppModule {}
```

**Regla**: usa `forRootAsync()` con `useFactory` + `inject: [ConfigService]` cuando la configuración dependa de variables de entorno. No leas `process.env` dentro de `forRoot()`.

## Módulos globales

- `@Global()` solo para infraestructura transversal realmente usada en todas partes (configuración, logger, cliente de base de datos).
- No marques módulos de dominio como globales: oculta las dependencias reales y dificulta los tests.

## Dependencias circulares

- Evita la importación circular de módulos; usa `forwardRef()` solo si es imprescindible y documéntalo:

```typescript
@Module({
  // Dependencia circular documentada: Orders necesita validar usuarios y
  // Users muestra el recuento de pedidos. Pendiente: extraer a un módulo común.
  imports: [forwardRef(() => UsersModule)],
  providers: [OrdersService],
  exports: [OrdersService],
})
export class OrdersModule {}
```

- Antes de usar `forwardRef()`, intenta romper el ciclo:
  - Extraer la funcionalidad compartida a un tercer módulo del que dependan ambos.
  - Comunicar mediante eventos (`@nestjs/event-emitter`, o mensajería entre servicios: ver `nestjs-microservices`) en lugar de llamadas directas.
  - Revisar si un barrel `index.ts` está provocando el ciclo de imports de ficheros.
- Un error `Nest can't resolve dependencies of X (?)` con `?` en una posición suele indicar un ciclo de imports de ficheros o un provider no exportado/importado.

## Módulos dinámicos propios

Para módulos reutilizables configurables, usa `ConfigurableModuleBuilder`:

```typescript
export interface NotificationsModuleOptions {
  readonly apiUrl: string;
  readonly timeoutMs: number;
}

export const { ConfigurableModuleClass, MODULE_OPTIONS_TOKEN } =
  new ConfigurableModuleBuilder<NotificationsModuleOptions>().build();

@Module({
  providers: [NotificationsService],
  exports: [NotificationsService],
})
export class NotificationsModule extends ConfigurableModuleClass {}

// Uso
NotificationsModule.registerAsync({
  inject: [ConfigService],
  useFactory: (config: ConfigService) => ({
    apiUrl: config.getOrThrow<string>('NOTIFICATIONS_URL'),
    timeoutMs: 5000,
  }),
});
```

Solo crea módulos dinámicos cuando el módulo se reutiliza con configuraciones distintas; para un único uso, un módulo normal es suficiente. En un monorepo, es el patrón natural para una librería que usan varias aplicaciones con configuración distinta.

## Checklist

- [ ] Un módulo por dominio funcional
- [ ] `AppModule` sin lógica de negocio
- [ ] Configuración dinámica con `forRootAsync` + `ConfigService`
- [ ] Solo se exporta lo que otros módulos consumen
- [ ] Ningún provider declarado en dos módulos
- [ ] Sin `@Global()` en módulos de dominio
- [ ] Sin `forwardRef()` sin documentar
