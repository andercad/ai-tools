---
name: spring-solid
description: 'Principios SOLID aplicados a Spring: responsabilidad única, extensión con estrategias (inyección de List/Map de beans), sustitución de implementaciones, interfaces segregadas e inversión de dependencias con inyección por constructor, @Qualifier y @Primary. Usar cuando: diseñar o refactorizar servicios, desacoplar una implementación (persistencia, proveedor externo, mensajería), decidir si crear una interfaz.'
argument-hint: 'Describe el diseño o la refactorización que necesitas.'
---

# Principios SOLID

SOLID es una herramienta para reducir acoplamiento y facilitar el cambio, no un fin en sí mismo. Aplica cada principio cuando resuelva un problema real; evita capas, interfaces y abstracciones que no aportan nada. Un CRUD sencillo no necesita arquitectura hexagonal.

## Inyección de dependencias

Base de todo lo demás:

```java
@Service
public class InvoiceService {

    private final InvoiceRepository invoiceRepository;
    private final Clock clock;

    public InvoiceService(InvoiceRepository invoiceRepository, Clock clock) {
        this.invoiceRepository = invoiceRepository;
        this.clock = clock;
    }
}
```

- **Solo inyección por constructor** con campos `final`. Con un único constructor, `@Autowired` es innecesario.
- **Nunca** `@Autowired` en campos: oculta las dependencias, impide la inmutabilidad y obliga a usar reflexión en los tests.
- **Nunca** `new` de beans ni búsquedas manuales en el `ApplicationContext`.
- Un constructor con muchos parámetros (orientativo: más de 5-6) indica que la clase tiene demasiadas responsabilidades.

## S — Single Responsibility Principle

Cada clase tiene **una única razón para cambiar**.

```java
// ❌ Un servicio que hace de todo
@Service
public class UserService {
    public UserResponse create(CreateUserRequest r) { ... }
    public TokenResponse login(LoginRequest r) { ... }          // ← autenticación
    public void sendWelcomeEmail(String email) { ... }          // ← notificaciones
    public byte[] exportCsv() { ... }                           // ← informes
}

// ✅ Separado por razón de cambio
@Service public class UserService { ... }
@Service public class AuthService { ... }
@Service public class NotificationService { ... }
@Service public class UserReportService { ... }
```

- Un controlador por recurso; la lógica, en servicios.
- El mismo servicio se usa desde REST, GraphQL o mensajería: si un servicio conoce detalles del transporte (HTTP, cabeceras, mensajes), tiene dos razones para cambiar.

## O — Open/Closed Principle

Extiende con nuevas implementaciones en lugar de modificar las existentes. Spring inyecta **todas** las implementaciones de una interfaz en una `List` o `Map`:

```java
public interface PaymentGateway {
    String provider();
    PaymentResult charge(Money amount, String reference);
}

@Component
class StripePaymentGateway implements PaymentGateway {
    public String provider() { return "stripe"; }
    ...
}

@Component
class RedsysPaymentGateway implements PaymentGateway {
    public String provider() { return "redsys"; }
    ...
}

@Service
public class PaymentService {

    private final Map<String, PaymentGateway> gateways;

    public PaymentService(List<PaymentGateway> gateways) {
        this.gateways = gateways.stream()
                .collect(Collectors.toUnmodifiableMap(PaymentGateway::provider, Function.identity()));
    }

    public PaymentResult charge(String provider, Money amount, String reference) {
        PaymentGateway gateway = gateways.get(provider);
        if (gateway == null) {
            throw new UnsupportedPaymentProviderException(provider);
        }
        return gateway.charge(amount, reference);
    }
}
```

Añadir una pasarela es crear un nuevo `@Component`, sin tocar `PaymentService`. Usa este patrón solo cuando haya **variantes reales**.

## L — Liskov Substitution Principle

- Toda implementación de una interfaz cumple el mismo contrato **y el mismo comportamiento esperado**: no lanza excepciones que la interfaz no prevé, no ignora llamadas, no devuelve `null` donde el contrato promete un valor.
- Un doble de test debe ser intercambiable con la implementación real sin alterar al consumidor.
- Evita la herencia de implementación para reutilizar código; prefiere composición.

## I — Interface Segregation Principle

- Interfaces pequeñas por rol: un consumidor de solo lectura no depende de métodos de escritura.
- En repositorios de Spring Data, si una funcionalidad solo necesita unas pocas operaciones, puedes extender `Repository<T, ID>` y declarar solo esos métodos en lugar de `JpaRepository`.
- DTOs/proyecciones específicos por caso (`UserSummary` para listados, `UserDetail` para detalle) en lugar de un objeto que lo contiene todo.

## D — Dependency Inversion Principle

Depende de abstracciones en las **fronteras** (persistencia propia, proveedores externos, mensajería, reloj), no en cada servicio.

```java
// Abstracción en el dominio
public interface NotificationSender {
    void send(Notification notification);
}

// Implementación de infraestructura
@Component
class EmailNotificationSender implements NotificationSender { ... }
```

- Con **varias implementaciones del mismo tipo**, elige con `@Qualifier` en el punto de inyección o marca la principal con `@Primary`. Prefiere `@Qualifier` explícito o la inyección de `List`/`Map` frente a `@Primary`, que oculta la elección.
- Implementaciones según configuración: `@ConditionalOnProperty` en la clase de configuración, no `if` en el servicio.
- Spring ya permite sustituir cualquier bean concreto en tests (`@MockitoBean`, constructor en tests unitarios). Introduce una interfaz cuando haya **más de una implementación real**, una frontera que quieras aislar o una necesidad de test que no se cubra de otra forma; **no** una interfaz `XService` + `XServiceImpl` por cada servicio.

## Checklist de diseño

- [ ] Inyección por constructor con campos `final`; sin `@Autowired` en campos ni `new` de beans
- [ ] Cada clase con una razón de cambio identificable; constructores no sobrecargados
- [ ] Variantes reales como implementaciones inyectadas (`List`/`Map`)
- [ ] Implementaciones intercambiables respetan contrato y comportamiento
- [ ] Consumidores dependen solo de lo que usan
- [ ] Interfaces solo en fronteras o con varias implementaciones; sin `Impl` automático
- [ ] Elección de implementación explícita (`@Qualifier`, configuración)
