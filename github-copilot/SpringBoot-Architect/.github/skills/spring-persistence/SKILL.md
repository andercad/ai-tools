---
name: spring-persistence
description: 'Persistencia en Spring Boot con JPA/Hibernate y Spring Data: entidades, relaciones y fetch, equals/hashCode, repositorios, consultas derivadas, JPQL y nativas, proyecciones, N+1 con EntityGraph y join fetch, paginación, migraciones Flyway/Liquibase, open-in-view, bloqueo optimista, auditoría e índices. Usar cuando: crear o modificar entidades, escribir consultas, crear migraciones, resolver consultas lentas o N+1, gestionar concurrencia.'
argument-hint: 'Describe la entidad, consulta, migración o problema de persistencia.'
---

# Persistencia

Comprueba en el proyecto la tecnología de persistencia (JPA/Hibernate, JDBC/`JdbcClient`, jOOQ, MongoDB...) y la herramienta de migraciones. Esta skill se centra en JPA con Spring Data.

## Configuración base

```yaml
spring:
  jpa:
    open-in-view: false          # por defecto es true: desactívalo
    hibernate:
      ddl-auto: validate         # nunca update/create fuera de desarrollo local
    properties:
      hibernate:
        jdbc.batch_size: 50
        order_inserts: true
        order_updates: true
  flyway:
    enabled: true
```

- **`open-in-view=false`**: con el valor por defecto, la sesión de Hibernate queda abierta durante toda la petición, ocultando consultas *lazy* en el controlador o en la serialización (N+1 invisibles y conexiones retenidas). Spring Boot avisa de ello en el log al arrancar.
- **`ddl-auto=validate`** (o `none`): el esquema lo gestionan las migraciones; Hibernate solo comprueba que coincide.

## Entidades

```java
@Entity
@Table(name = "users")
public class UserEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, unique = true, length = 254)
    private String email;

    @Column(name = "password_hash", nullable = false)
    private String passwordHash;

    @Column(name = "display_name", length = 100)
    private String displayName;

    @Column(length = 500)
    private String bio;

    @OneToMany(mappedBy = "user")
    private List<OrderEntity> orders = new ArrayList<>();

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    @Version
    private long version;

    protected UserEntity() { // exigido por JPA
    }

    public UserEntity(String email, String passwordHash) {
        this.email = email;
        this.passwordHash = passwordHash;
    }

    // Métodos de negocio en lugar de setters públicos
    public void changeDisplayName(String displayName) {
        this.displayName = displayName;
    }

    public void changeBio(String bio) {
        this.bio = bio;
    }

    public UUID getId() { return id; }
    public String getEmail() { return email; }
    public String getDisplayName() { return displayName; }
    public Instant getCreatedAt() { return createdAt; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof UserEntity other)) return false;
        return id != null && id.equals(other.id);
    }

    @Override
    public int hashCode() {
        return getClass().hashCode(); // estable antes y después de persistir
    }
}
```

- **Sin setters indiscriminados**: expón métodos de negocio (`changeEmail`, `cancel`) o solo los setters de campos editables.
- **`equals`/`hashCode`** basados en el identificador y con `hashCode` constante, para que la entidad se comporte bien en `Set` antes y después de persistir. Nunca `@Data`/`@EqualsAndHashCode` de Lombok ni `equals` sobre todas las columnas o relaciones.
- **`toString`** sin relaciones *lazy* (dispara consultas o `LazyInitializationException`) ni datos sensibles.
- **Auditoría** (`@CreatedDate`, `@LastModifiedDate`) con `@EnableJpaAuditing` y `@EntityListeners(AuditingEntityListener.class)`, o `@CreationTimestamp`/`@UpdateTimestamp` de Hibernate, según las guidelines.
- No uses records como entidades JPA.

## Relaciones y fetch

- `@ManyToOne` y `@OneToOne` son **EAGER por defecto**: declara siempre `fetch = FetchType.LAZY`.

```java
@ManyToOne(fetch = FetchType.LAZY, optional = false)
@JoinColumn(name = "user_id", nullable = false)
private UserEntity user;
```

- Evita `@ManyToMany` con colecciones grandes; modela la tabla intermedia como entidad si tiene atributos o volumen.
- `cascade` y `orphanRemoval` solo dentro de un mismo agregado (pedido y sus líneas), nunca hacia entidades independientes.
- En relaciones bidireccionales, mantén ambos lados sincronizados con métodos auxiliares (`addLine`, `removeLine`).

## Repositorios

