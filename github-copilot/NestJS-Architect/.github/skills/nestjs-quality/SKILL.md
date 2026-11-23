---
name: nestjs-quality
description: 'Backend NestJS (API). Calidad de código NestJS: ESLint (typescript-eslint), Prettier, SonarQube, complejidad cognitiva, código muerto, logging con Logger/pino/winston y checklist pre-PR. Usar cuando: corregir warnings de lint, formatear, resolver issues de SonarQube, sustituir console.log por un logger, revisar calidad antes de un PR.'
argument-hint: 'Describe el problema de calidad o el fichero que necesitas revisar.'
---

# Calidad de código y logging

Lee siempre la configuración real del proyecto (`eslint.config.*`, Prettier, `sonar-project.properties`) antes de aplicar estas reglas: si difieren, prevalece la del proyecto. La estrategia de tests está en `nestjs-testing`.

## ESLint

- **ESLint**: `typescript-eslint` (recommended + stylistic) sin warnings ni errores. Si el proyecto lo tiene habilitado, también las reglas con información de tipos (`recommendedTypeChecked`).
- Reglas especialmente relevantes en NestJS:
  - `@typescript-eslint/no-explicit-any`: sin `any`.
  - `@typescript-eslint/no-floating-promises`: toda promesa se espera (`await`) o se marca con `void` de forma explícita. Una promesa no esperada en un servicio produce errores no controlados.
  - `@typescript-eslint/no-unused-vars`: sin variables ni imports sin usar.
- En un monorepo Nx, `@nx/enforce-module-boundaries` impone los límites entre librerías; en el modo monorepo del Nest CLI, el equivalente son reglas `no-restricted-imports` (ver `nestjs-monorepo`). No las desactives: si saltan, el código está en la librería equivocada.
- Corrige la causa. No desactives reglas con `eslint-disable` salvo excepción justificada y comentada en la propia línea.

```typescript
// ❌ Promesa flotante: el error se pierde
this.emailService.sendWelcome(user.email);

// ✅ Esperada
await this.emailService.sendWelcome(user.email);

// ✅ Fuego y olvido explícito, con gestión del error
void this.emailService.sendWelcome(user.email).catch((error: unknown) =>
  this.logger.error('Welcome email failed', error instanceof Error ? error.stack : undefined),
);
```

`ClientProxy.send()` tiene un problema equivalente: devuelve un Observable frío y, si nadie se suscribe, el mensaje no se envía (ver `nestjs-microservices`).

## Prettier

- **Prettier**: respeta la configuración del proyecto. No la modifiques; formatea antes de entregar.

## SonarQube

- **SonarQube**: sin code smells, duplicaciones ni vulnerabilidades.
- Complejidad cognitiva baja; el umbral lo fija el quality gate del proyecto (por defecto en Sonar, **15 por función**). Reduce extrayendo métodos con nombres descriptivos y con retornos tempranos.
- Sin código muerto (métodos privados no usados, ramas inalcanzables, providers registrados que nadie inyecta).
- Sin `console.log` en producción.
- Extrae lógica duplicada cuando representa el mismo concepto; no unifiques a la fuerza fragmentos parecidos que evolucionan por razones distintas. Si se repite entre aplicaciones del mismo monorepo, extráela a una librería `util`.

## Logging

- Usa un logger como `Logger` de `@nestjs/common` o `pino`/`winston` (p. ej. con `nestjs-pino`). **Nunca uses `console.log`** en código de producción.
- Un logger por clase con contexto:

```typescript
@Injectable()
export class OrdersService {
  private readonly logger = new Logger(OrdersService.name);

  async cancel(orderId: string): Promise<void> {
    this.logger.log(`Cancelling order ${orderId}`);
    // ...
  }
}
```

- En producción, logs **estructurados** (JSON) con nivel, contexto y `correlationId` (ver `nestjs-request-pipeline`); en consumidores de mensajes, también el `eventId`. En un monorepo, incluye además el nombre de la aplicación para distinguirlas.
- Niveles: `error` para fallos que requieren atención, `warn` para situaciones anómalas recuperables, `log`/`info` para eventos de negocio relevantes, `debug` para diagnóstico.
- **Nunca** registres contraseñas, tokens, cabeceras `Authorization`, cuerpos completos de petición o de mensaje ni datos personales. Si usas pino, configura `redact` para las rutas sensibles.
- Al registrar un error, incluye el stack en el log; nunca en la respuesta (ver `nestjs-error-handling`).

## Checklist pre-PR

Proyecto de una aplicación:

```powershell
npm run lint
npx prettier --check "src/**/*.ts" "test/**/*.ts"
npm run build
npm test
npm run test:e2e   # si el proyecto los tiene
```

Monorepo (ver `nestjs-monorepo`):

```powershell
# Modo monorepo del Nest CLI: por aplicación afectada
nest build billing
npx prettier --check "apps/**/*.ts" "libs/**/*.ts"

# Nx: solo lo afectado por los cambios
nx affected -t lint test build
nx format:check
```

- [ ] Lint sin warnings ni errores (en un monorepo, de todos los proyectos afectados)
- [ ] Prettier formateado
- [ ] Build sin errores
- [ ] Tests en verde (cobertura según guidelines)
- [ ] Sin `console.log`, código muerto ni duplicación
- [ ] Sin promesas flotantes ni `send()` de cliente sin suscribir
- [ ] Complejidad cognitiva dentro del quality gate
- [ ] Sin violaciones de límites entre librerías ni imports profundos (monorepo)
- [ ] Sin datos sensibles en logs
