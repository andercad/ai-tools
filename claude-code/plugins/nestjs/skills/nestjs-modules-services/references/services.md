# Servicios

## Reglas

- `@Injectable()` para todos los providers.
- Cada servicio tiene **una única responsabilidad**. Documenta con JSDoc.
- Inyecta dependencias **exclusivamente por constructor**.
- Los métodos de servicio son `async` cuando realizan operaciones de I/O.
- No expongas entidades de base de datos directamente; mapea a DTOs o interfaces de respuesta.
- El servicio contiene la lógica de negocio; controladores, resolvers GraphQL y handlers de mensajes solo adaptan el transporte y reutilizan el mismo servicio.

```typescript
/**
 * Gestión de usuarios: alta, consulta y actualización.
 */
@Injectable()
export class UsersService {
  // --- Properties ---
  private readonly logger = new Logger(UsersService.name);

  // --- Dependencies ---
  constructor(
    @InjectRepository(UserEntity)
    private readonly userRepository: Repository<UserEntity>,
    private readonly passwordHasher: PasswordHasher,
  ) {}

  // --- Public methods (lectura) ---
  async findOne(id: string): Promise<UserResponseDto> {
    const user = await this.userRepository.findOne({ where: { id } });
    if (!user) {
      throw new NotFoundException(`User ${id} not found`);
    }
    return this.toDto(user);
  }

  // --- Public methods (escritura) ---
  async create(dto: CreateUserDto): Promise<UserResponseDto> {
    const exists = await this.userRepository.exists({ where: { email: dto.email } });
    if (exists) {
      throw new ConflictException('Email already registered');
    }

    const user = this.userRepository.create({
      email: dto.email,
      passwordHash: await this.passwordHasher.hash(dto.password),
    });
    const saved = await this.userRepository.save(user);
    this.logger.log(`User created: ${saved.id}`); // nunca el email ni la contraseña
    return this.toDto(saved);
  }

  // --- Private methods ---
  private toDto(entity: UserEntity): UserResponseDto {
    return {
      id: entity.id,
      email: entity.email,
      createdAt: entity.createdAt,
    };
  }
}
```

La comprobación de email duplicado reduce errores, pero no evita la condición de carrera entre dos peticiones simultáneas: la garantía la da un índice único en base de datos, y el error de violación de unicidad debe traducirse a `409` (ver `nestjs-persistence` y `nestjs-api`).

## Mapeo entidad → DTO

- Mapea explícitamente en un método privado `toDto()` o en un mapper dedicado si se reutiliza en varios servicios.
- El mapeo explícito garantiza que un campo nuevo de la entidad no aparece en la API sin una decisión consciente.

## Errores de negocio

Por defecto, en servicios de una API REST lanza `HttpException` o sus subclases (`NotFoundException`, `ConflictException`, `BadRequestException`, `ForbiddenException`...). Nunca lances `Error` genérico para un error de negocio. El filtro global multicontexto también las traduce en GraphQL y mensajería (ver `nestjs-api`).

Si la lógica de negocio se ejecuta fuera de HTTP (consumidores de colas, microservicios, CLI, tareas programadas) y no quieres acoplarla a HTTP, lanza **errores de dominio** y tradúcelos en un filtro:

```typescript
export class DomainError extends Error {
  constructor(
    readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = new.target.name;
  }
}

export class EmailAlreadyRegisteredError extends DomainError {
  constructor() {
    super('EMAIL_ALREADY_REGISTERED', 'Email already registered');
  }
}
```

Elige un único criterio por proyecto (según el `CLAUDE.md` del proyecto) y aplícalo de forma consistente.

## Scope de los providers

- Por defecto los providers son **singleton**: no guardes en propiedades del servicio estado de una petición concreta (usuario actual, datos del request).
- Pasa el contexto de la petición como parámetro o usa `nestjs-cls` / `AsyncLocalStorage`. Evita `Scope.REQUEST` salvo necesidad: se propaga a todos los providers que dependen de él y tiene coste de rendimiento.

## Coordinar varias operaciones

- Si un caso de uso escribe en varias tablas, la consistencia la da una transacción (ver `nestjs-persistence`).
- Para efectos secundarios desacoplados dentro del mismo servicio (enviar un email tras un alta), usa eventos (`@nestjs/event-emitter`) en lugar de llamar a otros servicios en cadena. Un evento emitido en memoria se pierde si el proceso cae; si el efecto es crítico o lo procesa otro servicio, usa mensajería con el patrón outbox (ver `nestjs-microservices`).

## Checklist

- [ ] Una responsabilidad por servicio, con JSDoc
- [ ] Inyección por constructor, sin `new` de providers
- [ ] Métodos `async` en operaciones de I/O
- [ ] Mapeo explícito a DTOs de respuesta
- [ ] Excepciones HTTP o errores de dominio, nunca `Error` genérico
- [ ] Sin estado de la petición en propiedades del servicio singleton
- [ ] Sin datos personales ni secretos en los logs
