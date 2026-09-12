# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-12

### Added
- **Full Architecture Modernization**: Ported Python CustomTkinter POS into an enterprise-grade full-stack Nuxt 4 & Vue 3 application.
- **Hexagonal Architecture Core**:
  - Domain models (`Product`, `Customer`, `Sale`, `User`, `CashRegisterClose`).
  - Strict Ports and Adapters decoupling application business logic from framework and persistence drivers.
- **Implementation of 6 Design Patterns**:
  - `Singleton`: Thread-safe `DatabaseClient` and central `DomainEventBus`.
  - `Facade`: `PosFacade` offering unified, high-level POS APIs to HTTP controllers.
  - `Factory`: `PaymentStrategyFactory` for dynamic payment resolution.
  - `Strategy`: Pluggable payment strategies for `CASH`, `CARD`, and `CREDIT_DEBT`.
  - `Observer`: Reactive domain event handling (`SaleCompleted`, `LowStock`).
  - `Decorator`: `withAudit` providing performance latency measurement and error auditing.
- **Prisma ORM & InsForge DBA Integration**:
  - Production-ready PostgreSQL schema with indexes on barcodes, customer names, and dates.
  - Atomic transactions (`prisma.$transaction`) guaranteeing zero data loss on power cuts.
  - Database seeder (`prisma/seed.ts`) populating hardware, retail, and debtor data.
- **KatanaKit CDN Fetching Adapter**:
  - Dynamic client loading of `katanakit-js@2.14.1` from `https://esm.sh/katanakit-js@2.14.1`.
  - Safe Result wrapper for H3 responses and reactive composables in Vue 3.
- **Frontend User Interface**:
  - High-performance barcode scanner listener with rapid scan buffer and auto-focus.
  - Reactive cart management with quantity increments, unit price calculations, and subtotal updates.
  - Cash register closing view with cash, card, and fiado breakdown cards.
  - Store credit module with credit limit validation and partial/full debt repayment modals.
  - Administrative reporting dashboard with top 5 best-sellers and customer debtors table.
  - Role-based User Management interface with password resets and status toggling.
  - Product catalog and inventory management screen.
- **Security & Authorization**:
  - Bcrypt password hashing.
  - JWT session management stored in `httpOnly` secure cookies.
  - Global Nuxt middleware enforcing role-based routing (`ADMIN` vs `CASHIER`).
- **Comprehensive English Documentation**:
  - Complete `README.md`, `CHANGELOG.md`, and `AGENTS.md`.
