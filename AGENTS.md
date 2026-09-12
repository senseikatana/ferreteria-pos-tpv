# AGENTS.md — Development Guidelines for AI & Software Agents

Welcome to **Universal POS Core** (`@senseikatana/pos-universal`). This document establishes the mandatory architectural invariants, coding conventions, and operational workflows for autonomous coding agents and software engineers contributing to this repository.

---

## 🧭 Architectural Philosophy

This system follows **Hexagonal Architecture (Ports and Adapters)** combined with **Domain-Driven Design (DDD)** and strict adherence to **SOLID principles**.

```text
       [ Primary Adapters ]
    Nuxt 4 Pages & Nitro APIs
               │
               ▼
   [ Application Layer / Ports ]
      PosFacade & Repositories
               │
               ▼
        [ Domain Core ]
  Entities, Value Objects, Events
               ▲
               │
   [ Secondary / Driven Adapters ]
   Prisma ORM • PostgreSQL • InsForge
```

### The 6 Mandatory Design Patterns

All core functionality must respect these patterns:

1. **Singleton Pattern**:
   - `server/utils/prisma.ts`: Database client lifecycle management.
   - `server/core/observers/DomainEventBus.ts`: Central domain event coordinator.
2. **Facade Pattern**:
   - `server/core/facade/PosFacade.ts`: Single point of contact for controllers. HTTP handlers must **never** bypass the Facade to call Prisma directly.
3. **Factory Pattern**:
   - `server/core/factories/PaymentStrategyFactory.ts`: Resolves payment mechanisms dynamically without conditional sprawl.
4. **Strategy Pattern**:
   - `server/core/strategies/PaymentStrategies.ts`: Encapsulates payment rules (`CashPaymentStrategy`, `CardPaymentStrategy`, `CreditDebtPaymentStrategy`).
5. **Observer Pattern**:
   - `server/core/observers/DomainEventBus.ts`: Decoupled publish/subscribe mechanism for side-effects (`SaleCompleted`, `LowStock`).
6. **Decorator Pattern**:
   - `server/core/decorators/AuditDecorator.ts`: High-order wrapper providing latency telemetry and execution auditing (`withAudit`).

---

## 📁 Repository Layout

```text
├── app/                        # Nuxt 4 Presentation Layer (Vue 3)
│   ├── assets/css/             # Tailwind base styles
│   ├── composables/            # Reactive stores & KatanaKit CDN client
│   ├── layouts/                # Default layout with dynamic RBAC sidebar
│   ├── middleware/             # auth.global.ts protecting route tiers
│   ├── pages/                  # Route views (ventas, clientes, caja, etc.)
│   └── plugins/                # KatanaKit initialization plugin
├── prisma/
│   ├── schema.prisma           # Agnostic PostgreSQL / InsForge data models
│   └── seed.ts                 # Idempotent database seeder
├── server/
│   ├── api/                    # Nitro server endpoints
│   ├── core/                   # Hexagonal domain & patterns
│   │   ├── adapters/           # Prisma repository implementations
│   │   ├── decorators/         # Audit decorators
│   │   ├── domain/             # Entities and Domain Events
│   │   ├── factories/          # Strategy factories
│   │   ├── facade/             # PosFacade
│   │   ├── observers/          # Domain Event Bus
│   │   ├── ports/              # Repository & service contracts
│   │   └── strategies/         # Payment strategy implementations
│   └── utils/                  # Prisma client, JWT, and KatanaKit response helpers
├── nuxt.config.ts              # Nuxt 4 configuration
└── package.json                # Project dependencies & scripts
```

---

## 🔒 Security & Data Integrity Invariants

1. **Atomic Transactions**:
   - Every financial checkout or balance adjustment **must** be executed inside `prisma.$transaction`.
   - Never decrement stock or alter customer debt balances outside of an atomic transaction.
2. **Password Security**:
   - Always hash passwords using `bcrypt` (10 rounds). Plain text passwords must never enter persistence or logs.
3. **Session Integrity**:
   - Authentication tokens are transmitted via `httpOnly`, `SameSite=Lax` cookies.
4. **Role Isolation**:
   - Routes `/reportes` and `/usuarios` and their associated API endpoints (`server/api/reports/*`, `server/api/users/*`) strictly require role `ADMIN`.

---

## ⚡ Extension Guidelines

### Adding a New Payment Method
1. Create a new strategy implementing `IPaymentStrategy` in `server/core/strategies/PaymentStrategies.ts`.
2. Register the strategy in `PaymentStrategyFactory.ts`.
3. Add the enum value to `PaymentMethod` in `prisma/schema.prisma` and update UI selectors in `app/pages/ventas.vue`.

### Adding a Domain Event Listener
```typescript
import { eventBus } from '~/server/core/observers/DomainEventBus'

eventBus.subscribe('SaleCompleted', async (event) => {
  // Execute side-effect without coupling the checkout transaction
})
```

---

## 🧪 Verification Commands

Before committing or releasing new versions, ensure the following checks pass:

```bash
# Verify TypeScript types and build
yarn build

# Ensure database bindings are current
yarn prisma:generate
```
