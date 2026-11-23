# Entidades y persistencia

Detecta el ORM en `package.json` y en el `CLAUDE.md` del proyecto. Este documento cubre TypeORM y Prisma.

## Entidades (TypeORM)

- Define entidades en la carpeta `entities/` del módulo.
- Si usas TypeORM, decora con `@Entity()`, `@Column()`, `@PrimaryGeneratedColumn()`, etc.
- Las relaciones (`@OneToMany`, `@ManyToOne`, etc.) se declaran en la entidad, no en el servicio.
- Incluye `@CreateDateColumn()` y `@UpdateDateColumn()` en las entidades que persistan, salvo que el `CLAUDE.md` del proyecto indique otra cosa.
- Usa `!` en las propiedades (las asigna el ORM) y tipos explícitos en `@Column`.

```typescript
@Entity('users')
export class UserEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Index({ unique: true })
  @Column({ type: 'varchar', length: 254 })
  email!: string;

  @Column({ type: 'varchar', length: 255, select: false }) // no se carga por defecto
  passwordHash!: string;

  @OneToMany(() => OrderEntity, (order) => order.user)
  orders!: OrderEntity[];

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt!: Date;

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt!: Date;
}
```

- Marca con `select: false` los campos sensibles (hashes, tokens) para que no se carguen sin pedirlos explícitamente.
- Evita `eager: true` en relaciones: carga datos en todas las consultas. Pide las relaciones cuando se necesiten.

## Prisma

- Si usas Prisma, el esquema reside en `prisma/schema.prisma`; no crees clases de entidad manualmente.
- Expón el cliente con un `PrismaService` en un módulo de infraestructura:

```typescript
@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  async onModuleInit(): Promise<void> {
    await this.$connect();
  }
}

@Module({
  providers: [PrismaService],
  exports: [PrismaService],
})
export class PrismaModule {}
```

- Los tipos generados por Prisma son el modelo de persistencia: no los devuelvas en la API, mapea a DTOs igual que con TypeORM.

## Monorepos

- **Cada aplicación es dueña de su base de datos o esquema**: su `DataSource` (o su esquema de Prisma), sus entidades y **sus migraciones**, en carpetas de esa aplicación o de sus librerías `data-access`.
- Una librería compartida no da acceso a las tablas de otro servicio. Si dos aplicaciones necesitan los mismos datos, una los expone por API o eventos (ver `nestjs-microservices`).
- Las entidades pueden vivir en una librería si solo las usa una aplicación (para organizar el código), pero con `autoLoadEntities` asegúrate de que cada aplicación solo registra las suyas.
- Los comandos de migraciones se ejecutan **por aplicación**, con el `DataSource` de esa aplicación (ver `nestjs-workspace`).

## Migraciones

- **Nunca** `synchronize: true` en producción (TypeORM) ni `prisma db push` contra producción: los cambios de esquema van en migraciones versionadas.
- Genera la migración a partir del cambio de entidad/esquema, **revísala** antes de commitearla y pruébala en una base de datos de desarrollo.
- Cambios destructivos (borrar o renombrar columnas, cambiar tipos) en varios pasos compatibles con la versión desplegada (expand/contract), con copia de seguridad y plan de vuelta atrás.

```powershell
# TypeORM (según el script del proyecto; en un monorepo, con el data-source de la aplicación)
npm run typeorm -- migration:generate src/migrations/AddUserPhone -d src/data-source.ts
npm run typeorm -- migration:run -d src/data-source.ts

# Prisma
npx prisma migrate dev --name add-user-phone
npx prisma migrate deploy   # en despliegue
```

## Transacciones

Si un caso de uso escribe en varias tablas, envuélvelo en una transacción:

```typescript
@Injectable()
export class OrdersService {
  constructor(private readonly dataSource: DataSource) {}

  async createOrder(userId: string, dto: CreateOrderDto): Promise<OrderResponseDto> {
    const order = await this.dataSource.transaction(async (manager) => {
      const created = await manager.save(OrderEntity, { userId, status: 'pending' });
      await manager.save(
        OrderLineEntity,
        dto.lines.map((line) => ({ ...line, orderId: created.id })),
      );
      return created;
    });
    return this.toDto(order);
  }
}
```

- Dentro de la transacción usa **siempre** el `manager` recibido; un repositorio inyectado fuera de ella no participa en la transacción.
- Con Prisma: `this.prisma.$transaction(async (tx) => { ... })`.
- No hagas llamadas HTTP externas ni publiques mensajes al broker dentro de una transacción: la mantienen abierta y no se deshacen si la transacción falla. Para publicar eventos de forma consistente, usa el patrón outbox (ver `nestjs-microservices`).

## Rendimiento de consultas

- **N+1**: no recorras una lista lanzando una consulta por elemento. Carga relaciones con `relations`/joins o en una consulta con `In(ids)`. En GraphQL, usa DataLoader (ver `nestjs-graphql`).
- **Índices** en columnas usadas en `WHERE`, `ORDER BY` y claves foráneas consultadas habitualmente.
- **Paginación** obligatoria en listados (`take`/`skip` o paginación por cursor en tablas grandes); nunca devuelvas tablas completas.
- Selecciona solo las columnas necesarias en consultas pesadas.
- Las consultas con SQL nativo usan **parámetros**, nunca concatenación de strings (inyección SQL):

```typescript
// ✅ Parametrizado
await this.dataSource.query('SELECT * FROM users WHERE email = $1', [email]);
// ❌ Inyección SQL
await this.dataSource.query(`SELECT * FROM users WHERE email = '${email}'`);
```

## Concurrencia

- La unicidad la garantiza un índice único en base de datos, no una comprobación previa en código. Traduce la violación de unicidad a `409 Conflict` (ver `nestjs-api`).
- Para evitar actualizaciones perdidas en recursos editados concurrentemente, usa bloqueo optimista (`@VersionColumn()` en TypeORM) y responde `409` si la versión no coincide.

## Checklist

- [ ] Entidades con tipos explícitos, `!` y fechas de auditoría
- [ ] Campos sensibles con `select: false`
- [ ] Sin relaciones `eager` innecesarias
- [ ] Cambios de esquema en migraciones revisadas; `synchronize: false`
- [ ] Escrituras múltiples dentro de una transacción usando su `manager`
- [ ] Sin N+1, con índices y paginación
- [ ] SQL nativo parametrizado
- [ ] Unicidad garantizada por índice
- [ ] En un monorepo, base de datos y migraciones por aplicación
