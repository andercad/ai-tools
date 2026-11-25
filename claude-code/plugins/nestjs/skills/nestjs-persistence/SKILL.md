---
name: nestjs-persistence
description: 'Persistencia en NestJS con TypeORM o Prisma. Usar al añadir o cambiar tablas, entidades, relaciones, repositorios, consultas, índices, migraciones, transacciones, concurrencia o al resolver consultas lentas y N+1. No usar para elegir ORM o SQL frente a NoSQL a nivel arquitectura (skill nestjs-data-messaging).'
---

# Persistencia

## Reglas clave
- Detecta el ORM instalado; no mezcles ni generes código para otro.
- Cambios de esquema solo con migraciones; nunca `synchronize: true` en producción.
- Consultas parametrizadas; sin SQL concatenado con entrada del usuario.
- No expongas entidades: mapea a DTOs.
- Operaciones multi-paso en una transacción; evita N+1 (joins o `relations` explícitas, DataLoader en GraphQL).
- Índices para filtros y orden frecuentes; paginación acotada.

## Referencias
- [persistence.md](references/persistence.md): entidades, relaciones, repositorios, migraciones, transacciones, rendimiento y concurrencia (TypeORM y Prisma).