```java
interface UserRepository extends JpaRepository<UserEntity, UUID> {

    boolean existsByEmail(String email);

    Optional<UserEntity> findByEmail(String email);

    @Query("select u from UserEntity u where u.status = :status and u.createdAt >= :since")
    Page<UserEntity> findActiveSince(@Param("status") UserStatus status,
                                     @Param("since") Instant since,
                                     Pageable pageable);
}
```

- Consultas derivadas para casos simples; `@Query` con JPQL cuando el nombre del método se vuelve ilegible.
- **Siempre parámetros con nombre o posicionales**, nunca concatenación de strings (inyección, ver `spring-security`). Lo mismo en consultas nativas, `EntityManager.createQuery` y `JdbcClient`.
- **Proyecciones** (interfaces o records) para lecturas que no necesitan la entidad completa:

```java
record UserSummary(UUID id, String email) { }

@Query("select new com.example.app.user.UserSummary(u.id, u.email) from UserEntity u where u.status = :status")
List<UserSummary> findSummaries(@Param("status") UserStatus status);
```

- Búsquedas con filtros opcionales: `Specification` (JPA Criteria) o Querydsl, en lugar de construir JPQL concatenando condiciones.

## N+1

Recorrer una lista y acceder a una relación *lazy* lanza una consulta por elemento.

```java
// ✅ Cargar la relación en la misma consulta
@EntityGraph(attributePaths = "lines")
Optional<OrderEntity> findWithLinesById(UUID id);

@Query("select o from OrderEntity o join fetch o.lines where o.user.id = :userId")
List<OrderEntity> findWithLinesByUserId(@Param("userId") UUID userId);
```

- **`join fetch` de colecciones con paginación**: Hibernate pagina en memoria (aviso `HHH90003004`) y carga todos los resultados. Pagina primero los identificadores y carga las relaciones en una segunda consulta, o usa `@BatchSize`/`hibernate.default_batch_fetch_size`.
- Activa durante el desarrollo el log de SQL o las estadísticas de Hibernate para detectar N+1; nunca en producción con valores reales de parámetros.

## Paginación

- Listados siempre con `Pageable` y tamaño máximo (ver `spring-controllers`).
- En tablas grandes, `Page` ejecuta un `count` adicional costoso: usa `Slice` o paginación por clave/cursor (`Window`/`ScrollPosition` de Spring Data) cuando no se necesite el total.

## Migraciones

- Flyway (`db/migration/V1__create_users.sql`) o Liquibase, según las guidelines.
- Una migración aplicada **nunca se modifica**: los cambios van en una migración nueva.
- Revisa el SQL generado; pruébalo contra el mismo motor que producción (Testcontainers, ver `spring-testing`).
- Cambios destructivos (borrar o renombrar columnas, cambiar tipos) en varios pasos compatibles con la versión desplegada (*expand/contract*), con copia de seguridad y plan de vuelta atrás.
- Índices para las columnas usadas en filtros, ordenaciones y claves foráneas consultadas habitualmente; restricciones `UNIQUE` y `NOT NULL` en la base de datos, no solo en las anotaciones.

## Concurrencia

- **Bloqueo optimista** con `@Version` en entidades que se editan concurrentemente; la colisión lanza `ObjectOptimisticLockingFailureException`, que se traduce a 409 (ver `spring-error-handling`).
- Bloqueo pesimista (`@Lock(PESSIMISTIC_WRITE)`) solo para secciones críticas cortas, con timeout.
- La unicidad la garantiza la base de datos; traduce `DataIntegrityViolationException` a 409 sin exponer el mensaje del motor.

## Transacciones

Las transacciones se definen en la capa de servicio (ver `spring-services`). Dentro de una transacción, las entidades gestionadas se guardan al hacer commit sin llamar a `save()` (*dirty checking*); llamar a `save()` igualmente es aceptable por legibilidad si las guidelines lo prefieren.

## Checklist

- [ ] `open-in-view=false`, `ddl-auto=validate|none`
- [ ] Entidades con constructor protegido, sin `@Data`, `equals`/`hashCode` por id
- [ ] `@ManyToOne`/`@OneToOne` con `FetchType.LAZY`
- [ ] Consultas parametrizadas; filtros opcionales con `Specification`
- [ ] Sin N+1; sin `join fetch` de colecciones con paginación
- [ ] Proyecciones para lecturas parciales
- [ ] Migraciones nuevas para cada cambio; nunca editar las aplicadas
- [ ] Índices y restricciones en base de datos
- [ ] `@Version` en entidades con edición concurrente
